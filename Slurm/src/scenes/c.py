"""Scenes 6-9: priority, fair-share, backfill, preemption."""
import json, math, os
from engine import *
from scenes.common import *
from paths import DATA

SCENES = {}


def scene(sid, title="", sources=None):
    def deco(fn):
        SCENES[sid] = dict(title=title, sources=sources or [], draw=fn)
        return fn
    return deco


def note(cv, t, ts, x, y, w, head, body, size=19):
    a = appear(t, ts, 0.7)
    if a > 0:
        sidenote(cv, x, y + (1 - a) * 8, w, head, body, a, "dim", size)


# ================================================================================ S06 priority
FACT = [("age", "waited", "yellow"), ("fair-share", "under-served", "blue"), ("job size", "", "teal"),
        ("partition", "", "purple"), ("QOS", "", "orange"), ("TRES", "", "green"), ("site / nice", "", "dim")]


@scene("s06_priority", "Priority", ["priority_multifactor · slurm.conf(5) · sched_config · priority/multifactor docs"])
def s06(cv, t, S):
    headline(cv, "One number per pending job", t, 0.3, "ink")
    # ---------- beat 0: stacked bar of weighted factors for three jobs (weights shown with beat 1)
    x0, bw = 220, 900
    weights = [1000, 10000, 500, 1000, 2000, 0, 0]
    vals = {"A": [0.9, 0.2, 0.3, 0.5, 0.0, 0, 0], "B": [0.3, 0.8, 0.6, 0.5, 0.5, 0, 0], "C": [0.1, 0.5, 0.1, 0.5, 1.0, 0, 0]}
    show_w = appear(t, S.c(1, 0.2), 0.8)
    cv.text("illustrative weights and factor values", x0, 214, 19, "dim", "ital", a=appear(t, S.c(0, 1.0), 0.6))
    for r, (jn, vs) in enumerate(vals.items()):
        y = 280 + r * 130
        a = appear(t, S.c(0, 0.4 + r * 0.35), 0.6)
        cv.text(f"job {jn}", 110, y + 34, 26, "ink", "mono", a=a)
        x = x0
        for k, (nm, sub, c) in enumerate(FACT):
            f_in = appear(t, S.f(0, 0.25 + k * 0.08), 0.5)
            # before weights: unit widths (factor 0..1 * 60); after: weighted
            unit = vs[k] * 110
            wgt = vs[k] * weights[k] / 10000 * bw
            w = lerp(unit, wgt, ease_io(show_w)) * f_in
            if w > 0.5:
                cv.rect(x, y, w, 52, fill=c, r=3, a=0.5 * a)
                cv.rect(x, y, w, 52, stroke=c, sw=1.1, r=3, a=a)
            x += w
        cv.text(f"= {sum(v * wt for v, wt in zip(vs, weights)):,.0f}", x + 18, y + 36, 26, "yellow", "mono", a=a * show_w)
    # legend
    lx = 110
    for k, (nm, sub, c) in enumerate(FACT):
        a = appear(t, S.f(0, 0.25 + k * 0.08), 0.5)
        lx += chip(cv, lx, 700, nm, c, a, 18, "sans", 10) + 12
    cv.text("each factor is a number from 0 to 1", 110, 760, 24, "ink", "ital", a=appear(t, S.f(0, 0.7), 0.6))
    # beat 1: weights default zero
    z = appear(t, S.f(1, 0.2), 0.8)
    if z > 0:
        cv.text("default PriorityWeight for every factor", 110, 840, 26, "ink", "ital", a=z)
        chip(cv, 760, 842, "0", "red", z, 30, "mono", 16)
        cv.text("→ no factor counts until an administrator sets weights", 860, 840, 24, "dim", "ital", a=z)
    # ---------- beat 2: the real comparison order (right column)
    c2 = appear(t, S.c(2, -0.2), 0.8)
    if c2 > 0:
        cv.rect(0, 160, 1920, 860, fill="bg", a=1.0 * c2)
        cv.text("what the scheduler compares, in order", 110, 215, 30, "ink", "ital", a=c2)
        steps = [("1", "can it preempt?", "orange"), ("2", "advanced reservation", "purple"), ("3", "partition priority tier", "teal"),
                 ("4", "priority number", "yellow"), ("5", "submit time", "dim"), ("6", "job id", "dim")]
        for k, (n, w_, c) in enumerate(steps):
            a = appear(t, S.f(2, 0.12 + k * 0.12), 0.55) * c2
            y = 270 + k * 100
            ww = 640 - (0 if k != 3 else 0)
            cv.rect(180, y, ww, 70, fill=c, r=9, a=0.09 * a)
            cv.rect(180, y, ww, 70, stroke=c, sw=2.4 if k == 3 else 1.3, r=9, a=a)
            cv.text(n, 222, y + 47, 30, c, "bold", "c", a)
            cv.text(w_, 262, y + 47, 29, "ink", "body", a=a)
            if k < 5:
                cv.arrow(500, y + 72, 500, y + 98, "rule", 1.3, a * 0.8, head=8)
        cv.text("the number you tune is only the fourth tiebreaker", 900, 600, 30, "yellow", "ital", a=appear(t, S.f(2, 0.75), 0.8) * c2)
        cv.arrow(900, 584, 830, 484, "yellow", 1.5, appear(t, S.f(2, 0.75), 0.8) * c2, head=10)
    if t < S.c(2, -0.3): note(cv, t, S.c(1, 2), 1380, 360, 420, "", "Set per site in slurm.conf: PriorityWeightAge, …Fairshare, …JobSize, …Partition, …QOS.", 20)


# ================================================================================ S07 fair share
def classic_f(u, s=1.0):
    return 2.0 ** (-u / s)


@scene("s07_fairshare", "Fair-share", ["priority_multifactor (classic & Fair Tree) · fair_tree.html · slurm.conf(5): PriorityDecayHalfLife"])
def s07(cv, t, S):
    headline(cv, "Fair-share: promises, not quotas", t, 0.3, "ink")
    # ---- beat 0 : shares vs usage bars for two accounts
    ax, ay = 140, 270
    a0 = appear(t, S.c(0, 0.2), 0.8) * (1 - appear(t, S.c(1, 0.0), 0.7))
    if a0 > 0:
        for i, (nm, sh, us, c) in enumerate((("A", 60, 25, "blue"), ("B", 40, 75, "orange"))):
            y = ay + i * 170
            cv.text(f"account {nm}", ax, y + 28, 27, c, "bold", a=a0)
            g = ease_out(prog(t, S.f(0, 0.2 + i * 0.1), 1.2))
            cv.rect(ax + 230, y, 600, 30, stroke=c, sw=1.3, r=4, a=a0)
            cv.rect(ax + 230, y, 600 * sh / 100 * g, 30, fill=c, r=4, a=0.22 * a0)
            cv.text(f"claim: {sh}% of shares", ax + 840, y + 24, 19, "dim", "ital", a=a0)
            g2 = ease_out(prog(t, S.f(0, 0.5 + i * 0.1), 1.2))
            cv.rect(ax + 230, y + 46, 600 * us / 100 * g2, 30, fill=c, r=4, a=0.75 * a0)
            cv.text(f"usage: {us}% of recent use", ax + 840, y + 70, 19, "dim", "ital", a=a0)
            verdict = ("under-served → rises", "over-used → sinks")[i]
            cv.text(verdict, ax + 230, y + 118, 24, c, "ital", a=a0 * appear(t, S.f(0, 0.8), 0.7))
        cv.text("(illustrative numbers)", ax, 640, 18, "dim", "ital", a=a0)
    # ---- beat 1 : the curve 2^(-U/S)
    c1 = appear(t, S.c(1, 0.0), 0.7) * (1 - appear(t, S.c(3, -0.3), 0.7))
    if c1 > 0:
        gx, gy, gw, gh = 190, 280, 780, 520
        cv.line(gx, gy + gh, gx + gw, gy + gh, "rule", 1.2, c1)
        cv.line(gx, gy, gx, gy + gh, "rule", 1.2, c1)
        for u in (0, 1, 2, 3, 4):
            px = gx + u / 4 * gw
            cv.line(px, gy + gh, px, gy + gh + 7, "rule", 1, c1)
            cv.text(str(u), px, gy + gh + 30, 18, "dim", "sans", "c", c1)
        for v in (0, 0.5, 1):
            py = gy + gh - v * gh
            cv.text(f"{v:g}", gx - 14, py + 6, 18, "dim", "sans", "r", c1)
            cv.line(gx - 6, py, gx, py, "rule", 1, c1)
        cv.text("usage ÷ shares   (U/S)", gx + gw / 2, gy + gh + 62, 20, "dim", "ital", "c", c1)
        cv.text("fair-share factor", gx - 70, gy - 52, 20, "dim", "ital", a=c1)
        cv.text("F = 2", gx + 400, gy + 80, 34, "ink", "math", a=c1 * appear(t, S.f(1, 0.1), 0.6))
        cv.text("−U/S", gx + 480, gy + 58, 22, "ink", "math", a=c1 * appear(t, S.f(1, 0.1), 0.6))
        N = 120
        pts = []
        gr = ease_out(prog(t, S.f(1, 0.15), 3.0))
        for k in range(int(N * gr) + 1):
            u = 4 * k / N
            pts.append((gx + u / 4 * gw, gy + gh - classic_f(u) * gh))
        if len(pts) > 1:
            cv.polyline(pts, "yellow", 3.2, c1)
        marks = [(0, "use nothing → near 1", S.f(1, 0.38)), (1, "use your share → ½", S.f(1, 0.55)), (3.2, "use far more → near 0", S.f(1, 0.78))]
        for u, lab, ts in marks:
            a = appear(t, ts, 0.6) * c1
            px, py = gx + u / 4 * gw, gy + gh - classic_f(u) * gh
            cv.circle(px, py, 8, fill="ink", a=a)
            cv.text(lab, px + (16 if u < 3 else -16), py + (34 if u == 0 else (-50 if u > 3 else -16)), 21, "ink", "ital", "l" if u < 3 else "r", a)
        if appear(t, S.f(1, 0.55), 0.6) > 0:
            a = appear(t, S.f(1, 0.55), 0.6) * c1
            cv.line(gx, gy + gh * 0.5, gx + gw / 4, gy + gh * 0.5, "dim", 1, a, dash=(4, 5))
            cv.line(gx + gw / 4, gy + gh * 0.5, gx + gw / 4, gy + gh, "dim", 1, a, dash=(4, 5))
    # ---- beat 2 : decay (right half, mini plot) — shown alongside the curve
    d2 = appear(t, S.c(2, 0.0), 0.8) * (1 - appear(t, S.c(3, -0.3), 0.7))
    if d2 > 0:
        gx, gy, gw, gh = 1110, 330, 640, 300
        cv.text("one burst of usage, charged on day 0", gx, gy - 50, 22, "ink", "ital", a=d2)
        cv.line(gx, gy + gh, gx + gw, gy + gh, "rule", 1.1, d2)
        cv.line(gx, gy, gx, gy + gh, "rule", 1.1, d2)
        for d in (0, 7, 14, 21, 28):
            px = gx + d / 28 * gw
            cv.line(px, gy + gh, px, gy + gh + 6, "rule", 1, d2)
            cv.text(f"{d}", px, gy + gh + 26, 17, "dim", "sans", "c", d2)
        cv.text("days", gx + gw, gy + gh + 52, 18, "dim", "ital", "r", d2)
        pts = []
        gr = ease_out(prog(t, S.f(2, 0.15), 2.5))
        for k in range(int(100 * gr) + 1):
            dd = 28 * k / 100
            pts.append((gx + dd / 28 * gw, gy + gh - (0.5 ** (dd / 7)) * gh))
        if len(pts) > 1:
            cv.polyline(pts, "blue", 3, d2)
        hl = appear(t, S.f(2, 0.5), 0.6) * d2
        cv.line(gx, gy + gh / 2, gx + gw / 4, gy + gh / 2, "dim", 1, hl, dash=(4, 5))
        cv.line(gx + gw / 4, gy + gh / 2, gx + gw / 4, gy + gh, "dim", 1, hl, dash=(4, 5))
        cv.text("half-life: 7 days (default)", gx + gw / 4 + 14, gy + gh / 2 - 8, 21, "blue", "ital", a=hl)
        cv.text("PriorityDecayHalfLife", gx, gy + gh + 92, 18, "dim", "mono", a=hl)
        cv.text("PriorityUsageResetPeriod can zero usage on a schedule", gx, gy + gh + 120, 18, "dim", "ital", a=appear(t, S.f(2, 0.8), 0.6) * d2)
    # ---- beat 3-4 : Fair Tree
    ft = appear(t, S.c(3, -0.3), 0.8)
    if ft > 0:
        cv.text("Fair Tree (default since 19.05):  rank siblings, then walk depth-first", 110, 215, 26, "ink", "ital", a=ft)
        # account tree
        root = (480, 300)
        A = (290, 440); B = (670, 440)
        users = {"a1": (170, 590), "a2": (300, 590), "a3": (430, 590), "b1": (590, 590), "b2": (720, 590)}
        ul = {"a1": 0.9, "a2": 0.1, "a3": 0.5, "b1": 0.7, "b2": 0.4}
        def node(p, lab, c, a, r=15):
            cv.circle(p[0], p[1], r, fill=c, a=0.9 * a)
            cv.text(lab, p[0], p[1] + r + 24, 20, "ink", "body", "c", a)
        a_tree = appear(t, S.f(3, 0.05), 0.7) * ft
        for u in (A, B):
            cv.line(*root, *u, "rule", 1.3, a_tree)
        for k, (nm, p) in enumerate(users.items()):
            cv.line(*(A if nm[0] == "a" else B), *p, "rule", 1.1, a_tree)
        node(root, "root", "ink", a_tree)
        node(A, "A", "blue", a_tree, 18)
        node(B, "B", "orange", a_tree, 18)
        for nm, p in users.items():
            node(p, nm, "blue" if nm[0] == "a" else "orange", a_tree, 11)
        # worked example numbers (60/70 vs 40/30)
        ex = appear(t, S.f(3, 0.30), 0.7) * ft
        cv.text("shares 60 · usage 70", A[0] - 120, A[1] - 28, 19, "blue", "mono", a=ex)
        cv.text("shares 40 · usage 30", B[0] - 20, B[1] - 28, 19, "orange", "mono", a=ex)
        lf = appear(t, S.f(3, 0.48), 0.7) * ft
        cv.text("level factor = shares ÷ usage", 110, 770, 24, "ink", "ital", a=lf)
        cv.text("A: 0.857", 110, 812, 26, "blue", "mono", a=lf)
        cv.text("B: 1.333  → B ranks first", 330, 812, 26, "orange", "mono", a=lf)
        # rank order panel
        rk = appear(t, S.f(3, 0.65), 0.8) * ft
        px = 1080
        cv.text("depth-first order  →  final fair-share factor", px, 300, 24, "ink", "ital", a=rk)
        order = [("b1", "orange"), ("b2", "orange"), ("a3", "blue"), ("a1", "blue"), ("a2", "blue")]
        order = [("b·best", "orange", 1.0), ("b·next", "orange", 0.75), ("a·best", "blue", 0.5), ("a·mid", "blue", 0.25), ("a·last", "blue", 0.0)]
        for k, (nm, c, f) in enumerate(order):
            a = appear(t, S.f(3, 0.68 + k * 0.045), 0.5) * ft
            y = 340 + k * 74
            cv.rect(px, y, 520, 56, fill=c, r=8, a=0.09 * a)
            cv.rect(px, y, 520, 56, stroke=c, sw=1.2, r=8, a=a)
            cv.text(f"rank {k+1}", px + 18, y + 37, 22, "ink", "mono", a=a)
            cv.text(("under-served user in B", "next user in B", "best user in A", "middle user in A", "heaviest user in A")[k], px + 130, y + 37, 20, "ink", "body", a=a)
            cv.text(f"{(5 - k) / 5:.2f}", px + 500, y + 37, 22, "yellow", "mono", "r", a)
        cv.text("(user factor = rank ÷ number of users, per fair_tree.c; the 5 users are illustrative)", px, 740, 17, "dim", "ital", a=rk)
        # beat 3 punchline then beat 4
        pl = appear(t, S.f(3, 0.85), 0.8) * ft
        cv.text("a sibling outranks → all its users outrank all of the other's", px, 790, 21, "yellow", "ital", a=pl)
        n4 = appear(t, S.c(4, 0.1), 0.8) * ft
        cv.text("fair-share only orders the queue — it never blocks a job", 110, 920, 30, "yellow", "ital", a=n4)


# ================================================================================ S08 backfill
# Gantt demo: 8 nodes, hours. Running A (4 nodes to t=3), B (3 nodes to t=6).
GN, GX, GY, GW, GH = 8, 150, 270, 780, 520    # node rows, geometry
TMAX = 12.0


def gx_(h):
    return GX + h / TMAX * GW


def gy_(n):
    return GY + n * GH / GN


def block(cv, h0, h1, n0, n1, color, label, a=1.0, fill=0.30, dash=None, sw=1.5):
    x, y, w, h = gx_(h0), gy_(n0), gx_(h1) - gx_(h0), gy_(n1) - gy_(n0)
    cv.rect(x + 1.5, y + 1.5, w - 3, h - 3, fill=color, r=3, a=fill * a)
    cv.rect(x + 1.5, y + 1.5, w - 3, h - 3, stroke=color, sw=sw, r=3, a=a, dash=dash)
    if label:
        cv.text(label, x + w / 2, y + h / 2 + 7, 21, "ink", "mono", "c", a)


def gantt_frame(cv, a, title, ox=0):
    cv.text(title, GX, GY - 34, 24, "ink", "ital", a=a)
    for n in range(GN + 1):
        cv.line(GX, gy_(n), GX + GW, gy_(n), "faint", 0.8, a)
    cv.line(GX, GY + GH, GX + GW, GY + GH, "rule", 1.2, a)
    for h in range(0, 13, 2):
        cv.text(f"{h}", gx_(h), GY + GH + 26, 17, "dim", "sans", "c", a)
    cv.text("hours", GX + GW + 8, GY + GH + 26, 17, "dim", "ital", a=a)
    cv.text("nodes", GX - 16, GY - 6, 17, "dim", "ital", "r", a)


@scene("s08_backfill", "Backfill", ["sched_config · slurm.conf(5): SchedulerParameters (bf_*) · Mu'alem & Feitelson 2001 (IEEE TPDS 12:529) · data/backfill_sweep.json"])
def s08(cv, t, S):
    headline(cv, "Backfill: look ahead, don't line up", t, 0.3, "ink")
    sw = json.load(open(DATA / "backfill_sweep.json"))["summary"]
    g01 = (1 - appear(t, S.c(2, -0.3), 0.8))
    # ---- Gantt part (beats 0-1)
    if g01 > 0.01:
        G = g01
        gantt_frame(cv, G * appear(t, 0.8, 0.8), "8 nodes · illustrative")
        block(cv, 0, 3, 0, 4, "blue", "A", G * appear(t, S.c(0, 0.3), 0.6))
        block(cv, 0, 6, 4, 7, "blue", "B", G * appear(t, S.c(0, 0.5), 0.6))
        # idle node 7 (always free) + the half left
        # top job J1 needs all 8 nodes, 2h
        a = appear(t, S.f(0, 0.35), 0.7) * G
        # FIFO view (beat 0): J1 waits until t=6; free nodes idle
        fifo = appear(t, S.f(0, 0.35), 0.7) * (1 - appear(t, S.c(1, 0.0), 0.6))
        if fifo > 0:
            block(cv, 6, 8, 0, 8, "yellow", "J1", fifo * G, 0.25)
            idle_a = appear(t, S.f(0, 0.65), 0.8) * fifo * G
            cv.rect(gx_(3) + 2, gy_(0) + 2, gx_(6) - gx_(3) - 4, gy_(4) - gy_(0) - 4, stroke="red", sw=1.3, r=3, a=idle_a, dash=(5, 5))
            cv.rect(gx_(0) + 2, gy_(7) + 2, gx_(8) - gx_(0) - 4, gy_(8) - gy_(7) - 4, stroke="red", sw=1.3, r=3, a=idle_a, dash=(5, 5))
            cv.text("idle, waiting", gx_(4.5), gy_(2) + 8, 22, "red", "ital", "c", idle_a)
        # backfill view (beat 1)
        bf = appear(t, S.c(1, 0.2), 0.7) * G
        if bf > 0:
            block(cv, 6, 8, 0, 8, "yellow", "J1", bf, 0.25, dash=(7, 5))
            cv.text("reservation: planned start at t = 6", gx_(6) + 6, GY - 8, 19, "yellow", "ital", a=bf)
            # small jobs slide in
            for lab, h0, h1, n0, n1, c, ts in (("J2", 0, 5, 7, 8, "teal", 0.2), ("J3", 3, 5.5, 0, 4, "green", 0.45), ("J4", 6, 8, 0, 0, "orange", 9)):
                if lab == "J4":
                    continue
                aa = appear(t, S.f(1, ts), 0.8) * G
                slide = (1 - ease_out(prog(t, S.f(1, ts), 1.0))) * -140
                cv.save(); cv.translate(slide, 0)
                block(cv, h0, h1, n0, n1, c, lab, aa, 0.35)
                cv.restore()
            ok = appear(t, S.f(1, 0.7), 0.8) * G
            cv.text("J2, J3 fit before t = 6 → J1 isn't delayed", GX, GY + GH + 70, 24, "ink", "ital", a=ok)
            pl = appear(t, S.f(1, 0.85), 0.8) * G
            chip(cv, GX + GW - 150, GY - 52, "planned", "purple", pl, 17, "sans", 9)
        # right-side text
        rx = 1010
        note(cv, t, S.f(0, 0.6), rx, 330, 780, "", "Strict order: the top job needs everything, so nothing behind it may start.", 22)
        note(cv, t, S.f(1, 0.45), rx, 470, 780, "", "Slurm uses time limits as the estimate of when running jobs end, and plans around them.", 22)
        note(cv, t, S.f(1, 0.75), rx, 610, 780, "sinfo", "Nodes held for those future reservations are reported in state ‘planned’.", 22)
    # ---- beat 2-3 : sweep charts
    h2 = appear(t, S.c(2, -0.2), 0.9)
    if h2 > 0:
        tag_model(cv, 1420, 124, h2)
        cv.text("128 nodes · heavy-tailed jobs · 30 random workloads · 95% CI", 96, 210, 20, "dim", "ital", a=h2)
        # left chart: FIFO vs backfill mean wait
        a2 = appear(t, S.f(2, 0.25), 0.8) * h2 * (1 - 0.0)
        bx, by, bwid, bh = 150, 300, 360, 520
        cv.text("mean wait (hours)", bx, by - 24, 22, "ink", "ital", a=a2)
        cv.line(bx, by + bh, bx + bwid, by + bh, "rule", 1.1, a2)
        mx = 15.0
        for i, (nm, key, c) in enumerate((("FIFO", "fifo", "red"), ("backfill", "f=1", "green"))):
            m, ci = sw[key]["mean_wait_h"]
            g = ease_out(prog(t, S.f(2, 0.35 + i * 0.12), 1.2))
            x = bx + 40 + i * 170
            hh = m / mx * bh * g
            cv.rect(x, by + bh - hh, 110, hh, fill=c, r=3, a=0.55 * a2)
            cv.rect(x, by + bh - hh, 110, hh, stroke=c, sw=1.3, r=3, a=a2)
            cv.line(x + 55, by + bh - (m + ci) / mx * bh * g, x + 55, by + bh - max(m - ci, 0) / mx * bh * g, "ink", 1.4, a2)
            cv.text(f"{m:.1f}", x + 70, by + bh - hh + 8 if g > 0.3 else by + bh - 10, 27, "ink", "mono", "l", a2 * appear(t, S.f(2, 0.55 + i * 0.12), 0.5))
            cv.text(nm, x + 55, by + bh + 30, 20, "ink", "body", "c", a2)
        # right chart: padding factor f -> wait & forecast error
        c3 = appear(t, S.c(3, 0.0), 0.9) * h2
        px, py, pw, ph = 700, 300, 520, 520
        fs = ["1", "1.5", "2", "3", "5", "10"]
        xs = [px + 40 + i * (pw - 80) / 5 for i in range(6)]
        cv.text("users pad time limits by factor f", px, py - 24, 22, "ink", "ital", a=c3)
        cv.line(px, py + ph, px + pw, py + ph, "rule", 1.1, c3)
        for x, f in zip(xs, fs):
            cv.text("×" + f, x, py + ph + 28, 18, "dim", "sans", "c", c3)
        # mean wait (green) scale 0..2.5 ; forecast err (orange) scale 0..30
        g = ease_out(prog(t, S.f(3, 0.15), 1.6))
        w_pts = [(x, py + ph - sw["f=" + f]["mean_wait_h"][0] / 2.5 * ph * 0.45) for x, f in zip(xs, fs)]
        e_pts = [(x, py + ph - sw["f=" + f]["pred_abs_error_mean_h"][0] / 30 * ph) for x, f in zip(xs, fs)]
        cv.polyline(w_pts, "green", 3.2, c3, frac=g)
        cv.polyline(e_pts, "orange", 3.2, c3 * appear(t, S.f(3, 0.45), 0.6), frac=ease_out(prog(t, S.f(3, 0.5), 1.8)))
        la = appear(t, S.f(3, 0.3), 0.7) * c3
        cv.text("mean wait: 1.9 → 1.4 h", xs[0], w_pts[0][1] - 22, 21, "green", "ital", a=la)
        lb = appear(t, S.f(3, 0.62), 0.7) * c3
        cv.text("forecast error (|planned − actual start|)", px + 12, py + 28, 20, "orange", "ital", a=lb)
        for i in (2, 5):
            cv.circle(*e_pts[i], 6, fill="orange", a=lb)
            v = sw["f=" + fs[i]]["pred_abs_error_mean_h"][0]
            cv.text(f"{v:.1f} h", e_pts[i][0] - 10, e_pts[i][1] - 14, 22, "orange", "mono", "r", lb)
        note(cv, t, S.f(3, 0.82), 1290, 330, 490, "reading", "Throughput-like metrics barely move; what degrades is the promise.", 21)
    # ---- beat 4: caveats
    cv4 = appear(t, S.c(4, 0.1), 0.9)
    if cv4 > 0:
        cv.rect(1290, 560, 540, 340, fill="bg", a=1.0 * cv4)
        cv.text("toy ignores", 1310, 600, 24, "yellow", "ital", a=cv4)
        for i, w in enumerate(("killing jobs at their limit", "partial-node jobs", "how real users round estimates", "preemption, limits, topology")):
            cv.text("· " + w, 1310, 646 + i * 40, 22, "ink", "ital", a=appear(t, S.f(4, 0.25 + i * 0.12), 0.5) * cv4)
        cv.text("→ don't carry the numbers elsewhere", 1310, 840, 22, "red", "ital", a=appear(t, S.f(4, 0.8), 0.6) * cv4)
    # ---- beat 5: tunables
    c5 = appear(t, S.c(5, 0.0), 0.9)
    if c5 > 0:
        cv.rect(0, 160, 1920, 860, fill="bg", a=1.0 * c5)
        cv.text("backfill is tuned through SchedulerParameters", 110, 230, 30, "ink", "ital", a=c5)
        rows = [("bf_interval", "how often it runs", "30 s", "yellow"), ("bf_window", "how far ahead it plans", "1 day", "blue"),
                ("bf_resolution", "granularity of the plan", "60 s", "teal"), ("bf_max_job_test", "jobs examined per pass", "see man page", "orange")]
        for i, (k, d, v, c) in enumerate(rows):
            a = appear(t, S.f(5, 0.15 + i * 0.16), 0.6) * c5
            y = 330 + i * 120
            cv.rect(130, y, 1100, 86, fill=c, r=10, a=0.07 * a)
            cv.rect(130, y, 1100, 86, stroke=c, sw=1.3, r=10, a=a)
            cv.text(k, 160, y + 54, 29, c, "mono", a=a)
            cv.text(d, 560, y + 54, 26, "ink", "ital", a=a)
            cv.text("default: " + v, 1210, y + 54, 24, "ink", "mono", "r", a)
        cv.text("(the video's defaults are from the man page; check your version)", 130, 860, 19, "dim", "ital", a=appear(t, S.f(5, 0.8), 0.6) * c5)


# ================================================================================ S09 preemption
@scene("s09_preempt", "Preemption", ["preempt.html · slurm.conf(5): PreemptType, PreemptMode, GraceTime"])
def s09(cv, t, S):
    headline(cv, "Preemption: waiting isn't always acceptable", t, 0.3, "ink")
    # timeline lanes: 6 nodes; victim low-tier, preemptor high-tier
    gx, gy, gw, gh = 150, 300, 1000, 360
    nrows = 6

    def gxh(h):
        return gx + h / 10 * gw

    def gyn(n):
        return gy + n * gh / nrows
    cv.text("nodes", gx - 16, gy - 8, 17, "dim", "ital", "r", appear(t, 0.8, 0.7))
    for n in range(nrows + 1):
        cv.line(gx, gyn(n), gx + gw, gyn(n), "faint", 0.8, appear(t, 0.8, 0.7))
    # low-priority job occupying all nodes from t=0
    victim_end = 4.0
    a = appear(t, S.c(0, 0.3), 0.8)
    pre_t = S.f(0, 0.55)
    p = prog(t, pre_t, 0.0001) 
    fadecut = prog(t, S.f(1, 0.35), 0.7)
    cv.rect(gx + 2, gy + 2, (gxh(victim_end) - gx) - 4, gh - 4, fill="teal", r=4, a=0.28 * a * (1 - 0.6 * fadecut))
    cv.rect(gx + 2, gy + 2, (gxh(victim_end) - gx) - 4, gh - 4, stroke="teal", sw=1.5, r=4, a=a)
    cv.text("low tier / standby job", gxh(2), gy + gh / 2 + 7, 24, "teal", "ital", "c", a)
    # what the victim would have done: ghost 4-6, then resumes 8-10 after the preemptor
    cv.rect(gxh(4) + 2, gy + 2, gxh(6) - gxh(4) - 4, gh - 4, stroke="teal", sw=1.3, r=4, a=0.8 * a * appear(t, S.f(0, 0.45), 0.6) * (1 - fadecut), dash=(6, 5))
    rs = appear(t, S.f(1, 0.4), 0.8)
    if rs > 0:
        cv.rect(gxh(8) + 2, gy + 2, gxh(10) - gxh(8) - 4, gh - 4, stroke="teal", sw=1.5, r=4, a=rs, dash=(6, 5))
        cv.rect(gxh(8) + 2, gy + 2, gxh(10) - gxh(8) - 4, gh - 4, fill="teal", r=4, a=0.14 * rs)
        cv.text("resumes", gxh(9), gy + gh / 2 + 7, 22, "teal", "ital", "c", rs)
    # high-tier arrives
    hi = appear(t, S.f(0, 0.45), 0.8)
    if hi > 0:
        slide = (1 - ease_out(prog(t, S.f(0, 0.45), 1.0))) * -80
        cv.save(); cv.translate(0, slide)
        cv.rect(gxh(4) + 2, gy + 2, gxh(8) - gxh(4) - 4, gh - 4, fill="orange", r=4, a=0.28 * hi)
        cv.rect(gxh(4) + 2, gy + 2, gxh(8) - gxh(4) - 4, gh - 4, stroke="orange", sw=1.5, r=4, a=hi)
        cv.text("higher tier arrives", gxh(6), gy + gh / 2 + 7, 24, "orange", "ital", "c", hi)
        cv.restore()
    # two routes in beat 0
    r0 = appear(t, S.f(0, 0.2), 0.7) * (1 - appear(t, S.c(1, 0.0), 0.7))
    if r0 > 0:
        for i, (nm, d, c) in enumerate((("PreemptType=preempt/partition_prio", "higher PriorityTier displaces lower", "purple"),
                                         ("PreemptType=preempt/qos", "QOS rules in the database say who may preempt whom", "orange"))):
            y = 740 + i * 90
            cv.text(nm, 150, y, 22, c, "mono", a=r0 * appear(t, S.f(0, 0.5 + i * 0.2), 0.6))
            cv.text(d, 150, y + 30, 20, "dim", "ital", a=r0 * appear(t, S.f(0, 0.55 + i * 0.2), 0.6))
    # beat 1: modes
    m1 = appear(t, S.c(1, 0.0), 0.8)
    if m1 > 0:
        modes = [("CANCEL", "the job ends", "red"), ("REQUEUE", "back in the queue, runs again", "yellow"), ("SUSPEND", "paused in memory, resumed later", "blue")]
        cv.text("what happens to the victim (PreemptMode)", 1240, 330, 24, "ink", "ital", a=m1)
        for i, (nm, d, c) in enumerate(modes):
            a = appear(t, S.f(1, 0.12 + i * 0.14), 0.6) * m1
            y = 370 + i * 110
            cv.rect(1240, y, 560, 88, fill=c, r=9, a=0.08 * a)
            cv.rect(1240, y, 560, 88, stroke=c, sw=1.3, r=9, a=a)
            cv.text(nm, 1264, y + 38, 26, c, "mono", a=a)
            cv.text(d, 1264, y + 70, 20, "ink", "ital", a=a)
        # grace time
        gt = appear(t, S.f(1, 0.55), 0.8)
        if gt > 0:
            cv.line(gxh(3.2), gy + gh + 40, gxh(4), gy + gh + 40, "yellow", 3, gt)
            cv.text("GraceTime: time to checkpoint", gxh(3.2), gy + gh + 74, 22, "yellow", "ital", a=gt)
            cv.text("signal → grace → kill", gxh(3.2), gy + gh + 102, 19, "dim", "ital", a=gt)
        sb = appear(t, S.f(1, 0.8), 0.8)
        cv.text("→ cheap, interruptible standby queues", 1240, 760, 27, "yellow", "ital", a=sb)
