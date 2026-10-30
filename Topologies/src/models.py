#!/usr/bin/env python3
"""Run every model experiment and write data/results.json.
All on-screen numbers in the video come from this file or from a cited source.
Usage:  python3 models.py            (runs selftest first, then experiments)
"""
import json, math, os, random, statistics, subprocess, sys, time
import topo_graphs as G
import topo_flows as F

from paths import DATA
OUT = DATA / "results.json"


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * (len(xs) - 1) + 0.5))]


# ----------------------------------------------------------------------------
def exp_fat_tree():
    out = {}
    out["sizes"] = {
        "k64_2level": G.fat_tree_formulas(64, 2),
        "k64_3level": G.fat_tree_formulas(64, 3),
        "k32_3level": G.fat_tree_formulas(32, 3),
    }
    out["oversub_table_r64"] = G.oversub_table(64, [(32, 32), (48, 16), (56, 8)])
    # uniform all-to-all on a small leaf-spine, simulated vs closed form
    chk = []
    for d, u, L in [(8, 8, 8), (8, 4, 8), (8, 2, 8), (12, 4, 6)]:
        ls = F.LeafSpine(d, u, L)
        pairs = [(s, t) for s in range(ls.H) for t in range(ls.H) if s != t]
        N = ls.H
        # lam = per-pair rate; a host injects (N-1)*lam in total
        sim = (N - 1) * ls.uniform_lambda_explicit(pairs)
        f_off = (N - d) / (N - 1)
        closed = min(1.0, (u / d) / f_off)
        chk.append(dict(d=d, u=u, leaves=L, sim_per_host=sim, closed_form=closed))
        assert abs(sim - closed) < 1e-6, (sim, closed)
    out["uniform_alltoall_check"] = chk
    return out


def exp_permutations(trials=200):
    out = {}
    res = F.permutation_experiment(16, 16, 16, trials, seed=11)
    out["leafspine_16x16_1to1"] = {
        k: dict(mean=statistics.mean(v), p5=pct(v, .05), p95=pct(v, .95)) for k, v in res.items() if v}
    out["trials"] = trials
    # hash-collision demo permutation (small, for the animation): 4 leaves x 4 hosts
    rng = random.Random(3)
    ls = F.LeafSpine(4, 4, 4)
    perm = list(range(ls.H)); rng.shuffle(perm)
    pairs = [(s, t) for s, t in enumerate(perm) if s != t]
    r_e, sp_e = ls.rates(pairs, "ecmp", random.Random(9))
    r_p, sp_p = ls.rates(pairs, "perfect")
    out["demo"] = dict(pairs=pairs, ecmp_spine=sp_e, ecmp_rate=r_e, perfect_spine=sp_p,
                       perfect_rate=r_p, d=4, u=4, leaves=4)
    return out


def exp_clos():
    return F.clos_theory_checks()


def exp_cubes():
    out = {}
    rows = []
    for name, dims, wrap in [("2D torus 8x8", (8, 8), True), ("2D torus 16x16", (16, 16), True),
                              ("3D torus 8x8x8", (8, 8, 8), True), ("3D torus 16x16x16", (16, 16, 16), True),
                              ("3D torus 16x16x32", (16, 16, 32), True),
                              ("3D mesh 16x16x16", (16, 16, 16), False)]:
        N = math.prod(dims)
        diam = G.torus_diameter_formula(dims) if wrap else G.mesh_diameter_formula(dims)
        bis = G.torus_bisection_links_formula(dims) if wrap else G.mesh_bisection_links_formula(dims)
        rows.append(dict(name=name, N=N, degree=2 * len(dims), diameter=diam, bisection_links=bis,
                         beta=bis / (N / 2)))
    out["rows"] = rows
    # BFS cross-check of the two 8x8-ish rows
    adj, _ = G.torus_nd((8, 8, 8))
    assert G.eccentricity(adj, 0) == 12
    # Blue Gene/L: 64 x 32 x 32 torus, 1.4 Gb/s per direction per link (paper)
    bgl_links = G.torus_bisection_links_formula((64, 32, 32))
    out["bluegene_l"] = dict(nodes=64 * 32 * 32, bisection_links=bgl_links,
                             gbytes_per_s_per_direction=bgl_links * 1.4 / 8,
                             paper_says_GBps=360)
    # K computer: 24x18x16 x (2x3x2)
    out["k_computer"] = dict(nodes=24 * 18 * 16 * 2 * 3 * 2, virtual_torus=(54, 48, 32),
                             virtual_nodes=54 * 48 * 32)
    # TPU v4: 64 cubes of 4x4x4
    out["tpu_v4"] = dict(chips=64 * 4 * 4 * 4, optical_links_per_cube=6 * 16,
                         ocs_pairs=6 * 16 // 2, torus_16=G.torus_bisection_links_formula((16, 16, 16)))
    # scaling of relative bisection with N
    Ns = [2 ** e for e in range(6, 21)]
    curves = {"2D torus": [], "3D torus": [], "5D torus": [], "fat tree 1:1": [], "fat tree 3:1": [],
              "hypercube": [], "HyperX / flattened butterfly (L=2)": [], "dragonfly (balanced)": []}
    for N in Ns:
        curves["2D torus"].append(4 / N ** (1 / 2))
        curves["3D torus"].append(4 / N ** (1 / 3))
        curves["5D torus"].append(4 / N ** (1 / 5))
        curves["fat tree 1:1"].append(1.0)
        curves["fat tree 3:1"].append(1 / 3)
        curves["hypercube"].append(1.0)
        curves["HyperX / flattened butterfly (L=2)"].append(0.5)
        curves["dragonfly (balanced)"].append(0.5)
    out["beta_curves"] = dict(N=Ns, curves=curves)
    # dragonfly beta from the group-split cut at concrete sizes (upper bound on min bisection)
    dfb = []
    for a, p, h in [(4, 2, 2), (8, 4, 4), (16, 8, 8), (32, 16, 17)]:
        g = a * h + 1
        N = a * p * g
        cut = (g // 2) * (g - g // 2)
        dfb.append(dict(a=a, p=p, h=h, g=g, N=N, cut_links=cut, beta_group_cut=cut / (N / 2)))
    out["dragonfly_group_cut"] = dfb
    return out


def dor_loads(k, wrap):
    from collections import defaultdict
    load = defaultdict(float)
    def walk(x1, x2):
        """list of (from,to,weight) steps along one dimension, ties split."""
        if x1 == x2:
            return []
        if not wrap:
            step = 1 if x2 > x1 else -1
            return [[(x1 + i * step, x1 + (i + 1) * step, 1.0) for i in range(abs(x2 - x1))]]
        diff = (x2 - x1) % k
        if 2 * diff < k:
            return [[((x1 + i) % k, (x1 + i + 1) % k, 1.0) for i in range(diff)]]
        if 2 * diff > k:
            return [[((x1 - i) % k, (x1 - i - 1) % k, 1.0) for i in range(k - diff)]]
        plus = [((x1 + i) % k, (x1 + i + 1) % k, 0.5) for i in range(diff)]
        minus = [((x1 - i) % k, (x1 - i - 1) % k, 0.5) for i in range(k - diff)]
        return [plus, minus]
    total_hops = 0.0
    for x1 in range(k):
        for y1 in range(k):
            for x2 in range(k):
                for y2 in range(k):
                    if (x1, y1) == (x2, y2):
                        continue
                    for px in (walk(x1, x2) or [[]]):
                        wx = px[0][2] if px else 1.0
                        for py in (walk(y1, y2) or [[]]):
                            wy = py[0][2] if py else 1.0
                            w = wx * wy
                            for a, b, _ in px:
                                load[((a, y1), (b, y1))] += w
                                total_hops += w
                            for a, b, _ in py:
                                load[((x2, a), (x2, b))] += w
                                total_hops += w
    return load, total_hops


def exp_alltoall_loads(k=8):
    out = {}
    for name, wrap in (("torus", True), ("mesh", False)):
        load, total = dor_loads(k, wrap)
        N = k * k
        nlinks = 4 * N if wrap else 2 * 2 * k * (k - 1)
        # identity check: sum of loads == total path length over all ordered pairs
        assert abs(sum(load.values()) - total) < 1e-6
        mx = max(load.values())
        avg = sum(load.values()) / nlinks
        out[name] = dict(k=k, directed_links=nlinks, max_load=mx, mean_load=avg, max_over_mean=mx / avg,
                         load={f"{a[0]},{a[1]}>{b[0]},{b[1]}": v for (a, b), v in load.items()})
        # `load` is in units of "one flow of rate 1 per ordered pair".  With uniform destinations a
        # node injecting `x` in total sends x/(N-1) to each destination, so the hottest unit-capacity
        # link saturates at x = (N-1)/max_load.
        out[name]["saturation_injection"] = (N - 1) / mx
    return out


def exp_hyperx():
    out = {}
    rows = []
    for L, S, K, T in [(2, 16, 1, 32), (2, 16, 1, 16), (2, 16, 1, 8), (3, 8, 1, 16), (3, 8, 1, 8)]:
        f = G.hyperx_formulas(L, S, K, T)
        rows.append(dict(L=L, S=S, K=K, T=T, **f))
    out["rows"] = rows
    adj, _ = G.hyperx(2, 16)
    out["diameter_L2_S16"] = G.eccentricity(adj, 0)
    # paper: hypercube is HyperX(S=2); full mesh is L=1
    return out


def exp_dragonfly():
    out = {}
    out["slingshot_max"] = dict(G.dragonfly_formulas(32, 16, 17))
    assert out["slingshot_max"]["N"] == 279040 and out["slingshot_max"]["g"] == 545 and out["slingshot_max"]["radix"] == 64
    rows = []
    for a, p, h in [(4, 2, 2), (6, 3, 3)]:
        dm = F.DragonflyModel(a, p, h)
        wc = dm.pattern_worst_case()
        un = dm.pattern_uniform()
        r = dict(a=a, p=p, h=h, g=dm.g, N=dm.info["terminals"], radix=dm.info["radix"])
        # wc: one flow per terminal -> throughput is already a fraction of injection rate.
        r["wc_min"], _ = dm.throughput(wc, "min")
        r["wc_val"], _ = dm.throughput(wc, "val")
        # uniform: N-1 flows per terminal -> scale per-pair rate by (N-1) to get per-node injection.
        N = r["N"]
        r["uni_min"] = (N - 1) * dm.throughput(un, "min")[0]
        r["uni_val"] = (N - 1) * dm.throughput(un, "val")[0]
        rows.append(r)
    out["sims"] = rows
    # concrete layout of the a=4,p=2,h=2 example for drawing
    dm = F.DragonflyModel(4, 2, 2)
    out["draw"] = dict(g=dm.g, a=4, p=2, h=2,
                       glinks=[[int(i), int(k), int(ri), int(rk)]
                               for (i, k), (ri, rk) in dm.glink.items() if i < k])
    return out


def exp_compare():
    """Per-endpoint scorecard for concrete designs near 8K-16K endpoints.
    Diameter = router-to-router hops (BFS).  beta = bisection / (N/2)."""
    rows = []
    # fat tree k=32, 3 levels
    adj, info = G.fat_tree_k(32)
    H = info["hosts"]
    edges = G.n_links(adj) - H                       # inter-switch links
    dist = G.bfs_dist(adj, H)                        # from one edge switch (all edge switches are equivalent)
    ecc = max(dist[H:])                              # switch-to-switch hops only (hosts excluded)
    rows.append(dict(name="fat tree (3 levels, 32-port, 1:1)", N=H, routers=info["switches"], radix=32,
                     cables_per_endpoint=edges / H, diameter=ecc, beta=1.0,
                     note="beta=1 by construction (k/2 up per k/2 down)"))
    # fat tree 3:1 oversubscribed (2-level 64-port, 48 down 16 up)
    rows.append(dict(name="fat tree (2 levels, 64-port, 3:1)", N=64 * 48, routers=64 + 16, radix=64,
                     cables_per_endpoint=(64 * 16) / (64 * 48), diameter=2, beta=1 / 3,
                     note="beta = uplinks/downlinks"))
    # 3D torus 16x16x32
    dims = (16, 16, 32)
    N = math.prod(dims)
    adjt, _ = G.torus_nd(dims)
    rows.append(dict(name="3D torus 16x16x32", N=N, routers=N, radix=6 + 1,
                     cables_per_endpoint=G.n_links(adjt) / N, diameter=G.eccentricity(adjt, 0),
                     beta=G.torus_bisection_links_formula(dims) / (N / 2), note="router per node"))
    # hypercube 2^13
    adjh = G.hypercube(13)
    rows.append(dict(name="hypercube (13 dimensions)", N=2 ** 13, routers=2 ** 13, radix=13 + 1,
                     cables_per_endpoint=G.n_links(adjh) / 2 ** 13, diameter=G.eccentricity(adjh, 0),
                     beta=1.0, note="router per node"))
    # HyperX L=2 S=16 T=32
    adjx, _ = G.hyperx(2, 16)
    hf = G.hyperx_formulas(2, 16, 1, 32)
    rows.append(dict(name="HyperX 16x16, 32 nodes/switch", N=hf["terminals"], routers=hf["switches"], radix=hf["radix"],
                     cables_per_endpoint=G.n_links(adjx) / hf["terminals"], diameter=G.eccentricity(adjx, 0),
                     beta=hf["beta"], note="paper formula beta = K*S/(2T)"))
    # dragonfly a=16 p=8 h=8
    adjd, glink, info = G.dragonfly(16, 8, 8)
    g = info["g"]
    cut = (g // 2) * (g - g // 2)
    rows.append(dict(name="dragonfly a=16, p=8, h=8", N=info["terminals"], routers=info["routers"], radix=info["radix"],
                     cables_per_endpoint=G.n_links(adjd) / info["terminals"], diameter=G.diameter_exact(adjd),
                     beta=cut / (info["terminals"] / 2), note="group-split cut (upper bound)"))
    return dict(rows=rows)


def exp_collectives():
    alpha, bw = 2e-6, 50e9            # illustrative: 2 us per message, 400 Gb/s = 50 GB/s
    beta = 1 / bw
    out = dict(alpha=alpha, beta=beta, link_GBps=50)
    sizes = [2 ** e for e in range(6, 31)]        # 64 B .. 1 GiB
    for p in (64, 1024, 16384):
        out[f"p{p}"] = dict(
            n=sizes,
            ring=[F.t_ring_allreduce(p, n, alpha, beta) for n in sizes],
            rabenseifner=[F.t_rabenseifner_allreduce(p, n, alpha, beta) for n in sizes],
            recdbl=[F.t_recdbl_allreduce(p, n, alpha, beta) for n in sizes],
            tree=[F.t_tree_allreduce(p, n, alpha, beta) for n in sizes],
        )
    # message size at which recursive doubling (full vector) loses to Rabenseifner, p=1024
    p = 1024
    cross = None
    for n in sizes:
        if F.t_recdbl_allreduce(p, n, alpha, beta) > F.t_rabenseifner_allreduce(p, n, alpha, beta):
            cross = n; break
    out["recdbl_vs_rabenseifner_crossover_bytes_p1024"] = cross
    # latency-only comparison (n -> 0): ring grows linearly in p
    out["latency_only"] = {str(p): dict(ring=2 * (p - 1) * alpha, rabenseifner=2 * math.log2(p) * alpha)
                           for p in (64, 1024, 16384)}
    return out


def exp_placement():
    res = {}
    for name, (d, u, L) in {"1to1": (32, 32, 16), "2to1": (32, 16, 16),
                            "4to1": (32, 8, 16), "8to1": (32, 4, 16)}.items():
        res[name] = F.placement_experiments(d, u, L)
    return res


def main():
    t0 = time.time()
    subprocess.check_call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "selftest.py")],
                          stdout=subprocess.DEVNULL)
    print("self-tests passed")
    R = {}
    for name, fn in [("fat_tree", exp_fat_tree), ("permutations", exp_permutations), ("clos", exp_clos),
                     ("cubes", exp_cubes), ("alltoall_loads", exp_alltoall_loads), ("hyperx", exp_hyperx),
                     ("dragonfly", exp_dragonfly), ("compare", exp_compare), ("collectives", exp_collectives),
                     ("placement", exp_placement)]:
        t1 = time.time()
        R[name] = fn()
        print(f"{name:16s} {time.time()-t1:6.1f}s")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(R, f)
    print("wrote", os.path.normpath(OUT), f"({time.time()-t0:.0f}s total)")


if __name__ == "__main__":
    main()
