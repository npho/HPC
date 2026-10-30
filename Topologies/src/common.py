"""Shared helpers for scene modules."""
import math, json, os
from engine import *

from paths import DATA
R = json.load(open(DATA / "results.json"))


def head(c, s, a=1.0, y=128):
    text(c, s, 64, y, 38, "i", Pal.INK, a)


def note(c, s, x, y, a=1.0, size=19, color=Pal.MUTED, anchor="l"):
    return text(c, s, x, y, size, "i", color, a, anchor)


def label(c, s, x, y, a=1.0, size=18, color=Pal.MUTED, anchor="c"):
    return text(c, s, x, y, size, "r", color, a, anchor)


def big(c, s, x, y, a=1.0, size=64, color=Pal.INK, anchor="c", style="r"):
    return text(c, s, x, y, size, style, color, a, anchor)


def fade(t, t0, d=0.6):
    return ease(t, t0, d)


def host(c, x, y, a=1.0, col=Pal.BLUE, s=9):
    rect(c, x - s, y - s, 2 * s, 2 * s, col, a, r=2)


def switch(c, x, y, a=1.0, col=Pal.INK, r=13, fill=Pal.BG, sw=2.0):
    circle(c, x, y, r, fill, a, col, sw, a)


def bar_h(c, x, y, w, h, frac, color=Pal.BLUE, a=1.0):
    rect(c, x, y, max(0.0, w * clamp01(frac)), h, color, a)


def table(c, x, y, cols, rows, row_h=44, a=1.0, size=22, header_size=15):
    """cols: list of (title, width, anchor). rows: list of lists of str (or (str,color)).
    returns bottom y.  Header uses small caps + hairline rule (Tufte)."""
    cx = x
    for title, w, anc in cols:
        px = cx if anc == "l" else cx + w if anc == "r" else cx + w / 2
        small_caps(c, title, px, y, header_size, Pal.MUTED, a, anc)
        cx += w
    line(c, x, y + 10, x + sum(w for _, w, _ in cols), y + 10, Pal.FAINT, 1.2, a)
    yy = y + 10 + row_h * 0.72
    for r_ in rows:
        cx = x
        for (title, w, anc), val in zip(cols, r_):
            col = Pal.INK
            if isinstance(val, tuple):
                val, col = val
            px = cx if anc == "l" else cx + w if anc == "r" else cx + w / 2
            text(c, val, px, yy, size, "r", col, a, anc)
            cx += w
        yy += row_h
    return yy


def legend_dot(c, x, y, color, s, a=1.0, size=18):
    circle(c, x, y - 5, 6, color, a)
    text(c, s, x + 14, y, size, "r", Pal.MUTED, a)


# --- mini topology glyphs (used in several scenes) -----------------------------------
def ring_pts(cx, cy, r, n, rot=-math.pi / 2):
    return [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def glyph(c, kind, cx, cy, size=70, a=1.0, col=Pal.BLUE):
    """tiny topology icons"""
    s = size
    if kind == "tree":
        top = [(cx - s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy - s * 0.5)]
        bot = [(cx - s * 0.75 + i * s * 0.5, cy + s * 0.5) for i in range(4)]
        for tp in top:
            for b in bot:
                line(c, tp[0], tp[1], b[0], b[1], col, 1.2, a * 0.7)
        for tp in top:
            circle(c, tp[0], tp[1], 5, Pal.INK, a)
        for b in bot:
            circle(c, b[0], b[1], 4, col, a)
    elif kind == "torus":
        pts = [[(cx - s * 0.6 + j * s * 0.4, cy - s * 0.6 + i * s * 0.4) for j in range(4)] for i in range(4)]
        for i in range(4):
            for j in range(4):
                if j < 3:
                    line(c, *pts[i][j], *pts[i][j + 1], col, 1.2, a * 0.7)
                if i < 3:
                    line(c, *pts[i][j], *pts[i + 1][j], col, 1.2, a * 0.7)
        for i in range(4):
            curve(c, *pts[i][0], *pts[i][3], -s * 0.12 if False else s * 0.25, col, 1.0, a * 0.5)
            curve(c, *pts[0][i], *pts[3][i], s * 0.25, col, 1.0, a * 0.5)
        for row in pts:
            for p in row:
                circle(c, *p, 3.5, col, a)
    elif kind == "cube":
        sq = lambda o: [(cx - s * 0.4 + o, cy - s * 0.4 - o), (cx + s * 0.4 + o, cy - s * 0.4 - o),
                        (cx + s * 0.4 + o, cy + s * 0.4 - o), (cx - s * 0.4 + o, cy + s * 0.4 - o)]
        a1, a2 = sq(-s * 0.22), sq(s * 0.22)
        for P_ in (a1, a2):
            polyline(c, P_, col, 1.4, a * 0.8, closed=True)
        for p, q in zip(a1, a2):
            line(c, *p, *q, col, 1.4, a * 0.8)
        for p in a1 + a2:
            circle(c, *p, 3.5, col, a)
    elif kind == "hyperx":
        pts = [[(cx - s * 0.6 + j * s * 0.4, cy - s * 0.6 + i * s * 0.4) for j in range(4)] for i in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(j + 1, 4):
                    curve(c, *pts[i][j], *pts[i][k], 0 if k == j + 1 else -s * 0.12 * (k - j), col, 0.9, a * 0.6)
        for row in pts:
            for p in row:
                circle(c, *p, 3.5, col, a)
    elif kind == "petersen":
        outer = ring_pts(cx, cy, s * 0.6, 5)
        inner = ring_pts(cx, cy, s * 0.28, 5)
        for i in range(5):
            line(c, *outer[i], *outer[(i + 1) % 5], col, 1.2, a * 0.8)
            line(c, *outer[i], *inner[i], col, 1.2, a * 0.8)
            line(c, *inner[i], *inner[(i + 2) % 5], col, 1.2, a * 0.8)
        for p in outer + inner:
            circle(c, *p, 3.5, col, a)
    elif kind == "dragonfly":
        cs = ring_pts(cx, cy, s * 0.55, 5)
        for i, (gx, gy) in enumerate(cs):
            rp = ring_pts(gx, gy, s * 0.17, 4)
            for u in range(4):
                for v in range(u + 1, 4):
                    line(c, *rp[u], *rp[v], col, 0.9, a * 0.7)
            for p in rp:
                circle(c, *p, 2.6, col, a)
        for i in range(5):
            for j in range(i + 1, 5):
                line(c, *cs[i], *cs[j], Pal.GOLD, 0.9, a * 0.5)
