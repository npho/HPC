import math, random, json
from fx import *
from lx import *

# ======================================================================= S7  scaling metadata
def s7(c, A):
    notes = [
        (1, 200, '1', 'Wikipedia: DNE in 2.4 (May 2013, subdirectory trees on separate MDTs); 2.7+ distributes large single directories; 2.15 default directory layouts round-robin and space-balanced.'),
        (2, 400, '2', 'Wikipedia: Data-on-MDT and FLR in 2.11 (Apr 2018); PFL in 2.10 (Jul 2017).'),
        (4, 600, '3', 'Admin docs: max file size 31.25 PiB (ldiskfs) vs 8 EiB (ZFS). Wikipedia: ZFS backend since 2.4; ldiskfs is an enhanced ext4.'),
        (5, 780, '4', 'Admin docs: after the default 100 s timeout a client is evicted, its locks revoked and dirty cache discarded.'),
        (6, 900, '5', 'Admin docs limits: 8150 OSTs, 256 MDTs, 131,072 clients (30,000+ tested in production). Schwan 2003 goal: "tens of thousands of clients and petabytes of data."'),
    ]
    chrome(c, A, 'Stretching the metadata side', 7, notes)
    n = 7
    # 0: funnel
    v = vis(A, 0, n)
    if v > 0:
        for i in range(24):
            x = 160 + (i % 8) * 40; y = 300 + (i // 8) * 40
            node(c, x, y, 16, BLUE, v)
            ph = (A.t * 0.7 + i * 0.13) % 1
            pkt(c, [(x, y), (900, 460)], ph, AMBER, v * 0.9, 6)
        server(c, 880, 430, 130, 56, AMBER, v, lit=0.6 + 0.3 * math.sin(A.t * 6))
        text(c, 'one MDS', 945, 418, 22, AMBER, v, 'sans_m', align='c')
        text(c, 'every create, stat, rename in the system', 540, 650, 24, INK, v * A.fade(0, 3.0), 'serif', align='c')
        text(c, 'funnels through one machine', 540, 690, 24, RED, v * A.fade(0, 5.0), 'serif', align='c')
    # 1: DNE
    v = vis(A, 1, n)
    if v > 0:
        text(c, 'Distributed Namespace Environment', 150, 240, 24, INK, v, 'serif')
        # tree
        root = (400, 320)
        subs = [(240, 440, AMBER, 'MDT 0'), (460, 440, BLUE, 'MDT 1'), (680, 440, GREEN, 'MDT 2')]
        node(c, *root, 22, INK, v)
        for q, (x, y, col, lab) in enumerate(subs):
            a_ = v * A.fade(1, 1.0 + q * 2.0)
            line(c, root[0], root[1] + 12, x, y - 12, FAINT, a_, 1.4); node(c, x, y, 22, col, a_)
            text(c, lab, x, y + 40, 17, col, a_, 'sans_m', align='c')
            for k in range(3):
                xx = x - 50 + k * 50; yy = y + 120
                line(c, x, y + 12, xx, yy - 8, FAINT, a_ * 0.6, 1); rect(c, xx - 8, yy - 8, 16, 16, fill=col, a=a_, fa=0.5 * a_, r=2)
        text(c, 'subtrees on different targets (2.4)', 150, 760, 21, AMBER, v * A.fade(1, 1.0), 'serif_i')
        b = A.fade(1, 8.0)
        if b > 0:
            text(c, 'one huge directory, sharded', 1030, 300, 22, INK, v * b, 'serif', align='c')
            for k in range(12):
                col = [AMBER, BLUE, GREEN][k % 3]
                rect(c, 900 + (k % 6) * 38, 340 + (k // 6) * 38, 32, 32, fill=col, a=v * b, fa=0.55 * b, r=3)
            text(c, 'new directories placed round-robin', 1030, 480, 18, DIM, v * A.fade(1, 11.0), 'serif_i', align='c')
            text(c, 'or by free space (2.15)', 1030, 508, 18, DIM, v * A.fade(1, 11.0), 'serif_i', align='c')
    # 2: DoM
    v = vis(A, 2, n)
    if v > 0:
        for (x, ti, col, steps_) in [(380, 'before', RED, 2), (1000, 'Data on MDT (2.11)', GREEN, 1)]:
            text(c, ti, x, 260, 25, col, v, 'serif', align='c')
            node(c, x - 190, 520, 24, BLUE, v); server(c, x + 20, 340, 100, 34, AMBER, v); text(c, 'MDS', x + 70, 330, 16, AMBER, v, 'sans_m', align='c')
            if steps_ == 2: server(c, x + 20, 640, 100, 34, VIOLET, v); text(c, 'OSS', x + 70, 630, 16, VIOLET, v, 'sans_m', align='c')
        f = A.p(2, 1.0, 0.9)
        if f > 0: arrow(c, 210, 505, lerp(210, 400, f), 365, AMBER, v, 2); text(c, 'layout', 230, 420, 16, AMBER, v * f, 'serif_i')
        f = A.p(2, 3.5, 0.9)
        if f > 0: arrow(c, 210, 540, lerp(210, 400, f), 650, BLUE, v, 2); text(c, 'data', 250, 610, 16, BLUE, v * f, 'serif_i')
        f = A.p(2, 7.5, 0.9)
        if f > 0: arrow(c, 830, 505, lerp(830, 1020, f), 365, GREEN, v, 3); text(c, 'layout + first piece of the file', 820, 420, 16, GREEN, v * f, 'serif_i')
        text(c, 'small files served from one place', 690, 840, 24, INK, v * A.fade(2, 9.5), 'serif', align='c')
    # 3: PFL / FLR
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'one file, different layout per region (PFL, 2.10)', 150, 250, 23, INK, v, 'serif')
        segs = [(0, 0.25, 1, 'first part:\n1 stripe', BLUE), (0.25, 0.6, 4, 'growing:\n4 stripes', GREEN), (0.6, 1.0, 12, 'large:\nmany stripes', AMBER)]
        x0, W = 170, 1000
        for q, (a0, a1, st, lab, col) in enumerate(segs):
            a_ = v * A.fade(3, 1.0 + q * 2.4)
            for s_ in range(min(st, 6)):
                rect(c, x0 + a0 * W + 2, 330 + s_ * 20, (a1 - a0) * W - 4, 17, fill=col, a=a_, fa=0.6 * a_, r=2)
            for li, ln in enumerate(lab.split('\n')): text(c, ln, x0 + (a0 + a1) / 2 * W, 490 + li * 24, 18, col, a_, 'serif_i', align='c')
        b = A.fade(3, 8.5)
        text(c, 'file level redundancy (2.11): mirrored layouts', 150, 650, 23, INK, v * b, 'serif')
        for m in range(2):
            rect(c, 170, 690 + m * 56, 1000, 40, fill=BLUE if m == 0 else VIOLET, a=v * b, fa=0.35 * b, stroke=BLUE if m == 0 else VIOLET, sw=1.3, r=4)
            text(c, f'mirror {m+1}', 190, 717 + m * 56, 17, INK, v * b, 'sans')
        text(c, 'availability and read performance', 170, 830, 20, DIM, v * b, 'serif_i')
    # 4: backends
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'underneath: a local file system on each target', 150, 250, 24, INK, v, 'serif')
        for (x, ti, col, d1, d2) in [(330, 'ldiskfs', DIM, 'a modified ext4', 'max file ≈ 31 PiB'), (880, 'ZFS (since 2.4)', GREEN, 'checksums, software RAID', 'max file 8 EiB')]:
            a_ = v * A.fade(4, 1.0 + (x > 500) * 4.0)
            rect(c, x - 200, 320, 400, 250, stroke=col, a=a_, sw=1.6, r=10)
            text(c, ti, x, 380, 30, col if col != DIM else INK, a_, 'title', align='c')
            text(c, d1, x, 440, 21, INK, a_, 'serif_i', align='c')
            text(c, d2, x, 500, 24, AMBER, a_, 'serif', align='c')
        text(c, 'Orion uses ZFS (next scene)', 690, 680, 21, DIM, v * A.fade(4, 9.0), 'serif_i', align='c')
    # 5: failure
    v = vis(A, 5, n)
    if v > 0:
        text(c, 'a client goes silent', 150, 250, 24, INK, v, 'serif')
        x0, x1 = 170, 1170
        line(c, x0, 420, x1, 420, FAINT, v, 1.5)
        for q, (t_, lab) in enumerate([(0, 'last contact'), (100, 'timeout: 100 s (default)')]):
            xx = lerp(x0, x1, t_ / 130)
            line(c, xx, 400, xx, 440, INK, v, 1.5); text(c, lab, xx, 470, 18, DIM, v, 'serif_i', align='c')
        pr = A.p(5, 1.5, 4.0)
        rect(c, x0, 405, (lerp(x0, x1, 100 / 130) - x0) * pr, 30, fill=AMBER, a=v, fa=0.5 * v, r=3)
        f = A.fade(5, 6.0)
        if f > 0:
            xx = lerp(x0, x1, 100 / 130)
            cross(c, xx, 420, 14, RED, v * f, 3)
            for q, s_ in enumerate(['evicted: its locks are revoked', 'its unwritten cached data is discarded', 'it must remount']):
                text(c, '• ' + s_, 170, 570 + q * 40, 22, RED if q else INK, v * A.fade(5, 6.5 + q * 1.6), 'serif')
        text(c, 'server pairs: a partner mounts the dead server\'s targets', 170, 760, 21, GREEN, v * A.fade(5, 12.0), 'serif_i')
    # 6: limits dumbbell-ish
    v = A.fade(6, 0.4)
    if v > 0:
        text(c, 'documented limits today', 150, 250, 24, INK, v, 'serif')
        rows = [('clients', '131,072', '30,000+ tested in production'), ('object storage targets', '8,150', ''), ('metadata targets', '256', ''), ('stripes per file', '2,000', '')]
        for q, (k, val, sub) in enumerate(rows):
            y = 340 + q * 100
            a_ = v * A.fade(6, 0.8 + q * 1.8)
            text(c, k, 190, y, 23, DIM, a_, 'serif_i')
            text(c, val, 620, y, 48, AMBER, a_, 'sans_b')
            if sub: text(c, sub, 900, y, 19, GREEN, a_, 'serif_i')
        text(c, '2003 goal: "tens of thousands of clients"', 190, 780, 22, DIM, v * A.fade(6, 9.5), 'serif_i')

# ======================================================================= S8  Orion
def s8(c, A):
    notes = [
        (0, 180, '1', 'OLCF Orion page: Lustre with ZFS, HPE ClusterStor, ~500 server nodes, 50 cabinets, "around 700 PB." Frontier was No. 1 on the TOP500 in 2022 (Wikipedia).'),
        (1, 340, '2', 'OLCF / insideHPC: metadata 480 NVMe, ~10 PB; performance 5,400 NVMe, 11.5 PB; capacity 47,700 HDD, 679 PB. LUG 2023 slides give the raw sizes as 9.7, 11.4 and 667.6 PB.'),
        (2, 560, '3', 'LUG 2023 Orion slides: 2 MGS, 40 MDS, 450 OSS, 169 LNet routers; ZFS 2.1.7, dRAID inside each enclosure; Lustre 2.15 with vendor patches.'),
        (3, 740, '4', 'LUG 2023 slides: 0-256K DoM; 256K-8M 1 stripe on the performance pool; 8M-128G 1 stripe on capacity; 128G-EOF 8 stripes on capacity; 1M stripe size.'),
        (5, 900, '5', 'The OLCF page and insideHPC swap read and write for the disk tier (5.5 vs 4.6 TB/s), so I use "about 5". Ratios vs ASCI White are mine: 679 PB / 140 TB ≈ 4,850; 10 TB/s / 12 GB/s ≈ 830.'),
    ]
    chrome(c, A, 'A real one: Orion on Frontier', 8, notes)
    n = 6
    v = vis(A, 0, n)
    if v > 0:
        text(c, 'Orion', 660, 360, 110, AMBER, v, 'title', align='c')
        text(c, 'the file system of Frontier, Oak Ridge', 660, 430, 26, DIM, v * A.fade(0, 1.5), 'serif_i', align='c')
        tiles = [('≈ 700 PB', 'total'), ('Lustre + ZFS', 'open source'), ('HPE ClusterStor', 'hardware'), ('≈ 500', 'server nodes')]
        for q, (a1, a2) in enumerate(tiles):
            a_ = v * A.fade(0, 3.0 + q * 2.2)
            x = 250 + q * 270
            text(c, a1, x, 580, 30, INK, a_, 'serif', align='c'); text(c, a2, x, 614, 18, DIM, a_, 'serif_i', align='c')
            line(c, x - 100, 545, x + 100, 545, RULE, a_, 1)
    v = vis(A, 1, n)
    if v > 0:
        rows = [('metadata', 'NVMe flash', '480 drives', 10, AMBER), ('performance', 'NVMe flash', '5,400 drives', 11.5, BLUE), ('capacity', 'hard disk', '47,700 drives', 679, VIOLET)]
        for q, (nm, md, dr, pb, col) in enumerate(rows):
            a_ = v * A.fade(1, 0.8 + q * 3.5)
            y = 330 + q * 150
            text(c, nm, 150, y - 14, 25, col, a_, 'serif')
            text(c, f'{md} · {dr}', 150, y + 18, 18, DIM, a_, 'serif_i')
            wbar = max(pb / 679 * 780, 6) * A.p(1, 1.0 + q * 3.5, 1.2, ease_out)
            rect(c, 470, y - 34, wbar, 52, fill=col, a=a_, fa=0.7 * a_, r=3)
            text(c, f'{pb:g} PB', 470 + wbar + 14, y + 4, 26, INK, a_, 'serif')
        text(c, 'bars to scale', 470, 800, 17, FAINT, v, 'serif_i')
    v = vis(A, 2, n)
    if v > 0:
        items = [('management', 2, INK), ('metadata servers', 40, AMBER), ('object storage servers', 450, VIOLET), ('LNet routers', 169, BLUE)]
        y = 260
        for q, (nm, cnt, col) in enumerate(items):
            a_ = v * A.fade(2, 0.6 + q * 3.2)
            text(c, f'{cnt}', 150, y + 40, 52, col, a_, 'sans_b')
            text(c, nm, 290, y + 38, 22, DIM, a_, 'serif_i')
            per_row = 75; sz = 12
            for i in range(cnt):
                if i / cnt > A.p(2, 0.6 + q * 3.2, 1.5): break
                rect(c, 560 + (i % per_row) * 10.5, y + 8 + (i // per_row) * 14, 8, 11, fill=col, a=a_, fa=0.75 * a_, r=1)
            y += 100 if cnt < 100 else (130 if cnt > 300 else 100)
        text(c, 'drives grouped by ZFS declustered RAID inside each enclosure', 150, 780, 21, GREEN, v * A.fade(2, 14.0), 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'default progressive layout: where each part of a file lives', 150, 250, 22, INK, v, 'serif')
        # log axis 64K..1T
        lo, hi = math.log2(64 * 1024), math.log2(2 * 1024**4)
        gx, gw = 170, 1100
        Xl = lambda b: gx + (math.log2(b) - lo) / (hi - lo) * gw
        segs = [(64 * 1024, 256 * 1024, AMBER, 'on the MDT (flash)', 'first 256 KB'), (256 * 1024, 8 * 1024**2, BLUE, 'one flash OST', '256 KB – 8 MB'),
                (8 * 1024**2, 128 * 1024**3, VIOLET, 'one disk OST', '8 MB – 128 GB'), (128 * 1024**3, 2 * 1024**4, GREEN, '8 disk OSTs', '128 GB →')]
        prog = A.pf(3, 0.05, 0.9)
        for q, (b0, b1, col, lab, rng_) in enumerate(segs):
            xa, xb = Xl(b0), Xl(b1)
            w = max(0, min(xb, gx + (gw * prog)) - xa) if True else 0
            w = max(0.0, min(xb - xa, gx + gw * prog - xa))
            rect(c, xa, 380, w, 70, fill=col, a=v, fa=0.65 * v, r=2)
            if w > (xb - xa) * 0.9:
                yl = 332 if q % 2 == 0 else 492
                text(c, lab, (xa + xb) / 2, yl, 19, col, v, 'serif', align='c')
                text(c, rng_, (xa + xb) / 2, yl + 24, 15, DIM, v, 'serif_i', align='c')
        for b_, lb in [(64 * 1024, '64 KB'), (1024**2, '1 MB'), (1024**3, '1 GB'), (1024**4, '1 TB')]:
            text(c, lb, Xl(b_), 540, 15, DIM, v, 'sans', align='c'); line(c, Xl(b_), 450, Xl(b_), 460, FAINT, v)
        text(c, 'file size (log scale)', gx + gw, 575, 16, DIM, v, 'serif_i', align='r')
        text(c, 'a file moves outward through the tiers as it grows', 660, 680, 25, INK, v * A.fade(3, 8.0), 'serif', align='c')
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'below 8 MB, a file never touches a hard disk', 660, 330, 32, GREEN, v, 'serif', align='c')
        rows = [('one namespace', 'users see one tree'), ('different rules by size', 'set once, as the default layout'), ('an architecture decision', 'not a hardware trick')]
        for q, (a1, a2) in enumerate(rows):
            a_ = v * A.fade(4, 3.0 + q * 3.0)
            text(c, a1, 330, 480 + q * 80, 28, INK, a_, 'serif'); text(c, a2, 760, 480 + q * 80, 21, DIM, a_, 'serif_i')
    v = A.fade(5, 0.4)
    if v > 0:
        text(c, 'peak bandwidth (TB/s), as listed by Oak Ridge', 150, 250, 22, INK, v, 'serif')
        for q, (nm, val, col) in enumerate([('flash tier', 10, BLUE), ('disk tier', 5, VIOLET)]):
            a_ = v * A.fade(5, 0.8 + q * 2.5)
            y = 340 + q * 80
            text(c, nm, 150, y + 6, 22, col, a_, 'serif')
            rect(c, 330, y - 22, val * 70 * A.p(5, 0.8 + q * 2.5, 1.2, ease_out), 40, fill=col, a=a_, fa=0.7 * a_, r=3)
            text(c, ('about ' if q else '≈ ') + f'{val}', 330 + val * 70 + 14, y + 6, 24, INK, a_, 'serif')
        b = A.fade(5, 8.0)
        if b > 0:
            text(c, 'versus the GPFS machine in the 2002 paper (derived by me, direction only)', 150, 560, 20, DIM, v * b, 'serif_i')
            for q, (a1, a2, col) in enumerate([('≈ 4,850×', 'capacity', GREEN), ('≈ 830×', 'bandwidth (flash tier)', GREEN)]):
                a_ = v * A.fade(5, 9.5 + q * 2.2)
                text(c, a1, 330 + q * 480, 650, 62, col, a_, 'title', align='c')
                text(c, a2, 330 + q * 480, 695, 20, DIM, a_, 'serif_i', align='c')

# ======================================================================= S9  compare + recap + sources
def s9(c, A):
    notes = [
        (1, 260, '1', 'My architectural summary of the two designs as described in the GPFS FAST \'02 paper and the Lustre sources. Not a benchmark.'),
        (3, 560, '2', 'I did not find a fair, same-hardware GPFS vs Lustre benchmark. Treat any single-number claim of superiority with suspicion.'),
    ]
    chrome(c, A, 'Two designs, side by side', 9, notes)
    n = 6
    v = vis(A, 0, n)
    if v > 0:
        text(c, 'what they share', 150, 250, 26, INK, v, 'serif')
        for q, s_ in enumerate(['stripe files across many servers', 'POSIX semantics via byte-range locking', 'metadata on flash these days', 'machines at the top of the Top500']):
            a_ = v * A.fade(0, 1.0 + q * 3.0)
            check(c, 170, 330 + q * 70, 11, GREEN, a_); text(c, s_, 210, 340 + q * 70, 26, INK, a_, 'serif')
    v = vis(A, 1, n)
    if v > 0:
        for (x, ti, col, kind) in [(380, 'GPFS', BLUE, 0), (1000, 'Lustre', AMBER, 1)]:
            text(c, ti, x, 250, 38, col, v, 'title', align='c')
            for i in range(5): node(c, x - 160 + i * 80, 340, 22, BLUE, v)
            for j in range(4): disk(c, x - 150 + j * 100, 600, 28, 44, DIM, v, fill=DIM, fa=0.2)
            if kind == 0:
                for i in range(5):
                    for j in range(4): line(c, x - 160 + i * 80, 352, x - 136 + j * 100, 598, VIOLET, v * 0.35, 1)
                text(c, 'any node → any disk', x, 700, 22, INK, A.fade(1, 3.0) * v, 'serif', align='c')
                text(c, 'tokens; log replayed by another node', x, 732, 18, DIM, A.fade(1, 3.0) * v, 'serif_i', align='c')
            else:
                for j in range(4): server(c, x - 175 + j * 100, 480, 70, 26, VIOLET, v); line(c, x - 140 + j * 100, 506, x - 136 + j * 100, 598, DIM, v, 1.2)
                for i in range(5):
                    for j in range(4): line(c, x - 160 + i * 80, 352, x - 140 + j * 100, 480, BLUE, v * 0.22, 1)
                text(c, 'client ↔ the server that owns the target', x, 700, 22, INK, A.fade(1, 8.0) * v, 'serif', align='c')
                text(c, 'clients are only clients', x, 732, 18, DIM, A.fade(1, 8.0) * v, 'serif_i', align='c')
    v = vis(A, 2, n)
    if v > 0:
        for (x, ti, col, lines_) in [(380, 'GPFS', BLUE, ['metadata work distributed across nodes by design', 'metanode per file, token managers by inode']), (1000, 'Lustre', AMBER, ['metadata scaling is a feature you add (DNE)', 'data path: client, network, server, disk'])]:
            text(c, ti, x, 280, 36, col, v, 'title', align='c')
            for q, s_ in enumerate(lines_):
                text(c, s_, x, 380 + q * 70, 21, INK, v * A.fade(2, 1.0 + q * 4.0 + (x > 500) * 0.0), 'serif', align='c')
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'which is faster?', 660, 420, 60, INK, v, 'title', align='c')
        text(c, 'not answered by architecture alone', 660, 490, 26, DIM, v * A.fade(3, 2.5), 'serif_i', align='c')
        text(c, 'no fair same-hardware benchmark seen', 660, 550, 24, AMBER, v * A.fade(3, 5.5), 'serif', align='c')
    v = vis(A, 4, n)
    if v > 0:
        lv = [('node-local flash, burst buffers', 'above', BLUE, 560, 0), ('Lustre / GPFS: shared, always-on', 'the middle', AMBER, 700, 1), ('archives and tape', 'below', DIM, 840, 2)]
        for lab, rel, col, w, q in lv:
            a_ = v * A.fade(4, 0.8 + q * 4.0)
            y = 330 + q * 130
            rect(c, 660 - w / 2, y, w, 100, fill=col, a=a_, fa=0.18 * a_, stroke=col, sw=1.6, r=8)
            text(c, lab, 660, y + 60, 26, col if col != DIM else INK, a_, 'serif', align='c')
            text(c, rel, 660 - w / 2 - 20, y + 56, 18, DIM, a_, 'serif_i', align='r')
    v = A.fade(5, 0.4)
    if v > 0:
        text(c, 'recap', 150, 250, 26, DIM, v, 'serif_i')
        pts = [('metadata and data are separate', AMBER), ('a file is a layout of objects on targets', BLUE), ('clients get the layout once, then go direct', VIOLET), ('locks keep it coherent; LNet moves the bytes', GREEN), ('DNE, PFL and Data-on-MDT keep stretching it', INK)]
        for q, (s_, col) in enumerate(pts):
            text(c, s_, 150, 320 + q * 56, 26, col, v * A.fade(5, 1.0 + q * 3.5), 'serif')
        srcs = A.fade(5, 16.5)
        if srcs > 0:
            rect(c, 100, 120, 1290, 880, fill=BG, a=srcs, fa=srcs)
            text(c, 'sources', 150, 200, 28, INK, srcs, 'serif')
            L = ['Cluster File Systems, "Lustre: A Scalable, High-Performance File System," white paper v1.0, Nov 2002',
                 'P. Schwan, "Lustre: Building a File System for 1,000-node Clusters," Linux Symposium 2003',
                 'Wikipedia, "Lustre (file system)": history, release timeline, limits',
                 'wiki.lustre.org, "Lustre Architecture for Admins"; "Understanding Lustre Internals"',
                 'OLCF, Orion file system page; insideHPC, "Orion: Frontier\'s Massive File System" (2023)',
                 'Lustre User Group 2023, Orion talk (OpenSFS)',
                 'Schmuck & Haskin, GPFS, USENIX FAST \'02 (for the comparison)',
                 'my own: sim_stripe.py (toy balance simulation), bandwidth model, ratios: all labelled on screen']
            for q, s_ in enumerate(L):
                for q2, ln in enumerate(wrap(s_, 21, 1100)):
                    text(c, ln, 150, 262 + q * 62 + q2 * 26, 21, INK if q < 7 else AMBER, srcs * A.fade(5, 17.3 + q * 0.55), 'serif')
