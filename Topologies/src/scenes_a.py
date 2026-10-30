"""Scenes 1-5: open, history, metrics, tree, oversub."""
from common import *
import random

SC = {}


def scene(fn):
    SC[fn.__name__.replace("s_", "")] = fn
    return fn


def bu(ctx, t, i, pad=0.0):
    """fraction of beat i elapsed (0..1)"""
    b0, b1 = ctx.b0(i), ctx.b1(i) + pad
    return clamp01((t - b0) / max(b1 - b0, 0.1))


# ------------------------------------------------------------------ 1 open
_rng = random.Random(7)
_COLS, _ROWS = 40, 25
_ORDER = list(range(_COLS * _ROWS)); _rng.shuffle(_ORDER)
_RANK = {k: i for i, k in enumerate(_ORDER)}


def morph_layouts(n=16):
    ring = ring_pts(960, 520, 300, n)
    grid = [(960 + (j - 1.5) * 150, 520 + (i - 1.5) * 150) for i in range(4) for j in range(4)]
    tree = []
    # 16 nodes as a 4-level fat-ish tree: 1,3,... simple layered layout: 2,4,4,6
    layers = [2, 4, 4, 6]
    for li, k in enumerate(layers):
        for j in range(k):
            tree.append((960 + (j - (k - 1) / 2) * 190, 300 + li * 150))
    ring_e = [(i, (i + 1) % n) for i in range(n)] + [(i, (i + 4) % n) for i in range(0, n, 2)]
    grid_e = [(i * 4 + j, i * 4 + j + 1) for i in range(4) for j in range(3)] + [(i * 4 + j, (i + 1) * 4 + j) for i in range(3) for j in range(4)]
    idx = 0; tree_e = []; starts = []
    for k in layers:
        starts.append(idx); idx += k
    for li in range(3):
        for a in range(layers[li]):
            for b in range(layers[li + 1]):
                if (a + b) % 2 == 0 or li == 0:
                    tree_e.append((starts[li] + a, starts[li + 1] + b))
    return [ring, grid, tree], [ring_e, grid_e, tree_e]


@scene
def s_open(c, t, ctx):
    u0 = bu(ctx, t, 0)
    # --- beat 0 : a thousand machines, one number
    if t < ctx.b0(1) + 0.4:
        out = 1 - fade(t, ctx.b0(1) - 0.2, 0.6)
        for k in range(_COLS * _ROWS):
            i, j = divmod(k, _COLS)
            x, y = 172 + j * 39.5, 190 + i * 29
            ap = fade(t, 0.9 + _RANK[k] / (_COLS * _ROWS) * 6.0, 0.5)
            col, a = Pal.BLUE, 0.85
            # converging wave: ring distance to center decides when a dot "gives" its piece
            d = math.hypot(x - 960, y - 465) / 820
            wave = prog(t, ctx.b0(0) + 0.55 * (ctx.b1(0) - ctx.b0(0)), 0.4 * (ctx.b1(0) - ctx.b0(0)))
            tt = clamp01((wave * 1.3) - (1 - d) * 0.0 - d * 0.3)
            if wave > 0:
                f = clamp01((wave * 1.35 - d * 0.55))
                x = lerp(x, 960, f * 0.82); y = lerp(y, 465, f * 0.82)
                col = mix(Pal.BLUE, Pal.GOLD, f)
            circle(c, x, y, 4.0, col, a * ap * out)
        if u0 > 0.8:
            a = fade(t, ctx.b0(0) + 0.8 * (ctx.b1(0) - ctx.b0(0)), 1.0) * out
            glow(c, 960, 465, 70, Pal.GOLD, 0.5 * a)
            big(c, "one number", 960, 700, a, 44, Pal.GOLD, "c", "i")
        small_caps(c, "1,000 machines × a piece each", 960, 160, 17, Pal.MUTED, fade(t, 1.5, 0.8) * out, "c")
    # --- beat 1 : the pattern is called a topology
    if ctx.b0(1) - 0.2 < t < ctx.b0(2) + 0.6:
        a_all = fade(t, ctx.b0(1) - 0.1, 0.8) * (1 - fade(t, ctx.b0(2) - 0.2, 0.6))
        lays, edges = morph_layouts()
        T = ctx.b1(1) - ctx.b0(1)
        ph = clamp01((t - ctx.b0(1)) / max(T, 1))
        # three layouts, ease between them
        s1, s2 = smooth(clamp01((ph - 0.28) / 0.17)), smooth(clamp01((ph - 0.62) / 0.17))
        pos = []
        for i in range(16):
            x = lerp(lerp(lays[0][i][0], lays[1][i][0], s1), lays[2][i][0], s2)
            y = lerp(lerp(lays[0][i][1], lays[1][i][1], s1), lays[2][i][1], s2)
            pos.append((x, y))
        wts = [1 - s1, s1 * (1 - s2), s2]
        for k in range(3):
            for (a, b) in edges[k]:
                line(c, *pos[a], *pos[b], Pal.BLUE, 2.0, 0.55 * wts[k] * a_all)
        for (x, y) in pos:
            circle(c, x, y, 9, Pal.INK, a_all, Pal.BLUE, 2, a_all)
        big(c, "topology", 960, 880, a_all * fade(t, ctx.b0(1) + 3.0, 1.0), 64, Pal.INK, "c", "i")
    # --- beat 2 : the roadmap
    if t > ctx.b0(2) - 0.1:
        items = [("tree", "fat tree"), ("torus", "torus"), ("cube", "hypercube"), ("hyperx", "HyperX"), ("dragonfly", "dragonfly")]
        T = ctx.b1(2) - ctx.b0(2)
        for k, (kind, name) in enumerate(items):
            x = 260 + k * 350
            a = fade(t, ctx.b0(2) + 0.4 + k * 0.45, 0.7)
            glyph(c, kind, x, 430, 150, a)
            text(c, name, x, 580, 30, "i", Pal.INK, a, "c")
        a = fade(t, ctx.b0(2) + 0.4 + 5 * 0.45 + 0.6, 0.8)
        line(c, 160, 660, 1760, 660, Pal.FAINT, 1.2, a)
        small_caps(c, "then", 160, 710, 15, Pal.MUTED, a)
        text(c, "collective algorithms  ·  schedulers  ·  a short tour of the proprietary names", 240, 716, 28, "r", Pal.INK, a)


# ------------------------------------------------------------------ 2 history
EVENTS = [
    (1953, "Clos", "three-stage non-blocking networks", "Bell System Tech. J.", "a", 0),
    (1981, "Cosmic Cube", "Seitz, Caltech: 4-node prototype 1981–82", "64 nodes, 6 links each", "b", 1),
    (1985, "Fat trees", "Leiserson", "IEEE Trans. Computers", "a", 2),
    (1987, "Virtual channels", "Dally & Seitz", "deadlock-free torus routing", "b", 2),
    (1990, "Low-dimension wins", "Dally", "under wiring limits", "a", 2),
    (2008, "Dragonfly", "Kim, Dally, Scott, Abts", "ISCA 2008", "a", 3),
    (2009, "HyperX", "Ahn et al.", "SC09", "b", 3),
]


@scene
def s_history(c, t, ctx):
    X = lambda y: 130 + (y - 1950) * (1660 / 62)
    ya = 640
    line(c, X(1950), ya, X(2012), ya, Pal.MUTED, 1.2, fade(t, 0.5, 1))
    for yr in range(1950, 2013, 10):
        line(c, X(yr), ya, X(yr), ya + 8, Pal.MUTED, 1.2, fade(t, 0.5, 1))
        text(c, str(yr), X(yr), ya + 32, 16, "r", Pal.MUTED, fade(t, 0.5, 1), "c")
    for k, (yr, name, who, where, side, beat) in enumerate(EVENTS):
        t0 = ctx.b0(beat) + (0.6 if yr == EVENTS[[e[5] for e in EVENTS].index(beat)][0] else 0.6 + 2.5 * (k - [e[5] for e in EVENTS].index(beat)))
        a = fade(t, t0, 0.6)
        x = X(yr)
        circle(c, x, ya, 7, Pal.GOLD, a)
        up = side == "a"
        stag = 0 if yr not in (1987, 2009) else 0
        y1 = ya - 40 if up else ya + 60
        y2 = ya - 150 if up else ya + 175
        yline_end = y2 + (10 if up else -34)
        line(c, x, ya + (-9 if up else 9), x, yline_end if True else y1, Pal.FAINT, 1.2, a)
        ty = y2 - (0 if up else 0)
        anc = "c"
        if yr in (1985,):
            ox = -40
        elif yr in (1987,):
            ox = 40
        elif yr in (2008,):
            ox = -60
        elif yr in (2009,):
            ox = 40
        else:
            ox = 0
        text(c, str(yr), x + ox, ty - (62 if up else -26), 26, "b", Pal.GOLD, a, anc)
        text(c, name, x + ox, ty - (30 if up else -58), 25, "r", Pal.INK, a, anc)
        text(c, who, x + ox, ty - (6 if up else -84), 18, "i", Pal.MUTED, a, anc)
        text(c, where, x + ox, ty + (16 if up else -108 + 192), 16, "i", Pal.MUTED, a, anc) if False else None
    # illustration panel (above timeline), swaps with beat
    # beat 0: three-stage clos
    p0 = fade(t, ctx.b0(0) + 3, 0.8) * (1 - fade(t, ctx.b0(1) - 0.2, 0.5))
    if p0 > 0:
        xs = [300, 520, 740]
        for s_i in range(3):
            for k in range(2):
                for m in range(2):
                    if s_i < 2:
                        line(c, xs[s_i], 245 + k * 80, xs[s_i + 1], 245 + m * 80, Pal.BLUE, 1.6, 0.5 * p0)
        for s_i in range(3):
            for k in range(2):
                rect(c, xs[s_i] - 16, 245 + k * 80 - 16, 32, 32, Pal.BG, p0, Pal.INK, 2, p0, r=4)
        small_caps(c, "input · middle · output", 520, 400, 15, Pal.MUTED, p0, "c")
    p1 = fade(t, ctx.b0(1) + 3, 0.8) * (1 - fade(t, ctx.b0(2) - 0.2, 0.5))
    if p1 > 0:
        cx, cy = 520, 300
        circle(c, cx, cy, 16, Pal.GOLD, p1)
        for k in range(6):
            ang = k * math.pi / 3
            ex, ey = cx + 120 * math.cos(ang), cy + 120 * math.sin(ang)
            line(c, cx, cy, ex, ey, Pal.BLUE, 2, 0.8 * p1)
            circle(c, ex, ey, 9, Pal.BLUE, p1)
        small_caps(c, "each processor ↔ six neighbours", 520, 470, 15, Pal.MUTED, p1, "c")
    p2 = fade(t, ctx.b0(2) + 1, 0.8) * (1 - fade(t, ctx.b0(3) - 0.2, 0.5))
    if p2 > 0:
        glyph(c, "tree", 380, 300, 150, p2)
        glyph(c, "torus", 700, 300, 150, p2)
        small_caps(c, "fat tree", 380, 440, 15, Pal.MUTED, p2, "c")
        small_caps(c, "torus + virtual channels", 700, 440, 15, Pal.MUTED, p2, "c")
    p3 = fade(t, ctx.b0(3) + 1, 0.8) * (1 - fade(t, ctx.b0(4) - 0.2, 0.5))
    if p3 > 0:
        glyph(c, "dragonfly", 1250, 300, 160, p3)
        glyph(c, "hyperx", 1560, 300, 150, p3)
    p4 = fade(t, ctx.b0(4) + 0.3, 0.9)
    if p4 > 0:
        for k, s in enumerate(["what is cheap?", "what is expensive?", "what traffic do you expect?"]):
            text(c, s, 960, 270 + k * 62, 46, "i", [Pal.GREEN, Pal.RED, Pal.GOLD][k], p4 * fade(t, ctx.b0(4) + 0.3 + k * 1.2, 0.8), "c")
    footer(c, "Clos 1953 · Seitz 1985 · Leiserson 1985 · Dally & Seitz 1987 · Dally 1990 · Kim et al. 2008 · Ahn et al. 2009", fade(t, 1, 1))


# ------------------------------------------------------------------ 3 metrics
LEAF_X = [230, 430, 630, 830]
SPINE_X = [330, 730]
Y_SP, Y_LF, Y_H = 330, 510, 650


def host_x(l, k, nper=2):
    return LEAF_X[l] + (k - (nper - 1) / 2) * 70


def mini_net(c, a=1.0, hl=None, extra=0.0, vis=None, linkcol=Pal.BLUE, cutcols=None):
    cutcols = cutcols or {}
    for l in range(4):
        for s_i in range(2):
            col = cutcols.get(("up", l, s_i), linkcol)
            line(c, LEAF_X[l], Y_LF, SPINE_X[s_i], Y_SP, col, 2.4 if col != linkcol else 2.0, a * (0.9 if col != linkcol else 0.55))
        for k in range(2):
            line(c, LEAF_X[l], Y_LF, host_x(l, k), Y_H, linkcol, 2.0, a * 0.55)
    if extra > 0:
        for k in (2, 3):
            xh = LEAF_X[0] + 70 + (k - 2) * 40
            line(c, LEAF_X[0], Y_LF, xh, Y_H, linkcol, 2.0, a * 0.55 * extra)
            host(c, xh, Y_H, a * extra)
    for l in range(4):
        for k in range(2):
            host(c, host_x(l, k), Y_H, a)
        switch(c, LEAF_X[l], Y_LF, a)
    for s_i in range(2):
        switch(c, SPINE_X[s_i], Y_SP, a)


@scene
def s_metrics(c, t, ctx):
    a0 = fade(t, ctx.b0(0) + 0.5, 1.0)
    cutcols = {}
    # beat 3: cut sweeps and crossing links go gold
    cut = fade(t, ctx.b0(3) + 2.0, 1.0)
    cut_out = fade(t, ctx.b0(4) - 0.2, 0.5)
    if cut > 0 and cut_out < 1:
        for (l, s_i) in [(2, 0), (3, 0), (0, 1), (1, 1)]:
            cutcols[("up", l, s_i)] = Pal.GOLD
    extra = fade(t, ctx.b0(4) + 3.0, 0.8) * (1 - fade(t, ctx.b0(5) - 0.2, 0.6))
    mini_net(c, a0, extra=extra, cutcols=cutcols if cut_out < 1 else {})
    # labels
    note(c, "hosts", 120, Y_H + 6, a0, 18, Pal.MUTED, "r")
    note(c, "leaf switches", 120, Y_LF + 6, a0, 18, Pal.MUTED, "r")
    note(c, "spine switches", 120, Y_SP + 6, a0, 18, Pal.MUTED, "r")
    # beat 0 caption
    if ctx.b0(0) < t < ctx.b0(1):
        note(c, "a graph:  endpoints · switches · links", 530, 250, fade(t, ctx.b0(0) + 1.5, 0.8), 24, Pal.INK, "c")
    # beat 1 : diameter
    if t >= ctx.b0(1) - 0.1:
        a = fade(t, ctx.b0(1), 0.6)
        path = [(host_x(0, 0), Y_H), (LEAF_X[0], Y_LF), (SPINE_X[0], Y_SP), (LEAF_X[3], Y_LF), (host_x(3, 1), Y_H)]
        pa = a * (1 - fade(t, ctx.b0(2) - 0.2, 0.5))
        if pa > 0:
            polyline(c, path, Pal.GOLD, 4, pa)
            packet(c, path, (t - ctx.b0(1)) / 4 % 1.0, Pal.GOLD, 8, pa, 0.1)
    # right panel: sticks
    X0 = 1010
    def stick(i, name, formula, t0):
        a = fade(t, t0, 0.7)
        y = 230 + i * 150
        small_caps(c, name, X0, y, 17, Pal.GOLD, a)
        line(c, X0, y + 12, X0 + 740, y + 12, Pal.FAINT, 1.2, a)
        return a, y
    a, y = stick(0, "Diameter", "", ctx.b0(1))
    text(c, "largest hop count over all pairs", X0, y + 50, 26, "r", Pal.INK, a)
    text(c, "here: 2 switch hops · sets the latency floor", X0, y + 88, 20, "i", Pal.MUTED, a)
    a, y = stick(1, "Radix", "", ctx.b0(2))
    text(c, "ports per switch · fixed by silicon", X0, y + 50, 26, "r", Pal.INK, a)
    text(c, "radix k = 4 here: k/2 face down, k/2 face up", X0, y + 88, 20, "i", Pal.MUTED, a)
    a, y = stick(2, "Bisection", "", ctx.b0(3))
    text(c, "least bandwidth across any equal split", X0, y + 50, 26, "r", Pal.INK, a)
    if cut > 0:
        rich(c, "$\\beta$ = bisection / (N/2 · b) = 4 / (4 · 1) = 1".replace("\\beta", "β"), X0, y + 100, 26, Pal.GOLD, a * cut)
    a, y = stick(3, "Cost", "", ctx.b0(5))
    text(c, "switch ports  ·  cables, especially long ones", X0, y + 50, 26, "r", Pal.INK, a)
    if t > ctx.b0(5) + 1.5:
        text(c, "here: 24 ports · 16 cables", X0, y + 88, 20, "i", Pal.MUTED, fade(t, ctx.b0(5) + 1.5, 0.6))
    # radix zoom (beat 2)
    ar = fade(t, ctx.b0(2) + 0.4, 0.6) * (1 - fade(t, ctx.b0(3) - 0.3, 0.5))
    if ar > 0:
        sx, sy = SPINE_X[0], Y_SP
        circle(c, sx, sy, 28, None, 1, Pal.GOLD, 3, ar)
        for k in range(4):
            ang = math.pi * (0.25 + 0.5 * k / 3) + math.pi
            ex, ey = sx + 60 * math.cos(ang + math.pi / 2 * 0), sy - 0
        for k in range(4):
            ang = math.radians(220 + k * 33)
            line(c, sx + 26 * math.cos(ang), sy + 26 * math.sin(ang), sx + 54 * math.cos(ang), sy + 54 * math.sin(ang), Pal.GOLD, 2.5, ar)
        small_caps(c, "k = 4 ports", sx, sy - 76, 16, Pal.GOLD, ar, "c")
    # bisection cut line
    if cut > 0 and cut_out < 1:
        ya, yb = 270, 700
        yy = lerp(ya, yb, cut)
        line(c, 530, ya, 530, yy, Pal.GOLD, 2.4, (1 - cut_out), dash=(9, 8))
        text(c, "4 links cross", 545, 296, 22, "i", Pal.GOLD, cut * (1 - cut_out))
    # beat 4 : narrower cut around leaf 0
    p4 = fade(t, ctx.b0(4) + 0.3, 0.7) * (1 - fade(t, ctx.b0(5) - 0.2, 0.6))
    if p4 > 0:
        rect(c, 150, 440, 240, 260, None, 1, Pal.RED, 2.4, p4, r=18, dash=(8, 7))
        for s_i in range(2):
            line(c, LEAF_X[0], Y_LF, SPINE_X[s_i], Y_SP, Pal.RED, 3.6, p4 * 0.9)
        text(c, "2 uplinks", 520, 430, 24, "i", Pal.RED, p4, "l") if False else None
        e = fade(t, ctx.b0(4) + 3.0, 0.8)
        note(c, "2 uplinks for 2 hosts: fine", 232, 770, p4 * (1 - e), 22, Pal.RED, "c")
        note(c, "2 uplinks for 4 hosts: β = 0.5", 232, 770, p4 * e, 22, Pal.RED, "c")
        note(c, "the balanced cut still says 1 — a particular cut says less", 530, 850, p4 * e, 22, Pal.INK, "c")


# ------------------------------------------------------------------ 4 tree
def binary_tree(depth=4):
    """returns node positions dict (level, idx) -> (x,y); leaves at bottom."""
    pos = {}
    n_leaf = 2 ** depth
    for l in range(depth + 1):
        n = 2 ** l
        for i in range(n):
            span = (n_leaf / n)
            x = 160 + (i * span + span / 2) * (1600 / n_leaf)
            y = 250 + l * ((650 - 250) / depth)
            pos[(l, i)] = (x, y)
    return pos


@scene
def s_tree(c, t, ctx):
    depth = 4
    # beats 0-1 : binary tree -> fat tree
    A = fade(t, ctx.b0(0) + 0.3, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if A > 0:
        pos = binary_tree(depth)
        grow = fade(t, ctx.b0(1) + 0.5, 3.5)
        for l in range(depth):
            for i in range(2 ** l):
                for ch in (2 * i, 2 * i + 1):
                    # width of link above node (l+1, ch) is proportional to leaves under it when grown
                    leaves_under = 2 ** (depth - (l + 1))
                    w = lerp(2.5, 2.5 + 3.0 * leaves_under ** 0.9 / 2.2, grow)
                    col = Pal.BLUE
                    if l == 0 and ch == 1 and grow < 0.5:
                        col = Pal.RED
                    line(c, *pos[(l, i)], *pos[(l + 1, ch)], col, w, A * 0.8)
        for (l, i), (x, y) in pos.items():
            if l == depth:
                host(c, x, y + 8, A)
            else:
                switch(c, x, y, A, r=10 if l else 14)
        # traffic: left half sends to right half through the root
        if t > ctx.b0(0) + 3.0:
            for k in range(8):
                lx = pos[(depth, k)]; rx = pos[(depth, 8 + k)]
                # path up the left tree, over root, down right tree
                pts = [(lx[0], lx[1] + 8)]
                i = k
                for l in range(depth, 0, -1):
                    i //= 2
                    pts.append(pos[(l - 1, i)])
                i = 8 + k
                down = []
                for l in range(depth, 0, -1):
                    i //= 2
                    down.append(pos[(l - 1, i)])
                pts += list(reversed(down))[1:] + [(rx[0], rx[1] + 8)]
                u = ((t - ctx.b0(0)) * 0.22 + k * 0.125) % 1.0
                packet(c, pts, u, Pal.GOLD if grow < 0.5 else Pal.GREEN, 5, A * 0.95)
        if grow < 0.5:
            rx, ry = pos[(1, 1)]
            note(c, "cut: one link wide", rx + 90, (pos[(0, 0)][1] + ry) / 2 - 10, A * fade(t, ctx.b0(0) + 5.0, 0.7), 24, Pal.RED, "l")
        else:
            note(c, "capacity at each level matches the traffic below it", 960, 770, A * grow, 24, Pal.INK, "c")
    # beat 2 : folded clos k=4 (2 levels)
    B = fade(t, ctx.b0(2) + 0.2, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if B > 0:
        lx = [300 + i * 220 for i in range(4)]
        sx = [410, 630]
        sy, ly, hy = 300, 500, 650
        for l in range(4):
            for s_i in range(2):
                line(c, lx[l], ly, sx[s_i] + 0, sy, Pal.BLUE, 2.4, 0.7 * B)
            for k in range(2):
                hx = lx[l] + (k - 0.5) * 70
                line(c, lx[l], ly, hx, hy, Pal.BLUE, 2.0, 0.55 * B)
                host(c, hx, hy, B)
        for l in range(4):
            switch(c, lx[l], ly, B, r=18)
        for s_i in range(2):
            switch(c, sx[s_i], sy, B, r=18)
        note(c, "spine", 150, sy + 6, B, 20, Pal.MUTED, "r")
        note(c, "leaf", 150, ly + 6, B, 20, Pal.MUTED, "r")
        note(c, "hosts", 150, hy + 6, B, 20, Pal.MUTED, "r")
        # right: the arithmetic
        X0 = 1130
        a1 = fade(t, ctx.b0(2) + 3.0, 0.7)
        small_caps(c, "identical switches, k ports each", X0, 250, 16, Pal.GOLD, a1)
        text(c, "½ ports down to hosts", X0, 300, 26, "r", Pal.INK, a1)
        text(c, "½ ports up to spines", X0, 340, 26, "r", Pal.INK, a1)
        text(c, "every leaf ↔ every spine", X0, 380, 26, "r", Pal.INK, a1)
        a2 = fade(t, ctx.b0(2) + 7.0, 0.7)
        rich(c, "hosts  =  $k^{2}$/2", X0, 470, 36, Pal.GOLD, a2)
        rich(c, "switches  =  3$k$/2", X0, 520, 36, Pal.GOLD, a2)
        rich(c, "k = 4  →  8 hosts · 6 switches", X0, 580, 26, Pal.MUTED, fade(t, ctx.b0(2) + 8.5, 0.7))
    # beat 3 : scale table
    C = fade(t, ctx.b0(3) + 0.3, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if C > 0:
        FT = R["fat_tree"]["sizes"]
        rows = [("two levels", "k = 64", FT["k64_2level"]), ("three levels", "k = 64", FT["k64_3level"])]
        small_caps(c, "64-port switches", 260, 250, 16, Pal.GOLD, C)
        small_caps(c, "hosts", 760, 250, 16, Pal.MUTED, C)
        small_caps(c, "switches", 1500, 250, 16, Pal.MUTED, C, "r")
        for k, (nm, kk, d) in enumerate(rows):
            y = 340 + k * 160
            a = fade(t, ctx.b0(3) + 1.0 + k * 3.0, 0.7)
            text(c, nm, 260, y + 8, 30, "i", Pal.INK, C * a)
            frac = math.log10(d["hosts"]) / math.log10(65536)
            bar_h(c, 760, y - 14, 520 * frac * a, 30, 1.0, Pal.BLUE, C * a)
            text(c, f"{d['hosts']:,}", 760 + 520 * frac * a + 16, y + 8, 30, "r", Pal.INK, C * a)
            text(c, f"{d['switches']:,}", 1500, y + 8, 30, "r", Pal.INK, C * a, "r")
        note(c, "bar length ∝ log of hosts", 760, 560, C, 18)
        rich(c, "$k^{3}$/4 hosts  on  5$k^{2}$/4 switches", 960, 700, 34, Pal.GOLD, C * fade(t, ctx.b0(3) + 5.5, 0.7), "c")
    # beat 4 : 3-level k=4 and the six-link path
    D = fade(t, ctx.b0(4) + 0.2, 0.8)
    if D > 0:
        pods = 4
        pw = 400
        hosts = []
        agg = {}; edge = {}; core = []
        for p in range(pods):
            px = 160 + p * pw + pw / 2
            for j in range(2):
                agg[(p, j)] = (px + (j - 0.5) * 140, 400)
                edge[(p, j)] = (px + (j - 0.5) * 140, 530)
                for h in range(2):
                    hosts.append(((p, j, h), (edge[(p, j)][0] + (h - 0.5) * 56, 650)))
        for j in range(4):
            core.append((160 + (j + 0.5) * 400, 250))
        hp = dict(hosts)
        for p in range(pods):
            for j in range(2):
                for jj in range(2):
                    line(c, *agg[(p, j)], *edge[(p, jj)], Pal.BLUE, 1.6, 0.45 * D)
                for cc in (2 * j, 2 * j + 1):
                    line(c, *agg[(p, j)], *core[cc], Pal.BLUE, 1.6, 0.4 * D)
                for h in range(2):
                    line(c, *edge[(p, j)], *hp[(p, j, h)], Pal.BLUE, 1.6, 0.45 * D)
        for p in range(pods):
            for j in range(2):
                switch(c, *agg[(p, j)], D, r=11); switch(c, *edge[(p, j)], D, r=11)
        for cp in core:
            switch(c, *cp, D, r=13)
        for _, hxy in hosts:
            host(c, hxy[0], hxy[1], D, s=6)
        # path from host (0,0,0) to (3,1,1)
        s_, d_ = hp[(0, 0, 0)], hp[(3, 1, 1)]
        pth = [s_, edge[(0, 0)], agg[(0, 0)], core[0], agg[(3, 0)], edge[(3, 1)], d_]
        pa = fade(t, ctx.b0(4) + 2.0, 0.8)
        polyline(c, pth, Pal.GOLD, 4, D * pa)
        packet(c, pth, ((t - ctx.b0(4) - 2.5) * 0.18) % 1.0, Pal.GOLD, 8, D * pa, 0.08)
        n_links = int(min(6, max(0, (t - ctx.b0(4) - 2.0) / 0.9)))
        big(c, f"{6 if t > ctx.b0(4) + 7.5 else n_links} links", 960, 800, D * pa, 54, Pal.GOLD, "c", "i")
        note(c, "k = 4, three levels: 16 hosts · 20 switches", 960, 860, D * pa, 22, Pal.MUTED, "c")


# ------------------------------------------------------------------ 5 oversub
@scene
def s_oversub(c, t, ctx):
    T = R["fat_tree"]["oversub_table_r64"]
    # beat 0 : 1:1 leaf
    A = fade(t, ctx.b0(0) + 0.3, 0.8) * (1 - fade(t, ctx.b0(1) - 0.3, 0.6))
    if A > 0:
        lx, ly = 700, 450
        for k in range(4):
            hx = lx - 180 + k * 120
            line(c, lx, ly, hx, 640, Pal.BLUE, 3, 0.7 * A); host(c, hx, 640, A)
            line(c, lx, ly, lx - 180 + k * 120, 260, Pal.GREEN, 3, 0.7 * A)
        switch(c, lx, ly, A, r=26)
        note(c, "k/2 down", lx + 260, 640, A, 22, Pal.MUTED, "l"); note(c, "k/2 up", lx + 260, 270, A, 22, Pal.MUTED, "l")
        big(c, "1 : 1", 1380, 400, A * fade(t, ctx.b0(0) + 3, 0.8), 110, Pal.GREEN, "c", "b")
        note(c, "non-blocking", 1380, 460, A * fade(t, ctx.b0(0) + 3, 0.8), 28, Pal.INK, "c")
        note(c, "≈ one extra cable per host for every level", 1380, 560, A * fade(t, ctx.b0(0) + 6, 0.8), 24, Pal.MUTED, "c")
    # beat 1 : 48 down, 16 up
    B = fade(t, ctx.b0(1) + 0.3, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if B > 0:
        lx, ly = 560, 480
        for k in range(12):
            hx = lx - 300 + k * 55
            line(c, lx, ly, hx, 680, Pal.BLUE, 1.6, 0.5 * B); host(c, hx, 680, B, s=6)
        for k in range(4):
            line(c, lx, ly, lx - 80 + k * 55, 280, Pal.GREEN, 4, 0.8 * B)
        switch(c, lx, ly, B, r=28)
        text(c, "48 ports down", lx, 740, 24, "r", Pal.BLUE, B, "c"); text(c, "16 ports up", lx, 244, 24, "r", Pal.GREEN, B, "c")
        # bandwidth bars
        X0 = 1050
        wd = fade(t, ctx.b0(1) + 3.0, 1.0)
        small_caps(c, "bandwidth at the leaf", X0, 330, 16, Pal.MUTED, B)
        bar_h(c, X0, 360, 600 * wd, 34, 1.0, Pal.BLUE, B); text(c, "down 48", X0 + 600 * wd + 14, 386, 24, "r", Pal.BLUE, B * wd)
        bar_h(c, X0, 420, 200 * wd, 34, 1.0, Pal.GREEN, B); text(c, "up 16", X0 + 200 * wd + 14, 446, 24, "r", Pal.GREEN, B * wd)
        e = fade(t, ctx.b0(1) + 6.0, 0.8)
        big(c, "3 : 1", X0 + 150, 600, B * e, 96, Pal.GOLD, "c", "b")
        note(c, "blocking factor = downlink ÷ uplink bandwidth", X0 + 10, 660, B * e, 24, Pal.INK, "l")
    # beat 2 : table
    C = fade(t, ctx.b0(2) + 0.3, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if C > 0:
        cols = [("down : up", 180, "l"), ("blocking", 150, "r"), ("hosts", 170, "r"), ("switches", 170, "r"), ("", 30, "l"), ("switches / 1,000 hosts", 450, "l"), ("uplink cables / host", 330, "r")]
        x = 150
        rows = []
        for r_ in T:
            rows.append([f"{r_['down']} : {r_['up']}", f"{r_['down'] / r_['up']:.2g} : 1", f"{r_['hosts']:,}", f"{r_['switches']}", "", "", f"{r_['uplink_cables'] / r_['hosts']:.2f}".rstrip("0").rstrip(".") if False else ("1" if r_['uplink_cables'] == r_['hosts'] else f"1/{round(r_['hosts'] / r_['uplink_cables'])}")])
        # reveal rows progressively
        for k, row in enumerate(rows):
            a = C * fade(t, ctx.b0(2) + 1.0 + k * 4.0, 0.7)
            pass
        # draw header + each row manually for the staggered reveal
        cx = x
        for title, w, anc in cols:
            px = cx if anc == "l" else cx + w if anc == "r" else cx + w / 2
            small_caps(c, title, px, 260, 15, Pal.MUTED, C, anc); cx += w
        line(c, x, 272, x + sum(w for _, w, _ in cols), 272, Pal.FAINT, 1.2, C)
        for k, row in enumerate(rows):
            a = C * fade(t, ctx.b0(2) + 1.0 + k * 4.0, 0.7)
            yy = 330 + k * 74
            cx = x
            for (title, w, anc), val in zip(cols, row):
                px = cx if anc == "l" else cx + w if anc == "r" else cx + w / 2
                if val:
                    col = [Pal.INK, Pal.GOLD, Pal.INK, Pal.INK, Pal.INK, Pal.INK, Pal.GREEN][cols.index((title, w, anc))]
                    text(c, val, px, yy, 32, "r", col, a, anc)
                cx += w
            per = T[k]["switches_per_1000_hosts"]
            bx = x + 180 + 150 + 170 + 170 + 30
            bar_h(c, bx, yy - 22, 340 * per / 50 * a, 26, 1.0, Pal.ORANGE, C * a)
            text(c, f"{per:.1f}", bx + 340 * per / 50 * a + 12, yy, 28, "r", Pal.INK, C * a)
        note(c, "64-port switches, two-level tree", x, 640, C * fade(t, ctx.b0(2) + 2, 0.6), 22)
        note(c, "3 : 1 reaches 3,072 hosts on 80 switches where 1 : 1 reached 2,048 on 96", x, 700, C * fade(t, ctx.b0(2) + 12, 0.8), 26, Pal.INK)
    # beat 3 : the leaf under load + the curve
    D = fade(t, ctx.b0(3) + 0.3, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        lx, ly = 420, 500
        for k in range(12):
            hx = lx - 260 + k * 47
            line(c, lx, ly, hx, 720, Pal.BLUE, 1.4, 0.5 * D); host(c, hx, 720, D, s=5)
        for k in range(3):
            xk = lx - 70 + k * 70
            line(c, lx, ly, xk, 300, Pal.GREEN, 4, 0.8 * D)
        switch(c, lx, ly, D, r=26)
        for k in range(12):
            hx = lx - 260 + k * 47
            for q in range(2):
                u = ((t - ctx.b0(3)) * 0.35 + k * 0.083 + q * 0.5) % 1.0
                tgt = (lx - 70 + (k % 3) * 70, 300)
                pts = [(hx, 720), (lx, ly), tgt]
                packet(c, pts, u, Pal.GOLD if u < 0.5 else Pal.RED, 4.5, D * (0.9 if u < 0.62 else 0.55))
        note(c, "48 senders, 16 uplinks → each gets 1/3", lx, 780, D, 22, Pal.INK, "c")
        # plot
        ax = Axes(960, 700, 1740, 300, (0, 1), (0, 1))
        a2 = D * fade(t, ctx.b0(3) + 2.5, 0.8)
        ax.frame(c, [0, 0.25, 0.5, 0.75, 1.0], [0, 0.5, 1.0], lambda v: f"{v:g}", lambda v: f"{v:g}", a2, 16,
                 "fraction of a host's traffic that leaves its leaf", "per-host throughput (× line rate)")
        pts = [(ax.X(f), ax.Y(min(1, (1 / 3) / f if f > 0 else 1))) for f in [i / 200 for i in range(0, 201)]]
        n = int(len(pts) * fade(t, ctx.b0(3) + 3.0, 2.5))
        polyline(c, pts[:max(2, n)], Pal.BLUE, 3.5, a2)
        pa = fade(t, ctx.b0(3) + 8.0, 0.7)
        circle(c, ax.X(0), ax.Y(1), 8, Pal.GREEN, D * pa)
        note(c, "job fits under one leaf", ax.X(0) + 18, ax.Y(1) - 14, D * pa, 20, Pal.GREEN)
        pb = fade(t, ctx.b0(3) + 12.0, 0.7)
        circle(c, ax.X(0.985), ax.Y(0.339), 8, Pal.RED, D * pb)
        note(c, "spread everywhere: ≈ 0.34", ax.X(0.985) + 4, ax.Y(0.339) + 40, D * pb, 20, Pal.RED, "r")
    # beat 4 : ratios multiply
    E = fade(t, ctx.b0(4) + 0.3, 0.9)
    if E > 0:
        X0 = 360
        levels = [("hosts", 9, Pal.BLUE), ("leaf uplinks", 3, Pal.GREEN), ("across the top", 1, Pal.GOLD)]
        for k, (nm, v, col) in enumerate(levels):
            a = fade(t, ctx.b0(4) + 1.0 + k * 2.5, 0.8)
            y = 330 + k * 120
            text(c, nm, X0 - 30, y + 12, 28, "i", Pal.INK, E * a, "r")
            bar_h(c, X0, y - 16, 90 * v * a, 44, 1.0, col, E * a)
            text(c, f"{v}", X0 + 90 * v * a + 16, y + 14, 34, "b", col, E * a)
            if k < 2:
                text(c, "÷ 3", X0 - 4, y + 78, 24, "i", Pal.MUTED, E * a * fade(t, ctx.b0(4) + 2.0 + k * 2.5, 0.6), "r")
        big(c, "3 : 1  ×  3 : 1  =  9 : 1", 1360, 430, E * fade(t, ctx.b0(4) + 8, 0.8), 52, Pal.GOLD, "c", "i")
        text(c, "ask for the blocking factor at each level,", 1360, 520, 26, "r", Pal.INK, E * fade(t, ctx.b0(4) + 11, 0.8), "c")
        text(c, "and whether the scheduler packs jobs beneath it", 1360, 558, 26, "r", Pal.INK, E * fade(t, ctx.b0(4) + 11, 0.8), "c")

s_metrics.dy = 40
s_tree.dy = 50
s_oversub.dy = 40
