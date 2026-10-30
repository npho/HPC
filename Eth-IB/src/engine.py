"""
Tiny 2D animation engine (skia-python) for the InfiniBand-vs-Ethernet explainer.

Design rules
  * Scenes are *stateless*: draw(canvas, t) is a pure function of scene time t (seconds).  That makes every frame
    independently renderable (parallel workers, stills for QA) and lets the renderer skip identical frames.
  * Logical canvas is 1920x1080; the renderer scales it to the output size (3840x2160 for 4K).
  * Look = 3Blue1Brown motion (smooth easing, partial-path "Create", glow) + Tufte typography/data-ink
    (ET Book, thin rules, range-frame axes, direct labels, marginalia, sources on every slide).
  * Semantic colour (used consistently): InfiniBand = blue, Ethernet/RoCE = orange, Slingshot = purple,
    OK/lossless = green, loss/problem = red, focus = yellow, everything else = paper-white / greys.
"""
import math, os
import skia

from paths import font_path
LW, LH = 1920, 1080

# ------------------------------------------------------------------ palette
def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
BG     = rgb("#111317")
BG2    = rgb("#171a20")      # panels
INK    = rgb("#ebe7da")      # warm paper-white
DIM    = rgb("#9a9a93")
FAINT  = rgb("#5b5e63")
GRID   = rgb("#2b2f36")
IB     = rgb("#58c4dd")      # 3b1b blue
ETH    = rgb("#f2a23a")      # warm orange
SLING  = rgb("#b48ad0")      # purple
GOOD   = rgb("#83c167")      # 3b1b green
BAD    = rgb("#fc6255")      # 3b1b red
HI     = rgb("#ffd166")      # yellow focus

# ------------------------------------------------------------------ easing / timeline helpers
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, u): return a + (b - a) * u
def lerp2(p, q, u): return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))
def lin(u): return u
def smooth(u):                       # 3Blue1Brown's `smooth`
    u = clamp(u); inflection = 10.0
    err = 1 / (1 + math.exp(inflection / 2))
    return clamp((1 / (1 + math.exp(-inflection * (u - 0.5))) - err) / (1 - 2 * err))
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3
def ease_in(u): u = clamp(u); return u ** 3
def ease_io(u): u = clamp(u); return 3 * u * u - 2 * u ** 3
def P(t, a, b, ease=smooth):
    """progress of an animation running from time a to time b"""
    if b <= a: return 1.0 if t >= a else 0.0
    return ease(clamp((t - a) / (b - a)))
def pulse(t, a, b):                  # 0 -> 1 -> 0 between a and b
    u = clamp((t - a) / (b - a)); return math.sin(math.pi * u) if 0 < u < 1 else 0.0

# ------------------------------------------------------------------ fonts
_FONT_FILES = {
    "serif":  "et-book-roman-line-figures.ttf",
    "serifb": "et-book-bold-line-figures.ttf",
    "serifi": "et-book-display-italic-old-style-figures.ttf",
    "sans":   "Inter-Regular.otf",
    "sansm":  "Inter-Medium.otf",
    "sansb":  "Inter-SemiBold.otf",
    "mono":   "DejaVuSansMono.ttf",
    "math":   "lmroman10-regular.otf",
    "mathi":  "lmroman10-italic.otf",
}
_tf, _fc = {}, {}
_DEBUG_GLYPHS = bool(os.environ.get("DEBUG_GLYPHS"))
MISSING = set()
def font(name="serif", size=28):
    key = (name, round(size * 4))
    f = _fc.get(key)
    if f is None:
        if name not in _tf:
            _tf[name] = skia.Typeface.MakeFromFile(font_path(_FONT_FILES[name]))
        f = skia.Font(_tf[name], size)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
        _fc[key] = f
    return f

def col(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(255 * clamp(a)))

_pc = {}
def paint(c=INK, a=1.0, style="fill", sw=1.5, dash=None, cap="round"):
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    if style == "stroke":
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(sw)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        if dash: p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    return p

# ------------------------------------------------------------------ text
def tw(s, name="serif", size=28): return font(name, size).measureText(s)

def text(c, s, x, y, size=28, color=INK, name="serif", align="l", a=1.0):
    if a <= 0.003 or not s: return
    f = font(name, size)
    if _DEBUG_GLYPHS:
        if 0 in f.textToGlyphs(s): MISSING.add((name, s))
    if align != "l":
        w = f.measureText(s); x = x - w / 2 if align == "c" else x - w
    c.drawString(s, x, y, f, paint(color, a))

def wrap(s, name, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, name, size) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def para(c, s, x, y, maxw, size=24, color=INK, name="serif", lh=1.32, a=1.0, align="l"):
    """wrapped paragraph; returns y after last line"""
    for ln in wrap(s, name, size, maxw):
        text(c, ln, x, y, size, color, name, align, a); y += size * lh
    return y

def rich(c, parts, x, y, size=26, name="serif", a=1.0, align="l"):
    """parts = [(string, colour[, fontname]), ...] drawn inline; returns end x"""
    total = sum(tw(p[0], p[2] if len(p) > 2 else name, size) for p in parts)
    if align == "c": x -= total / 2
    elif align == "r": x -= total
    for p in parts:
        nm = p[2] if len(p) > 2 else name
        text(c, p[0], x, y, size, p[1], nm, "l", a); x += tw(p[0], nm, size)
    return x

# ------------------------------------------------------------------ shapes
def rect(c, x, y, w, h, fill=None, stroke=None, sw=1.5, r=0, a=1.0, fa=None, dash=None):
    rr = skia.Rect.MakeXYWH(x, y, w, h)
    if fill is not None and (fa if fa is not None else a) > 0.003:
        p = paint(fill, a if fa is None else fa)
        c.drawRoundRect(rr, r, r, p) if r else c.drawRect(rr, p)
    if stroke is not None and a > 0.003:
        p = paint(stroke, a, "stroke", sw, dash)
        c.drawRoundRect(rr, r, r, p) if r else c.drawRect(rr, p)

def circle(c, x, y, r, fill=None, stroke=None, sw=1.5, a=1.0, fa=None):
    if fill is not None and (fa if fa is not None else a) > 0.003:
        c.drawCircle(x, y, r, paint(fill, a if fa is None else fa))
    if stroke is not None and a > 0.003:
        c.drawCircle(x, y, r, paint(stroke, a, "stroke", sw))

def line(c, x0, y0, x1, y1, color=INK, sw=1.5, a=1.0, dash=None, cap="round"):
    if a <= 0.003: return
    c.drawLine(x0, y0, x1, y1, paint(color, a, "stroke", sw, dash, cap))

def path_of(pts, closed=False):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if closed: p.close()
    return p

def poly(c, pts, color=INK, sw=2, a=1.0, prog=1.0, dash=None, closed=False):
    """polyline with partial drawing (3b1b 'Create')"""
    if a <= 0.003 or prog <= 0: return
    p = path_of(pts, closed)
    if prog < 1.0:
        pm = skia.PathMeasure(p, False); L = pm.getLength(); seg = skia.Path()
        pm.getSegment(0, L * prog, seg, True); p = seg
    c.drawPath(p, paint(color, a, "stroke", sw, dash))

def curve(c, p0, p1, p2, p3, color=INK, sw=2, a=1.0, prog=1.0):
    p = skia.Path(); p.moveTo(*p0); p.cubicTo(*p1, *p2, *p3)
    if prog < 1.0:
        pm = skia.PathMeasure(p, False); L = pm.getLength(); seg = skia.Path()
        pm.getSegment(0, L * prog, seg, True); p = seg
    c.drawPath(p, paint(color, a, "stroke", sw))

def arrow(c, p0, p1, color=INK, sw=2, a=1.0, prog=1.0, head=11, dash=None):
    if prog <= 0 or a <= 0.003: return
    q = lerp2(p0, p1, prog)
    line(c, p0[0], p0[1], q[0], q[1], color, sw, a, dash)
    if prog > 0.98:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        pts = [(p1[0], p1[1]),
               (p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)),
               (p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45))]
        c.drawPath(path_of(pts, True), paint(color, a))

def glow(c, x, y, r, color=IB, a=0.55):
    if a <= 0.003: return
    sh = skia.GradientShader.MakeRadial((x, y), r, [col(color, a), col(color, 0)], None, skia.TileMode.kClamp)
    p = skia.Paint(AntiAlias=True); p.setShader(sh); c.drawCircle(x, y, r, p)

def dot(c, x, y, r=6, color=IB, a=1.0, gl=True):
    if gl: glow(c, x, y, r * 4.2, color, 0.5 * a)
    circle(c, x, y, r, fill=color, a=a)

def pkt(c, x, y, color=IB, w=22, h=12, a=1.0, gl=True):
    if gl: glow(c, x, y, w * 1.4, color, 0.45 * a)
    rect(c, x - w / 2, y - h / 2, w, h, fill=color, r=3, a=a)

def along(pts, u):
    """position at fraction u (0..1) along a polyline"""
    seg = [math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1)]
    L = sum(seg); d = clamp(u) * L
    for i, s in enumerate(seg):
        if d <= s or i == len(seg) - 1:
            v = 0 if s == 0 else d / s
            return lerp2(pts[i], pts[i+1], clamp(v))
        d -= s
    return pts[-1]

# ------------------------------------------------------------------ Tufte furniture
def rule(c, x0, y0, x1, y1, color=FAINT, a=1.0, sw=1.0):
    line(c, x0, y0, x1, y1, color, sw, a, cap="butt")

def margin_note(c, s, x, y, w, size=21, color=DIM, a=1.0, leader=None):
    """italic marginalia; optional leader line to a point"""
    if a <= 0.003: return y
    if leader: line(c, x - 10, y - size * 0.35, leader[0], leader[1], FAINT, 1.0, a * 0.8)
    return para(c, s, x, y, w, size, color, "serifi", 1.28, a)

def tag(c, s, x, y, color=HI, a=1.0, size=15):
    """small boxed label, e.g. MODEL / VENDOR CLAIM"""
    w = tw(s, "sansb", size) + 14
    rect(c, x, y - size - 3, w, size + 9, stroke=color, sw=1.2, r=3, a=a * 0.9)
    text(c, s, x + 7, y, size, color, "sansb", "l", a)
    return x + w

def axis_range_frame(c, x0, y0, x1, y1, a=1.0):
    """Tufte range frame: axes only span the data"""
    line(c, x0, y1, x0, y0, FAINT, 1.2, a, cap="butt"); line(c, x0, y1, x1, y1, FAINT, 1.2, a, cap="butt")

# ------------------------------------------------------------------ icons (schematic)
def chip(c, x, y, w, h, label="", color=INK, a=1.0, size=18, fill=BG2, sw=1.6, name="sansm", pins=0):
    rect(c, x, y, w, h, fill=fill, stroke=color, sw=sw, r=5, a=a)
    if pins:
        for i in range(pins):
            px = x + (i + 1) * w / (pins + 1)
            line(c, px, y - 5, px, y, color, 1.2, a * .8); line(c, px, y + h, px, y + h + 5, color, 1.2, a * .8)
    if label: text(c, label, x + w / 2, y + h / 2 + size * 0.34, size, color, name, "c", a)

def switch_icon(c, x, y, w=120, h=34, color=IB, a=1.0, ports=8, label=None):
    rect(c, x, y, w, h, fill=BG2, stroke=color, sw=1.6, r=4, a=a)
    for i in range(ports):
        px = x + 10 + i * (w - 20) / max(1, ports - 1)
        rect(c, px - 4, y + h - 13, 8, 8, stroke=color, sw=1.0, a=a * .8)
    if label: text(c, label, x + w / 2, y + 17, 15, color, "sansm", "c", a)

def host_icon(c, x, y, w=64, h=40, color=INK, a=1.0, label=None):
    rect(c, x, y, w, h, fill=BG2, stroke=color, sw=1.4, r=4, a=a)
    line(c, x + 8, y + 12, x + w - 8, y + 12, color, 1.0, a * .6); line(c, x + 8, y + 22, x + w - 8, y + 22, color, 1.0, a * .6)
    circle(c, x + w - 12, y + h - 9, 2.5, fill=color, a=a)
    if label: text(c, label, x + w / 2, y + h + 20, 16, DIM, "sans", "c", a)

# ------------------------------------------------------------------ scene base
class Scene:
    id = ""
    title = ""
    sources = ""             # footer line (Tufte: cite on the slide)
    extra_tail = 0.0

    def __init__(self, timing):
        self.beats = timing["beats"]; self.dur = timing["dur"] + self.extra_tail
        self.chrome_a = 1.0

    # time helpers ---------------------------------------------------------
    def B(self, i, off=0.0): return self.beats[i][0] + off      # beat start
    def E(self, i, off=0.0): return self.beats[i][1] + off      # beat end
    def Pb(self, t, i, a=0.0, b=1.2, ease=smooth):                # progress of an animation starting `a` s after beat i
        return P(t, self.B(i, a), self.B(i, b), ease)

    # drawing ---------------------------------------------------------------
    def background(self, c):
        c.clear(col(BG))

    def chrome(self, c, t):
        if self.title:
            a = P(t, 0.25, 0.9)
            text(c, self.title, 96, 86, 46, INK, "serif", "l", a)
            line(c, 96, 108, 96 + (LW - 192) * P(t, 0.3, 1.2), 108, FAINT, 1.0, a, cap="butt")
        if self.sources:
            ls = wrap(self.sources, "sans", 15, LW - 192)
            y0 = 1046 - 20 * (len(ls) - 1)
            for k, ln in enumerate(ls): text(c, ln, 96, y0 + 20 * k, 15, FAINT, "sans", "l", P(t, 0.8, 1.6))

    def draw(self, c, t):        # override
        pass

    def render(self, c, t):
        self.background(c)
        self.chrome(c, t)
        self.draw(c, t)
        # fade in / out through the background colour
        f = min(P(t, 0.0, 0.55, lin), 1 - P(t, self.dur - 0.7, self.dur - 0.1, lin))
        if f < 0.999:
            c.drawRect(skia.Rect.MakeWH(LW, LH), paint(BG, 1 - clamp(f)))
