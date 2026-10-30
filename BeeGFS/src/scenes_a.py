import math, random
from fx import *
from lx import *

MGMT_XY = (760, 130)

def _draw_mgmt(c, a=1.0, x=None, y=None):
    x0, y0 = (x, y) if x is not None else MGMT_XY
    rect(c, x0, y0, 120, 34, stroke=INK, a=a, sw=1.4, r=4)
    text(c, 'management', x0 + 60, y0 + 23, 16, INK, a, 'sans_m', align='c')
    disk(c, x0 + 140, y0 - 4, 24, 38, INK, a)

def _open_cycle(c, A, t0, a, per=7.0, n_oss=6, cl=(0, 7, 13)):
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

# ======================================================================= S0  cold open
def s0(c, A):
    notes = [
        (0, 200, '1', 'Next Platform (Jan 2018) and BeeGFS docs: designed for performance and ease of use ("the file system is just a tool to get the job done," a vendor voice).'),
        (2, 640, '2', 'BeeGFS docs: the client contacts metadata servers for file details, then storage servers directly for file I/O.'),
    ]
    chrome(c, A, 'The third of the big three', 0, notes)
    n = 4
    v0 = vis(A, 0, n)
    if v0 > 0:
        for q, (nm, col, x, sz) in enumerate([('GPFS', BLUE, 280, 46), ('Lustre', AMBER, 660, 46), ('BeeGFS', GREEN, 1040, 70)]):
            a_ = v0 * A.fade(0, 0.5 + q * 3.5 if q < 2 else 12.0)
            text(c, nm, x, 420, sz, col, a_, 'title', align='c')
        text(c, 'intelligence in every node', 280, 470, 19, DIM, v0 * A.fade(0, 1.0), 'serif_i', align='c')
        text(c, 'metadata apart from data', 660, 470, 19, DIM, v0 * A.fade(0, 4.5), 'serif_i', align='c')
        text(c, 'performance and ease of use', 1040, 500, 21, GREEN, v0 * A.fade(0, 14.0), 'serif_i', align='c')
    v1 = vis(A, 1, n)
    if v1 > 0:
        svc = [('management', 'a registry', INK), ('metadata', 'knows where things are', AMBER), ('storage', 'holds the data', VIOLET), ('client', 'mounts it as a directory', BLUE)]
        for q, (nm, sub, col) in enumerate(svc):
            a_ = v1 * A.fade(1, 1.5 + q * 3.2)
            x = 170 + q * 290
            rect(c, x, 360, 250, 170, stroke=col, a=a_, sw=1.6, r=10)
            text(c, nm, x + 125, 430, 28, col, a_, 'serif', align='c')
            text(c, sub, x + 125, 472, 19, DIM, a_, 'serif_i', align='c')
        text(c, 'four kinds of service', 660, 300, 24, INK, v1, 'serif', align='c')
    v2 = A.fade(2, 0.3, 1.0)
    if v2 > 0:
        draw_clients(c, v2)
        label(c, 'clients', 200, 270, 19, BLUE, v2)
        draw_fabric(c, v2)
        draw_mds(c, v2, name='metadata', tgt='')
        _draw_mgmt(c, v2 * 0.9)
        for k in range(6): draw_oss(c, k, v2, name=f'storage {k+1}')
        for i in range(18):
            x, y = client_xy(i); line(c, x + 12, y, FAB_X - 8, y, FAINT, v2 * 0.5, 1)
        line(c, FAB_X + 8, MDS_XY[1] + 19, MDS_XY[0], MDS_XY[1] + 19, FAINT, v2 * 0.6, 1.2)
        for k in range(6):
            ox, oy = oss_xy(k); line(c, FAB_X + 8, oy + 18, ox, oy + 18, FAINT, v2 * 0.6, 1.2)
        tt = A.at(2, 1.0)
        if tt > 0:
            _open_cycle(c, A, tt, v2)
            ph = tt % 7.0
            lab = 'ask the metadata server: how is this file striped?' if ph < 2.6 else ('stream to the storage servers directly, in parallel' if ph < 6.4 else '')
            col = AMBER if ph < 2.6 else BLUE
            if lab: text(c, lab, 640, 880, 24, col, v2, 'serif_i', align='c')
    v3 = A.fade(3, 0.4, 1.0)
    if v3 > 0:
        items = [('history', INK), ('striping', BLUE), ('metadata', AMBER), ('consistency', RED), ('network', VIOLET), ('mirroring', GREEN)]
        for q, (s_, col) in enumerate(items):
            chip(c, 200 + q * 190, 960, s_, col, v3 * A.fade(3, 0.5 + q * 1.5), w=165, size=16)

# ======================================================================= S1  history
def _X(y): return 150 + (y - 2005) * 56.0

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
        (0, 160, '1', 'Wikipedia (secondary): development began 2005 as an in-house Fraunhofer ITWM project; Next Platform / HPCwire (2018) agree on 2005 and the FhGFS name.'),
        (1, 330, '2', 'Wikipedia: first beta announced at ISC07 (Dresden), introduced at SC07 (Reno), first stable major release a year later.'),
        (2, 480, '3', 'Wikipedia: ThinkParQ founded 2014 as a Fraunhofer spin-off; ~100 commercially supported customers in 2014. 2018 CSIRO deal: a 2 PB all-NVMe system (vendor quote, HPCwire).'),
        (3, 700, '4', 'I found no founding paper for BeeGFS. Sources used: docs.beegfs.io / doc.beegfs.io (primary), Wikipedia, HPCwire, Next Platform, NetApp blog (secondary / vendor).'),
        (4, 880, '5', 'Wikipedia infobox: server proprietary, client GPL v2. beegfs.io edition table: Community self-supported; Enterprise requires a support contract.'),
    ]
    chrome(c, A, 'Where it came from', 1, notes)
    n = 5
    pa = A.fade(0, 0.2)
    line(c, _X(2004.5), 700, _X(2027.0), 700, FAINT, pa, 1.4)
    for yr in range(2005, 2027, 3):
        x = _X(yr); line(c, x, 700, x, 707, FAINT, pa); text(c, str(yr), x, 728, 14, DIM, pa, 'sans', align='c')
    a = A.fade(0, 1.0)
    _ev(c, a, 2005.0, '2005  in-house project', 'u', 1, INK, 'l', 'Fraunhofer ITWM, Germany')
    if a > 0:
        rect(c, 150, 220, 560, 84, stroke=AMBER, a=a * A.fade(0, 8.0), sw=1.5, r=6)
        text(c, 'FhGFS', 220, 262, 30, AMBER, a * A.fade(0, 8.0), 'title', align='c')
        text(c, 'Fraunhofer Gesellschaft File System', 440, 262, 19, DIM, a * A.fade(0, 8.0), 'serif_i', align='c')
        text(c, 'built to replace the file system of a new cluster', 150, 330, 20, DIM, a * A.fade(0, 4.0), 'serif_i')
    _ev(c, A.fade(1, 0.8), 2007.4, '2007  first beta', 'd', 0.8, INK, 'l', 'ISC07 Dresden · SC07 Reno')
    _ev(c, A.fade(1, 6.0), 2008.4, '~2008  first stable release', 'u', 2.3, GREEN, 'l')
    a = A.fade(2, 0.8)
    _ev(c, a, 2014.3, '2014  ThinkParQ founded, FhGFS → BeeGFS', 'u', 1, AMBER, 'l', 'spin-off from Fraunhofer')
    a2 = A.fade(2, 7.0)
    if a2 > 0:
        rect(c, 880, 330, 480, 120, stroke=GREEN, a=a2, sw=1.4, r=8)
        text(c, '≈ 100 supported customers', 1120, 372, 24, GREEN, a2, 'serif', align='c')
        text(c, 'universities · research labs', 1120, 402, 17, DIM, a2, 'serif_i', align='c')
        text(c, 'finance · oil and gas', 1120, 426, 17, DIM, a2, 'serif_i', align='c')
    _ev(c, A.fade(2, 12.0), 2018.0, '2018  CSIRO deal, 2 PB all-NVMe', 'd', 1.3, DIM, 'l', '(vendor quote)')
    a3 = A.fade(3, 0.5)
    if a3 > 0:
        text(c, 'no founding paper that I could find', 150, 400, 26, INK, a3, 'serif')
        rows = [('primary', 'product documentation', GREEN), ('secondary', 'Wikipedia, trade press', AMBER), ('vendor voice', 'interviews, solution briefs', RED)]
        for q, (k, v_, col) in enumerate(rows):
            aa = a3 * A.fade(3, 5.0 + q * 3.0)
            chip(c, 240, 480 + q * 56, k, col, aa, w=170, size=16)
            text(c, v_, 360, 487 + q * 56, 21, INK, aa, 'serif')
    a4 = A.fade(4, 0.5)
    if a4 > 0:
        cols = [('client', 'GPL v2', GREEN), ('servers', 'proprietary, free to use (Community)', AMBER), ('Enterprise', 'extra features, needs a support subscription', VIOLET)]
        for q, (k, v_, col) in enumerate(cols):
            aa = a4 * A.fade(4, 1.0 + q * 3.5)
            x = 150 + q * 400
            rect(c, x, 400, 370, 150, stroke=col, a=aa, sw=1.5, r=10)
            text(c, k, x + 185, 450, 28, col, aa, 'serif', align='c')
            for li, ln in enumerate(wrap(v_, 19, 330, 'serif_i')): text(c, ln, x + 185, 490 + li * 26, 19, DIM, aa, 'serif_i', align='c')

# ======================================================================= S2  what it is built on
def s2(c, A):
    notes = [
        (0, 200, '1', 'BeeGFS docs (architecture): storage runs as user-space daemons; metadata target typically ext4 on RAID1/10 flash; storage typically xfs on hardware RAID. NetApp (2019): management, storage, metadata are user-space daemons; client is a patchless kernel module.'),
        (2, 480, '2', 'Next Platform (2018), vendor quote: "you really can start with two servers and then you can just add components on the fly."'),
        (3, 700, '3', 'Bright Computing CTO (Next Platform, 2018): "we found BeeGFS to be the most lightweight" compared with GPFS and Lustre. A partner\'s opinion, not a measurement.'),
    ]
    chrome(c, A, 'Built on what is already there', 2, notes)
    n = 5
    v = vis(A, 0, n)
    if v > 0:
        # layered stack: client (kernel) ... server (user space over local FS over RAID)
        text(c, 'a server, layer by layer', 150, 240, 22, INK, v, 'serif')
        layers = [('BeeGFS service (user-space daemon)', VIOLET, 0), ('local file system', INK, 1), ('RAID or ZFS', DIM, 2), ('disks', DIM, 3)]
        for lab, col, q in layers:
            a_ = v * A.fade(0, 1.0 + q * 2.0)
            rect(c, 200, 290 + q * 95, 560, 80, stroke=col, a=a_, sw=1.6, r=8, fill=col, fa=0.10 * a_)
            text(c, lab, 480, 340 + q * 95, 24, col if col != DIM else INK, a_, 'serif', align='c')
        b = A.fade(0, 9.0)
        text(c, 'metadata: usually ext4', 800, 380, 22, AMBER, v * b, 'serif_i')
        text(c, 'storage: usually XFS', 800, 475, 22, VIOLET, v * b, 'serif_i')
        arrow(c, 790, 375, 770, 380 + 0, AMBER, v * b, 1.4)
    v = vis(A, 1, n)
    if v > 0:
        rect(c, 200, 300, 500, 140, stroke=BLUE, a=v, sw=1.6, r=10)
        text(c, 'client', 450, 350, 28, BLUE, v, 'serif', align='c')
        text(c, 'a kernel module', 450, 392, 21, INK, v, 'serif_i', align='c')
        text(c, 'patchless', 450, 420, 18, DIM, v * A.fade(1, 2.5), 'serif_i', align='c')
        chip(c, 900, 360, 'compiled for your running kernel', BLUE, v * A.fade(1, 3.5), w=330, size=16)
        chip(c, 900, 420, 'install or update without a reboot', GREEN, v * A.fade(1, 6.5), w=330, size=16)
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'any combination of services can share a machine', 150, 240, 22, INK, v, 'serif')
        servers = [(200, 'server 1', ['mgmt', 'meta', 'storage']), (520, 'server 2', ['meta', 'storage'])]
        for q, (x, nm, svcs) in enumerate(servers):
            a_ = v * A.fade(2, 1.0 + q * 2.0)
            rect(c, x, 300, 280, 190, stroke=VIOLET, a=a_, sw=1.5, r=10)
            text(c, nm, x + 140, 330, 19, VIOLET, a_, 'sans_m', align='c')
            for k, s_ in enumerate(svcs):
                chip(c, x + 140, 372 + k * 38, s_, {'mgmt': INK, 'meta': AMBER, 'storage': VIOLET}[s_], a_, w=130, size=15)
        for q in range(3):
            a_ = v * A.fade(2, 6.0 + q * 1.5)
            x = 840 + q * 150
            rect(c, x, 300, 120, 190, stroke=VIOLET, a=a_, sw=1.3, r=10, dash=[5, 4])
            text(c, '+ server', x + 60, 400, 17, DIM, a_, 'serif_i', align='c')
        text(c, 'start small, add components on the fly (vendor claim)', 200, 580, 21, GREEN, v * A.fade(2, 8.0), 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        cols = ['GPFS', 'Lustre', 'BeeGFS']; colc = [BLUE, AMBER, GREEN]
        rows = [('RAID', ['own software RAID (optional)', 'RAID or ZFS underneath', 'RAID or ZFS underneath']),
                ('lock manager', ['tokens', 'distributed lock manager', 'not found in the docs I read']),
                ('network layer', ['standard fabrics', 'its own (LNet)', 'OpenFabrics verbs or TCP'])]
        for k, nm in enumerate(cols): text(c, nm, 540 + k * 300, 270, 30, colc[k], v, 'title', align='c')
        for r_, (rn, cells) in enumerate(rows):
            y = 360 + r_ * 110
            text(c, rn, 150, y, 21, DIM, v * A.fade(3, 1.0 + r_ * 3.0), 'serif_i')
            for k, cell in enumerate(cells):
                col = AMBER if (r_ == 1 and k == 2) else INK
                for li, ln in enumerate(wrap(cell, 19, 270, 'serif')): text(c, ln, 540 + k * 300, y + li * 26, 19, col, v * A.fade(3, 1.0 + r_ * 3.0 + k * 0.4), 'serif', align='c')
    v = A.fade(4, 0.4)
    if v > 0:
        rect(c, 330, 330, 660, 200, stroke=AMBER, a=v, sw=1.6, r=10)
        text(c, 'thin has a price', 660, 395, 32, INK, v, 'serif', align='c')
        text(c, 'fewer documented guarantees', 660, 445, 23, DIM, v * A.fade(4, 2.5), 'serif_i', align='c')
        text(c, 'protection features in the paid edition', 660, 485, 23, DIM, v * A.fade(4, 4.5), 'serif_i', align='c')

# ======================================================================= S3  the services
def s3(c, A):
    notes = [
        (0, 200, '1', 'BeeGFS docs: management is "the registry and watchdog," not performance-critical, stores no user data. NetApp blog (2019): 88 KB in the author\'s environment.'),
        (1, 380, '2', 'BeeGFS docs: one metadata target per metadata instance, a local POSIX file system (ext4 typical, RAID1/10 of flash).'),
        (2, 560, '3', 'BeeGFS docs: storage targets typically hardware RAID-6 (8+2 or 10+2) or ZFS RAIDz2, usually xfs on hardware RAID.'),
        (3, 740, '4', 'BeeGFS docs / NetApp blog: client mounts at /mnt/beegfs by default; after open, the metadata service does not take part in reads or writes until close.'),
    ]
    chrome(c, A, 'The services', 3, notes)
    n = 6
    a_cl = A.fade(3, 0.3) if False else 1.0
    draw_clients(c, A.fade(0, 0.2))
    label(c, 'clients', 200, 270, 19, BLUE, A.fade(0, 0.2))
    a_f = A.fade(0, 1.0)
    draw_fabric(c, a_f)
    for i in range(18):
        x, y = client_xy(i); line(c, x + 12, y, FAB_X - 8, y, FAINT, a_f * 0.5, 1)
    # management
    a = A.fade(0, 0.5)
    _draw_mgmt(c, a)
    if a > 0:
        line(c, FAB_X, 147, FAB_X, 240, FAINT, a * 0.5, 1); line(c, FAB_X, 147, MGMT_XY[0], 147, FAINT, a * 0.5, 1)
        text(c, 'registry and watchdog; no user data', 960, 154, 17, DIM, a * A.fade(0, 4.0), 'serif_i')
        text(c, 'not in the I/O path', 960, 180, 17, GREEN, a * A.fade(0, 8.0), 'serif_i')
    a = A.fade(1, 0.3)
    draw_mds(c, a, name='metadata', tgt='1 target')
    line(c, FAB_X + 8, MDS_XY[1] + 19, MDS_XY[0], MDS_XY[1] + 19, FAINT, a * 0.6, 1.2)
    if a > 0:
        text(c, 'namespace, ownership,', 820, 305, 17, DIM, a, 'serif_i', align='c')
        text(c, 'stripe pattern per file', 820, 327, 17, DIM, a, 'serif_i', align='c')
        text(c, 'ext4 on mirrored flash', 820, 360, 17, AMBER, a * A.fade(1, 5.0), 'serif_i', align='c')
    a_o = A.fade(2, 0.3)
    for k in range(6):
        draw_oss(c, k, a_o * A.fade(2, 0.3 + k * 0.35), name=f'storage {k+1}')
        ox, oy = oss_xy(k); line(c, FAB_X + 8, oy + 18, ox, oy + 18, FAINT, a_o * 0.6, 1.2)
    if a_o > 0:
        label(c, 'chunk files; RAID 6 or ZFS RAIDz2 targets', 1180, 282, 17, VIOLET, a_o)
        chip(c, 1180, 920, 'add servers → add capacity and bandwidth', VIOLET, a_o * A.fade(2, 8.0), w=400, size=15)
    if A.started(4):
        tt = A.at(4, 1.0)
        v4 = vis(A, 4, n, 0.5, 0.9)
        if tt > 0:
            mx, my = MDS_XY[0], MDS_XY[1] + 19
            ci = 7
            p1 = route_client(ci, mx, my)
            pkt(c, p1, tt / 1.4, AMBER, v4); pkt(c, p1[::-1], (tt - 2.0) / 1.4, AMBER, v4, 12)
            if tt > 3.6:
                for k in range(6):
                    ox, oy = oss_xy(k); p2 = route_client(ci, ox, oy + 18)
                    for q in range(3): pkt(c, p2, ((tt - 3.8) * 0.5 - q * 0.33) % 1.0, BLUE, v4, 8)
            msg = 'open( )' if tt < 2.0 else ('stripe pattern comes back' if tt < 3.7 else 'direct, parallel I/O')
            text(c, msg, 640, 860, 25, AMBER if tt < 3.7 else BLUE, v4, 'serif_i', align='c')
    v5 = A.fade(5, 0.4)
    if v5 > 0:
        rect(c, 20, 110, 1400, 890, fill=BG, a=v5, fa=v5)
        text(c, 'optional extras, off the data path', 150, 260, 26, INK, v5, 'serif')
        rows = [('monitoring service', 'feeds a time-series database, e.g. InfluxDB, for Grafana dashboards', GREEN), ('admin GUI service', 'described in older documentation (Java GUI over HTTP)', DIM)]
        for q, (k, d, col) in enumerate(rows):
            a_ = v5 * A.fade(5, 1.0 + q * 4.0)
            text(c, k, 190, 360 + q * 120, 28, col if col != DIM else INK, a_, 'serif')
            text(c, d, 190, 400 + q * 120, 21, DIM, a_, 'serif_i')
