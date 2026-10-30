import math, random
from fx import *
from lx import *

# ======================================================================= S0  cold open
def _open_cycle(c, A, t0, a, per=7.0, n_oss=6, cl=(0, 7, 13)):
    """repeating open: client -> MDS (amber, small) -> layout back -> parallel blue to every OSS"""
    for q, i in enumerate(cl):
        t = (t0 + q * 1.1) % per
        mx, my = MDS_XY[0], MDS_XY[1] + 19
        p1 = route_client(i, mx, my)
        pkt(c, p1, t / 1.2, AMBER, a)
        pkt(c, p1[::-1], (t - 1.4) / 1.2, AMBER, a, 7)
        for k in range(n_oss):
            ox, oy = oss_xy(k)
            p2 = route_client(i, ox, oy + 18)
            pkt(c, p2, (t - 3.0) / 1.6, BLUE, a, 8)
            pkt(c, p2[::-1], (t - 4.8) / 1.6, BLUE, a * 0.8, 6)

def s0(c, A):
    notes = [
        (1, 270, '1', '"Lustre" is a portmanteau of "Linux" and "cluster" (Wikipedia, Lustre (file system)).'),
        (2, 560, '2', 'Admin docs: the MDS "is not involved in file I/O"; reads and writes go directly between clients and OSSs, in parallel (wiki.lustre.org, Lustre Architecture for Admins).'),
    ]
    chrome(c, A, 'The other giant', 0, notes)
    n = 4
    # beat 0: last time / this time
    v0 = vis(A, 0, n)
    if v0 > 0:
        text(c, 'last time', 300, 330, 22, DIM, v0, 'serif_i', align='c')
        text(c, 'GPFS', 300, 400, 54, BLUE, v0, 'title', align='c')
        para(c, 'shared disks; coordination spread across every node', 130, 450, 340, 22, DIM, v0, 'serif_i', align='l')
        text(c, 'this time', 960, 330, 22, DIM, v0 * A.fade(0, 3.0), 'serif_i', align='c')
        text(c, 'Lustre', 960, 400, 54, AMBER, v0 * A.fade(0, 3.0), 'title', align='c')
        para(c, 'almost the opposite bet', 800, 450, 340, 22, DIM, v0 * A.fade(0, 3.0), 'serif_i', align='l')
        text(c, 'vs', 630, 395, 24, FAINT, v0 * A.fade(0, 3.0), 'serif_i', align='c')
    # beat 1: name + sentence
    v1 = vis(A, 1, n)
    if v1 > 0:
        text(c, 'Lustre', 740, 360, 96, INK, v1, 'title', align='c')
        pa = A.fade(1, 1.2)
        text(c, 'Linux', 560, 420, 26, DIM, v1 * pa, 'serif_i', align='c')
        text(c, '+', 650, 420, 26, FAINT, v1 * pa, 'serif', align='c')
        text(c, 'cluster', 740, 420, 26, DIM, v1 * pa, 'serif_i', align='c')
        # two ideas
        pb = A.fade(1, 6.5)
        rect(c, 230, 520, 450, 150, stroke=AMBER, a=v1 * pb, sw=1.6, r=8)
        text(c, 'small, chatty work', 455, 565, 24, AMBER, v1 * pb, 'serif', align='c')
        text(c, 'names, directories, permissions', 455, 605, 19, DIM, v1 * pb, 'serif_i', align='c')
        text(c, '→  one place', 455, 645, 22, INK, v1 * pb, 'serif', align='c')
        pc = A.fade(1, 11.0)
        rect(c, 800, 520, 450, 150, stroke=BLUE, a=v1 * pc, sw=1.6, r=8)
        text(c, 'big, heavy work', 1025, 565, 24, BLUE, v1 * pc, 'serif', align='c')
        text(c, 'moving the bytes', 1025, 605, 19, DIM, v1 * pc, 'serif_i', align='c')
        text(c, '→  many servers at once', 1025, 645, 22, INK, v1 * pc, 'serif', align='c')
    # beat 2/3: topology and the open
    v2 = A.fade(2, 0.3, 1.0)
    if v2 > 0:
        draw_clients(c, v2)
        label(c, 'clients', 200, 270, 19, BLUE, v2)
        draw_fabric(c, v2)
        draw_mds(c, v2, lit=0.0)
        label(c, 'one metadata server', 820, 305, 18, AMBER, v2)
        for k in range(6): draw_oss(c, k, v2)
        label(c, 'many storage servers', 1090, 285, 19, VIOLET, v2)
        for i in range(18):
            x, y = client_xy(i)
            line(c, x + 12, y, FAB_X - 8, y, FAINT, v2 * 0.5, 1)
        line(c, FAB_X + 8, MDS_XY[1] + 19, MDS_XY[0], MDS_XY[1] + 19, FAINT, v2 * 0.6, 1.2)
        for k in range(6):
            ox, oy = oss_xy(k); line(c, FAB_X + 8, oy + 18, ox, oy + 18, FAINT, v2 * 0.6, 1.2)
        # caption of phases
        tt = A.at(2, 1.0)
        if tt > 0:
            _open_cycle(c, A, tt, v2)
            ph = tt % 7.0
            lab = 'ask where the file lives' if ph < 2.6 else ('read and write directly, in parallel' if ph < 6.4 else '')
            col = AMBER if ph < 2.6 else BLUE
            if lab: text(c, lab, 640, 850, 24, col, v2, 'serif_i', align='c')
    v3 = A.fade(3, 0.4, 1.0)
    if v3 > 0:
        items = [('the pieces', AMBER), ('the layout', BLUE), ('consistency', GREEN), ('a real system', VIOLET)]
        for q, (s_, col) in enumerate(items):
            a_ = v3 * A.fade(3, 0.5 + q * 2.6)
            chip(c, 330 + q * 250, 930, s_, col, a_, w=215, size=17)

# ======================================================================= S1  history
def _X(y): return 150 + (y - 1999) * 46.0

def _ev(c, a, y, lab, side, lvl, color=INK, align='l', sub=None):
    x = _X(y); y0 = 700
    h = 60 + 62 * lvl
    ty = y0 - h if side == 'u' else y0 + h
    line(c, x, y0, x, ty + (6 if side == 'u' else -20), color, a * 0.7, 1.2)
    circle(c, x, y0, 6, fill=color, a=a)
    tx = x - 4 if align == 'l' else x + 4
    text(c, lab, tx, ty, 19, color, a, 'serif', align=align)
    if sub: text(c, sub, tx, ty + 22, 15, DIM, a, 'serif_i', align=align)

def s1(c, A):
    notes = [
        (0, 160, '1', 'Wikipedia (secondary source): research started 1999 at Carnegie Mellon; Cluster File Systems founded 2001, building on InterMezzo / Coda.'),
        (2, 410, '2', 'Cluster File Systems, "Lustre: A Scalable, High-Performance File System," white paper v1.0, 11 Nov 2002. P. Schwan, "Lustre: Building a File System for 1,000-node Clusters," Linux Symposium, Ottawa, July 2003.'),
        (3, 700, '3', 'Wikipedia: Sun acquired CFS assets Sep 2007; Oracle announced end of 2.x development Dec 2010; Intel acquired Whamcloud Jul 2012; DDN acquired the team Jun 2018; trademark to OpenSFS + EOFS Nov 2019.'),
        (4, 880, '4', 'Wikipedia: "more than 60 of the top 100" since 2005. The same page is inconsistent about this figure, so treat it as approximate.'),
    ]
    chrome(c, A, 'Where it came from', 1, notes)
    # axis
    pa = A.fade(0, 0.2)
    line(c, _X(1998.5), 700, _X(2025.3), 700, FAINT, pa, 1.4)
    for yr in range(1999, 2026, 2):
        x = _X(yr); line(c, x, 700, x, 707, FAINT, pa); text(c, str(yr), x, 728, 14, DIM, pa, 'sans', align='c')
    # beat 0
    a = A.fade(0, 0.8)
    _ev(c, a, 1999.0, '1999  Braam starts the research', 'u', 1, INK, 'l', 'Carnegie Mellon')
    a = A.fade(0, 4.5)
    _ev(c, a, 2001.5, '2001  Cluster File Systems', 'd', 0.6, INK, 'l', 'company founded')
    # beat 1: DOE
    a = A.fade(1, 0.6)
    if a > 0:
        rect(c, 150, 190, 400, 74, stroke=AMBER, a=a, sw=1.5, r=6)
        text(c, 'US Dept. of Energy', 350, 222, 22, AMBER, a, 'serif', align='c')
        text(c, 'ASCI Path Forward funding', 350, 250, 17, DIM, a, 'serif_i', align='c')
    _ev(c, A.fade(1, 5.5), 2003.2, 'Mar 2003  first production use', 'u', 2, INK, 'l', 'a cluster at LLNL')
    _ev(c, A.fade(1, 10.5), 2003.95, 'Dec 2003  version 1.0', 'd', 1.7, GREEN, 'l')
    # beat 2: documents
    for (yy, lab, col, dl) in [(2002.87, 'Nov 2002 white paper', BLUE, 1.0), (2003.55, 'Jul 2003 Schwan, Linux Symposium', BLUE, 5.0)]:
        a = A.fade(2, dl)
        if a > 0:
            x = _X(yy); rect(c, x - 7, 664, 14, 20, stroke=col, a=a, sw=1.5, r=2)
    a = A.fade(2, 1.0)
    if a > 0:
        rect(c, 170, 300, 330, 80, stroke=BLUE, a=a, sw=1.4, r=6)
        text(c, 'white paper, Nov 2002', 335, 332, 20, BLUE, a, 'serif', align='c')
        text(c, 'the architecture', 335, 360, 16, DIM, a, 'serif_i', align='c')
    a = A.fade(2, 5.0)
    if a > 0:
        rect(c, 530, 300, 400, 80, stroke=BLUE, a=a, sw=1.4, r=6)
        text(c, 'Schwan, Linux Symposium 2003', 730, 332, 20, BLUE, a, 'serif', align='c')
        text(c, '"Building a File System for 1,000-node Clusters"', 730, 360, 15, DIM, a, 'serif_i', align='c')
    a = A.fade(2, 12.0)
    if a > 0:
        rect(c, 960, 300, 380, 80, stroke=GREEN, a=a, sw=1.4, r=6)
        text(c, '3 of the 8 largest clusters', 1150, 332, 20, GREEN, a, 'serif', align='c')
        text(c, 'June 2003 Top500 list', 1150, 360, 16, DIM, a, 'serif_i', align='c')
    # beat 3: owners
    ev = [(2007.7, '2007 Sun', 'u', 1, 'l', None), (2010.9, '2010 Oracle', 'd', 1, 'l', 'ends 2.x development'),
          (2011.0, '', 'u', 2, 'l', None), (2012.55, '2012 Intel', 'u', 1, 'l', 'buys Whamcloud'),
          (2018.5, '2018 DDN', 'd', 1, 'r', 'takes the team'), (2019.85, '2019 OpenSFS + EOFS', 'u', 2, 'r', 'get the trademark')]
    for q, (yy, lab, sd, lv, al, sub) in enumerate(ev):
        a = A.fade(3, 0.8 + q * 3.2)
        if lab: _ev(c, a, yy, lab, sd, lv, AMBER, al, sub)
    a = A.fade(3, 4.0)
    if a > 0:
        rect(c, _X(2010.2), 650, _X(2011.4) - _X(2010.2), 24, stroke=VIOLET, a=a, sw=1.3, r=4)
        text(c, 'Whamcloud', _X(2010.8), 667, 14, VIOLET, a, 'sans_m', align='c')
    # beat 4: open source bar
    a = A.fade(4, 0.6)
    if a > 0:
        x0, x1 = _X(2001.5), _X(2025.2)
        rect(c, x0, 940, (x1 - x0) * A.p(4, 0.6, 2.0), 16, fill=GREEN, a=a, fa=0.5 * a, r=4)
        text(c, 'open source throughout (GPL)', (x0 + x1) / 2, 925, 22, GREEN, a, 'serif', align='c')
        b = A.fade(4, 5.0)
        text(c, '> 60 of the 100 fastest machines used it since 2005 (approximate)', (x0 + x1) / 2, 985, 19, DIM, a * b, 'serif_i', align='c')

# ======================================================================= S2  objects, not blocks
def s2(c, A):
    notes = [
        (0, 200, '1', 'Schwan 2003: shared disk arrays "become cost-ineffective" on large clusters, and block-level inode and allocation locking limits scaling to "a dozen or two" nodes. This is the Lustre authors\' claim; GPFS reaches thousands of nodes by a different design.'),
        (3, 700, '2', 'Wikipedia: an OSS "typically serves 2 to 8 OSTs." Admin docs: each OST is one block device or ZFS pool/dataset.'),
    ]
    chrome(c, A, 'Objects, not blocks', 2, notes)
    n = 5
    # beat 0: block-sharing argument
    v = vis(A, 0, n)
    if v > 0:
        text(c, 'clients share raw disk blocks', 150, 230, 24, INK, v, 'serif')
        k = int(2 + 12 * A.p(0, 2.0, 8.0))
        for i in range(k):
            cx = 160 + (i % 8) * 60; cy = 300 + (i // 8) * 60
            node(c, cx, cy, 20, BLUE, v)
            line(c, cx, cy + 10, 560 + (i - 5) * 4, 520, FAINT, v * 0.5, 1)
        rect(c, 440, 520, 260, 60, stroke=DIM, a=v, sw=1.5, r=6)
        text(c, 'shared disks', 570, 558, 21, DIM, v, 'serif', align='c')
        # lock tokens crowding
        for i in range(k):
            ph = (A.t * 0.6 + i * 0.37) % 1
            lx_, ly_ = lerp(170 + (i % 8) * 60, 570, ph), lerp(310 + (i // 8) * 60, 515, ph)
            circle(c, lx_, ly_, 4, fill=AMBER, a=v * 0.8)
        text(c, 'locks on inodes and allocation maps, per block', 150, 660, 21, AMBER, v * A.fade(0, 4.0), 'serif_i')
        # scaling bar
        b = A.fade(0, 9.0)
        text(c, 'the authors: this limits scaling to roughly', 150, 740, 21, DIM, v * b, 'serif_i')
        rect(c, 150, 760, 40 * 2.4 * b, 30, fill=RED, a=v * b, fa=0.7 * b, r=4)
        text(c, 'a dozen or two nodes', 150 + 40 * 2.4 + 14, 782, 23, RED, v * b, 'serif')
    # beat 1: objects
    v = vis(A, 1, n)
    if v > 0:
        text(c, 'a file is a set of objects', 150, 230, 24, INK, v, 'serif')
        rect(c, 170, 320, 240, 150, stroke=AMBER, a=v, sw=1.6, r=8)
        text(c, 'inode on the', 290, 370, 18, DIM, v, 'serif_i', align='c')
        text(c, 'metadata server', 290, 396, 20, AMBER, v, 'serif', align='c')
        text(c, 'layout: 3 objects', 290, 440, 18, INK, v, 'serif_i', align='c')
        for q in range(3):
            y = 290 + q * 130
            a_ = v * A.fade(1, 2.5 + q * 1.8)
            server(c, 780, y, 120, 38, VIOLET, a_)
            text(c, f'storage server {q+1}', 840, y - 10, 17, VIOLET, a_, 'sans_m', align='c')
            rect(c, 970, y - 6, 56, 50, fill=BLUE, a=a_, fa=0.35 * a_, stroke=BLUE, sw=1.4, r=4)
            text(c, 'object', 998, y + 24, 15, BLUE, a_, 'sans', align='c')
            arrow(c, 410, 395, 770, y + 19, AMBER, a_ * 0.9, 1.6)
            disk(c, 1080, y - 2, 30, 46, DIM, a_, fill=DIM, fa=0.2)
            disk(c, 1120, y - 2, 30, 46, DIM, a_, fill=DIM, fa=0.2)
            arrow(c, 1030, y + 19, 1074, y + 19, DIM, a_ * 0.8, 1.2)
        b = A.fade(1, 9.0)
        text(c, 'each server decides for itself where the bytes go on its own disks', 150, 740, 21, GREEN, v * b, 'serif_i')
    # beat 2: division of labour
    v = vis(A, 2, n)
    if v > 0:
        lanes = [('metadata servers', AMBER, 300, ['names', 'directories', 'permissions', 'file layouts']),
                 ('object storage servers', VIOLET, 800, ['file data', 'as objects', 'on their own disks'])]
        for q, (ti, col, x, its) in enumerate(lanes):
            a_ = v * A.fade(2, 0.3 + q * 3.6)
            rect(c, x - 200, 250, 400, 280, stroke=col, a=a_, sw=1.6, r=10)
            text(c, ti, x, 296, 25, col, a_, 'serif', align='c')
            for j, s_ in enumerate(its): text(c, s_, x, 350 + j * 40, 21, INK, a_, 'serif_i', align='c')
        b = A.fade(2, 9.0)
        node(c, 550, 640, 28, BLUE, v * b)
        text(c, 'client', 550, 692, 18, BLUE, v * b, 'serif_i', align='c')
        arrow(c, 540, 624, 340, 540, AMBER, v * b, 2.0)
        text(c, 'ask once', 400, 600, 17, AMBER, v * b, 'serif_i', align='c')
        b2 = A.fade(2, 12.5)
        arrow(c, 560, 624, 760, 540, BLUE, v * b2, 2.6); arrow(c, 570, 630, 830, 540, BLUE, v * b2, 2.6)
        text(c, 'then talk directly', 770, 610, 17, BLUE, v * b2, 'serif_i', align='c')
    # beat 3: contrast with GPFS
    v = vis(A, 3, n)
    if v > 0:
        for (x, ti, col, kind) in [(380, 'GPFS', BLUE, 0), (1000, 'Lustre', AMBER, 1)]:
            text(c, ti, x, 250, 34, col, v, 'title', align='c')
            for i in range(4):
                nx = x - 150 + i * 100
                node(c, nx, 340, 22, BLUE, v)
            for j in range(3):
                dx = x - 100 + j * 100
                disk(c, dx - 14, 520, 28, 44, DIM, v, fill=DIM, fa=0.2)
            if kind == 0:
                for i in range(4):
                    for j in range(3):
                        line(c, x - 150 + i * 100, 352, x - 100 + j * 100, 518, VIOLET, v * 0.45, 1)
                text(c, 'any node reaches any disk', x, 620, 20, INK, v, 'serif', align='c')
                text(c, 'coordinated by tokens', x, 650, 18, AMBER, v, 'serif_i', align='c')
            else:
                for j in range(3):
                    sx = x - 100 + j * 100
                    server(c, sx - 35, 430, 70, 26, VIOLET, v)
                    line(c, sx, 456, sx, 518, DIM, v, 1.2)
                for i in range(4):
                    for j in range(3):
                        line(c, x - 150 + i * 100, 352, x - 100 + j * 100, 430, BLUE, v * 0.30, 1)
                text(c, 'each target has one server at a time', x, 620, 20, INK, v, 'serif', align='c')
                text(c, 'no one to agree with on a block', x, 650, 18, GREEN, v, 'serif_i', align='c')
    # beat 4: the price
    v = A.fade(4, 0.4)
    if v > 0:
        rect(c, 330, 330, 660, 200, stroke=RED, a=v, sw=1.6, r=10)
        text(c, 'the price', 660, 385, 24, DIM, v, 'serif_i', align='c')
        text(c, 'metadata lives in specific places', 660, 440, 30, INK, v, 'serif', align='c')
        text(c, '→ much of Lustre\'s story is about scaling that side', 660, 490, 22, AMBER, v * A.fade(4, 3.0), 'serif_i', align='c')

# ======================================================================= S3  the cast
def s3(c, A):
    notes = [
        (2, 330, '1', 'Wikipedia: "An OSS typically serves 2 to 8 OSTs." Admin docs: up to 8150 OSTs, up to 256 MDTs, typical OST 24 to 48 TB, 1024 TiB maximum.'),
        (3, 520, '2', 'Admin docs: the MGT is "less than 100 MB even on the largest systems" and is usually co-located with the first MDS.'),
        (5, 700, '3', 'Failure behaviour from the admin docs; HA partners assume failover has been configured. Default eviction timeout 100 s.'),
    ]
    chrome(c, A, 'The cast', 3, notes)
    n = 6
    base = 1.0
    a_cl = A.fade(0, 0.3)
    draw_clients(c, a_cl)
    label(c, 'clients', 200, 270, 19, BLUE, a_cl)
    if a_cl > 0.2:
        text(c, 'POSIX mount, one namespace', 200, 640, 17, DIM, a_cl, 'serif_i', align='c')
    a_f = A.fade(0, 3.0)
    draw_fabric(c, a_f)
    for i in range(18):
        x, y = client_xy(i); line(c, x + 12, y, FAB_X - 8, y, FAINT, a_f * 0.5, 1)
    a_m = A.fade(1, 0.3)
    draw_mds(c, a_m)
    line(c, FAB_X + 8, MDS_XY[1] + 19, MDS_XY[0], MDS_XY[1] + 19, FAINT, a_m * 0.6, 1.2)
    if a_m > 0:
        text(c, 'names, directories,', 820, 305, 17, DIM, a_m, 'serif_i', align='c')
        text(c, 'permissions, layouts', 820, 327, 17, DIM, a_m, 'serif_i', align='c')
        b = A.fade(1, 5.5)
        chip(c, 820, 375, 'up to 256 MDTs (DNE)', AMBER, a_m * b, w=215, size=15)
    a_o = A.fade(2, 0.3)
    for k in range(6):
        draw_oss(c, k, a_o * A.fade(2, 0.3 + k * 0.35))
        ox, oy = oss_xy(k); line(c, FAB_X + 8, oy + 18, ox, oy + 18, FAINT, a_o * 0.6, 1.2)
    if a_o > 0:
        label(c, 'storage servers (OSS) with 2 to 8 OSTs each', 1180, 295, 18, VIOLET, a_o)
        chip(c, 1190, 900, 'up to 8,150 OSTs', VIOLET, a_o * A.fade(2, 9.0), w=190, size=15)
    a_g = A.fade(3, 0.3)
    if a_g > 0:
        rect(c, 760, 130, 130, 34, stroke=INK, a=a_g, sw=1.4, r=4)
        text(c, 'MGS', 825, 154, 19, INK, a_g, 'sans_m', align='c')
        disk(c, 912, 124, 24, 38, INK, a_g)
        text(c, 'config for all file systems, < 100 MB', 840, 118 + 0, 14, DIM, a_g * 0, 'serif_i')
        line(c, 760, 147, FAB_X + 8, 147, FAINT, a_g * 0.5, 1)
        line(c, FAB_X, 147, FAB_X, 240, FAINT, a_g * 0.5, 1)
        text(c, 'management: "who is who"', 960, 154, 17, DIM, a_g, 'serif_i')
    # beat 4: open animation
    if A.started(4):
        tt = A.at(4, 1.0)
        mx, my = MDS_XY[0], MDS_XY[1] + 19
        ci = 7
        v4 = vis(A, 4, n, 0.5, 0.9)
        if tt > 0:
            p1 = route_client(ci, mx, my)
            pkt(c, p1, tt / 1.4, AMBER, v4)
            pkt(c, p1[::-1], (tt - 2.0) / 1.4, AMBER, v4, 12)
            if tt > 3.6:
                for k in range(6):
                    ox, oy = oss_xy(k); p2 = route_client(ci, ox, oy + 18)
                    for q in range(3): pkt(c, p2, ((tt - 3.8) * 0.5 - q * 0.33) % 1.0, BLUE, v4, 8)
            msg = 'open( )' if tt < 2.0 else ('layout: OSTs + stripe size' if tt < 3.7 else 'direct, parallel I/O')
            col = AMBER if tt < 3.7 else BLUE
            text(c, msg, 640, 850, 25, col, v4, 'serif_i', align='c')
            if tt > 3.7:
                rect(c, 700, 205, 200, 130, stroke=RED, a=v4 * 0.0, sw=1)
                text(c, 'MDS is out of the data path', 820, 400, 18, GREEN, v4, 'serif_i', align='c')
    # beat 5: failures
    v5 = A.fade(5, 0.4)
    if v5 > 0:
        rect(c, 20, 110, 1400, 890, fill=BG, a=v5, fa=v5)
        rows = [('storage server dies', VIOLET, 'only files on its targets are affected; a partner can take over'),
                ('metadata server stops', AMBER, 'new opens, creates, renames stall; files already open keep doing I/O'),
                ('management server stops', INK, 'the file system keeps running; new mounts and config changes wait')]
        for q, (ti, col, desc) in enumerate(rows):
            y = 300 + q * 190
            a_ = v5 * A.fade(5, 1.0 + q * 6.5)
            if q == 0: server(c, 190, y - 22, 110, 36, VIOLET, a_)
            if q == 1: server(c, 190, y - 22, 110, 36, AMBER, a_)
            if q == 2: rect(c, 190, y - 22, 110, 36, stroke=INK, a=a_, sw=1.4, r=4)
            cross(c, 245, y - 4, 16, RED, a_ * (0.5 + 0.5 * math.sin(A.t * 4)), 3)
            text(c, ti, 340, y - 6, 28, col, a_, 'serif')
            text(c, desc, 340, y + 32, 21, INK, a_, 'serif_i')
