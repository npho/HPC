"""Drawing helpers: a hybrid of 3Blue1Brown (dark canvas, motion, semantic colour) and Tufte
(data-ink discipline, direct labels, hairlines, serif type, marginal sidenotes, small multiples)."""
import skia, math, numpy as np

W, H = 1920, 1080          # logical canvas; scaled x2 for 4K

def C(r, g, b, a=255): return skia.Color(r, g, b, a)
BG    = (14, 17, 22)
INK   = (238, 232, 216)    # warm "paper" ink for text
DIM   = (146, 152, 162)
FAINT = (86, 93, 104)
RULE  = (52, 58, 68)
BLUE  = (88, 196, 221)     # data / clients / bandwidth
AMBER = (244, 208, 102)    # tokens, locks, metadata, attention
GREEN = (131, 193, 103)    # healthy, parity, spare, success
RED   = (252, 98, 85)      # failure, contention, bottleneck
VIOLET= (178, 148, 220)    # servers / NSD layer

def rgba(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))

def mix(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

def clamp01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def smooth(x):
    x = clamp01(x); return x * x * (3 - 2 * x)
def ease_out(x):
    x = clamp01(x); return 1 - (1 - x) ** 3
def ease_io(x):
    x = clamp01(x); return 0.5 * (1 - math.cos(math.pi * x))
def lerp(a, b, t): return a + (b - a) * t

_FD = '/usr/share/fonts/'
_FILES = {
    'serif':  _FD + 'truetype/google-fonts/Lora-Variable.ttf',
    'serif_i':_FD + 'truetype/google-fonts/Lora-Italic-Variable.ttf',
    'title':  _FD + 'truetype/google-fonts/Lora-Variable.ttf',
    'sans':   _FD + 'opentype/inter/Inter-Regular.otf',
    'sans_m': _FD + 'opentype/inter/Inter-Medium.otf',
    'sans_b': _FD + 'opentype/inter/Inter-SemiBold.otf',
    'mono':   _FD + 'truetype/dejavu/DejaVuSansMono.ttf',
}
_TF = {}; _FONT = {}
TS = 1.2
def font(kind, size):
    size = round(size * TS * 2) / 2
    k = (kind, size)
    if k not in _FONT:
        if kind not in _TF:
            _TF[kind] = skia.Typeface.MakeFromFile(_FILES[kind])
        f = skia.Font(_TF[kind], size)
        f.setSubpixel(True); f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
        _FONT[k] = f
    return _FONT[k]

_PAINT = skia.Paint(AntiAlias=True)
def P(color, a=1.0, style='fill', w=1.0, cap='butt', dash=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(rgba(color, a))
    if style == 'stroke':
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w)
        p.setStrokeCap({'butt': skia.Paint.kButt_Cap, 'round': skia.Paint.kRound_Cap}[cap])
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    return p

_FALL = {}
def _has(kind, ch):
    k = (kind, ch)
    if k not in _FALL:
        font(kind, 10)
        _FALL[k] = _TF[kind].unicharToGlyph(ord(ch)) != 0
    return _FALL[k]

def text(c, s, x, y, size=24, color=INK, a=1.0, kind='serif', align='l', track=0):
    if a <= 0.003: return 0
    if kind in ('serif', 'serif_i', 'title') and any(not _has(kind, ch) for ch in s):
        # split into runs, drawing missing glyphs with the sans face
        runs = []; cur = ''; cur_k = kind
        for ch in s:
            k2 = kind if _has(kind, ch) else 'sans'
            if k2 != cur_k and cur: runs.append((cur, cur_k)); cur = ''
            cur_k = k2; cur += ch
        if cur: runs.append((cur, cur_k))
        total = sum(font(k_, size).measureText(r) for r, k_ in runs)
        xx = x - (total / 2 if align == 'c' else total if align == 'r' else 0)
        for r, k_ in runs:
            c.drawString(r, xx, y, font(k_, size), P(color, a)); xx += font(k_, size).measureText(r)
        return total
    f = font(kind, size)
    p = P(color, a)
    if track:
        w = sum(f.measureText(ch) + track for ch in s) - track
        if align == 'c': x -= w / 2
        elif align == 'r': x -= w
        for ch in s:
            c.drawString(ch, x, y, f, p); x += f.measureText(ch) + track
        return w
    w = f.measureText(s)
    if align == 'c': x -= w / 2
    elif align == 'r': x -= w
    c.drawString(s, x, y, f, p)
    return w

def tw(s, size=24, kind='serif'):
    return font(kind, size).measureText(s)

def wrap(s, size, maxw, kind='serif'):
    f = font(kind, size); out = []; cur = ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if f.measureText(t) <= maxw: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

def para(c, s, x, y, maxw, size=24, color=INK, a=1.0, kind='serif', lh=1.38, align='l'):
    ys = y
    for ln in wrap(s, size, maxw, kind):
        text(c, ln, x, ys, size, color, a, kind, align); ys += size * lh
    return ys

def line(c, x1, y1, x2, y2, color=RULE, a=1.0, w=1.0, dash=None, cap='butt'):
    if a <= 0.003: return
    c.drawLine(x1, y1, x2, y2, P(color, a, 'stroke', w, cap, dash))

def rect(c, x, y, w, h, fill=None, stroke=None, a=1.0, sw=1.0, r=0, fa=None, dash=None):
    rr = skia.Rect.MakeXYWH(x, y, w, h)
    if fill is not None:
        p = P(fill, a if fa is None else fa)
        if r: c.drawRoundRect(rr, r, r, p)
        else: c.drawRect(rr, p)
    if stroke is not None:
        p = P(stroke, a, 'stroke', sw, dash=dash)
        if r: c.drawRoundRect(rr, r, r, p)
        else: c.drawRect(rr, p)

def circle(c, x, y, r, fill=None, stroke=None, a=1.0, sw=1.0, fa=None):
    if fill is not None: c.drawCircle(x, y, r, P(fill, a if fa is None else fa))
    if stroke is not None: c.drawCircle(x, y, r, P(stroke, a, 'stroke', sw))

def arrow(c, x1, y1, x2, y2, color=DIM, a=1.0, w=1.5, head=9, dash=None):
    if a <= 0.003: return
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - math.cos(ang) * head * 0.8, y2 - math.sin(ang) * head * 0.8
    c.drawLine(x1, y1, bx, by, P(color, a, 'stroke', w, dash=dash))
    path = skia.Path(); path.moveTo(x2, y2)
    path.lineTo(x2 - head * math.cos(ang - 0.38), y2 - head * math.sin(ang - 0.38))
    path.lineTo(x2 - head * math.cos(ang + 0.38), y2 - head * math.sin(ang + 0.38)); path.close()
    c.drawPath(path, P(color, a))

def curve(c, pts, color=DIM, a=1.0, w=1.5, dash=None):
    path = skia.Path(); path.moveTo(*pts[0])
    path.cubicTo(*pts[1], *pts[2], *pts[3])
    c.drawPath(path, P(color, a, 'stroke', w, dash=dash))

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])

def disk(c, x, y, w=34, h=44, color=DIM, a=1.0, fill=None, fa=0.25, sw=1.4, level=None, level_color=BLUE):
    """Cylinder icon (hard disk / LUN). (x,y) = top-left."""
    ry = h * 0.16
    if fill is not None:
        rect(c, x, y + ry, w, h - 2*ry, fill=fill, a=a, fa=fa*a)
        c.drawOval(skia.Rect.MakeXYWH(x, y + h - 2*ry, w, 2*ry), P(fill, fa*a))
    if level is not None and level > 0:
        lh = (h - 2*ry) * clamp01(level)
        rect(c, x, y + h - ry - lh, w, lh, fill=level_color, a=a, fa=0.55*a)
    p = P(color, a, 'stroke', sw)
    path = skia.Path(); path.moveTo(x, y + ry); path.lineTo(x, y + h - ry)
    path.arcTo(skia.Rect.MakeXYWH(x, y + h - 2*ry, w, 2*ry), 180, -180, False)
    path.lineTo(x + w, y + ry); c.drawPath(path, p)
    c.drawOval(skia.Rect.MakeXYWH(x, y, w, 2*ry), p)

def server(c, x, y, w=70, h=26, color=VIOLET, a=1.0, lit=0.0):
    rect(c, x, y, w, h, fill=color, stroke=color, a=a, sw=1.4, r=3, fa=(0.12 + 0.35*lit)*a)
    for i in range(3):
        circle(c, x + 9 + i*8, y + h/2, 1.8, fill=color if i or lit > 0.1 else DIM, a=a*0.9)
    line(c, x + w - 30, y + h/2, x + w - 8, y + h/2, color, a*0.7, 1.2)

def node(c, x, y, s=14, color=BLUE, a=1.0, glow=0.0, ring=None):
    rect(c, x - s/2, y - s/2, s, s, fill=color, a=a, fa=(0.30 + 0.6*glow)*a, r=2, stroke=color, sw=1.2)
    if ring is not None: circle(c, x, y, s*0.95, stroke=ring, a=a, sw=2)

def star(c, x, y, r, color=AMBER, a=1.0):
    path = skia.Path()
    for i in range(10):
        rr = r if i % 2 == 0 else r*0.45
        ang = -math.pi/2 + i*math.pi/5
        (path.moveTo if i == 0 else path.lineTo)(x + rr*math.cos(ang), y + rr*math.sin(ang))
    path.close(); c.drawPath(path, P(color, a))

def check(c, x, y, s=10, color=GREEN, a=1.0, w=2.5):
    path = skia.Path(); path.moveTo(x - s, y); path.lineTo(x - s*0.3, y + s*0.7); path.lineTo(x + s, y - s*0.7)
    c.drawPath(path, P(color, a, 'stroke', w, 'round'))

def cross(c, x, y, s=10, color=RED, a=1.0, w=2.5):
    line(c, x - s, y - s, x + s, y + s, color, a, w, cap='round'); line(c, x - s, y + s, x + s, y - s, color, a, w, cap='round')

def bracket(c, x1, x2, y, h=10, color=AMBER, a=1.0, w=2):
    path = skia.Path(); path.moveTo(x1, y - h); path.lineTo(x1, y); path.lineTo(x2, y); path.lineTo(x2, y - h)
    c.drawPath(path, P(color, a, 'stroke', w))

# ----------------------------------------------------------------- timing / scene chrome
class Anim:
    def __init__(self, t, cues, dur, ends=None):
        self.t, self.cues, self.dur = t, cues, dur
        self.ends = ends or [c + 10 for c in cues]
    def p(self, i, delay=0.0, d=1.0, f=ease_io):
        """progress (0..1) of an animation that starts `delay` s after line i begins."""
        return f((self.t - self.cues[i] - delay) / d)
    def started(self, i, delay=0.0): return self.t >= self.cues[i] + delay
    def at(self, i, delay=0.0): return self.t - self.cues[i] - delay    # seconds since
    def L(self, i): return self.ends[i] - self.cues[i]
    def tf(self, i, frac): return self.cues[i] + frac * self.L(i)
    def pf(self, i, f0, f1, f=ease_io):
        """progress between fractions f0..f1 of line i's duration"""
        a, b = self.tf(i, f0), self.tf(i, f1)
        return f((self.t - a) / max(b - a, 1e-6))
    def fade(self, i, delay=0.0, d=0.8): return self.p(i, delay, d, smooth)
    def out(self, i, delay=0.0, d=0.8): return 1 - self.p(i, delay, d, smooth)

LEFT, RIGHT = 120, 1380       # main figure column
NOTE_X, NOTE_W = 1450, 380    # marginal sidenote column

def chrome(c, A, title, num, notes=(), caption=None, cap_i=0, cap_delay=0.5):
    # running head: tracked small caps + hairline, Tufte style
    text(c, title.upper(), LEFT, 74, 17, DIM, 1.0, 'sans_m', track=3.2)
    text(c, f'{num:02d}', 1800, 74, 17, FAINT, 1.0, 'sans_m', align='r', track=2)
    line(c, LEFT, 94, 1800, 94, RULE, 1.0, 1.0)
    # sidenotes in the margin (Tufte): each (line_index, y, marker, text, delay)
    for (i, y, mark, s, *rest) in notes:
        dl = rest[0] if rest else 0.4
        a = A.fade(i, dl, 0.9)
        if a <= 0: continue
        text(c, mark, NOTE_X - 22, y, 14, AMBER, a, 'sans_m')
        text(c, '', 0, 0)
        yy = y
        for ln in wrap(s, 17, NOTE_W, 'serif_i'):
            text(c, ln, NOTE_X, yy, 17, DIM, a, 'serif_i'); yy += 27
    if caption:
        a = A.fade(cap_i, cap_delay, 0.9)
        lab, body = caption
        w = text(c, lab, LEFT, 1004, 19, INK, a, 'serif')
        text(c, body, LEFT + w + 8, 1004, 19, DIM, a, 'serif_i')

def hair_axis(c, x1, y1, x2, y2, a=1.0): line(c, x1, y1, x2, y2, FAINT, a, 1.0)
