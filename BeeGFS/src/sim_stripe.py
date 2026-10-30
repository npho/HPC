"""Toy model: how evenly do randomly placed files fill OSTs, as a function of stripe count?
K OSTs, F files with heavy-tailed (lognormal) sizes, each file's stripes go on `sc` distinct uniformly random OSTs,
size split evenly across its stripes. Metric: fullest OST / mean OST fill, averaged over trials.
NOT how the real MDS allocator works (it steers toward emptier OSTs); this shows the problem it solves."""
import numpy as np, json
from paths import DATA
rng = np.random.default_rng(7)
K, F, TR = 100, 3000, 300
out = {}
for sc in (1, 2, 4, 8, 16):
    r = []
    for _ in range(TR):
        sizes = rng.lognormal(0, 1.5, F)
        fill = np.zeros(K)
        for s in sizes:
            idx = rng.choice(K, sc, replace=False)
            fill[idx] += s / sc
        r.append(fill.max() / fill.mean())
    out[sc] = dict(mean=float(np.mean(r)), sd=float(np.std(r)))
    print(sc, out[sc])
json.dump(dict(K=K, F=F, trials=TR, sigma=1.5, res=out), open(DATA / 'sim_stripe.json', 'w'), indent=1)
