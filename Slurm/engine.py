"""
engine.py - a small Skia-based 2D animation toolkit.

Authoring space is 1920x1080 "units". The surface is scaled (x2 for 4K, x1 for
1080p, x0.5 for the cheap hold-detection probe), so every scene is written once.

Look: dark graphite ground + 3Blue1Brown-style accent colours, Tufte-style
typography and layout (Pagella serif, hairline rules, direct labels, margin notes).
"""
import math
import skia

LW, LH = 1920, 1080

# ------------------------------------------------------------------ palette
def _c(h):
    return h


PAL = dict(
    bg=0xFF14161B,
    panel=0xFF1B1E25,
    panel2=0xFF22262F,
    ink=0xFFECE7DC,
    dim=0xFFA3A8B1,
    faint=0xFF3B4048,
    rule=0xFF565C68,
    blue=0xFF58C4DD,
    teal=0xFF5CD0B3,
    green=0xFF83C167,
    yellow=0xFFF7D96F,
    orange=0xFFFF862F,
    red=0xFFFC6255,
    purple=0xFF9A72AC,
    pink=0xFFD76FB8,
)


def col(c, a=1.0):
    """Colour with alpha multiplied by a (0..1). c may be a palette key or int."""
    if isinstance(c, str):
        c = PAL[c]
    base_a = (c >> 24) & 0xFF
    r, g, b = (c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF
    return skia.ColorSetARGB(int(max(0, min(255, base_a * a))), r, g, b)


def mix(c1, c2, t):
    if isinstance(c1, str):
        c1 = PAL[c1]
    if isinstance(c2, str):
        c2 = PAL[c2]
    t = clamp(t)
    out = 0xFF000000
    for sh in (16, 8, 0):
        a = (c1 >> sh) & 0xFF
        b = (c2 >> sh) & 0xFF
        out |= int(a + (b - a) * t) << sh
    return out


# ------------------------------------------------------------------ easing
def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def prog(t, t0, d):
    """0..1 progress of an animation that starts at t0 and lasts d seconds."""
    if d <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / d)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def lerp(a, b, x):
    return a + (b - a) * x


def appear(t, t0, d=0.5):
    return smooth(prog(t, t0, d))


# ------------------------------------------------------------------ fonts
_FONT_DIR = "/usr/share/texmf/fonts/opentype/public/"
_FACES = {
    "body": _FONT_DIR + "tex-gyre/texgyrepagella-regular.otf",
    "bold": _FONT_DIR + "tex-gyre/texgyrepagella-bold.otf",
    "ital": _FONT_DIR + "tex-gyre/texgyrepagella-italic.otf",
    "bital": _FONT_DIR + "tex-gyre/texgyrepagella-bolditalic.otf",
    "mono": _FONT_DIR + "lm/lmmono10-regular.otf",
    "math": _FONT_DIR + "lm-math/latinmodern-math.otf",
    "sans": _FONT_DIR + "tex-gyre/texgyreheros-regular.otf",
}
_tf = {}
_fonts = {}


def font(face, size):
    key = (face, round(size, 2))
    f = _fonts.get(key)
    if f is None:
        tf = _tf.get(face)
        if tf is None:
            tf = skia.Typeface.MakeFromFile(_FACES[face])
            _tf[face] = tf
        f = skia.Font(tf, size)
        f.setSubpixel(True)
        f.setHinting(skia.FontHinting.kNone)
        f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
        _fonts[key] = f
    return f


def text_w(s, size=24, face="body"):
    return font(face, size).measureText(s)


# math-italic mapping for formulas
def mi(s):
    out = []
    for ch in s:
        if "a" <= ch <= "z":
            # U+1D455 is reserved; italic h lives at U+210E (Planck constant)
            out.append(chr(0x210E) if ch == "h" else chr(0x1D44E + ord(ch) - ord("a")))
        elif "A" <= ch <= "Z":
            out.append(chr(0x1D434 + ord(ch) - ord("A")))
        else:
            out.append(ch)
    return "".join(out)


# ------------------------------------------------------------------ canvas
class Cv:
    def __init__(self, width, height):
        self.surface = skia.Surface(width, height)
        self.c = self.surface.getCanvas()
        self.s = width / LW
        self.w = width
        self.h = height
        self.c.scale(self.s, self.s)

    # --- basics
    def clear(self, color="bg"):
        self.c.drawColor(col(color))

    def paint(self, color, a=1.0, stroke=None, sw=1.0, cap="round", dash=None, join="round"):
        p = skia.Paint(AntiAlias=True)
        p.setColor(col(color, a))
        if stroke:
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeWidth(sw)
            p.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap,
                            "square": skia.Paint.kSquare_Cap}[cap])
            p.setStrokeJoin({"round": skia.Paint.kRound_Join, "miter": skia.Paint.kMiter_Join,
                             "bevel": skia.Paint.kBevel_Join}[join])
            if dash:
                p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
        return p

    def rect(self, x, y, w, h, fill=None, stroke=None, sw=1.0, r=0, a=1.0, dash=None):
        if w <= 0 or h <= 0:
            return
        rc = skia.Rect.MakeXYWH(x, y, w, h)
        if fill is not None:
            p = self.paint(fill, a)
            if r:
                self.c.drawRRect(skia.RRect.MakeRectXY(rc, r, r), p)
            else:
                self.c.drawRect(rc, p)
        if stroke is not None:
            p = self.paint(stroke, a, stroke=True, sw=sw, dash=dash)
            if r:
                self.c.drawRRect(skia.RRect.MakeRectXY(rc, r, r), p)
            else:
                self.c.drawRect(rc, p)

    def circle(self, x, y, r, fill=None, stroke=None, sw=1.0, a=1.0, dash=None):
        if r <= 0:
            return
        if fill is not None:
            self.c.drawCircle(x, y, r, self.paint(fill, a))
        if stroke is not None:
            self.c.drawCircle(x, y, r, self.paint(stroke, a, stroke=True, sw=sw, dash=dash))

    def line(self, x1, y1, x2, y2, color="rule", sw=1.0, a=1.0, dash=None, frac=1.0, cap="round"):
        if frac <= 0:
            return
        if frac < 1:
            x2 = x1 + (x2 - x1) * frac
            y2 = y1 + (y2 - y1) * frac
        self.c.drawLine(x1, y1, x2, y2, self.paint(color, a, stroke=True, sw=sw, dash=dash, cap=cap))

    def poly(self, pts, fill=None, stroke=None, sw=1.0, a=1.0, closed=True, dash=None):
        p = skia.Path()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        if closed:
            p.close()
        if fill is not None:
            self.c.drawPath(p, self.paint(fill, a))
        if stroke is not None:
            self.c.drawPath(p, self.paint(stroke, a, stroke=True, sw=sw, dash=dash))

    def curve(self, p0, p1, p2, p3, color="ink", sw=1.5, a=1.0, frac=1.0, dash=None):
        if frac <= 0:
            return
        path = skia.Path()
        path.moveTo(*p0)
        path.cubicTo(*p1, *p2, *p3)
        self._stroke_frac(path, color, sw, a, frac, dash)

    def polyline(self, pts, color="ink", sw=1.5, a=1.0, frac=1.0, dash=None):
        if frac <= 0 or len(pts) < 2:
            return
        path = skia.Path()
        path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
        self._stroke_frac(path, color, sw, a, frac, dash)

    def _stroke_frac(self, path, color, sw, a, frac, dash):
        if frac < 1:
            pm = skia.PathMeasure(path, False)
            L = pm.getLength()
            dst = skia.Path()
            pm.getSegment(0, L * frac, dst, True)
            path = dst
        self.c.drawPath(path, self.paint(color, a, stroke=True, sw=sw, dash=dash))

    def arrow(self, x1, y1, x2, y2, color="ink", sw=1.6, a=1.0, head=9, frac=1.0, dash=None):
        if frac <= 0:
            return
        ex = x1 + (x2 - x1) * frac
        ey = y1 + (y2 - y1) * frac
        ang = math.atan2(y2 - y1, x2 - x1)
        # shorten the shaft so that it doesn't poke through the head
        sx = ex - math.cos(ang) * head * 0.6
        sy = ey - math.sin(ang) * head * 0.6
        self.c.drawLine(x1, y1, sx, sy, self.paint(color, a, stroke=True, sw=sw, dash=dash))
        if frac > 0.02:
            l = [ex, ey]
            r1 = (ex - head * math.cos(ang - 0.42), ey - head * math.sin(ang - 0.42))
            r2 = (ex - head * math.cos(ang + 0.42), ey - head * math.sin(ang + 0.42))
            self.poly([tuple(l), r1, r2], fill=color, a=a)

    def glow(self, x, y, r, color="blue", a=0.35):
        sh = skia.GradientShader.MakeRadial((x, y), r, [col(color, a), col(color, 0)], [0, 1])
        p = skia.Paint(AntiAlias=True)
        p.setShader(sh)
        self.c.drawCircle(x, y, r, p)

    def vgrad(self, x, y, w, h, c1, c2, a=1.0):
        sh = skia.GradientShader.MakeLinear([(x, y), (x, y + h)], [col(c1, a), col(c2, a)], [0, 1])
        p = skia.Paint(AntiAlias=True)
        p.setShader(sh)
        self.c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)

    # --- text
    def text(self, s, x, y, size=26, color="ink", face="body", align="l", a=1.0):
        if a <= 0.003 or not s:
            return 0
        f = font(face, size)
        w = f.measureText(s)
        if align == "c":
            x -= w / 2
        elif align == "r":
            x -= w
        self.c.drawString(s, x, y, f, self.paint(color, a))
        return w

    def text_rot(self, s, x, y, angle, size=20, color="dim", face="sans", align="c", a=1.0):
        self.c.save()
        self.c.rotate(angle, x, y)
        self.text(s, x, y, size, color, face, align, a)
        self.c.restore()

    def runs(self, parts, x, y, size=26, align="l", a=1.0):
        """Mixed-style line. parts: (text, face, color[, size_mult[, dy]])"""
        tot = 0
        meas = []
        for p in parts:
            t, face, color = p[0], p[1], p[2]
            sm = p[3] if len(p) > 3 else 1.0
            w = text_w(t, size * sm, face)
            meas.append(w)
            tot += w
        if align == "c":
            x -= tot / 2
        elif align == "r":
            x -= tot
        cx = x
        for p, w in zip(parts, meas):
            t, face, color = p[0], p[1], p[2]
            sm = p[3] if len(p) > 3 else 1.0
            dy = p[4] if len(p) > 4 else 0
            self.text(t, cx, y + dy * size, size * sm, color, face, "l", a)
            cx += w
        return tot

    def wrap(self, s, x, y, width, size=24, color="ink", face="body", lh=1.32, a=1.0, align="l"):
        """Greedy word wrap. Returns the y after the last line."""
        words = s.split(" ")
        line = ""
        yy = y
        for w in words:
            trial = (line + " " + w).strip()
            if text_w(trial, size, face) > width and line:
                self.text(line, x if align == "l" else x + width / 2, yy, size, color, face, align, a)
                yy += size * lh
                line = w
            else:
                line = trial
        if line:
            self.text(line, x if align == "l" else x + width / 2, yy, size, color, face, align, a)
            yy += size * lh
        return yy

    # --- layer / clip helpers
    def save(self):
        self.c.save()

    def restore(self):
        self.c.restore()

    def clip(self, x, y, w, h):
        self.c.save()
        self.c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))

    def unclip(self):
        self.c.restore()

    def layer(self, a):
        self.c.saveLayerAlpha(None, int(clamp(a) * 255))

    def endlayer(self):
        self.c.restore()

    def translate(self, dx, dy):
        self.c.translate(dx, dy)

    def scale_about(self, cx, cy, sx, sy=None):
        sy = sx if sy is None else sy
        self.c.translate(cx, cy)
        self.c.scale(sx, sy)
        self.c.translate(-cx, -cy)

    # --- output
    def rgba(self):
        img = self.surface.makeImageSnapshot()
        return img.tobytes() if hasattr(img, "tobytes") else bytes(img.toarray())

    def save_png(self, path):
        img = self.surface.makeImageSnapshot()
        img.save(path, skia.kPNG)


# ------------------------------------------------------------------ Tufte-ish helpers
def hairline(cv, x1, y1, x2, y2, a=1.0, frac=1.0):
    cv.line(x1, y1, x2, y2, "rule", 0.8, a, frac=frac)


def sidenote(cv, x, y, w, head, body, a=1.0, color="dim", size=19):
    """Marginalia: small italic note with a tiny bold-ish heading."""
    if a <= 0.003:
        return y
    if head:
        cv.text(head, x, y, size - 1, "yellow", "ital", a=a)
        y += size * 1.35
    return cv.wrap(body, x, y, w, size, color, "ital", 1.28, a)


def tag(cv, x, y, label, color="yellow", a=1.0, size=15):
    """Small boxed tag, e.g. 'MY MODEL' / 'VENDOR CLAIM'."""
    w = text_w(label, size, "sans") + 14
    cv.rect(x, y - size - 3, w, size + 9, stroke=color, sw=1, r=3, a=a * 0.9)
    cv.text(label, x + 7, y, size, color, "sans", a=a)
    return w


def node_grid(cv, x, y, cols, rows, size, gap, colors=None, a=1.0, r=2):
    """Grid of small squares; colors(i,j)->color or None for empty outline."""
    for j in range(rows):
        for i in range(cols):
            c = colors(i, j) if colors else None
            px, py = x + i * (size + gap), y + j * (size + gap)
            if c is None:
                cv.rect(px, py, size, size, stroke="faint", sw=0.8, r=r, a=a)
            else:
                cv.rect(px, py, size, size, fill=c, r=r, a=a)
