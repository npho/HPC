"""Scenes 6-9: clos, routing, torus, hyper."""
from common import *
from scenes_a import bu

SC = {}


def scene(fn):
    SC[fn.__name__.replace("s_", "")] = fn
    return fn


SPINE_COLS = [Pal.BLUE, Pal.ORANGE, Pal.PURPLE, Pal.TEAL]


# ------------------------------------------------------------------ 6 clos
IN_X, ISW_X, MID_X, OSW_X, OUT_X = 260, 520, 960, 1400, 1660
ISW_Y = [330, 610]
MID_Y = [250, 470, 690]       # A (idx1), B (idx0), C (idx2) drawn top->bottom
IN_Y = [ISW_Y[0] - 40, ISW_Y[0] + 40, ISW_Y[1] - 40, ISW_Y[1] + 40]
MIDLAB = {1: ("A", MID_Y[0]), 0: ("B", MID_Y[1]), 2: ("C", MID_Y[2])}


def clos_path(inp, out, mid):
    isw, osw = inp // 2, out // 2
    return [(IN_X, IN_Y[inp]), (ISW_X, ISW_Y[isw]), (MIDLAB[mid][1] and MID_X, MIDLAB[mid][1]), (OSW_X, ISW_Y[osw]), (OUT_X, IN_Y[out])]


def xmark(c, x, y, a, s=13):
    line(c, x - s, y - s, x + s, y + s, Pal.RED, 5, a); line(c, x - s, y + s, x + s, y - s, Pal.RED, 5, a)


@scene
def s_clos(c, t, ctx):
    m3 = fade(t, ctx.b0(2) + 4.0, 0.9)           # third middle switch appears in beat 2
    m3_gone = 0 if t < ctx.b0(3) - 0.2 else fade(t, ctx.b0(3) - 0.2, 0.5)
    mids = [1, 0] + ([2] if m3 > 0 else [])
    a_net = fade(t, ctx.b0(0) + 0.3, 0.9)
    m3a = m3 * (1 - m3_gone)
    ra = (t - ctx.b0(3))
    # ---- links
    for mid in (1, 0, 2):
        al = a_net if mid != 2 else m3a
        if al <= 0:
            continue
        my = MIDLAB[mid][1]
        for s_ in range(2):
            line(c, ISW_X, ISW_Y[s_], MID_X, my, Pal.BLUE, 1.8, 0.35 * al)
            line(c, MID_X, my, OSW_X, ISW_Y[s_], Pal.BLUE, 1.8, 0.35 * al)
    for k in range(4):
        sw = k // 2
        line(c, IN_X, IN_Y[k], ISW_X, ISW_Y[sw], Pal.BLUE, 1.8, 0.5 * a_net)
        line(c, OSW_X, ISW_Y[sw], OUT_X, IN_Y[k], Pal.BLUE, 1.8, 0.5 * a_net)
    # ---- calls
    call1 = clos_path(1, 1, 1)
    call2 = clos_path(2, 2, 0)
    newp = clos_path(0, 3, 2)
    c_on = fade(t, ctx.b0(1) + 0.5, 0.8)
    # beat 3 : rearrangement: call1 moves from A to B, new call takes A
    reA = fade(t, ctx.b0(3) + 6.0, 1.5)
    call1_b = clos_path(1, 1, 0)
    if c_on > 0:
        if reA <= 0:
            polyline(c, call1, Pal.GOLD, 4.5, c_on)
        else:
            polyline(c, call1, Pal.GOLD, 4.5, c_on * (1 - reA)); polyline(c, call1_b, Pal.GOLD, 4.5, c_on * reA)
        polyline(c, call2, Pal.GOLD, 4.5, c_on)
    # beat 1: the blocked call
    nb = fade(t, ctx.b0(1) + 5.0, 0.7)
    if nb > 0 and t < ctx.b0(2) + 4.5 or (nb > 0 and ctx.b0(3) <= t < ctx.b0(3) + 6.0 and False):
        blocked_fade = 1 - fade(t, ctx.b0(2) + 4.0, 0.6)
        circle(c, IN_X, IN_Y[0], 14, None, 1, Pal.RED, 3, nb * blocked_fade)
        circle(c, OUT_X, IN_Y[3], 14, None, 1, Pal.RED, 3, nb * blocked_fade)
        text(c, "idle", IN_X - 62, IN_Y[0] + 6, 20, "i", Pal.RED, nb * blocked_fade, "r")
        text(c, "idle", OUT_X + 62, IN_Y[3] + 6, 20, "i", Pal.RED, nb * blocked_fade, "l")
        # try route via A: first link I0-A is busy ; via B: B-O1 busy
        pa = fade(t, ctx.b0(1) + 6.5, 0.8)
        line(c, ISW_X, ISW_Y[0], MID_X, MID_Y[0], Pal.RED, 4, nb * pa * blocked_fade)
        pb = fade(t, ctx.b0(1) + 9.0, 0.8)
        line(c, MID_X, MID_Y[1], OSW_X, ISW_Y[1], Pal.RED, 4, nb * pb * blocked_fade)
        xmark(c, (ISW_X + MID_X) / 2, (ISW_Y[0] + MID_Y[0]) / 2 - 6, nb * pa * blocked_fade)
        xmark(c, (MID_X + OSW_X) / 2 + 20, (MID_Y[1] + ISW_Y[1]) / 2 - 6, nb * pb * blocked_fade)
        if t > ctx.b0(1) + 11.0:
            big(c, "blocked", 960, 880, nb * fade(t, ctx.b0(1) + 11.0, 0.6) * blocked_fade, 60, Pal.RED, "c", "i")
    # beat 2: free route via C appears
    nc = fade(t, ctx.b0(2) + 6.0, 0.8) * (1 - m3_gone)
    if nc > 0:
        polyline(c, newp, Pal.GREEN, 4.5, nc)
        packet(c, newp, ((t - ctx.b0(2) - 6.5) * 0.25) % 1.0, Pal.GREEN, 7, nc, 0.1)
    # beat 3 rearrange: the new call routes via A
    nr = fade(t, ctx.b0(3) + 8.0, 0.8)
    if nr > 0:
        polyline(c, clos_path(0, 3, 1), Pal.GREEN, 4.5, nr)
    # nodes
    for k in range(4):
        host(c, IN_X, IN_Y[k], a_net, Pal.BLUE if True else Pal.BLUE); host(c, OUT_X, IN_Y[k], a_net, Pal.BLUE)
        text(c, str(k), IN_X - 26, IN_Y[k] + 6, 18, "r", Pal.MUTED, a_net, "r"); text(c, str(k), OUT_X + 26, IN_Y[k] + 6, 18, "r", Pal.MUTED, a_net, "l")
    for s_ in range(2):
        rect(c, ISW_X - 24, ISW_Y[s_] - 62, 48, 124, Pal.BG, a_net, Pal.INK, 2.2, a_net, r=8)
        rect(c, OSW_X - 24, ISW_Y[s_] - 62, 48, 124, Pal.BG, a_net, Pal.INK, 2.2, a_net, r=8)
    for mid in (1, 0, 2):
        al = a_net if mid != 2 else m3a
        if al <= 0:
            continue
        lab, my = MIDLAB[mid]
        rect(c, MID_X - 28, my - 28, 56, 56, Pal.BG, al, Pal.GREEN if mid == 2 else Pal.INK, 2.2, al, r=8)
        text(c, lab, MID_X, my + 8, 26, "b", Pal.GREEN if mid == 2 else Pal.MUTED, al, "c")
    rich(c, "input switches  ($n$ = 2 inputs each)", ISW_X, 200, 20, Pal.MUTED, a_net, "c")
    rich(c, f"middle switches  ($m$ = {3 if m3a > 0.5 else 2})", MID_X, 160, 22, Pal.GOLD if m3a < .5 else Pal.GREEN, a_net, "c")
    text(c, "output switches", OSW_X, 200, 20, "r", Pal.MUTED, a_net, "c")
    # beat 2 formula
    f = fade(t, ctx.b0(2) + 8.5, 0.8) * (1 - m3_gone)
    if f > 0:
        rich(c, "input side blocks ≤ $n$−1 middles; output side ≤ $n$−1 more", 960, 830, 26, Pal.INK, f, "c")
        rich(c, "$m$ = 2$n$−1  →  one is always free   (strictly non-blocking)", 960, 876, 32, Pal.GREEN, f, "c")
    # beat 3 numbers
    n3 = fade(t, ctx.b0(3) + 0.3, 0.7)
    if n3 > 0 and reA <= 0.01 and False:
        pass
    if n3 > 0:
        cl = R["clos"]
        y0 = 800
        a_ = n3
        text(c, f"m = 2 (= n):  {cl['n2_r2_m2']['states']} reachable states,", 360, y0, 26, "r", Pal.INK, a_, "l")
        text(c, f"{cl['n2_r2_m2']['blocking_states']} of them blocking", 900, y0, 26, "b", Pal.RED, a_, "l")
        text(c, f"m = 3:  {cl['n2_r2_m3']['states']:,} states,", 1250, y0, 26, "r", Pal.INK, a_, "l")
        text(c, "0 blocking", 1520, y0, 26, "b", Pal.GREEN, a_, "l")
        text(c, "with m = 2 a rearrangement always exists (0 failures)", 960, y0 + 48, 24, "i", Pal.MUTED, a_ * fade(t, ctx.b0(3) + 5.0, 0.7), "c")
    # beat 4 summary
    s4 = fade(t, ctx.b0(4) + 0.3, 0.9)
    if s4 > 0:
        rect(c, 0, 120, DW, 900, Pal.BG, s4)
        rows = [("m ≥ 2n − 1", "strictly non-blocking", "any new call finds a free route", Pal.GREEN),
                ("m ≥ n", "rearrangeably non-blocking", "…if calls in progress may be moved", Pal.GOLD),
                ("m < n", "blocking", "even with both ends idle", Pal.RED)]
        for k, (a1, a2, a3, col) in enumerate(rows):
            a = s4 * fade(t, ctx.b0(4) + 0.8 + k * 1.2, 0.8)
            y = 300 + k * 130
            text(c, a1, 520, y, 44, "i", col, a, "r")
            text(c, a2, 570, y - 6, 34, "r", Pal.INK, a, "l")
            text(c, a3, 570, y + 32, 22, "i", Pal.MUTED, a, "l")
        b = s4 * fade(t, ctx.b0(4) + 5.0, 0.9)
        text(c, "data center:  calls = flows,  rearranging = routing", 960, 760, 34, "r", Pal.INK, b, "c")
        text(c, "do the wires you paid for get used?  that depends on how flows are routed.", 960, 810, 26, "i", Pal.MUTED, b, "c")
    footer(c, "Clos 1953, BSTJ 32(2) · brute force: n = 2, r = 2 (this video's models)", a_net)


# ------------------------------------------------------------------ 7 routing
NH = 16
HX = lambda h: 140 + h * 58.5 + (h // 4) * 24
LX = lambda l: sum(HX(l * 4 + k) for k in range(4)) / 4
SPX = lambda s_: 250 + s_ * 230
SPY, LFY, HYY = 280, 500, 690


def routing_net(c, a, spines, rates=None, color_by_spine=True, loads=True):
    D = R["permutations"]["demo"]
    pairs = D["pairs"]
    up = {}; dn = {}
    for (s_, d_), sp in zip(pairs, spines):
        up[(s_ // 4, sp)] = up.get((s_ // 4, sp), 0) + 1
        dn[(sp, d_ // 4)] = dn.get((sp, d_ // 4), 0) + 1
    for l in range(4):
        for sp in range(4):
            line(c, LX(l), LFY, SPX(sp), SPY, Pal.FAINT, 1.4, a)
    for (s_, d_), sp in zip(pairs, spines):
        l1, l2 = s_ // 4, d_ // 4
        col = SPINE_COLS[sp] if color_by_spine else Pal.GOLD
        ov = max(up[(l1, sp)], dn[(sp, l2)]) > 1
        line(c, HX(s_), HYY, LX(l1), LFY, col, 1.8, 0.8 * a)
        line(c, LX(l2), LFY, HX(d_), HYY, col, 1.8, 0.8 * a, dash=(4, 4))
        line(c, LX(l1), LFY, SPX(sp), SPY, col, 3.0, 0.85 * a)
        line(c, SPX(sp), SPY, LX(l2), LFY, col, 3.0, 0.85 * a)
    if loads:
        for (l, sp), n in up.items():
            if n > 1:
                x, y = (LX(l) + SPX(sp)) / 2, (LFY + SPY) / 2
                circle(c, x, y, 11, Pal.RED, a); text(c, str(n), x, y + 6, 17, "b", Pal.BG, a, "c")
        for (sp, l), n in dn.items():
            if n > 1:
                x, y = (LX(l) + SPX(sp)) / 2 + 22, (LFY + SPY) / 2 + 18
                circle(c, x, y, 11, Pal.RED, a); text(c, str(n), x, y + 6, 17, "b", Pal.BG, a, "c")
    for h in range(NH):
        host(c, HX(h), HYY, a, Pal.MUTED, 7)
    for l in range(4):
        switch(c, LX(l), LFY, a, r=16)
    for sp in range(4):
        switch(c, SPX(sp), SPY, a, r=16, col=SPINE_COLS[sp])
    note(c, "spines", 90, SPY + 6, a, 18, Pal.MUTED, "r"); note(c, "leaves", 90, LFY + 6, a, 18, Pal.MUTED, "r"); note(c, "hosts", 90, HYY + 6, a, 18, Pal.MUTED, "r")


@scene
def s_routing(c, t, ctx):
    D = R["permutations"]["demo"]; P_ = R["permutations"]["leafspine_16x16_1to1"]
    A = fade(t, ctx.b0(0) + 0.3, 0.9)
    plan = fade(t, ctx.b0(1) + 8.0, 1.0)
    sp = D["ecmp_spine"] if plan < 0.5 else D["perfect_spine"]
    routing_net(c, A, sp)
    # per-demo caption
    if plan < 0.5:
        m = sum(D["ecmp_rate"]) / len(D["ecmp_rate"])
        note(c, f"hashing, one random permutation on a 4×4 demo: mean flow rate {m:.2f}   (ranges {min(D['ecmp_rate']):.2f} – 1.00)", 560, 790, A * fade(t, ctx.b0(0) + 6, 0.8), 22, Pal.INK, "c")
    else:
        note(c, "planned (edge-coloured) routing, same traffic: every flow 1.00", 560, 790, plan, 22, Pal.GREEN, "c")
    # right: bipartite graph for beat 1
    b1 = fade(t, ctx.b0(1) + 0.5, 0.9) * (1 - fade(t, ctx.b0(2) + 4, 0.8))
    X1, X2 = 1350, 1700
    if b1 > 0:
        small_caps(c, "König: leaves = nodes, flows = edges, spines = colours", 1525, 190, 15, Pal.MUTED, b1, "c")
        for l in range(4):
            yy = 260 + l * 90
            circle(c, X1, yy, 14, Pal.BG, b1, Pal.INK, 2, b1); circle(c, X2, yy, 14, Pal.BG, b1, Pal.INK, 2, b1)
            text(c, f"L{l}", X1 - 26, yy + 6, 18, "r", Pal.MUTED, b1, "r"); text(c, f"L{l}", X2 + 26, yy + 6, 18, "r", Pal.MUTED, b1, "l")
        cols = SPINE_COLS
        for (s_, d_), spn in zip(D["pairs"], D["perfect_spine"]):
            ap = fade(t, ctx.b0(1) + 4.0 + (s_ % 7) * 0.4, 0.5)
            y1, y2 = 260 + (s_ // 4) * 90, 260 + (d_ // 4) * 90
            line(c, X1 + 14, y1 + ((s_ % 4) - 1.5) * 3, X2 - 14, y2 + ((d_ % 4) - 1.5) * 3, cols[spn], 2.2, 0.9 * b1 * ap)
        note(c, "no node sees a colour twice", 1525, 660, b1 * fade(t, ctx.b0(1) + 9, 0.7), 22, Pal.INK, "c")
    # right: the dot plot (beats 0 -> 2)
    pl = fade(t, ctx.b0(0) + 7.0, 0.9)
    if pl > 0:
        ax = Axes(1250, 800 + 0, 1790, 200, (0, 1), (0, 1))
        # horizontal range-frame dot plot : rows at fixed y
        x0, x1 = 1250, 1780
        X = lambda v: lerp(x0, x1, v)
        ypl = {"hash": 890, "dmodk": 940, "plan": 990}
        base = 870
        rowsd = [("hashing (ECMP)", P_["ecmp"], Pal.RED, 0.0), ("static by destination", P_["dmodk"], Pal.ORANGE, 1.4), ("planned colouring", P_["perfect"], Pal.GREEN, 0.0)]
        show = [pl, pl * fade(t, ctx.b0(0) + 11, 0.7), fade(t, ctx.b0(1) + 8.5, 0.8)]
        if b1 > 0.01:
            pass
        # place the plot lower-right when bipartite graph is present
        yb = 770 if b1 > 0.01 or t > ctx.b0(1) else 520
        yb = lerp(520, 790, fade(t, ctx.b0(1) + 0.2, 0.8))
        small_caps(c, "mean flow rate, 200 random permutations", 1250, yb - 70, 15, Pal.MUTED, pl)
        for k, (nm, d, col, _) in enumerate(rowsd):
            y = yb + k * 52
            a = show[k]
            if a <= 0:
                continue
            text(c, nm, x0 - 14, y + 6, 20, "r", Pal.INK, a, "r")
            line(c, X(d["p5"]), y, X(d["p95"]), y, col, 3, a * 0.8)
            circle(c, X(d["mean"]), y, 7, col, a)
            text(c, f"{d['mean'] * 100:.0f}%", X(d["p95"]) + 14, y + 6, 20, "b", col, a, "l")
        line(c, x0, yb + 130, x1, yb + 130, Pal.MUTED, 1.2, pl)
        for v in (0, 0.5, 1.0):
            line(c, X(v), yb + 130, X(v), yb + 137, Pal.MUTED, 1.2, pl); text(c, f"{v:g}", X(v), yb + 156, 15, "r", Pal.MUTED, pl, "c")
        if t > ctx.b0(0) + 14:
            mn = P_["ecmp_min"]["mean"]
            circle(c, X(mn), yb, 5, Pal.RED, pl * fade(t, ctx.b0(0) + 14, 0.7), None)
            note(c, "unluckiest flow ≈ 0.22", X(mn), yb - 18, pl * fade(t, ctx.b0(0) + 14, 0.7), 16, Pal.RED, "c")
    # beat 2
    s2 = fade(t, ctx.b0(2) + 4.0, 0.9)
    if s2 > 0:
        rect(c, 1130, 150, 790, 720, Pal.BG, s2 * 0.0)
        text(c, "the topology says what is possible", 1525, 330, 30, "i", Pal.INK, s2, "c")
        text(c, "the routing decides what you get", 1525, 380, 30, "i", Pal.GOLD, s2 * fade(t, ctx.b0(2) + 6.0, 0.7), "c")
        for k, s_ in enumerate(["hashing", "adaptive routing in the switch", "a central planner (subnet manager)"]):
            text(c, "· " + s_, 1330, 450 + k * 40, 24, "r", Pal.MUTED, s2 * fade(t, ctx.b0(2) + 8.0 + k * 1.0, 0.7), "l")
    footer(c, "this video's flow model: 16 leaves × 16 hosts, 1:1 · edge colouring (König)", A)


# ------------------------------------------------------------------ 8 torus
def iso(x, y, z, s=70, ox=960, oy=520):
    return (ox + (x - y * 0.55) * s, oy + (y * 0.4 - z) * s * 1.0 + (x * 0.0))


@scene
def s_torus(c, t, ctx):
    # ---------------- beat 0 : line -> ring -> grid/torus -> 3D
    A = fade(t, ctx.b0(0) + 0.2, 0.8) * (1 - fade(t, ctx.b0(1) - 0.3, 0.6))
    if A > 0:
        u = bu(ctx, t, 0)
        # phase 1: 1D mesh then ring
        p1 = (1 - smooth(clamp01((u - 0.30) / 0.05)))
        if p1 > 0:
            xs = [560 + i * 160 for i in range(6)]
            for i in range(5):
                line(c, xs[i], 520, xs[i + 1], 520, Pal.BLUE, 3, A * p1)
            wr = fade(t, ctx.b0(0) + (ctx.b1(0) - ctx.b0(0)) * 0.10, 1.2)
            curve(c, xs[0], 520, xs[-1], 520, -150, Pal.GOLD, 3, A * p1, p=wr)
            for x in xs:
                circle(c, x, 520, 10, Pal.INK, A * p1, Pal.BLUE, 2, A * p1)
            note(c, "n = 1:  a line is a mesh; join the ends and it is a ring", 960, 760, A * p1, 26, Pal.INK, "c")
        # phase 2: 2D
        p2 = smooth(clamp01((u - 0.30) / 0.05)) * (1 - smooth(clamp01((u - 0.62) / 0.05)))
        if p2 > 0:
            n = 5; sp = 130
            gx = lambda j: 960 - (n - 1) * sp / 2 + j * sp
            gy = lambda i: 500 - (n - 1) * sp / 2 + i * sp
            wr = fade(t, ctx.b0(0) + (ctx.b1(0) - ctx.b0(0)) * 0.42, 1.8)
            for i in range(n):
                for j in range(n):
                    if j < n - 1:
                        line(c, gx(j), gy(i), gx(j + 1), gy(i), Pal.BLUE, 2.4, A * p2)
                    if i < n - 1:
                        line(c, gx(j), gy(i), gx(j), gy(i + 1), Pal.BLUE, 2.4, A * p2)
            for i in range(n):
                curve(c, gx(0), gy(i), gx(n - 1), gy(i), -80 - 8 * i if False else 150 if i % 2 else -150, Pal.GOLD, 2.2, A * p2 * 0.9, p=wr) if False else None
                curve(c, gx(0), gy(i), gx(n - 1), gy(i), 70 + (i - 2) * 0 + 30 * abs(i - 2) if i < 2 else -(70 + 30 * abs(i - 2)) if i > 2 else 0.1, Pal.GOLD, 2.0, A * p2 * 0.85, p=wr)
                curve(c, gx(i), gy(0), gx(i), gy(n - 1), 70 + 30 * abs(i - 2) if i < 2 else -(70 + 30 * abs(i - 2)) if i > 2 else 0.1, Pal.GOLD, 2.0, A * p2 * 0.85, p=wr)
            for i in range(n):
                for j in range(n):
                    circle(c, gx(j), gy(i), 9, Pal.INK, A * p2, Pal.BLUE, 2, A * p2)
            note(c, "n = 2:  wrap the rows and columns and you have a torus", 960, 880, A * p2, 26, Pal.INK, "c")
        # phase 3: 3D
        p3 = smooth(clamp01((u - 0.62) / 0.05))
        if p3 > 0:
            n = 4
            pts = {}
            for x in range(n):
                for y in range(n):
                    for z in range(n):
                        pts[(x, y, z)] = iso(x - 1.5, y - 1.5, z - 1.5, 105, 960, 500)
            wr = fade(t, ctx.b0(0) + (ctx.b1(0) - ctx.b0(0)) * 0.78, 1.8)
            for (x, y, z), p in pts.items():
                for d in range(3):
                    q = [x, y, z]; q[d] += 1
                    if tuple(q) in pts:
                        line(c, *p, *pts[tuple(q)], Pal.BLUE, 1.6, A * p3 * 0.65)
            for (x, y, z), p in pts.items():
                for d in range(3):
                    if (x, y, z)[d] == 0:
                        q = [x, y, z]; q[d] = n - 1
                        if d == 2 and (x + y) % 2 == 0 or d != 2 and (x + y + z) % 2 == 0:
                            curve(c, *p, *pts[tuple(q)], 55 if d != 1 else -55, Pal.GOLD, 1.3, A * p3 * 0.5, p=wr)
            for p in pts.values():
                circle(c, *p, 6.5, Pal.INK, A * p3, Pal.BLUE, 1.5, A * p3)
            note(c, "n = 3:  the shape behind many famous machines", 960, 960, A * p3, 26, Pal.INK, "c") if False else None
            note(c, "n = 3:  the shape behind many famous machines", 960, 920, A * p3, 26, Pal.INK, "c")
    # ---------------- beat 1 : one node, 2n links
    B = fade(t, ctx.b0(1) + 0.2, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if B > 0:
        cx, cy = 700, 500
        rect(c, cx - 50, cy - 50, 100, 100, Pal.BG, B, Pal.INK, 3, B, r=10)
        text(c, "node", cx, cy - 4, 22, "i", Pal.INK, B, "c"); text(c, "+ router", cx, cy + 22, 18, "r", Pal.MUTED, B, "c")
        dirs = [("+x", 1, 0), ("−x", -1, 0), ("+y", 0, -1), ("−y", 0, 1), ("+z", .7, -.7), ("−z", -.7, .7)]
        for k, (nm, dx, dy) in enumerate(dirs):
            a = B * fade(t, ctx.b0(1) + 1.0 + k * 0.9, 0.6)
            line(c, cx + dx * 50, cy + dy * 50, cx + dx * 200, cy + dy * 200, Pal.BLUE, 3, a)
            circle(c, cx + dx * 200, cy + dy * 200, 11, Pal.INK, a, Pal.BLUE, 2, a)
            text(c, nm, cx + dx * 238, cy + dy * 238 + 7, 22, "i", Pal.GOLD, a, "c")
        a2 = B * fade(t, ctx.b0(1) + 4.5, 0.8)
        rich(c, "links per node  =  2$n$", 1250, 400, 44, Pal.GOLD, a2)
        text(c, "however large the machine", 1250, 450, 28, "i", Pal.INK, a2)
        for k, s_ in enumerate(["no giant switches", "no growing radix", "almost every cable joins neighbours"]):
            text(c, "· " + s_, 1250, 530 + k * 44, 28, "r", Pal.INK, B * fade(t, ctx.b0(1) + 5.5 + k * 1.2, 0.7))
    # ---------------- beat 2 : measuring sticks vs N
    C = fade(t, ctx.b0(2) + 0.2, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if C > 0:
        BC = R["cubes"]["beta_curves"]
        N = BC["N"]; cv = BC["curves"]
        ax = Axes(760, 780, 1740, 250, (64, N[-1]), (0, 2.0), xlog=True)
        ax.frame(c, [64, 512, 4096, 32768, 262144], [0, 0.5, 1.0, 1.5, 2.0], lambda v: f"{int(v):,}", lambda v: f"{v:g}", C, 16, "nodes N", "β  (bisection ÷ injection)")
        spec = [("2D torus", Pal.BLUE), ("3D torus", Pal.TEAL), ("5D torus", Pal.PURPLE), ("fat tree 1:1", Pal.GREEN), ("fat tree 3:1", Pal.ORANGE)]
        prog_ = fade(t, ctx.b0(2) + 6.0, 4.0)
        for nm, col in spec:
            ys = cv[nm]
            pts = [(ax.X(n_), ax.Y(min(v, 2.0))) for n_, v in zip(N, ys)]
            k = max(2, int(len(pts) * prog_))
            polyline(c, pts[:k], col, 3.2, C)
            if prog_ > 0.95:
                text(c, nm, pts[-1][0] + 10, pts[-1][1] + 6 + {"2D torus": 16, "3D torus": -2}.get(nm, 0), 18, "r", col, C * fade(t, ctx.b0(2) + 10.5, 0.5))
        # highlight 8^3 and 16^3
        h = fade(t, ctx.b0(2) + 12, 0.7)
        for n_, v, lab in [(512, 0.5, "8×8×8"), (4096, 0.25, "16³")]:
            circle(c, ax.X(n_), ax.Y(v), 8, Pal.GOLD, C * h)
            note(c, lab, ax.X(n_) + 12, ax.Y(v) - 14, C * h, 20, Pal.GOLD)
        note(c, "β = 4/k with k = N^(1/n): smooth in N, so the 5-D curve passes 1 where k < 4", 760, 862, C * fade(t, ctx.b0(2) + 12, 0.7), 17, Pal.MUTED)
        X0 = 150
        fa = C * fade(t, ctx.b0(2) + 1.0, 0.7)
        rich(c, "diameter  =  $n$ · ⌊$k$/2⌋", X0, 340, 34, Pal.INK, fa)
        fb = C * fade(t, ctx.b0(2) + 3.2, 0.7)
        rich(c, "bisection  =  2$k^{n-1}$ links", X0, 420, 34, Pal.INK, fb)
        text(c, "(wraparound: two planes are cut)", X0, 456, 20, "i", Pal.MUTED, fb)
        fc = C * fade(t, ctx.b0(2) + 5.0, 0.7)
        rich(c, "β  =  4 / $k$", X0, 540, 46, Pal.GOLD, fc)
        text(c, "double k  →  halve β", X0, 580, 24, "i", Pal.INK, fc)
        fd = C * fade(t, ctx.b0(2) + 13, 0.7)
        text(c, "8×8×8:  β = 0.5,  diameter 12", X0, 680, 24, "r", Pal.INK, fd)
        text(c, "16³ (4,096 nodes):  β = 0.25,  diameter 24", X0, 716, 24, "r", Pal.INK, fd)
    # ---------------- beat 3 : all-to-all load heatmaps
    D = fade(t, ctx.b0(3) + 0.2, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        AL = R["alltoall_loads"]
        def draw_grid(ox, oy, loads, wrap, mx, a):
            sp = 62; k = 8
            P_ = lambda r, c_: (ox + c_ * sp, oy + r * sp)
            def ld(r1, c1, r2, c2):
                return max(loads.get(f"{r1},{c1}>{r2},{c2}", 0), loads.get(f"{r2},{c2}>{r1},{c1}", 0))
            for r in range(k):
                for c_ in range(k):
                    for dr, dc in ((0, 1), (1, 0)):
                        r2, c2 = r + dr, c_ + dc
                        if r2 < k and c2 < k:
                            v = ld(r, c_, r2, c2) / mx
                            line(c, *P_(r, c_), *P_(r2, c2), mix(Pal.BLUE, Pal.RED, clamp01((v - 0.35) / 0.65)), 2 + 4 * v, a)
            if wrap:
                for r in range(k):
                    v = ld(r, 0, r, k - 1) / mx
                    curve(c, *P_(r, 0), *P_(r, k - 1), -30 - 3 * abs(r - 3.5), mix(Pal.BLUE, Pal.RED, clamp01((v - .35) / .65)), 2 + 4 * v, a * 0.55)
                for c_ in range(k):
                    v = ld(0, c_, k - 1, c_) / mx
                    curve(c, *P_(0, c_), *P_(k - 1, c_), 30 + 3 * abs(c_ - 3.5), mix(Pal.BLUE, Pal.RED, clamp01((v - .35) / .65)), 2 + 4 * v, a * 0.55)
            for r in range(k):
                for c_ in range(k):
                    circle(c, *P_(r, c_), 5, Pal.INK, a)
        mx = AL["mesh"]["max_load"]
        # torus wrap links exist in torus loads under keys like "0,7>0,0"
        draw_grid(250, 330, AL["torus"]["load"], True, mx, D * fade(t, ctx.b0(3) + 1, 0.8))
        draw_grid(1100, 330, AL["mesh"]["load"], False, mx, D * fade(t, ctx.b0(3) + 1, 0.8))
        text(c, "torus", 480, 250, 32, "i", Pal.INK, D, "c"); text(c, "mesh", 1330, 250, 32, "i", Pal.INK, D, "c")
        e = D * fade(t, ctx.b0(3) + 8, 0.8)
        text(c, f"every link carries {AL['torus']['max_over_mean']:.2f}× the mean", 480, 840, 24, "r", Pal.INK, e, "c")
        text(c, f"centre links carry {AL['mesh']['max_over_mean']:.2f}× the mean", 1330, 840, 24, "r", Pal.RED, e, "c")
        g = D * fade(t, ctx.b0(3) + 12, 0.8)
        text(c, f"saturates at {AL['torus']['saturation_injection']:.2f} of injection", 480, 880, 24, "i", Pal.MUTED, g, "c")
        text(c, f"saturates at {AL['mesh']['saturation_injection']:.2f} of injection", 1330, 880, 24, "i", Pal.MUTED, g, "c")
        note(c, "8×8, uniform all-to-all, dimension-order routing (this video's model)", 960, 940, D, 18, Pal.MUTED, "c")
    # ---------------- beat 4 : deadlock + dateline
    E_ = fade(t, ctx.b0(4) + 0.2, 0.8) * (1 - fade(t, ctx.b0(5) - 0.3, 0.6))
    if E_ > 0:
        cx, cy, r = 700, 500, 190
        nodes = ring_pts(cx, cy, r, 4, -math.pi / 4)
        dl = fade(t, ctx.b0(4) + 9.0, 0.9)    # dateline / VC phase
        for i in range(4):
            a_, b_ = nodes[i], nodes[(i + 1) % 4]
            line(c, *a_, *b_, Pal.BLUE, 5, E_ * 0.55)
            if dl > 0:
                # second lane
                mx_, my_ = (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2
                ox, oy = (mx_ - cx) * 0.18, (my_ - cy) * 0.18
                line(c, a_[0] + ox, a_[1] + oy, b_[0] + ox, b_[1] + oy, Pal.GREEN, 5, E_ * dl * 0.55)
        for p in nodes:
            circle(c, *p, 15, Pal.BG, E_, Pal.INK, 2.5, E_)
        # four packets, each holding its channel, waiting for the next
        wt = fade(t, ctx.b0(4) + 2.0, 0.8)
        for i in range(4):
            a_, b_ = nodes[i], nodes[(i + 1) % 4]
            px, py = lerp(a_[0], b_[0], 0.55), lerp(a_[1], b_[1], 0.55)
            col = Pal.RED if dl < 0.5 else Pal.GOLD
            rect(c, px - 20, py - 11, 40, 22, col, E_ * wt, r=4)
            # waits-for arrow to next channel
            n_a, n_b = nodes[(i + 1) % 4], nodes[(i + 2) % 4]
            nx_, ny_ = lerp(n_a[0], n_b[0], 0.2), lerp(n_a[1], n_b[1], 0.2)
            if dl < 0.99:
                arrow(c, px + (b_[0] - a_[0]) * 0.25, py + (b_[1] - a_[1]) * 0.25, nx_, ny_, Pal.RED, 2.2, E_ * wt * (1 - dl) * fade(t, ctx.b0(4) + 3.5, 0.8), 11)
        if dl < 0.5:
            big(c, "no one moves", cx, cy + 12, E_ * wt * (1 - dl * 2), 40, Pal.RED, "c", "i")
        # dateline
        if dl > 0:
            line(c, cx - 15, cy - r - 60, cx - 15, cy - r + 50, Pal.GOLD, 3, E_ * dl, dash=(8, 7))
            text(c, "dateline", cx - 15, cy - r - 72, 20, "i", Pal.GOLD, E_ * dl, "c")
            big(c, "cycle broken", cx, cy + 12, E_ * dl * fade(t, ctx.b0(4) + 13, 0.7), 40, Pal.GREEN, "c", "i")
        X0 = 1180
        text(c, "wraparound closes a cycle", X0, 400, 30, "r", Pal.INK, E_ * fade(t, ctx.b0(4) + 1, 0.7))
        text(c, "each packet holds a channel and waits for the next", X0, 440, 24, "i", Pal.MUTED, E_ * fade(t, ctx.b0(4) + 3, 0.7))
        text(c, "cure: 2 virtual channels per link;", X0, 540, 30, "r", Pal.GREEN, E_ * fade(t, ctx.b0(4) + 9, 0.7))
        text(c, "switch to the second at the dateline", X0, 580, 30, "r", Pal.GREEN, E_ * fade(t, ctx.b0(4) + 9.5, 0.7))
        text(c, "checked on small tori: a dependency cycle without VCs, none with the dateline", X0, 680, 22, "i", Pal.MUTED, E_ * fade(t, ctx.b0(4) + 14, 0.7))
        text(c, "Dally & Seitz, 1987", X0, 730, 22, "i", Pal.MUTED, E_ * fade(t, ctx.b0(4) + 14, 0.7))
    # ---------------- beat 5 : Blue Gene/L
    F = fade(t, ctx.b0(5) + 0.2, 0.8) * (1 - fade(t, ctx.b0(6) - 0.3, 0.6))
    if F > 0:
        # isometric slab 64 x 32 x 32 (x long)
        ox, oy = 330, 600
        Lx, Ly, Lz = 520, 230, 230
        dx, dy = 0.5 * Ly, -0.35 * Ly
        def P3(x, y, z):
            return (ox + x * Lx + y * dx, oy + y * dy - z * Lz * 0.9)
        edges = []
        for (a1, a2) in [((0,0,0),(1,0,0)),((0,1,0),(1,1,0)),((0,0,1),(1,0,1)),((0,1,1),(1,1,1)),
                         ((0,0,0),(0,1,0)),((1,0,0),(1,1,0)),((0,0,1),(0,1,1)),((1,0,1),(1,1,1)),
                         ((0,0,0),(0,0,1)),((1,0,0),(1,0,1)),((0,1,0),(0,1,1)),((1,1,0),(1,1,1))]:
            line(c, *P3(*a1), *P3(*a2), Pal.BLUE, 2.4, F * 0.8)
        # lattice hint
        for i in range(1, 8):
            f = i / 8
            line(c, *P3(f, 0, 0), *P3(f, 0, 1), Pal.BLUE, 1, F * 0.25); line(c, *P3(f, 0, 1), *P3(f, 1, 1), Pal.BLUE, 1, F * 0.25)
        cut = fade(t, ctx.b0(5) + 3.5, 1.0)
        if cut > 0:
            poly = [P3(0.5, 0, 0), P3(0.5, 1, 0), P3(0.5, 1, 1), P3(0.5, 0, 1)]
            path = skia.Path(); path.moveTo(*poly[0]); [path.lineTo(*q) for q in poly[1:]]; path.close()
            c.drawPath(path, P(Pal.GOLD, 0.28 * F * cut))
            polyline(c, poly, Pal.GOLD, 3, F * cut, closed=True)
        text(c, "64", P3(0.5, 0, 0)[0], P3(0.5, 0, 0)[1] + 34, 28, "b", Pal.MUTED, F, "c")
        text(c, "32", P3(1, 0.5, 0)[0] + 28, P3(1, 0.5, 0)[1] + 14, 28, "b", Pal.MUTED, F, "l")
        text(c, "32", P3(0, 0, 0.5)[0] - 20, P3(0, 0, 0.5)[1] + 8, 28, "b", Pal.MUTED, F, "r")
        X0 = 1230
        text(c, "Blue Gene/L", X0, 300, 34, "i", Pal.INK, F)
        text(c, "64 × 32 × 32 = 65,536 nodes", X0, 342, 24, "r", Pal.MUTED, F)
        a1 = F * fade(t, ctx.b0(5) + 5.0, 0.7)
        rich(c, "cut across the long axis:  2 × 32 × 32 = 2,048 links", X0, 440, 24, Pal.INK, a1)
        a2 = F * fade(t, ctx.b0(5) + 8.0, 0.7)
        rich(c, "× 1.4 Gb/s ÷ 8  =  358.4 GB/s per direction", X0, 490, 26, Pal.GOLD, a2)
        a3 = F * fade(t, ctx.b0(5) + 11.0, 0.7)
        text(c, "IBM's paper: 360 GB/s", X0, 540, 24, "r", Pal.GREEN, a3)
        a4 = F * fade(t, ctx.b0(5) + 15.0, 0.7)
        text(c, "plus a separate tree network for reductions", X0, 640, 24, "i", Pal.INK, a4)
    # ---------------- beat 6 : Tofu / K
    G = fade(t, ctx.b0(6) + 0.2, 0.8) * (1 - fade(t, ctx.b0(7) - 0.3, 0.6))
    if G > 0:
        # a 24x18 sheet of "units" (abstract), one zoomed
        ux, uy = 160, 270
        for i in range(9):
            for j in range(12):
                rect(c, ux + j * 40, uy + i * 40, 32, 32, Pal.BLUE, G * 0.18 * fade(t, ctx.b0(6) + 0.5 + (i + j) * 0.04, 0.5), Pal.BLUE, 1, G * 0.5, r=3)
        text(c, "24 × 18 × 16 units  (3 axes of the fabric)", ux, uy + 9 * 40 + 36, 22, "r", Pal.MUTED, G * fade(t, ctx.b0(6) + 4, 0.6))
        # zoomed unit 2x3x2 = 12 nodes
        cx0, cy0 = 960, 380
        a = G * fade(t, ctx.b0(6) + 5.0, 0.8)
        rect(c, 740, 300, 440, 330, None, a, Pal.GOLD, 2, a, r=10, dash=(8, 7)) if False else None
        pts = {}
        for x in range(2):
            for y in range(3):
                for z in range(2):
                    pts[(x, y, z)] = (cx0 + 100 + x * 150 + z * 75, 330 + y * 90 - z * 55 + 0)
        for (x, y, z), p in pts.items():
            for d, mx_ in enumerate((2, 3, 2)):
                q = [x, y, z]; q[d] += 1
                if tuple(q) in pts:
                    line(c, *p, *pts[tuple(q)], Pal.GOLD, 2, a * 0.8)
        for p in pts.values():
            circle(c, *p, 9, Pal.INK, a, Pal.GOLD, 2, a)
        text(c, "one unit:  2 × 3 × 2 = 12 nodes", cx0 + 100, 590, 22, "r", Pal.GOLD, a)
        b_ = G * fade(t, ctx.b0(6) + 8.0, 0.8)
        rich(c, "24 × 18 × 16 × 12  =  82,944 nodes  (K computer)", 960, 760, 30, Pal.INK, b_, "c")
        c_ = G * fade(t, ctx.b0(6) + 12.0, 0.8)
        text(c, "the user asks for a 3-D shape — e.g. 54 × 48 × 32 —", 960, 820, 26, "i", Pal.INK, c_, "c")
        text(c, "and neighbours in that virtual torus are neighbours in the real network", 960, 860, 26, "i", Pal.INK, c_, "c")
    # ---------------- beat 7 : TPU v4
    H_ = fade(t, ctx.b0(7) + 0.2, 0.8)
    if H_ > 0:
        gx0, gy0, sp = 280, 270, 70
        failed = {(2, 3), (5, 1), (6, 6)}
        sl = fade(t, ctx.b0(7) + 7.0, 1.0)
        # slice: pick 16 healthy cubes avoiding failed (scattered)
        slice_cells = [(r, c_) for r in range(8) for c_ in range(8) if (r, c_) not in failed and (r + 2 * c_) % 4 in (0,)][:16]
        ocs = (gx0 + 3.5 * sp + 560, gy0 + 3.5 * sp)
        for r in range(8):
            for c_ in range(8):
                x, y = gx0 + c_ * sp, gy0 + r * sp
                a = H_ * fade(t, ctx.b0(7) + 0.5 + (r + c_) * 0.05, 0.5)
                if (r, c_) in failed:
                    col, st = Pal.RED, Pal.RED
                    f = 0.35
                elif (r, c_) in slice_cells:
                    col, st = Pal.GOLD, Pal.GOLD; f = 0.25 + 0.4 * sl
                else:
                    col, st = Pal.BLUE, Pal.BLUE; f = 0.15
                rect(c, x - 24, y - 24, 48, 48, col, a * f, st, 1.5, a * 0.8, r=4)
                if (r, c_) in slice_cells and sl > 0:
                    line(c, x + 24, y, ocs[0] - 70, ocs[1] + (y - ocs[1]) * 0.1, Pal.GOLD, 1.0, H_ * sl * 0.28)
        rect(c, ocs[0] - 70, ocs[1] - 70, 140, 140, Pal.BG, H_, Pal.GOLD, 2.4, H_, r=10)
        text(c, "optical", ocs[0], ocs[1] - 8, 22, "i", Pal.GOLD, H_, "c"); text(c, "circuit switches", ocs[0], ocs[1] + 22, 20, "i", Pal.GOLD, H_, "c")
        text(c, "64 cubes of 4 × 4 × 4 chips = 4,096", gx0 + 3.5 * sp, 205, 24, "r", Pal.INK, H_, "c")
        text(c, "failed cubes", gx0 + 7 * sp + 90, gy0 + 6 * sp + 8, 20, "i", Pal.RED, H_ * fade(t, ctx.b0(7) + 4, 0.6), "l")
        text(c, "slice built from healthy cubes", gx0 + 3.5 * sp, gy0 + 7 * sp + 70, 22, "i", Pal.GOLD, H_ * sl, "c")
        X0 = 1280
        a = H_ * fade(t, ctx.b0(7) + 10, 0.8)
        text(c, "twisted torus, all-to-all:", X0, 760, 24, "r", Pal.INK, a)
        text(c, "1.63× and 1.31× throughput", X0, 800, 30, "b", Pal.GOLD, a)
        text(c, "on two slice shapes (Google's paper)", X0, 836, 20, "i", Pal.MUTED, a)
        text(c, "OCS: < 5% of cost, < 3% of power", X0, 420, 24, "r", Pal.INK, H_ * fade(t, ctx.b0(7) + 14, 0.8))
        text(c, "without them: host availability must be 99.9%", X0, 460, 24, "r", Pal.INK, H_ * fade(t, ctx.b0(7) + 17, 0.8))
    footer(c, "Dally & Seitz 1987 · Adiga et al. 2005 (BG/L) · Fujitsu Tofu · Jouppi et al. 2023 (TPU v4)", 1.0)


# ------------------------------------------------------------------ 9 hyper
def cube_pts(nd, cx, cy, s=110):
    """hypercube vertices projected (nd=1..4)"""
    pts = {}
    base = {0: (1, 0), 1: (0, 1), 2: (0.45, -0.35), 3: (1.6, 0.3)}
    for v in range(2 ** nd):
        x = y = 0.0
        for d in range(nd):
            if v >> d & 1:
                x += base[d][0]; y += base[d][1]
        pts[v] = (cx + (x - 0.5 * sum(base[d][0] for d in range(nd))) * s,
                  cy + (y - 0.5 * sum(base[d][1] for d in range(nd))) * s)
    return pts


@scene
def s_hyper(c, t, ctx):
    # ---- beat 0 : doubling
    A = fade(t, ctx.b0(0) + 0.2, 0.8) * (1 - fade(t, ctx.b0(1) - 0.3, 0.6))
    if A > 0:
        T0 = ctx.b0(0)
        stages = [(1, 1.0), (2, 5.5), (3, 9.5), (4, 14.0)]
        cur = 1
        for nd, ts in stages:
            if t >= T0 + ts:
                cur = nd
        # draw cur with the newest edges fading in
        nd = cur
        ts = dict(stages)[nd]
        new = fade(t, T0 + ts, 1.2)
        pts = cube_pts(nd, 760, 520, 120)
        for v in range(2 ** nd):
            for d in range(nd):
                w = v ^ (1 << d)
                if v < w:
                    isnew = (d == nd - 1)
                    line(c, *pts[v], *pts[w], Pal.GOLD if isnew and new < 1 else Pal.BLUE, 3, A * (new if isnew else 1) * 0.9)
        for v, p in pts.items():
            isnewv = v >> (nd - 1) & 1
            circle(c, *p, 11, Pal.INK, A * (new if isnewv else 1), Pal.BLUE, 2, A)
        X0 = 1280
        text(c, f"{nd} dimension{'s' if nd > 1 else ''}", X0, 400, 36, "i", Pal.INK, A)
        text(c, f"{2 ** nd} nodes", X0, 450, 30, "r", Pal.GOLD, A)
        text(c, f"{nd} link{'s' if nd > 1 else ''} per node", X0, 496, 30, "r", Pal.GOLD, A)
        if t > T0 + 18:
            text(c, "the Cosmic Cube was a 6-cube: 64 nodes", X0, 620, 24, "i", Pal.MUTED, A * fade(t, T0 + 18, 0.7))
            text(c, "and contains every lower-dimensional mesh", X0, 656, 24, "i", Pal.MUTED, A * fade(t, T0 + 20, 0.7))
    # ---- beat 1 : the catch is radix
    B = fade(t, ctx.b0(1) + 0.2, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if B > 0:
        T0 = ctx.b0(1)
        X0 = 160
        rows = [("diameter", "log₂ N", "13"), ("bisection", "N / 2", ""), ("β", "", "1")]
        for k, (nm, f_, v) in enumerate(rows):
            a = B * fade(t, T0 + 0.8 + k * 1.2, 0.7)
            small_caps(c, nm, X0, 300 + k * 70, 16, Pal.MUTED, a)
            text(c, f_ if f_ else v, X0 + 200, 306 + k * 70, 34, "i" if f_ else "b", Pal.GREEN, a)
        a = B * fade(t, T0 + 8.0, 0.8)
        text(c, "for N = 8,192:", X0, 580, 26, "i", Pal.MUTED, a)
        text(c, "13 links per node  ·  6.5 cables per node", X0, 630, 34, "b", Pal.RED, a)
        # plot cables per node vs N
        ax = Axes(1010, 780, 1760, 280, (16, 65536), (0, 9), xlog=True)
        ax.frame(c, [16, 256, 4096, 65536], [0, 3, 6, 9], lambda v: f"{int(v):,}", lambda v: f"{v:g}", B, 16, "nodes N", "cables per node")
        pg = fade(t, T0 + 4.0, 3.0)
        pts = [(ax.X(2 ** n), ax.Y(n / 2)) for n in range(4, 17)]
        polyline(c, pts[:max(2, int(len(pts) * pg))], Pal.RED, 3.5, B)
        pts2 = [(ax.X(2 ** n), ax.Y(3)) for n in range(4, 17)]
        polyline(c, pts2[:max(2, int(len(pts2) * pg))], Pal.TEAL, 3.5, B)
        text(c, "hypercube", ax.X(65536) - 8, ax.Y(8) - 8, 20, "r", Pal.RED, B * pg, "r")
        text(c, "3-D torus", ax.X(65536) - 8, ax.Y(3) - 12, 20, "r", Pal.TEAL, B * pg, "r")
    # ---- beat 2 : HyperX construction
    C = fade(t, ctx.b0(2) + 0.2, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if C > 0:
        T0 = ctx.b0(2)
        S = 4; sp = 150
        gx = lambda j: 560 - (S - 1) * sp / 2 + j * sp
        gy = lambda i: 520 - (S - 1) * sp / 2 + i * sp
        rowp = fade(t, T0 + 1.5, 3.0); colp = fade(t, T0 + 5.5, 3.0)
        for i in range(S):
            for j in range(S):
                for k in range(j + 1, S):
                    curve(c, gx(j), gy(i), gx(k), gy(i), 0.1 if k == j + 1 else -34 * (k - j) * (1 if (i + j) % 2 else -1), Pal.BLUE, 2.2, C * 0.7, p=rowp)
                    curve(c, gx(i), gy(j), gx(i), gy(k), 0.1 if k == j + 1 else -34 * (k - j) * (1 if (i + j) % 2 else -1), Pal.PURPLE, 2.2, C * 0.7, p=colp)
        for i in range(S):
            for j in range(S):
                circle(c, gx(j), gy(i), 12, Pal.BG, C, Pal.INK, 2.4, C)
        # two-hop path
        ph = fade(t, T0 + 10, 0.8)
        pth = [(gx(0), gy(0)), (gx(3), gy(0)), (gx(3), gy(3))]
        polyline(c, pth, Pal.GOLD, 4.5, C * ph)
        packet(c, pth, ((t - T0 - 11) * 0.3) % 1.0, Pal.GOLD, 8, C * ph, 0.1)
        X0 = 1130
        text(c, "each row and column is a full mesh", X0, 340, 30, "r", Pal.INK, C * fade(t, T0 + 1.0, 0.7))
        text(c, "diameter = number of dimensions", X0, 400, 30, "r", Pal.GOLD, C * ph)
        text(c, "(here 2 hops, any two switches)", X0, 436, 22, "i", Pal.MUTED, C * ph)
        text(c, "two switches per row → hypercube", X0, 540, 26, "r", Pal.INK, C * fade(t, T0 + 12, 0.7))
        text(c, "one dimension → fully connected graph", X0, 584, 26, "r", Pal.INK, C * fade(t, T0 + 14, 0.7))
    # ---- beat 3 : choosing T
    D = fade(t, ctx.b0(3) + 0.2, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        T0 = ctx.b0(3)
        small_caps(c, "16 × 16 grid of 256 switches", 160, 250, 16, Pal.GOLD, D)
        cols = [("machines / switch", 260, "r"), ("switch radix", 220, "r"), ("machines", 220, "r"), ("β", 140, "r")]
        x = 160
        cx = x
        for title, w, anc in cols:
            small_caps(c, title, cx + w, 320, 15, Pal.MUTED, D, "r"); cx += w
        line(c, x, 332, x + sum(w for *_, w in [(0, 0, w) for _, w, _ in cols]), 332, Pal.FAINT, 1.2, D)
        for k, r_ in enumerate(R["hyperx"]["rows"][:3]):
            a = D * fade(t, T0 + 1.0 + k * 3.0, 0.7)
            y = 390 + k * 70
            vals = [str(r_["T"]), str(r_["radix"]), f"{r_['terminals']:,}", f"{r_['beta']:g}"]
            cx = x
            for (title, w, anc), v in zip(cols, vals):
                text(c, v, cx + w, y, 34, "r" if title != "β" else "b", Pal.GOLD if title == "β" else Pal.INK, a, "r"); cx += w
            bar_h(c, x + 940, y - 22, 300 * r_["beta"] * a, 28, 1.0, Pal.GREEN, D * a)
        note(c, "fewer machines per switch buys bisection …", 160, 700, D * fade(t, T0 + 10, 0.8), 28, Pal.INK)
        note(c, "… at the price of more switches per machine", 160, 746, D * fade(t, T0 + 13, 0.8), 28, Pal.INK)
        # switch-per-1000 numbers
        a = D * fade(t, T0 + 15, 0.8)
        for k, r_ in enumerate(R["hyperx"]["rows"][:3]):
            text(c, f"{256 / r_['terminals'] * 1000:.0f} switches / 1,000 machines", 1480, 392 + k * 70 + 0, 20, "i", Pal.MUTED, a * fade(t, T0 + 15 + k * 0.5, 0.5), "l") if False else None
        text(c, "radix = T + 2·15 = T + 30", 1480, 760, 22, "i", Pal.MUTED, a, "c") if False else None
    # ---- beat 4 : cautions
    E_ = fade(t, ctx.b0(4) + 0.3, 0.9)
    if E_ > 0:
        T0 = ctx.b0(4)
        glyph(c, "tree", 560, 400, 170, E_ * fade(t, T0 + 0.8, 0.7)); glyph(c, "hyperx", 1360, 400, 170, E_ * fade(t, T0 + 0.8, 0.7))
        a = E_ * fade(t, T0 + 1.5, 0.8)
        text(c, "folded Clos", 560, 560, 34, "i", Pal.INK, a, "c"); text(c, "generally more efficient", 560, 600, 24, "r", Pal.MUTED, a, "c"); text(c, "when you need full bisection", 560, 634, 24, "r", Pal.MUTED, a, "c")
        b = E_ * fade(t, T0 + 4.0, 0.8)
        text(c, "HyperX", 1360, 560, 34, "i", Pal.INK, b, "c"); text(c, "shines with high-radix switches", 1360, 600, 24, "r", Pal.MUTED, b, "c"); text(c, "when you can live with less bisection", 1360, 634, 24, "r", Pal.MUTED, b, "c")
        d = E_ * fade(t, T0 + 9.0, 0.9)
        text(c, "one research machine, both planes: a fat tree and a 12 × 8 HyperX", 960, 790, 28, "i", Pal.INK, d, "c")
        text(c, "with pattern-aware routing the HyperX can challenge — even beat — the fat tree", 960, 836, 24, "r", Pal.GOLD, d * fade(t, T0 + 11, 0.8), "c")
        text(c, "Ahn et al., SC09 · Domke et al., SC19", 960, 900, 18, "i", Pal.MUTED, d, "c")

s_hyper.dy = 30
