"""Shared HUD, timing helper and drawing components for all scenes."""
import math
from engine import *

# The four questions get fixed colours so chapters read as a system.
Q_COL = dict(who="blue", first="yellow", where="green", how="orange")
CHAPTERS = {
    "Q": ("", "ink", ""),
    "H": ("ORIGINS", "dim", ""),
    "W": ("HOW IT RUNS  ·  the machinery", "orange", "4"),
    "V": ("WHO MAY RUN  ·  the vocabulary", "blue", "1"),
    "L": ("HOW IT RUNS  ·  life of a job", "orange", "4"),
    "F": ("WHO GOES FIRST", "yellow", "2"),
    "P": ("WHERE IT LANDS", "green", "3"),
    "S": ("IN PRACTICE  ·  typical setups", "dim", ""),
    "U": ("THE LARGER PICTURE", "dim", ""),
}
JOBCOL = ["blue", "teal", "orange", "purple", "green", "yellow", "red", "pink"]
MARGIN_X = 96


class Timing:
    """Per-scene narration cues. S.c(i): start of beat i (s); S.e(i): end; S.dur: scene length."""

    def __init__(self, cues, ends, dur):
        self.cues, self.ends, self.dur = cues, ends, dur

    def c(self, i, off=0.0):
        return self.cues[min(i, len(self.cues) - 1)] + off

    def e(self, i, off=0.0):
        return self.ends[min(i, len(self.ends) - 1)] + off

    def f(self, i, frac, off=0.0):
        """Time at fraction `frac` (0..1) through beat i - lets a visual land when the words do."""
        i = min(i, len(self.cues) - 1)
        return self.cues[i] + frac * (self.ends[i] - self.cues[i]) + off


def hud(cv, chapter, sources, t, dur):
    label, color, num = CHAPTERS.get(chapter, ("", "dim", ""))
    if label:
        x = MARGIN_X
        if num:
            cv.circle(x + 10, 55, 13, stroke=color, sw=1.6)
            cv.text(num, x + 10, 61, 17, color, "sans", "c")
            x += 34
        cv.text(label, x, 61, 17, color, "sans")
    if sources:
        cv.line(MARGIN_X, 1032, LW - MARGIN_X, 1032, "faint", 0.8)
        cv.text("sources  " + "  ·  ".join(sources), MARGIN_X, 1056, 15.5, "dim", "ital", a=0.95)


def headline(cv, text, t, t0=0.3, color="ink", y=128):
    a = appear(t, t0, 0.6)
    if a > 0:
        cv.text(text, MARGIN_X, y + (1 - a) * 10, 46, color, "ital", a=a)


def chip(cv, x, y, label, color="blue", a=1.0, size=18, face="mono", pad=11, fill=0.16, h=None):
    w = text_w(label, size, face) + pad * 2
    h = h or size + 14
    cv.rect(x, y - h + 6, w, h, fill=color, r=h / 2.6, a=a * fill)
    cv.rect(x, y - h + 6, w, h, stroke=color, sw=1.1, r=h / 2.6, a=a * 0.9)
    cv.text(label, x + pad, y - 1, size, color, face, a=a)
    return w


def box(cv, x, y, w, h, label, sub=None, color="blue", a=1.0, fill=0.13, r=9, size=24, face="mono", sw=1.4):
    cv.rect(x, y, w, h, fill=color, r=r, a=a * fill)
    cv.rect(x, y, w, h, stroke=color, sw=sw, r=r, a=a)
    if sub:
        cv.text(label, x + w / 2, y + h / 2 - 2, size, "ink", face, "c", a)
        cv.text(sub, x + w / 2, y + h / 2 + size * 0.95, size * 0.62, "dim", "ital", "c", a)
    else:
        cv.text(label, x + w / 2, y + h / 2 + size * 0.33, size, "ink", face, "c", a)


def cylinder(cv, x, y, w, h, color="teal", a=1.0, label=None):
    ry = h * 0.14
    cv.rect(x, y + ry, w, h - 2 * ry, fill=color, a=a * 0.13)
    cv.line(x, y + ry, x, y + h - ry, color, 1.4, a)
    cv.line(x + w, y + ry, x + w, y + h - ry, color, 1.4, a)
    for yy, op in ((y + ry, 1), (y + h - ry, 0)):
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(x, yy - ry, w, 2 * ry))
        cv.c.drawPath(p, cv.paint(color, a * (0.25 if op else 0.1)))
        cv.c.drawPath(p, cv.paint(color, a, stroke=True, sw=1.4))
    if label:
        cv.text(label, x + w / 2, y + h / 2 + 8, 19, "ink", "mono", "c", a)


def key_icon(cv, x, y, color="yellow", a=1.0, s=1.0):
    cv.circle(x, y, 5 * s, stroke=color, sw=1.5, a=a)
    cv.line(x + 5 * s, y, x + 17 * s, y, color, 1.5, a)
    cv.line(x + 13 * s, y, x + 13 * s, y + 4 * s, color, 1.5, a)
    cv.line(x + 17 * s, y, x + 17 * s, y + 4 * s, color, 1.5, a)


def mono_block(cv, x, y, lines, size=18, a=1.0, lh=1.36, color="ink"):
    """lines: str or (str, color). Returns y after the block."""
    for ln in lines:
        txt, c = (ln, color) if isinstance(ln, str) else ln
        cv.text(txt, x, y, size, c, "mono", a=a)
        y += size * lh
    return y


def tick_axis_x(cv, x, y, w, t0, t1, step, fmt="{:g}", a=1.0, size=15):
    cv.line(x, y, x + w, y, "rule", 1, a)
    v = t0
    while v <= t1 + 1e-9:
        px = x + (v - t0) / (t1 - t0) * w
        cv.line(px, y, px, y + 6, "rule", 1, a)
        cv.text(fmt.format(v), px, y + 22, size, "dim", "sans", "c", a)
        v += step


def stagger(t, t0, i, per=0.12, d=0.5):
    return appear(t, t0 + i * per, d)


def pulse(t, period=1.6, lo=0.55, hi=1.0):
    return lo + (hi - lo) * (0.5 + 0.5 * math.sin(2 * math.pi * t / period))


def tag_model(cv, x, y, a=1.0, label="MY TOY MODEL  ·  not Slurm code"):
    return tag(cv, x, y, label, "yellow", a)
