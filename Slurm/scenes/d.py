"""Scenes 10-13: placement, topology, typical setups, the HPC universe."""
import math
from engine import *
from scenes.common import *

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


# ================================================================================ S10 placement
@scene("s10_place", "Placement", ["cons_tres · gres · cgroup.conf · slurm.conf(5): SelectType, TRESBillingWeights"])
def s10(cv, t, S):
    headline(cv, "Where a job lands", t, 0.3, "ink")
    nx, ny, nw, nh = 110, 215, 640, 560
    A = appear(t, 0.8, 0.8)
    cv.rect(nx, ny, nw, nh, stroke="blue", sw=1.5, r=12, a=A)
    cv.text("one node", nx + 18, ny - 12, 21, "dim", "ital", a=A)
    # 2 sockets x 16 cores
    jobcols = ["purple", "orange", "teal", "yellow"]
    # allocation of cores to jobs (index per core, -1 free)
    alloc = [0] * 6 + [1] * 4 + [2] * 3 + [-1] * 3 + [3] * 8 + [-1] * 8
    for s_ in range(2):
        sx = nx + 24 + s_ * 300
        cv.rect(sx, ny + 40, 270, 190, stroke="dim", sw=1, r=8, a=A)
        cv.text(f"socket {s_}", sx + 8, ny + 36, 15, "dim", "sans", a=A)
        for c_ in range(16):
            idx = s_ * 16 + c_
            j = alloc[idx]
            ta = S.c(0, 0.5 + (j if j >= 0 else 0) * 0.5)
            a = appear(t, ta, 0.5)
            px, py = sx + 12 + (c_ % 8) * 31, ny + 58 + (c_ // 8) * 40
            cv.rect(px, py, 25, 30, stroke="faint", sw=1, r=3, a=A)
            if j >= 0:
                cv.rect(px, py, 25, 30, fill=jobcols[j], r=3, a=0.65 * a)
    # memory bar
    cv.text("memory", nx + 24, ny + 262, 17, "dim", "sans", a=A)
    segs = [(0.30, "purple"), (0.18, "orange"), (0.22, "teal"), (0.20, "yellow")]
    x = nx + 24
    for i, (f, c) in enumerate(segs):
        w = f * 580 * appear(t, S.c(0, 0.6 + i * 0.5), 0.6)
        cv.rect(x, ny + 272, w, 24, fill=c, a=0.6)
        x += f * 580
    cv.rect(nx + 24, ny + 272, 580, 24, stroke="rule", sw=1, a=A)
    k0 = 1 - appear(t, S.c(1, 0.0), 0.5)
    cv.text("four jobs share one node (cons_tres default per the man page)", nx + 24, ny + 330, 20, "ink", "ital", a=appear(t, S.f(0, 0.8), 0.7) * k0)
    cv.text("whole-node mode exists per partition (ExclusiveUser / OverSubscribe=EXCLUSIVE)", nx + 24, ny + 358, 17, "dim", "ital", a=appear(t, S.f(0, 0.9), 0.7) * k0)
    # GRES (beat 1)
    g1 = appear(t, S.c(1, 0.1), 0.8)
    if g1 > 0:
        for i in range(4):
            gxx = nx + 24 + i * 150
            a = appear(t, S.f(1, 0.1 + i * 0.1), 0.6)
            cv.rect(gxx, ny + 390, 130, 70, fill="green", r=7, a=0.15 * a)
            cv.rect(gxx, ny + 390, 130, 70, stroke="green", sw=1.4, r=7, a=a)
            cv.text(f"gpu{i}", gxx + 65, ny + 432, 22, "ink", "mono", "c", a)
            # affinity line to socket
            sx = nx + 24 + (0 if i < 2 else 300) + 135
            aa = appear(t, S.f(1, 0.4 + i * 0.06), 0.6)
            cv.line(gxx + 65, ny + 390, sx, ny + 230, "green", 1.1, aa * 0.7, dash=(4, 4))
        cv.text("GRES: name · type · device files · close cores", nx + 24, ny + 500, 20, "green", "ital", a=appear(t, S.f(1, 0.55), 0.7))
        cv.text("GPU count is still configured (autodetect fills the rest)", nx + 24, ny + 528, 17, "dim", "ital", a=appear(t, S.f(1, 0.7), 0.7))
        # request syntax as concept, right side
        rx = 830
        cv.text("jobs ask by count", rx, 280, 26, "ink", "ital", a=appear(t, S.f(1, 0.5), 0.7))
        for i, w in enumerate(("per node", "per socket", "per task", "per job")):
            chip(cv, rx + (i % 2) * 220, 340 + (i // 2) * 60, w, "green", appear(t, S.f(1, 0.6 + i * 0.07), 0.5), 21, "sans", 12)
    # cgroups (beat 2)
    c2 = appear(t, S.c(2, 0.1), 0.8)
    if c2 > 0:
        rx = 830
        cv.text("declared ≠ enforced", rx, 540, 28, "ink", "ital", a=c2)
        items = [("task/cgroup", "confines the job to its cores, memory, devices", "teal", 0.3), ("proctrack/cgroup", "tracks every process the job spawns", "orange", 0.6)]
        for i, (p, d, c, f) in enumerate(items):
            a = appear(t, S.f(2, f), 0.6)
            y = 580 + i * 96
            cv.rect(rx, y, 920, 76, fill=c, r=9, a=0.08 * a)
            cv.rect(rx, y, 920, 76, stroke=c, sw=1.3, r=9, a=a)
            cv.text(p, rx + 20, y + 48, 25, c, "mono", a=a)
            cv.text(d, rx + 330, y + 48, 21, "ink", "ital", a=a)
        # dashed cgroup walls around job 0 cores
        wa = appear(t, S.f(2, 0.35), 0.8)
        cv.rect(nx + 32, ny + 52, 6 * 31 + 4, 36, stroke="purple", sw=2.2, r=6, a=wa, dash=(6, 4))
    # billing (beat 3)
    b3 = appear(t, S.c(3, 0.1), 0.8)
    if b3 > 0:
        cv.rect(0, 160, 1920, 860, fill="bg", a=1.0 * b3)
        cv.text("TRESBillingWeights → one currency", 110, 230, 32, "ink", "ital", a=b3)
        tag(cv, 1300, 226, "ILLUSTRATIVE WEIGHTS", "yellow", b3)
        wts = [("cpu", 1.0, 4, "blue"), ("mem (per GiB)", 0.25, 64, "teal"), ("gpu", 10.0, 1, "green")]
        y = 330
        tot = 0
        for i, (nm, w, q, c) in enumerate(wts):
            a = appear(t, S.f(3, 0.15 + i * 0.16), 0.6) * b3
            cv.text(nm, 160, y + i * 110, 28, c, "mono", a=a)
            cv.text(f"× {w:g}", 560, y + i * 110, 28, "ink", "mono", a=a)
            cv.text(f"× {q}", 760, y + i * 110, 28, "ink", "mono", a=a)
            cv.text(f"= {w * q:g}", 960, y + i * 110, 28, "yellow", "mono", a=a)
            tot += w * q
        ta = appear(t, S.f(3, 0.65), 0.8) * b3
        cv.line(160, y + 3 * 110 - 60, 1100, y + 3 * 110 - 60, "rule", 1.3, ta)
        cv.text(f"job billing  =  {tot:g} per hour", 160, y + 3 * 110 + 4, 34, "yellow", "bold", a=ta)
        cv.text("fair-share and limits charge in this unit", 160, y + 3 * 110 + 56, 24, "dim", "ital", a=appear(t, S.f(3, 0.82), 0.7) * b3)
        cv.text("4 CPUs · 64 GiB · 1 GPU", 1180, y + 12, 24, "dim", "ital", a=ta)


# ================================================================================ S11 topology
@scene("s11_topology", "Topology", ["topology.html · topology.conf · sbatch(1): --switches"])
def s11(cv, t, S):
    headline(cv, "Placement has geometry", t, 0.3, "ink")
    a0 = appear(t, 0.8, 0.9)
    # switch tree: 1 spine, 4 leaf, 4 nodes each
    sp = (700, 290)
    leaves = [(240 + i * 300, 500) for i in range(4)]
    cv.text("tightly coupled jobs talk constantly", 1120, 260, 24, "ink", "ital", a=appear(t, S.f(0, 0.05), 0.7))
    sa = appear(t, S.f(0, 0.08), 0.8)
    cv.rect(sp[0] - 80, sp[1] - 30, 160, 60, fill="purple", r=8, a=0.14 * sa)
    cv.rect(sp[0] - 80, sp[1] - 30, 160, 60, stroke="purple", sw=1.4, r=8, a=sa)
    cv.text("top switch", sp[0], sp[1] + 8, 21, "ink", "mono", "c", sa)
    node_pos = {}
    for i, (lx, ly) in enumerate(leaves):
        a = appear(t, S.f(0, 0.12 + i * 0.05), 0.7)
        cv.line(sp[0], sp[1] + 30, lx, ly - 30, "purple", 1.4, a)
        cv.rect(lx - 70, ly - 30, 140, 60, fill="blue", r=8, a=0.12 * a)
        cv.rect(lx - 70, ly - 30, 140, 60, stroke="blue", sw=1.4, r=8, a=a)
        cv.text(f"leaf {i}", lx, ly + 8, 21, "ink", "mono", "c", a)
        for k in range(4):
            nx_, ny_ = lx - 105 + k * 70, 690
            node_pos[(i, k)] = (nx_, ny_)
            cv.line(lx, ly + 30, nx_, ny_ - 20, "faint", 1, a)
            cv.rect(nx_ - 24, ny_ - 20, 48, 40, stroke="dim", sw=1.1, r=5, a=a)
    # job placements: spread (bad) vs packed (good)
    spread = appear(t, S.f(0, 0.45), 0.7) * (1 - appear(t, S.f(0, 0.62), 0.6))
    packed = appear(t, S.f(0, 0.65), 0.8)
    if spread > 0:
        for (i, k) in ((0, 1), (1, 2), (2, 0), (3, 3)):
            x, y = node_pos[(i, k)]
            cv.rect(x - 22, y - 18, 44, 36, fill="red", r=4, a=0.55 * spread)
        for i in range(4):
            cv.line(leaves[i][0], leaves[i][1] - 30, sp[0], sp[1] + 30, "red", 3.2, spread * 0.9)
        cv.text("crosses the top switch → contention", 100, 780, 22, "red", "ital", a=spread)
    if packed > 0:
        for k in range(4):
            x, y = node_pos[(1, k)]
            cv.rect(x - 22, y - 18, 44, 36, fill="green", r=4, a=0.6 * packed)
        cv.rect(leaves[1][0] - 128, 628, 256, 90, stroke="green", sw=2, r=8, a=packed, dash=(6, 4))
        cv.text("one leaf switch → fewer hops", 100, 780, 22, "green", "ital", a=packed)
    # algorithm text
    t1 = appear(t, S.f(0, 0.72), 0.7)
    cv.text("find the lowest switch that can host the job → then fill it best-fit", 100, 850, 26, "ink", "ital", a=t1)
    uf = appear(t, S.f(0, 0.85), 0.8)
    chip(cv, 100, 920, "--switches=1@60", "yellow", uf, 24, "mono", 14)
    cv.text("at most 1 leaf switch, waiting up to 60 min for it", 420, 916, 21, "dim", "ital", a=uf)
    note(cv, t, S.f(0, 0.92), 1190, 700, 600, "docs advice", "Describe leaf switches plus one top level, not every physical link.", 21)


# ================================================================================ S12 setups
@scene("s12_setups", "Typical setups", ["slurm.conf(5) · power_save · slurm.schedmd.com (quickstart_admin); all three configurations are illustrative, not site data"])
def s12(cv, t, S):
    headline(cv, "Three typical shapes", t, 0.3, "ink")
    cols = [("Lab", "blue", 96), ("Campus", "orange", 696), ("Cloud", "teal", 1296)]
    tag(cv, 1560, 124, "ILLUSTRATIVE", "yellow", appear(t, 0.8, 0.7))
    PWc, PHc = 530, 700
    for i, (nm, c, x) in enumerate(cols):
        a = appear(t, S.c(i, 0.0), 0.8)
        if a <= 0:
            continue
        y = 190
        cv.rect(x, y, PWc, PHc, stroke="faint", sw=1, r=10, a=a)
        cv.text(nm, x + 20, y + 44, 32, c, "bold", a=a)
        if i == 0:
            cv.text("slurm.conf, one file", x + 20, y + 80, 20, "dim", "ital", a=a)
            for k in range(6):
                cv.rect(x + 30 + k * 82, y + 130, 66, 56, stroke="blue", sw=1.3, r=6, a=appear(t, S.f(i, 0.15 + k * 0.05), 0.5) * a)
            cv.rect(x + 30, y + 130, 6 * 82 - 16, 56, stroke="ink", sw=1.0, r=6, a=appear(t, S.f(i, 0.5), 0.6) * a, dash=(5, 4))
            cv.text("one partition", x + 30, y + 220, 22, "ink", "ital", a=appear(t, S.f(i, 0.5), 0.6) * a)
            cv.text("scheduler: first-in, first-out", x + 30, y + 256, 20, "dim", "ital", a=appear(t, S.f(i, 0.65), 0.6) * a)
            cv.text("no accounting database", x + 30, y + 288, 20, "dim", "ital", a=appear(t, S.f(i, 0.75), 0.6) * a)
            cv.text("a good place to start", x + 30, y + 420, 26, "yellow", "ital", a=appear(t, S.f(i, 0.9), 0.7) * a)
        elif i == 1:
            parts = [("cpu", "blue"), ("bigmem", "purple"), ("gpu", "green"), ("short", "yellow")]
            for k, (pn, pc) in enumerate(parts):
                aa = appear(t, S.f(i, 0.10 + k * 0.07), 0.5) * a
                yy = y + 90 + k * 54
                cv.rect(x + 30, yy, 200, 40, fill=pc, r=6, a=0.14 * aa)
                cv.rect(x + 30, yy, 200, 40, stroke=pc, sw=1.2, r=6, a=aa)
                cv.text(pn, x + 130, yy + 28, 21, "ink", "mono", "c", aa)
            cv.text("partitions by hardware class", x + 250, y + 150, 19, "dim", "ital", a=appear(t, S.f(i, 0.3), 0.6) * a)
            cylinder(cv, x + 30, y + 330, 140, 90, "teal", appear(t, S.f(i, 0.35), 0.6) * a, "slurmdbd")
            for k, w in enumerate(("accounts per research group", "QOS: normal · urgent · standby", "fair-share weights", "cgroup plugins enforce it")):
                cv.text("· " + w, x + 30, y + 470 + k * 38, 21, "ink", "ital", a=appear(t, S.f(i, 0.45 + k * 0.12), 0.6) * a)
        else:
            cv.text("power_save hooks", x + 20, y + 80, 20, "dim", "ital", a=a)
            # nodes booting / terminating
            for k in range(8):
                ph = prog(t, S.f(i, 0.2 + k * 0.03), 0.8)
                down = prog(t, S.f(i, 0.65 + k * 0.02), 0.8)
                px, py = x + 34 + (k % 4) * 118, y + 130 + (k // 4) * 80
                on = ph * (1 - down)
                cv.rect(px, py, 96, 56, stroke="teal", sw=1.2, r=6, a=a * (0.3 + 0.7 * on), dash=None if on > 0.5 else (4, 4))
                cv.rect(px, py, 96, 56, fill="teal", r=6, a=a * 0.35 * on)
            cv.text("job waiting → ResumeProgram boots nodes", x + 30, y + 330, 20, "ink", "ital", a=appear(t, S.f(i, 0.28), 0.6) * a)
            cv.text("idle → SuspendProgram tears them down", x + 30, y + 366, 20, "ink", "ital", a=appear(t, S.f(i, 0.68), 0.6) * a)
            cv.text("your scripts do the cloud API calls", x + 30, y + 430, 22, "yellow", "ital", a=appear(t, S.f(i, 0.85), 0.7) * a)
    # beat 3: order of work
    o = appear(t, S.c(3, 0.2), 0.9)
    if o > 0:
        cv.rect(0, 160, 1920, 860, fill="bg", a=1.0 * o)
        cv.text("whatever the shape, the order of work is the same", 110, 240, 32, "ink", "ital", a=o)
        steps = [("nodes", "blue"), ("partitions", "teal"), ("accounts & limits", "purple"), ("priority", "yellow"), ("enforcement", "orange")]
        x = 130
        for k, (nm, c) in enumerate(steps):
            a = appear(t, S.f(3, 0.12 + k * 0.15), 0.6) * o
            w = 300
            cv.rect(x, 440, w, 150, fill=c, r=12, a=0.10 * a)
            cv.rect(x, 440, w, 150, stroke=c, sw=1.5, r=12, a=a)
            cv.text(str(k + 1), x + 32, 490, 30, c, "bold", "c", a)
            cv.text(nm, x + w / 2, 535, 27, "ink", "body", "c", a)
            if k < 4:
                cv.arrow(x + w + 4, 515, x + w + 28, 515, "rule", 1.6, a, head=10)
            x += w + 34


# ================================================================================ S13 universe
@scene("s13_universe", "The HPC universe", ["slurm.schedmd.com (SchedMD docs & source) · Yoo, Jette, Grondona, JSSPP 2003 · Jette & Grondona 2003 · results/backfill_sweep.json (mine)"])
def s13(cv, t, S):
    headline(cv, "Slurm in the larger stack", t, 0.3, "ink")
    # stack layers
    layers = [("your program", "MPI · PyTorch · simulation codes", "purple"), ("Slurm", "time and ownership of shared hardware", "yellow"),
              ("Linux", "cgroups · kernel · drivers", "blue"), ("hardware", "CPUs · GPUs · memory · interconnect", "teal")]
    x, w = 130, 900
    for i, (nm, d, c) in enumerate(layers):
        a = appear(t, S.f(0, 0.12 + i * 0.18), 0.7)
        slide = (1 - ease_out(prog(t, S.f(0, 0.12 + i * 0.18), 0.9))) * 30
        y = 260 + i * 130 - slide
        glow = 1.0 if i == 1 else 0.0
        if glow:
            cv.glow(x + w / 2, y + 48, 420, "yellow", 0.12 * a)
        cv.rect(x, y, w, 100, fill=c, r=10, a=0.11 * a)
        cv.rect(x, y, w, 100, stroke=c, sw=2.2 if i == 1 else 1.4, r=10, a=a)
        cv.text(nm, x + 28, y + 46, 32, "ink", "bold", a=a)
        cv.text(d, x + 28, y + 80, 21, "dim", "ital", a=a)
    # side: other worlds
    s1 = appear(t, S.c(1, 0.1), 0.8)
    if s1 > 0:
        cv.text("not Slurm's job:", 1130, 300, 26, "ink", "ital", a=s1)
        for i, wd in enumerate(("moving your data", "tuning the file system", "writing your code")):
            cv.text("· " + wd, 1130, 350 + i * 44, 24, "dim", "ital", a=appear(t, S.f(1, 0.15 + i * 0.12), 0.6) * s1)
        cv.text("Slurm owns time and ownership", 1130, 540, 27, "yellow", "ital", a=appear(t, S.f(1, 0.45), 0.7) * s1)
        cv.text("docs report validating 500 simple batch jobs / s, sustained", 1130, 600, 22, "ink", "ital", a=appear(t, S.f(1, 0.7), 0.7) * s1)
        tag(cv, 1130, 650, "VENDOR CLAIM", "yellow", appear(t, S.f(1, 0.7), 0.7) * s1)
    # beat 2: four questions recap
    q = appear(t, S.c(2, -0.2), 0.9)
    if q > 0:
        cv.rect(0, 160, 1920, 860, fill="bg", a=1.0 * q)
        qs = [("1 · Who may run?", "accounts · QOS · limits", "blue"), ("2 · Who goes first?", "priority · fair-share · backfill · preemption", "yellow"),
              ("3 · Where?", "nodes · consumable resources · GPUs · topology", "green"), ("4 · How?", "daemons · launch path · cgroups · accounting", "orange")]
        for i, (a_, b_, c) in enumerate(qs):
            a = appear(t, S.f(2, 0.12 + i * 0.2), 0.7) * q
            y = 250 + i * 150
            cv.rect(130, y, 1660, 118, fill=c, r=12, a=0.08 * a)
            cv.rect(130, y, 1660, 118, stroke=c, sw=1.5, r=12, a=a)
            cv.text(a_, 170, y + 52, 36, c, "bold", a=a)
            cv.text(b_, 170, y + 92, 25, "ink", "ital", a=a)
    # beat 3: sources & caveats card
    e = appear(t, S.c(3, -0.1), 0.9)
    if e > 0:
        cv.rect(0, 160, 1920, 860, fill="bg", a=1.0 * e)
        cv.text("Sources and caveats", 130, 240, 40, "ink", "ital", a=e)
        src = ["SchedMD documentation and source tree (slurm.schedmd.com)", "Yoo, Jette, Grondona — SLURM: Simple Linux Utility for Resource Management, JSSPP 2003",
               "Jette & Grondona — SLURM: Simple Linux Utility for Resource Management, ClusterWorld 2003 (LLNL report)",
               "Mu'alem & Feitelson — Utilization, predictability, workloads, and user runtime estimates, IEEE TPDS 12(6), 2001"]
        for i, s_ in enumerate(src):
            cv.text("· " + s_, 130, 320 + i * 44, 22, "ink", "body", a=appear(t, S.f(3, 0.1 + i * 0.08), 0.6) * e)
        tag(cv, 130, 560, "MY TOY MODEL", "yellow", appear(t, S.f(3, 0.45), 0.6) * e)
        cv.text("backfill simulation: my code, marked wherever it appears", 330, 560, 22, "ink", "ital", a=appear(t, S.f(3, 0.45), 0.6) * e)
        cv.text("config snippets, weights and share values are illustrative", 130, 620, 22, "ink", "ital", a=appear(t, S.f(3, 0.55), 0.6) * e)
        cv.text("defaults can change between versions; check your version's man page", 130, 664, 22, "ink", "ital", a=appear(t, S.f(3, 0.65), 0.6) * e)
        cv.text("the notes file lists what I could not verify", 130, 740, 28, "yellow", "ital", a=appear(t, S.f(3, 0.8), 0.7) * e)
