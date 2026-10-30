"""Minimal animation engine on skia-python.

Design coordinates are 1920x1080; output is 3840x2160 (scaled 2x) so vector
art stays crisp.  A scene is a pure function of time: draw(c, t, ctx).
Each frame is recorded ONCE as an SkPicture, replayed on a small preview
surface to detect change, and replayed on the 4K surface only when it differs
from the previous frame (static holds cost almost nothing).
"""
from __future__ import annotations
import functools
import math
import os
import subprocess
import sys

import numpy as np
import skia

DW, DH = 1920, 1080
W, H = 3840, 2160
FPS = 30

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")


# ----------------------------------------------------------------------------
# colour
# ----------------------------------------------------------------------------
def hexc(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(round(255 * max(0.0, min(1.0, a)))))


class Pal:
    BG = "#11151b"        # deep slate "paper"
    INK = "#ece6d8"       # warm off-white, ET Book on dark
    MUTED = "#8b94a1"
    FAINT = "#3a4350"
    GRID = "#232a34"
    BLUE = "#58c4dd"      # links / data
    GREEN = "#83c167"     # ok / ideal / free
    GOLD = "#f2c94c"      # focus / highlight
    RED = "#fc6255"       # congestion / blocked
    ORANGE = "#e8884b"
    PURPLE = "#a98ade"
    TEAL = "#4fd1c5"


def mix(c1, c2, t):
    """linear blend of two hex colours -> hex"""
    a = [int(c1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(c2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


# ----------------------------------------------------------------------------
# easing
# ----------------------------------------------------------------------------
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(x):
    """3b1b-style sigmoid easing, exact 0 and 1 at the ends."""
    x = clamp01(x)
    s = lambda v: 1 / (1 + math.exp(-v))
    lo, hi = s(-6), s(6)
    return (s((x - 0.5) * 12) - lo) / (hi - lo)


def prog(t, t0, dur):
    return clamp01((t - t0) / dur) if dur > 0 else (1.0 if t >= t0 else 0.0)


def ease(t, t0, dur):
    return smooth(prog(t, t0, dur))


def there_and_back(x):
    x = clamp01(x)
    return 1 - abs(2 * x - 1)


# ----------------------------------------------------------------------------
# paints & fonts (cached; never mutate a cached object)
# ----------------------------------------------------------------------------
@functools.lru_cache(maxsize=4096)
def P(color, a=1.0, w=0.0, fill=True, cap="round", dash=None, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=hexc(color, a))
    if fill and w == 0.0:
        p.setStyle(skia.Paint.kFill_Style)
    else:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(w if w else 1.0)
        p.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap,
                        "square": skia.Paint.kSquare_Cap}[cap])
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


_TF = {}
FONT_FILES = {
    "r": "et-book-roman-line-figures.ttf",
    "b": "et-book-bold-line-figures.ttf",
    "i": "et-book-display-italic-old-style-figures.ttf",
}
FALLBACK = {
    "r": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "i": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "m": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}


def typeface(style):
    if style not in _TF:
        if style == "m":
            _TF[style] = skia.Typeface.MakeFromFile(FALLBACK["m"])
        else:
            tf = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, FONT_FILES[style]))
            _TF[style] = tf
        assert _TF[style] is not None, style
    return _TF[style]


@functools.lru_cache(maxsize=None)
def fallback_face(style):
    return skia.Typeface.MakeFromFile(FALLBACK[style if style in FALLBACK else "r"])


@functools.lru_cache(maxsize=512)
def font(style, size):
    f = skia.Font(typeface(style), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    return f


@functools.lru_cache(maxsize=512)
def fb_font(style, size):
    f = skia.Font(fallback_face(style), size * 0.92)
    f.setSubpixel(True)
    return f


@functools.lru_cache(maxsize=None)
def has_glyph(style, ch):
    if style == "m":
        return True
    return typeface(style).unicharToGlyph(ord(ch)) != 0


def _runs(s, style):
    """split into (text, use_fallback) runs by ET Book glyph coverage"""
    out, cur, curfb = [], "", None
    for ch in s:
        fb = (not has_glyph(style, ch)) and ch not in " \t"
        if curfb is None or fb == curfb:
            cur += ch
            curfb = fb
        else:
            out.append((cur, curfb)); cur, curfb = ch, fb
    if cur:
        out.append((cur, bool(curfb)))
    return out


def text_width(s, size=24, style="r"):
    w = 0.0
    for run, fb in _runs(s, style):
        f = fb_font(style, size) if fb else font(style, size)
        w += f.measureText(run)
    return w


def text(c, s, x, y, size=24, style="r", color=Pal.INK, a=1.0, anchor="l", blur=0.0):
    """Draw text with baseline at y. anchor: l / c / r."""
    if a <= 0.004 or not s:
        return 0.0
    w = text_width(s, size, style)
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    paint = P(color, a)
    cx = x
    for run, fb in _runs(s, style):
        f = fb_font(style, size) if fb else font(style, size)
        c.drawString(run, cx, y, f, paint)
        cx += f.measureText(run)
    return w


def small_caps(c, s, x, y, size=16, color=Pal.MUTED, a=1.0, anchor="l", spacing=1.6):
    """letter-spaced capitals (Tufte-ish labels)"""
    s = ''.join(ch.upper() if ch.isascii() else ch for ch in s)
    w = sum(text_width(ch, size, "r") + spacing for ch in s) - spacing
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    cx = x
    for ch in s:
        text(c, ch, cx, y, size, "r", color, a)
        cx += text_width(ch, size, "r") + spacing
    return w


def mono(c, s, x, y, size=20, color=Pal.INK, a=1.0):
    c.drawString(s, x, y, font("m", size), P(color, a))


def rich(c, s, x, y, size=26, color=Pal.INK, a=1.0, anchor="l"):
    """Mini math markup.  $...$ = math (letters italic).  ^{..} superscript, _{..} subscript.
    Text outside $ is roman.  Returns width."""
    toks = []   # (string, style, dy_scale, size_scale)

    def emit_math(m):
        i = 0
        while i < len(m):
            ch = m[i]
            if ch in "^_" and i + 1 < len(m) and m[i + 1] == "{":
                j = m.index("}", i)
                inner = m[i + 2:j]
                for k, chh in enumerate(inner):
                    st = "i" if chh.isalpha() and chh.isascii() else "r"
                    toks.append((chh, st, -0.38 if ch == "^" else 0.22, 0.68))
                i = j + 1
            else:
                st = "i" if ch.isalpha() and ch.isascii() else "r"
                toks.append((ch, st, 0.0, 1.0))
                i += 1

    parts = s.split("$")
    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            for ch in part:
                toks.append((ch, "r", 0.0, 1.0))
        else:
            emit_math(part)
    w = sum(text_width(t, size * sc, st) for t, st, dy, sc in toks)
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    cx = x
    for t, st, dy, sc in toks:
        text(c, t, cx, y + dy * size, size * sc, st, color, a)
        cx += text_width(t, size * sc, st)
    return w


def wrap(s, size, style, max_w):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_width(trial, size, style) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines


def paragraph(c, s, x, y, size=24, style="r", color=Pal.INK, a=1.0, max_w=600, lead=1.35, anchor="l"):
    for i, ln in enumerate(wrap(s, size, style, max_w)):
        text(c, ln, x, y + i * size * lead, size, style, color, a, anchor)
    return len(wrap(s, size, style, max_w)) * size * lead


# ----------------------------------------------------------------------------
# geometry primitives
# ----------------------------------------------------------------------------
def line(c, x1, y1, x2, y2, color=Pal.BLUE, w=2.0, a=1.0, dash=None, cap="round"):
    if a <= 0.004:
        return
    c.drawLine(x1, y1, x2, y2, P(color, a, w, False, cap, dash))


def line_p(c, x1, y1, x2, y2, p, color=Pal.BLUE, w=2.0, a=1.0, dash=None):
    """line drawn progressively from (x1,y1) towards (x2,y2)"""
    if p <= 0:
        return
    line(c, x1, y1, lerp(x1, x2, p), lerp(y1, y2, p), color, w, a, dash)


def polyline(c, pts, color=Pal.BLUE, w=2.0, a=1.0, dash=None, closed=False):
    if len(pts) < 2 or a <= 0.004:
        return
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if closed:
        path.close()
    c.drawPath(path, P(color, a, w, False, "round", dash))


def arc_path(x1, y1, x2, y2, bulge):
    """quadratic arc between two points; bulge = perpendicular offset of control point"""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    return (mx + nx * bulge, my + ny * bulge)


def curve(c, x1, y1, x2, y2, bulge, color=Pal.BLUE, w=2.0, a=1.0, dash=None, p=1.0):
    if a <= 0.004 or p <= 0:
        return
    cx, cy = arc_path(x1, y1, x2, y2, bulge)
    if p >= 1:
        path = skia.Path(); path.moveTo(x1, y1); path.quadTo(cx, cy, x2, y2)
    else:
        pts = [quad_pt(x1, y1, cx, cy, x2, y2, i / 24 * p) for i in range(25)]
        path = skia.Path(); path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
    c.drawPath(path, P(color, a, w, False, "round", dash))


def quad_pt(x1, y1, cx, cy, x2, y2, t):
    u = 1 - t
    return (u * u * x1 + 2 * u * t * cx + t * t * x2, u * u * y1 + 2 * u * t * cy + t * t * y2)


def curve_pt(x1, y1, x2, y2, bulge, t):
    cx, cy = arc_path(x1, y1, x2, y2, bulge)
    return quad_pt(x1, y1, cx, cy, x2, y2, t)


def circle(c, x, y, r, fill=Pal.BLUE, a=1.0, stroke=None, sw=1.5, sa=1.0):
    if fill is not None and a > 0.004:
        c.drawCircle(x, y, r, P(fill, a))
    if stroke is not None and sa > 0.004:
        c.drawCircle(x, y, r, P(stroke, sa, sw, False))


def glow(c, x, y, r, color=Pal.GOLD, a=0.5):
    c.drawCircle(x, y, r, P(color, a, 0.0, True, "round", None, r * 0.55))


def rect(c, x, y, w, h, fill=None, a=1.0, stroke=None, sw=1.5, sa=1.0, r=0, dash=None):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    if fill is not None and a > 0.004:
        c.drawRRect(rr, P(fill, a))
    if stroke is not None and sa > 0.004:
        c.drawRRect(rr, P(stroke, sa, sw, False, "round", dash))


def arrow(c, x1, y1, x2, y2, color=Pal.INK, w=2.0, a=1.0, head=10, p=1.0):
    if p <= 0:
        return
    ex, ey = lerp(x1, x2, p), lerp(y1, y2, p)
    line(c, x1, y1, ex, ey, color, w, a)
    if p >= 0.98:
        ang = math.atan2(y2 - y1, x2 - x1)
        for s in (-1, 1):
            line(c, x2, y2, x2 - head * math.cos(ang + s * 0.45), y2 - head * math.sin(ang + s * 0.45), color, w, a)


def packet(c, pts, u, color=Pal.GOLD, r=5.0, a=1.0, trail=0.0):
    """dot travelling along polyline pts at fraction u in [0,1]"""
    if a <= 0.004:
        return
    segs = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    total = sum(segs) or 1
    def at(uu):
        d = clamp01(uu) * total
        for i, s in enumerate(segs):
            if d <= s or i == len(segs) - 1:
                f = d / s if s else 0
                return (lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f))
            d -= s
    x, y = at(u)
    if trail > 0:
        for k in range(1, 5):
            tx, ty = at(u - trail * k / 4)
            circle(c, tx, ty, r * (1 - 0.15 * k), color, a * (1 - k / 5) * 0.6)
    circle(c, x, y, r, color, a)


def brace_v(c, x, y1, y2, color=Pal.MUTED, a=1.0, w=1.5, depth=8):
    ym = (y1 + y2) / 2
    path = skia.Path()
    path.moveTo(x, y1); path.quadTo(x + depth, y1, x + depth, ym - 6); path.lineTo(x + depth, ym - 6)
    path.quadTo(x + depth, ym, x + depth * 2, ym)
    path.quadTo(x + depth, ym, x + depth, ym + 6)
    path.quadTo(x + depth, y2, x, y2)
    c.drawPath(path, P(color, a, w, False))


# ----------------------------------------------------------------------------
# Tufte "range-frame" axes
# ----------------------------------------------------------------------------
class Axes:
    """Range-frame axes: axis lines span only the data range; ticks at chosen values."""

    def __init__(self, x0, y0, x1, y1, xr, yr, xlog=False, ylog=False):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1      # pixel box: x0..x1, y0 (bottom) .. y1 (top)
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    def X(self, v):
        a, b = self.xr
        if self.xlog:
            v, a, b = math.log10(v), math.log10(a), math.log10(b)
        return lerp(self.x0, self.x1, (v - a) / (b - a))

    def Y(self, v):
        a, b = self.yr
        if self.ylog:
            v, a, b = math.log10(v), math.log10(a), math.log10(b)
        return lerp(self.y0, self.y1, (v - a) / (b - a))

    def frame(self, c, xticks, yticks, xfmt=str, yfmt=str, a=1.0, size=15, xlabel=None, ylabel=None):
        col = Pal.MUTED
        line(c, self.X(xticks[0]), self.y0 + 8, self.X(xticks[-1]), self.y0 + 8, col, 1.2, a)
        line(c, self.x0 - 8, self.Y(yticks[0]), self.x0 - 8, self.Y(yticks[-1]), col, 1.2, a)
        for v in xticks:
            line(c, self.X(v), self.y0 + 8, self.X(v), self.y0 + 14, col, 1.2, a)
            text(c, xfmt(v), self.X(v), self.y0 + 14 + size + 2, size, "r", col, a, "c")
        for v in yticks:
            line(c, self.x0 - 8, self.Y(v), self.x0 - 14, self.Y(v), col, 1.2, a)
            text(c, yfmt(v), self.x0 - 18, self.Y(v) + size * 0.32, size, "r", col, a, "r")
        if xlabel:
            text(c, xlabel, (self.x0 + self.x1) / 2, self.y0 + 14 + size * 2 + 14, size, "i", col, a, "c")
        if ylabel:
            c.save(); c.translate(self.x0 - 64, (self.y0 + self.y1) / 2); c.rotate(-90)
            text(c, ylabel, 0, 0, size, "i", col, a, "c"); c.restore()


# ----------------------------------------------------------------------------
# frame chrome: chapter label, subtitle
# ----------------------------------------------------------------------------
class Ctx:
    """Per-scene timing context handed to scene draw functions."""

    def __init__(self, scene_info, idx, n_scenes, results):
        self.info = scene_info
        self.idx = idx
        self.n = n_scenes
        self.R = results
        self.dur = scene_info["dur"]
        self.beats = scene_info["beats"]

    def b0(self, i):
        return self.beats[i]["start"]

    def b1(self, i):
        return self.beats[i]["end"]

    def bp(self, t, i, delay=0.0, dur=1.0):
        """eased progress since beat i start (+delay)"""
        return ease(t, self.b0(i) + delay, dur)

    def lp(self, t, i, delay=0.0, dur=1.0):
        """linear progress"""
        return prog(t, self.b0(i) + delay, dur)

    def now_beat(self, t):
        cur = 0
        for i, b in enumerate(self.beats):
            if t >= b["start"] - 0.05:
                cur = i
        return cur


def chrome(c, t, ctx):
    info = ctx.info
    # chapter label (top-left), Tufte margin-note style
    small_caps(c, f"{ctx.idx + 1:02d}", 64, 54, 16, Pal.MUTED)
    line(c, 96, 49, 118, 49, Pal.FAINT, 1.2)
    small_caps(c, info["title"], 128, 54, 16, Pal.MUTED)
    # subtitle
    cur = None
    for b in ctx.beats:
        for s in b["sentences"]:
            if s["start"] - 0.05 <= t <= s["end"] + 0.25:
                cur = s
    if cur is not None:
        a = min(prog(t, cur["start"] - 0.05, 0.15), 1 - prog(t, cur["end"] + 0.05, 0.2))
        lines = wrap(cur["text"], 30, "r", 1500)
        y0 = 1000 if len(lines) == 1 else 986
        for i, ln in enumerate(lines[:3]):
            text(c, ln, DW / 2, y0 + i * 38, 30, "r", Pal.INK, 0.92 * a, "c")


def footer(c, s, a=1.0):
    """Source line, top-right margin (Tufte: sources on every slide)."""
    text(c, s, DW - 64, 54, 15, "i", Pal.MUTED, 0.9 * a, "r")


# ----------------------------------------------------------------------------
# renderer
# ----------------------------------------------------------------------------
class Renderer:
    def __init__(self, full=True, size=(W, H)):
        self.full = full
        self.W, self.H = size
        self.surf = skia.Surface(self.W, self.H)
        self.prev = skia.Surface(DW // 4, DH // 4)
        self.last_prev = None
        self.last_bytes = None
        self.bg = hexc(Pal.BG)

    def record(self, draw, t, ctx):
        rec = skia.PictureRecorder()
        c = rec.beginRecording(skia.Rect.MakeWH(DW, DH))
        c.drawPaint(P(Pal.BG))
        c.save(); c.translate(0, getattr(draw, 'dy', 0)); draw(c, t, ctx); c.restore()
        chrome(c, t, ctx)
        return rec.finishRecordingAsPicture()

    def frame(self, draw, t, ctx):
        pic = self.record(draw, t, ctx)
        pc = self.prev.getCanvas()
        pc.save(); pc.scale(0.25, 0.25); pc.drawPicture(pic); pc.restore()
        pv = self.prev.makeImageSnapshot().toarray()
        if self.last_prev is not None and np.array_equal(pv, self.last_prev) and self.last_bytes is not None:
            return self.last_bytes, False
        self.last_prev = pv
        fc = self.surf.getCanvas()
        fc.save(); fc.scale(self.W / DW, self.H / DH); fc.drawPicture(pic); fc.restore()
        arr = self.surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType)
        self.last_bytes = np.ascontiguousarray(arr).tobytes()
        return self.last_bytes, True

    def png(self, draw, t, ctx, path):
        pic = self.record(draw, t, ctx)
        fc = self.surf.getCanvas()
        fc.save(); fc.scale(self.W / DW, self.H / DH); fc.drawPicture(pic); fc.restore()
        self.surf.makeImageSnapshot().save(path, skia.kPNG)


def open_encoder(path, w, h, fps=FPS, crf=18, preset="veryfast", threads=2):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{w}x{h}",
           "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-tune", "animation", "-g", str(fps * 2), "-threads", str(threads),
           "-movflags", "+faststart", path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
