"""Scenes 7-9: routing, congestion, sharp"""
import math, random
from engine import *


# ---------------------------------------------------------------------------------------------- routing
class Routing(Scene):
    id = "routing"
    title = "Routing: a planner, or a hash"
    sources = ("OpenSM routing engines (min-hop, up/down, ftree, dfsssp, lash, nue).  Throughput figures: MY TOY MODEL (max-min fair sharing, 16 leaves x 16 hosts, 1:1, "
               "300 random permutations; src/model_numbers.py) - not a measurement.  Microsoft ~60 %: Guo et al., SIGCOMM 2016 (production Clos, 40GbE).")

    def __init__(self, timing):
        super().__init__(timing)
        rng = random.Random(11)
        self.L, self.H, self.U = 4, 4, 4
        N = self.L * self.H
        perm = list(range(N)); rng.shuffle(perm)
        self.flows = []
        for s in range(N):
            d = perm[s]
            if s // self.H == d // self.H: continue
            self.flows.append((s, d, rng.randrange(self.U)))
        self.up, self.down = {}, {}
        for s, d, sp in self.flows:
            self.up[(s // self.H, sp)] = self.up.get((s // self.H, sp), 0) + 1
            self.down[(sp, d // self.H)] = self.down.get((sp, d // self.H), 0) + 1

    # geometry of the demo fabric
    def pos(self, kind, i, x0=260, x1=1660):
        if kind == "spine": return (x0 + (i + 0.5) * (x1 - x0) / self.U, 300)
        if kind == "leaf": return (x0 + (i + 0.5) * (x1 - x0) / self.L, 520)
        return (x0 + (i + 0.5) * (x1 - x0) / (self.L * self.H), 720)

    def fabric(self, c, a, show_lids=False, hl=None):
        for l in range(self.L):
            for s in range(self.U):
                p, q = self.pos("leaf", l), self.pos("spine", s)
                line(c, p[0], p[1], q[0], q[1], FAINT, 1.0, a * 0.7)
        for h in range(self.L * self.H):
            p, q = self.pos("host", h), self.pos("leaf", h // self.H)
            line(c, p[0], p[1], q[0], q[1], FAINT, 1.0, a * 0.7)
            circle(c, p[0], p[1], 7, fill=BG, stroke=INK, sw=1.2, a=a)
            if show_lids:
                text(c, str(h + 1), p[0], p[1] + 30, 18, HI, "mono", "c", a)
        for s in range(self.U):
            p = self.pos("spine", s); switch_icon(c, p[0] - 45, p[1] - 14, 90, 28, IB, a, 4)
        for l in range(self.L):
            p = self.pos("leaf", l); switch_icon(c, p[0] - 45, p[1] - 14, 90, 28, IB, a, 4)

    def draw(self, c, t):
        B = self.B
        # ---- beats 0-1 : subnet manager discovery / LIDs / forwarding table
        if t < B(2) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            self.fabric(c, a, show_lids=t > B(1) + 1.0)
            # SM node
            sm = (960, 190)
            circle(c, sm[0], sm[1], 30, stroke=IB, sw=2.5, fill=BG2, a=a)
            text(c, "SM", sm[0], sm[1] + 8, 24, IB, "sansb", "c", a)
            text(c, "master subnet manager", sm[0] + 60, sm[1] + 8, 22, DIM, "serifi", "l", a)
            # discovery wave: hop by hop BFS (spines -> leaves -> hosts)
            w = (t - B(0)) / 5.0
            if B(0) < t < B(1) + 0.5:
                for s in range(self.U):
                    u = clamp(w * 2.0 - 0.0)
                    p = self.pos("spine", s)
                    line(c, sm[0], sm[1] + 30, *lerp2((sm[0], sm[1] + 30), (p[0], p[1] - 14), u), IB, 2, a)
                    if u >= 1: dot(c, p[0], p[1], 6, IB, a)
                for l in range(self.L):
                    for s in range(self.U):
                        u = clamp(w * 2.0 - 1.0)
                        p, q = self.pos("spine", s), self.pos("leaf", l)
                        r = lerp2((p[0], p[1] + 14), (q[0], q[1] - 14), u)
                        line(c, p[0], p[1] + 14, r[0], r[1], IB, 1.6, a * 0.8)
                for h in range(self.L * self.H):
                    u = clamp(w * 2.0 - 2.0)
                    q = self.pos("leaf", h // self.H); p = self.pos("host", h)
                    line(c, q[0], q[1] + 14, *lerp2((q[0], q[1] + 14), (p[0], p[1] - 7), u), IB, 1.6, a * 0.8)
                    if u >= 1: dot(c, p[0], p[1], 5, IB, a, False)
                text(c, "discovery: management packets, hop by hop", 960, 880, 26, IB, "serifi", "c", a)
            if t > B(1) + 1.0:
                text(c, "every port gets a 16-bit local identifier (LID)", 960, 880, 26, HI, "serifi", "c", a * P(t, B(1) + 1.0, B(1) + 2.0))
            # forwarding table
            if t > B(1) + 5.0:
                fa = a * P(t, B(1) + 5.0, B(1) + 6.0)
                rect(c, 1400, 600, 360, 250, fill=BG2, stroke=IB, sw=1.4, r=6, a=fa)
                text(c, "leaf 2 forwarding table", 1580, 632, 20, IB, "sansm", "c", fa)
                text(c, "dest LID", 1470, 664, 18, DIM, "sans", "c", fa); text(c, "out port", 1690, 664, 18, DIM, "sans", "c", fa)
                rows = [(1, 2), (5, 5), (9, 6), (13, 7)]
                for i, (d, p_) in enumerate(rows):
                    text(c, str(d), 1470, 702 + i * 38, 24, INK, "mono", "c", fa); text(c, str(p_), 1690, 702 + i * 38, 24, INK, "mono", "c", fa)
                text(c, "destination in, port out", 1580, 880, 20, DIM, "serifi", "c", fa * P(t, B(1) + 8, B(1) + 9))
                # packet: host 1 -> leaf0 -> spine -> leaf3 -> host 16 (a series of lookups)
                if t > B(1) + 10:
                    path = [self.pos("host", 0), self.pos("leaf", 0), self.pos("spine", 1), self.pos("leaf", 3), self.pos("host", 15)]
                    u = ((t - B(1) - 10) * 0.18) % 1.4
                    if u < 1.0:
                        px = along(path, u); pkt(c, px[0], px[1], HI, 22, 12, fa)
                    text(c, "a journey is a series of lookups", 960, 930, 24, DIM, "serifi", "c", fa)
        # ---- beat 2: routing engines
        if B(2) - 0.3 < t < B(3) + 0.8:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.8))
            text(c, "choosing the algorithm", 960, 200, 36, DIM, "serifi", "c", a)
            eng = [("min-hop", "shortest paths; may form credit loops"), ("up/down", "never go up after going down"),
                   ("ftree", "fat-tree aware, destination-based"), ("dfsssp · lash · nue", "use virtual lanes to break cycles on any topology")]
            for i, (n, d) in enumerate(eng):
                ts = B(2) + 2.0 + i * 3.0
                aa = a * P(t, ts, ts + 1.0)
                x = 150 + i * 430
                rect(c, x, 280, 390, 190, fill=BG2, stroke=IB, sw=1.2, r=6, a=aa)
                text(c, n, x + 195, 340, 34, IB, "mono" if i < 3 else "sansm", "c", aa)
                para(c, d, x + 24, 390, 340, 22, DIM, "serifi", 1.3, aa)
            ua = a * P(t, B(2) + 5.5, B(2) + 6.5)
            # up/down illustration
            px = [(500, 780), (640, 640), (780, 780), (920, 640)]
            text(c, "up / down", 330, 700, 26, IB, "serifi", "c", ua)
            for k in range(3):
                col_ = GOOD if k < 2 else BAD
                arrow(c, px[k], px[k + 1], col_, 3, ua, 1.0)
            text(c, "×", 920, 640, 46, BAD, "sansb", "c", ua)
            text(c, "down, then up: forbidden", 1180, 700, 24, BAD, "serifi", "c", ua)
        # ---- beat 3: collisions in a small fabric
        if B(3) - 0.3 < t < B(4) + 8:
            a = P(t, B(3), B(3) + 1.0) * (1 - self.Pb(t, 4, 6.0, 8.0))
            self.fabric(c, a)
            # draw each flow with its chosen spine; reveal progressively
            for i, (s, d, sp) in enumerate(self.flows):
                ts = B(3) + 2.0 + i * 0.35
                u = P(t, ts, ts + 0.8, lin)
                if u <= 0: continue
                p0 = self.pos("host", s); l0 = self.pos("leaf", s // self.H); sp_ = self.pos("spine", sp)
                l1 = self.pos("leaf", d // self.H); p1 = self.pos("host", d)
                bad = self.up[(s // self.H, sp)] > 1 or self.down[(sp, d // self.H)] > 1
                colr = BAD if bad else GOOD
                off = (i % 5 - 2) * 3
                poly(c, [(p0[0] + off, p0[1]), (l0[0] + off, l0[1]), (sp_[0] + off, sp_[1]), (l1[0] + off, l1[1]), (p1[0] + off, p1[1])], colr, 2.2, a * 0.85, u)
            used_up = set(self.up.keys())
            text(c, "random permutation, each flow hashed to one spine", 960, 880, 26, DIM, "serifi", "c", a)
            idle = sum(1 for l in range(self.L) for s in range(self.U) if (l, s) not in used_up)
            text(c, f"red: two flows share a link.   idle uplinks: {idle} of {self.L * self.U}", 960, 930, 26, BAD, "serifi", "c", a * P(t, B(3) + 9, B(3) + 10))
        # ---- beat 4-5: model bars
        if B(4) - 0.2 < t:
            a = P(t, B(4) + 5.0, B(4) + 6.5)
            text(c, "delivered throughput, % of ideal  (16×16 leaf-spine, 1:1, random permutation)", 960, 230, 28, INK, "serif", "c", a)
            tag(c, "MY TOY MODEL", 780, 270, HI, a)
            bars = [("flow hash\n(ECMP)", 55.6, ETH), ("destination-based\ntable", 69.2, IB), ("per-packet\nspraying", 100.0, GOOD)]
            bx, by, bh = 420, 830, 450
            axis_range_frame(c, bx - 20, by - bh, bx + 1060, by, a)
            for i, (nm, v, colr) in enumerate(bars):
                ts = B(4) + 7 + i * (3.0 if i < 2 else 0)
                if i == 2: ts = B(5) - 14
                h = bh * (v / 100) * P(t, ts, ts + 1.3)
                x = bx + 60 + i * 340
                rect(c, x, by - h, 190, h, fill=colr, a=a)
                text(c, f"{v:.0f} %" if i < 2 else "100 %", x + 95, by - h - 14 - (22 if (i == 0 and t > B(5)) else 0), 32, colr, "serif", "c", a * P(t, ts + 1, ts + 1.8))
                for j, ln in enumerate(nm.split("\n")):
                    text(c, ln, x + 95, by + 34 + j * 26, 22, DIM, "sans", "c", a)
            note = a * P(t, B(4) + 9, B(4) + 10)
            text(c, "shift pattern, destination-based: 100 %", 1430, 400, 22, IB, "serifi", "c", note) if False else None
            margin_note(c, "On the shift pattern the table was tuned for, destination-based routing delivers 100 %. Per-packet spraying is an idealized bound; real hardware gets less.", 1520, 420, 330, 20, DIM, note)
            if t > B(5):
                ma = P(t, B(5), B(5) + 1.2)
                y60 = by - bh * 0.60
                line(c, bx - 20, y60, bx + 1060, y60, HI, 1.6, ma, dash=(8, 6))
                text(c, "Microsoft, ~60 %", bx + 1060, y60 - 10, 22, HI, "serifi", "r", ma)
                
                text(c, "a hint, not a proof — mine is a toy model", 960, 960, 28, DIM, "serifi", "c", P(t, B(5) + 3.5, B(5) + 4.5))


# ---------------------------------------------------------------------------------------------- congestion
class Congestion(Scene):
    id = "congestion"
    title = "Lossless is not congestion-free"
    sources = ("DCQCN: Zhu et al., SIGCOMM 2015.  Slingshot: De Sensi et al., SC20 (worst-case victim slowdown 1.3x vs 93x on Cray Aries; authors’ measurements).")

    def draw(self, c, t):
        B = self.B
        # ---- beat 0: incast + backpressure spreading
        if t < B(1) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.5))
            rx, ry = 1480, 520
            host_icon(c, rx - 30, ry - 20, 70, 44, INK, a, "one receiver")
            leaf = (1180, 520); sp = [(820, 330), (820, 520), (820, 710)]
            switch_icon(c, leaf[0] - 50, leaf[1] - 14, 100, 28, IB, a, 4)
            line(c, leaf[0] + 50, leaf[1], rx - 30, ry, FAINT, 2, a)
            for i, p in enumerate(sp):
                switch_icon(c, p[0] - 50, p[1] - 14, 100, 28, IB, a, 4)
                line(c, p[0] + 50, p[1], leaf[0] - 50, leaf[1], FAINT, 1.5, a)
                for k in range(3):
                    hy = p[1] - 70 + k * 70
                    hx = 360
                    line(c, hx + 8, hy, p[0] - 50, p[1], FAINT, 1, a * 0.8)
                    circle(c, hx, hy, 7, fill=DIM, a=a)
                    for j in range(2):
                        u = (t * 0.4 + (i * 3 + k) * 0.11 + j * 0.5) % 1.0
                        q = lerp2((hx, hy), (p[0] - 50, p[1]), u)
                        circle(c, q[0], q[1], 3, fill=ETH, a=a * 0.9)
            # queues: build at the leaf first, then spreads upstream
            lvl = [clamp((t - B(0) - 1.5) / 2.0), clamp((t - B(0) - 3.5) / 3.5), 0]
            def qbar(x, y, v, w=90):
                rect(c, x, y, w, 12, stroke=FAINT, sw=1, a=a)
                rect(c, x, y, w * v, 12, fill=BAD if v > 0.6 else ETH, a=a)
            qbar(leaf[0] - 45, leaf[1] + 22, lvl[0])
            for p in sp: qbar(p[0] - 45, p[1] + 22, lvl[1])
            text(c, "queues build — and backpressure spreads backward, like a traffic jam", 960, 900, 28, BAD, "serifi", "c", a * P(t, B(0) + 5.5, B(0) + 7))
        # ---- beat 1: control loop + DCQCN sawtooth
        if B(1) - 0.2 < t < B(2) + 0.5:
            a = P(t, B(1), B(1) + 1.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            text(c, "senders must be told to slow down", 960, 215, 36, INK, "serif", "c", a)
            # loop diagram
            ys = 360
            chip(c, 150, ys, 150, 70, "sender", INK, a, 22)
            switch_icon(c, 700, ys + 20, 140, 36, IB, a, 6, "switch")
            chip(c, 1240, ys, 190, 70, "receiving adapter", INK, a, 20)
            line(c, 300, ys + 35, 700, ys + 38, FAINT, 2, a); line(c, 840, ys + 38, 1240, ys + 35, FAINT, 2, a)
            ph = (t - B(1)) * 0.28
            for k in range(3):
                u = (ph + k / 3) % 1.0
                pkt(c, lerp(300, 1240, u), ys + 36, ETH if u < 0.4 else HI, 20, 12, a)
            e = P(t, B(1) + 5, B(1) + 6)
            text(c, "ECN mark", 770, ys + 100, 22, HI, "sansm", "c", a * e)
            if e > 0:
                arrow(c, (1240, ys + 110), (300, ys + 110), HI, 2, a * e * 0.8, P(t, B(1) + 6.5, B(1) + 9), dash=(6, 5))
                text(c, "notify the sender", 770, ys + 138, 22, HI, "serifi", "c", a * P(t, B(1) + 7, B(1) + 8))
            # rate sawtooth
            gx, gy, gw, gh = 380, 860, 1160, 250
            axis_range_frame(c, gx, gy - gh, gx + gw, gy, a)
            text(c, "sender rate", gx - 14, gy - gh + 12, 20, DIM, "serifi", "r", a)
            text(c, "time", gx + gw, gy + 30, 20, DIM, "serifi", "r", a)
            u = P(t, B(1) + 12, B(2) - 3, lin)
            pts, r, cut_at = [], 1.0, [0.12, 0.38, 0.64]
            n = 140
            for k in range(n + 1):
                x = k / n
                r_ = 1.0
                for ct in cut_at:
                    if x >= ct: r_ = 0.5 + 0.5 * (0.0) if False else r_
                # piecewise: cut by half, then climb back in steps
                val = 1.0
                last = -1
                for ct in cut_at:
                    if x >= ct: last = ct
                if last >= 0:
                    dtn = x - last
                    base = 0.5
                    val = min(1.0, base + 0.5 * min(1.0, math.floor(dtn / 0.05) / 8.0))
                    if last == cut_at[0] and False: val = val
                pts.append((gx + x * gw, gy - 20 - val * (gh - 50)))
            poly(c, pts, ETH, 3, a, u)
            text(c, "DCQCN: each notification cuts the rate by up to half; it climbs back in steps", 960, 1000, 22, DIM, "serifi", "c", a * P(t, B(1) + 16, B(1) + 17))
            text(c, "pause frames remain the backstop", 960, 1030, 22, ETH, "serifi", "c", a * P(t, B(1) + 22, B(1) + 23))
        # ---- beat 2: Slingshot
        if B(2) - 0.2 < t:
            a = P(t, B(2), B(2) + 1.0)
            text(c, "Slingshot: track every in-flight packet between every pair of endpoints", 960, 230, 32, SLING, "serif", "c", a)
            text(c, "stiff backpressure only on the sources causing the jam", 960, 278, 26, DIM, "serifi", "c", a * P(t, B(2) + 4, B(2) + 5))
            bx, by = 420, 800
            text(c, "worst-case slowdown of an innocent (“victim”) flow", 960, 380, 26, INK, "serif", "c", a * P(t, B(2) + 7, B(2) + 8))
            for i, (nm, v, colr) in enumerate([("Cray Aries\n(previous network)", 93, BAD), ("Slingshot", 1.3, SLING)]):
                ts = B(2) + 9 + i * 3
                w = 1000 * (v / 93.0) * P(t, ts, ts + 1.5)
                yy = 440 + i * 130
                rect(c, bx + 200, yy, max(w, 0.1), 70, fill=colr, a=a)
                for j, ln in enumerate(nm.split("\n")):
                    text(c, ln, bx + 180, yy + 30 + j * 26, 24 if j == 0 else 18, colr if j == 0 else DIM, "serif" if j == 0 else "sans", "r", a)
                text(c, f"{v:g}×", bx + 200 + w + 16, yy + 50, 34, colr, "serif", "l", a * P(t, ts + 1, ts + 2))
            tag(c, "AUTHORS' MEASUREMENTS", 1380, 810, HI, a * P(t, B(2) + 14, B(2) + 15))


# ---------------------------------------------------------------------------------------------- sharp
class Sharp(Scene):
    id = "sharp"
    title = "In-network computing: SHARP"
    sources = ("Graham et al., SHARP (original paper): 128 hosts, pre-release hardware, tuned for low noise - best case.  Nvidia “up to 9x” for SHARPv4: vendor claim, NOT independently verified.")

    HOSTS = 8

    def tree_pos(self):
        hp = [(250 + i * 200, 780) for i in range(8)]
        lp = [(350 + i * 400, 560) for i in range(4)]
        sp = [(550, 360), (1350, 360)]
        rp = (950, 230)
        return hp, lp, sp, rp

    def draw(self, c, t):
        B = self.B
        hp, lp, sp, rp = self.tree_pos()
        vals = [3, 1, 4, 1, 5, 9, 2, 6]
        # ---- beat 0: the problem
        if t < B(1) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.5))
            for i, p in enumerate(hp):
                circle(c, p[0], p[1], 26, stroke=INK, sw=1.6, fill=BG2, a=a)
                text(c, str(vals[i]), p[0], p[1] + 9, 28, HI, "serif", "c", a * P(t, B(0) + 6 + i * 0.4, B(0) + 7 + i * 0.4))
            text(c, "an all-reduce:  every host ends up with the sum", 960, 380, 40, INK, "serif", "c", a)
            text(c, "the heartbeat of distributed training, and of many simulations", 960, 440, 26, DIM, "serifi", "c", a * P(t, B(0) + 3, B(0) + 4.5))
            text(c, "128 hosts in the paper's measurement", 960, 960, 22, DIM, "serifi", "c", a * P(t, B(0) + 9, B(0) + 10))
        # ---- beat 1: host-based vs in-network
        if B(1) - 0.3 < t < B(2) + 0.5:
            a = P(t, B(1), B(1) + 1.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            def fabric(a_):
                for l in range(4):
                    for k in range(2):
                        line(c, lp[l][0], lp[l][1], hp[2 * l + k][0], hp[2 * l + k][1], FAINT, 1.2, a_)
                    s = sp[l // 2]; line(c, lp[l][0], lp[l][1], s[0], s[1], FAINT, 1.2, a_)
                for s in sp: line(c, s[0], s[1], rp[0], rp[1], FAINT, 1.2, a_)
                for p in lp: switch_icon(c, p[0] - 40, p[1] - 13, 80, 26, IB, a_, 4)
                for p in sp: switch_icon(c, p[0] - 40, p[1] - 13, 80, 26, IB, a_, 4)
                switch_icon(c, rp[0] - 40, rp[1] - 13, 80, 26, IB, a_, 4)
            fabric(a * 0.8)
            mode = t < B(1) + 6.4
            if mode:
                text(c, "host-based: exchange partial results in rounds", 960, 160, 32, ETH, "serif", "c", a)
                rnd = int(clamp((t - B(1) - 1.0) / 1.7, 0, 2.99))
                partner = [1, 2, 4][rnd]
                ph = ((t - B(1) - 1.0) / 1.7) % 1.0
                for i in range(8):
                    j = i ^ partner
                    if i < j:
                        p, q = hp[i], hp[j]
                        pa = a * clamp(ph * 3)
                        curve(c, (p[0], p[1] - 30), (p[0], 500 - 40 * partner), (q[0], 500 - 40 * partner), (q[0], q[1] - 30), ETH, 2, pa * (1 - clamp((ph - .8) * 5)))
                for i, p in enumerate(hp): circle(c, p[0], p[1], 26, stroke=INK, sw=1.6, fill=BG2, a=a)
                text(c, f"round {rnd + 1} of 3", 960, 930, 26, ETH, "serifi", "c", a)
                text(c, "data crosses the network again and again", 960, 970, 24, DIM, "serifi", "c", a * P(t, B(1) + 3.5, B(1) + 4.5))
            else:
                text(c, "SHARP: the switches do the arithmetic", 960, 160, 32, IB, "serif", "c", a * P(t, B(1) + 6.4, B(1) + 7.2))
                u = P(t, B(1) + 7.2, B(1) + 12.6, lin)
                for i, p in enumerate(hp):
                    circle(c, p[0], p[1], 26, stroke=INK, sw=1.6, fill=BG2, a=a)
                    text(c, str(vals[i]), p[0], p[1] + 9, 28, HI, "serif", "c", a)
                # up phase 0..0.5 ; down phase 0.5..1
                up = clamp(u * 2.0); dn = clamp(u * 2.0 - 1.0)
                lsum = [vals[2 * l] + vals[2 * l + 1] for l in range(4)]
                ssum = [lsum[0] + lsum[1], lsum[2] + lsum[3]]
                tot = sum(vals)
                # packets up
                if up > 0:
                    for l in range(4):
                        for k in range(2):
                            p = hp[2 * l + k]; q = lp[l]
                            uu = clamp(up * 3.0)
                            if uu < 1: dot(c, *lerp2(p, q, uu), 6, HI, a)
                    if up > 0.33:
                        for l in range(4):
                            text(c, str(lsum[l]), lp[l][0], lp[l][1] - 22, 26, HI, "serifb", "c", a * clamp((up - .33) * 6))
                    if up > 0.4 and up < 0.7:
                        for l in range(4):
                            uu = clamp((up - 0.4) * 3.4); dot(c, *lerp2(lp[l], sp[l // 2], uu), 6, HI, a)
                    if up > 0.66:
                        for s in range(2):
                            text(c, str(ssum[s]), sp[s][0], sp[s][1] - 22, 26, HI, "serifb", "c", a * clamp((up - .66) * 6))
                    if up > 0.7 and up < 1.0:
                        for s in range(2):
                            uu = clamp((up - 0.7) * 3.4); dot(c, *lerp2(sp[s], rp, uu), 6, HI, a)
                    if up >= 1.0:
                        text(c, str(tot), rp[0], rp[1] - 24, 32, GOOD, "serifb", "c", a)
                if dn > 0:
                    for s in range(2):
                        dot(c, *lerp2(rp, sp[s], clamp(dn * 3)), 6, GOOD, a)
                    for l in range(4):
                        if dn > 0.3: dot(c, *lerp2(sp[l // 2], lp[l], clamp((dn - .3) * 3)), 6, GOOD, a)
                    for h in range(8):
                        if dn > 0.6:
                            uu = clamp((dn - .6) * 3); dot(c, *lerp2(lp[h // 2], hp[h], uu), 6, GOOD, a)
                            if uu >= 1: text(c, str(tot), hp[h][0], hp[h][1] + 56, 22, GOOD, "serifb", "c", a)
                if u == 0: pass
        # ---- beat 2: numbers
        if B(2) - 0.2 < t < B(3) + 0.5:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.5))
            text(c, "all-reduce latency, 128 hosts (original SHARP paper)", 960, 230, 30, INK, "serif", "c", a)
            gx, gy = 470, 820
            axis_range_frame(c, gx, 300, gx + 1000, gy, a)
            groups = [("8 B", 6.0, 3.0, "6 → under 3"), ("4 KiB", 47.0, 14.5, "47 → 14.5")]
            sc_ = 9.0
            for gi, (nm, h0, h1, lab) in enumerate(groups):
                x = gx + 120 + gi * 480
                ts = B(2) + 3 + gi * 6
                for bi, (v, colr) in enumerate([(h0, ETH), (h1, IB)]):
                    hh = v * sc_ * P(t, ts + bi * 1.6, ts + bi * 1.6 + 1.3)
                    rect(c, x + bi * 130, gy - hh, 110, hh, fill=colr, a=a)
                    text(c, ("<3" if (gi == 0 and bi == 1) else f"{v:g}"), x + bi * 130 + 55, gy - hh - 12, 28, colr, "serif", "c", a * P(t, ts + bi * 1.6 + 1, ts + bi * 1.6 + 1.8))
                text(c, nm, x + 120, gy + 36, 26, INK, "serif", "c", a)
            text(c, "microseconds", gx - 20, 330, 20, DIM, "serifi", "r", a)
            rich(c, [("host-based", ETH), ("  vs  ", DIM), ("SHARP", IB)], 1230, 320, 24, "serif", a * P(t, B(2) + 2, B(2) + 3), "c")
        # ---- beat 3: caveats
        if B(3) - 0.2 < t:
            a = P(t, B(3), B(3) + 1.0)
            tag(c, "AUTHORS' NUMBERS", 640, 400, HI, a * P(t, B(3) + 1, B(3) + 2), 20)
            text(c, "pre-release hardware, tuned for low noise: a best case", 960, 470, 34, INK, "serif", "c", a * P(t, B(3) + 1.5, B(3) + 2.5))
            tag(c, "VENDOR CLAIM · NOT VERIFIED", 640, 640, BAD, a * P(t, B(3) + 7, B(3) + 8), 20)
            text(c, "Nvidia: fourth generation, “up to 9×”", 960, 710, 34, INK, "serif", "c", a * P(t, B(3) + 7.5, B(3) + 8.5))
