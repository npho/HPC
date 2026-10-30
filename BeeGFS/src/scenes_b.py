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

CH_COL = [mix(BLUE, GREEN, i / 8) for i in range(9)]

# ======================================================================= S4  striping
def s4(c, A):
    notes = [
        (0, 200, '1', 'BeeGFS docs, Client Node Tuning: chunk size "default 512 KiB". The striping page\'s example output shows RAID0 (4x1M) for the root directory, so the two pages differ; check your own system with `beegfs entry info`.'),
        (1, 420, '2', 'BeeGFS docs (architecture): at most one chunk file per file per target; created only on write, not preallocated; a one-byte write creates a one-byte chunk file.'),
        (2, 560, '3', 'BeeGFS docs (striping): `beegfs entry set --num-targets=4 --chunk-size=4MiB <dir>`; applies to new files only; use `entry migrate` or a copy to restripe.'),
        (3, 700, '4', 'BeeGFS docs: targets chosen randomly by default; capacity pools Normal / Low / Emergency with thresholds set on the management service (values not given).'),
        (4, 860, '5', f'My toy simulation (sim_stripe.py): {_SIM["K"]} targets, {_SIM["F"]} lognormal-size files, uniform random placement, {_SIM["trials"]} trials; 4 stripes gives {_SIM["res"]["4"]["mean"]:.2f}x. Real choosers use free-space labels; this shows the problem, not observed behaviour.'),
    ]
    chrome(c, A, 'Striping: chunks across targets', 4, notes)
    n = 6
    va = A.fade(0, 0.2, 0.9) * (1 - A.p(2, 0.0, 0.9, smooth))
    if va > 0:
        NCH = 12
        text(c, 'a file, cut into chunks (default 512 KiB)', 150, 240, 20, DIM, va, 'serif_i')
        osx = [250, 520, 790, 1060]
        for q in range(4):
            rect(c, osx[q] - 70, 500, 140, 270, stroke=VIOLET, a=va, sw=1.5, r=6)
            text(c, f'target {q+1}', osx[q], 805, 19, VIOLET, va, 'sans_m', align='c')
        for i in range(NCH):
            x1, y1 = 150 + i * 90, 280
            q = i % 4; slot = i // 4
            x2, y2 = osx[q] - 52, 515 + slot * 70
            f = A.p(0, 2.0 + i * 1.6, 1.0, ease_out)
            x = lerp(x1, x2, f); y = lerp(y1, y2, f)
            w = lerp(70, 104, f)
            rect(c, x, y, w, 52, fill=CH_COL[i % 9], a=va, fa=0.85 * va, r=4)
            text(c, str(i + 1), x + w / 2, y + 33, 20, BG, va, 'sans_b', align='c')
        text(c, 'pattern RAID0: plain striping, round-robin', 150, 870, 21, AMBER, va * A.fade(0, 22.0), 'serif_i')
        # chunk files
        b = A.fade(1, 0.5)
        if b > 0:
            for q in range(4):
                rect(c, osx[q] - 70, 500, 140, 270, fill=BG, a=b, fa=0.0)
            text(c, 'one chunk file per target, made on first write', 150, 900, 20, GREEN, va * b, 'serif_i')
    vb = vis(A, 1, n, 0.9, 0.9) * (1 - 0) if False else 0
    vc_ = A.fade(1, 3.0) * (1 - A.p(2, 0.0, 0.9, smooth))
    if vc_ > 0:
        # tiny write demo to the right
        rect(c, 1190, 330, 180, 130, stroke=DIM, a=vc_, sw=1.2, r=6)
        text(c, 'write 1 byte', 1280, 366, 17, INK, vc_, 'serif', align='c')
        rect(c, 1210, 392, 6, 26, fill=AMBER, a=vc_, fa=vc_, r=1)
        text(c, '→ a 1-byte chunk file', 1280, 442, 15, AMBER, vc_, 'serif_i', align='c')
    vb = vis(A, 2, n)
    if vb > 0:
        text(c, 'set per directory: how many targets, what chunk size', 150, 240, 22, INK, vb, 'serif')
        rect(c, 150, 290, 1150, 90, fill=(24, 28, 36), a=vb, fa=vb, stroke=RULE, r=8)
        mono(c, '$ beegfs entry set --num-targets=4 --chunk-size=4MiB /mnt/beegfs/data', 180, 345, 24, GREEN, vb)
        rows = [('new files', 'inherit the pattern', GREEN, 2.0), ('existing files', 'unchanged', AMBER, 5.0), ('to restripe', 'recreate (copy) or migrate', INK, 8.0)]
        for q, (k, d, col, dl) in enumerate(rows):
            a_ = vb * A.fade(2, dl)
            y = 480 + q * 90
            text(c, k, 190, y, 25, DIM, a_, 'serif_i')
            text(c, d, 520, y, 28, col, a_, 'serif')
    vc = vis(A, 3, n)
    if vc > 0:
        text(c, 'choosing targets', 150, 240, 22, INK, vc, 'serif')
        pools = [('Normal', GREEN, 0.35), ('Normal', GREEN, 0.5), ('Low', AMBER, 0.82), ('Emergency', RED, 0.95), ('Normal', GREEN, 0.42), ('Normal', GREEN, 0.6)]
        for q, (nm, col, fl) in enumerate(pools):
            a_ = vc * A.fade(3, 0.6 + q * 0.8)
            x = 200 + q * 190
            rect(c, x, 330, 120, 260, stroke=DIM, a=a_, sw=1.4, r=6)
            rect(c, x, 330 + 260 * (1 - fl), 120, 260 * fl, fill=col, a=a_, fa=0.45 * a_)
            text(c, nm, x + 60, 625, 19, col, a_, 'sans_m', align='c')
        b = A.fade(3, 6.0)
        text(c, 'new files: random choice, preferring Normal', 200, 710, 24, INK, vc * b, 'serif')
        text(c, 'labels come from free space; thresholds set on the management service', 200, 750, 19, DIM, vc * A.fade(3, 9.0), 'serif_i')
        rng = random.Random(5)
        picks = [0, 1, 4, 5, 0, 4]
        for q in range(4):
            tq = (A.t * 0.45 + q * 0.25) % 1.0
            pk = picks[(int(A.t * 0.45 + q * 0.25) + q) % 6]
            pkt(c, [(660, 650), (260 + pk * 190, 590)], tq, GREEN, vc * b * 0.9, 9)
    vd = vis(A, 4, n)
    if vd > 0:
        K = 100; sc = 4
        fill = _typical(sc)
        mean = sum(fill) / K
        px, py, pw, ph = 150, 300, 700, 260
        text(c, f'{sc} random targets per file: one typical trial', px, py - 24, 21, INK, vd, 'serif')
        line(c, px, py + ph, px + pw, py + ph, FAINT, vd)
        top = 4.0
        for i in range(K):
            hh = min(fill[i] / mean, top) / top * ph
            rect(c, px + i * pw / K, py + ph - hh, pw / K - 1, hh, fill=RED if fill[i] / mean > 2 else BLUE, a=vd, fa=0.8 * vd)
        line(c, px, py + ph - ph / top, px + pw, py + ph - ph / top, AMBER, vd * 0.8, 1, dash=[4, 4])
        text(c, 'average', px + pw - 2, py + ph - ph / top - 8, 14, AMBER, vd, 'serif_i', align='r')
        text(c, f'fullest ≈ {max(fill) / mean:.1f}× average  (mean over {_SIM["trials"]} trials: {_SIM["res"]["4"]["mean"]:.2f}×)', px, py + ph + 32, 19, RED, vd * A.fade(4, 5.0), 'serif_i')
        text(c, 'free-space labels (Normal / Low / Emergency) push back against this', px, py + ph + 74, 19, GREEN, vd * A.fade(4, 9.0), 'serif_i')
    ve = A.fade(5, 0.4)
    if ve > 0:
        text(c, 'keep a chunk within the client\'s RDMA buffers', 150, 260, 24, INK, ve, 'serif')
        scale = 760 / 600.0
        rect(c, 190, 340, 512 * scale * A.p(5, 1.0, 1.2, ease_out), 56, fill=BLUE, a=ve, fa=0.6 * ve, r=3)
        text(c, 'chunk: 512 KiB', 190 + 512 * scale + 14, 376, 22, BLUE, ve * A.fade(5, 1.5), 'serif')
        rect(c, 190, 440, 560 * scale * A.p(5, 4.0, 1.2, ease_out), 56, fill=VIOLET, a=ve, fa=0.6 * ve, r=3)
        text(c, '70 × 8 KiB RDMA buffers = 560 KiB', 190 + 560 * scale + 14, 476, 22, VIOLET, ve * A.fade(5, 4.5), 'serif')
        text(c, 'a few MB per chunk can cut message count', 190, 600, 23, GREEN, ve * A.fade(5, 8.0), 'serif_i')
        text(c, 'but then the buffers must grow too', 190, 640, 23, AMBER, ve * A.fade(5, 11.0), 'serif_i')

# ======================================================================= S5  metadata per directory
DIRCOL = [AMBER, BLUE, GREEN]
def s5(c, A):
    notes = [
        (0, 200, '1', 'BeeGFS docs: each metadata service owns an exclusive fraction of the namespace; a directory\'s contents live on one metadata node, chosen at random per directory. NetApp blog: a metadata server is selected when a directory is created.'),
        (2, 440, '2', 'My inference, not a documented statement: one directory lives on one metadata server, so a very large hot directory is served by that one server.'),
        (3, 620, '3', 'BeeGFS metadata tuning page: metadata stored as xattrs on a 0-byte file; `mkfs.ext4 -I 512`; `-I 1024` if striping over >4 targets by default or using ACLs.'),
        (4, 800, '4', 'System requirements page: ~0.3–0.5% of capacity; 500 GB of metadata for ~150 million files on tuned ext4; per file one metadata file; per directory two directories and two metadata files.'),
        (5, 960, '5', 'Metadata tuning page: ext4 "handles small file workloads... significantly faster"; XFS allocates inodes dynamically (system requirements page).'),
    ]
    chrome(c, A, 'Metadata: sharded by directory', 5, notes)
    n = 7
    v = vis(A, 0, n)
    if v > 0:
        text(c, 'each directory is assigned to a metadata server when it is created', 150, 240, 22, INK, v, 'serif')
        root = (460, 330)
        node(c, *root, 24, INK, v)
        text(c, '/', root[0], root[1] - 24, 18, INK, v, 'serif', align='c')
        kids = [(220, 470, 0, 'home'), (400, 470, 1, 'data'), (580, 470, 2, 'scratch'), (760, 470, 1, 'proj')]
        for q, (x, y, mc, nm) in enumerate(kids):
            a_ = v * A.fade(0, 3.0 + q * 2.0)
            line(c, root[0], root[1] + 12, x, y - 14, FAINT, a_, 1.4)
            node(c, x, y, 24, DIRCOL[mc], a_)
            text(c, nm, x, y + 42, 17, DIRCOL[mc], a_, 'serif_i', align='c')
            for k in range(3):
                xx = x - 36 + k * 36; yy = y + 130
                line(c, x, y + 12, xx, yy - 8, FAINT, a_ * 0.6, 1); rect(c, xx - 7, yy - 7, 14, 14, fill=DIRCOL[mc], a=a_, fa=0.5 * a_, r=2)
        for q, (nm, col) in enumerate([('metadata server 1', AMBER), ('metadata server 2', BLUE), ('metadata server 3', GREEN)]):
            chip(c, 1050, 420 + q * 60, nm, col, v * A.fade(0, 12.0), w=230, size=15)
        text(c, 'a directory\'s entries all live on its server', 1050, 640, 18, DIM, v * A.fade(0, 16.0), 'serif_i', align='c')
    v = vis(A, 1, n)
    if v > 0:
        text(c, 'a tree fans out across metadata servers from the start', 150, 300, 26, INK, v, 'serif')
        text(c, 'no extra feature to switch on', 150, 370, 28, GREEN, v * A.fade(1, 3.0), 'serif')
        text(c, '(Lustre: DNE, from version 2.4)', 150, 410, 20, DIM, v * A.fade(1, 4.5), 'serif_i')
        text(c, 'more metadata servers can be added later (docs)', 150, 490, 24, AMBER, v * A.fade(1, 7.0), 'serif')
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'inference: one busy directory = one busy server', 150, 240, 26, RED, v, 'serif')
        for q in range(3):
            col = DIRCOL[q]
            server(c, 200 + q * 260, 520, 120, 38, col, v * (1 if q == 1 else 0.6), lit=0.9 if q == 1 else 0.0)
            text(c, f'metadata {q+1}', 260 + q * 260, 510, 16, col, v, 'sans_m', align='c')
        rect(c, 400, 330, 340, 90, stroke=RED, a=v, sw=1.5, r=8)
        text(c, 'one enormous directory', 570, 385, 22, INK, v, 'serif', align='c')
        for i in range(20):
            ph = (A.t * 0.8 + i * 0.07) % 1
            pkt(c, [(150 + (i % 10) * 90, 300), (460 + 0 * i, 520)], ph, AMBER, v * 0.8, 6)
        text(c, 'remedy: spread files over many directories', 150, 700, 23, GREEN, v * A.fade(2, 6.0), 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'one user file = one 0-byte file, metadata in extended attributes', 150, 240, 22, INK, v, 'serif')
        rect(c, 200, 320, 520, 150, stroke=AMBER, a=v, sw=1.8, r=8)
        text(c, 'ext4 inode, 512 bytes', 460, 354, 19, DIM, v, 'serif_i', align='c')
        rect(c, 230, 380, 460, 62, fill=AMBER, a=v, fa=0.3 * v, stroke=AMBER, sw=1.2, r=4)
        text(c, 'xattrs: owner, permissions, stripe pattern, ...', 460, 419, 21, INK, v * A.fade(3, 3.0), 'serif', align='c')
        text(c, 'attributes inline → one read finds everything', 780, 405, 21, GREEN, v * A.fade(3, 6.0), 'serif_i')
        text(c, 'inode size', 200, 600, 22, DIM, v * A.fade(3, 9.0), 'serif_i')
        text(c, '512 B', 360, 600, 34, AMBER, v * A.fade(3, 9.0), 'sans_b')
        text(c, 'default advice', 480, 600, 19, DIM, v * A.fade(3, 9.0), 'serif_i')
        text(c, '1024 B', 360, 660, 34, VIOLET, v * A.fade(3, 12.5), 'sans_b')
        text(c, 'if > 4 targets per file by default, or ACLs', 480, 660, 19, DIM, v * A.fade(3, 12.5), 'serif_i')
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'what it costs', 150, 240, 22, INK, v, 'serif')
        rows = [('a file', '1 metadata file'), ('a directory', '2 directories + 2 metadata files'), ('metadata size', 'grows linearly with file count; no central database'), ('sizing', '≈ 0.3–0.5% of capacity'), ('rule of thumb', '500 GB ≈ 150 million files (tuned ext4)')]
        for q, (k, d) in enumerate(rows):
            a_ = v * A.fade(4, 1.0 + q * 3.2)
            text(c, k, 190, 330 + q * 70, 22, DIM, a_, 'serif_i')
            text(c, d, 470, 330 + q * 70, 25, INK if q < 3 else AMBER, a_, 'serif')
    v = vis(A, 5, n)
    if v > 0:
        for (x, ti, col, d1, d2) in [(380, 'ext4', AMBER, 'handles small-file workloads', 'significantly faster (docs)'), (940, 'XFS', VIOLET, 'inodes allocated dynamically', 'no fixed count at format time')]:
            a_ = v * A.fade(5, 1.0 + (x > 500) * 3.0)
            rect(c, x - 220, 320, 440, 220, stroke=col, a=a_, sw=1.6, r=10)
            text(c, ti, x, 390, 36, col, a_, 'title', align='c')
            text(c, d1, x, 450, 20, INK, a_, 'serif', align='c'); text(c, d2, x, 482, 19, DIM, a_, 'serif_i', align='c')
    v = A.fade(6, 0.4)
    if v > 0:
        rows = [('GPFS', BLUE, 'metanode per file + token managers'), ('Lustre', AMBER, 'metadata targets, sharded with DNE'), ('BeeGFS', GREEN, 'directories sharded from day one')]
        for q, (nm, col, d) in enumerate(rows):
            a_ = v * A.fade(6, 1.0 + q * 3.2)
            text(c, nm, 250, 380 + q * 110, 40, col, a_, 'title')
            text(c, d, 520, 380 + q * 110, 24, INK, a_, 'serif')

# ======================================================================= S6  consistency and caching
def s6(c, A):
    notes = [
        (0, 200, '1', 'I did not find a statement of locking or consistency semantics in the BeeGFS docs pages I read (architecture, striping, mirroring, client tuning, metadata caching). The vendor solution brief says "POSIX compatibility." Treat this as unverified.'),
        (1, 380, '2', 'BeeGFS docs, Client Metadata Caching: by default the client caches metadata only briefly, in milliseconds (tuneDirSubentryCacheValidityMS, tuneFileSubentryCacheValidityMS, tuneENOENTCacheValidityMS).'),
        (2, 560, '3', 'BeeGFS docs, Client Node Tuning: tuneRemoteFSync - true commits fsync() to server disks; false needs only the server cache. Also tuneFileCacheType and sysSyncOnClose (named in the caching page).'),
        (3, 740, '4', 'BeeGFS docs 8.4: sysRemoteInvalEnabled, default off; tuneInvalWatchMaxObjects default 50,000,000 (~6 GiB at 128 B per entry).'),
        (4, 900, '5', 'Same page: "Delayed coherence," a lost-invalidation race, little benefit for create-heavy workloads, and "applications that rely on mtime or file size as an instant synchronization signal should not rely on this cache."'),
    ]
    chrome(c, A, 'What does it promise? Caching and consistency', 6, notes)
    n = 6
    v = vis(A, 0, n)
    if v > 0:
        lanes = [(280, 'client A', BLUE), (700, 'the file', DIM), (1120, 'client B', GREEN)]
        for x, lab, col in lanes:
            rect(c, x - 90, 240, 180, 44, stroke=col, a=v, sw=1.6, r=6)
            text(c, lab, x, 270, 20, col, v, 'serif', align='c')
            line(c, x, 284, x, 760, FAINT, v, 1.2, dash=[5, 5])
        text(c, 'two clients, one file', 700, 215, 20, DIM, v, 'serif_i', align='c')
        rect(c, 480, 450, 440, 120, stroke=AMBER, a=v * A.fade(0, 6.0), sw=1.6, r=10)
        text(c, 'locking and consistency semantics', 700, 500, 23, AMBER, v * A.fade(0, 6.0), 'serif', align='c')
        text(c, 'not found in the docs I read', 700, 540, 21, RED, v * A.fade(0, 9.0), 'serif_i', align='c')
        text(c, 'what the docs do describe: caching', 700, 690, 22, INK, v * A.fade(0, 14.0), 'serif', align='c')
    v = vis(A, 1, n)
    if v > 0:
        lanes = [(280, 'client A', BLUE), (1120, 'client B', GREEN)]
        for x, lab, col in lanes:
            rect(c, x - 90, 240, 180, 44, stroke=col, a=v, sw=1.6, r=6)
            text(c, lab, x, 270, 20, col, v, 'serif', align='c')
            line(c, x, 284, x, 800, FAINT, v, 1.2, dash=[5, 5])
        f = A.p(1, 1.5, 0.9)
        if f > 0: arrow(c, 280, 350, lerp(280, 1100, f), 350, AMBER, v, 2.2); text(c, 'A changes the file', 690, 336, 18, AMBER, v * f, 'serif_i', align='c')
        f = A.p(1, 5.0, 0.9)
        if f > 0: arrow(c, 1120, 480, lerp(1120, 300, f), 480, GREEN, v, 2.2); text(c, 'B: stat (cached, a few ms old)', 700, 466, 18, GREEN, v * f, 'serif_i', align='c')
        text(c, 'B may see slightly old metadata', 700, 640, 26, RED, v * A.fade(1, 9.0), 'serif', align='c')
        text(c, 'cache validity is set in milliseconds by three timeouts', 700, 690, 20, DIM, v * A.fade(1, 11.5), 'serif_i', align='c')
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'data caching is a separate setting', 150, 240, 22, INK, v, 'serif')
        knobs = [('tuneFileCacheType', 'which file cache the client uses', BLUE), ('sysSyncOnClose', 'sync when a file is closed', GREEN), ('tuneRemoteFSync', 'fsync → server disks (true) or server cache (false)', AMBER)]
        for q, (k, d, col) in enumerate(knobs):
            a_ = v * A.fade(2, 1.5 + q * 4.0)
            mono(c, k, 190, 340 + q * 110, 26, col, a_)
            text(c, d, 190, 380 + q * 110, 20, DIM, a_, 'serif_i')
        text(c, 'off = fewer disk seeks, less safety', 190, 700, 23, RED, v * A.fade(2, 14.0), 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        text(c, 'BeeGFS 8.4, experimental: remote invalidation', 150, 240, 22, INK, v, 'serif')
        node(c, 250, 480, 28, BLUE, v); text(c, 'clients', 250, 530, 17, BLUE, v, 'serif_i', align='c')
        server(c, 760, 450, 150, 44, AMBER, v); text(c, 'metadata server', 835, 440, 17, AMBER, v, 'sans_m', align='c')
        f = A.p(3, 1.5, 1.0)
        if f > 0:
            arrow(c, 270, 470, lerp(270, 750, f), 470, BLUE, v, 2); text(c, 'reads an inode', 510, 455, 17, BLUE, v * f, 'serif_i', align='c')
        f = A.p(3, 3.5, 1.0)
        if f > 0: text(c, 'server remembers the client as a "watcher"', 835, 540, 18, AMBER, v * f, 'serif_i', align='c')
        f = A.p(3, 7.0, 1.0)
        if f > 0:
            arrow(c, 750, 490, lerp(750, 270, f), 490, RED, v, 2); text(c, 'inode changed: invalidate', 510, 520, 17, RED, v * f, 'serif_i', align='c')
        text(c, 'off by default  ·  up to 50,000,000 inodes tracked  ·  ≈ 6 GiB', 150, 700, 22, DIM, v * A.fade(3, 10.0), 'serif_i')
    v = vis(A, 4, n)
    if v > 0:
        text(c, 'the docs list the trade-offs themselves', 150, 240, 24, INK, v, 'serif')
        items = ['changes can still become visible late', 'a race can lose an invalidation: stale, then self-heals', 'create-heavy workloads see little benefit', 'do not use mtime or size as an instant sync signal']
        for q, s_ in enumerate(items):
            a_ = v * A.fade(4, 1.5 + q * 4.5)
            cross(c, 175, 340 + q * 80, 9, RED, a_, 2.2); text(c, s_, 210, 348 + q * 80, 24, INK, a_, 'serif')
    v = A.fade(5, 0.4)
    if v > 0:
        rect(c, 280, 330, 760, 230, stroke=AMBER, a=v, sw=1.6, r=10)
        text(c, 'if you depend on cross-node locking', 660, 400, 28, INK, v, 'serif', align='c')
        text(c, 'or instant visibility: test it yourself', 660, 445, 28, INK, v * A.fade(5, 1.5), 'serif', align='c')
        text(c, 'the documentation I read does not settle the question', 660, 505, 21, AMBER, v * A.fade(5, 3.5), 'serif_i', align='c')

# ======================================================================= S7  network
def s7(c, A):
    notes = [
        (0, 200, '1', 'BeeGFS docs, RDMA Support: built on the OpenFabrics ibverbs API; InfiniBand, RoCE and Omni-Path; some traffic (management) still uses TCP/IP.'),
        (2, 420, '2', 'RDMA Support page: max peers: metadata = clients + 2×(meta−1) + storage; storage = clients + meta; client = meta + storage (each × connMaxInternodeNum). The example numbers are mine.'),
        (3, 620, '3', 'RDMA Support page: connRDMABufNum 70, connRDMABufSize 8192; memory per connection = size × num × 2. My example assumes one connection per peer pair: 1,026 × 573,440 × 2 ≈ 1.18 GB.'),
        (4, 800, '4', 'RDMA Support page: client multi-rail since 7.3.0 via connRDMAInterfacesFile; one IPoIB device per line; NICs must not be in separate IPoIB subnets.'),
        (5, 940, '5', '`beegfs health net`: shows established connections and spots clients falling back to TCP.'),
    ]
    chrome(c, A, 'The wire: RDMA and TCP', 7, notes)
    n = 6
    v = vis(A, 0, n)
    if v > 0:
        layers = [('BeeGFS services and client', GREEN, 0), ('OpenFabrics verbs (ibverbs)', INK, 1)]
        for lab, col, q in layers:
            a_ = v * A.fade(0, 0.5 + q * 2.0)
            rect(c, 300, 260 + q * 110, 720, 80, stroke=col, a=a_, sw=1.6, r=8)
            text(c, lab, 660, 310 + q * 110, 26, col, a_, 'serif', align='c')
        fabs = [('InfiniBand', VIOLET), ('RoCE', VIOLET), ('Omni-Path', VIOLET)]
        for q, (nm, col) in enumerate(fabs):
            a_ = v * A.fade(0, 4.0 + q * 1.0)
            x = 300 + q * 250
            rect(c, x, 490, 220, 60, stroke=col, a=a_, sw=1.4, r=6); text(c, nm, x + 110, 528, 21, col, a_, 'serif', align='c')
            line(c, x + 110, 490, 660, 450, FAINT, a_, 1)
        rect(c, 300, 620, 720, 60, stroke=DIM, a=v * A.fade(0, 8.0), sw=1.4, r=6, dash=[5, 4])
        text(c, 'plain TCP otherwise · management traffic always TCP', 660, 658, 21, DIM, v * A.fade(0, 8.0), 'serif_i', align='c')
    v = vis(A, 1, n)
    if v > 0:
        pos = {'client': (300, 480), 'meta': (700, 330), 'meta2': (1000, 330), 'stor': (700, 640), 'stor2': (1000, 640)}
        for nm, (x, y) in pos.items():
            col = BLUE if nm == 'client' else (AMBER if nm.startswith('meta') else VIOLET)
            lab = {'client': 'clients', 'meta': 'metadata', 'meta2': 'metadata', 'stor': 'storage', 'stor2': 'storage'}[nm]
            rect(c, x - 70, y - 30, 140, 60, stroke=col, a=v, sw=1.6, r=8); text(c, lab, x, y + 7, 21, col, v, 'serif', align='c')
        edges = [('client', 'meta', 1.0), ('client', 'meta2', 1.0), ('client', 'stor', 2.5), ('client', 'stor2', 2.5), ('meta', 'meta2', 5.0), ('meta', 'stor', 7.0), ('meta2', 'stor2', 7.0), ('meta', 'stor2', 7.0), ('meta2', 'stor', 7.0)]
        for a_, b_, dl in edges:
            f = A.fade(1, dl)
            line(c, pos[a_][0] + 70, pos[a_][1], pos[b_][0] - 70 if pos[b_][0] > pos[a_][0] else pos[b_][0] + 70, pos[b_][1], GREEN, v * f * 0.8, 1.8)
        f = A.fade(1, 10.0)
        line(c, 770, 640, 930, 640, RED, v * f, 2); cross(c, 850, 640, 12, RED, v * f)
        text(c, 'storage ↔ storage: none', 850, 700, 19, RED, v * f, 'serif_i', align='c')
    v = vis(A, 2, n)
    if v > 0:
        text(c, 'peers per node (documented formula)', 150, 240, 22, INK, v, 'serif')
        rows = [('metadata server', 'clients + 2 × (metadata − 1) + storage', '1,000 + 2×3 + 20 = 1,026', AMBER), ('storage server', 'clients + metadata', '1,000 + 4 = 1,004', VIOLET), ('client', 'metadata + storage', '4 + 20 = 24', BLUE)]
        for q, (k, f_, ex, col) in enumerate(rows):
            a_ = v * A.fade(2, 1.5 + q * 5.0)
            y = 340 + q * 130
            text(c, k, 190, y, 26, col, a_, 'serif'); text(c, f_, 190, y + 36, 20, DIM, a_, 'serif_i')
            text(c, ex, 900, y + 8, 30, INK, a_ * A.fade(2, 3.5 + q * 5.0), 'sans_b')
        text(c, 'example: 1,000 clients, 4 metadata servers, 20 storage servers (mine)', 150, 760, 20, FAINT, v, 'serif_i')
    v = vis(A, 3, n)
    if v > 0:
        scale = 760 / 600.0
        text(c, 'buffers per connection', 150, 240, 22, INK, v, 'serif')
        for q in range(70):
            a_ = v * A.fade(3, 1.0 + q * 0.04, 0.3)
            rect(c, 190 + (q % 35) * 22, 300 + (q // 35) * 40, 18, 32, fill=VIOLET, a=a_, fa=0.55 * a_, r=2)
        text(c, '70 buffers × 8 KiB = 560 KiB  (≥ one 512 KiB chunk)', 190, 430, 22, VIOLET, v * A.fade(3, 5.0), 'serif')
        text(c, 'memory per connection = size × number × 2 (send + receive)', 190, 500, 21, DIM, v * A.fade(3, 8.0), 'serif_i')
        text(c, 'my example, 1 connection per peer: ≈ 1.2 GB on each metadata server', 190, 590, 25, AMBER, v * A.fade(3, 12.0), 'serif')
        text(c, 'RDMA memory cannot be swapped out', 190, 640, 21, RED, v * A.fade(3, 15.0), 'serif_i')
    v = vis(A, 4, n)
    if v > 0:
        node(c, 300, 480, 30, BLUE, v)
        text(c, 'client with 2 IPoIB interfaces', 300, 540, 18, BLUE, v, 'serif_i', align='c')
        for k, y in enumerate((400, 560)):
            a_ = v * A.fade(4, 1.5 + k * 1.5)
            line(c, 330, 480, 800, y, BLUE, a_, 3); rect(c, 800, y - 35, 160, 70, stroke=VIOLET, a=a_, sw=1.5, r=8)
            text(c, 'every service', 880, y + 7, 19, VIOLET, a_, 'serif', align='c')
        text(c, 'balanced by connection count (since 7.3.0)', 300, 720, 22, GREEN, v * A.fade(4, 5.0), 'serif_i')
        text(c, 'every interface must reach every service; no separate subnets', 300, 765, 20, AMBER, v * A.fade(4, 9.0), 'serif_i')
    v = A.fade(5, 0.4)
    if v > 0:
        rect(c, 150, 280, 1000, 100, fill=(24, 28, 36), a=v, fa=v, stroke=RULE, r=8)
        mono(c, '$ beegfs health net', 180, 342, 28, GREEN, v)
        text(c, 'lists established connections: RDMA, or fallen back to TCP?', 150, 450, 26, INK, v * A.fade(5, 2.0), 'serif')
        text(c, 'a misconfigured client can quietly use TCP', 150, 510, 24, RED, v * A.fade(5, 5.0), 'serif_i')
