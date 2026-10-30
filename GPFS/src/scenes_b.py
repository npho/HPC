import math, random, json
from fx import *

def vis(A, i, n_lines, d_in=0.9, d_out=0.9, delay=0.2):
    """visibility of beat i: fades in at its cue, fades out when the next beat starts"""
    a = A.p(i, delay, d_in, smooth)
    if i + 1 < n_lines: a *= 1 - A.p(i + 1, 0.0, d_out, smooth)
    return a

def chip(c, x, y, label, color=AMBER, a=1.0, w=None, size=15):
    w = w or (tw(label, size, 'sans_m') + 18)
    rect(c, x - w / 2, y - 14, w, 28, fill=color, a=a, fa=0.9 * a, r=6)
    text(c, label, x, y + 6, size, BG, a, 'sans_b', align='c')

# ======================================================================= S4  tokens
def s4(c, A):
    notes = [
        (0, 150, '1', 'The paper: GPFS "guarantees single-node equivalent POSIX semantics for file system operations across the cluster."'),
        (2, 360, '2', '"The first node to write to a file will acquire a byte-range token for the whole file." Ranges are rounded to block boundaries. Schmuck & Haskin.'),
        (4, 600, '3', '"Only the metanode reads or writes the inode from or to disk." Data shipping is used mainly for fine-grained MPI-IO sharing. Schmuck & Haskin.'),
        (5, 800, '4', 'OLCF Spectrum Scale on Summit workshop, slide 8: IO500, 504 nodes × 2 processes per node, GB/s as reported. ior-hard = 47,008-byte interleaved writes to one shared file (G. Klockwood).'),
    ]
    chrome(c, A, 'Second idea: tokens, not a central lock server', 4, notes)
    n = 7
    # ---------------- beat 0: POSIX promise
    v = vis(A, 0, n)
    if v > 0:
        lanes = [(250, 'process A', BLUE), (620, 'shared file', DIM), (990, 'process B', GREEN)]
        for x, lab, col in lanes:
            rect(c, x - 75, 230, 150, 44, stroke=col, a=v, sw=1.6, r=6)
            text(c, lab, x, 260, 20, col, v, 'serif', align='c')
            line(c, x, 274, x, 560, FAINT, v, 1.2, dash=[5, 5])
        a1 = A.p(0, 3.0, 1.0)
        if a1 > 0:
            xe = lerp(250, 620, a1)
            arrow(c, 250, 350, xe, 350, AMBER, v, 2.2)
            text(c, 'write x = 1', 435, 336, 19, AMBER, v * a1, 'serif_i', align='c')
        a2 = A.p(0, 7.0, 1.0)
        if a2 > 0:
            arrow(c, 990, 450, lerp(990, 620, a2), 450, GREEN, v, 2.2)
            text(c, 'read x', 805, 436, 19, GREEN, v * a2, 'serif_i', align='c')
        a3 = A.p(0, 9.0, 1.0)
        if a3 > 0:
            arrow(c, 620, 500, lerp(620, 990, a3), 500, GREEN, v, 2.2, dash=[7, 5])
            text(c, 'x = 1', 805, 526, 19, GREEN, v * a3, 'serif_i', align='c')
        if A.p(0, 10.5, 0.5) > 0:
            check(c, 1060, 500, 11, GREEN, v * A.p(0, 10.5, 0.5))
        text(c, 'same promise as one machine', 620, 610, 22, INK, v * A.fade(0, 11.0), 'serif_i', align='c')
        # naive alternative
        b = A.fade(0, 14.0, 1.2)
        if b > 0:
            bx, by = 1240, 420
            rect(c, bx - 60, by - 30, 120, 60, stroke=RED, a=v * b, sw=2, r=8)
            text(c, 'one lock', bx, by - 4, 18, RED, v * b, 'serif', align='c')
            text(c, 'server?', bx, by + 18, 18, RED, v * b, 'serif', align='c')
            for k in range(10):
                yy = 250 + k * 36
                arrow(c, 1130, yy + 6 if yy < by else yy - 6, bx - 62, by + (yy - by) * 0.25, RED, v * b * 0.5, 1.2, 6)
            text(c, 'every operation waits in line', bx, 640, 18, RED, v * b, 'serif_i', align='c')
    # ---------------- beat 1: the token
    v = vis(A, 1, n)
    if v > 0:
        mx, my = 700, 270
        rect(c, mx - 120, my - 32, 240, 64, stroke=AMBER, a=v, sw=1.8, r=8)
        text(c, 'token manager', mx, my + 6, 22, AMBER, v, 'serif', align='c')
        ax, ay = 400, 600
        rect(c, ax - 90, ay - 32, 180, 64, stroke=BLUE, a=v, sw=1.8, r=8)
        text(c, 'node A', ax, ay + 6, 22, BLUE, v, 'serif', align='c')
        rect(c, 880, 570, 170, 60, stroke=DIM, a=v, sw=1.4, r=6)
        text(c, 'file X', 965, 607, 21, DIM, v, 'serif', align='c')
        # request / grant
        r1 = A.p(1, 3.0, 1.2)
        g1 = A.p(1, 5.0, 1.5)
        if r1 > 0:
            arrow(c, ax + 20, ay - 36, lerp(ax + 20, mx - 40, r1), lerp(ay - 36, my + 34, r1), BLUE, v, 2.0)
            text(c, 'request: write X', ax - 40, 430, 19, BLUE, v * r1, 'serif_i', align='r')
        has = A.p(1, 6.5, 0.8, smooth)
        if g1 > 0 and g1 < 1:
            x = lerp(mx - 20, ax + 40, g1); y = lerp(my + 34, ay - 36, g1)
            chip(c, x, y, 'token', AMBER, v)
        if has > 0:
            chip(c, ax + 40, ay - 52, 'write token · X', AMBER, v * has, 200)
        # local ops counter vs messages
        lo = A.p(1, 8.5, 9.0, f=lambda x: clamp01(x))
        ops = int(lo * 10000 // 1)
        text(c, 'operations done locally', 1120, 330, 20, DIM, v * A.fade(1, 8.5), 'serif_i')
        text(c, f'{ops:,}', 1120, 400, 62, GREEN, v * A.fade(1, 8.5), 'title')
        text(c, 'messages to the token manager', 1120, 470, 20, DIM, v * A.fade(1, 8.5), 'serif_i')
        text(c, '1' if has > 0.5 else '0', 1120, 540, 62, AMBER, v * A.fade(1, 8.5), 'title')
        text(c, 'schematic', 1120, 600, 15, FAINT, v * A.fade(1, 8.5), 'serif_i')
    # ---------------- beat 2: byte ranges
    v = vis(A, 2, n)
    if v > 0:
        fx0, fx1, fy = 250, 1250, 540
        rect(c, fx0, fy, fx1 - fx0, 56, stroke=DIM, a=v, sw=1.6)
        for k in range(1, 20): line(c, fx0 + k * (fx1 - fx0) / 20, fy, fx0 + k * (fx1 - fx0) / 20, fy + 56, RULE, v * 0.7, 1.0)
        text(c, 'byte 0', fx0, fy + 86, 17, DIM, v, 'sans', align='c')
        text(c, 'end of file', fx1, fy + 86, 17, DIM, v, 'sans', align='c')
        split = A.p(2, 10.0, 2.0)
        mid = lerp(fx1, (fx0 + fx1) / 2, split)
        # A's token
        bracket(c, fx0, mid - 6, fy - 24, 14, BLUE, v, 3)
        text(c, 'node A: write token for [0, ∞)' if split < 0.5 else 'node A: [0, ½)', fx0, fy - 56, 21, BLUE, v * A.fade(2, 2.0), 'serif')
        # B's token
        if split > 0:
            bracket(c, mid + 6, fx1, fy - 24, 14, GREEN, v * split, 3)
            text(c, 'node B: [½, ∞)', fx1, fy - 56, 21, GREEN, v * split, 'serif', align='r')
        # request annotation
        rq = A.fade(2, 7.5) * (1 - A.p(2, 12.5, 1.0, smooth))
        text(c, 'B asks for the back half  →  A gives up part of its range', 760, 380, 21, AMBER, v * rq, 'serif_i', align='c')
        # writing progress
        wa = A.p(2, 3.0, 6.0, f=lambda x: clamp01(x))
        wa_end = lerp(fx0, fx1, wa)
        if split == 0:
            rect(c, fx0, fy + 8, (wa_end - fx0) * 0.9, 40, fill=BLUE, a=v, fa=0.55 * v)
        else:
            wA = A.p(2, 12.5, 9.0, f=lambda x: clamp01(x))
            rect(c, fx0, fy + 8, lerp((fx1 - fx0) * 0.45, (mid - fx0 - 8), wA), 40, fill=BLUE, a=v, fa=0.55 * v)
            rect(c, mid + 8, fy + 8, wA * (fx1 - mid - 8), 40, fill=GREEN, a=v, fa=0.55 * v)
            text(c, 'both writing in parallel, no further coordination', 760, 700, 22, INK, v * A.fade(2, 14.0), 'serif_i', align='c')
    # ---------------- beat 3: false sharing vs aligned
    v = vis(A, 3, n)
    if v > 0:
        for m, (x0_, ttl, aligned) in enumerate([(180, 'writes inside the same block', False), (780, 'block-aligned writes', True)]):
            text(c, ttl, x0_, 260, 24, INK, v, 'serif')
            for b in range(4):
                rect(c, x0_ + b * 130, 400, 120, 70, stroke=DIM, a=v, sw=1.5)
            text(c, 'file blocks', x0_, 500, 15, FAINT, v, 'serif_i')
            if not aligned:
                rect(c, x0_ + 130, 400, 60, 70, fill=BLUE, a=v, fa=0.5 * v)
                rect(c, x0_ + 190, 400, 60, 70, fill=GREEN, a=v, fa=0.5 * v)
                # token ping-pong
                per = 1.1
                tt = (A.at(3, 3.0)) / per
                k = int(tt) if tt > 0 else 0
                f = ease_io(tt - int(tt)) if tt > 0 else 0
                p0, p1 = (x0_ + 100, 330), (x0_ + 270, 330)
                frm, to = (p0, p1) if k % 2 == 0 else (p1, p0)
                px = lerp(frm[0], to[0], f); py = 330 - 30 * math.sin(math.pi * f)
                if tt > 0: chip(c, px + 70, py, 'token', RED, v)
                circle(c, x0_ + 100 + 70 - 70, 330, 0, a=0)
                text(c, 'A', x0_ + 160, 380, 20, BLUE, v, 'serif_i', align='c'); text(c, 'B', x0_ + 220, 380, 20, GREEN, v, 'serif_i', align='c')
                cnt = max(0, k + (1 if f > 0.99 else 0)) if tt > 0 else 0
                text(c, f'token transfers: {cnt}', x0_, 600, 26, RED, v, 'serif')
                text(c, 'the token and the dirty data bounce back and forth', x0_, 636, 17, DIM, v, 'serif_i')
            else:
                rect(c, x0_ + 0, 400, 120, 70, fill=BLUE, a=v, fa=0.5 * v)
                rect(c, x0_ + 260, 400, 120, 70, fill=GREEN, a=v, fa=0.5 * v)
                text(c, 'A', x0_ + 60, 440, 20, BLUE, v, 'serif_i', align='c'); text(c, 'B', x0_ + 320, 440, 20, GREEN, v, 'serif_i', align='c')
                chip(c, x0_ + 60, 330, 'token', BLUE, v); chip(c, x0_ + 320, 330, 'token', GREEN, v)
                text(c, 'token transfers: 0', x0_, 600, 26, GREEN, v, 'serif')
                text(c, 'each node keeps its own range', x0_, 636, 17, DIM, v, 'serif_i')
    # ---------------- beat 4: metanode + data shipping
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'every writer changes size and mtime', 180, 250, 23, INK, v, 'serif')
        ws = [(220 + k * 130, 400) for k in range(5)]
        dsk_x, dsk_y = 560, 640
        st = 1 - A.p(4, 14.0, 1.0, smooth)         # stampede phase fades
        for (x, y) in ws:
            node(c, x, y, 20, BLUE, v)
            arrow(c, x, y + 14, dsk_x + 20, dsk_y - 16, RED, v * st * 0.7, 1.4, 7)
        disk(c, dsk_x, dsk_y, 40, 50, DIM, v, fill=RED, fa=0.2 * st + 0.05)
        text(c, 'inode on disk', dsk_x + 20, dsk_y + 78, 17, DIM, v, 'serif_i', align='c')
        text(c, 'a stampede', 540, 330, 20, RED, v * st, 'serif_i', align='c')
        ma = A.p(4, 14.5, 1.5, smooth)
        if ma > 0:
            mx, my = 560, 520
            rect(c, mx - 90, my - 26, 180, 52, stroke=AMBER, a=v * ma, sw=2, r=7)
            star(c, mx - 64, my, 10, AMBER, v * ma)
            text(c, 'metanode', mx + 14, my + 7, 20, AMBER, v * ma, 'serif', align='c')
            for (x, y) in ws:
                arrow(c, x, y + 14, mx - 10 + (x - 560) * 0.08, my - 26, AMBER, v * ma * 0.8, 1.4, 7)
            arrow(c, mx, my + 26, dsk_x + 20, dsk_y - 16, GREEN, v * ma, 2.2, 9)
            text(c, 'merges updates, writes the inode once', 740, 520, 19, GREEN, v * ma, 'serif_i')
        # data shipping panel
        dsx = A.fade(4, 24.0, 1.2)
        if dsx > 0:
            text(c, 'data shipping', 1000, 280, 22, INK, v * dsx, 'serif')
            text(c, 'blocks have owners; others forward their I/O', 1000, 308, 17, DIM, v * dsx, 'serif_i')
            cols = [BLUE, GREEN, AMBER, VIOLET]
            for k in range(8):
                rect(c, 1000 + k * 46, 380, 40, 40, fill=cols[k % 4], a=v * dsx, fa=0.55 * v * dsx)
                text(c, 'ABCD'[k % 4], 1020 + k * 46, 407, 18, BG, v * dsx, 'sans_b', align='c')
            for k in range(4):
                node(c, 1030 + k * 90, 560, 18, cols[k], v * dsx)
                arrow(c, 1030 + k * 90, 545, 1020 + k * 46 + (k % 4) * 0, 424, cols[k], v * dsx * 0.7, 1.2, 6)
            text(c, 'round-robin ownership (paper)', 1000, 620, 15, FAINT, v * dsx, 'serif_i')
    # ---------------- beats 5/6: IO500 dumbbell
    v = vis(A, 5, n, delay=0.4) if False else A.p(5, 0.4, 0.9, smooth)
    if v > 0:
        gx0, gx1 = 330, 1280
        X = lambda g: gx0 + (math.log10(g) + 1) / 4.5 * (gx1 - gx0)
        text(c, 'IO500 on Summit’s Alpine  ·  504 nodes × 2 processes', 150, 220, 24, INK, v, 'serif')
        for g in (0.1, 1, 10, 100, 1000):
            line(c, X(g), 330, X(g), 700, RULE, v * 0.8, 0.8)
            text(c, f'{g:g}', X(g), 728, 17, DIM, v, 'sans', align='c')
        text(c, 'GB/s, log scale', gx1, 760, 17, DIM, v, 'serif_i', align='r')
        rows = [('write', 440, 2158.0, 0.57), ('read', 600, 1788.0, 27.4)]
        for r_, (lab, y, easy, hard) in enumerate(rows):
            ar = A.p(5, 15.0, 2.2) if r_ == 0 else A.p(6, 8.0, 2.2)
            text(c, lab, 150, y + 7, 26, INK, v * (A.fade(5, 2.0) if r_ == 0 else A.fade(6, 7.0)), 'serif')
            if ar > 0:
                xe, xh = X(easy), X(hard)
                xcur = lerp(xe, xh, ar)
                line(c, xe, y, xcur, y, DIM, v, 2.0)
                circle(c, xe, y, 11, fill=BLUE, a=v)
                text(c, f'easy  {easy:,.0f}', xe, y - 24, 21, BLUE, v * ar, 'serif', align='c')
                circle(c, xcur, y, 11, fill=RED, a=v)
                if ar > 0.95:
                    text(c, f'hard  {hard:g}', xh, y - 24, 21, RED, v, 'serif', align='c')
                    ratio = easy / hard
                    text(c, f'{ratio:,.0f}× slower', (xe + xh) / 2, y + 40, 24, AMBER, v * (A.fade(5, 18.5) if r_ == 0 else A.fade(6, 10.5)), 'serif_i', align='c')
        text(c, 'easy: every process writes its own file     hard: small interleaved writes to one shared file', 150, 830, 19, DIM, v * A.fade(5, 4.0), 'serif_i')
    v6 = A.fade(6, 0.6, 1.2)
    if v6 > 0:
        text(c, 'The slide doesn’t say why. Usual suspects: token traffic, and read-modify-write on partial blocks.', 150, 900, 22, AMBER, v6, 'serif_i')

# ======================================================================= S5  directories, allocation, logs
_H_STAGES = [
    (['0', '1'], [0, 1], [('0', 3), ('1', 3)]),
    (['00', '01', '10', '11'], [0, 1, 2, 2], [('00', 2), ('01', 2), ('1', 3)]),
    (['000', '001', '010', '011', '100', '101', '110', '111'], [0, 0, 1, 1, 2, 2, 3, 3], [('00', 2), ('01', 2), ('10', 2), ('11', 2)]),
]
def s5(c, A):
    notes = [
        (0, 150, '1', 'Directories use extensible hashing: "a lookup needs a single directory block access regardless of directory size." Schmuck & Haskin.'),
        (1, 400, '2', 'Allocation maps are split into separately lockable regions; an allocation manager hands regions to nodes. Schmuck & Haskin.'),
        (2, 650, '3', 'Each node keeps a write-ahead log per file system, stored in the file system. "User data are not logged." Any node can replay a failed node’s log. Schmuck & Haskin.'),
    ]
    chrome(c, A, 'Keeping it from falling over at scale', 5, notes)
    n = 4
    # ---------------- beat 0: extensible hashing
    v = vis(A, 0, n)
    if v > 0:
        # stage windows
        w = [A.p(0, 1.0, 1.0, smooth), A.p(0, 5.0, 1.0, smooth), A.p(0, 9.0, 1.0, smooth)]
        stage_alpha = [w[0] * (1 - w[1]), w[1] * (1 - w[2]), w[2]]
        depth_txt = ['depth 1: one bit of the hash', 'depth 2: a full block splits', 'depth 3: the directory doubles, only the full block splits']
        for si, (slots, mp, buckets) in enumerate(_H_STAGES):
            a = stage_alpha[si] * v
            if a <= 0.01: continue
            ns = len(slots); sh = 40
            y0 = 440 - ns * sh / 2
            text(c, 'directory (array of pointers)', 200, 270, 19, DIM, a, 'serif_i')
            text(c, 'directory blocks', 700, 270, 19, DIM, a, 'serif_i')
            text(c, depth_txt[si], 200, 232, 23, AMBER, a, 'serif_i')
            for k, lab in enumerate(slots):
                yy = y0 + k * sh
                rect(c, 200, yy, 110, sh - 4, stroke=DIM, a=a, sw=1.2)
                text(c, lab, 255, yy + sh - 14, 19, INK, a, 'sans_m', align='c')
            # bucket positions
            nb = len(buckets)
            for b, (bl, fill) in enumerate(buckets):
                idxs = [k for k in range(ns) if mp[k] == b]
                by = y0 + (idxs[0] + idxs[-1]) / 2 * sh - 4
                for q in range(4):
                    rect(c, 700 + q * 40, by, 36, 32, fill=BLUE if q < fill else None, stroke=BLUE, a=a, sw=1.2, fa=0.5 * a)
                for k in idxs:
                    arrow(c, 312, y0 + k * sh + sh / 2 - 2, 696, by + 16, DIM, a * 0.7, 1.2, 7)
        # lookup
        lk = A.p(0, 12.5, 1.5)
        if lk > 0:
            text(c, 'hash("run42/output.nc") =  1 0 1 …', 200, 800, 22, INK, v * lk, 'mono')
            ns = 8; sh = 40; y0 = 440 - ns * sh / 2
            rect(c, 198, y0 + 5 * sh - 2, 114, sh, stroke=AMBER, a=v * lk, sw=3)
            rect(c, 694, y0 + 5 * sh - 14, 168, 36, stroke=AMBER, a=v * lk, sw=3)
            text(c, 'one block read, however large the directory', 940, y0 + 5 * sh + 8, 22, AMBER, v * lk, 'serif_i')
    # ---------------- beat 1: allocation regions
    v = vis(A, 1, n)
    if v > 0:
        cols = [BLUE, GREEN, AMBER, VIOLET]
        NR = 24; x0, y0, rw, rh = 190, 470, 40, 70
        assign = [(i * 7 + (i // 5)) % 4 for i in range(NR)]
        rect(c, 680 - 130, 270, 260, 50, stroke=INK, a=v, sw=1.6, r=7)
        text(c, 'allocation manager', 680, 302, 19, INK, v, 'serif', align='c')
        text(c, 'free-space map, cut into regions', x0, y0 - 24, 19, DIM, v, 'serif_i')
        nodes_x = [300, 560, 820, 1080]
        for k, nx in enumerate(nodes_x):
            node(c, nx, 760, 22, cols[k], v)
            text(c, f'node {"ABCD"[k]}', nx, 806, 18, cols[k], v, 'serif_i', align='c')
        for i in range(NR):
            ta = A.p(1, 3.0 + i * 0.22, 0.5, smooth)
            col = cols[assign[i]]
            rect(c, x0 + i * rw, y0, rw - 3, rh, stroke=DIM, a=v, sw=1.0)
            if ta > 0:
                rect(c, x0 + i * rw, y0, rw - 3, rh, fill=col, a=v, fa=0.25 * ta * v)
                if ta < 1: line(c, 680, 322, x0 + i * rw + rw / 2, y0, col, v * (1 - ta), 1.4)
            fa_ = A.p(1, 10.0 + (i % 6) * 0.3, 6.0, f=lambda x: clamp01(x))
            if fa_ > 0:
                nfill = int(fa_ * 6)
                for q in range(nfill):
                    rect(c, x0 + i * rw + 5 + (q % 2) * 15, y0 + 8 + (q // 2) * 20, 12, 15, fill=col, a=v, fa=0.9 * v)
        # hand-out arrows from regions to nodes (lightly)
        if A.p(1, 10.0, 1.0) > 0:
            for i in range(0, NR, 3):
                k = assign[i]
                curve(c, [(x0 + i * rw + rw / 2, y0 + rh), (x0 + i * rw + rw / 2, y0 + rh + 80), (nodes_x[k], 700), (nodes_x[k], 740)], cols[k], v * 0.3, 1.0)
        text(c, 'inside its own region, a node allocates without asking anyone', 680, 880, 22, INK, v * A.fade(1, 11.0), 'serif_i', align='c')
    # ---------------- beat 2: logs and recovery
    v = vis(A, 2, n)
    if v > 0:
        xs = [300, 600, 900, 1200]
        cols = [BLUE, GREEN, AMBER, VIOLET]
        fail = A.p(2, 8.0, 0.5, smooth)
        rep = A.p(2, 13.0, 8.0, f=lambda x: clamp01(x))
        for k, x in enumerate(xs):
            dead = (k == 2) and fail > 0.5
            col = RED if dead else cols[k]
            rect(c, x - 70, 260, 140, 50, stroke=col, a=v, sw=1.8, r=7)
            text(c, f'node {k+1}', x, 293, 21, col, v, 'serif', align='c')
            # log strip on shared disk
            for q in range(10):
                done = (k == 2 and rep > (q + 1) / 10.0)
                fc = GREEN if done else (cols[k] if not (k == 2 and fail > 0.5) else RED)
                rect(c, x - 100 + q * 20, 470, 18, 36, fill=fc, a=v, fa=(0.75 if (q > 5 or done) else 0.35) * v)
            rect(c, x - 102, 468, 204, 40, stroke=DIM, a=v, sw=1.0)
            text(c, f'log of node {k+1}', x, 540, 17, DIM, v, 'serif_i', align='c')
            line(c, x, 310, x, 466, FAINT, v, 1.0, dash=[4, 4])
        text(c, 'shared disks', 150, 590, 18, FAINT, v, 'serif_i')
        line(c, 150, 600, 1330, 600, FAINT, v * 0.6, 1.0)
        if fail > 0:
            cross(c, xs[2], 285, 22, RED, v * fail)
            text(c, 'node 3 fails', xs[2], 350, 22, RED, v * fail, 'serif_i', align='c')
        rp = A.p(2, 11.0, 1.5)
        if rp > 0:
            curve(c, [(xs[2] - 60, 520), (xs[2] - 160, 660), (xs[0] + 60, 660), (xs[0] + 20, 316)], GREEN, v * rp, 2.2)
            text(c, 'node 1 reads the dead node’s log and replays it', 600, 700, 22, GREEN, v * rp, 'serif_i', align='c')
        if rep >= 1:
            check(c, xs[2], 440, 14, GREEN, v)
            text(c, 'consistent again, without waiting for node 3', 900, 780, 24, INK, v * A.fade(2, 21.5), 'serif_i', align='c')
        text(c, 'metadata only: user data isn’t logged', 1330, 900, 18, DIM, v * A.fade(2, 22.0), 'serif_i', align='r')
    # ---------------- beat 3: summary
    v = A.p(3, 0.3, 0.9, smooth)
    if v > 0:
        for k, (a_, b_) in enumerate([('no single', 'metadata server'), ('no single', 'lock server'), ('no one place', 'where everything waits')]):
            f = A.fade(3, 0.3 + k * 2.2, 0.9)
            y = 500 + k * 100
            text(c, a_, 640, y, 54, AMBER, v * f, 'serif_i', align='r')
            text(c, b_, 670, y, 54, INK, v * f, 'serif')

# ======================================================================= S6  GNR, declustered RAID, ESS
_SIM = None
def _sim():
    global _SIM
    if _SIM is None: _SIM = json.load(open('sim_summary.json'))
    return _SIM

def _prog_bar(c, x, y, w, label, p, col, a):
    text(c, label, x, y - 12, 18, DIM, a, 'serif_i')
    rect(c, x, y, w, 14, stroke=DIM, a=a, sw=1.2)
    rect(c, x, y, w * clamp01(p), 14, fill=col, a=a, fa=0.85 * a)

def s6(c, A):
    notes = [
        (0, 150, '1', '"RAID rebuild times are reduced to a fraction of the time needed with hardware RAID"; declustering can make rebuild impact "a factor of three to four times less than a conventional RAID." IBM Spectrum Scale RAID docs.'),
        (3, 480, '2', 'Toy model, my own simulation: N disks, 6,000 strips per disk, 8+2p, random placement, one failed disk; load = strips read + written. Ignores network, CPU and foreground I/O.'),
        (4, 700, '3', 'Efficiency excludes spare space. 8+2p / 8+3p: Reed-Solomon, 8 data strips + 2 or 3 parity. IBM Spectrum Scale RAID Administration.'),
        (5, 850, '4', 'End-to-end checksum: 8 bytes appended by the NSD client. Pdisk I/O "times out … after about ten seconds"; a suspect pdisk is admitted to the disk hospital. IBM docs.'),
    ]
    chrome(c, A, 'Underneath: declustered RAID in software', 6, notes)
    n = 7
    rnd = random.Random(11)
    pal = [BLUE, GREEN, AMBER, VIOLET, (200, 120, 150)]
    # ---------------- panels (beats 0-2)
    pv = A.p(0, 0.4, 0.9, smooth) * (1 - A.p(3, 0.0, 1.0, smooth))
    ratio30 = _sim()['30']['ratio']
    u = A.at(2, 4.0)                    # synchronized rebuild clock (beat 2)
    pc_ = clamp01(u / (7.0 * ratio30)) if u > 0 else 0
    pd_ = clamp01(u / 7.0) if u > 0 else 0
    if pv > 0:
        # conventional
        text(c, 'conventional: groups of 10, each with a spare', 150, 232, 21, INK, pv, 'serif')
        fail_a = A.p(0, 3.0, 0.5, smooth)
        for g in range(3):
            y = 290 + g * 110
            for d in range(10):
                x = 150 + d * 46
                failed = (g == 0 and d == 3 and fail_a > 0.5)
                col = RED if failed else (BLUE if g == 0 else FAINT)
                disk(c, x, y, 34, 46, col, pv * (1.0 if g == 0 else 0.7), fill=col, fa=0.2)
                if failed: cross(c, x + 17, y + 24, 11, RED, pv)
            sx = 150 + 10 * 46 + 22
            disk(c, sx, y, 34, 46, GREEN if g == 0 else FAINT, pv, fill=GREEN if g == 0 else FAINT, fa=0.12)
            text(c, 'spare', sx + 17, y + 70, 15, DIM, pv, 'serif_i', align='c')
        if fail_a > 0.5:
            heat = 0.5 + 0.5 * math.sin(A.t * 6)
            for d in range(10):
                if d == 3: continue
                x = 150 + d * 46 + 17
                curve(c, [(x, 336), (x, 372), (150 + 10 * 46 + 39, 372), (150 + 10 * 46 + 39, 340)], RED, pv * 0.5 * fail_a, 1.2)
            circle(c, 150 + 10 * 46 + 39, 313, 30 + 4 * heat, stroke=RED, a=pv * 0.7 * fail_a, sw=2)
            text(c, 'every rebuilt strip lands on one disk', 150, 700 - 12, 18, RED, pv * fail_a, 'serif_i')
        text(c, 'groups 2 and 3 sit idle', 150, 660, 16, FAINT, pv * fail_a, 'serif_i')
    # GNR strip (beat 1)
    g1 = A.fade(1, 1.5, 1.0) * (1 - A.p(3, 0.0, 1.0, smooth))
    if g1 > 0:
        rect(c, 150, 790, 330, 56, stroke=RED, a=g1, sw=1.6, r=7)
        text(c, 'hardware RAID controller', 315, 824, 19, DIM, g1, 'serif', align='c')
        line(c, 160, 800, 470, 836, RED, g1, 2)
        arrow(c, 500, 818, 600, 818, INK, g1, 2)
        rect(c, 610, 780, 560, 76, stroke=GREEN, a=g1, sw=2, r=8)
        text(c, 'software on the NSD servers', 890, 812, 21, GREEN, g1, 'serif', align='c')
        text(c, 'GPFS Native RAID · Spectrum Scale RAID', 890, 838, 17, DIM, g1, 'serif_i', align='c')
    # declustered (beat 2)
    d2 = A.fade(2, 0.6, 1.0) * (1 - A.p(3, 0.0, 1.0, smooth))
    if d2 > 0:
        text(c, 'declustered: spread over all 30 disks', 790, 232, 21, INK, d2, 'serif')
        rr = random.Random(5)
        for r_ in range(3):
            for d in range(10):
                x = 790 + d * 46; y = 290 + r_ * 110
                failed = (r_ == 0 and d == 3)
                col = RED if failed else BLUE
                rect(c, x, y, 34, 46, stroke=col, a=d2, sw=1.3, r=3)
                for sgm in range(4):
                    rect(c, x + 2, y + 3 + sgm * 9.5, 30, 8, fill=pal[rr.randrange(5)], a=d2, fa=0.55 * d2)
                rect(c, x + 2, y + 41, 30, 4, fill=GREEN, a=d2, fa=0.9 * d2)
                if failed: cross(c, x + 17, y + 23, 11, RED, d2)
        # many-to-many rebuild traffic
        if u > 0:
            rr2 = random.Random(9)
            for k in range(46):
                sd, dd = rr2.randrange(30), rr2.randrange(30)
                if sd == 3 or dd == 3: continue
                sx_, sy_ = 790 + (sd % 10) * 46 + 17, 290 + (sd // 10) * 110 + 23
                dx_, dy_ = 790 + (dd % 10) * 46 + 17, 290 + (dd // 10) * 110 + 23
                f = ((A.t * 0.6 + k * 0.137) % 1.0)
                line(c, sx_, sy_, dx_, dy_, BLUE, d2 * 0.07, 0.8)
                circle(c, lerp(sx_, dx_, f), lerp(sy_, dy_, f), 2.4, fill=GREEN if k % 3 == 0 else BLUE, a=d2 * 0.85)
        text(c, 'everyone reads a little, everyone writes a little', 790, 660, 19, GREEN, d2 * A.fade(2, 5.0), 'serif_i')
        _prog_bar(c, 150, 750, 520, 'conventional rebuild progress (toy)', pc_, RED, d2) if False else None
    if d2 > 0 and (pv > 0):
        _prog_bar(c, 150, 905, 520, 'conventional: rebuild progress', pc_, RED, d2)
        _prog_bar(c, 790, 905, 520, 'declustered: rebuild progress', pd_, GREEN, d2)
        text(c, 'same failure; 30-disk toy model', 790, 940, 15, FAINT, d2, 'serif_i')
        im = A.fade(2, 18.0, 1.0)
        text(c, 'IBM docs: rebuild impact 3–4× smaller', 1330, 760, 19, AMBER, d2 * im, 'serif_i', align='r')
    # ---------------- beat 3: simulation chart
    v = vis(A, 3, n)
    if v > 0:
        S = _sim()
        text(c, 'work per surviving disk during one rebuild', 150, 232, 24, INK, v, 'serif')
        text(c, '(strips read + written, N = 60 disks)', 150, 262, 17, DIM, v, 'serif_i')
        X = lambda g: 190 + g / 6500 * 640
        for g in (0, 2000, 4000, 6000):
            line(c, X(g), 330, X(g), 640, RULE, v * 0.8, 0.8)
            text(c, f'{g:,}', X(g), 668, 16, DIM, v, 'sans', align='c')
        conv_a = A.p(3, 2.0, 2.0)
        dec_a = A.p(3, 6.0, 2.0)
        text(c, 'conventional', 190, 372, 19, RED, v * conv_a, 'serif')
        cl = S['60']['conv_load']
        for i, val in enumerate(cl):
            jy = 410 + ((i * 37) % 7 - 3) * 6
            circle(c, X(val * conv_a), jy, 6, fill=RED if i == len(cl) - 1 else BLUE, a=v * conv_a * 0.9)
        if conv_a > 0.95:
            text(c, 'the spare: 6,000', X(6000), 452, 17, RED, v, 'serif_i', align='r')
        text(c, 'declustered', 190, 520, 19, GREEN, v * dec_a, 'serif')
        dl = S['60']['dec_load']
        for i, val in enumerate(dl):
            jy = 560 + ((i * 53) % 9 - 4) * 7
            circle(c, X(val * dec_a), jy, 5, fill=GREEN, a=v * dec_a * 0.85)
        if dec_a > 0.95:
            text(c, f'busiest: {S["60"]["dec_max"]:,.0f}', X(S['60']['dec_max']) + 12, 612, 17, GREEN, v, 'serif_i')
            text(c, f'≈ {S["60"]["ratio"]:.1f}× less', X(3000), 520, 26, AMBER, v * A.fade(3, 9.5), 'serif_i', align='c')
        # scaling chart
        sc = A.fade(3, 16.0, 1.0)
        if sc > 0:
            gx0, gy0, gw, gh = 1010, 340, 300, 270
            text(c, 'busiest-disk load, conventional ÷ declustered', gx0 - 20, 290, 17, DIM, v * sc, 'serif_i')
            hair_axis(c, gx0, gy0 + gh, gx0 + gw, gy0 + gh, v * sc); hair_axis(c, gx0, gy0, gx0, gy0 + gh, v * sc)
            Y = lambda r: gy0 + gh - r / 14 * gh
            rect(c, gx0, Y(4), gw, Y(3) - Y(4), fill=AMBER, a=v * sc, fa=0.18 * v * sc)
            text(c, 'IBM docs: 3–4×', gx0 + gw - 6, Y(4) - 8, 16, AMBER, v * sc, 'serif_i', align='r')
            pts = [(30, S['30']['ratio']), (60, S['60']['ratio']), (120, S['120']['ratio'])]
            px = lambda N_: gx0 + 30 + (N_ - 30) / 90 * (gw - 80)
            for k, (N_, r_) in enumerate(pts):
                ap = A.fade(3, 17.0 + k * 3.0, 0.8)
                circle(c, px(N_), Y(r_), 7, fill=GREEN, a=v * ap)
                text(c, f'{r_:.1f}×', px(N_) + 12, Y(r_) - 6, 19, GREEN, v * ap, 'serif')
                text(c, str(N_), px(N_), gy0 + gh + 24, 16, DIM, v * ap, 'sans', align='c')
            text(c, 'disks in the array', gx0 + gw, gy0 + gh + 52, 16, DIM, v * sc, 'serif_i', align='r')
    # ---------------- beat 4: codes
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'protection options, and what they cost', 150, 232, 24, INK, v, 'serif')
        rows = [('8+2p', 8, 2, 80, BLUE), ('8+3p', 8, 3, 73, BLUE), ('3-way replication', 1, 2, 33, GREEN), ('4-way replication', 1, 3, 25, GREEN)]
        for k, (nm, nd, npar, eff, col) in enumerate(rows):
            y = 330 + k * 120
            a = A.fade(4, 1.0 + k * 1.2, 0.8)
            text(c, nm, 150, y + 8, 25, INK, v * a, 'serif')
            for q in range(nd):
                rect(c, 420 + q * 30, y - 16, 26, 30, fill=col, a=v * a, fa=0.75 * v * a)
            for q in range(npar):
                rect(c, 420 + (nd + q) * 30 + (6 if nd > 1 else 14), y - 16, 26, 30, fill=AMBER if nd > 1 else col, a=v * a, fa=0.75 * v * a)
            ea = A.p(4, 7.0 + k * 1.2, 1.0)
            rect(c, 800, y - 14, 4.4 * eff * ea, 28, fill=GREEN, a=v, fa=0.8 * v * ea)
            text(c, f'{eff}%', 800 + 4.4 * eff * ea + 12, y + 8, 22, GREEN, v * ea, 'serif')
        text(c, 'blue: data strips   amber: parity   green bar: usable fraction (before spare space)', 150, 860, 17, DIM, v * A.fade(4, 11.0), 'serif_i')
    # ---------------- beat 5: checksum + hospital
    v = vis(A, 5, n)
    if v > 0:
        # data path
        cx_, sx_, dx_ = 240, 700, 1150
        rect(c, cx_ - 80, 300, 160, 56, stroke=BLUE, a=v, sw=1.8, r=7); text(c, 'NSD client', cx_, 335, 21, BLUE, v, 'serif', align='c')
        rect(c, sx_ - 90, 300, 180, 56, stroke=VIOLET, a=v, sw=1.8, r=7); text(c, 'NSD server', sx_, 335, 21, VIOLET, v, 'serif', align='c')
        disk(c, dx_ - 20, 296, 40, 60, DIM, v)
        arrow(c, cx_ + 85, 328, sx_ - 95, 328, DIM, v, 1.6); arrow(c, sx_ + 95, 328, dx_ - 30, 328, DIM, v, 1.6)
        t1 = A.p(0 + 5, 2.0, 1.0)
        # chip appended
        if t1 > 0:
            rect(c, 330, 404, 190, 34, fill=BLUE, a=v * t1, fa=0.55 * v * t1, r=4)
            rect(c, 524, 404, 230, 34, fill=AMBER, a=v * t1, fa=0.9 * v * t1, r=4)
            text(c, 'data block', 425, 428, 17, BG, v * t1, 'sans_b', align='c'); text(c, '8-byte checksum', 639, 428, 17, BG, v * t1, 'sans_b', align='c')
        vf = A.fade(5, 5.0)
        if vf > 0:
            check(c, sx_ + 120, 290, 11, GREEN, v * vf); text(c, 'verified on write', sx_ + 140, 296, 18, GREEN, v * vf, 'serif_i')
        vr = A.fade(5, 8.0)
        if vr > 0:
            check(c, sx_ + 120, 372, 11, GREEN, v * vr); text(c, 'checked again on read', sx_ + 140, 378, 18, GREEN, v * vr, 'serif_i')
        # hospital timeline
        hp = A.fade(5, 11.0, 1.0)
        if hp > 0:
            x0, x1, y = 250, 1250, 700
            X = lambda s: x0 + s / 14 * (x1 - x0)
            line(c, x0, y, x1, y, FAINT, v * hp, 1.5)
            for s_ in (0, 5, 10):
                line(c, X(s_), y - 6, X(s_), y + 6, FAINT, v * hp, 1); text(c, f'{s_} s', X(s_), y + 30, 16, DIM, v * hp, 'sans', align='c')
            rect(c, X(0), y - 14, X(10) - X(0), 8, fill=BLUE, a=v * hp, fa=0.5 * v * hp)
            text(c, 'disk I/O outstanding', X(5), y - 28, 18, BLUE, v * hp, 'serif_i', align='c')
            tm = A.fade(5, 13.0)
            line(c, X(10), y - 50, X(10), y + 6, RED, v * tm, 2)
            text(c, 'times out (about 10 s)', X(10), y - 62, 19, RED, v * tm, 'serif', align='c')
            hs = A.fade(5, 15.0)
            rect(c, X(10), y + 14, X(14) - X(10), 28, fill=AMBER, a=v * hs, fa=0.55 * v * hs)
            text(c, 'disk hospital: is it the disk, or its path?', X(10) - 8, y + 70, 19, AMBER, v * hs, 'serif_i', align='r')
            rr_ = A.fade(5, 17.5)
            rect(c, X(10), y + 52, X(14) - X(10), 14, fill=GREEN, a=v * rr_, fa=0.6 * v * rr_)
            text(c, 'reads served from redundancy', X(10) - 8, y + 106, 19, GREEN, v * rr_, 'serif_i', align='r')
    # ---------------- beat 6: ESS building block
    v = A.p(6, 0.4, 0.9, smooth)
    if v > 0:
        text(c, 'an example building block (Elastic Storage Server)', 150, 232, 24, INK, v, 'serif')
        sv = [(420, 'IBM POWER server 1', BLUE), (900, 'IBM POWER server 2', AMBER)]
        for x, lab, col in sv:
            rect(c, x - 130, 280, 260, 56, stroke=col, a=v, sw=2, r=8)
            text(c, lab, x, 315, 21, col, v, 'serif', align='c')
        encl = [(150, 'NL-SAS enclosure', '5U, 84 bays', 12, 7), (610, 'NL-SAS enclosure', '5U, 84 bays', 12, 7), (1070, 'SSD enclosure', '2U, 24 slots', 12, 2)]
        for (ex, nm, sub, cc, rr_) in encl:
            ea = A.fade(6, 2.0 + 2.5 * encl.index((ex, nm, sub, cc, rr_)), 1.0)
            w_, h_ = cc * 30 + 14, rr_ * 24 + 14
            ey = 520
            rect(c, ex, ey, w_, h_, stroke=DIM, a=v * ea, sw=1.6, r=5)
            for r2 in range(rr_):
                for q in range(cc):
                    col = BLUE if q % 2 == 0 else AMBER
                    rect(c, ex + 7 + q * 30, ey + 7 + r2 * 24, 24, 18, fill=col, a=v * ea, fa=0.55 * v * ea, r=2)
            text(c, nm, ex, ey - 10, 18, INK, v * ea, 'serif')
            text(c, sub, ex + w_, ey - 10, 16, DIM, v * ea, 'serif_i', align='r')
            for (x, lab, col) in sv:
                line(c, x + (-40 if x < 600 else 40), 336, ex + w_ / 2 + (-30 if x < 600 else 30), ey, col, v * ea * 0.5, 1.2)
        ra = A.fade(6, 11.0, 1.0)
        text(c, 'each server actively serves one recovery group', 660, 820, 21, INK, v * ra, 'serif_i', align='c')
        text(c, 'and stands ready to take over the other’s', 660, 850, 21, INK, v * ra, 'serif_i', align='c')
        text(c, 'blue / amber = the two recovery groups', 150, 920, 16, FAINT, v * ra, 'serif_i')
