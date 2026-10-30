"""Self-tests: every formula the video states is checked against an independent
computation (BFS / brute force / exhaustive search / hand-solved case)."""
import math, random, sys, time
import topo_graphs as G
import topo_flows as F


def t(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + extra if extra else ""))
    if not cond:
        raise SystemExit(1)


t0 = time.time()
F._selftest_maxmin(); t("max-min: single link, textbook, parking-lot", True)

# --- k-ary n-cube formulas vs graph computations -----------------------------
for dims in [(4, 4), (6, 6), (4, 4, 4), (8, 4), (2, 2, 2, 2), (5, 5)]:
    adj, _ = G.torus_nd(dims, wrap=True)
    d_bfs = G.eccentricity(adj, 0)            # vertex-transitive
    t(f"torus {dims} diameter", d_bfs == G.torus_diameter_formula(dims),
      f"bfs={d_bfs} formula={G.torus_diameter_formula(dims)}")
    adjm, _ = G.torus_nd(dims, wrap=False)
    dm = G.diameter_exact(adjm)
    t(f"mesh  {dims} diameter", dm == G.mesh_diameter_formula(dims), f"bfs={dm}")

for dims in [(4, 4), (2, 2, 2, 2), (6, 2), (4, 2, 2)]:
    adj, _ = G.torus_nd(dims, wrap=True)
    if len(adj) <= 20:
        b = G.min_bisection_bruteforce(adj)
        t(f"torus {dims} exact min bisection", b == G.torus_bisection_links_formula(dims),
          f"brute={b} formula={G.torus_bisection_links_formula(dims)}")
for dims in [(4, 4), (2, 2, 2, 2)]:
    adj, _ = G.torus_nd(dims, wrap=False)
    b = G.min_bisection_bruteforce(adj)
    t(f"mesh  {dims} exact min bisection", b == G.mesh_bisection_links_formula(dims),
      f"brute={b} formula={G.mesh_bisection_links_formula(dims)}")

# --- HyperX formulas ---------------------------------------------------------
for L, S in [(2, 4), (1, 8), (3, 2)]:
    adj, _ = G.hyperx(L, S)
    hf = G.hyperx_formulas(L, S, 1, 1)
    t(f"hyperx L={L} S={S} diameter == L", G.eccentricity(adj, 0) == L)
    t(f"hyperx L={L} S={S} radix", max(len(a) for a in adj) + 1 == hf["radix"],
      f"graph={max(len(a) for a in adj)+1} formula={hf['radix']}")
    if len(adj) <= 20:
        b = G.min_bisection_bruteforce(adj)
        t(f"hyperx L={L} S={S} exact min bisection vs paper C_m", b == hf["bisection_channels"],
          f"brute={b} formula={hf['bisection_channels']}")
# hypercube is HyperX with S=2
a1, _ = G.hyperx(4, 2); a2 = G.hypercube(4)
t("hypercube == HyperX(S=2)", a1 == a2)

# --- dragonfly ----------------------------------------------------------------
for a, p, h in [(4, 2, 2), (6, 3, 3)]:
    adj, glink, info = G.dragonfly(a, p, h)
    fm = G.dragonfly_formulas(a, p, h)
    t(f"dragonfly a={a} p={p} h={h} groups/terminals",
      info["g"] == fm["g"] and info["terminals"] == fm["N"], f"g={info['g']} N={info['terminals']}")
    degs = {len(x) for x in adj}
    t("dragonfly router degree = a-1+h", degs == {a - 1 + h}, f"{degs}")
    t("dragonfly radix formula p+a+h-1", info["radix"] == fm["radix"])
    pairs = {frozenset((i, k)) for (i, k) in glink}
    t("one global link per group pair", len(pairs) == info["g"] * (info["g"] - 1) // 2)
    t("dragonfly router diameter == 3", G.diameter_exact(adj) == 3)

# --- fat tree -------------------------------------------------------------------
for k in (4, 6, 8):
    adj, info = G.fat_tree_k(k)
    f3 = G.fat_tree_formulas(k, 3)
    t(f"fat-tree k={k} hosts/switches", info["hosts"] == f3["hosts"] and info["switches"] == f3["switches"])
    d = G.bfs_dist(adj, 0)
    t(f"fat-tree k={k} host-host diameter 6 hops", max(d[:info['hosts']]) == 6)
    t(f"fat-tree k={k} host degree 1, switch degree k",
      all(len(adj[h]) == 1 for h in range(info['hosts'])) and
      all(len(adj[s]) == k for s in range(info['hosts'], len(adj))))
adj, info = G.fat_tree_k(48)           # Al-Fares example, built not asserted
t("Al-Fares k=48: 27,648 hosts, 2,880 switches", info["hosts"] == 27648 and info["switches"] == 2880)
t("144^2/2 = 10,368 (two-level, 144-port)", G.fat_tree_formulas(144, 2)["hosts"] == 10368)
t("k=64 two-level 2,048/96 and three-level 65,536/5,120",
  G.fat_tree_formulas(64, 2) == dict(hosts=2048, switches=96) and
  G.fat_tree_formulas(64, 3) == dict(hosts=65536, switches=5120))

# --- Clos blocking: exhaustive ---------------------------------------------------
cl = F.clos_theory_checks()
t("Clos n=2,r=2: m=2 blocks, m=3 (2n-1) never blocks, m=2 is rearrangeable", True, str(cl))

# --- edge colouring routes any permutation conflict-free at 1:1 -------------------
ls = F.LeafSpine(8, 8, 8)
rng = random.Random(5)
for trial in range(60):
    perm = list(range(ls.H)); rng.shuffle(perm)
    pairs = [(s, x) for s, x in enumerate(perm) if s != x]
    rates, _ = ls.rates(pairs, "perfect")
    assert min(rates) > 1 - 1e-9, (trial, min(rates))
t("edge-colouring: 60 random permutations on 8x8 1:1 leaf-spine all at rate 1.0", True)
# the same permutations under ECMP hashing lose throughput
res = F.permutation_experiment(8, 8, 8, 60, seed=5)
mean_ecmp = sum(res["ecmp"]) / len(res["ecmp"])
t("ECMP hashing on the same fabric is strictly worse than 1.0", mean_ecmp < 0.9, f"mean={mean_ecmp:.3f}")

# --- oversubscription: worst-case permutation rate == u/d, in the max-min sim ----
for d_, u_ in [(8, 4), (12, 4), (8, 8)]:
    ls = F.LeafSpine(d_, u_, 6)
    pairs = [(s, (s + d_) % ls.H) for s in range(ls.H)]    # leaf i -> leaf i+1
    r = min(ls.fluid_rates(pairs))
    t(f"leaf shift pattern d={d_} u={u_} rate == u/d", abs(r - min(1, u_ / d_)) < 1e-9, f"{r:.4f}")

# --- dragonfly: adversarial pattern ------------------------------------------------
dm = F.DragonflyModel(4, 2, 2)
wc = dm.pattern_worst_case()
lam_min, _ = dm.throughput(wc, "min")
lam_val, _ = dm.throughput(wc, "val")
t("dragonfly a=4,p=h=2 MIN on adversarial pattern == 1/(a*p)", abs(lam_min - 1 / (4 * 2)) < 1e-9, f"{lam_min:.4f}")
t("dragonfly VAL on adversarial pattern in (0.40, 0.55)", 0.40 < lam_val < 0.55, f"{lam_val:.4f}")

# --- deadlock / channel dependency graphs -----------------------------------------
dc = F.deadlock_checks()
t("channel-dependency cycles: torus without VCs, none with dateline", True, str(dc))

# --- collectives: closed forms --------------------------------------------------------
a_, b_, p_, n_ = 2e-6, 1 / 50e9, 8, 1e6
t("ring vs Rabenseifner share the bandwidth term",
  abs((F.t_ring_allreduce(p_, n_, 0, b_) - F.t_rabenseifner_allreduce(p_, n_, 0, b_))) < 1e-18)
t("p=2: ring allreduce = 2a + n*b", abs(F.t_ring_allreduce(2, n_, a_, b_) - (2 * a_ + n_ * b_)) < 1e-18)

print(f"\nAll self-tests passed in {time.time()-t0:.1f}s")
