"""Scenes 0-2: title, the four questions, origins."""
import math, random
from engine import *
from scenes.common import *

SCENES = {}


def scene(sid, title="", sources=None):
    def deco(fn):
        SCENES[sid] = dict(title=title, sources=sources or [], draw=fn)
        return fn
    return deco


# ---------------------------------------------------------------------------------- packing helper
def first_fit(blocks, cols, rows):
    """Greedy left-to-right packing of (w,h) blocks into a cols x rows grid -> [(x,y,w,h)]."""
    occ = [[False] * cols for _ in range(rows)]
    out = []
    for (w, h) in blocks:
        placed = None
        for x in range(0, cols - w + 1):
            for y in range(0, rows - h + 1):
                if all(not occ[y + j][x + i] for j in range(h) for i in range(w)):
                    placed = (x, y)
                    break
            if placed:
                break
        if placed is None:
            continue
        x, y = placed
        for j in range(h):
            for i in range(w):
                occ[y + j][x + i] = True
        out.append((x, y, w, h))
    return out


_rng = random.Random(7)
_TITLE_BLOCKS = first_fit([(_rng.choice([3, 4, 5, 6, 8, 10]), _rng.choice([1, 2, 2, 3, 4, 6])) for _ in range(90)], 48, 24)


# =================================================================================== S00 title
@scene("s00_title", "Slurm", ["slurm.schedmd.com", "JSSPP 2003"])
def s00(cv, t, S):
    cell = 40
    ox, oy = 0, 60
    for k, (x, y, w, h) in enumerate(_TITLE_BLOCKS):
        ts = 0.3 + k * 0.19
        a = appear(t, ts, 0.5)
        if a <= 0:
            continue
        c = JOBCOL[(k * 5 + x) % len(JOBCOL)]
        sl = (1 - ease_out(prog(t, ts, 0.7))) * 40
        cv.rect(ox + x * cell + 2 - sl, oy + y * cell + 2, w * cell - 4, h * cell - 4, fill=c, r=5, a=0.20 * a)
        cv.rect(ox + x * cell + 2 - sl, oy + y * cell + 2, w * cell - 4, h * cell - 4, stroke=c, sw=1.1, r=5, a=0.45 * a)
    # soft vignette so the title reads
    cv.glow(960, 520, 640, "bg", 0.96)
    a = appear(t, 0.7, 1.0)
    cv.text("Slurm", 960, 535 + (1 - a) * 14, 190, "ink", "bold", "c", a)
    a2 = appear(t, 2.0, 0.9)
    cv.text("how a supercomputer decides who runs next", 960, 612, 45, "blue", "ital", "c", a2)
    a3 = appear(t, 3.4, 0.9)
    cv.text("A   F I R S T - P R I N C I P L E S   T O U R", 960, 690, 21, "dim", "sans", "c", a3)
    a4 = appear(t, 5.0, 0.9)
    cv.text("job and resource scheduling for HPC", 960, 735, 25, "dim", "ital", "c", a4)


# =================================================================================== S01 the plane
_PLANE_JOBS = None


def _plane_jobs():
    global _PLANE_JOBS
    if _PLANE_JOBS is None:
        r = random.Random(11)
        bl = [(r.choice([3, 4, 5, 6, 8]), r.choice([2, 3, 4, 5, 6, 8])) for _ in range(40)]
        pk = first_fit(bl, 26, 20)
        owners = ["blue", "orange", "teal"]
        _PLANE_JOBS = [(x, y, w, h, owners[(i * 7 + x + y) % 3]) for i, (x, y, w, h) in enumerate(pk)]
    return _PLANE_JOBS


def draw_plane(cv, px, py, pw, ph, t, t_jobs0, a=1.0, label_job=None, show_labels=True, per=0.26, tfade=None):
    cols, rows = 26, 20
    cw, rh = pw / cols, ph / rows
    # axes (hairlines, Tufte)
    cv.line(px, py + ph, px + pw, py + ph, "rule", 1.2, a)
    cv.line(px, py, px, py + ph, "rule", 1.2, a)
    if show_labels:
        cv.text("time", px + pw, py + ph + 36, 21, "dim", "ital", "r", a)
        cv.text_rot("nodes", px - 30, py + ph / 2, -90, 21, "dim", "ital", "c", a)
    for k, (x, y, w, h, c) in enumerate(_plane_jobs()):
        ts = t_jobs0 + k * per
        aa = appear(t, ts, 0.45) * a
        if aa <= 0:
            continue
        sx = ease_out(prog(t, ts, 0.5))
        cv.rect(px + x * cw + 1.5, py + y * rh + 1.5, (w * cw - 3) * sx, h * rh - 3, fill=c, r=3, a=0.30 * aa)
        cv.rect(px + x * cw + 1.5, py + y * rh + 1.5, (w * cw - 3) * sx, h * rh - 3, stroke=c, sw=1.2, r=3, a=0.9 * aa)


@scene("s01_plane", "The cluster as a plane", ["Slurm overview (slurm.schedmd.com/overview.html)"])
def s01(cv, t, S):
    headline(cv, "A cluster is a plane of nodes and time", t)
    # plane geometry: starts large-left, then shrinks to make room for the four questions
    k = ease_io(prog(t, S.c(2, -0.4), 1.2))
    px = lerp(170, 120, k)
    py = lerp(230, 300, k)
    pw = lerp(1080, 520, k)
    ph = lerp(600, 310, k)
    draw_plane(cv, px, py, pw, ph, t, S.c(0, 1.2), a=1.0 - 0.35 * k, per=0.30)

    # beat 0: label one job directly
    jobs = _plane_jobs()
    j = jobs[5]
    cols, rows = 26, 20
    cw, rh = pw / cols, ph / rows
    a = appear(t, S.f(0, 0.55), 0.6) * (1 - k)
    if a > 0:
        jx, jy = px + (j[0] + j[2] / 2) * cw, py + j[1] * rh
        cv.line(jx, jy, jx + 70, jy - 60, "ink", 1, a * 0.8)
        cv.rect(jx + 66, jy - 94, 300, 62, fill="bg", r=4, a=0.92 * a)
        cv.text("one job: 4 nodes for 3 hours", jx + 76, jy - 66, 22, "ink", "ital", "l", a)
        cv.text("a rectangle", jx + 76, jy - 40, 19, "dim", "ital", "l", a)

    # beat 1: who is behind the rectangles
    a1 = appear(t, S.c(1, 0.2), 0.6) * (1 - k)
    if a1 > 0:
        lx, ly = 1330, 300
        cv.text("every rectangle has an owner", lx, ly, 25, "ink", "ital", a=a1)
        for i, (nm, c) in enumerate((("lab A", "blue"), ("lab B", "orange"), ("lab C", "teal"))):
            aa = stagger(t, S.c(1, 0.8), i, 0.25) * (1 - k)
            cv.rect(lx, ly + 34 + i * 38, 22, 22, fill=c, r=3, a=0.35 * aa)
            cv.rect(lx, ly + 34 + i * 38, 22, 22, stroke=c, sw=1.2, r=3, a=aa)
            cv.text(nm, lx + 36, ly + 52 + i * 38, 22, "ink", "body", a=aa)
        for i, w in enumerate(("budgets", "deadlines", "opinions about fairness")):
            aa = stagger(t, S.f(1, 0.45), i, 0.55, 0.6) * (1 - k)
            cv.line(lx - 8, ly + 190 + i * 44 - 6, lx - 8 - 70, ly + 190 + i * 44 - 6, "yellow", 1.4, aa)
            cv.arrow(lx - 8 - 70, ly + 190 + i * 44 - 6, lx - 8 - 130, ly + 130 + i * 24, "yellow", 1.0, aa * 0.0)
            cv.text(w, lx, ly + 190 + i * 44, 26, "yellow", "ital", a=aa)

    # beat 2: the four questions
    cards = [("1", "Who is allowed to run?", "accounts · QOS · limits", "blue", 0.22),
             ("2", "Who goes first?", "priority · fair-share · backfill", "yellow", 0.42),
             ("3", "Where does the job land?", "nodes · GPUs · topology", "green", 0.64),
             ("4", "How is it run?", "daemons · launch · cgroups · accounting", "orange", 0.80)]
    x0, y0, cw2, chh = 760, 250, 480, 190
    for i, (n, q, sub, c, fr) in enumerate(cards):
        a = appear(t, S.f(2, fr - 0.12), 0.7)
        if a <= 0:
            continue
        cx = x0 + (i % 2) * (cw2 + 40)
        cy = y0 + (i // 2) * (chh + 40) + (1 - a) * 14
        cv.rect(cx, cy, cw2, chh, fill=c, r=12, a=0.08 * a)
        cv.rect(cx, cy, cw2, chh, stroke=c, sw=1.6, r=12, a=0.9 * a)
        cv.circle(cx + 46, cy + 52, 25, stroke=c, sw=2, a=a)
        cv.text(n, cx + 46, cy + 61, 28, c, "bold", "c", a)
        cv.text(q, cx + 90, cy + 62, 31, "ink", "body", a=a)
        cv.text(sub, cx + 34, cy + 128, 22, c, "ital", a=a)
    a = appear(t, S.f(2, 0.86), 0.8)
    cv.text("everything in Slurm answers one of these", 1280, 880, 28, "dim", "ital", "c", a)


# =================================================================================== S02 origins
Y0, Y1 = 1985, 2027
TX0, TX1, TY = 150, 1770, 300


def ty(year):
    return TX0 + (year - Y0) / (Y1 - Y0) * (TX1 - TX0)


def ev(cv, t, ts, year, text, sub=None, up=True, h=70, color="ink", align="l", dx=0, size=23):
    a = appear(t, ts, 0.6)
    if a <= 0:
        return
    x = ty(year)
    y = TY - h if up else TY + h
    cv.circle(x, TY, 6, fill=color, a=a)
    cv.line(x, TY + (-7 if up else 7), x, y + (6 if up else -6) * (1 if up else -1) * 0, color, 1.1, a * 0.8, frac=ease_out(prog(t, ts, 0.5)))
    tx = x + dx
    yy = y - 12 if up else y + 26
    cv.text(text, tx, yy, size, color, "body", align, a)
    if sub:
        cv.text(sub, tx, yy + 25, size * 0.78, "dim", "ital", align, a)


@scene("s02_history", "Origins", ["Yoo, Jette & Grondona, JSSPP 2003 (LNCS 2862)", "Jette & Grondona, ClusterWorld 2003",
                                  "SchedMD FAQ", "Wikipedia (HTCondor, PBS, Platform LSF)", "NVIDIA blog, 15 Dec 2025"])
def s02(cv, t, S):
    headline(cv, "Why another scheduler?", t)
    # timeline axis
    a = appear(t, 0.4, 0.8)
    cv.line(TX0, TY, TX1, TY, "rule", 1.2, a, frac=ease_out(prog(t, 0.4, 1.4)))
    for yr in range(1985, 2030, 5):
        cv.line(ty(yr), TY, ty(yr), TY + 7, "rule", 1, a)
        cv.text(str(yr), ty(yr), TY + 28, 16, "dim", "sans", "c", a * 0.9)

    # beat 0
    ev(cv, t, S.f(0, 0.18), 1988, "Condor", "Wisconsin", True, 70, "ink", "l", -10)
    ev(cv, t, S.f(0, 0.42), 1991, "PBS", "NASA contract", False, 70, "ink", "l", -10)
    for i, (nm, sub) in enumerate((("LSF", "from the Utopia project, Toronto"), ("LoadLeveler", "IBM"))):
        aa = appear(t, S.f(0, 0.62 + i * 0.16), 0.6)
        cv.text(nm, 200 + i * 520, 452, 22, "ink", "body", a=aa)
        cv.text(sub, 200 + i * 520 + text_w(nm, 22) + 12, 452, 18, "dim", "ital", a=aa)

    # beat 1: Slurm appears
    ev(cv, t, S.f(1, 0.04), 2002, "Slurm  at LLNL", None, True, 70, "blue", "r", 12, 27)
    a1 = appear(t, S.f(1, 0.30), 0.7)
    b0 = S.c(1)
    lower_a = appear(t, S.c(1, 0.2), 0.6) * (1 - appear(t, S.c(2, -0.2), 0.5))
    if lower_a > 0:
        cv.text("what the authors said they could not find in 2002 …", 200, 500, 25, "ink", "ital", a=lower_a)
        for i, w in enumerate(("simple", "highly scalable", "portable")):
            aa = appear(t, S.f(1, 0.45 + i * 0.12), 0.6) * (1 - appear(t, S.c(2, -0.2), 0.5))
            chip(cv, 200 + i * 290, 590, w, "blue", aa, 27, "body", 18, 0.16)
        a2 = appear(t, S.f(1, 0.88), 0.7) * (1 - appear(t, S.c(2, -0.2), 0.5))
        cv.text("The paper does not name the systems it surveyed.", 200, 690, 23, "yellow", "ital", a=a2)
        tag(cv, 200, 740, "FROM THE PAPER", "yellow", a2)

    # beat 2: launch-time bars (log scale)
    pa = appear(t, S.c(2, 0.2), 0.7) * (1 - appear(t, S.c(3, -0.2), 0.5))
    if pa > 0:
        bx, by = 420, 520
        cv.text("time to launch a trivial program on 1,000 nodes (Nov 2002)", 200, 488, 23, "ink", "ital", a=pa)
        rows = [("Slurm", 1.0, "blue"), ("Quadrics RMS", 1.0, "dim"), ("IBM LoadLeveler", 80.0, "orange")]
        scale = 1100 / math.log10(100.0)
        for i, (nm, v, c) in enumerate(rows):
            yy = by + 50 + i * 74
            g = ease_out(prog(t, S.f(2, 0.25 + i * 0.18), 0.9))
            wlen = max(8.0, math.log10(v) * scale * 1.0 + 8)
            cv.text(nm, bx - 18, yy + 22, 24, "ink", "body", "r", pa)
            cv.rect(bx, yy, wlen * g, 34, fill=c, r=3, a=pa * 0.85)
            lab = "≈ 1×" if v == 1.0 else "≈ 80× slower"
            if g > 0.95:
                cv.text(lab, bx + wlen + 14, yy + 25, 23, c, "ital", a=pa * appear(t, S.f(2, 0.30 + i * 0.18, 0.9), 0.5))
        cv.line(bx, by + 40, bx, by + 50 + 3 * 74, "rule", 1, pa)
        cv.text("log scale, relative to Slurm", bx, by + 50 + 3 * 74 + 26, 18, "dim", "ital", a=pa)
        cv.text("/bin/hostname, two tasks per node. Ratios from the text; the paper gives no table of times.", 200, 905, 20, "dim", "ital", a=pa)

    # beat 3: design — external scheduler + plugins
    da = appear(t, S.c(3, 0.2), 0.7) * (1 - appear(t, S.c(4, 0.3), 0.6) * 0.0)
    if da > 0:
        ext_a = 1.0 - ease_io(prog(t, S.f(4, 0.02), 1.2))
        # left: resource manager
        rx, ry, rw, rh = 210, 470, 520, 230
        cv.rect(rx, ry, rw, rh, fill="blue", r=12, a=0.08 * da)
        cv.rect(rx, ry, rw, rh, stroke="blue", sw=1.6, r=12, a=da)
        cv.text("Slurm 2003", rx + 24, ry + 40, 27, "blue", "bold", a=da)
        cv.text("nodes · partitions · jobs", rx + 24, ry + 82, 23, "ink", "body", a=da)
        cv.text("default scheduler: plain FIFO", rx + 24, ry + 118, 23, "ink", "body", a=da)
        # what grows in beat 4
        a4 = appear(t, S.f(4, 0.12), 0.8)
        for i, w in enumerate(("priority", "fair-share", "backfill", "accounting")):
            aa = appear(t, S.f(4, 0.12 + i * 0.07), 0.6)
            chip(cv, rx + 24 + (i % 2) * 215, ry + 168 + (i // 2) * 44 - 10 + 8, w, "yellow", aa, 22, "body", 14, 0.16)
        if ext_a > 0.01:
            ex, ey = 930, 470
            cv.rect(ex, ey, 420, 230, fill="yellow", r=12, a=0.06 * da * ext_a)
            cv.rect(ex, ey, 420, 230, stroke="yellow", sw=1.6, r=12, a=da * ext_a, dash=(7, 6))
            cv.text("external scheduler", ex + 24, ey + 40, 27, "yellow", "bold", a=da * ext_a)
            cv.text("Maui  ·  LLNL's DPCS", ex + 24, ey + 84, 23, "ink", "body", a=da * ext_a)
            cv.text("decides the policy", ex + 24, ey + 120, 23, "dim", "ital", a=da * ext_a)
            cv.arrow(ex, ey + 160, rx + rw, ey + 160, "yellow", 1.5, da * ext_a * appear(t, S.f(3, 0.3), 0.6))
            cv.text("sets priorities, reorders", (ex + rx + rw) / 2, ey + 190, 18, "dim", "ital", "c", da * ext_a)
        # plugin sockets
        pa2 = appear(t, S.f(3, 0.62), 0.7)
        cv.text("and every site-specific piece is a plugin:", 210, 776, 23, "ink", "ital", a=pa2 * da)
        for i, w in enumerate(("authentication", "interconnect", "scheduling")):
            aa = appear(t, S.f(3, 0.68 + i * 0.09), 0.5) * da
            x = 210 + i * 260
            cv.rect(x, 800, 236, 46, stroke="teal", sw=1.3, r=8, a=aa)
            cv.rect(x + 18, 790, 12, 12, fill="teal", a=aa * 0.9)
            cv.rect(x + 206, 790, 12, 12, fill="teal", a=aa * 0.9)
            cv.text(w, x + 118, 831, 23, "ink", "body", "c", aa)
        # beat 4 later events on the timeline
    ev(cv, t, S.f(4, 0.30), 2010, "SchedMD founded", None, False, 70, "ink", "r", 10)
    ev(cv, t, S.f(4, 0.46), 2012, "acronym retired: “SLURM” → Slurm", None, True, 70, "ink", "l", -10, 21)
    ev(cv, t, S.f(4, 0.70), 2025, "NVIDIA to acquire SchedMD", "announced 15 Dec 2025", False, 70, "yellow", "r", 10)
    # 2003 papers
    ev(cv, t, S.f(1, 0.70), 2003, "two papers", "ClusterWorld · JSSPP", True, 135, "ink", "l", -8, 21)

    # beat 5: adoption claims
    aa = appear(t, S.c(5, 0.1), 0.7)
    if aa > 0:
        cover = aa
        cv.rect(150, 440, 1620, 470, fill="bg", a=cover * 0.97)
        for i, (num, cap, tg, c, frac) in enumerate((("≈ 60 %", "of TOP500 systems, as of Nov 2021", "SECONDARY SOURCE · Wikipedia", "blue", 0.6),
                                                       ("> ½", "of the top 10 and top 100 systems", "VENDOR CLAIM · NVIDIA, Dec 2025", "yellow", 0.5))):
            x = 220 + i * 760
            ai = appear(t, S.f(5, 0.25 + i * 0.35), 0.7)
            cv.text(num, x, 600, 120, c, "bold", a=ai)
            cv.text(cap, x, 650, 26, "ink", "body", a=ai)
            cv.line(x, 700, x + 600, 700, "faint", 8, ai, cap="butt")
            cv.line(x, 700, x + 600 * frac, 700, c, 8, ai, cap="butt", frac=ease_out(prog(t, S.f(5, 0.3 + i * 0.35), 1.0)))
            tag(cv, x, 760, tg, "yellow", ai)
        cv.text("not a measured census", 960, 880, 26, "dim", "ital", "c", appear(t, S.f(5, 0.78), 0.7))
