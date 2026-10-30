import numpy as np
def run(N=60, W=10, D=6000, seed=1, k=8):
    """Toy rebuild-load model. N disks, each holds D strips; tracks have W strips (k data + W-k parity).
    Conventional: N/W groups of W disks, one dedicated spare disk. Declustered: tracks placed on random W-disk subsets,
    spare capacity (one disk's worth) spread over all disks. Fail one disk; rebuild every lost strip by reading k
    surviving strips of its track and writing one strip to a spare slot. Returns per-disk I/O (reads+writes) in strips."""
    rng = np.random.default_rng(seed)
    # Conventional group (W disks + dedicated spare): D lost strips, each needs k survivor reads (of W-1 survivors)
    conv = np.zeros(W)          # survivors in group (W-1) + spare
    for _ in range(D):
        surv = rng.choice(W-1, size=k, replace=False)
        conv[surv] += 1
    conv_spare = D              # all D rebuilt strips written to the one spare disk
    conv_max = max(conv[:W-1].max(), conv_spare)
    # Declustered
    n_tracks = N*D//W
    load = np.zeros(N)
    failed = 0
    lost = 0
    tracks_with_failed = []
    # Sample placement efficiently: probability a track contains disk 0 is W/N
    n_lost = rng.binomial(n_tracks, W/N)
    for _ in range(n_lost):
        others = rng.choice(np.arange(1, N), size=W-1, replace=False)      # other strips' disks
        reads = rng.choice(others, size=k, replace=False)                     # read k survivors
        load[reads] += 1
        # write rebuilt strip to spare space on a disk not already holding a strip of this track
        cand = np.setdiff1d(np.arange(1, N), others)
        load[rng.choice(cand)] += 1
    dec_max = load[1:].max()
    return dict(N=N, W=W, D=D, lost_strips_conv=D, lost_strips_dec=int(n_lost), conv_max=float(conv_max), dec_max=float(dec_max),
                ratio=float(conv_max/dec_max), dec_mean=float(load[1:].mean()), conv_survivor_mean=float(conv[:W-1].mean()),
                dec_load=load[1:].tolist(), conv_load=list(conv[:W-1])+[conv_spare])
if __name__ == "__main__":
    for N in (30, 60, 120):
        r = run(N=N)
        print(N, {k: (round(v,3) if isinstance(v,float) else v) for k,v in r.items() if k not in ('dec_load','conv_load')})
    import json; json.dump(run(N=60), open('sim_n60.json','w'))
