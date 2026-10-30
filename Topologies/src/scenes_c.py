"""Scenes 10-15: dragonfly, compare, collectives, place, zoo, close."""
from common import *
from scenes_a import bu

SC = {}


def scene(fn):
    SC[fn.__name__.replace("s_", "")] = fn
    return fn


# ------------------------------------------------------------------ 10 dragonfly
_DFC = [960]


def pct(v):
    p = v * 100
    return f"{p:.0f}%" if abs(p - round(p)) < 0.05 else f"{p:.1f}%"


def df_group_pos(g, G, cx=None, cy=520, R_=320):
    cx = _DFC[0] if cx is None else cx
    ang = -math.pi / 2 + 2 * math.pi * g / G
    return cx + R_ * math.cos(ang) * 1.25, cy + R_ * math.sin(ang) * 0.95


def df_router_pos(g, r, a, G, rad=40, **kw):
    gx, gy = df_group_pos(g, G, **kw)
    ang = -math.pi / 2 + 2 * math.pi * r / a + math.pi / a
    return gx + rad * math.cos(ang), gy + rad * math.sin(ang)


@scene
def s_dragonfly(c, t, ctx):
    DF = R["dragonfly"]["draw"]
    G, a_, p_, h_ = DF["g"], DF["a"], DF["p"], DF["h"]
    # ---- beat 0 : cables
    A = fade(t, ctx.b0(0) + 0.2, 0.8) * (1 - fade(t, ctx.b0(1) - 0.3, 0.6))
    if A > 0:
        T0 = ctx.b0(0)
        cab = [(220 + k * 270, 400) for k in range(6)]
        for k, (x, y) in enumerate(cab):
            a = A * fade(t, T0 + 0.5 + k * 0.3, 0.6)
            rect(c, x - 90, y - 130, 180, 330, Pal.BG, a, Pal.MUTED, 2, a, r=8)
            for i in range(7):
                yy = y - 100 + i * 42
                rect(c, x - 66, yy - 12, 132, 24, Pal.FAINT, a * 0.6, r=3)
            for i in range(3):
                curve(c, x - 54, y - 80 + i * 70, x - 54, y - 38 + i * 70, 20, Pal.GREEN, 2.2, a * 0.9)
        text(c, "short, in-cabinet: copper, cheap", 960, 700, 28, "i", Pal.GREEN, A * fade(t, T0 + 3, 0.8), "c")
        for k in range(5):
            ap = A * fade(t, T0 + 5 + k * 0.5, 0.8)
            curve(c, cab[k][0] + 60, cab[k][1] - 130, cab[k + 1][0] - 60, cab[k + 1][1] - 130, -90 - 20 * (k % 2), Pal.ORANGE, 4.5, ap)
        curve(c, cab[0][0], cab[0][1] - 130, cab[3][0], cab[3][1] - 130, -210, Pal.ORANGE, 4.5, A * fade(t, T0 + 8.0, 1.0))
        text(c, "long, between cabinets: optical, and the bulk of the cost", 960, 760, 28, "i", Pal.ORANGE, A * fade(t, T0 + 6, 0.8), "c")
    # ---- beat 1 : group as virtual router
    B = fade(t, ctx.b0(1) + 0.2, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if B > 0:
        T0 = ctx.b0(1)
        # left: a group, routers all-to-all
        gx, gy = 460, 520
        pts = ring_pts(gx, gy, 130, 6)
        for i in range(6):
            for j in range(i + 1, 6):
                line(c, *pts[i], *pts[j], Pal.GREEN, 2, B * 0.7 * fade(t, T0 + 1.0 + (i + j) * 0.1, 0.5))
        for p in pts:
            circle(c, *p, 14, Pal.BG, B, Pal.INK, 2.5, B)
        v = fade(t, T0 + 5.0, 1.0)
        circle(c, gx, gy, 190 * 1, None, 1, Pal.GOLD, 3, B * v)
        text(c, "one group = one giant virtual router", gx, gy + 260, 24, "i", Pal.GOLD, B * v, "c")
        # right: K5 of groups
        cx2, cy2 = 1350, 520
        gp = ring_pts(cx2, cy2, 200, 5)
        k5 = fade(t, T0 + 7.0, 2.5)
        for i in range(5):
            for j in range(i + 1, 5):
                curve(c, *gp[i], *gp[j], 0.1, Pal.ORANGE, 3, B * 0.85, p=k5)
        for p in gp:
            circle(c, *p, 38, Pal.BG, B, Pal.GOLD, 3, B)
            rr = ring_pts(p[0], p[1], 18, 4)
            for i in range(4):
                for j in range(i + 1, 4):
                    line(c, *rr[i], *rr[j], Pal.GREEN, 1.2, B * 0.8)
            for q in rr:
                circle(c, *q, 3.5, Pal.INK, B)
        text(c, "all groups joined, one long cable per pair", cx2, 800, 24, "i", Pal.ORANGE, B * fade(t, T0 + 9, 0.8), "c")
    # ---- beat 2 : the three numbers
    C = fade(t, ctx.b0(2) + 0.2, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if C > 0:
        T0 = ctx.b0(2)
        # one router, ports labelled
        rx, ry = 480, 520
        rect(c, rx - 70, ry - 70, 140, 140, Pal.BG, C, Pal.INK, 3, C, r=12)
        text(c, "router", rx, ry + 8, 26, "i", Pal.INK, C, "c")
        items = [("p", "machines", Pal.BLUE, 160, 0.30, T0 + 1.0), ("a − 1", "local links", Pal.GREEN, 180, 0.0, T0 + 3.0), ("h", "global links", Pal.ORANGE, 160, -0.30, T0 + 5.0)]
        for nm, desc, col, L, ang, t0 in items:
            aa = C * fade(t, t0, 0.7)
            for k in range(3):
                an = math.radians({"p": 120, "a − 1": 0, "h": 240}[nm] + (k - 1) * 22)
                line(c, rx + 70 * math.cos(an), ry + 70 * math.sin(an), rx + (70 + L * .6) * math.cos(an), ry + (70 + L * .6) * math.sin(an), col, 3.5, aa)
            an = math.radians({"p": 120, "a − 1": 0, "h": 240}[nm])
            xx, yy = rx + (70 + L * .6 + 40) * math.cos(an), ry + (70 + L * .6 + 40) * math.sin(an)
            rich(c, f"$p$" if nm == "p" else ("$a$ − 1" if nm == "a − 1" else "$h$"), xx, yy + 8, 34, col, aa, "c")
            text(c, desc, xx, yy + 38, 20, "i", Pal.MUTED, aa, "c")
        X0 = 1010
        text(c, "a routers per group · p machines per router · h global links per router", X0 - 40, 280, 22, "i", Pal.MUTED, C * fade(t, T0 + 1, 0.7), "l")
        f1 = C * fade(t, T0 + 8.0, 0.8)
        rich(c, "a group reaches  $a$·$h$  other groups  →  $g$ = $a$·$h$ + 1", X0 - 40, 400, 30, Pal.INK, f1)
        f2 = C * fade(t, T0 + 11.0, 0.8)
        rich(c, "machines  $N$ = $a$ · $p$ · ($a$·$h$ + 1)", X0 - 40, 480, 36, Pal.GOLD, f2)
        f3 = C * fade(t, T0 + 15.0, 0.8)
        rich(c, "balanced when  $a$ = 2$p$ = 2$h$", X0 - 40, 560, 30, Pal.GREEN, f3)
        text(c, "load spreads evenly over machine, local and global channels", X0 - 40, 600, 22, "i", Pal.MUTED, f3)
    # ---- beat 3 : the g=9 example and Slingshot
    D = fade(t, ctx.b0(3) + 0.2, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        T0 = ctx.b0(3)
        _DFC[0] = 600
        def draw_df(a_net, hl=None, dim=1.0):
            for (g1, g2, r1, r2) in DF["glinks"]:
                p1 = df_router_pos(g1, r1 % a_, a_, G); p2 = df_router_pos(g2, r2 % a_, a_, G)
                col = Pal.ORANGE
                curve(c, *p1, *p2, 0.1 if abs(g1 - g2) in (1, G - 1) else -90, col, 1.4, a_net * 0.55 * dim)
            for g in range(G):
                gx, gy = df_group_pos(g, G)
                rr = [df_router_pos(g, r, a_, G) for r in range(a_)]
                for i in range(a_):
                    for j in range(i + 1, a_):
                        line(c, *rr[i], *rr[j], Pal.GREEN, 1.5, a_net * 0.8)
                for q in rr:
                    circle(c, *q, 6, Pal.BG, a_net, Pal.INK, 1.8, a_net)
        draw_df(D * fade(t, T0 + 0.8, 1.0))
        text(c, "a = 4, p = h = 2:   9 groups · 72 machines · ≤ 3 router hops", 600, 905, 24, "r", Pal.INK, D * fade(t, T0 + 6, 0.8), "c")
        # path highlight
        ph = D * fade(t, T0 + 9, 0.8)
        # route g0 router -> g? : use a global link and local hops
        g1, g2, r1, r2 = DF["glinks"][2]
        pth = [df_router_pos(0, 0, a_, G), df_router_pos(g1, r1 % a_, a_, G), df_router_pos(g2, r2 % a_, a_, G), df_router_pos(g2, (r2 + 1) % a_, a_, G)]
        # Slingshot numbers
        if t > T0 + 13:
            _DFC[0] = 960
            rect(c, 1300, 250, 560, 260, Pal.BG, D * fade(t, T0 + 13, 0.7) * 0.92, Pal.FAINT, 1.2, D * fade(t, T0 + 13, 0.7), r=8)
            a1 = D * fade(t, T0 + 13, 0.7)
            small_caps(c, "Slingshot, largest configuration", 1330, 285, 15, Pal.GOLD, a1)
            rich(c, "$p$ = 16   $a$ = 32 (31 local)   $h$ = 17", 1330, 335, 24, Pal.INK, a1 * fade(t, T0 + 14, 0.6))
            text(c, "64-port switch", 1330, 375, 22, "i", Pal.MUTED, a1 * fade(t, T0 + 14.5, 0.6))
            text(c, "545 groups", 1330, 425, 30, "b", Pal.GOLD, a1 * fade(t, T0 + 17, 0.6))
            text(c, "279,040 machines", 1330, 470, 30, "b", Pal.GOLD, a1 * fade(t, T0 + 19, 0.6))
    # ---- beat 4 : cost claim
    E_ = fade(t, ctx.b0(4) + 0.3, 0.8) * (1 - fade(t, ctx.b0(5) - 0.3, 0.6))
    if E_ > 0:
        T0 = ctx.b0(4)
        small_caps(c, "estimated cost of the dragonfly, at 16K+ nodes (Kim et al., 2008 cost model)", 960, 260, 16, Pal.MUTED, E_, "c")
        rows = [("flattened butterfly", 0.80, "≈ 20% lower"), ("folded Clos", 0.48, "≈ 52% lower")]
        for k, (nm, v, lab) in enumerate(rows):
            a = E_ * fade(t, T0 + 1 + k * 3, 0.8)
            y = 380 + k * 120
            text(c, f"vs {nm}", 520, y + 10, 30, "i", Pal.INK, a, "r")
            bar_h(c, 560, y - 22, 700, 44, 1.0, Pal.FAINT, a)
            bar_h(c, 560, y - 22, 700 * v * a, 44, 1.0, Pal.GREEN, a)
            text(c, lab, 560 + 700 * v * a + 20, y + 10, 30, "b", Pal.GREEN, a)
        text(c, "bar = dragonfly cost relative to the comparison design (=1.0 at the pale end)", 560, 640, 18, "i", Pal.MUTED, E_ * fade(t, T0 + 6, 0.7))
        text(c, "a claim from the paper's model, not a measurement", 960, 740, 26, "i", Pal.GOLD, E_ * fade(t, T0 + 8, 0.7), "c")
    # ---- beat 5 : the weak spot
    F = fade(t, ctx.b0(5) + 0.2, 0.8) * (1 - fade(t, ctx.b0(6) - 0.3, 0.6))
    if F > 0:
        T0 = ctx.b0(5)
        # two groups side by side with the single link
        gA, gB = (460, 520), (1460, 520)
        for (gx, gy), nm in ((gA, "group 0"), (gB, "group 1")):
            rr = ring_pts(gx, gy, 130, 4, -math.pi / 4)
            for i in range(4):
                for j in range(i + 1, 4):
                    line(c, *rr[i], *rr[j], Pal.GREEN, 2, F * 0.8)
            for q in rr:
                circle(c, *q, 14, Pal.BG, F, Pal.INK, 2.4, F)
            text(c, nm, gx, gy + 200, 24, "i", Pal.MUTED, F, "c")
        ra = ring_pts(*gA, 130, 4, -math.pi / 4)[0]; rb = ring_pts(*gB, 130, 4, -math.pi / 4)[2]
        ra = ring_pts(*gA, 130, 4, -math.pi / 4)[0]; rb = ring_pts(*gB, 130, 4, -math.pi / 4)[1]
        line(c, *ra, *rb, Pal.RED, 5, F * fade(t, T0 + 1.0, 0.8))
        # traffic
        ld = fade(t, T0 + 3.0, 0.8)
        for k in range(8):
            pts = [ring_pts(*gA, 130, 4, -math.pi / 4)[k % 4], ra, rb, ring_pts(*gB, 130, 4, -math.pi / 4)[(k + 1) % 4]]
            packet(c, pts, ((t - T0) * 0.25 + k * 0.125) % 1.0, Pal.RED, 5, F * ld)
        text(c, "every machine in group 0 sends to group 1", 960, 300, 28, "i", Pal.INK, F * ld, "c")
        text(c, "…all of it needs one link", 960, 340, 28, "i", Pal.RED, F * fade(t, T0 + 5, 0.7), "c")
        rich(c, "minimal routing: throughput = 1 / ($a$·$p$) = 1/8", 960, 840, 40, Pal.RED, F * fade(t, T0 + 8, 0.8), "c")
        text(c, "in this model, a = 4, p = 2", 960, 884, 20, "i", Pal.MUTED, F * fade(t, T0 + 8, 0.8), "c")
    # ---- beat 6 : randomised routing
    G_ = fade(t, ctx.b0(6) + 0.2, 0.8) * (1 - fade(t, ctx.b0(7) - 0.3, 0.6))
    if G_ > 0:
        T0 = ctx.b0(6)
        gs = 7
        def gp(g):
            return df_group_pos(g, gs, 500, 510, 250)
        ids = list(range(gs))
        src, dst = 0, 1
        for g in ids:
            x, y = gp(g)
            circle(c, x, y, 36, Pal.BG, G_, Pal.GOLD if g in (src, dst) else Pal.MUTED, 3, G_)
        for i in ids:
            for j in ids:
                if i < j:
                    line(c, *gp(i), *gp(j), Pal.FAINT, 1.2, G_)
        line(c, *gp(src), *gp(dst), Pal.RED, 4, G_ * 0.8)
        sp = fade(t, T0 + 2.0, 1.0)
        for k, mid in enumerate([2, 3, 4, 5, 6]):
            ap = G_ * fade(t, T0 + 2.0 + k * 0.6, 0.6)
            pts = [gp(src), gp(mid), gp(dst)]
            polyline(c, pts, Pal.GREEN, 2.6, ap * 0.8)
            packet(c, pts, ((t - T0) * 0.3 + k * 0.2) % 1.0, Pal.GREEN, 5, ap)
        text(c, "send each packet via a random intermediate group", 500, 850, 24, "i", Pal.INK, G_ * fade(t, T0 + 2, 0.8), "c")
        # bars
        X0 = 1100
        S_ = R["dragonfly"]["sims"][0]
        small_caps(c, "throughput, a = 4, p = h = 2 (model)", X0, 300, 15, Pal.MUTED, G_ * fade(t, T0 + 8, 0.7))
        for k, (nm, v_min, v_val) in enumerate([("adversarial pattern", S_["wc_min"], S_["wc_val"]), ("uniform traffic", S_["uni_min"], S_["uni_val"])]):
            a = G_ * fade(t, T0 + 9 + k * 4.0, 0.8)
            y = 380 + k * 170
            text(c, nm, X0, y, 26, "i", Pal.INK, a)
            bar_h(c, X0, y + 20, 600 * v_min * a, 30, 1.0, Pal.RED, a); text(c, f"minimal  {pct(v_min)}", X0 + 600 * v_min * a + 12, y + 44, 22, "r", Pal.RED, a)
            bv = a * fade(t, T0 + 11 + k * 4.0, 0.8)
            bar_h(c, X0, y + 66, 600 * v_val * bv, 30, 1.0, Pal.GREEN, bv); text(c, f"randomised  {pct(v_val)}", X0 + 600 * v_val * bv + 12, y + 90, 22, "r", Pal.GREEN, bv)
    # ---- beat 7 : adaptive routing + variants
    H_ = fade(t, ctx.b0(7) + 0.3, 0.9)
    if H_ > 0:
        T0 = ctx.b0(7)
        # chooser sketch
        text(c, "adaptive: choose between minimal and non-minimal using queue depth", 960, 250, 28, "i", Pal.INK, H_ * fade(t, T0 + 0.5, 0.8), "c")
        paths = [("minimal", 0.8, Pal.RED), ("via other group", 0.3, Pal.GREEN)]
        for k, (nm, q, col) in enumerate(paths):
            a = H_ * fade(t, T0 + 2 + k * 1.2, 0.7)
            y = 340 + k * 70
            text(c, nm, 480, y + 8, 24, "r", Pal.INK, a, "r")
            rect(c, 500, y - 16, 400, 30, Pal.BG, a, Pal.MUTED, 1.5, a, r=4)
            bar_h(c, 502, y - 14, 396 * q * a, 26, 1.0, col, a * 0.85)
        text(c, "← queue depth", 920, 390, 20, "i", Pal.MUTED, H_ * fade(t, T0 + 3, 0.7))
        text(c, "dragonfly paper: local queues alone gave limited throughput", 960, 520, 24, "r", Pal.MUTED, H_ * fade(t, T0 + 12, 0.8), "c")
        text(c, "and high latency on adversarial traffic", 960, 554, 24, "r", Pal.MUTED, H_ * fade(t, T0 + 12.5, 0.8), "c")
        text(c, "Slingshot estimates load from acknowledgements carried back with each packet", 960, 620, 26, "r", Pal.GOLD, H_ * fade(t, T0 + 16, 0.8), "c")
        for k, (kind, nm, desc) in enumerate([("dragonfly", "Dragonfly+", "group = leaf–spine network"), ("tree", "Slim Fly", "diameter 2 · ≈ 25% better cost-effectiveness (authors' model)")]):
            a = H_ * fade(t, T0 + 20 + k * 3.0, 0.9)
            x = 420 + k * 760
            glyph(c, kind if k == 0 else "petersen", x, 790, 100, a)
            text(c, nm, x + 90, 780, 30, "i", Pal.INK, a)
            text(c, desc, x + 90, 816, 20, "r", Pal.MUTED, a)
    footer(c, "Kim, Dally, Scott, Abts, ISCA 2008 · De Sensi et al., SC20 · this video's model", 1.0)


# ------------------------------------------------------------------ 11 compare
@scene
def s_compare(c, t, ctx):
    A = fade(t, ctx.b0(0) + 0.2, 0.8)
    rows = R["compare"]["rows"]
    short = ["fat tree · 3 levels · 32-port · 1:1", "fat tree · 2 levels · 64-port · 3:1", "3-D torus 16×16×32", "hypercube · 13 dims", "HyperX 16×16 · 32 per switch", "dragonfly a=16 p=8 h=8"]
    kinds = ["tree", "tree", "torus", "cube", "hyperx", "dragonfly"]
    cols = [("endpoints", 150), ("routers", 130), ("radix", 100), ("cables / endpoint", 250), ("diameter", 190), ("β", 150)]
    x0 = 620
    cx = x0
    for title, w in cols:
        small_caps(c, title, cx + w, 250, 15, Pal.MUTED, A, "r"); cx += w
    line(c, 160, 266, x0 + sum(w for _, w in cols) + 10, 266, Pal.FAINT, 1.2, A)
    hl = [None, None]
    if t >= ctx.b0(1) - 0.2:
        hl = [2, 3]
    if t >= ctx.b0(2) - 0.2:
        hl = [4, 5, 0, 1]
    if t >= ctx.b0(3) - 0.2:
        hl = []
    for k, (r_, nm, kd) in enumerate(zip(rows, short, kinds)):
        a = A * fade(t, ctx.b0(0) + 1.5 + k * 0.7, 0.7)
        y = 330 + k * 90
        on = (not hl and t >= ctx.b0(3) - 0.2) or (k in (hl or []))
        if k in (hl or []):
            rect(c, 150, y - 52, x0 + sum(w for _, w in cols) - 130, 78, Pal.GOLD, a * 0.07, Pal.GOLD, 1.4, a * 0.6, r=8)
        glyph(c, kd, 205, y - 18, 56, a)
        text(c, nm, 260, y - 2, 22, "r", Pal.INK, a)
        cx = x0
        vals = [f"{r_['N']:,}", f"{r_['routers']:,}", f"{r_['radix']}", f"{r_['cables_per_endpoint']:.2f}".rstrip("0").rstrip("."), f"{r_['diameter']}", f"{r_['beta']:.3g}"]
        for (title, w), v in zip(cols, vals):
            text(c, v, cx + w, y, 28, "r", Pal.INK, a, "r")
            if title == "cables / endpoint":
                bar_h(c, cx + w - 220, y + 10, 190 * min(1, r_["cables_per_endpoint"] / 7) * a, 8, 1.0, Pal.ORANGE, a * 0.9)
            if title == "β":
                bar_h(c, cx + w - 130, y + 10, 100 * min(1, r_["beta"]) * a, 8, 1.0, Pal.GREEN, a * 0.9)
            if title == "diameter":
                bar_h(c, cx + w - 160, y + 10, 140 * min(1, r_["diameter"] / 32) * a, 8, 1.0, Pal.BLUE, a * 0.9)
            cx += w
    note(c, "diameter in router-to-router hops · β = bisection ÷ injection (dragonfly: group-split cut, an upper bound)", 160, 880, A * fade(t, ctx.b0(0) + 6, 0.8), 18, Pal.MUTED)
    f = fade(t, ctx.b0(3) + 1.0, 0.9)
    if f > 0:
        big(c, "each topology is a bet on the traffic it will carry", 960, 940, f, 40, Pal.GOLD, "c", "i")
    footer(c, "every number from building the graph and measuring it (this video's models)", A)


# ------------------------------------------------------------------ 12 collectives
@scene
def s_collectives(c, t, ctx):
    CO = R["collectives"]
    # ---- beat 0 : what a collective is
    A = fade(t, ctx.b0(0) + 0.2, 0.8) * (1 - fade(t, ctx.b0(1) - 0.3, 0.6))
    if A > 0:
        T0 = ctx.b0(0)
        n = 8; cx, cy = 700, 520
        pts = ring_pts(cx, cy, 240, n)
        vals = [3, 1, 4, 1, 5, 9, 2, 6]
        conv = fade(t, T0 + 3.5, 2.5); back = fade(t, T0 + 7.5, 2.5)
        for i, (x, y) in enumerate(pts):
            xx, yy = lerp(x, cx, conv * (1 - back)), lerp(y, cy, conv * (1 - back))
            circle(c, x, y, 26, Pal.BG, A, Pal.BLUE, 2.4, A)
            text(c, str(vals[i]) if back < 0.5 else str(sum(vals)), x, y + 8, 24, "b", Pal.GOLD if back >= 0.5 else Pal.INK, A, "c")
            if 0 < conv < 1 or (conv >= 1 and back < 1):
                circle(c, xx, yy, 7, Pal.GOLD, A * (conv > 0) * (1 - (back > 0.95)))
        glow(c, cx, cy, 50, Pal.GOLD, 0.5 * A * conv * (1 - back))
        text(c, f"Σ = {sum(vals)}", cx, cy + 10, 34, "b", Pal.GOLD, A * conv * (1 - back), "c")
        X0 = 1180
        text(c, "all-reduce:", X0, 420, 38, "i", Pal.INK, A * fade(t, T0 + 1, 0.7))
        text(c, "every process ends with the sum", X0, 468, 28, "r", Pal.INK, A * fade(t, T0 + 1.5, 0.7))
        text(c, "of everyone's vectors", X0, 504, 28, "r", Pal.INK, A * fade(t, T0 + 1.5, 0.7))
        text(c, "the traffic in HPC and AI is mostly collectives", X0, 600, 24, "i", Pal.GOLD, A * fade(t, T0 + 9, 0.8))
    # ---- beat 1 : alpha-beta, ring
    B = fade(t, ctx.b0(1) + 0.2, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if B > 0:
        T0 = ctx.b0(1)
        n = 8; cx, cy = 560, 540
        pts = ring_pts(cx, cy, 230, n)
        step_dur = 1.3
        s_f = max(0.0, (t - T0 - 8.0) / step_dur)
        step = int(min(s_f, 14))
        ph = (s_f - step) if s_f < 14 else 1.0
        for i in range(n):
            line(c, *pts[i], *pts[(i + 1) % n], Pal.FAINT, 3, B)
        for i, p in enumerate(pts):
            circle(c, *p, 22, Pal.BG, B, Pal.INK, 2.4, B)
            text(c, str(i), p[0], p[1] + 7, 20, "b", Pal.MUTED, B, "c")
        if s_f > 0 and s_f < 14.9:
            col = Pal.BLUE if step < 7 else Pal.GREEN
            for i in range(n):
                a_, b_ = pts[i], pts[(i + 1) % n]
                u = smooth(ph)
                rect(c, lerp(a_[0], b_[0], u) - 9, lerp(a_[1], b_[1], u) - 9, 18, 18, col, B, r=3)
            small_caps(c, ("reduce-scatter" if step < 7 else "all-gather") + f"  ·  step {min(step + 1, 14)} of 14", cx, 840, 16, col, B, "c")
        text(c, "each vector cut into p chunks, passed around the ring", cx, 250, 22, "i", Pal.MUTED, B * fade(t, T0 + 6, 0.8), "c")
        X0 = 1000
        a1 = B * fade(t, T0 + 1.0, 0.8)
        rich(c, "sending $n$ bytes costs  $\\alpha$ + $n$/$B$".replace("\\alpha", "α"), X0, 330, 32, Pal.INK, a1)
        text(c, "a startup, plus time per byte — topology ignored on purpose", X0, 366, 20, "i", Pal.MUTED, a1)
        a2 = B * fade(t, T0 + 14.0, 0.8)
        rich(c, "ring:  2($p$−1) steps", X0, 470, 32, Pal.INK, a2)
        a3 = B * fade(t, T0 + 20.0, 0.8)
        rich(c, "bandwidth term  =  2 · ($p$−1)/$p$ · $n$/$B$", X0, 540, 30, Pal.GOLD, a3)
        text(c, "the minimum possible", X0, 576, 22, "i", Pal.GOLD, a3)
        a4 = B * fade(t, T0 + 26.0, 0.8)
        text(c, "Patarasuk & Yuan: ring is bandwidth-optimal", X0, 660, 24, "r", Pal.INK, a4)
        text(c, "on any tree-connected network, one port per node", X0, 696, 24, "r", Pal.INK, a4)
    # ---- beat 2 : latency gap
    C = fade(t, ctx.b0(2) + 0.2, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if C > 0:
        T0 = ctx.b0(2)
        LO = CO["latency_only"]["1024"]
        text(c, "startup cost with 1,024 processes at 2 µs per message", 960, 290, 24, "i", Pal.MUTED, C, "c")
        # log bars
        def lb(v): return (math.log10(v) - math.log10(1e-5)) / (math.log10(1e-2) - math.log10(1e-5))
        rows = [("ring: 2(p−1)·α", LO["ring"], Pal.RED, "4.09 ms"), ("halving & doubling: 2·log₂p·α", LO["rabenseifner"], Pal.GREEN, "40 µs")]
        for k, (nm, v, col, lab) in enumerate(rows):
            a = C * fade(t, T0 + 1.5 + k * 3.5, 0.8)
            y = 420 + k * 130
            text(c, nm, 460, y + 10, 28, "i", Pal.INK, a, "r")
            bar_h(c, 500, y - 22, 1000 * lb(v) * a, 44, 1.0, col, a)
            text(c, lab, 500 + 1000 * lb(v) * a + 18, y + 12, 34, "b", col, a)
        note(c, "log scale", 500, 640, C * fade(t, T0 + 2, 0.6), 18)
        text(c, "same data moved, 100× less waiting", 960, 760, 34, "i", Pal.GOLD, C * fade(t, T0 + 8, 0.8), "c")
    # ---- beat 3 : NCCL
    D = fade(t, ctx.b0(3) + 0.2, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        T0 = ctx.b0(3)
        # ring chain vs binary tree
        xs = [200 + i * 90 for i in range(8)]
        for i in range(7):
            line(c, xs[i], 380, xs[i + 1], 380, Pal.RED, 3, D)
        for x in xs:
            circle(c, x, 380, 12, Pal.BG, D, Pal.RED, 2.4, D)
        text(c, "ring: latency grows linearly with GPUs", 480, 460, 24, "i", Pal.RED, D, "c")
        tp = {}
        for lvl in range(4):
            for i in range(2 ** lvl):
                tp[(lvl, i)] = (1330 + (i - (2 ** lvl - 1) / 2) * (330 / 2 ** lvl) * 1.8, 280 + lvl * 80)
        for lvl in range(3):
            for i in range(2 ** lvl):
                for ch in (2 * i, 2 * i + 1):
                    line(c, *tp[(lvl, i)], *tp[(lvl + 1, ch)], Pal.GREEN, 2.4, D * fade(t, T0 + 3, 0.8))
        for k, p in tp.items():
            circle(c, *p, 11, Pal.BG, D * fade(t, T0 + 3, 0.8), Pal.GREEN, 2.4, D)
        text(c, "double binary tree: latency ∝ log GPUs", 1330, 560, 24, "i", Pal.GREEN, D * fade(t, T0 + 3, 0.8), "c")
        a = D * fade(t, T0 + 9, 0.9)
        text(c, "NVIDIA's NCCL team reported", 960, 700, 28, "r", Pal.INK, a, "c")
        text(c, "up to 180× lower latency", 960, 764, 54, "b", Pal.GOLD, a, "c")
        text(c, "double binary tree vs ring, 24K GPUs on Summit — NVIDIA's measurement", 960, 810, 20, "i", Pal.MUTED, a, "c")
    # ---- beat 4 : cost vs message size
    E_ = fade(t, ctx.b0(4) + 0.2, 0.8) * (1 - fade(t, ctx.b0(5) - 0.3, 0.6))
    if E_ > 0:
        T0 = ctx.b0(4)
        P1 = CO["p1024"]
        ns = P1["n"]
        ax = Axes(260, 800, 1700, 260, (ns[0], ns[-1]), (1e-6, 10.0), xlog=True, ylog=True)
        ax.frame(c, [64, 4096, 262144, 16777216, 1073741824], [1e-6, 1e-4, 1e-2, 1], lambda v: ("%g" % v) if v < 1024 else (f"{int(v / 1024):,} KB" if v < 1048576 else f"{int(v / 1048576):,} MB" if v < 1073741824 else "1 GB"), lambda v: f"{v:g} s" if v >= 1 else (f"{v * 1e3:g} ms" if v >= 1e-3 else f"{v * 1e6:g} µs"), E_, 16, "message size n", "time")
        prg = fade(t, T0 + 1.0, 5.0)
        spec = [("ring", "ring", Pal.RED), ("recdbl", "recursive doubling", Pal.ORANGE), ("rabenseifner", "halving & doubling", Pal.GREEN)]
        for key, nm, col in spec:
            ys = P1[key]
            pts = [(ax.X(n_), ax.Y(max(v, 1e-6))) for n_, v in zip(ns, ys)]
            k = max(2, int(len(pts) * prg))
            polyline(c, pts[:k], col, 3.4, E_)
            if prg > 0.95:
                lx_, ly_ = pts[4]
                text(c, nm, lx_ + 30, ly_ + {"ring": -16, "recdbl": 34, "rabenseifner": -14}[key], 20, "r", col, E_ * fade(t, T0 + 6.5, 0.6), "l")
        text(c, "small messages: startup dominates → logarithmic algorithms win", 340, 300, 22, "i", Pal.INK, E_ * fade(t, T0 + 6, 0.8))
        text(c, "large: bandwidth dominates → ring and halving-doubling converge", 340, 336, 22, "i", Pal.INK, E_ * fade(t, T0 + 8, 0.8))
        note(c, "α = 2 µs, 50 GB/s per link, p = 1,024 — this video's α–β model", 260, 930, E_, 18)
    # ---- beat 5 : partner distance
    F = fade(t, ctx.b0(5) + 0.2, 0.8) * (1 - fade(t, ctx.b0(6) - 0.3, 0.6))
    if F > 0:
        T0 = ctx.b0(5)
        n = 16; xs = [180 + i * 104 for i in range(n)]; y = 560
        for i, x in enumerate(xs):
            circle(c, x, y, 13, Pal.BG, F, Pal.INK, 2.2, F)
        # leaf grouping (4 per leaf)
        for l in range(4):
            rect(c, xs[l * 4] - 24, y - 40, xs[l * 4 + 3] - xs[l * 4] + 48, 80, None, F, Pal.FAINT, 1.5, F, r=10)
            text(c, f"leaf {l}", (xs[l * 4] + xs[l * 4 + 3]) / 2, y + 74, 18, "i", Pal.MUTED, F, "c")
        a = F * fade(t, T0 + 1.5, 0.8)
        for i in range(n):
            j = (i + 1) % n
            if j > i:
                curve(c, xs[i], y - 16, xs[j], y - 16, -22, Pal.GREEN, 2.4, a * 0.9)
        text(c, "ring: talks to neighbours — mostly inside a leaf", 960, 330, 26, "i", Pal.GREEN, a, "c")
        b = F * fade(t, T0 + 6.0, 0.8)
        for i in range(8):
            curve(c, xs[i], y + 16, xs[i + 8], y + 16, 130 + (i % 2) * 14, Pal.RED, 2.2, b * 0.8)
        text(c, "recursive halving: first swap half the vector with a partner p/2 away", 960, 840, 26, "i", Pal.RED, b, "c")
        text(c, "the biggest messages go the farthest — through the uplinks", 960, 884, 26, "i", Pal.RED, F * fade(t, T0 + 9.5, 0.8), "c")
    # ---- beat 6 : placement bars
    G_ = fade(t, ctx.b0(6) + 0.2, 0.8) * (1 - fade(t, ctx.b0(7) - 0.3, 0.6))
    if G_ > 0:
        T0 = ctx.b0(6)
        PL = R["placement"]["4to1"]
        small_caps(c, "slowdown vs a non-blocking tree, 512 ranks on 16 leaves of 32, blocking factor 4 : 1", 960, 250, 15, Pal.MUTED, G_, "c")
        rows = [("ring, ranks in order", PL["ring_block"], Pal.GREEN, T0 + 2.0),
                ("ring, ranks shuffled across leaves", PL["ring_cyclic"], Pal.RED, T0 + 7.0),
                ("recursive halving, ranks in order", PL["rab_block_halving"], Pal.RED, T0 + 12.0),
                ("halving, big messages to near neighbours first", PL["rab_block_doubling"], Pal.GREEN, T0 + 18.0)]
        for k, (nm, v, col, t0) in enumerate(rows):
            a = G_ * fade(t, t0, 0.7)
            y = 340 + k * 110
            text(c, nm, 700, y + 10, 26, "i", Pal.INK, a, "r")
            bw = 800 * v / 4.2 * fade(t, t0 + 0.2, 1.0)
            bar_h(c, 740, y - 20, bw, 40, 1.0, col, a)
            text(c, f"{v:.2f}×", 740 + bw + 16, y + 12, 32, "b", col, a)
        note(c, "fluid model: traffic sprayed perfectly across spines, so placement is isolated from hashing", 960, 840, G_ * fade(t, T0 + 20, 0.8), 20, Pal.MUTED, "c")
    # ---- beat 7 : conclusion
    H_ = fade(t, ctx.b0(7) + 0.3, 0.9)
    if H_ > 0:
        T0 = ctx.b0(7)
        big(c, "same cluster · same algorithms", 960, 400, H_, 46, Pal.INK, "c", "i")
        big(c, "a factor of four", 960, 520, H_ * fade(t, T0 + 3, 0.9), 96, Pal.GOLD, "c", "b")
        big(c, "decided entirely by who talks to whom", 960, 610, H_ * fade(t, T0 + 6, 0.9), 40, Pal.INK, "c", "i")
        text(c, "that is why topology-aware collectives exist — and why rank order is not a detail", 960, 740, 26, "r", Pal.MUTED, H_ * fade(t, T0 + 11, 0.8), "c")
    footer(c, "Patarasuk & Yuan 2009 · Thakur et al. 2005 · NVIDIA 2019 (NCCL) · this video's α–β and placement models", 1.0)


# ------------------------------------------------------------------ 13 place
@scene
def s_place(c, t, ctx):
    # ---- beat 0
    A = fade(t, ctx.b0(0) + 0.2, 0.8) * (1 - fade(t, ctx.b0(1) - 0.3, 0.6))
    if A > 0:
        T0 = ctx.b0(0)
        items = [("tree", "fat tree", "which nodes share a leaf?"), ("torus", "torus", "is there a contiguous box?"), ("dragonfly", "dragonfly", "which groups, and how loaded?")]
        for k, (kd, nm, q) in enumerate(items):
            a = A * fade(t, T0 + 0.8 + k * 1.8, 0.8)
            x = 380 + k * 580
            glyph(c, kd, x, 440, 170, a)
            text(c, nm, x, 590, 34, "i", Pal.INK, a, "c")
            text(c, q, x, 640, 24, "r", Pal.GOLD, a, "c")
    # ---- beat 1 : Slurm tree
    B = fade(t, ctx.b0(1) + 0.2, 0.8) * (1 - fade(t, ctx.b0(2) - 0.3, 0.6))
    if B > 0:
        T0 = ctx.b0(1)
        busy = {0: [0, 1, 2, 3, 4], 1: [0, 1, 2, 3, 4, 5, 6, 7], 2: [0, 1, 2, 3], 3: [0, 2, 5, 7]}
        free_ct = {l: 8 - len(busy[l]) for l in busy}
        lx = [270 + l * 270 for l in range(4)]
        for l in range(4):
            line(c, lx[l], 440, 540 + (l % 2) * 270 if False else 675, 300, Pal.BLUE, 2.4, B * 0.7)
        switch(c, 675, 300, B, r=18)
        text(c, "spine", 675, 262, 20, "i", Pal.MUTED, B, "c")
        for l in range(4):
            switch(c, lx[l], 440, B, r=16)
            for k in range(8):
                x, y = lx[l] - 98 + (k % 4) * 65, 560 + (k // 4) * 52
                line(c, lx[l], 440, x, y - 8, Pal.FAINT, 1.2, B)
                rect(c, x - 14, y - 14, 28, 28, Pal.FAINT if k in busy[l] else Pal.BLUE, B * (0.9 if k in busy[l] else 0.35), Pal.MUTED if k in busy[l] else Pal.BLUE, 1.4, B, r=3)
        # job A: needs 3 nodes -> best fit leaf with fewest free >= 3 : leaf 3 (4 free) beats leaf 0 (3 free)? leaf0 has 3 free exactly -> best fit
        ja = fade(t, T0 + 6, 0.8)
        for k in (5, 6, 7):
            x, y = lx[0] - 98 + (k % 4) * 65, 560 + (k // 4) * 52
            rect(c, x - 14, y - 14, 28, 28, Pal.GOLD, B * ja * 0.9, r=3)
        text(c, "job A needs 3 → fits under one leaf, best fit", lx[0] + 60, 700, 22, "i", Pal.GOLD, B * ja, "c")
        jb = fade(t, T0 + 11, 0.8)
        for l, ks in ((2, [4, 5, 6, 7]), (3, [1, 3, 4, 6])):
            for k in ks:
                x, y = lx[l] - 98 + (k % 4) * 65, 560 + (k // 4) * 52
                rect(c, x - 14, y - 14, 28, 28, Pal.GREEN, B * jb * 0.9, r=3)
        text(c, "job B needs 8 → lowest switch that can hold it: the spine", 1320, 700, 22, "i", Pal.GREEN, B * jb, "c")
        # right/bottom config
        cf = fade(t, T0 + 15, 0.8)
        rect(c, 150, 760, 1060, 150, Pal.BG, B * cf, Pal.FAINT, 1.2, B * cf, r=6)
        mono(c, "SwitchName=leaf0 Nodes=n[0-7]", 175, 800, 22, Pal.INK, B * cf)
        mono(c, "SwitchName=spine Switches=leaf[0-3]", 175, 836, 22, Pal.INK, B * cf)
        cf2 = fade(t, T0 + 19, 0.8)
        mono(c, "sbatch --switches=1@60 …", 175, 884, 22, Pal.GOLD, B * cf2)
        text(c, "≤ 1 leaf switch, wait ≤ 60 min: queue time for locality", 650, 884, 20, "i", Pal.MUTED, B * cf2)
        text(c, "topology.conf (tree plugin)", 1240, 800, 22, "i", Pal.MUTED, B * cf)
        text(c, "a newer block topology allocates contiguous node blocks", 1240, 840, 22, "r", Pal.INK, B * fade(t, T0 + 22, 0.8))
        text(c, "to limit fragmentation", 1240, 872, 22, "r", Pal.INK, B * fade(t, T0 + 22, 0.8))
    # ---- beat 2 : torus contiguity
    C = fade(t, ctx.b0(2) + 0.2, 0.8) * (1 - fade(t, ctx.b0(3) - 0.3, 0.6))
    if C > 0:
        T0 = ctx.b0(2)
        k = 8; sp = 70; ox, oy = 250, 300
        busy_cells = {(0, 2), (0, 3), (1, 2), (1, 5), (2, 0), (2, 4), (3, 1), (3, 3), (3, 7), (4, 2), (4, 5), (5, 0), (5, 3), (5, 6), (6, 1), (6, 4), (6, 7), (7, 2), (7, 5), (0, 6), (2, 7), (4, 0), (7, 0)}
        free_n = k * k - len(busy_cells)
        for r in range(k):
            for c_ in range(k):
                x, y = ox + c_ * sp, oy + r * sp
                b = (r, c_) in busy_cells
                rect(c, x - 26, y - 26, 52, 52, Pal.FAINT if b else Pal.BLUE, C * (0.9 if b else 0.3), Pal.MUTED if b else Pal.BLUE, 1.3, C, r=4)
        text(c, f"{free_n} nodes are free", ox + 3.5 * sp, 250, 28, "r", Pal.INK, C * fade(t, T0 + 2, 0.7), "c")
        # attempted 4x4 box
        a = C * fade(t, T0 + 5, 0.8)
        rect(c, ox - 30, oy - 30, 4 * sp - 8, 4 * sp - 8, None, a, Pal.RED, 4, a, r=6, dash=(10, 8))
        text(c, "the job wants a 4 × 4 box:  there isn't one", ox + 3.5 * sp, oy + 8.2 * sp, 26, "i", Pal.RED, a, "c")
        X0 = 1010
        text(c, "enough nodes, wrong shape", X0, 340, 32, "i", Pal.INK, C * fade(t, T0 + 7, 0.8))
        text(c, "Slurm: a torus plugin", X0, 440, 26, "r", Pal.INK, C * fade(t, T0 + 10, 0.8))
        text(c, "Tofu: the user asks for a shape", X0, 482, 26, "r", Pal.INK, C * fade(t, T0 + 13, 0.8))
        text(c, "Google's optical switches: no contiguity needed", X0, 524, 26, "r", Pal.GOLD, C * fade(t, T0 + 16, 0.8))
        text(c, "without them, host availability would need to be 99.9%", X0, 566, 22, "i", Pal.MUTED, C * fade(t, T0 + 19, 0.8))
        text(c, "for reasonable slice goodput (Google's paper)", X0, 596, 22, "i", Pal.MUTED, C * fade(t, T0 + 19, 0.8))
    # ---- beat 3 : dragonfly interference
    D = fade(t, ctx.b0(3) + 0.2, 0.8) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        T0 = ctx.b0(3)
        G = 6
        gp = lambda g: df_group_pos(g, G, 560, 520, 230)
        for i in range(G):
            for j in range(i + 1, G):
                hot = (i, j) in ((0, 1), (0, 2), (1, 2))
                line(c, *gp(i), *gp(j), Pal.RED if hot and t > T0 + 4 else Pal.FAINT, 3 if hot and t > T0 + 4 else 1.4, D * (0.9 if hot else 0.8) * (fade(t, T0 + 4, 0.8) if hot else 1) + (D * 0.8 * (1 - fade(t, T0 + 4, 0.8)) if hot else 0))
        for g in range(G):
            x, y = gp(g)
            circle(c, x, y, 34, Pal.BG, D, Pal.INK, 2.6, D)
        # heavy job (red) on groups 0,1,2 ; light job (blue) on 1,3
        for g in (0, 1, 2):
            circle(c, *gp(g), 22, Pal.RED, D * fade(t, T0 + 2, 0.7) * 0.8)
        for g in (3,):
            circle(c, *gp(g), 22, Pal.BLUE, D * fade(t, T0 + 6, 0.7) * 0.9)
        text(c, "bully", gp(0)[0] - 60, gp(0)[1] - 50, 22, "i", Pal.RED, D * fade(t, T0 + 4, 0.7), "c")
        text(c, "victim", gp(3)[0] + 70, gp(3)[1] + 44, 22, "i", Pal.BLUE, D * fade(t, T0 + 8, 0.7), "c")
        X0 = 1010
        text(c, "Bhatele et al.: hot spots on a few links", X0, 330, 26, "r", Pal.INK, D * fade(t, T0 + 2, 0.8))
        text(c, "when each task has few neighbours", X0, 366, 22, "i", Pal.MUTED, D * fade(t, T0 + 2.5, 0.8))
        text(c, "Yang et al.: random placement + adaptive routing", X0, 470, 26, "r", Pal.INK, D * fade(t, T0 + 10, 0.8))
        text(c, "balances load — but communication-heavy jobs", X0, 506, 26, "r", Pal.INK, D * fade(t, T0 + 11, 0.8))
        text(c, "can degrade lighter ones: a bully effect", X0, 542, 26, "r", Pal.RED, D * fade(t, T0 + 12, 0.8))
        text(c, "a hybrid placement reduced the worst case", X0, 640, 26, "r", Pal.GREEN, D * fade(t, T0 + 17, 0.8))
    # ---- beat 4 : Slingshot claim + synthesis
    E_ = fade(t, ctx.b0(4) + 0.3, 0.9)
    if E_ > 0:
        T0 = ctx.b0(4)
        small_caps(c, "worst-case congestion slowdown, HPE's benchmarks (log scale)", 960, 260, 15, Pal.MUTED, E_, "c")
        lb = lambda v: math.log10(v) / math.log10(100)
        for k, (nm, v, col) in enumerate([("Slingshot", 1.3, Pal.GREEN), ("Aries", 93, Pal.RED)]):
            a = E_ * fade(t, T0 + 1.5 + k * 3, 0.8)
            y = 340 + k * 80
            text(c, nm, 500, y + 10, 28, "i", Pal.INK, a, "r")
            bw = 900 * max(0.03, lb(v)) * a
            bar_h(c, 530, y - 20, bw, 40, 1.0, col, a)
            text(c, f"{v:g}×", 530 + bw + 16, y + 12, 32, "b", col, a)
        text(c, "the authors' benchmarks — a claim to test", 960, 490, 24, "i", Pal.GOLD, E_ * fade(t, T0 + 8, 0.8), "c")
        # four-way agreement
        names = ["cables", "routing", "algorithm", "placement"]
        for k, nm in enumerate(names):
            a = E_ * fade(t, T0 + 12 + k * 1.5, 0.8)
            x = 330 + k * 420
            rect(c, x - 140, 640, 280, 80, Pal.BG, a, [Pal.BLUE, Pal.ORANGE, Pal.GREEN, Pal.PURPLE][k], 2.6, a, r=10)
            text(c, nm, x, 692, 34, "i", Pal.INK, a, "c")
        text(c, "topology is not a property of the cables alone — they have to agree", 960, 810, 30, "i", Pal.GOLD, E_ * fade(t, T0 + 19, 0.9), "c")
    footer(c, "SchedMD Slurm topology docs · Bhatele et al. SC11 · Yang et al. SC16 · De Sensi et al. SC20 · Jouppi et al. 2023", 1.0)


# ------------------------------------------------------------------ 14 zoo
ZOO = [
    ("Myrinet", "Myricom", "cluster network built when Ethernet meant 100 Mb/s: low-overhead switching, link-level flow control",
     "peak June 2005: 141 TOP500 systems (28%) · June 2014: 1 · assets sold 2013", "history", Pal.MUTED, 1),
    ("QsNet", "Quadrics", "fat-tree network whose adapters took communication work off the processor",
     "6 of the 10 fastest, June 2003 · company closed June 2009", "history", Pal.MUTED, 1),
    ("Blue Gene", "IBM", "tens of thousands of simple nodes behind a torus, plus tree and barrier networks (Q: 5-D torus)",
     "IBM moved to other platforms", "history", Pal.MUTED, 2),
    ("Tofu", "Fujitsu", "6-D torus · 6 interfaces per node · 6.8 GB/s per link",
     "Fugaku: #9, June 2026 list", "alive", Pal.GREEN, 2),
    ("Aries → Slingshot", "Cray / HPE", "3-D torus → dragonfly (Aries, 2012: ≤ 5 hops) → Slingshot: 64 × 200 Gb/s, Ethernet-compatible, hardware congestion management",
     "El Capitan · Frontier · Aurora · 6 of the top 10", "alive", Pal.GREEN, 3),
    ("Omni-Path", "Intel → Cornelis", "lossless alternative to InfiniBand (2015) · Trinity, Cori",
     "Intel dropped it by 2019 · Cornelis spun out 2020 · CN5000, 400 Gb/s, 2025", "niche", Pal.GOLD, 4),
    ("LingQi", "LineShine (#1)", "reported multi-rail fat tree, 1.6 Tb/s per node",
     "single outlet — I could not confirm it", "unconfirmed", Pal.ORANGE, 4),
]


@scene
def s_zoo(c, t, ctx):
    A = fade(t, ctx.b0(0) + 0.2, 0.8)
    x0 = 160
    small_caps(c, "name", x0, 232, 15, Pal.MUTED, A)
    small_caps(c, "what it was for", 470, 232, 15, Pal.MUTED, A)
    small_caps(c, "where it stands", 1280, 232, 15, Pal.MUTED, A)
    small_caps(c, "status", 1760, 232, 15, Pal.MUTED, A, "r")
    line(c, x0, 246, 1760, 246, Pal.FAINT, 1.2, A)
    # group rows by beat (1..4); beat 5 is interpretation
    y = 280
    row_h = 96
    for k, (nm, who, why, now, st, col, beat) in enumerate(ZOO):
        t0 = ctx.b0(beat) + 0.3 + (0.0 if k == 0 or ZOO[k - 1][6] != beat else (ctx.b1(beat) - ctx.b0(beat)) * 0.45)
        a = fade(t, t0, 0.8)
        yy = y + k * row_h
        text(c, nm, x0, yy + 22, 28, "b", Pal.INK, a)
        text(c, who, x0, yy + 50, 19, "i", Pal.MUTED, a)
        for i, ln in enumerate(wrap(why, 21, "r", 760)[:3]):
            text(c, ln, 470, yy + 18 + i * 26, 21, "r", Pal.INK, a)
        for i, ln in enumerate(wrap(now, 21, "r", 370)[:3]):
            text(c, ln, 1280, yy + 18 + i * 26, 21, "r", Pal.MUTED, a)
        small_caps(c, st, 1760, yy + 22, 15, col, a, "r")
        line(c, x0, yy + row_h - 16, 1760, yy + row_h - 16, Pal.FAINT, 0.8, a * 0.7)
    # beat 5 : interpretation
    s5 = fade(t, ctx.b0(5) + 0.3, 0.9)
    if s5 > 0:
        rect(c, 0, 120, DW, 900, Pal.BG, s5 * 0.96)
        text(c, "my read — interpretation, not a sourced claim", 960, 380, 26, "i", Pal.GOLD, s5, "c")
        a = s5 * fade(t, ctx.b0(5) + 1.0, 0.9)
        text(c, "the ones that died were out-competed on", 960, 490, 44, "i", Pal.INK, a, "c")
        text(c, "cost and volume by Ethernet and InfiniBand", 960, 548, 44, "i", Pal.INK, a, "c")
        b = s5 * fade(t, ctx.b0(5) + 6.0, 0.9)
        text(c, "the ones that survive are tied to a builder's whole machine", 960, 680, 36, "i", Pal.GREEN, b, "c")
    footer(c, "TOP500 June 2026 · Myricom · Quadrics · IBM · Fujitsu · HPE/Cray · Cornelis (see notes for sources)", A)


# ------------------------------------------------------------------ 15 close
@scene
def s_close(c, t, ctx):
    items = [("1", "bisection is a ceiling, not a promise", "the narrowest cut for your traffic decides — routing decides whether you reach it", Pal.GOLD, 0),
             ("2", "every topology is a bet on traffic", "neighbours → tori  ·  permutations, collectives → fat trees  ·  cable-limited scale → dragonfly, HyperX", Pal.BLUE, 1),
             ("3", "wires, routing, algorithm, placement must agree", "change any one and the same hardware can be several times faster — or slower", Pal.GREEN, 2)]
    hide3 = fade(t, ctx.b0(3) - 0.3, 0.7)
    for k, (n, h1, h2, col, beat) in enumerate(items):
        a = fade(t, ctx.b0(beat) + 0.3, 0.9) * (1 - hide3)
        y = 330 + k * 190
        text(c, n, 220, y + 24, 96, "i", col, a, "c")
        text(c, h1, 330, y + 6, 42, "i", Pal.INK, a)
        text(c, h2, 330, y + 50, 24, "r", Pal.MUTED, a)
    # beat 3 : the measurement suggestion
    D = fade(t, ctx.b0(3) + 0.3, 0.9) * (1 - fade(t, ctx.b0(4) - 0.3, 0.6))
    if D > 0:
        T0 = ctx.b0(3)
        small_caps(c, "a suggestion of mine, not a standard method: all-to-all bandwidth per node", 960, 250, 16, Pal.MUTED, D, "c")
        vals = [("inside one leaf", 1.0), ("across leaves", 0.62), ("whole machine", 0.34)]
        ax = Axes(520, 780, 1500, 330, (0, 3), (0, 1.1))
        for k, (nm, v) in enumerate(vals):
            a = D * fade(t, T0 + 1.0 + k * 2.2, 0.8)
            x = 520 + 160 + k * 320
            bar_h(c, x, 760 - 380 * v * a, 0, 0, 1.0)  # no-op keeps API usage simple
            rect(c, x - 70, 760 - 380 * v * a, 140, 380 * v * a, Pal.BLUE, a * 0.9)
            text(c, nm, x, 800, 22, "i", Pal.INK, a, "c")
            if k > 0:
                prev = vals[k - 1][1]
                text(c, "drop = blocking factor", x - 160, 760 - 380 * (v + prev) / 2 - 20, 18, "i", Pal.RED, a * fade(t, T0 + 4 + k * 1.5, 0.7), "c")
        note(c, "illustrative shape only — not measured data", 960, 880, D, 18, Pal.MUTED, "c")
        text(c, "the drop-offs are the blocking factors, measured", 960, 930, 28, "i", Pal.GOLD, D * fade(t, T0 + 9, 0.8), "c")
    E_ = fade(t, ctx.b0(4) + 0.3, 0.9)
    if E_ > 0:
        big(c, "sources, and the status of every number", 960, 470, E_, 44, Pal.INK, "c", "i")
        big(c, "verified · modelled · unverified", 960, 540, E_ * fade(t, ctx.b0(4) + 1.5, 0.8), 34, Pal.GOLD, "c", "r")
        text(c, "are in the notes that come with this video", 960, 610, 26, "i", Pal.MUTED, E_ * fade(t, ctx.b0(4) + 3, 0.8), "c")
