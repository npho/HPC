import math, random, json
from fx import *
from lx import *

_SIM = json.load(open('sim_stripe.json'))

_TYP = {}
def _typical(sc, K=100, F=3000):
    """one trial of the sim_stripe model whose fullest/mean is close to the all-trials mean (so the picture is typical)"""
    if sc in _TYP: return _TYP[sc]
    import numpy as np
    target = _SIM['res'][str(sc)]['mean']; best = None
    for seed in range(400):
        rg = np.random.default_rng(1000 + seed)
        fill = np.zeros(K)
        for s_ in rg.lognormal(0, 1.5, F): fill[rg.choice(K, sc, replace=False)] += s_ / sc
        r = fill.max() / fill.mean()
        if best is None or abs(r - target) < best[0]: best = (abs(r - target), fill.tolist())
        if abs(r - target) < 0.08 * target: break
    _TYP[sc] = best[1]; return best[1]

# ======================================================================= S4  striping
CH_COL = [mix(BLUE, GREEN, i / 8) for i in range(9)]

def s4(c, A):
    notes = [
        (0, 200, '1', 'Admin docs: with stripe count 3 and 1 MB stripes, chunk 1 goes to OST0, chunk 2 to OST1, chunk 3 to OST2, chunk 4 back to OST0. Each OST holds one object per file.'),
        (2, 420, '2', 'Admin docs: default stripe_count is 1; -1 stripes across all OSTs; maximum 2000 (since Lustre 2.2). I did not state the default stripe size because the sources I found disagree.'),
        (3, 620, '3', 'Illustrative model. Assumed 2 GB/s per OST and a 25 GB/s client link; bandwidth = min(stripes x 2, 25). Not a measurement.'),
        (4, 800, '4', f'My toy simulation (sim_stripe.py): {_SIM["K"]} OSTs, {_SIM["F"]} files with lognormal sizes (sigma {_SIM["sigma"]}), uniform random placement, {_SIM["trials"]} trials. Real allocators steer toward emptier OSTs.'),
    ]
    chrome(c, A, 'The layout: stripes across targets', 4, notes)
    n = 6
    # ---- beat 0/1: round robin
    v = vis(A, 0, n, 0.9, 0.9) + 0 if False else None
    va = A.fade(0, 0.2, 0.9) * (1 - A.p(2, 0.0, 0.9, smooth))
    if va > 0:
        NCH = 9
        text(c, 'a file, cut into 1 MB chunks', 150, 240, 20, DIM, va, 'serif_i')
        osx = [330, 620, 910]
        for q in range(3):
            rect(c, osx[q] - 70, 520, 140, 250, stroke=VIOLET, a=va, sw=1.5, r=6)
            text(c, f'OST {q}', osx[q], 805, 19, VIOLET, va, 'sans_m', align='c')
            text(c, 'object of this file', osx[q], 828, 14, DIM, va, 'serif_i', align='c')
        for i in range(NCH):
            x1, y1 = 150 + i * 70, 280
            q = i % 3; slot = i // 3
            x2, y2 = osx[q] - 52, 535 + slot * 54
            f = A.p(0, 1.5 + i * 1.5, 1.0, ease_out)
            x = lerp(x1, x2, f); y = lerp(y1, y2, f)
            w = lerp(60, 104, f)
            rect(c, x, y, w, 44, fill=CH_COL[i], a=va, fa=0.85 * va, r=4)
            text(c, str(i + 1), x + w / 2, y + 29, 20, BG, va, 'sans_b', align='c')
        b = A.fade(1, 0.5)
        if b > 0:
            text(c, 'object on OST 0 holds chunks 1, 4, 7', osx[0] - 70, 870, 20, AMBER, va * b, 'serif_i')
            rect(c, 1040, 330, 300, 200, stroke=AMBER, a=va * b, sw=1.4, r=8)
            text(c, 'the MDS stores the layout', 1190, 380, 19, AMBER, va * b, 'serif', align='c')
            mono(c, 'stripe_count = 3', 1070, 430, 17, INK, va * b)
            mono(c, 'stripe_size  = 1M', 1070, 462, 17, INK, va * b)
            mono(c, 'OSTs = 0, 1, 2', 1070, 494, 17, INK, va * b)
    # ---- beat 2: lfs setstripe
    vb = vis(A, 2, n)
    if vb > 0:
        text(c, 'chosen per file, or per directory so new files inherit it', 150, 240, 22, INK, vb, 'serif')
        rect(c, 150, 290, 1050, 90, fill=(24, 28, 36), a=vb, fa=vb, stroke=RULE, r=8)
        mono(c, '$ lfs setstripe -c 4 -S 1M /scratch/run42', 180, 345, 27, GREEN, vb)
        rows = [('default stripe count', '1', '(one target per new file)', 2.0), ('-c -1', 'all', 'use every available OST', 5.0), ('maximum', '2000', 'stripes per file (since 2.2)', 8.0)]
        for q, (k, v_, d, dl) in enumerate(rows):
            a_ = vb * A.fade(2, dl)
            y = 470 + q * 90
            text(c, k, 190, y, 22, DIM, a_, 'serif_i')
            text(c, v_, 520, y, 36, AMBER, a_, 'sans_b')
            text(c, d, 640, y, 21, INK, a_, 'serif')
        text(c, 'good for many small files', 190, 790, 20, GREEN, vb * A.fade(2, 11.0), 'serif_i')
        text(c, 'wasteful for one huge shared file', 600, 790, 20, RED, vb * A.fade(2, 13.5), 'serif_i')
    # ---- beat 3: bandwidth model
    vc = vis(A, 3, n)
    if vc > 0:
        gx0, gy0, gw, gh = 190, 240, 920, 520
        hair_axis(c, gx0, gy0 + gh, gx0 + gw, gy0 + gh, vc); hair_axis(c, gx0, gy0, gx0, gy0 + gh, vc)
        text(c, 'aggregate bandwidth (GB/s)', gx0, gy0 - 20, 17, DIM, vc, 'serif_i')
        text(c, 'stripe count', gx0 + gw, gy0 + gh + 42, 17, DIM, vc, 'serif_i', align='r')
        Xs = lambda s_: gx0 + (s_ / 32) * gw
        Ys = lambda b_: gy0 + gh - (b_ / 30) * gh
        for b_ in (0, 10, 20, 30):
            line(c, gx0, Ys(b_), gx0 + gw, Ys(b_), RULE, vc * 0.7, 0.8); text(c, str(b_), gx0 - 12, Ys(b_) + 5, 15, DIM, vc, 'sans', align='r')
        for s_ in (1, 4, 8, 16, 32):
            text(c, str(s_), Xs(s_), gy0 + gh + 22, 15, DIM, vc, 'sans', align='c')
        gr = A.pf(3, 0.08, 0.55)
        path = skia.Path(); first = True
        for s_ in [1 + k * 0.25 for k in range(int(31 / 0.25 * gr) + 1)]:
            xx, yy = Xs(s_), Ys(min(2.0 * s_, 25.0))
            if first: path.moveTo(xx, yy); first = False
            else: path.lineTo(xx, yy)
        c.drawPath(path, P(BLUE, vc, 'stroke', 3.2))
        m = A.pf(3, 0.55, 0.7, smooth)
        text(c, 'each stripe adds a server\'s worth', Xs(5), Ys(10) - 40, 19, BLUE, vc * m, 'serif_i')
        m2 = A.pf(3, 0.72, 0.85, smooth)
        text(c, 'client link saturates', Xs(20), Ys(25) - 18, 19, RED, vc * m2, 'serif_i')
        line(c, Xs(12.5), Ys(25), Xs(12.5), gy0 + gh, RED, vc * m2, 1, dash=[4, 4])
        text(c, 'assumed numbers: shape only', gx0 + gw, gy0 + 20, 16, FAINT, vc, 'serif_i', align='r')
    # ---- beat 4: balance simulation
    vd = vis(A, 4, n)
    if vd > 0:
        K = 100
        for q, sc in enumerate((1, 16)):
            fill = _typical(sc)
            mean = sum(fill) / K
            px, py, pw, ph = 150 + q * 540, 300, 440, 250
            a_ = vd * A.fade(4, 0.5 + q * 4.5)
            text(c, f'stripe count {sc}: one typical trial', px, py - 24, 21, INK, a_, 'serif')
            line(c, px, py + ph, px + pw, py + ph, FAINT, a_)
            top = 5.0
            for i in range(K):
                hh = min(fill[i] / mean, top) / top * ph
                col = RED if fill[i] / mean > 2 else BLUE
                rect(c, px + i * pw / K, py + ph - hh, pw / K - 1, hh, fill=col, a=a_, fa=0.8 * a_)
            line(c, px, py + ph - ph / top, px + pw, py + ph - ph / top, AMBER, a_ * 0.8, 1, dash=[4, 4])
            text(c, 'average', px + pw - 2, py + ph - ph / top - 8, 14, AMBER, a_, 'serif_i', align='r')
            text(c, f'fullest ≈ {max(fill) / mean:.1f}× average', px, py + ph + 30, 18, RED if sc == 1 else GREEN, a_, 'serif_i')
        b = A.fade(4, 10.0)
        if b > 0:
            text(c, 'fullest target ÷ average, over 300 random trials', 150, 660, 20, DIM, vd * b, 'serif_i')
            for q, sc in enumerate((1, 2, 4, 8, 16)):
                r_ = _SIM['res'][str(sc)]['mean']
                y = 700 + q * 40
                text(c, f'{sc}', 190, y + 6, 17, DIM, vd * b, 'sans', align='r')
                rect(c, 210, y - 12, (r_ - 1) / 3 * 600 + 10, 24, fill=RED if sc == 1 else BLUE, a=vd * b, fa=0.7 * b, r=3)
                text(c, f'{r_:.2f}×', 230 + (r_ - 1) / 3 * 600 + 10, y + 6, 17, INK, vd * b, 'sans')
    # ---- beat 5: stripes are not free
    ve = A.fade(5, 0.4)
    if ve > 0:
        text(c, 'one target fails', 150, 260, 22, INK, ve, 'serif')
        for q in range(8):
            x = 190 + q * 120
            rect(c, x, 330, 90, 70, stroke=VIOLET if q != 3 else RED, a=ve, sw=1.6, r=5, fill=RED if q == 3 else None, fa=0.2 * ve)
            text(c, f'OST {q}', x + 45, 372, 17, VIOLET if q != 3 else RED, ve, 'sans_m', align='c')
        cross(c, 190 + 3 * 120 + 45, 365, 18, RED, ve * A.fade(5, 1.5), 3)
        b = A.fade(5, 3.0)
        # file A single stripe on OST 6; file B on all
        text(c, 'narrow file (1 stripe)', 150, 500, 20, GREEN, ve * b, 'serif', align='l')
        rect(c, 190 + 6 * 120, 430, 90, 36, fill=GREEN, a=ve * b, fa=0.45 * b, r=4)
        check(c, 190 + 6 * 120 + 45, 448, 10, GREEN, ve * b)
        text(c, 'unaffected', 190 + 6 * 120 + 45, 490, 15, GREEN, ve * b, 'serif_i', align='c')
        b2 = A.fade(5, 7.0)
        text(c, 'wide file (8 stripes)', 150, 620, 20, RED, ve * b2, 'serif', align='l')
        for q in range(8):
            rect(c, 190 + q * 120, 560, 90, 36, fill=RED if q == 3 else BLUE, a=ve * b2, fa=0.45 * b2, r=4)
        text(c, 'unavailable until that target is back', 190, 660, 19, RED, ve * b2, 'serif_i')
        b3 = A.fade(5, 11.0)
        for q, s_ in enumerate(['another server to contact', 'another lock to hold', 'another failure that can take the file offline']):
            text(c, '+ ' + s_, 190, 740 + q * 38, 22, AMBER, ve * A.fade(5, 11.0 + q * 1.4), 'serif')

# ======================================================================= S5  locks
def s5(c, A):
    notes = [
        (1, 250, '1', 'Schwan 2003: "Locks are always managed by a single service node and do not migrate between masters"; the Lustre DLM was "just over 4,000 lines."'),
        (2, 450, '2', 'Schwan 2003: a policy function can grant a lock larger than requested, so a sole user of a file typically gets one lock for the whole file. Callback-on-conflict is the standard DLM mechanism (wiki.lustre.org mentions lock-cancellation callbacks).'),
        (3, 650, '3', 'Schwan 2003: intent locks let the MDS "combine a lookup with the intended operation, such as file creation." Cluster File Systems white paper 2002 describes the same idea.'),
        (4, 830, '4', 'Schwan 2003: high-contention directories such as /tmp get no lock; the server does the operation. The write-back cache for quiet directories was described as planned, not yet shipped.'),
    ]
    chrome(c, A, 'Keeping it coherent: the lock manager', 5, notes)
    n = 6
    # beat 0: write then read
    v = vis(A, 0, n)
    if v > 0:
        lanes = [(250, 'client A', BLUE), (700, 'storage server', VIOLET), (1150, 'client B', GREEN)]
        for x, lab, col in lanes:
            rect(c, x - 90, 230, 180, 44, stroke=col, a=v, sw=1.6, r=6)
            text(c, lab, x, 260, 20, col, v, 'serif', align='c')
            line(c, x, 274, x, 800, FAINT, v, 1.2, dash=[5, 5])
        steps = [(2.0, 330, 250, 700, AMBER, 'write x = 1  (takes a lock)'), (6.0, 460, 1150, 700, AMBER, 'read x  (conflicts)'),
                 (9.5, 560, 700, 250, RED, 'callback: release'), (12.5, 660, 250, 700, BLUE, 'flush x = 1'), (15.5, 760, 700, 1150, GREEN, 'x = 1')]
        for dl, y, x1, x2, col, lab in steps:
            f = A.p(0, dl, 0.9)
            if f > 0:
                arrow(c, x1, y, lerp(x1, x2, f), y, col, v, 2.2)
                text(c, lab, (x1 + x2) / 2, y - 12, 18, col, v * f, 'serif_i', align='c')
    # beat 1: LDLM
    v = vis(A, 1, n)
    if v > 0:
        rect(c, 420, 300, 480, 280, stroke=VIOLET, a=v, sw=1.8, r=10)
        text(c, 'a storage server', 660, 345, 22, VIOLET, v, 'serif', align='c')
        rect(c, 470, 380, 380, 70, fill=AMBER, a=v, fa=0.18 * v, stroke=AMBER, sw=1.4, r=6)
        text(c, 'LDLM', 660, 425, 30, AMBER, v, 'title', align='c')
        text(c, 'manages locks for the objects it holds', 660, 490, 18, DIM, v, 'serif_i', align='c')
        b = A.fade(1, 4.0)
        text(c, 'each lock has one manager that never changes', 660, 625, 22, INK, v * b, 'serif', align='c')
        b = A.fade(1, 9.0)
        text(c, 'whole lock manager, 2003:', 660, 700, 20, DIM, v * b, 'serif_i', align='c')
        text(c, 'just over 4,000 lines of code', 660, 745, 34, GREEN, v * b, 'serif', align='c')
    # beat 2: extent locks
    v = vis(A, 2, n)
    if v > 0:
        x0, x1_ = 220, 1120
        text(c, 'byte ranges of one file', x0, 250, 20, DIM, v, 'serif_i')
        rect(c, x0, 300, x1_ - x0, 50, stroke=DIM, a=v, sw=1.5)
        text(c, '0', x0, 385, 15, DIM, v, 'sans', align='c'); text(c, 'end of file', x1_, 385, 15, DIM, v, 'sans', align='c')
        mid = (x0 + x1_) / 2
        t1 = A.at(2, 1.5)
        # A: whole file
        rect(c, x0, 430, x1_ - x0, 44, fill=BLUE, a=v * smooth(t1 / 1.0), fa=0.45 * smooth(t1 / 1.0), stroke=BLUE, sw=1.4, r=4)
        text(c, 'client A: gets a lock on the whole file', x0 + 12, 460, 19, INK, v * smooth(t1 / 1.0), 'serif')
        # conflict
        t2 = A.at(2, 8.0)
        if t2 > 0:
            f = smooth(t2 / 1.2)
            rect(c, mid, 540, x1_ - mid, 44, fill=GREEN, a=v * f, fa=0.45 * f, stroke=GREEN, sw=1.4, r=4)
            text(c, 'client B asks for the back half', mid + 12, 570, 19, INK, v * f, 'serif')
            arrow(c, mid + 100, 534, mid + 100, 480, RED, v * f, 2)
            text(c, 'server calls A back', mid + 120, 512, 17, RED, v * f, 'serif_i')
        t3 = A.at(2, 12.5)
        if t3 > 0:
            f = smooth(t3 / 1.2)
            rect(c, mid, 430, (x1_ - mid) * f, 44, fill=BG, a=v, fa=v)
            rect(c, mid, 430, (x1_ - mid) * f, 44, stroke=DIM, a=v * 0.5, sw=1, dash=[4, 4])
            text(c, 'A keeps the first half, B gets the second', 660, 660, 22, AMBER, v * f, 'serif', align='c')
    # beat 3: intent
    v = vis(A, 3, n)
    if v > 0:
        for (x, ti, col, steps_) in [(380, 'without intent', RED, ['lookup directory', 'take a lock', 'create the file']), (1000, 'with an intent lock', GREEN, ['“open + create”'])]:
            text(c, ti, x, 250, 25, col, v, 'serif', align='c')
            node(c, x - 190, 520, 24, BLUE, v); server(c, x + 110, 495, 100, 36, AMBER, v)
            text(c, 'client', x - 190, 565, 16, BLUE, v, 'serif_i', align='c'); text(c, 'MDS', x + 160, 480, 16, AMBER, v, 'sans_m', align='c')
        for q in range(3):
            y = 380 + q * 60
            f = A.p(3, 1.0 + q * 2.2, 0.8)
            if f > 0:
                arrow(c, 190, y, lerp(190, 490, f), y, RED, v, 2); text(c, ['lookup directory', 'take a lock', 'create the file'][q], 340, y - 10, 17, RED, v * f, 'serif_i', align='c')
        f = A.p(3, 9.0, 0.9)
        if f > 0:
            arrow(c, 810, 430, lerp(810, 1110, f), 430, GREEN, v, 3); text(c, 'open + create', 960, 415, 18, GREEN, v * f, 'serif_i', align='c')
        f2 = A.p(3, 11.5, 0.9)
        if f2 > 0:
            arrow(c, 1110, 470, lerp(1110, 810, f2), 470, GREEN, v, 3); text(c, 'result + a lock if useful', 960, 500 + 0, 17, GREEN, v * f2, 'serif_i', align='c')
        text(c, '3 round trips  →  1', 690, 740, 30, INK, v * A.fade(3, 13.0), 'serif', align='c')
    # beat 4: contention policy
    v = vis(A, 4, n)
    if v > 0:
        for (x, ti, col, kind) in [(380, 'a quiet directory', GREEN, 0), (1000, 'a hot directory (/tmp)', RED, 1)]:
            a_ = v * A.fade(4, 0.5 + kind * 6.5)
            text(c, ti, x, 250, 25, col, a_, 'serif', align='c')
            for i in range(4 if kind else 1):
                node(c, x - 200, 340 + i * 60, 20, BLUE, a_)
            server(c, x + 90, 395, 100, 36, AMBER, a_)
            if kind == 0:
                rect(c, x - 130, 380, 120, 70, stroke=AMBER, a=a_, sw=1.5, r=6)
                text(c, 'lock held', x - 70, 420, 17, AMBER, a_, 'serif_i', align='c')
                text(c, 'client can cache and batch', x, 520, 20, INK, a_, 'serif', align='c')
                text(c, '(planned in 2003)', x, 550, 16, DIM, a_, 'serif_i', align='c')
            else:
                for i in range(4):
                    ph = (A.t * 0.9 + i * 0.25) % 1.0
                    pkt(c, [(x - 190, 340 + i * 60), (x + 90, 413)], ph, AMBER, a_)
                text(c, 'no lock granted', x, 520, 20, INK, a_, 'serif', align='c')
                text(c, 'the server does each operation itself', x, 550, 17, DIM, a_, 'serif_i', align='c')
    # beat 5: compare
    v = A.fade(5, 0.4)
    if v > 0:
        for (x, ti, col) in [(380, 'GPFS', BLUE), (1000, 'Lustre', AMBER)]:
            text(c, ti, x, 250, 34, col, v, 'title', align='c')
        for j in range(4):
            server(c, 240 + j * 60 - 25, 380 + (j % 2) * 0, 50, 24, AMBER, v * A.fade(5, 1.0 + j * 0.5))
            circle(c, 265 + j * 60, 460, 0.1, fill=BG, a=0)
        text(c, 'lock state spread across token managers', 380, 480, 20, INK, v * A.fade(5, 1.0), 'serif', align='c')
        for k in range(3):
            x = 860 + k * 110
            server(c, x, 380, 90, 32, VIOLET, v * A.fade(5, 6.0 + k * 0.5))
            text(c, 'locks', x + 45, 440, 16, AMBER, v * A.fade(5, 7.0 + k * 0.3), 'serif_i', align='c')
        text(c, 'held by the server that owns the object', 1000, 520, 20, INK, v * A.fade(5, 6.0), 'serif', align='c')

# ======================================================================= S6  LNet
def s6(c, A):
    notes = [
        (0, 200, '1', 'Wikipedia: LNet was originally based on the Sandia Portals API; supports InfiniBand, Omni-Path, RoCE, iWARP, and TCP/IP over Ethernet, plus several proprietary interconnects.'),
        (1, 480, '2', 'Admin docs: NIDs take the form address@network_type; common LNDs are ksocklnd (TCP) and ko2iblnd (InfiniBand); all nodes listen on TCP port 988.'),
        (3, 700, '3', 'Wikipedia: bulk RPCs up to 4 MB (2.4), 16 MiB (2.9), 64 MB (2.13). "Amortize fixed cost" is my interpretation, not a quote.'),
        (4, 850, '4', 'Schwan 2003: >300 MB/s between two nodes over Quadrics Elan, bottlenecked by the PCI bus; parallel I/O to a single file shown to scale to >1,100 nodes, the limit of available hardware.'),
    ]
    chrome(c, A, 'The wire: LNet', 6, notes)
    n = 5
    v = vis(A, 0, n)
    if v > 0:
        layers = [('Lustre file system', AMBER, 0), ('LNet: one messaging API', INK, 1)]
        for lab, col, q in layers:
            a_ = v * A.fade(0, 0.5 + q * 2.0)
            rect(c, 300, 250 + q * 110, 720, 80, stroke=col, a=a_, sw=1.6, r=8)
            text(c, lab, 660, 300 + q * 110, 26, col, a_, 'serif', align='c')
        lnds = [('ksocklnd', 'TCP / Ethernet'), ('ko2iblnd', 'InfiniBand'), ('Omni-Path', ''), ('RoCE, iWARP', ''), ('proprietary', '')]
        for q, (a1, a2) in enumerate(lnds):
            a_ = v * A.fade(0, 4.0 + q * 1.0)
            x = 150 + q * 215
            rect(c, x, 480, 190, 70, stroke=VIOLET, a=a_, sw=1.4, r=6)
            text(c, a1, x + 95, 515, 19, VIOLET, a_, 'mono', align='c')
            if a2: text(c, a2, x + 95, 538, 15, DIM, a_, 'serif_i', align='c')
            line(c, x + 95, 480, 660, 440, FAINT, a_, 1)
        text(c, 'a driver (LND) per fabric', 660, 600, 20, VIOLET, v * A.fade(0, 9.5), 'serif_i', align='c')
    v = vis(A, 1, n)
    if v > 0:
        mono(c, '192.168.1.10@tcp', 150, 300, 38, INK, v)
        text(c, 'address', 150 + 0, 350, 19, AMBER, v * A.fade(1, 3.0), 'serif_i')
        text(c, '@network type', 480, 350, 19, BLUE, v * A.fade(1, 3.0), 'serif_i')
        text(c, 'a node\'s network identifier (NID)', 150, 400, 22, DIM, v * A.fade(1, 3.0), 'serif_i')
        chip(c, 250, 520, 'TCP port 988', VIOLET, v * A.fade(1, 5.5), w=170, size=17)
        # RDMA diagram
        b = A.fade(1, 9.0)
        for (x, lab) in [(300, 'client memory'), (900, 'server memory')]:
            rect(c, x - 100, 640, 200, 90, stroke=BLUE, a=v * b, sw=1.5, r=6)
            text(c, lab, x, 692, 20, BLUE, v * b, 'serif', align='c')
        for q in range(4):
            ph = (A.t * 0.5 + q * 0.25) % 1
            rect(c, lerp(400, 800, ph) - 6, 680, 12, 12, fill=BLUE, a=v * b, fa=0.9 * b, r=2)
        text(c, 'RDMA: bulk data moves without the CPU copying it', 600, 780, 20, DIM, v * b, 'serif_i', align='c')
    v = vis(A, 2, n)
    if v > 0:
        rect(c, 150, 280, 320, 220, stroke=BLUE, a=v, sw=1.5, r=10); text(c, 'network 1', 310, 320, 20, BLUE, v, 'serif', align='c')
        rect(c, 850, 280, 320, 220, stroke=VIOLET, a=v, sw=1.5, r=10); text(c, 'network 2', 1010, 320, 20, VIOLET, v, 'serif', align='c')
        for i in range(3): node(c, 220 + i * 90, 400, 22, BLUE, v)
        for i in range(3): node(c, 920 + i * 90, 400, 22, VIOLET, v)
        a_ = v * A.fade(2, 2.0)
        rect(c, 570, 360, 180, 80, fill=AMBER, a=a_, fa=0.2 * a_, stroke=AMBER, sw=1.6, r=8)
        text(c, 'LNet router', 660, 408, 20, AMBER, a_, 'serif', align='c')
        line(c, 470, 400, 570, 400, AMBER, a_, 1.6); line(c, 750, 400, 850, 400, AMBER, a_, 1.6)
        chip(c, 660, 540, 'Orion: 169 routers', AMBER, v * A.fade(2, 5.0), w=220, size=17)
        b = A.fade(2, 9.0)
        node(c, 330, 700, 28, BLUE, v * b)
        for q in range(3):
            line(c, 345, 690 + q * 10, 620, 690 + q * 10, BLUE, v * b, 2.2)
        text(c, 'multi-rail (2.10): several interfaces, one fatter pipe', 700, 740, 20, DIM, v * b, 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        gx0, gy0, gw, gh = 220, 300, 900, 380
        text(c, 'largest bulk RPC', gx0, gy0 - 30, 20, DIM, v, 'serif_i')
        Xr = lambda mb: gx0 + (math.log2(mb) - 1) / 7 * gw
        for mb in (2, 4, 8, 16, 32, 64, 128):
            line(c, Xr(mb), gy0, Xr(mb), gy0 + gh, RULE, v * 0.6, 0.8); text(c, f'{mb} MB', Xr(mb), gy0 + gh + 26, 15, DIM, v, 'sans', align='c')
        pts = [(4, 'Lustre 2.4', 580), (16, 'Lustre 2.9', 460), (64, 'Lustre 2.13', 340)]
        for q, (mb, lab, y) in enumerate(pts):
            a_ = v * A.fade(3, 1.0 + q * 3.6)
            circle(c, Xr(mb), y - 40, 11, fill=AMBER, a=a_)
            text(c, f'{lab}: {mb} MB', Xr(mb) + 22, y - 33, 21, INK, a_, 'serif')
            if q: arrow(c, Xr(pts[q-1][0]) + 12, pts[q-1][2] - 40, Xr(mb) - 12, y - 40, FAINT, a_, 1.4)
    v = A.fade(4, 0.4)
    if v > 0:
        text(c, '2003', 360, 270, 26, DIM, v, 'title', align='c')
        text(c, '> 300 MB/s', 360, 380, 66, BLUE, v * A.fade(4, 1.0), 'title', align='c')
        text(c, 'two nodes, Quadrics Elan, limited by the PCI bus', 360, 430, 20, DIM, v * A.fade(4, 1.0), 'serif_i', align='c')
        text(c, '> 1,100 nodes', 960, 380, 66, GREEN, v * A.fade(4, 6.0), 'title', align='c')
        text(c, 'writing one shared file: the limit of the hardware they had', 960, 430, 20, DIM, v * A.fade(4, 6.0), 'serif_i', align='c')
