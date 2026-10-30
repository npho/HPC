"""Scenes 3-5: machinery, vocabulary, life of a job."""
import math, random
from engine import *
from scenes.common import *

SCENES = {}


def scene(sid, title="", sources=None):
    def deco(fn):
        SCENES[sid] = dict(title=title, sources=sources or [], draw=fn)
        return fn
    return deco


def note(cv, t, ts, x, y, w, head, body, size=19, color="dim"):
    a = appear(t, ts, 0.7)
    if a > 0:
        sidenote(cv, x, y + (1 - a) * 8, w, head, body, a, color, size)


# ================================================================================ S03 machinery
@scene("s03_anatomy", "The machinery", ["quickstart_admin · network · slurm.conf(5): TreeWidth, SlurmctldTimeout · configless_slurm · accounting",
                                      "2003 design report"])
def s03(cv, t, S):
    headline(cv, "A cluster is a handful of daemons", t)
    tree_a = appear(t, S.c(3, -0.3), 0.8) * (1 - appear(t, S.c(4, -0.2), 0.8))
    dg = 1 - tree_a                       # diagram alpha while the tree overlay is up

    # ---------------- geometry
    CX, CY, CW, CH = 560, 205, 330, 104         # slurmctld
    BX = 940                                    # backup
    DX, DY, DW = 1190, 205, 250                 # slurmdbd
    LX, LY, LW_ = 110, 215, 250                 # login
    BUS = 372
    RX, RY = 110, 470                           # compute rack
    nodes = [(RX + 20 + (i % 6) * 150, RY + 44 + (i // 6) * 84) for i in range(12)]

    # beat 0 : controller
    a0 = appear(t, S.c(0, 0.2), 0.8) * dg
    if a0 > 0:
        cv.glow(CX + CW / 2, CY + CH / 2, 230, "orange", 0.22 * a0 * pulse(t, 2.4, 0.6, 1))
        box(cv, CX, CY, CW, CH, "slurmctld", "queue · node state · decisions", "orange", a0, size=30)
        for i, w in enumerate(("holds the whole queue", "tracks every node", "decides what runs")):
            aa = appear(t, S.f(0, 0.30 + i * 0.16), 0.6) * dg
            cv.text("· " + w, CX + CW + 26, CY + 30 + i * 28, 20, "dim", "ital", a=aa * (1 - appear(t, S.c(1, 0.5), 0.6)))

    # beat 1 : slurmd on each node + slurmdbd + database
    rack_a = appear(t, S.c(1, 0.1), 0.7) * dg
    if rack_a > 0:
        cv.rect(RX, RY, 920, 210, stroke="rule", sw=1.1, r=10, a=rack_a * 0.8, dash=(6, 6))
        cv.text("compute nodes", RX + 14, RY - 12, 21, "dim", "ital", a=rack_a)
        for i, (nx, ny) in enumerate(nodes):
            aa = appear(t, S.c(1, 0.25 + i * 0.12), 0.5) * dg
            cv.rect(nx, ny - 12, 134, 62, fill="blue", r=7, a=0.10 * aa)
            cv.rect(nx, ny - 12, 134, 62, stroke="blue", sw=1.2, r=7, a=aa)
            cv.text("slurmd", nx + 67, ny + 25, 21, "ink", "mono", "c", aa)
    ad = appear(t, S.f(1, 0.55), 0.8) * dg
    if ad > 0:
        box(cv, DX, DY, DW, CH, "slurmdbd", "accounting history", "teal", ad, size=28)
        cylinder(cv, DX + 40, DY + CH + 70, 170, 112, "teal", ad, "MariaDB")
        cv.arrow(DX + DW / 2, DY + CH + 2, DX + DW / 2, DY + CH + 68, "teal", 1.5, ad)

    # management bus
    bus_a = appear(t, S.c(2, 0.0), 0.8) * dg
    if bus_a > 0:
        cv.line(LX + LW_ / 2, BUS, DX + DW / 2 + 40, BUS, "rule", 1.4, bus_a, frac=ease_out(prog(t, S.c(2), 1.2)))
        for x, y0 in ((CX + CW / 2, CY + CH), (LX + LW_ / 2, LY + 70), (DX + 40, BUS)):
            if y0 < BUS:
                cv.line(x, y0, x, BUS, "rule", 1.2, bus_a)
        cv.line(RX + 460, BUS, RX + 460, RY, "rule", 1.2, bus_a)
        cv.text("management network", LX + LW_ / 2 + 260, BUS - 10, 18, "dim", "ital", a=bus_a)

    # beat 2 : login nodes, munge keys
    al = appear(t, S.c(2, 0.15), 0.8) * dg
    if al > 0:
        box(cv, LX, LY, LW_, 70, "login", "sbatch · srun · squeue", "purple", al, size=26)
        key_a = appear(t, S.f(2, 0.35), 0.7) * dg
        for (kx, ky) in [(LX + LW_ - 20, LY - 14), (CX + CW - 22, CY - 14), (DX + DW - 22, DY - 14)] + [(nx + 118, ny - 6) for nx, ny in nodes]:
            key_icon(cv, kx - 14, ky, "yellow", key_a * 0.95, 0.75)
        if key_a > 0:
            cv.text("same MUNGE key everywhere", 130, 175, 21, "yellow", "ital", a=key_a)

    # backup controller + shared state (beat 4)
    ab = appear(t, S.f(4, 0.05), 0.7)
    if ab > 0:
        fail = prog(t, S.f(4, 0.20), 0.6)
        take = prog(t, S.f(4, 0.46), 0.6)
        back = prog(t, S.f(4, 0.78), 0.6)
        pri_dead = fail * (1 - back)
        bk_on = take * (1 - back)
        box(cv, BX, CY, 220, CH, "backup", "slurmctld", "orange", ab * (0.35 + 0.65 * bk_on), size=26)
        cv.rect(BX, CY, 220, CH, stroke="orange", sw=1.4, r=9, a=ab * (1 - bk_on), dash=(6, 6))
        # shared state
        cylinder(cv, CX + 80, CY + CH + 66, 170, 84, "orange", ab * 0.8, "state dir")
        cv.line(CX + CW / 2 - 40, CY + CH, CX + CW / 2 - 40, CY + CH + 66, "orange", 1.2, ab * 0.8)
        cv.line(BX + 110, CY + CH, BX + 110, CY + CH + 40, "orange", 1.2, ab * 0.8)
        cv.line(BX + 110, CY + CH + 40, CX + 250, CY + CH + 40, "orange", 1.2, ab * 0.8)
        cv.line(CX + 250, CY + CH + 40, CX + 250, CY + CH + 66, "orange", 1.2, ab * 0.8)
        if pri_dead > 0:
            cv.rect(CX, CY, CW, CH, fill="red", r=9, a=0.28 * pri_dead)
            cv.line(CX + 24, CY + 24, CX + CW - 24, CY + CH - 24, "red", 3, pri_dead)
            cv.line(CX + CW - 24, CY + 24, CX + 24, CY + CH - 24, "red", 3, pri_dead)
        # timer arc (SlurmctldTimeout)
        if fail > 0.1 and take < 1.0:
            cx, cy = (CX + BX + 220) / 2 + 20, CY - 52
            cv.circle(cx, cy, 20, stroke="rule", sw=1.4, a=1)
            ang = 2 * math.pi * prog(t, S.f(4, 0.22), S.f(4, 0.46) - S.f(4, 0.22))
            pts = [(cx + 17 * math.sin(a_), cy - 17 * math.cos(a_)) for a_ in [ang * k / 24 for k in range(25)]]
            cv.polyline(pts, "yellow", 2.4)
            cv.text("2 min by default", cx + 34, cy + 7, 19, "yellow", "ital")
        # database outage + queue
        dbd = prog(t, S.f(4, 0.55), 0.5) * (1 - prog(t, S.f(4, 0.92), 0.5))
        if dbd > 0:
            cv.rect(DX, DY, DW, CH, fill="red", r=9, a=0.22 * dbd)
            cv.text("database down", DX + DW / 2, DY - 14, 20, "red", "ital", "c", dbd)
            cv.rect(DX - 10, DY + CH + 8, 0, 0)
            for i in range(5):
                bx = BUS - 0
                cv.rect(1010 + i * 34, 330, 24, 18, stroke="orange", sw=1.1, r=3, a=dbd * 0.9)
            cv.text("records queue on the controller", 1010, 322, 19, "orange", "ital", a=dbd)

    # beat 5 : configless pull
    ac = appear(t, S.c(5, 0.1), 0.6) * (1 - appear(t, S.c(6, 0.6), 0.6))
    if ac > 0:
        for i in (0, 3, 6, 9):
            nx, ny = nodes[i]
            ph = (prog(t, S.f(5, 0.25 + i * 0.05), 1.6))
            sx, sy = nx + 67, ny - 12
            ex, ey = CX + CW / 2, CY + CH
            cv.curve((sx, sy), (sx, BUS), (ex, BUS + 40), (ex, ey + 4), "yellow", 1.6, ac * 0.8, frac=ease_io(ph))
            if 0 < ph < 1:
                p = ease_io(ph)
                cv.circle(*bez((sx, sy), (sx, BUS), (ex, BUS + 40), (ex, ey + 4), 1 - p), 6, fill="yellow", a=ac)
        cv.text("slurmd asks the controller for its config at startup", 130, 745, 22, "yellow", "ital", a=ac)

    # beat 6 : fabric + parallel file system
    af = appear(t, S.c(6, 0.2), 0.9)
    if af > 0:
        cv.line(RX + 460, RY + 210, RX + 460, 735, "teal", 3, af, frac=1)
        cv.line(RX + 40, 735, RX + 880, 735, "teal", 3, af)
        for nx in range(RX + 80, RX + 880, 150):
            cv.line(nx, RY + 210, nx, 735, "teal", 1.2, af * 0.7)
        cv.text("high-speed fabric  (for the jobs themselves)", RX + 900, 742, 21, "teal", "ital", a=af)
        pf = appear(t, S.f(6, 0.55), 0.9)
        cv.rect(RX, 790, 920, 74, fill="purple", r=10, a=0.12 * pf)
        cv.rect(RX, 790, 920, 74, stroke="purple", sw=1.5, r=10, a=pf)
        cv.text("parallel file system  ·  GPFS · Lustre · BeeGFS", RX + 460, 835, 25, "ink", "body", "c", pf)
        cv.line(RX + 460, 735, RX + 460, 790, "purple", 2, pf)
        cv.text("mounted by every node; Slurm schedules compute, not data", RX + 460, 895, 21, "dim", "ital", "c", appear(t, S.f(6, 0.82), 0.8))

    # ---------------- beat 3 overlay: the fan-out tree
    if tree_a > 0:
        a = tree_a
        rx, ry = 960, 250
        cv.rect(110, 190, 1700, 800, fill="bg", a=0.0)
        box(cv, rx - 115, ry - 40, 230, 64, "slurmctld", None, "orange", a, size=26)
        l1y, l2y = 410, 560
        xs1 = [200 + i * 90 for i in range(16)]
        g1 = ease_out(prog(t, S.f(3, 0.22), 0.9))
        # level 1
        for i, x in enumerate(xs1):
            cv.line(rx, ry + 24, x, l1y - 14, "orange", 1.0, a * 0.7, frac=g1)
            if g1 > 0.7:
                cv.circle(x, l1y, 11, fill="blue", a=a * 0.9)
        # level 2: 16 tiny dots under each level-1 node
        g2 = ease_out(prog(t, S.f(3, 0.45), 1.1))
        for i, x in enumerate(xs1):
            for k in range(16):
                dx = (k % 8 - 3.5) * 7.2
                dy = (k // 8) * 10
                px, py = x + dx, l2y + dy
                cv.line(x, l1y + 11, px, py - 3, "blue", 0.5, a * 0.30, frac=g2)
                if g2 > 0.75:
                    cv.circle(px, py, 2.6, fill="blue", a=a * 0.85)
        # level 3 hint
        g3 = ease_out(prog(t, S.f(3, 0.66), 1.0))
        cv.rect(160, 690, 1400 * g3, 26, fill="blue", r=3, a=a * 0.28)
        cv.rect(160, 690, 1400 * g3, 26, stroke="blue", sw=1.0, r=3, a=a * 0.7)
        # counters
        def cnt(ts, y, txt, c="ink"):
            aa = appear(t, ts, 0.6) * a
            cv.text(txt, 1850, y, 24, c, "body", "r", aa)
        cnt(S.f(3, 0.30), l1y + 6, "× 16  =  16")
        cnt(S.f(3, 0.52), l2y + 24, "× 16  =  256")
        cnt(S.f(3, 0.72), 712, "× 16  =  4,096")
        tot = appear(t, S.f(3, 0.80), 0.8) * a
        cv.text("16 + 256 + 4,096  =  4,368 nodes in three hops", 960, 800, 34, "yellow", "ital", "c", tot)
        chip(cv, 760, 868, "TreeWidth=16", "yellow", tot, 24, "mono", 14)
        cv.text("(default; the man page's own arithmetic)", 1000, 862, 20, "dim", "ital", a=tot)
        cv.text("The 2003 report describes the controller and srun contacting each slurmd directly.", 960, 940, 19, "dim", "ital", "c", appear(t, S.f(3, 0.9), 0.7) * a)

    # margin notes
    mx, mw = 1480, 340
    note(cv, t, S.c(0, 6.0), mx, 215, mw, "", "One controller is active; a backup may be listed.", 20)
    note(cv, t, S.c(2, 2.5), mx, 330, mw, "docs", "Clocks, user IDs and group IDs must agree across the cluster.", 20)
    note(cv, t, S.f(4, 0.30), mx, 500, mw, "slurm.conf", "SlurmctldTimeout default: 120 s. If slurmdbd is down, records queue; if the queue overflows they are dropped.", 19)
    note(cv, t, S.f(5, 0.55), mx, 700, mw, "configless", "On by default since 20.02; slurmd finds the controller via --conf-server or a DNS SRV record.", 19)


def bez(p0, p1, p2, p3, u):
    """cubic bezier point at parameter 1-u (so u=1 -> start)."""
    s = 1 - u
    x = (1 - s) ** 3 * p0[0] + 3 * (1 - s) ** 2 * s * p1[0] + 3 * (1 - s) * s * s * p2[0] + s ** 3 * p3[0]
    y = (1 - s) ** 3 * p0[1] + 3 * (1 - s) ** 2 * s * p1[1] + 3 * (1 - s) * s * s * p2[1] + s ** 3 * p3[1]
    return x, y


# ================================================================================ S04 vocabulary
PX = [96, 684, 1272]
PY = [185, 590]
PW, PH = 552, 372


def panel(cv, i, title, color, a_on, a_frame):
    px, py = PX[i % 3], PY[i // 3]
    cv.rect(px, py, PW, PH, stroke="faint", sw=1.0, r=10, a=a_frame)
    cv.text(title, px + 20, py + 40, 29, color, "bold", a=max(a_on, 0.35 * a_frame))
    return px, py


@scene("s04_vocab", "Vocabulary", ["overview · slurm.conf(5) · accounting · qos · tres · resource_limits"])
def s04(cv, t, S):
    headline(cv, "Slurm's nouns are its design", t)
    ladder = appear(t, S.c(6, -0.4), 0.9)
    gridA = 1 - 0.93 * ladder
    fr = appear(t, 0.8, 1.0) * gridA

    # ---- 0 node
    a = appear(t, S.c(0, 0.1), 0.7) * gridA
    px, py = panel(cv, 0, "node", "blue", a, fr)
    if a > 0:
        cv.rect(px + 22, py + 66, 330, 250, stroke="blue", sw=1.4, r=10, a=a)
        for s_ in range(2):
            sx = px + 38 + s_ * 160
            cv.rect(sx, py + 84, 142, 110, stroke="dim", sw=1.0, r=6, a=a)
            cv.text(f"socket {s_}", sx + 6, py + 80, 15, "dim", "sans", a=a)
            for c_ in range(8):
                aa = stagger(t, S.f(0, 0.12), c_ + s_ * 8, 0.04, 0.4) * gridA
                cv.rect(sx + 10 + (c_ % 4) * 31, py + 104 + (c_ // 4) * 32, 24, 24, fill="blue", r=3, a=0.55 * aa)
        cv.rect(px + 38, py + 212, 302, 20, stroke="teal", sw=1.0, r=4, a=a)
        cv.rect(px + 38, py + 212, 302 * 0.7 * appear(t, S.f(0, 0.3), 0.8), 20, fill="teal", r=4, a=0.5 * a)
        cv.text("memory", px + 44, py + 248, 16, "dim", "sans", a=a)
        for g in range(2):
            aa = appear(t, S.f(0, 0.4 + g * 0.05), 0.5) * gridA
            cv.rect(px + 38 + g * 70, py + 262, 58, 40, stroke="green", sw=1.3, r=5, a=aa)
            cv.text("GPU", px + 67 + g * 70, py + 288, 16, "green", "sans", "c", aa)
        cv.text("sockets · cores · threads · memory · devices", px + 22, py + PH - 14, 16.5, "dim", "ital", a=a)
        for k, (nm, c) in enumerate((("idle", "green"), ("allocated", "blue"), ("draining", "orange"), ("down", "red"))):
            aa = appear(t, S.f(0, 0.62 + k * 0.08), 0.5) * gridA
            chip(cv, px + 376, py + 100 + k * 52, nm, c, aa, 20, "body", 12)
        cv.text("state", px + 376, py + 72, 17, "dim", "ital", a=a)

    # ---- 1 partition
    a = appear(t, S.c(1, 0.1), 0.7) * gridA
    px, py = panel(cv, 1, "partition", "teal", a, fr)
    if a > 0:
        for n in range(12):
            nx = px + 22 + n * 43.5
            aa = stagger(t, S.c(1, 0.2), n, 0.05, 0.4) * gridA
            cv.rect(nx, py + 150, 36, 36, fill="dim", r=4, a=0.25 * aa)
            cv.rect(nx, py + 150, 36, 36, stroke="dim", sw=1.0, r=4, a=aa)
        ba = appear(t, S.f(1, 0.30), 0.7) * gridA
        x1, x2 = px + 22, px + 22 + 8 * 43.5 - 7
        cv.line(x1, py + 134, x2, py + 134, "teal", 3, ba)
        cv.text("short", x1, py + 120, 22, "teal", "ital", a=ba)
        cv.text("MaxTime=4:00:00", x1 + 78, py + 120, 18, "teal", "mono", a=ba)
        bb = appear(t, S.f(1, 0.55), 0.7) * gridA
        x3, x4 = px + 22 + 4 * 43.5, px + 22 + 12 * 43.5 - 7
        cv.line(x3, py + 204, x4, py + 204, "yellow", 3, bb)
        cv.text("long", x3, py + 240, 22, "yellow", "ital", a=bb)
        cv.text("MaxTime=7-00:00:00", x3 + 62, py + 240, 18, "yellow", "mono", a=bb)
        bo = appear(t, S.f(1, 0.78), 0.7) * gridA
        cv.rect(x3 - 3, py + 144, 4 * 43.5 + 2, 48, stroke="ink", sw=1.4, r=5, a=bo, dash=(5, 4))
        cv.text("overlap is allowed", px + 22, py + 296, 21, "ink", "ital", a=bo)
        cv.text("a node can serve a short queue and a long one", px + 22, py + 324, 17, "dim", "ital", a=bo)
        cv.text("(the 2003 design: disjoint)", px + 22, py + 346, 16, "dim", "ital", a=bo)

    # ---- 2 job & step
    a = appear(t, S.c(2, 0.1), 0.7) * gridA
    px, py = panel(cv, 2, "job  &  step", "purple", a, fr)
    if a > 0:
        jx, jy, jw, jh = px + 70, py + 80, 420, 220
        cv.line(jx - 10, jy + jh, jx + jw + 10, jy + jh, "rule", 1, a)
        cv.line(jx, jy - 10, jx, jy + jh, "rule", 1, a)
        cv.text("nodes", px + 22, jy + 20, 16, "dim", "ital", a=a)
        cv.text("time", jx + jw, jy + jh + 24, 16, "dim", "ital", "r", a)
        ja = appear(t, S.f(2, 0.1), 0.7) * gridA
        cv.rect(jx, jy, jw, jh, fill="purple", r=6, a=0.10 * ja)
        cv.rect(jx, jy, jw, jh, stroke="purple", sw=2, r=6, a=ja)
        cv.text("job: 4 nodes, 3 h limit", jx + 10, jy - 12, 20, "purple", "body", a=ja)
        steps = [(0, 0, 130, 220, "step 0", "blue"), (136, 0, 284, 108, "step 1", "teal"), (136, 112, 284, 108, "step 2", "orange")]
        for k, (sx, sy, sw_, sh, nm, c) in enumerate(steps):
            aa = appear(t, S.f(2, 0.45 + k * 0.14), 0.6) * gridA
            cv.rect(jx + sx + 5, jy + sy + 5, sw_ - 10, sh - 10, fill=c, r=4, a=0.22 * aa)
            cv.rect(jx + sx + 5, jy + sy + 5, sw_ - 10, sh - 10, stroke=c, sw=1.3, r=4, a=aa)
            cv.text(nm, jx + sx + sw_ / 2, jy + sy + sh / 2 + 7, 21, "ink", "mono", "c", aa)
        cv.text("steps (srun) are the parallel programs inside an allocation", px + 22, py + PH - 14, 16.5, "dim", "ital", a=ja)

    # ---- 3 account tree + association
    a = appear(t, S.c(3, 0.1), 0.7) * gridA
    px, py = panel(cv, 3, "account  &  association", "blue", a, fr)
    if a > 0:
        nodes = {"cluster": (px + 276, py + 84), "physics": (px + 150, py + 160), "chem": (px + 402, py + 160),
                 "ana": (px + 84, py + 250), "bo": (px + 216, py + 250), "cy": (px + 402, py + 250)}
        edges = [("cluster", "physics"), ("cluster", "chem"), ("physics", "ana"), ("physics", "bo"), ("chem", "cy")]
        for k, (u, v) in enumerate(edges):
            aa = appear(t, S.c(3, 0.3 + k * 0.2), 0.5) * gridA
            cv.line(*nodes[u], *nodes[v], "rule", 1.3, aa)
        labels = {"cluster": ("cluster", "ink"), "physics": ("account", "blue"), "chem": ("account", "blue"),
                  "ana": ("user", "teal"), "bo": ("user", "teal"), "cy": ("user", "teal")}
        names = {"cluster": "cluster", "physics": "physics", "chem": "chemistry", "ana": "ana", "bo": "bo", "cy": "cy"}
        for k, (nm, (x, y)) in enumerate(nodes.items()):
            aa = appear(t, S.c(3, 0.15 + k * 0.2), 0.5) * gridA
            c = labels[nm][1]
            cv.circle(x, y, 9, fill=c, a=aa * 0.9)
            cv.text(names[nm], x, y - 17 if nm == "cluster" else y + 33, 19, "ink", "body", "c", aa)
        for nm, sh in (("physics", "shares 60"), ("chem", "shares 40")):
            aa = appear(t, S.f(3, 0.55), 0.6) * gridA
            x, y = nodes[nm]
            cv.text(sh, x + 20, y + 8, 16, "yellow", "mono", "l", aa)
        # highlight an association
        ha = appear(t, S.f(3, 0.72), 0.7) * gridA
        pts = [nodes["cluster"], nodes["physics"], nodes["ana"]]
        cv.polyline(pts, "yellow", 3.2, ha)
        cv.text("association = (cluster, account, user [, partition])", px + 22, py + PH - 14, 16.5, "yellow", "ital", a=ha)

    # ---- 4 QOS
    a = appear(t, S.c(4, 0.1), 0.7) * gridA
    px, py = panel(cv, 4, "QOS", "yellow", a, fr)
    if a > 0:
        cards = [("normal", [("priority", "base"), ("UsageFactor", "1")], "ink"),
                 ("high", [("priority", "higher"), ("UsageFactor", "2")], "orange"),
                 ("standby", [("priority", "lower"), ("UsageFactor", "0"), ("preemptible", "yes")], "teal")]
        for k, (nm, rows, c) in enumerate(cards):
            aa = appear(t, S.c(4, 0.2 + k * 0.5), 0.6) * gridA
            cx = px + 20 + k * 172
            cv.rect(cx, py + 70, 160, 226, fill=c, r=9, a=0.08 * aa)
            cv.rect(cx, py + 70, 160, 226, stroke=c, sw=1.4, r=9, a=aa)
            cv.text(nm, cx + 80, py + 106, 25, c, "bold", "c", aa)
            for j, (kk, vv) in enumerate(rows):
                cv.text(kk, cx + 14, py + 150 + j * 44, 16, "dim", "mono", a=aa)
                cv.text(vv, cx + 146, py + 150 + j * 44, 20, "ink", "mono", "r", aa)
        cv.text("illustrative values; a QOS also carries limits", px + 22, py + PH - 38, 16.5, "dim", "ital", a=a)
        cv.text("and says whom it may preempt", px + 22, py + PH - 14, 16.5, "dim", "ital", a=a)

    # ---- 5 TRES
    a = appear(t, S.c(5, 0.1), 0.7) * gridA
    px, py = panel(cv, 5, "TRES", "orange", a, fr)
    if a > 0:
        names_ = ["cpu", "mem", "node", "gres/gpu", "license", "billing"]
        x, y = px + 22, py + 92
        for k, nm in enumerate(names_):
            aa = appear(t, S.c(5, 0.2 + k * 0.28), 0.5) * gridA
            w = chip(cv, x, y, nm, "orange" if nm != "billing" else "yellow", aa, 21, "mono", 11)
            x += w + 12
            if x > px + PW - 130:
                x, y = px + 22, y + 52
        fa = appear(t, S.f(5, 0.7), 0.8) * gridA
        cv.text("billing  =  Σ  weight × amount", px + 22, py + 232, 25, "yellow", "body", a=fa)
        cv.text("doc example: CPU=1.0, Mem=0.25/GiB", px + 22, py + 272, 18, "dim", "mono", a=fa)
        cv.text("1 CPU + 8 GiB  →  1.0 + 2.0 = 3.0", px + 22, py + 302, 18, "ink", "mono", a=fa)
        cv.text("limits and usage are written in these units", px + 22, py + PH - 14, 16.5, "dim", "ital", a=fa)

    # ---- ladder
    if ladder > 0:
        L = ladder
        cv.text("When limits disagree, the first rung that defines the limit wins", 96, 200, 30, "ink", "ital", a=L)
        rungs = ["partition QOS", "job QOS", "user association", "account association(s), upward", "cluster (root) association", "partition limit"]
        lx, ly = 140, 262
        for k, r_ in enumerate(rungs):
            aa = appear(t, S.c(6, 0.4 + k * 0.45), 0.5) * L
            y = ly + k * 78
            cv.rect(lx, y, 540, 58, fill="yellow", r=8, a=0.07 * aa)
            cv.rect(lx, y, 540, 58, stroke="yellow", sw=1.3, r=8, a=aa)
            cv.text(str(k + 1), lx + 28, y + 38, 26, "yellow", "bold", "c", aa)
            cv.text(r_, lx + 62, y + 38, 24, "ink", "body", a=aa)
        # worked example
        ex = 800
        ea = appear(t, S.f(6, 0.42), 0.8) * L
        cv.text("the documentation's example", ex, 262, 24, "dim", "ital", a=ea)
        cv.text("partition QOS:", ex, 316, 22, "ink", "body", a=ea)
        cv.text("MaxJobs=20", ex + 220, 316, 22, "teal", "mono", a=ea)
        cv.text("user association:", ex, 356, 22, "ink", "body", a=ea)
        cv.text("MaxJobs=4  MaxSubmitJobs=50", ex + 220, 356, 22, "teal", "mono", a=ea)
        # walkers
        for k, (nm, stop, res, ts) in enumerate((("MaxJobs", 0, "20", 0.54), ("MaxSubmitJobs", 2, "50", 0.66))):
            aa = appear(t, S.f(6, ts), 0.6) * L
            yy = 470 + k * 120
            cv.text(nm + "  →", ex, yy, 26, "ink", "mono", a=aa)
            g = ease_io(prog(t, S.f(6, ts + 0.02), 1.6))
            ty_ = ly + 29 + (stop * g) * 78 if False else ly + 29 + stop * 78 * g
            cv.arrow(690, ty_, 700, ty_, "yellow", 2, aa * (1 if g > 0 else 0), head=11)
            cv.circle(684, ty_, 7, fill="yellow", a=aa * (1 if g > 0 else 0))
            fin = appear(t, S.f(6, ts + 0.04, 1.8), 0.5) * L
            cv.text(f"= {res}", ex + 330, yy, 30, "yellow", "bold", a=fin)
            cv.text(f"first defined at rung {stop + 1}", ex + 330, yy + 30, 18, "dim", "ital", a=fin)
        sw_a = appear(t, S.f(6, 0.88), 0.8) * L
        cv.text("flag OverPartQOS swaps rungs 1 and 2", ex, 760, 22, "ink", "ital", a=sw_a)
        cv.arrow(lx + 600, ly + 29, lx + 600, ly + 29 + 78 - 10, "yellow", 1.4, sw_a, head=8)
        cv.arrow(lx + 612, ly + 29 + 78 - 10, lx + 612, ly + 29, "yellow", 1.4, sw_a, head=8)


# ================================================================================ S05 life of a job
LANES = [("you", "sbatch · srun", 230, "purple"), ("slurmctld", "controller", 620, "orange"),
         ("slurmd", "first node", 1010, "blue"), ("slurmd", "other nodes", 1400, "blue"), ("slurmdbd", "database", 1730, "teal")]


def lane_x(i):
    return LANES[i][2]


def lane_heads(cv, a):
    for i, (nm, sub, x, c) in enumerate(LANES):
        w = 220 if i < 4 else 170
        cv.rect(x - w / 2, 180, w, 66, fill=c, r=8, a=0.10 * a)
        cv.rect(x - w / 2, 180, w, 66, stroke=c, sw=1.4, r=8, a=a)
        cv.text(nm, x, 214, 24, "ink", "mono", "c", a)
        cv.text(sub, x, 237, 15.5, "dim", "ital", "c", a)
        cv.line(x, 246, x, 930, "faint", 1.0, a * 0.9, dash=(3, 6))


def msg(cv, t, ts, fr, to, y, label, color="ink", a=1.0, dy=-9, dur=0.9, align="c"):
    p = ease_io(prog(t, ts, dur))
    if p <= 0:
        return
    x1, x2 = lane_x(fr), lane_x(to)
    cv.arrow(x1, y, x2, y, color, 1.9, a, head=11, frac=p)
    if p > 0.3:
        cv.text(label, (x1 + x2) / 2, y + dy, 19.5, color, "ital", "c", a * appear(t, ts + 0.3, 0.4))
    # traveling dot
    if p < 1:
        cv.circle(lerp(x1, x2, p), y, 6, fill=color, a=a)


def actbox(cv, t, ts, lane, y, h, label, color, a=1.0, w=250, size=19, sub=None):
    aa = appear(t, ts, 0.6) * a
    if aa <= 0:
        return
    x = lane_x(lane)
    cv.rect(x - w / 2, y, w, h, fill=color, r=7, a=0.14 * aa)
    cv.rect(x - w / 2, y, w, h, stroke=color, sw=1.3, r=7, a=aa)
    cv.text(label, x, y + h / 2 + (-2 if sub else 6), size, "ink", "body", "c", aa)
    if sub:
        cv.text(sub, x, y + h / 2 + 22, size * 0.8, "dim", "ital", "c", aa)


@scene("s05_job", "Life of a job", ["job_launch (slurm.schedmd.com) · squeue(1) job state codes · sinfo(1) node states · slurm.conf(5)"])
def s05(cv, t, S):
    headline(cv, "Follow one job", t, 0.3)
    phaseA = 1 - appear(t, S.c(5, -0.3), 0.7)
    lane_heads(cv, appear(t, 0.8, 0.8))

    # ---- phase A (beats 0-4)
    if phaseA > 0.01:
        A = phaseA
        msg(cv, t, S.f(0, 0.18), 0, 1, 292, "job request  (+ your uid / gid)", "purple", A)
        msg(cv, t, S.f(0, 0.62), 1, 0, 336, "job id, immediately", "orange", A)
        actbox(cv, t, S.f(1, 0.10), 1, 372, 70, "submit plugins may rewrite", "orange", A, 270, 18, "then validate vs. partition & limits")
        actbox(cv, t, S.f(1, 0.55), 1, 452, 50, "PENDING  + reason", "yellow", A, 270, 19)
        if S.f(1, 0.7) < t:
            for k, w in enumerate(("Priority", "Resources", "Dependency")):
                aa = appear(t, S.f(1, 0.72 + k * 0.08), 0.5) * A
                chip(cv, 660 - 40 + k * 0, 530 + k * 0, w, "yellow", 0.0)
            for k, w in enumerate(("Priority", "Resources", "Dependency")):
                aa = appear(t, S.f(1, 0.74 + k * 0.07), 0.5) * A
                chip(cv, 770 + k * 150, 482, w, "yellow", aa, 18, "mono", 9)
            cv.text("pending reasons, e.g.", 770, 446, 17, "dim", "ital", a=appear(t, S.f(1, 0.72), 0.5) * A)
        actbox(cv, t, S.f(2, 0.12), 1, 530, 70, "select plugin picks", "orange", A, 270, 18, "cores · memory · GRES  (topology-aware)")
        # prolog / configuring
        actbox(cv, t, S.f(2, 0.55), 2, 548, 40, "prolog", "blue", A, 130, 17)
        msg(cv, t, S.f(3, 0.02), 1, 2, 628, "start the batch step", "orange", A)
        actbox(cv, t, S.f(3, 0.10), 2, 648, 56, "slurmstepd runs your script", "blue", A, 290, 17)
        msg(cv, t, S.f(3, 0.30), 2, 1, 740, "srun: step request", "blue", A)
        msg(cv, t, S.f(3, 0.40), 1, 2, 776, "resources + signed credential", "orange", A)
        msg(cv, t, S.f(3, 0.52), 2, 3, 812, "launch  (forwarded down the tree)", "blue", A)
        actbox(cv, t, S.f(3, 0.62), 3, 836, 54, "slurmstepd per node", "blue", A, 260, 17)
        cv.text("the controller never touches task launch", 610, 905, 19, "orange", "ital", "l", appear(t, S.f(3, 0.8), 0.7) * A)
        # beat 4: what slurmstepd does
        if t > S.c(4) - 0.2:
            ca = appear(t, S.c(4, 0.0), 0.6) * A
            cv.rect(96, 640, 490, 270, fill="bg", a=1.0 * ca)
            cv.rect(96, 640, 490, 270, stroke="blue", sw=1.2, r=8, a=ca)
            cv.text("each slurmstepd, in order", 116, 674, 21, "blue", "ital", a=ca)
            items = ["MPI setup", "network (switch plugin)", "container for process tracking", "drop to your user id", "wire up input / output", "fork + exec the tasks"]
            for k, w in enumerate(items):
                aa = appear(t, S.f(4, 0.12 + k * 0.125), 0.5) * A
                cv.text(f"{k+1}", 132, 713 + k * 31, 19, "yellow", "mono", "c", aa)
                cv.text(w, 156, 713 + k * 31, 20, "ink", "body", a=aa)

    # ---- phase B (beat 5): termination
    B = appear(t, S.c(5, -0.1), 0.8)
    if B > 0.01:
        msg(cv, t, S.f(5, 0.10), 1, 2, 312, "time is up / scancel", "orange", B)
        msg(cv, t, S.f(5, 0.10), 1, 3, 330, "", "orange", B)
        actbox(cv, t, S.f(5, 0.22), 2, 372, 120, "SIGTERM", "red", B, 250, 19, "wait KillWait, then SIGKILL")
        actbox(cv, t, S.f(5, 0.22), 3, 372, 120, "SIGTERM", "red", B, 250, 19, "wait KillWait, then SIGKILL")
        actbox(cv, t, S.f(5, 0.42), 2, 530, 46, "epilog", "blue", B, 160, 19)
        actbox(cv, t, S.f(5, 0.42), 3, 530, 46, "epilog", "blue", B, 160, 19)
        msg(cv, t, S.f(5, 0.55), 2, 1, 628, "epilog complete", "blue", B)
        msg(cv, t, S.f(5, 0.70), 1, 4, 700, "accounting record", "teal", B)
        ch = appear(t, S.f(5, 0.80), 0.7) * B
        chip(cv, 480, 800, "COMPLETING → IDLE", "green", ch, 22, "mono", 12)

    # ---- state ribbon (bottom)
    ra = appear(t, S.c(1, 0.0), 0.8)
    if ra > 0:
        states = [("PD", "PENDING", S.f(1, 0.5), "yellow"), ("CF", "CONFIGURING", S.f(2, 0.5), "orange"), ("R", "RUNNING", S.f(2, 0.95), "green"),
                  ("CG", "COMPLETING", S.f(5, 0.28), "orange"), ("CD", "COMPLETED", S.f(5, 0.85), "teal")]
        x = 150
        for k, (code, nm, ts, c) in enumerate(states):
            on = prog(t, ts, 0.4)
            nxt = states[k + 1][2] if k + 1 < len(states) else 1e9
            cur = on * (1 - prog(t, nxt, 0.4))
            w = text_w(nm, 19, "mono") + 56
            cv.rect(x, 944, w, 42, fill=c, r=7, a=ra * (0.06 + 0.30 * cur + 0.12 * on))
            cv.rect(x, 944, w, 42, stroke=c, sw=1.2 + 1.2 * cur, r=7, a=ra * (0.35 + 0.65 * max(on, 0.0)))
            cv.text(code, x + 20, 972, 19, c, "bold", "c", ra)
            cv.text(nm, x + 40, 972, 19, "ink", "mono", a=ra * (0.5 + 0.5 * on))
            if k < len(states) - 1:
                cv.arrow(x + w + 4, 965, x + w + 26, 965, "rule", 1.3, ra, head=8)
            x += w + 32
        oa = appear(t, S.f(5, 0.9), 0.8)
        cv.text("other endings:  F  CA  TO  NF  PR  OOM", x + 20, 972, 19, "dim", "mono", a=oa)
