import math, random
from fx import *

# ======================================================================= S0  cold open
_N = None
def _nodes():
    global _N
    if _N is None:
        _N = [(160 + i*30, 262 + j*30) for j in range(10) for i in range(24)]
    return _N

def s0(c, A):
    t = A.t
    nodes = _nodes()
    text(c, 'PARALLEL FILE SYSTEMS  ·  PART I', LEFT, 74, 17, DIM, 1.0, 'sans_m', track=3.2)
    line(c, LEFT, 94, 1800, 94, RULE)
    # --- nodes appear as a wave
    fig_a = 1.0 - 0.93 * A.p(3, 0.0, 2.0)
    for k, (x, y) in enumerate(nodes):
        ap = clamp01((A.at(0, 0.0) - (k % 24) * 0.05 - (k // 24) * 0.03) / 0.6)
        flash = 0.0
        tfl = A.tf(0, 0.52)
        if t > tfl: flash = clamp01(1 - (t - tfl) / 1.2)
        col = mix(BLUE, AMBER, clamp01(flash * 1.4))
        if ap > 0: rect(c, x - 6, y - 6, 12, 12, fill=col, a=ap * fig_a, fa=0.35 + 0.6 * flash, r=2, stroke=col, sw=1.2)
    a_lab = A.fade(0, 1.0) * fig_a
    text(c, 'compute processes', 154, 228, 21, DIM, a_lab, 'serif_i')
    text(c, 'each square stands in for ~40 of 10,000', 154, 578, 16, FAINT, a_lab, 'serif_i')
    # --- target: one disk, later many
    one_a = A.fade(1, 0.0) * fig_a
    many = A.p(2, 1.0, 2.5, smooth)
    FX_, FY_ = 1230, 410
    ndisk = 20
    dys = [250 + k * 25 for k in range(ndisk)]
    # packets
    t1 = A.tf(0, 0.60)                           # wave 1 launch
    t2 = A.tf(2, 0.55)                           # wave 2 launch
    served1 = 0
    if t > t1:
        arr = []
        for k, (x, y) in enumerate(nodes):
            d = math.hypot(FX_ - x, FY_ - y)
            arr.append((d / 640.0 + (k % 7) * 0.012, k))
        arr.sort()
        free = 0.0; plan = []
        for (ta, k) in arr:
            st = max(ta, free); free = st + 0.048; plan.append((k, ta, st))
        wt = t - t1
        slot = 0
        waiting = [(k, ta, st) for (k, ta, st) in plan if ta <= wt < st]
        waiting.sort(key=lambda z: z[1])
        for (k, ta, st) in plan:
            x, y = nodes[k]
            if wt < 0: continue
            if wt < ta:
                f = wt / ta
                px, py = lerp(x, FX_ - 46, f), lerp(y, FY_, f)
                circle(c, px, py, 3.2, fill=AMBER, a=0.9 * fig_a)
            elif wt < st:
                idx = waiting.index((k, ta, st))
                px, py = FX_ - 46 - 8 * (idx // 14), FY_ - ((idx % 14) - 6.5) * 8
                circle(c, px, py, 3.2, fill=RED, a=0.9 * fig_a)
            else:
                served1 += 1
        disk_level = served1 / 240.0
    else:
        disk_level = 0
    # wave 2 straight to many disks
    if t > t2:
        wt = t - t2
        for k, (x, y) in enumerate(nodes):
            ty = dys[k % ndisk] + 12
            d = math.hypot(1220 - x, ty - y)
            tt = d / 760.0
            if 0 <= wt < tt + (k % 5) * 0.01:
                f = clamp01(wt / tt)
                circle(c, lerp(x, 1220, f), lerp(y, ty, f), 3.2, fill=GREEN, a=0.85 * fig_a)
    # drawing the disk(s)
    if one_a > 0:
        server(c, FX_ - 20, FY_ - 56, 70, 26, VIOLET, one_a * (1 - many) * fig_a)
        disk(c, FX_ - 2, FY_ - 18, 34, 44, DIM, one_a * (1 - many) * fig_a, fill=BLUE, level=disk_level)
        text(c, 'one disk, one server', FX_ + 15, FY_ + 100, 20, DIM, one_a * (1 - many) * fig_a, 'serif_i', align='c')
    if many > 0:
        for k in range(ndisk):
            ap = clamp01(many * 1.6 - k * 0.03)
            disk(c, 1222, dys[k], 26, 22, GREEN, ap * fig_a, fill=GREEN, fa=0.2, sw=1.1)
        text(c, 'many disks in parallel', 1222, 228, 21, GREEN, many * fig_a, 'serif_i')
    # --- little chart: demand vs ceiling
    cx0, cy0, cw, ch = 154, 650, 640, 220
    ca = A.fade(1, 0.5) * fig_a
    if ca > 0:
        hair_axis(c, cx0, cy0 + ch, cx0 + cw, cy0 + ch, ca); hair_axis(c, cx0, cy0, cx0, cy0 + ch, ca)
        text(c, 'rate', cx0 - 12, cy0 + 12, 15, DIM, ca, 'serif_i', align='r')
        text(c, 'time', cx0 + cw, cy0 + ch + 24, 15, DIM, ca, 'serif_i', align='r')
        grow = A.p(0, 0, 1) if False else clamp01((t - t1) / 1.0)
        dh = ch * 0.92 * grow
        bx0, bx1 = cx0 + 90, cx0 + 250
        rect(c, bx0, cy0 + ch - dh, bx1 - bx0, dh, fill=BLUE, a=ca, fa=0.35 * ca)
        text(c, 'everyone writes at once', bx0 + 6, cy0 + ch - dh - 8, 16, BLUE, ca * grow, 'serif_i')
        cap = 0.16 + 0.95 * many
        capy = cy0 + ch - ch * cap
        col = mix(RED, GREEN, many)
        line(c, cx0, capy, cx0 + cw, capy, col, ca, 1.6, dash=[7, 5])
        lab = 'ceiling of one box' if many < 0.5 else 'ceiling of many boxes'
        text(c, lab, cx0 + cw - 4, capy - 8, 16, col, ca, 'serif_i', align='r')
        over = max(0.0, dh - ch * cap)
        if over > 0 and many < 0.99:
            rect(c, bx0, cy0 + ch - dh, bx1 - bx0, over, fill=RED, a=ca * (1 - many), fa=0.55 * (1 - many))
        text(c, 'schematic, not to scale', cx0, cy0 + ch + 46, 14, FAINT, ca, 'serif_i')
    # --- the question
    qa = A.fade(2, 0.2, 1.2) * (1 - A.p(3, 0, 1.2, smooth))
    text(c, 'one namespace  ·  many writers  ·  one truth', 960, 168, 40, INK, qa, 'serif_i', align='c')
    # --- title card
    ta = A.fade(3, 0.4, 1.6)
    if ta > 0:
        text(c, 'GPFS', 960, 520, 200, INK, ta, 'title', align='c')
        text(c, 'General Parallel File System  →  IBM Spectrum Scale  →  IBM Storage Scale', 960, 600, 32, AMBER, ta, 'serif_i', align='c')
        text(c, 'A FIRST-PRINCIPLES TOUR  ·  HISTORY  ·  MECHANISMS  ·  REAL SYSTEMS', 960, 676, 18, DIM, ta, 'sans_m', align='c', track=4)

# ======================================================================= S1  history
def _yx(y): return 140 + (y - 1990) * 35.0

def s1(c, A):
    notes = [
        (0, 150, '1', 'Vesta: IBM Watson, 1992–95, commercialized as PIOFS (c. 1994). Tiger Shark: IBM Almaden, "as early as 1993", designed for high-throughput multimedia. Source: Wikipedia, GPFS.'),
        (2, 400, '2', 'Schmuck & Haskin, "GPFS: A Shared-Disk File System for Large Computing Clusters," Proc. FAST ’02, Monterey, pp. 231–244. First release c. 1998 on AIX (Wikipedia).'),
        (3, 650, '3', 'ASCI White: 512 nodes, 140 TB of disk in two file systems; "Sixteen nodes drive the entire 12 GB/s I/O bandwidth." Schmuck & Haskin, footnote 6.'),
        (4, 840, '4', 'The "Spectrum" prefix arrived in 2015 and was dropped in February 2023. Source: Blocks & Files, 24 Feb 2023.'),
    ]
    chrome(c, A, 'Where it came from', 1, notes, ('Fig. 1.', 'Two research lineages converge on one product.'), 0, 2.0)
    AX = 440
    # axis + ticks
    ax = A.fade(0, 0.0, 1.0)
    line(c, _yx(1990), AX, _yx(2025), AX, FAINT, ax, 1.0)
    for y in range(1990, 2026, 5):
        line(c, _yx(y), AX, _yx(y), AX + 6, FAINT, ax, 1.0)
        text(c, str(y), _yx(y), AX + 26, 14, DIM, ax, 'sans', align='c')
    # Vesta bar (1992-95) + Tiger Shark fading bar (1993 -> 1998)
    pv = A.p(0, 0.6, 2.0)
    x0, x1 = _yx(1992), lerp(_yx(1992), _yx(1995), pv)
    rect(c, x0, AX - 20, x1 - x0, 7, fill=AMBER, a=ax)
    pt = A.p(0, 3.0, 2.5)
    xa, xb = _yx(1993), lerp(_yx(1993), _yx(1998), pt)
    rect(c, xa, AX - 33, xb - xa, 7, fill=BLUE, a=ax)
    text(c, 'Vesta', _yx(1992), AX + 62, 22, AMBER, A.fade(0, 1.2), 'serif')
    text(c, 'Watson · parallel files', _yx(1992), AX + 86, 15, DIM, A.fade(0, 1.6), 'serif_i')
    text(c, 'Tiger Shark', _yx(1992), AX - 76, 22, BLUE, A.fade(0, 3.2), 'serif')
    text(c, 'Almaden · multimedia', _yx(1992), AX - 52, 15, DIM, A.fade(0, 3.6), 'serif_i')
    # inset: small multiples of load per disk (line 1)
    ia = A.fade(1, 0.3) * (1 - A.p(2, 0, 1.0, smooth))
    if ia > 0:
        for m, (x0_, ttl, hot) in enumerate([(150, 'no striping — one disk is the hot spot', True), (640, 'striped — load spreads evenly', False)]):
            by = 800
            text(c, ttl, x0_, 640, 18, INK, ia, 'serif_i')
            hair_axis(c, x0_, by, x0_ + 400, by, ia)
            g = A.p(1, 1.2 + m * 3.5, 2.0)
            for d in range(8):
                h = (170 if d == 3 else 8) if hot else 40
                col = RED if (hot and d == 3) else BLUE
                rect(c, x0_ + 20 + d * 46, by - h * g, 30, h * g, fill=col, a=ia, fa=0.8 * ia)
            text(c, 'load per disk (schematic)', x0_, by + 28, 14, FAINT, ia, 'serif_i')
    # GPFS marker + convergence (line 2)
    pg = A.p(2, 0.3, 1.6)
    gx = _yx(1998)
    if pg > 0:
        curve(c, [(_yx(1995), AX - 16), (_yx(1996.5), AX - 16), (gx - 20, AX - 6), (gx, AX - 2)], AMBER, pg * 0.8, 2)
        circle(c, gx, AX, 8 * pg, fill=INK, a=pg)
        text(c, 'GPFS', gx + 26, AX - 70, 40, INK, pg, 'title')
        text(c, 'first release · AIX · c. 1998', gx + 26, AX - 42, 15, DIM, pg, 'serif_i')
        line(c, gx, AX - 48, gx, AX - 12, FAINT, pg, 1)
    # 2002 paper marker
    pp = A.p(2, 3.0, 1.2)
    if pp > 0:
        px = _yx(2002)
        circle(c, px, AX, 6 * pp, fill=BLUE, a=pp)
        line(c, px, AX + 6, px, AX + 56, FAINT, pp, 1)
        text(c, 'FAST ’02 paper', px + 20, AX + 80, 22, BLUE, pp, 'serif', align='l')
    # three ideas
    ka = A.fade(2, 5.5, 1.2) * (1 - A.p(3, 0, 1.0, smooth))
    for k, wd in enumerate(['shared disks', 'wide striping', 'distributed locking']):
        cx3 = [330, 770, 1230][k]
        text(c, wd, cx3, 760, 38, INK, A.fade(2, 5.0 + k * 1.6, 1.0) * (1 - A.p(3, 0, 1.0, smooth)), 'serif_i', align='c')
        if k < 2: text(c, '·', [550, 1000][k], 760, 38, FAINT, A.fade(2, 5.0 + k * 1.6, 1.0) * (1 - A.p(3, 0, 1.0, smooth)), 'serif', align='c')
    # ASCI White panel (line 3)
    pa = A.fade(3, 0.5, 1.2) * (1 - A.p(4, 0, 1.0, smooth))
    if pa > 0:
        text(c, 'ASCI White  ·  2002', 150, 640, 24, INK, pa, 'serif')
        for k, (big, small) in enumerate([('512', 'nodes'), ('140 TB', 'of disk, in two file systems'), ('12 GB/s', 'I/O bandwidth, driven by 16 nodes')]):
            a = A.fade(3, 1.5 + k * 3.0, 1.2) * (1 - A.p(4, 0, 1.0, smooth))
            text(c, big, 150 + k * 410, 750, 78, AMBER, a, 'title')
            text(c, small, 152 + k * 410, 790, 18, DIM, a, 'serif_i')
    # naming chain (line 4)
    na = A.fade(4, 0.4, 1.2)
    if na > 0:
        xs = [150, 520, 1010]
        names = [('GPFS', '1998'), ('Spectrum Scale', '2015'), ('Storage Scale', '2023')]
        for k, (nm, yr) in enumerate(names):
            a = A.fade(4, 1.0 + k * 3.0, 1.0)
            text(c, nm, xs[k], 750, 46, INK if k < 2 else AMBER, a, 'title')
            text(c, yr, xs[k], 790, 18, DIM, a, 'sans')
            if k < 2: arrow(c, xs[k] + tw(nm, 46, 'title') + 20, 738, xs[k + 1] - 20, 738, DIM, a, 1.6)
        for yr, lab, col in [(2015, 'Spectrum Scale', INK), (2023, 'Storage Scale', AMBER)]:
            a = A.fade(4, 1.0 + (1 if yr == 2015 else 2) * 3.0, 1.0)
            circle(c, _yx(yr), AX, 6 * a, fill=col, a=a)
            line(c, _yx(yr), AX + 6, _yx(yr), AX + 56, FAINT, a, 1)
            text(c, lab, _yx(yr), AX + 80, 20, col, a, 'serif', align='c')
        text(c, 'same lineage, same core design', 150, 830, 20, DIM, A.fade(4, 11, 1.0), 'serif_i')

# ======================================================================= S2  striping, block size, subblocks
def _eff(B, tp, bw): return (B / bw) / (tp + B / bw)

def s2(c, A):
    notes = [
        (1, 230, '1', 'Schmuck & Haskin: "Files are striped across all disks in the file system"; up to 4,096 disks of up to 1 TB each, about 4 PB per file system, in the 2002 design.'),
        (2, 470, '2', 'Illustrative model, not measurements. Efficiency = transfer time ÷ (positioning time + transfer time). Assumed: c. 2002 disk 10 ms, 40 MB/s; modern HDD 8 ms, 200 MB/s.'),
        (2, 700, '3', 'Block size: "typically 256k, but can be configured between 16k and 1M" (paper). 16 MB on Summit: OLCF Spectrum Scale workshop slide 11.'),
        (3, 880, '4', 'Paper: subblocks "as small as 1/32 of the size of a full block."'),
    ]
    chrome(c, A, 'First idea: stripe everything', 2, notes)
    # ---- Part A: striping
    A_out = 1 - A.p(2, 0.0, 1.0, smooth)
    NB, ND = 18, 6
    col_of = lambda i: mix(BLUE, GREEN, i / (NB - 1))
    bx = lambda i: 150 + i * 50
    byf = 290
    def slot(i): return (150 + (i % ND) * 160 + 24, 560 + (i // ND) * 46)
    if A_out > 0:
        for d in range(ND):
            x = 150 + d * 160
            rect(c, x, 510, 112, 210, stroke=DIM, a=A_out * A.fade(0, 0.0), sw=1.3, r=6)
            text(c, f'disk {d+1}', x + 56, 752, 17, DIM, A_out * A.fade(0, 0.2), 'serif_i', align='c')
        text(c, 'a file, cut into blocks', 150, 250, 19, DIM, A_out * A.fade(0, 0.0), 'serif_i')
        for i in range(NB):
            s0 = 1.0 + i * 0.7
            f = A.p(0, s0, 0.9)
            x1, y1 = bx(i), byf
            x2, y2 = slot(i)
            f2 = ease_out(f)
            x = lerp(x1, x2, f2); y = lerp(y1, y2, f2) if f > 0 else y1
            rect(c, x, y, 44 if f == 0 else lerp(44, 64, f2), 34, fill=col_of(i), a=A_out * A.fade(0, 0.2), fa=0.75, r=3)
            text(c, str(i), x + (22 if f == 0 else lerp(22, 32, f2)), y + 23, 15, BG, A_out * A.fade(0, 0.4), 'sans_b', align='c')
    # read pulse: arrows up + aggregate bar chart
    ra = A.fade(1, 0.5) * A_out
    if ra > 0:
        for d in range(ND):
            x = 150 + d * 160 + 56
            ph = (A.at(1, 0) * 1.1 + d * 0.0) % 1.0
            arrow(c, x, 500, x, 420, BLUE, ra, 2.0)
            for k in range(2):
                yy = 500 - ((A.t * 70 + k * 40) % 80)
                circle(c, x, yy, 3, fill=BLUE, a=ra)
        line(c, 150 + 56, 420, 150 + 5 * 160 + 56, 420, BLUE, ra, 3)
        text(c, 'a read engages every disk at once', 150, 392, 19, BLUE, ra, 'serif_i')
        # chart: aggregate bandwidth vs disks
        gx0, gy0, gw, gh = 1130, 340, 230, 330
        hair_axis(c, gx0, gy0 + gh, gx0 + gw, gy0 + gh, ra); hair_axis(c, gx0, gy0, gx0, gy0 + gh, ra)
        text(c, 'bandwidth', gx0 - 8, gy0 - 8, 15, DIM, ra, 'serif_i', align='l')
        text(c, 'number of disks', gx0 + gw, gy0 + gh + 24, 15, DIM, ra, 'serif_i', align='r')
        n = int(1 + 15 * A.p(1, 1.5, 6.0))
        for k in range(1, n + 1):
            x = gx0 + (k / 16) * gw; h = (k / 16) * gh
            rect(c, x - 5, gy0 + gh - h, 10, h, fill=BLUE, a=ra, fa=0.7 * ra)
        text(c, '≈ proportional, until the network or servers saturate', gx0 - 8, gy0 + gh + 52, 14, FAINT, ra, 'serif_i')
    # ---- Part B: block size curve
    pb = A.fade(2, 0.8, 1.0) * (1 - A.p(3, 0, 1.0, smooth))
    if pb > 0:
        gx0, gy0, gw, gh = 190, 240, 1040, 560
        lo, hi = math.log2(16 * 1024), math.log2(32 * 1024 * 1024)
        X = lambda B: gx0 + (math.log2(B) - lo) / (hi - lo) * gw
        Y = lambda e: gy0 + gh - e * gh
        for e in (0, 0.25, 0.5, 0.75, 1.0):
            line(c, gx0, Y(e), gx0 + gw, Y(e), RULE, pb * 0.7, 0.8)
            text(c, f'{int(e*100)}%', gx0 - 14, Y(e) + 5, 15, DIM, pb, 'sans', align='r')
        labels = [(16*1024, '16 KB'), (64*1024, '64 KB'), (256*1024, '256 KB'), (1024**2, '1 MB'), (4*1024**2, '4 MB'), (16*1024**2, '16 MB')]
        for B, lab in labels:
            line(c, X(B), gy0 + gh, X(B), gy0 + gh + 6, FAINT, pb)
            text(c, lab, X(B), gy0 + gh + 26, 15, DIM, pb, 'sans', align='c')
        text(c, 'block size (log scale)', gx0 + gw, gy0 + gh + 54, 16, DIM, pb, 'serif_i', align='r')
        text(c, 'share of streaming bandwidth achieved', gx0, gy0 - 22, 17, DIM, pb, 'serif_i')
        grow = A.pf(2, 0.05, 0.40)
        for (tp, bw, col, lab, ly) in [(0.010, 40e6, DIM, 'c. 2002 disk', 0.22), (0.008, 200e6, BLUE, 'modern HDD', 0.55)]:
            path = skia.Path(); first = True
            pts = [16 * 1024 * (2 ** (k / 20)) for k in range(0, int(20 * (hi - lo)) + 1)]
            pts = pts[: max(2, int(len(pts) * grow))]
            for B in pts:
                xx, yy = X(B), Y(_eff(B, tp, bw))
                if first: path.moveTo(xx, yy); first = False
                else: path.lineTo(xx, yy)
            c.drawPath(path, P(col, pb, 'stroke', 3.0))
        e1 = _eff(256 * 1024, 0.010, 40e6); e2 = _eff(16 * 1024**2, 0.008, 200e6)
        m1 = A.p(2, 0, 1.0) if False else A.pf(2, 0.50, 0.58, smooth)
        m2 = A.pf(2, 0.78, 0.86, smooth)
        if m1 > 0:
            circle(c, X(256 * 1024), Y(e1), 8, fill=INK, a=m1)
            text(c, '256 KB: typical in the 2002 paper', X(256 * 1024) + 16, Y(e1) + 40, 19, INK, m1, 'serif')
            text(c, 'c. 2002 disk', X(1024**2 * 3), Y(_eff(3 * 1024**2, 0.010, 40e6)) + 28, 17, DIM, m1, 'serif_i')
        if m2 > 0:
            circle(c, X(16 * 1024**2), Y(e2), 8, fill=INK, a=m2)
            text(c, '16 MB: Summit today', X(16 * 1024**2) + 6, Y(e2) + 44, 19, INK, m2, 'serif', align='r')
            text(c, 'modern HDD', X(2 * 1024**2), Y(_eff(2 * 1024**2, 0.008, 200e6)) - 24, 17, BLUE, m2, 'serif_i')
        text(c, 'bandwidth grew faster than positioning time improved, so efficient blocks grew', gx0, gy0 + gh + 90, 18, AMBER, A.fade(2, 0.0) * 0 + A.pf(2, 0.88, 0.97, smooth) * pb, 'serif_i')
    # ---- Part C: subblocks
    pc = A.fade(3, 0.6, 1.0)
    if pc > 0:
        def block(x, y, filled, cols=8, rows=4, cw=42, ch=32, color=BLUE, wasted=False, a=1.0):
            for r in range(rows):
                for q in range(cols):
                    k = r * cols + q
                    fx_, fy_ = x + q * cw, y + r * ch
                    if k < filled: rect(c, fx_, fy_, cw - 2, ch - 2, fill=color, a=a, fa=0.85 * a)
                    elif wasted: rect(c, fx_, fy_, cw - 2, ch - 2, fill=RED, a=a, fa=0.25 * a)
                    else: rect(c, fx_, fy_, cw - 2, ch - 2, stroke=RULE, a=a, sw=1)
            rect(c, x - 3, y - 3, cols * cw + 4, rows * ch + 4, stroke=DIM, a=a, sw=1.4)
        text(c, 'a small file', 150, 250, 22, INK, pc, 'serif')
        q1 = A.fade(3, 1.0)
        block(150, 275, 1, wasted=False, a=pc * q1, color=AMBER)
        text(c, 'uses one subblock', 150, 440, 17, AMBER, pc * q1, 'serif_i')
        text(c, 'without subblocks', 700, 250, 22, INK, pc * A.fade(3, 6.0), 'serif')
        q2 = A.fade(3, 6.0)
        block(700, 275, 1, wasted=True, a=pc * q2, color=AMBER)
        text(c, 'a whole block reserved, 31/32 wasted', 700, 440, 17, RED, pc * q2, 'serif_i')
        q3 = A.fade(3, 12.0)
        text(c, 'a larger file: full blocks, then a tail', 150, 540, 22, INK, pc * q3, 'serif')
        block(150, 565, 32, a=pc * q3, color=BLUE)
        block(580, 565, 32, a=pc * q3, color=BLUE)
        block(1010, 565, 3, a=pc * q3, color=AMBER)
        text(c, 'tail uses 3 subblocks', 1010, 730, 17, AMBER, pc * q3, 'serif_i')
        text(c, 'each cell = 1/32 of a block (not to scale in bytes)', 150, 790, 16, FAINT, pc * q3, 'serif_i')

# ======================================================================= S3  architecture and roles
def s3(c, A):
    notes = [
        (1, 240, '1', 'NSD = Network Shared Disk. "Data/metadata might flow using direct path and/or network depending on NSD configuration." IBM, SC19 Spectrum Scale concepts.'),
        (2, 470, '2', 'Cluster manager: "one of the quorum nodes"; manages leases, failures, recoveries. "Apart from quorum, all the nodes are identical." IBM SC19 slides.'),
        (3, 640, '3', 'Token managers "each manage portion of tokens for each filesystem based on inode number." IBM SC19 slides.'),
        (4, 800, '4', 'Paper: access to the file system is allowed "only by the group containing a majority of the nodes in the cluster."'),
    ]
    chrome(c, A, 'The cast: clients, NSD servers, managers', 3, notes)
    random.seed(4)
    NC, NS = 30, 6
    cl = [(150 + (i % 5) * 36, 250 + (i // 5) * 36) for i in range(NC)]
    srv_y = [236 + k * 66 for k in range(NS)]
    srv_x = 950
    dsk = [(1110 + j * 40, srv_y[k] - 2) for k in range(NS) for j in range(4)]
    fab = (520, 330, 110, 100)       # x,y,w,h
    # --- beat 0: mesh
    ma = A.fade(0, 0.5) * (1 - A.p(1, 0.2, 1.2, smooth))
    for (x, y) in cl:
        node(c, x, y, 12, BLUE, A.fade(0, 0.0))
    if ma > 0:
        reveal = A.p(0, 2.0, 8.0)
        n_show = int(len(cl) * len(dsk) * reveal)
        k = 0
        for (x, y) in cl:
            for (dx_, dy_) in dsk:
                if k >= n_show: break
                line(c, x + 7, y, dx_ + 11, dy_ + 20, BLUE, 0.09 * ma, 0.8); k += 1
        for (dx_, dy_) in dsk:
            disk(c, dx_, dy_, 22, 30, DIM, ma)
        text(c, f'every node → every disk: {NC} × {len(dsk)} = {NC*len(dsk)} paths', 150, 200, 20, INK, ma * A.fade(0, 4.0), 'serif_i')
        text(c, 'and that is with 30 clients', 150, 224, 16, FAINT, ma * A.fade(0, 8.0), 'serif_i')
    # --- beat 1: NSD architecture
    na = A.fade(1, 0.8, 1.2)
    if na > 0:
        # links
        for (x, y) in cl: line(c, x + 7, y, fab[0], fab[1] + fab[3] / 2 + (y - 340) * 0.25, BLUE, 0.25 * na, 0.8)
        rect(c, fab[0], fab[1], fab[2], fab[3], stroke=DIM, a=na, sw=1.6, r=8)
        text(c, 'network', fab[0] + fab[2] / 2, fab[1] + fab[3] / 2 + 6, 20, DIM, na, 'serif_i', align='c')
        text(c, 'InfiniBand / Ethernet', fab[0] + fab[2] / 2, fab[1] + fab[3] + 22, 14, FAINT, na, 'serif_i', align='c')
        for k in range(NS):
            line(c, fab[0] + fab[2], fab[1] + fab[3] / 2 + (k - 2.5) * 12, srv_x, srv_y[k] + 13, VIOLET, 0.5 * na, 1.0)
            server(c, srv_x, srv_y[k], 100, 26, VIOLET, na, 0.0)
            for j in range(4):
                dx_, dy_ = dsk[k * 4 + j]
                line(c, srv_x + 100, srv_y[k] + 13, dx_, dy_ + 15, VIOLET, 0.4 * na, 0.8)
                disk(c, dx_, dy_, 22, 30, DIM, na, fill=BLUE, fa=0.15)
        text(c, 'NSD servers', srv_x + 50, 206, 19, VIOLET, na, 'serif_i', align='c')
        text(c, 'clients', 150 + 72, 206, 19, BLUE, na * (1 - ma), 'serif_i', align='c')
        # packets client -> server -> disk
        for q in range(14):
            k = q % NS; ci = (q * 7) % NC
            f = ((A.t * 0.45 + q * 0.173) % 1.0)
            if na < 0.9: continue
            p0 = (cl[ci][0] + 7, cl[ci][1]); p1 = (fab[0], fab[1] + fab[3] / 2); p2 = (srv_x, srv_y[k] + 13); p3 = (dsk[k * 4 + q % 4][0] + 11, dsk[k * 4 + q % 4][1] + 15)
            if f < 0.4: u = f / 0.4; x, y = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
            elif f < 0.7: u = (f - 0.4) / 0.3; x, y = lerp(p1[0] + fab[2], p2[0], u), lerp(p1[1], p2[1], u)
            else: u = (f - 0.7) / 0.3; x, y = lerp(p2[0] + 100, p3[0], u), lerp(p2[1], p3[1], u)
            circle(c, x, y, 3, fill=AMBER, a=0.9)
        # pool bracket
        pbk = A.fade(1, 6.0)
        bx = 1110 + 4 * 40 + 6
        path = skia.Path(); path.moveTo(bx, srv_y[0] - 8); path.lineTo(bx + 10, srv_y[0] - 8); path.lineTo(bx + 10, srv_y[-1] + 40); path.lineTo(bx, srv_y[-1] + 40)
        c.drawPath(path, P(AMBER, pbk * na, 'stroke', 2))
        text(c, 'one shared pool of NSDs', 1110 + 78, srv_y[-1] + 72, 21, AMBER, pbk * na, 'serif_i', align='c')
    # --- beat 2: quorum + cluster manager
    ra = A.fade(2, 0.8)
    quorum = [0, 2, 4]
    if ra > 0:
        for k in quorum:
            circle(c, srv_x - 16, srv_y[k] + 13, 9, stroke=AMBER, a=ra, sw=2.2)
        sm = A.fade(2, 5.5)
        star(c, srv_x - 16, srv_y[2] + 13, 9, AMBER, sm)
        text(c, 'quorum nodes', srv_x - 34, srv_y[0] + 18, 17, AMBER, ra, 'serif_i', align='r')
        text(c, 'cluster manager', srv_x - 34, srv_y[2] + 18, 17, AMBER, sm, 'serif', align='r')
        text(c, 'leases · failure detection · recovery', srv_x - 34, srv_y[2] + 40, 15, DIM, sm, 'serif_i', align='r')
    # --- beat 3: FS manager + token managers
    fa = A.fade(3, 0.5)
    if fa > 0:
        circle(c, srv_x - 16, srv_y[1] + 13, 9, stroke=GREEN, a=fa, sw=2.2)
        text(c, 'file system manager', srv_x - 34, srv_y[1] + 18, 17, GREEN, fa, 'serif', align='r')
        text(c, 'space · quotas · disk config', srv_x - 34, srv_y[1] - 4, 14, DIM, fa, 'serif_i', align='r')
        ta = A.fade(3, 6.0)
        tm = [3, 4, 5]
        cols = [BLUE, AMBER, VIOLET]
        for n_, k in enumerate(tm):
            circle(c, srv_x + 118, srv_y[k] + 13, 6, fill=cols[n_], a=ta)
        text(c, 'token managers', srv_x + 130, srv_y[3] + 17 - 36, 0 + 15, DIM, ta, 'serif_i') if False else None
        # inode-space bar split among token managers
        bx0, by0, bw = 150, 640, 420
        text(c, 'inode number space', bx0, by0 - 12, 16, DIM, ta, 'serif_i')
        for n_ in range(3):
            rect(c, bx0 + n_ * bw / 3, by0, bw / 3 - 3, 22, fill=cols[n_], a=ta, fa=0.7 * ta)
            text(c, f'token mgr {n_+1}', bx0 + n_ * bw / 3 + (bw / 3 - 3) / 2, by0 + 40, 14, cols[n_], ta, 'serif_i', align='c')
            curve(c, [(bx0 + n_ * bw / 3 + 50, by0), (bx0 + n_ * bw / 3 + 50, by0 - 60), (srv_x - 120, srv_y[tm[n_]] + 60), (srv_x + 108, srv_y[tm[n_]] + 22)], cols[n_], 0.30 * ta, 1.0)
    # --- beat 4: partition / majority
    pa = A.fade(4, 0.8)
    if pa > 0:
        y0 = 880
        text(c, 'a network partition', 860, y0 - 64, 20, INK, pa, 'serif_i', align='c')
        xs = [620 + k * 60 for k in range(5)] + [1080 + k * 60 for k in range(2)]
        cutp = A.p(4, 3.0, 1.0)
        for k, x in enumerate(xs):
            maj = k < 5
            col = GREEN if maj else mix(RED, DIM, 0.3)
            circle(c, x, y0, 13, fill=col, a=pa, fa=0.3 + 0.0, stroke=col, sw=2)
        for k in range(len(xs) - 1):
            if k == 4: continue
            line(c, xs[k] + 13, y0, xs[k + 1] - 13, y0, DIM, pa * 0.6, 1.2)
        line(c, xs[4] + 13, y0, xs[5] - 13, y0, RED, pa * (1 - cutp), 1.2)
        if cutp > 0:
            cx_ = (xs[4] + xs[5]) / 2
            path = skia.Path(); path.moveTo(cx_ - 8, y0 - 40); path.lineTo(cx_ + 8, y0 - 15); path.lineTo(cx_ - 8, y0 + 15); path.lineTo(cx_ + 8, y0 + 40)
            c.drawPath(path, P(RED, cutp * pa, 'stroke', 3))
        ok = A.fade(4, 5.5)
        text(c, 'majority: keeps the disks', (xs[0] + xs[4]) / 2, y0 + 60, 18, GREEN, pa * ok, 'serif', align='c')
        text(c, 'minority: fenced off', (xs[5] + xs[6]) / 2 + 10, y0 + 60, 18, RED, pa * ok, 'serif', align='c')
        check(c, (xs[0] + xs[4]) / 2, y0 - 36, 9, GREEN, pa * ok)
        cross(c, (xs[5] + xs[6]) / 2, y0 - 36, 8, RED, pa * ok)
