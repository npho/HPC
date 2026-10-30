"""Lustre-specific drawing helpers (on top of fx.py)."""
from fx import *

def vis(A, i, n_lines, d_in=0.9, d_out=0.9, delay=0.2):
    a = A.p(i, delay, d_in, smooth)
    if i + 1 < n_lines: a *= 1 - A.p(i + 1, 0.0, d_out, smooth)
    return a

def chip(c, x, y, label, color=AMBER, a=1.0, w=None, size=15):
    w = w or (tw(label, size, 'sans_m') + 18)
    rect(c, x - w / 2, y - 14, w, 28, fill=color, a=a, fa=0.9 * a, r=6)
    text(c, label, x, y + 6, size, BG, a, 'sans_b', align='c')

def poly_pt(pts, t):
    """point at fraction t (0..1) along a polyline"""
    t = clamp01(t)
    segs = [math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1)]
    tot = sum(segs) or 1; d = t * tot
    for i, s in enumerate(segs):
        if d <= s or i == len(segs) - 1:
            u = d / s if s else 0
            return (lerp(pts[i][0], pts[i+1][0], u), lerp(pts[i][1], pts[i+1][1], u))
        d -= s

def route_line(c, pts, color=FAINT, a=1.0, w=1.2, dash=None):
    for i in range(len(pts) - 1):
        line(c, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color, a, w, dash=dash)

def pkt(c, pts, t, color, a=1.0, s=9):
    if t <= 0 or t >= 1: return
    x, y = poly_pt(pts, t)
    rect(c, x - s/2, y - s/2, s, s, fill=color, a=a, fa=0.95 * a, r=2)

def label(c, s, x, y, size=18, color=DIM, a=1.0, kind='serif_i', align='c'):
    return text(c, s, x, y, size, color, a, kind, align)

def mono(c, s, x, y, size=18, color=INK, a=1.0, align='l'):
    return text(c, s, x, y, size, color, a, 'mono', align)

# ---------------------------------------------------------------- topology used by several scenes
FAB_X = 560
CLX, CLY, CLSP = 150, 300, 52
def client_xy(i, cols=3):
    return (CLX + (i % cols) * CLSP, CLY + (i // cols) * CLSP)
MDS_XY = (760, 215)
def oss_xy(k): return (990, 330 + k * 92)

def draw_clients(c, a=1.0, n=18, glow=None, cols=3):
    for i in range(n):
        x, y = client_xy(i, cols)
        g = 0.0 if glow is None else glow(i)
        node(c, x, y, 20, BLUE, a, glow=g)

def draw_fabric(c, a=1.0, y0=240, y1=720, lab=True):
    rect(c, FAB_X - 8, y0, 16, y1 - y0, fill=DIM, a=a, fa=0.30 * a, r=8, stroke=DIM, sw=1.2)
    if lab: label(c, 'network', FAB_X, y1 + 30, 17, DIM, a)

def draw_mds(c, a=1.0, name='MDS', lit=0.0, tgt='MDT', x=None, y=None):
    x0, y0 = (x if x is not None else MDS_XY[0]), (y if y is not None else MDS_XY[1])
    server(c, x0, y0, 120, 38, AMBER, a, lit)
    text(c, name, x0 + 60, y0 - 12, 19, AMBER, a, 'sans_m', align='c')
    disk(c, x0 + 150, y0 - 4, 28, 46, AMBER, a, fill=AMBER, fa=0.2)
    text(c, tgt, x0 + 164, y0 + 62, 15, AMBER, a, 'sans', align='c')

def draw_oss(c, k, a=1.0, lit=0.0, ndisk=3, name=None, tgt=True, x=None, y=None):
    x0, y0 = (x, y) if x is not None else oss_xy(k)
    server(c, x0, y0, 110, 36, VIOLET, a, lit)
    if name is not False:
        text(c, name or f'OSS {k+1}', x0 + 55, y0 - 10, 16, VIOLET, a, 'sans_m', align='c')
    for d in range(ndisk):
        disk(c, x0 + 135 + d * 40, y0 - 4, 28, 44, VIOLET, a, fill=VIOLET, fa=0.2)
    if tgt: text(c, 'OSTs', x0 + 195, y0 + 62, 14, VIOLET, a * 0.0 if k else a, 'sans', align='c')

def route_client(i, tx, ty, cols=3):
    cx, cy = client_xy(i, cols)
    return [(cx + 12, cy), (FAB_X, cy), (FAB_X, ty), (tx, ty)]
