import math, random, json
from fx import *
from lx import *

# ======================================================================= S8  mirroring and editions
def s8(c, A):
    notes = [
        (1, 200, '1', 'BeeGFS docs, mirroring: buddy group = primary + secondary target; choose equal-size targets on different servers or failure domains; storage mirroring set per directory; mirrored files consume twice their size (system requirements page).'),
        (3, 420, '2', 'Same page: switchover propagation takes up to ~30 s (default interval), "should stay under a minute"; writes during propagation may be lost; clients may read stale data from the secondary.'),
        (4, 620, '3', 'Same page: a degraded group plus another failure can lose data; an fsync error on a secondary may go undetected until its next operation; "Mirroring is not a backup."'),
        (5, 800, '4', 'beegfs.io enterprise-features page (vendor): Community capped at 1,000 TB HDD + 200 TB SSD; BeeOND up to 5 compute nodes in both editions; HA, mirroring, quota enforcement, storage pools, RST, copy, watch, index, rebalancing are Enterprise-only.'),
    ]
    chrome(c, A, 'Protection, and which edition has it', 8, notes)
    n = 7
    v = vis(A, 0, n)
    if v > 0:
        layers = [('inside a target', 'hardware RAID or ZFS', VIOLET, 200), ('across targets', 'buddy mirroring', GREEN, 720)]
        for q, (k, d, col, x) in enumerate(layers):
            a_ = v * A.fade(0, 1.0 + q * 4.0)
            rect(c, x, 330, 420, 240, stroke=col, a=a_, sw=1.8, r=12)
            text(c, k, x + 210, 410, 30, col, a_, 'serif', align='c')
            text(c, d, x + 210, 460, 24, INK, a_, 'serif_i', align='c')
        # shift second box right
    v = vis(A, 1, n)
    if v > 0:
        text(c, 'a buddy group', 150, 240, 24, INK, v, 'serif')
        for (x, nm, col, dl) in [(330, 'primary target', GREEN, 1.0), (850, 'secondary target', BLUE, 2.5)]:
            a_ = v * A.fade(1, dl)
            rect(c, x - 110, 340, 220, 130, stroke=col, a=a_, sw=1.6, r=10); text(c, nm, x, 412, 22, col, a_, 'serif', align='c')
        a_ = v * A.fade(1, 4.5)
        arrow(c, 450, 405, 730, 405, GREEN, a_, 2.6)
        for q in range(3): pkt(c, [(450, 405), (730, 405)], (A.t * 0.6 + q * 0.33) % 1.0, GREEN, a_, 10)
        text(c, 'forwarded to the secondary', 590, 380, 18, GREEN, a_, 'serif_i', align='c')
        notes_ = ['similar size', 'different servers or failure domains', 'set per directory', 'mirrored files take twice the space']
        for q, s_ in enumerate(notes_):
            check(c, 190, 580 + q * 50, 9, GREEN, v * A.fade(1, 8.0 + q * 2.2)); text(c, s_, 220, 588 + q * 50, 22, INK, v * A.fade(1, 8.0 + q * 2.2), 'serif')
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'metadata can be mirrored too', 150, 240, 24, INK, v, 'serif')
        text(c, 'once enabled, the root directory is mirrored by default', 150, 300, 22, DIM, v * A.fade(2, 2.0), 'serif_i')
        x0 = 200
        text(c, 'a target drops out and returns', 150, 420, 22, INK, v * A.fade(2, 5.0), 'serif')
        stages = [('offline: misses updates', RED, 6.0), ('re-registers', AMBER, 8.0), ('resyncs from its buddy', GREEN, 10.0)]
        for q, (s_, col, dl) in enumerate(stages):
            a_ = v * A.fade(2, dl)
            rect(c, x0 + q * 360, 470, 330, 70, fill=col, a=a_, fa=0.2 * a_, stroke=col, sw=1.5, r=8)
            text(c, s_, x0 + q * 360 + 165, 515, 21, col, a_, 'serif', align='c')
            if q: arrow(c, x0 + q * 360 - 28, 505, x0 + q * 360 - 2, 505, FAINT, a_, 1.6)
        text(c, 'usually automatic; manual resync also available', 150, 640, 21, DIM, v * A.fade(2, 13.0), 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'failover is not instant', 150, 240, 26, INK, v, 'serif')
        x0, x1 = 200, 1160
        line(c, x0, 480, x1, 480, FAINT, v, 1.5)
        for s_, lab in [(0, 'state change'), (30, '≈ 30 s default interval'), (60, '< 1 min')]:
            xx = lerp(x0, x1, s_ / 70)
            line(c, xx, 460, xx, 500, INK, v, 1.5); text(c, lab, xx, 535, 17, DIM, v, 'serif_i', align='c')
        pr = A.p(3, 1.5, 4.0)
        rect(c, x0, 465, (lerp(x0, x1, 30 / 70) - x0) * pr, 30, fill=AMBER, a=v, fa=0.5 * v, r=3)
        b = A.fade(3, 6.0)
        text(c, 'during the window: writes may be lost', 200, 620, 24, RED, v * b, 'serif')
        text(c, 'or a client may read stale data from the secondary', 200, 665, 24, RED, v * A.fade(3, 8.5), 'serif')
    v = vis(A, 4, n)
    if v > 0:
        items = ['a degraded group + one more failure can lose data', 'an fsync error on the secondary may go unnoticed until its next operation', 'mirroring is not a backup: deleted or overwritten files are not recoverable']
        for q, s_ in enumerate(items):
            a_ = v * A.fade(4, 1.0 + q * 4.5)
            cross(c, 175, 350 + q * 100, 9, RED, a_, 2.2); text(c, s_, 210, 358 + q * 100, 24, INK, a_, 'serif')
    v = vis(A, 5, n)
    if v > 0:
        text(c, 'vendor edition table (beegfs.io)', 150, 240, 22, DIM, v, 'serif_i')
        text(c, 'Community', 760, 290, 22, GREEN, v, 'sans_m', align='c'); text(c, 'Enterprise', 1030, 290, 22, AMBER, v, 'sans_m', align='c')
        rows = [('ACLs, monitoring', 1, 1), ('capacity', None, None), ('high availability', 0, 1), ('mirroring (metadata + data)', 0, 1), ('quota enforcement', 0, 1), ('storage pools, auto-tiering', 0, 1), ('remote storage targets (S3)', 0, 1), ('BeeOND', None, None)]
        for q, (k, cm, en) in enumerate(rows):
            y = 340 + q * 58
            a_ = v * A.fade(5, 1.0 + q * 1.7)
            text(c, k, 150, y, 22, INK, a_, 'serif')
            if cm is None and k == 'capacity':
                text(c, '1,000 TB HDD + 200 TB SSD', 760, y, 17, GREEN, a_, 'serif_i', align='c'); text(c, 'not capped', 1030, y, 17, AMBER, a_, 'serif_i', align='c')
            elif cm is None:
                text(c, 'up to 5 nodes', 760, y, 17, DIM, a_, 'serif_i', align='c'); text(c, 'up to 5 nodes', 1030, y, 17, DIM, a_, 'serif_i', align='c')
            else:
                (check if cm else cross)(c, 760, y - 6, 9, GREEN if cm else RED, a_, 2.2)
                (check if en else cross)(c, 1030, y - 6, 9, GREEN if en else RED, a_, 2.2)
    v = A.fade(6, 0.4)
    if v > 0:
        rect(c, 280, 330, 760, 230, stroke=AMBER, a=v, sw=1.6, r=10)
        text(c, 'the comparison depends on the edition', 660, 410, 28, INK, v, 'serif', align='c')
        text(c, 'check the table against your needs', 660, 460, 24, DIM, v * A.fade(6, 2.0), 'serif_i', align='c')
        text(c, 'before assuming a feature is there', 660, 498, 24, DIM, v * A.fade(6, 3.5), 'serif_i', align='c')

# ======================================================================= S9  BeeOND and version 8
def s9(c, A):
    notes = [
        (0, 200, '1', 'BeeGFS docs, BeeOND: pools the internal drives of compute nodes into a temporary parallel file system for the duration of a job; also works as a burst buffer. Both editions: up to 5 compute nodes contributing storage.'),
        (1, 360, '2', 'BeeOND docs: `beeond start -n nodefile -d /data/beeond -c /mnt/beeond`; `beeond stop -n nodefile -L -d`; Slurm and Torque named for prologue/epilogue integration; `beegfs copy` for parallel stage-in/out.'),
        (2, 560, '3', 'Next Platform (Jan 2018): "Fujitsu\'s ABCI ... uses BeeOND on compute nodes for a 1PB NVMe burst buffer at 1TB/s, according to ThinkParQ." Vendor claim, not verified.'),
        (3, 740, '4', 'BeeGFS 8.0.0 release notes: management service rewritten in Rust with an SQL database; gRPC + TLS; SHA256 connection authentication; beegfs-helperd removed; new Go-based `beegfs` CLI replaces beegfs-ctl; RSTs for S3-compatible storage; not compatible with older versions.'),
    ]
    chrome(c, A, 'Beyond (BeeOND), and version 8', 9, notes)
    n = 7
    v = vis(A, 0, n)
    if v > 0:
        text(c, 'BeeOND = BeeGFS On Demand', 150, 240, 26, INK, v, 'serif')
        for q in range(4):
            x = 200 + q * 260
            a_ = v * A.fade(0, 1.0 + q * 1.0)
            rect(c, x, 330, 200, 150, stroke=BLUE, a=a_, sw=1.5, r=10)
            text(c, f'node {q+1}', x + 100, 360, 17, BLUE, a_, 'sans_m', align='c')
            disk(c, x + 70, 390, 28, 44, VIOLET, a_, fill=VIOLET, fa=0.25)
            disk(c, x + 110, 390, 28, 44, VIOLET, a_, fill=VIOLET, fa=0.25)
        b = A.fade(0, 7.0)
        if b > 0:
            rect(c, 180, 530, 1040, 70, fill=GREEN, a=v * b, fa=0.18 * b, stroke=GREEN, sw=1.6, r=12)
            text(c, 'one temporary parallel file system, for the length of the job', 700, 574, 26, GREEN, v * b, 'serif', align='c')
            for q in range(4): arrow(c, 300 + q * 260, 490, 300 + q * 260, 526, GREEN, v * b, 1.8)
        text(c, 'local SSDs or disks of the job\'s compute nodes', 200, 680, 21, DIM, v * A.fade(0, 10.0), 'serif_i')
    v = vis(A, 1, n)
    if v > 0:
        rect(c, 150, 290, 1200, 80, fill=(24, 28, 36), a=v, fa=v, stroke=RULE, r=8)
        mono(c, '$ beeond start -n nodefile -d /data/beeond -c /mnt/beeond', 180, 342, 24, GREEN, v)
        parts = [('-n', 'hosts: each becomes client and server'), ('-d', 'raw data directory on each node'), ('-c', 'mount point')]
        for q, (k, d) in enumerate(parts):
            a_ = v * A.fade(1, 2.0 + q * 2.5)
            mono(c, k, 190, 450 + q * 52, 24, AMBER, a_); text(c, d, 270, 457 + q * 52, 22, INK, a_, 'serif')
        x0, x1 = 200, 1150
        a_ = v * A.fade(1, 11.0)
        line(c, x0, 700, x1, 700, FAINT, a_, 1.5)
        for xx, lab, col in [(x0, 'job prologue: beeond start', GREEN), ((x0 + x1) / 2, 'job runs', DIM), (x1, 'epilogue: beeond stop', RED)]:
            circle(c, xx, 700, 7, fill=col, a=a_); text(c, lab, xx, 740, 19, col if col != DIM else INK, a_, 'serif_i', align='c')
        text(c, 'documented with Slurm and Torque', 700, 810, 19, DIM, v * A.fade(1, 14.0), 'serif_i', align='c')
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'a burst buffer on local flash', 150, 250, 26, INK, v, 'serif')
        text(c, '1 PB', 330, 450, 90, GREEN, v * A.fade(2, 3.0), 'title', align='c')
        text(c, 'NVMe burst buffer', 330, 500, 22, DIM, v * A.fade(2, 3.0), 'serif_i', align='c')
        text(c, '1 TB/s', 800, 450, 90, GREEN, v * A.fade(2, 5.5), 'title', align='c')
        text(c, 'claimed bandwidth', 800, 500, 22, DIM, v * A.fade(2, 5.5), 'serif_i', align='c')
        chip(c, 560, 580, 'vendor claim (ThinkParQ via Next Platform): indicative only', RED, v * A.fade(2, 8.0), w=620, size=16)
        text(c, 'stage results out to persistent storage afterwards (beegfs copy)', 150, 700, 22, AMBER, v * A.fade(2, 12.0), 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'BeeGFS 8: management service', 150, 240, 26, INK, v, 'serif')
        for (x, ti, col, items, dl) in [(360, 'before', DIM, ['custom protocol', 'custom auth hash', 'string node IDs'], 1.0), (960, 'version 8', GREEN, ['rewritten from scratch in Rust', 'SQL database', 'gRPC → TLS possible', 'SHA-256 authentication'], 4.0)]:
            a_ = v * A.fade(3, dl)
            rect(c, x - 250, 320, 500, 330, stroke=col, a=a_, sw=1.6, r=10)
            text(c, ti, x, 370, 28, col if col != DIM else INK, a_, 'serif', align='c')
            for q, s_ in enumerate(items): text(c, s_, x, 430 + q * 52, 22, INK, a_ * A.fade(3, dl + 1.0 + q * 1.2), 'serif', align='c')
        text(c, '(left column: what the notes imply was replaced; wording mine)', 150, 720, 16, FAINT, v * A.fade(3, 4.0), 'serif_i')
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'beegfs-ctl  →  beegfs', 700, 330, 48, INK, v, 'title', align='c')
        for q, s_ in enumerate(['written in Go', 'noun-verb commands', 'tables by default, JSON on request', 'helper daemon removed']):
            a_ = v * A.fade(4, 1.5 + q * 2.2)
            check(c, 330, 430 + q * 60, 10, GREEN, a_); text(c, s_, 370, 438 + q * 60, 26, INK, a_, 'serif')
    v = vis(A, 5, n)
    if v > 0:
        text(c, 'remote storage targets (RST)', 150, 250, 26, INK, v, 'serif')
        rect(c, 230, 360, 320, 160, stroke=GREEN, a=v, sw=1.6, r=10); text(c, 'BeeGFS', 390, 450, 30, GREEN, v, 'title', align='c')
        a_ = v * A.fade(5, 3.0)
        rect(c, 820, 360, 320, 160, stroke=BLUE, a=a_, sw=1.6, r=10); text(c, 'S3-compatible', 980, 436, 24, BLUE, a_, 'serif', align='c'); text(c, 'object storage', 980, 470, 24, BLUE, a_, 'serif', align='c')
        for q in range(3): pkt(c, [(550, 420 + q * 20), (820, 420 + q * 20)], (A.t * 0.4 + q * 0.3) % 1.0, BLUE, a_, 9)
        text(c, 'two new services move data in parallel', 690, 590, 22, DIM, v * A.fade(5, 7.0), 'serif_i', align='c')
        chip(c, 690, 670, 'Enterprise feature', AMBER, v * A.fade(5, 10.0), w=240, size=17)
    v = A.fade(6, 0.4)
    if v > 0:
        rect(c, 280, 330, 760, 230, stroke=RED, a=v, sw=1.6, r=10)
        text(c, 'BeeGFS 8 is not compatible with older versions', 660, 410, 28, INK, v, 'serif', align='c')
        text(c, 'network and on-disk formats changed', 660, 462, 24, DIM, v * A.fade(6, 2.0), 'serif_i', align='c')
        text(c, 'plan the upgrade', 660, 510, 24, AMBER, v * A.fade(6, 4.0), 'serif_i', align='c')

# ======================================================================= S10  compare + recap + sources
def s10(c, A):
    notes = [
        (0, 240, '1', 'My summary, as described in the sources used across the three videos. GPFS dates: Vesta/Tiger Shark lineage early 1990s (Wikipedia, secondary).'),
        (4, 640, '2', 'The BeeGFS consistency cell is "not verified" by me; the other two come from the GPFS FAST \'02 paper and Lustre sources (Schwan 2003).'),
        (5, 820, '3', 'I did not find a fair same-hardware benchmark of GPFS vs Lustre vs BeeGFS. Weka, DAOS, CephFS and PanFS are named only to say they are not covered.'),
    ]
    chrome(c, A, 'The three, side by side', 10, notes)
    n = 7
    cols = [('GPFS', BLUE), ('Lustre', AMBER), ('BeeGFS', GREEN)]
    rows = [('born', ['IBM research lineage, early 1990s', 'research project, 1999', 'Fraunhofer ITWM, 2005']),
            ('metadata', ['spread over all nodes; tokens, metanode per file', 'metadata servers; sharded with DNE', 'directories sharded across metadata servers']),
            ('disk ownership', ['shared among nodes', 'one server per target at a time', 'each target behind a storage service']),
            ('protection', ['declustered RAID, or replication', 'RAID / ZFS; mirrored layouts available', 'RAID / ZFS; buddy mirroring (Enterprise)']),
            ('consistency', ['single-node-equivalent semantics via tokens', 'distributed lock manager', 'not verified in the docs I read'])]
    x0s = [470, 820, 1170]
    ta = A.fade(0, 0.3)
    for k, (nm, col) in enumerate(cols): text(c, nm, x0s[k], 220, 30, col, ta, 'title', align='c')
    for r_, (rn, cells) in enumerate(rows):
        y = 300 + r_ * 130
        # reveal row r_ at beat index (0->born,1->metadata,2->ownership,3->protection,4->consistency)
        a_ = A.fade(r_, 0.5)
        line(c, 150, y - 36, 1330, y - 36, RULE, a_ * 0.7, 0.8)
        text(c, rn, 150, y, 21, DIM, a_, 'serif_i')
        for k, cell in enumerate(cells):
            col = RED if (r_ == 4 and k == 2) else INK
            for li, ln in enumerate(wrap(cell, 17, 300, 'serif')): text(c, ln, x0s[k], y + li * 24, 17, col, a_ * A.fade(r_, 0.8 + k * 0.5), 'serif', align='c')
    v = A.fade(5, 0.6)
    if v > 0:
        rect(c, 20, 110, 1400, 890, fill=BG, a=v, fa=v)
        text(c, 'three systems are not all of them', 150, 280, 30, INK, v, 'serif')
        text(c, 'not covered here: Weka, DAOS, CephFS, PanFS', 150, 350, 24, DIM, v * A.fade(5, 3.0), 'serif_i')
        text(c, 'no fair same-hardware benchmark of these three in my research', 150, 440, 24, AMBER, v * A.fade(5, 7.0), 'serif')
        text(c, 'so none of this says which is fastest', 150, 484, 24, AMBER, v * A.fade(5, 9.0), 'serif')
    v = A.fade(6, 0.4)
    if v > 0:
        rect(c, 20, 110, 1400, 890, fill=BG, a=v, fa=v)
        text(c, 'BeeGFS in one line each', 150, 190, 26, DIM, v, 'serif_i')
        pts = [('four services', GREEN), ('chunked striping, set per directory', BLUE), ('metadata sharded by directory', AMBER), ('RDMA networking', VIOLET), ('buddy mirroring and more: Enterprise', RED), ('BeeOND for job-local file systems', INK)]
        for q, (s_, col) in enumerate(pts): text(c, s_, 150, 250 + q * 50, 25, col, v * A.fade(6, 1.0 + q * 2.4), 'serif')
        srcs = A.fade(6, 15.5)
        if srcs > 0:
            rect(c, 20, 110, 1400, 890, fill=BG, a=srcs, fa=srcs)
            text(c, 'sources', 150, 190, 28, INK, srcs, 'serif')
            L = ['BeeGFS documentation: architecture, striping, mirroring, system requirements, metadata tuning, client tuning, RDMA support, client metadata caching, BeeOND, release notes 8.0 (doc.beegfs.io)',
                 'beegfs.io: Community vs Enterprise features table; HPC solution brief (vendor)',
                 'Wikipedia, "BeeGFS": history, licensing, early deployments',
                 'HPCwire (Nov 2018) and The Next Platform (Jan 2018): trade press with vendor quotes (CSIRO, ABCI/BeeOND)',
                 'NetApp blog, "BeeGFS for Beginners" (Oct 2019): partner overview',
                 'For the comparison: Schmuck & Haskin, GPFS (USENIX FAST \'02); Cluster File Systems / Schwan on Lustre; earlier videos',
                 'my own: sim_stripe.py toy simulation, peer-count example, memory estimate (all labelled on screen)']
            yy = 250
            for q, s_ in enumerate(L):
                for q2, ln in enumerate(wrap(s_, 20, 1180)):
                    text(c, ln, 150, yy, 20, INK if q < 6 else AMBER, srcs * A.fade(6, 16.0 + q * 0.3), 'serif'); yy += 26
                yy += 18
