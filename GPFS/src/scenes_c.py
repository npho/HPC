import math, random
from fx import *
from scenes_b import vis, chip

# ======================================================================= S7  real deployments
def s7(c, A):
    notes = [
        (1, 150, '1', '"Using policy and/or fast inode scan in order to make decisions (placement, migration)." Independent filesets: "a fileset with a reserved set of inode block ranges." IBM SC19 slides. Rule shown is illustrative.'),
        (2, 320, '2', '"No designated mirror, each replica is stored in a different FG [failure group]." IBM SC19 slides.'),
        (3, 480, '3', 'AFM: "asynchronous file caching with side effects (DR)"; remote cluster mounts: IBM documentation, "Mounting a remote GPFS file system."'),
        (4, 650, '4', 'FPO released with GPFS 3.5, December 2012 (Wikipedia). ECE: "packaged as hardware solution (ESS/DSS) or software (ECE)." IBM SC19 slides.'),
        (5, 830, '5', 'Alpine: OLCF Spectrum Scale on Summit workshop slides 2 and 11; OLCF Summit page (250 PB, ~2.5 TB/s sequential, ~2.2 TB/s random).'),
    ]
    chrome(c, A, 'What real systems look like', 7, notes)
    n = 7
    # ---------------- beat 0: three tiers
    v = vis(A, 0, n)
    if v > 0:
        text(c, 'compute nodes', 150, 250, 20, BLUE, v, 'serif_i')
        for r in range(8):
            for q in range(5):
                node(c, 160 + q * 34, 290 + r * 34, 14, BLUE, v * A.fade(0, 1.0 + (r + q) * 0.05))
        text(c, 'Scale client on each', 150, 600, 16, DIM, v * A.fade(0, 2.5), 'serif_i')
        fa = A.fade(0, 4.0)
        rect(c, 470, 290, 120, 270, stroke=DIM, a=v * fa, sw=1.6, r=8)
        text(c, 'fast fabric', 530, 420, 20, DIM, v * fa, 'serif', align='c')
        text(c, 'InfiniBand / Ethernet', 530, 446, 14, FAINT, v * fa, 'serif_i', align='c')
        for r in range(8):
            line(c, 300, 290 + r * 34, 470, 400 + (r - 3.5) * 10, BLUE, v * fa * 0.3, 1)
        nb = 1 + int(3 * A.p(0, 7.0, 9.0, f=lambda x: clamp01(x)))
        text(c, 'building blocks: servers with storage behind them', 780, 250, 20, VIOLET, v * A.fade(0, 6.0), 'serif_i')
        for b in range(5):
            ba = A.fade(0, 6.5 + b * 2.4, 0.8)
            y = 290 + b * 70
            server(c, 780, y, 80, 26, VIOLET, v * ba)
            server(c, 780, y + 30, 80, 26, VIOLET, v * ba)
            for q in range(5): disk(c, 890 + q * 36, y + 2, 26, 52, DIM, v * ba, fill=BLUE, fa=0.15)
            line(c, 590, 425, 780, y + 28, VIOLET, v * ba * 0.4, 1)
        # bandwidth meter
        text(c, 'aggregate bandwidth', 1190, 262, 17, DIM, v * A.fade(0, 8.0), 'serif_i')
        text(c, '(schematic)', 1190, 286, 15, FAINT, v * A.fade(0, 8.0), 'serif_i')
        bars = int(1 + 4 * A.p(0, 6.5, 12.0, f=lambda x: clamp01(x)))
        for b in range(5):
            h = (b + 1) * 56
            ba = 1.0 if b < bars else 0.12
            rect(c, 1190 + b * 42, 650 - h, 32, h, fill=GREEN, a=v * A.fade(0, 8.0), fa=ba * 0.8 * v * A.fade(0, 8.0))
        text(c, 'add building blocks  →  add bandwidth and capacity', 780, 730, 20, GREEN, v * A.fade(0, 14.0), 'serif_i')
    # ---------------- beat 1: pools and policy
    v = vis(A, 1, n)
    if v > 0:
        pools = [(150, 270, 270, 110, 'metadata pool', 'fast media', AMBER), (150, 420, 270, 110, 'data pool: fast tier', 'flash', BLUE), (150, 570, 470, 140, 'data pool: capacity tier', 'large, cheaper disks', GREEN)]
        for (x, y, w_, h_, nm, sub, col) in pools:
            rect(c, x, y, w_, h_, stroke=col, a=v, sw=1.8, r=8)
            text(c, nm, x + 14, y + 30, 21, col, v, 'serif')
            text(c, sub, x + 14, y + 56, 16, DIM, v, 'serif_i')
        # files aging and migrating from fast to capacity
        rr = random.Random(3)
        for k in range(14):
            fx0 = 300 + (k % 7) * 18 + 8; fy0 = 460 + (k // 7) * 20 + 18
            tmig = 7.0 + k * 0.7
            f = A.p(1, tmig, 1.2)
            tx, ty = 200 + (k % 7) * 28, 640 + (k // 7) * 30
            x = lerp(fx0 - 60, tx, f); y = lerp(fy0, ty, f)
            age = clamp01((A.at(1, 2.0) + k * 0.3) / 8.0)
            col = mix(BLUE, DIM, 1.0 if f > 0 else age)
            circle(c, x, y, 7, fill=col, a=v * A.fade(1, 1.5))
        # rule box
        ra = A.fade(1, 3.0, 1.0)
        rect(c, 700, 270, 640, 190, stroke=DIM, a=v * ra, sw=1.4, r=8)
        text(c, 'a policy rule (illustrative)', 716, 300, 17, DIM, v * ra, 'serif_i')
        code = ["RULE 'cold' MIGRATE", "  FROM POOL 'fast'", "  TO POOL 'capacity'", "  WHERE (DAYS(CURRENT_TIMESTAMP)", "         - DAYS(ACCESS_TIME)) > 30"]
        for i, ln in enumerate(code):
            text(c, ln, 716, 336 + i * 26, 18, INK if i != 1 and i != 2 else AMBER, v * ra, 'mono')
        text(c, 'scanned in parallel across many nodes', 700, 500, 20, GREEN, v * A.fade(1, 5.0), 'serif_i')
        text(c, 'files older than 30 days drift to the capacity tier', 700, 534, 20, INK, v * A.fade(1, 7.0), 'serif_i')
    # ---------------- beat 2: filesets + failure groups
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'filesets: subtrees with their own quotas', 150, 250, 22, INK, v, 'serif')
        tree = [(300, 330, '/gpfs', INK), (180, 430, 'proj-a', BLUE), (300, 430, 'proj-b', GREEN), (420, 430, 'scratch', AMBER)]
        for (x, y, lab, col) in tree[1:]:
            line(c, 300, 340, x, 414, FAINT, v, 1.2)
        for (x, y, lab, col) in tree:
            rect(c, x - 50, y - 18, 100, 36, stroke=col, a=v, sw=1.6, r=6); text(c, lab, x, y + 7, 19, col, v, 'sans_m', align='c')
        for k, (x, y, lab, col) in enumerate(tree[1:]):
            used = [0.7, 0.35, 0.9][k]
            rect(c, x - 45, y + 36, 90, 10, stroke=DIM, a=v * A.fade(2, 3.0), sw=1)
            rect(c, x - 45, y + 36, 90 * used * A.p(2, 3.5, 1.5), 10, fill=col, a=v * A.fade(2, 3.0), fa=0.8 * v)
        text(c, 'quota used', 150, 530, 15, FAINT, v * A.fade(2, 3.0), 'serif_i')
        # failure groups
        text(c, 'failure groups: who shares a fate', 780, 250, 22, INK, v * A.fade(2, 6.0), 'serif')
        fa = A.fade(2, 6.0)
        for k, (x, nm) in enumerate([(790, 'failure group 1  (rack / enclosure)'), (1090, 'failure group 2')]):
            dead = (k == 0) and A.p(2, 11.0, 0.6) > 0.5
            col = RED if dead else DIM
            rect(c, x, 300, 250, 230, stroke=col, a=v * fa, sw=1.8, r=8)
            text(c, nm.split('  ')[0], x + 12, 330, 19, col, v * fa, 'serif')
            for q in range(6): disk(c, x + 18 + (q % 3) * 76, 360 + (q // 3) * 80, 36, 52, col, v * fa, fill=col, fa=0.12)
        rep = A.fade(2, 8.0)
        for k, x in enumerate([807, 1107]):
            rect(c, x + 8, 372, 36, 28, fill=AMBER, a=v * rep, fa=0.75 * v * rep, r=3)
        text(c, 'replica 1', 830, 600, 17, AMBER, v * rep, 'serif_i'); text(c, 'replica 2', 1130, 600, 17, AMBER, v * rep, 'serif_i')
        if A.p(2, 11.0, 0.6) > 0.5:
            cross(c, 915, 440, 26, RED, v * A.fade(2, 11.0))
            check(c, 1215, 440, 16, GREEN, v * A.fade(2, 12.5))
            text(c, 'one rack lost, data still served', 940, 680, 22, GREEN, v * A.fade(2, 12.5), 'serif_i', align='c')
    # ---------------- beat 3: remote mount + AFM
    v = vis(A, 3, n)
    if v > 0:
        sites = [(150, 300, 'Cluster A', 'owns the file system', BLUE), (830, 300, 'Cluster B', 'mounts it remotely', GREEN), (830, 580, 'Site C', 'AFM cache', AMBER)]
        for (x, y, nm, sub, col) in sites:
            rect(c, x, y, 300, 160, stroke=col, a=v, sw=2, r=10)
            text(c, nm, x + 16, y + 40, 26, col, v, 'serif'); text(c, sub, x + 16, y + 70, 18, DIM, v, 'serif_i')
        disk(c, 150 + 220, 300 + 70, 44, 66, BLUE, v, fill=BLUE, fa=0.2)
        a1 = A.fade(3, 3.0)
        arrow(c, 826, 380, 456, 380, GREEN, v * a1, 2.4)
        text(c, 'remote cluster mount', 641, 356, 20, GREEN, v * a1, 'serif_i', align='c')
        a2 = A.fade(3, 8.0)
        curve(c, [(300, 466), (300, 660), (560, 660), (826, 660)], AMBER, v * a2, 2.4, dash=[9, 6])
        text(c, 'asynchronous caching: disaster recovery, data sharing', 560, 710, 20, AMBER, v * a2, 'serif_i', align='c')
    # ---------------- beat 4: FPO + ECE
    v = vis(A, 4, n)
    if v > 0:
        for (x0_, ttl, sub, col, k0) in [(150, 'File Placement Optimizer', 'shared-nothing, 2012: each node’s own disks join the pool', BLUE, 3.0), (780, 'Erasure Code Edition', 'software only: declustered RAID on ordinary servers', GREEN, 9.0)]:
            text(c, ttl, x0_, 260, 25, col, v * A.fade(4, k0 - 2.0), 'serif')
            for line_i, ln in enumerate(wrap(sub, 17, 520, 'serif_i')):
                text(c, ln, x0_, 292 + line_i * 24, 17, DIM, v * A.fade(4, k0 - 2.0), 'serif_i')
            for k in range(4):
                a = A.fade(4, k0 + k * 0.5)
                x = x0_ + k * 150
                rect(c, x, 400, 124, 70, stroke=col, a=v * a, sw=1.6, r=7)
                text(c, f'node {k+1}', x + 62, 430, 17, col, v * a, 'serif', align='c')
                for q in range(3): disk(c, x + 16 + q * 34, 486, 26, 40, col, v * a, fill=col, fa=0.12)
            if A.fade(4, k0 + 2.5) > 0:
                bt = A.fade(4, k0 + 2.5)
                path = skia.Path(); path.moveTo(x0_, 560); path.lineTo(x0_, 574); path.lineTo(x0_ + 3 * 150 + 124, 574); path.lineTo(x0_ + 3 * 150 + 124, 560)
                c.drawPath(path, P(col, v * bt, 'stroke', 2))
                text(c, 'one pool', x0_ + 3 * 150 / 2 + 62, 606, 20, col, v * bt, 'serif_i', align='c')
    # ---------------- beat 5: Alpine table
    v = vis(A, 5, n)
    if v > 0:
        text(c, 'Alpine, the file system of Oak Ridge’s Summit', 150, 250, 28, INK, v, 'serif')
        rows = [('capacity', '250 PB'), ('NSD servers', '154'), ('network', 'EDR InfiniBand, 100 Gb/s'), ('block size', '16 MB'), ('peak, sequential', '≈ 2.5 TB/s'), ('peak, random', '≈ 2.2 TB/s'), ('small files, 32 KB', 'up to 2.6 million accesses/s')]
        for k, (lab, val) in enumerate(rows):
            a = A.fade(5, 1.5 + k * 2.4)
            y = 340 + k * 70
            line(c, 150, y + 22, 1300, y + 22, RULE, v * a, 0.8)
            text(c, lab, 150, y, 24, DIM, v * a, 'serif_i')
            text(c, val, 1300, y, 32, AMBER if k in (0, 4) else INK, v * a, 'serif', align='r')
    # ---------------- beat 6: then vs now
    v = A.p(6, 0.4, 0.9, smooth)
    if v > 0:
        text(c, 'ASCI White (2002)  →  Alpine', 150, 250, 26, INK, v, 'serif')
        # dumbbells (log scale)
        def dumbbell(y, lab, lo_v, hi_v, lo_txt, hi_txt, x_lo, x_hi, log_lo, log_hi, tstart, unit_note):
            a = A.fade(6, tstart)
            X = lambda g: x_lo + (math.log10(g) - log_lo) / (log_hi - log_lo) * (x_hi - x_lo)
            text(c, lab, 150, y + 7, 23, INK, v * a, 'serif')
            ap = A.p(6, tstart + 1.0, 1.8)
            xa, xb = X(lo_v), lerp(X(lo_v), X(hi_v), ap)
            line(c, xa, y, xb, y, DIM, v * a, 2)
            circle(c, xa, y, 10, fill=DIM, a=v * a)
            text(c, lo_txt, xa, y - 22, 19, DIM, v * a, 'serif', align='c')
            circle(c, xb, y, 10, fill=AMBER, a=v * a)
            if ap > 0.95:
                text(c, hi_txt, X(hi_v), y - 22, 19, AMBER, v, 'serif', align='c')
                text(c, f'×{hi_v / lo_v:,.0f}', (xa + X(hi_v)) / 2, y + 36, 24, GREEN, v * A.fade(6, tstart + 3.2), 'serif_i', align='c')
        dumbbell(360, 'capacity', 140e12, 250e15, '140 TB', '250 PB', 480, 1280, 14, 18, 2.5, '')
        dumbbell(500, 'bandwidth', 12.0, 2500.0, '12 GB/s', '2.5 TB/s', 480, 1280, 0.8, 3.6, 8.0, '')
        # time to read everything
        t_aw = 140e12 / 12e9 / 3600; t_al = 250e15 / 2.5e12 / 3600
        ba = A.fade(6, 14.0)
        text(c, 'time to read the whole file system once', 150, 620, 22, INK, v * ba, 'serif')
        for k, (lab, hrs, col) in enumerate([('ASCI White', t_aw, DIM), ('Alpine', t_al, AMBER)]):
            y = 680 + k * 70
            a = A.p(6, 15.5 + k * 3.0, 1.6)
            text(c, lab, 150, y + 7, 21, col, v * ba, 'serif')
            rect(c, 340, y - 16, 28 * 30 / 30 * hrs * 1.0 * a * 1.05, 32, fill=col, a=v, fa=0.8 * v * ba)
            text(c, f'{hrs:.1f} hours', 340 + hrs * 29.4 * a + 14, y + 7, 22, col, v * a, 'serif')
        text(c, 'rough comparison: different machines, years and measurements; the direction is the point', 150, 860, 17, FAINT, v * A.fade(6, 22.0), 'serif_i')

# ======================================================================= S8  the larger HPC universe
def s8(c, A):
    notes = [
        (1, 330, '1', 'Alpine slide 6: "each storage server is also metadata server." Lustre: dedicated metadata servers (MDS) and object storage servers (OSS).'),
        (2, 600, '2', 'OLCF Spectrum Scale on Summit workshop, slides 14–17: NAS BTIO write rate from 1,532 MB/s to as high as 35,509 MB/s with ROMIO hints (striping_unit, cb_config_list, romio_no_indep_rw).'),
    ]
    chrome(c, A, 'Where this sits, and what else is out there', 8, notes)
    n = 3
    v = vis(A, 0, n)
    if v > 0:
        tiers = [('node memory and local storage', 480, 'closest to the compute, smallest, fastest', BLUE), ('parallel file system (GPFS / Storage Scale)', 660, 'scratch and project data', AMBER), ('campaign storage and object stores', 840, 'bigger, cheaper, slower', GREEN), ('tape and archive', 1000, 'largest, coldest', DIM)]
        for k, (nm, w_, sub, col) in enumerate(tiers):
            a = A.fade(0, 1.5 + k * 3.5)
            y = 280 + k * 115
            x = 150 + (1000 - w_) / 2
            rect(c, x, y, w_, 86, stroke=col, a=v * a, sw=2, r=8, fill=col, fa=0.10 * v * a)
            text(c, nm, x + w_ / 2, y + 38, 21, col, v * a, 'serif', align='c')
            text(c, sub, x + w_ / 2, y + 66, 16, DIM, v * a, 'serif_i', align='c')
            if k < 3:
                arrow(c, 640, y + 90, 640, y + 112, DIM, v * a * 0.8, 1.6, 7)
                arrow(c, 660, y + 112, 660, y + 90, DIM, v * a * 0.8, 1.6, 7)
        pa = A.fade(0, 16.0)
        para(c, 'policy engines move data between the layers', 1190, 520, 250, 22, GREEN, v * pa, 'serif_i')
        text(c, 'capacity ↑  speed ↓', 1190, 640, 17, FAINT, v * pa, 'serif_i')
        text(c, '(qualitative)', 1190, 664, 15, FAINT, v * pa, 'serif_i')
        text(c, 'tier widths are illustrative, not to scale', 150, 925, 15, FAINT, v * pa, 'serif_i')
    v = vis(A, 1, n)
    if v > 0:
        for (x0_, ttl, col, kind) in [(150, 'Lustre, for contrast', GREEN, 'lustre'), (780, 'GPFS / Storage Scale', AMBER, 'gpfs')]:
            a = A.fade(1, 1.5 if kind == 'lustre' else 8.0)
            text(c, ttl, x0_, 270, 26, col, v * a, 'serif')
            for q in range(4): node(c, x0_ + 20 + q * 36, 360, 16, BLUE, v * a)
            text(c, 'clients', x0_ + 20, 335, 17, BLUE, v * a, 'serif_i')
            if kind == 'lustre':
                rect(c, x0_, 470, 240, 60, stroke=GREEN, a=v * a, sw=1.8, r=7); text(c, 'metadata servers', x0_ + 120, 507, 19, GREEN, v * a, 'serif', align='c')
                rect(c, x0_, 590, 240, 60, stroke=VIOLET, a=v * a, sw=1.8, r=7); text(c, 'object storage servers', x0_ + 120, 627, 19, VIOLET, v * a, 'serif', align='c')
                for (yy, cc) in [(470, GREEN), (590, VIOLET)]:
                    for q in range(4): line(c, x0_ + 20 + q * 36, 368, x0_ + 40 + q * 50, yy, cc, v * a * 0.35, 1.0)
                text(c, 'dedicated roles', x0_, 700, 18, DIM, v * a, 'serif_i')
            else:
                rect(c, x0_, 520, 400, 70, stroke=AMBER, a=v * a, sw=1.8, r=7); text(c, 'NSD servers: data and metadata', x0_ + 200, 562, 19, AMBER, v * a, 'serif', align='c')
                for q in range(4): line(c, x0_ + 20 + q * 36, 368, x0_ + 40 + q * 70, 520, AMBER, v * a * 0.35, 1.0)
                text(c, 'locks distributed as tokens', x0_, 640, 18, DIM, v * a, 'serif_i')
        text(c, 'different design philosophies, not a ranking', 960, 820, 24, INK, v * A.fade(1, 14.0), 'serif_i', align='c')
    v = A.p(2, 0.4, 0.9, smooth)
    if v > 0:
        text(c, 'same hardware, different I/O pattern', 150, 260, 28, INK, v, 'serif')
        text(c, 'NAS BTIO write rate on Summit, MB/s', 150, 296, 18, DIM, v, 'serif_i')
        gx = 150; gy = 760
        ba = A.p(2, 3.0, 2.0); bb = A.p(2, 8.0, 3.0)
        h1 = 1532 / 35509 * 380 * ba; h2 = 380 * bb
        rect(c, 300, gy - h1, 160, h1, fill=DIM, a=v, fa=0.8 * v)
        rect(c, 640, gy - h2, 160, h2, fill=AMBER, a=v, fa=0.85 * v)
        line(c, 220, gy, 900, gy, FAINT, v, 1.2)
        text(c, 'default', 380, gy + 34, 22, DIM, v, 'serif', align='c')
        text(c, 'tuned MPI-IO hints', 720, gy + 34, 22, AMBER, v, 'serif', align='c')
        text(c, '1,532', 380, gy - h1 - 14, 26, DIM, v * ba, 'serif', align='c')
        text(c, 'up to 35,509', 720, gy - h2 - 14, 26, AMBER, v * bb, 'serif', align='c')
        text(c, f'≈ {35509/1532:.0f}× faster', 900, 560, 42, GREEN, v * A.fade(2, 12.0), 'serif_i')
        text(c, 'tuning the application’s I/O, not the hardware', 900, 606, 17, DIM, v * A.fade(2, 14.0), 'serif_i')

# ======================================================================= S9  recap + references
def s9(c, A):
    chrome(c, A, 'What to carry away', 9)
    lines_ = [('Stripe everything across everything.', None, 0.5), ('Share the disks; distribute the intelligence.', 'tokens  ·  metanode  ·  logs on shared disks', 5.5), ('Protect the data in software.', 'declustered RAID, end-to-end checksums', 11.0)]
    v0 = 1 - A.p(2, 0.0, 1.0, smooth) * 0.0
    for k, (big, sub, dl) in enumerate(lines_):
        a = A.fade(0, dl)
        y = 270 + k * 130
        text(c, big, 150, y, 44, INK, a * (1 - A.p(2, 0.0, 1.0, smooth)), 'serif')
        if sub: text(c, sub, 150, y + 38, 22, AMBER, a * (1 - A.p(2, 0.0, 1.0, smooth)), 'serif_i')
    a = A.fade(1, 0.8) * (1 - A.p(2, 0.0, 1.0, smooth))
    text(c, 'Match the access pattern to the block.', 150, 270 + 3 * 130, 44, INK, a, 'serif')
    text(c, 'large, aligned, mostly independent  →  near the hardware’s limit', 150, 270 + 3 * 130 + 38, 22, GREEN, A.fade(1, 4.0) * (1 - A.p(2, 0.0, 1.0, smooth)), 'serif_i')
    text(c, 'small, shared, unaligned  →  fighting over tokens', 150, 270 + 3 * 130 + 70, 22, RED, A.fade(1, 8.0) * (1 - A.p(2, 0.0, 1.0, smooth)), 'serif_i')
    # references (endnotes)
    r = A.fade(2, 0.5, 1.2)
    if r > 0:
        panel = 0.0
        rect(c, 120, 150, 1700, 800, fill=BG, a=r, fa=0.96 * r)
        text(c, 'Sources', 150, 230, 34, INK, r, 'serif')
        refs = [
            'F. Schmuck, R. Haskin. “GPFS: A Shared-Disk File System for Large Computing Clusters.” FAST ’02, pp. 231–244.',
            'IBM. Spectrum Scale RAID Administration (raid_adm); IBM Community, “ESS fault tolerance,” 2018; IBM Spectrum Scale RAID FAQ.',
            'OLCF. “Spectrum Scale on Summit” workshop slides, Dec 2018; OLCF Summit system page.',
            'IBM. “Spectrum Scale: concepts and features,” SC19, via gpfsug.org.',
            'Blocks & Files. “Spectrum no more: IBM dropping brand name for storage products,” 24 Feb 2023.',
            'Wikipedia. “GPFS” (Vesta, Tiger Shark, release history, FPO).',
            'G. Klockwood. IO500 notes (ior-hard definition).',
        ]
        for k, rf in enumerate(refs):
            a2 = A.fade(2, 1.5 + k * 1.1)
            y = 290 + k * 62
            text(c, str(k + 1), 150, y, 20, AMBER, r * a2, 'sans_m')
            para(c, rf, 190, y, 1500, 21, DIM, r * a2, 'serif')
        text(c, 'Toy simulations and illustrative models are my own; their assumptions are shown on screen.', 150, 790, 19, FAINT, r * A.fade(2, 9.5), 'serif_i')
        text(c, 'Next: Lustre, and where the philosophies diverge.', 150, 860, 28, AMBER, r * A.fade(2, 12.0), 'serif_i')
