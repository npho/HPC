"""Scenes 10-11: fattree, dragonfly"""
import math
from engine import *


# ---------------------------------------------------------------------------------------------- fattree
class FatTree(Scene):
    id = "fattree"
    title = "Topology I: the fat tree"
    sources = ("Sizing formulas: 2-level k²/2 hosts, k+k/2 switches; 3-level k³/4 hosts, 5k²/4 switches (Al-Fares et al., SIGCOMM 2008), 1:1.  Computed in src/model_numbers.py.  "
               "Quantum-X800 Q3400 datasheet (144 ports -> 10,368 NICs).  DGX SuperPOD H100 reference architecture (NVIDIA docs).")

    def small_tree(self, c, a, t, x0=300, x1=1100, y_sp=330, y_lf=520, y_h=700, k=4, hl=None):
        nl, ns = k, k // 2
        lx = lambda i: x0 + (i + 0.5) * (x1 - x0) / nl
        sx = lambda j: x0 + (j + 0.5) * (x1 - x0) / ns
        for i in range(nl):
            for j in range(ns):
                line(c, lx(i), y_lf, sx(j), y_sp, IB, 1.4, a * 0.7)
            for h in range(k // 2):
                hx = lx(i) + (h - 0.5) * 70
                line(c, lx(i), y_lf, hx, y_h, FAINT, 1.2, a)
                circle(c, hx, y_h, 8, fill=BG, stroke=INK, sw=1.2, a=a)
        for j in range(ns):
            switch_icon(c, sx(j) - 50, y_sp - 14, 100, 28, IB, a, 4)
        for i in range(nl):
            switch_icon(c, lx(i) - 50, y_lf - 14, 100, 28, IB, a, 4)
        return lx, sx

    def draw(self, c, t):
        B = self.B
        # ---- beat 0 : k-port switch split, 2 level tree
        if t < B(1) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.5))
            lx, sx = self.small_tree(c, a, t)
            # annotate leaf: half down, half up
            e = P(t, B(0) + 5, B(0) + 6.5)
            text(c, "k = 4 ports per switch", 1380, 360, 30, INK, "serif", "l", a)
            text(c, "half of each leaf's ports go down to hosts", 1380, 420, 24, GOOD, "serifi", "l", a * e)
            text(c, "half go up to spines", 1380, 460, 24, IB, "serifi", "l", a * e)
            # moving packet between any host pair
            u = ((t - B(0)) * 0.22) % 1.0
            path = [(lx(0) - 35, 700), (lx(0), 520), (sx(1), 330), (lx(3), 520), (lx(3) + 35, 700)]
            pp = along(path, u); pkt(c, pp[0], pp[1], HI, 22, 12, a)
            text(c, "any host to any other host, at full speed", 960, 880, 28, DIM, "serifi", "c", a * P(t, B(0) + 9, B(0) + 10.5))
        # ---- beat 1 : 2-level formulas
        if B(1) - 0.3 < t < B(2) + 0.5:
            a = P(t, B(1), B(1) + 1.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            self.small_tree(c, a * 0.35, t, 260, 760)
            text(c, "two levels", 1120, 300, 40, IB, "serif", "l", a)
            text(c, "hosts  =  k² / 2", 1120, 380, 36, INK, "mono", "l", a * P(t, B(1) + 1.5, B(1) + 2.5))
            e = P(t, B(1) + 4.0, B(1) + 6.0)
            n = int(2048 * e)
            text(c, "k = 64:", 1120, 470, 28, DIM, "serifi", "l", a * P(t, B(1) + 4, B(1) + 5))
            text(c, f"{n:,} hosts", 1120, 540, 64, HI, "serif", "l", a * P(t, B(1) + 4, B(1) + 5))
            text(c, f"{int(96 * e)} switches  (64 leaf + 32 spine)", 1120, 600, 28, DIM, "serifi", "l", a * P(t, B(1) + 5, B(1) + 6))
            text(c, "a 64-port NDR switch", 1120, 650, 24, FAINT, "serifi", "l", a * P(t, B(1) + 5, B(1) + 6))
        # ---- beat 2 : 3 levels, log chart
        if B(2) - 0.3 < t < B(3) + 0.5:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.5))
            text(c, "a third level", 960, 230, 38, IB, "serif", "c", a)
            text(c, "hosts  =  k³ / 4", 960, 290, 32, INK, "mono", "c", a * P(t, B(2) + 1, B(2) + 2))
            rows = [("two levels", "2,048", "96 switches", "3 switch hops", IB), ("three levels", "65,536", "5,120 switches", "5 switch hops", ETH)]
            for i, (nm, h, sw, hp, colr) in enumerate(rows):
                ts = B(2) + 3 + i * 4
                aa = a * P(t, ts, ts + 1.0)
                x = 240 + i * 760
                rect(c, x, 400, 680, 340, fill=BG2, stroke=colr, sw=1.4, r=8, a=aa)
                text(c, nm, x + 340, 460, 34, colr, "serif", "c", aa)
                text(c, h, x + 340, 570, 80, INK, "serif", "c", aa)
                text(c, "hosts  (k = 64)", x + 340, 610, 24, DIM, "serifi", "c", aa)
                text(c, sw, x + 340, 670, 28, colr, "sansm", "c", aa * P(t, ts + 1, ts + 2))
                text(c, hp + " per message", x + 340, 710, 22, DIM, "sans", "c", aa * P(t, ts + 2, ts + 3))
            text(c, "32× the hosts, but 53× the switches, and two more hops", 960, 820, 28, DIM, "serifi", "c", a * P(t, B(2) + 8, B(2) + 9.5))
        # ---- beat 3 : check against datasheet
        if B(3) - 0.3 < t < B(4) + 0.5:
            a = P(t, B(3), B(3) + 1.0) * (1 - self.Pb(t, 4, 0.0, 0.5))
            text(c, "does the formula survive contact with a datasheet?", 960, 270, 36, INK, "serifi", "c", a)
            rich(c, [("144", IB, "mono"), ("² / 2", INK, "mono"), ("  =  ", DIM, "mono"), ("10,368", HI, "mono")], 960, 420, 64, "mono", a * P(t, B(3) + 3, B(3) + 4), "c")
            text(c, "two-level XDR, 144-port switch", 960, 480, 26, DIM, "serifi", "c", a * P(t, B(3) + 3, B(3) + 4))
            text(c, "NVIDIA datasheet: 10,368 adapters", 960, 600, 36, GOOD, "serif", "c", a * P(t, B(3) + 8, B(3) + 9))
            text(c, "✓ agrees", 960, 680, 40, GOOD, "sansb", "c", a * P(t, B(3) + 10, B(3) + 11))
        # ---- beat 4,5 : rails
        if B(4) - 0.3 < t:
            a = P(t, B(4), B(4) + 1.0)
            text(c, "rail-optimized: one rail per adapter", 960, 200, 34, INK, "serif", "c", a)
            nodes = 4
            nx0, ny = 250, 780
            leaf_x = [320 + r * 160 for r in range(8)]
            leaf_y = 380
            show_spines = t > B(5)
            for r in range(8):
                switch_icon(c, leaf_x[r] - 50, leaf_y - 14, 100, 28, IB, a, 4, None)
                text(c, f"leaf {r}", leaf_x[r], leaf_y - 26, 17, DIM, "sans", "c", a)
            hl = int(((t - B(4)) // 3) % 8) if t < B(5) else -1
            for n in range(nodes):
                nxp = 340 + n * 360
                rect(c, nxp - 150, ny - 40, 330, 80, fill=BG2, stroke=FAINT, sw=1.2, r=6, a=a)
                text(c, f"node {n}" if n < 3 else "node 31", nxp, ny + 70, 20, DIM, "sans", "c", a)
                for r in range(8):
                    px = nxp - 130 + r * 37
                    circle(c, px, ny - 20, 8, fill=BG, stroke=IB, sw=1.4, a=a)
                    colr = HI if r == hl else IB
                    line(c, px, ny - 28, leaf_x[r], leaf_y + 14, colr, 2.2 if r == hl else 1.0, a * (1.0 if r == hl else 0.55))
            text(c, "…", 1450, ny + 4, 40, DIM, "serif", "c", a)
            text(c, "one hop between same-numbered adapters", 960, 930, 28, HI, "serifi", "c", a * P(t, B(4) + 8, B(4) + 9) * (1 if t < B(5) else 0))
            if t > B(5) - 0.4:
                a5 = P(t, B(5), B(5) + 1.0)
                rect(c, 0, 960, LW, 120, fill=BG, fa=a5)
                text(c, "one scalable unit: up to 32 nodes  ·  8 leaf switches  ·  4 spines", 960, 960, 30, INK, "serif", "c", a5)
                text(c, "storage and management live on their own networks", 960, 1003, 24, DIM, "serifi", "c", a5 * P(t, B(5) + 3, B(5) + 4))
                for k in range(4):
                    px = 520 + k * 240
                    switch_icon(c, px - 50, 235, 100, 28, ETH, a5, 4)
                    for r in range(8):
                        line(c, leaf_x[r], leaf_y - 14, px, 263, ETH, 0.8, a5 * 0.25)
                text(c, "spines", 380, 255, 20, ETH, "serifi", "c", a5)


# ---------------------------------------------------------------------------------------------- dragonfly
class Dragonfly(Scene):
    id = "dragonfly"
    title = "Topology II: the dragonfly"
    sources = ("Kim, Dally, Scott, Abts, “Technology-Driven, Highly-Scalable Dragonfly Topology”, ISCA 2008.  Slingshot: De Sensi et al., SC20.  "
               "Frontier: 74 groups, up to 128 nodes/group; 4 global links per group pair (OLCF).  N and port counts computed in src/model_numbers.py")

    def group_pos(self, g, n, cx=960, cy=560, r=300):
        ang = -math.pi / 2 + 2 * math.pi * g / n
        return (cx + r * math.cos(ang), cy + r * math.sin(ang))

    def groups_graph(self, c, n, a, cx=960, cy=560, r=300, gr=34, linkcol=FAINT, lw=1.2, hl=None, colr=IB):
        for i in range(n):
            for j in range(i + 1, n):
                p, q = self.group_pos(i, n, cx, cy, r), self.group_pos(j, n, cx, cy, r)
                on = hl and (i, j) in hl
                line(c, p[0], p[1], q[0], q[1], hl[(i, j)] if on else linkcol, 2.6 if on else lw, a * (1.0 if on else 0.8))
        for i in range(n):
            p = self.group_pos(i, n, cx, cy, r)
            circle(c, p[0], p[1], gr, fill=BG2, stroke=colr, sw=1.8, a=a)

    def draw(self, c, t):
        B = self.B
        # ---- beat 0: why
        if t < B(1) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.5))
            text(c, "fat trees get expensive at scale", 960, 440, 54, INK, "serif", "c", a)
            text(c, "mostly in long optical cables", 960, 520, 40, DIM, "serifi", "c", a * P(t, B(0) + 4, B(0) + 5.5))
            text(c, "the dragonfly makes a different trade", 960, 640, 36, IB, "serif", "c", a * P(t, B(0) + 8, B(0) + 9.5))
        # ---- beat 1: group = all-to-all, short copper; global links
        if B(1) - 0.3 < t < B(2) + 0.5:
            a = P(t, B(1), B(1) + 1.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            # one group zoomed: 4 switches fully connected
            gx, gy = 560, 560
            pts = [(gx + 150 * math.cos(math.pi / 4 + k * math.pi / 2), gy + 150 * math.sin(math.pi / 4 + k * math.pi / 2)) for k in range(4)]
            circle(c, gx, gy, 230, stroke=FAINT, sw=1.2, a=a)
            for i in range(4):
                for j in range(i + 1, 4):
                    line(c, pts[i][0], pts[i][1], pts[j][0], pts[j][1], GOOD, 2.2, a * P(t, B(1) + 2, B(1) + 4))
            for p in pts: switch_icon(c, p[0] - 40, p[1] - 13, 80, 26, IB, a, 4)
            text(c, "short copper, every switch to every other", gx, gy + 280, 24, GOOD, "serifi", "c", a * P(t, B(1) + 3, B(1) + 4))
            # global links
            ga = P(t, B(1) + 5.5, B(1) + 7)
            for k in range(4):
                ang = math.pi / 4 + k * math.pi / 2
                q = (gx + 150 * math.cos(ang), gy + 150 * math.sin(ang))
                e = (gx + 330 * math.cos(ang + 0.0), gy + 330 * math.sin(ang + 0.0))
                line(c, q[0] + 30 * math.cos(ang), q[1] + 30 * math.sin(ang), e[0], e[1], ETH, 2.4, a * ga)
            text(c, "a few long links to other groups", 1280, 440, 26, ETH, "serifi", "l", a * ga)
            # group as virtual router
            if t > B(1) + 7.8:
                va = a * P(t, B(1) + 7.8, B(1) + 9)
                circle(c, 1480, 640, 90, fill=BG2, stroke=IB, sw=2.5, a=va)
                text(c, "one giant", 1480, 630, 26, INK, "serif", "c", va); text(c, "virtual router", 1480, 662, 26, INK, "serif", "c", va)
                arrow(c, (1000, 560), (1380, 620), DIM, 2, va * 0.7, 1.0)
        # ---- beat 2 : p, a, h; N formula; 9 group example
        if B(2) - 0.3 < t < B(3) + 0.5:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.5))
            self.groups_graph(c, 9, a * P(t, B(2) + 9, B(2) + 11), cx=480, cy=600, r=260, gr=30)
            lines = [("p", "terminals per switch", HI), ("a", "switches per group", GOOD), ("h", "global links per switch", ETH)]
            for i, (sym, d, colr) in enumerate(lines):
                aa = a * P(t, B(2) + 1.5 + i * 2.0, B(2) + 2.5 + i * 2.0)
                text(c, sym, 960, 290 + i * 62, 48, colr, "mathi", "l", aa)
                text(c, d, 1020, 290 + i * 62, 28, DIM, "serifi", "l", aa)
            rich(c, [("N", INK, "mathi"), (" = ", DIM, "mathi"), ("a", GOOD, "mathi"), ("·", DIM, "mathi"), ("p", HI, "mathi"), ("·(", DIM, "mathi"), ("a", GOOD, "mathi"), ("·", DIM, "mathi"), ("h", ETH, "mathi"), (" + 1)", DIM, "mathi")],
                 960, 580, 54, "mathi", a * P(t, B(2) + 7.5, B(2) + 8.5), "l")
            text(c, "balanced:  a = 2p = 2h", 960, 660, 32, INK, "serif", "l", a * P(t, B(2) + 10, B(2) + 11))
            text(c, "p = h = 2, a = 4  →  9 groups, 72 terminals", 960, 740, 26, DIM, "mono", "l", a * P(t, B(2) + 11, B(2) + 12)) if False else None
            text(c, "example: p = h = 2, a = 4", 960, 740, 26, DIM, "serifi", "l", a * P(t, B(2) + 11, B(2) + 12))
            text(c, "9 groups, 72 terminals", 960, 780, 26, DIM, "serifi", "l", a * P(t, B(2) + 12, B(2) + 13))
        # ---- beat 3 : Frontier
        if B(3) - 0.3 < t < B(4) + 0.5:
            a = P(t, B(3), B(3) + 1.0) * (1 - self.Pb(t, 4, 0.0, 0.5))
            text(c, "Frontier (OLCF)", 960, 230, 40, SLING, "serif", "c", a)
            vals = [("p", "16", "host links per switch", HI), ("a", "32", "switches per group  (31 local links)", GOOD), ("h", "16", "global links per switch (max)", ETH)]
            for i, (sym, v, d, colr) in enumerate(vals):
                aa = a * P(t, B(3) + 1.5 + i * 2.2, B(3) + 2.5 + i * 2.2)
                x = 260 + i * 470
                text(c, f"{sym} = {v}", x, 400, 66, colr, "mathi", "l", aa)
                text(c, d, x, 450, 22, DIM, "serifi", "l", aa)
            ga = a * P(t, B(3) + 8.5, B(3) + 9.5)
            self.groups_graph(c, 12, ga, cx=700, cy=720, r=170, gr=18, lw=0.8)
            text(c, "74 groups", 1180, 650, 52, SLING, "serif", "l", ga)
            text(c, "4 links between each pair", 1180, 700, 30, INK, "serifi", "l", ga * P(t, B(3) + 11, B(3) + 12))
            text(c, "(drawn: 12 of 74 groups)", 1180, 740, 20, FAINT, "serifi", "l", ga)
        # ---- beat 4 : routing: minimal vs Valiant
        if B(4) - 0.3 < t < B(5) + 0.5:
            a = P(t, B(4), B(4) + 1.0) * (1 - self.Pb(t, 5, 0.0, 0.5))
            n = 8
            hlm = {(0, 1): BAD}
            tmin = P(t, B(4) + 12, B(4) + 13)
            hl = dict(hlm)
            if t > B(4) + 9:
                for gm in (2, 3, 4, 5, 6, 7):
                    key = (0, gm) if gm > 0 else (gm, 0)
                    hl[(0, gm)] = GOOD
                    hl[(min(gm, 1), max(gm, 1))] = GOOD
            self.groups_graph(c, n, a, cx=700, cy=560, r=300, gr=34, hl=hl if t > B(4) + 5 else None)
            for g in range(n):
                p = self.group_pos(g, n, 700, 560, 300); text(c, "ABCDEFGH"[g], p[0], p[1] + 9, 26, INK, "serif", "c", a)
            text(c, "any path: at most 3 switch hops", 1180, 340, 30, INK, "serif", "l", a * P(t, B(4) + 0.5, B(4) + 1.5))
            text(c, "local  ·  global  ·  local", 1180, 380, 26, DIM, "mono", "l", a * P(t, B(4) + 1.5, B(4) + 2.5))
            text(c, "worst case: everything from A to B", 1180, 480, 30, BAD, "serif", "l", a * P(t, B(4) + 5, B(4) + 6))
            text(c, "squeezes through a single global link", 1180, 520, 26, BAD, "serifi", "l", a * P(t, B(4) + 6, B(4) + 7))
            if t > B(4) + 9:
                text(c, "so: detour via a random middle group,", 1180, 640, 28, GOOD, "serif", "l", a * P(t, B(4) + 9, B(4) + 10))
                text(c, "or choose per packet by watching queues", 1180, 680, 28, GOOD, "serif", "l", a * P(t, B(4) + 11, B(4) + 12))
                text(c, "dragonflies live and die by adaptive routing", 1180, 760, 24, DIM, "serifi", "l", a * P(t, B(4) + 13.5, B(4) + 14.5))
        # ---- beat 5 : dragonfly+
        if B(5) - 0.3 < t:
            a = P(t, B(5), B(5) + 1.0)
            text(c, "dragonfly+", 960, 240, 46, IB, "serif", "c", a)
            text(c, "each group is itself a small fat tree", 960, 290, 28, DIM, "serifi", "c", a * P(t, B(5) + 1.5, B(5) + 2.5))
            for g in range(4):
                gx = 360 + g * 400
                circle(c, gx, 560, 150, stroke=FAINT, sw=1.2, a=a)
                for s in range(2):
                    sxp = gx - 50 + s * 100
                    for l in range(3):
                        lxp = gx - 100 + l * 100
                        line(c, sxp, 500, lxp, 620, IB, 1.2, a * 0.8)
                    switch_icon(c, sxp - 30, 487, 60, 22, IB, a, 3)
                for l in range(3):
                    lxp = gx - 100 + l * 100
                    switch_icon(c, lxp - 30, 620, 60, 22, IB, a, 3)
                    line(c, lxp, 642, lxp, 690, FAINT, 1, a)
                    circle(c, lxp, 696, 6, fill=BG, stroke=INK, sw=1, a=a)
            for g in range(3):
                curve(c, (360 + g * 400 + 50, 487), (360 + g * 400 + 200, 330), (360 + (g + 1) * 400 - 200, 330), (360 + (g + 1) * 400 - 50, 487), ETH, 1.8, a * 0.8)
            text(c, "JUPITER, Jülich: NDR200 InfiniBand", 960, 850, 32, INK, "serif", "c", a * P(t, B(5) + 3, B(5) + 4))
