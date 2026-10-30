"""Flow-level models: max-min fair sharing, Clos blocking checks, routing on
leaf-spine and dragonfly, deadlock (channel dependency) analysis, collectives.

All of this is a *model*. Numbers it produces are labelled as modeled in the
video and in the notes; none of them is a measurement of real hardware.
"""
from __future__ import annotations
import itertools
import math
import random
from collections import defaultdict


# ----------------------------------------------------------------------------
# max-min fair rates by progressive filling
# ----------------------------------------------------------------------------
def maxmin(flow_links, cap):
    """flow_links: list of lists of link ids.  cap: dict link -> capacity.
    Returns list of rates.  Classic water-filling."""
    n = len(flow_links)
    rate = [0.0] * n
    frozen = [False] * n
    remaining = dict(cap)
    users = defaultdict(list)
    for i, links in enumerate(flow_links):
        for l in set(links):
            users[l].append(i)
    active = {l: len(v) for l, v in users.items()}
    n_frozen = 0
    while n_frozen < n:
        # tightest link: smallest fair share among links that still have active flows
        best_l, best_share = None, float("inf")
        for l, c in active.items():
            if c > 0:
                share = remaining[l] / c
                if share < best_share - 1e-15:
                    best_share, best_l = share, l
        if best_l is None:
            break
        for i in users[best_l]:
            if not frozen[i]:
                rate[i] = best_share
                frozen[i] = True
                n_frozen += 1
                for l in set(flow_links[i]):
                    remaining[l] -= best_share
                    active[l] -= 1
    return rate


def _selftest_maxmin():
    # one link, three flows
    r = maxmin([["A"], ["A"], ["A"]], {"A": 1.0})
    assert all(abs(x - 1 / 3) < 1e-12 for x in r), r
    # textbook: A cap 1 shared by f1,f2 ; B cap 2 shared by f2,f3
    r = maxmin([["A"], ["A", "B"], ["B"]], {"A": 1.0, "B": 2.0})
    assert abs(r[0] - 0.5) < 1e-12 and abs(r[1] - 0.5) < 1e-12 and abs(r[2] - 1.5) < 1e-12, r
    # parking-lot: long flow crosses 3 unit links, each shared with one short flow
    r = maxmin([["a", "b", "c"], ["a"], ["b"], ["c"]], {"a": 1, "b": 1, "c": 1})
    assert all(abs(x - 0.5) < 1e-12 for x in r), r


# ----------------------------------------------------------------------------
# Clos blocking: exhaustive check on tiny networks
#   C(n, m, r): r ingress switches with n inputs, m middle switches, r egress
#   switches with n outputs.  A call (i, o) occupies one ingress->middle link and
#   one middle->egress link.
# ----------------------------------------------------------------------------
def clos_states(n, m, r):
    """BFS over every state reachable by adding calls (with ANY legal middle
    choice) and removing calls.  Returns (states, blocking_states) where a
    blocking state has a free input and a free output but no legal middle."""
    NI = n * r
    start = frozenset()
    seen = {start}
    stack = [start]
    blocking = []
    while stack:
        st = stack.pop()
        used_in = {c[0] for c in st}
        used_out = {c[1] for c in st}
        a_used = {(c[0] // n, c[2]) for c in st}     # ingress switch, middle
        b_used = {(c[1] // n, c[2]) for c in st}     # egress switch, middle
        for i in range(NI):
            if i in used_in:
                continue
            for o in range(NI):
                if o in used_out:
                    continue
                legal = [mm for mm in range(m)
                         if (i // n, mm) not in a_used and (o // n, mm) not in b_used]
                if not legal:
                    blocking.append((st, i, o))
                for mm in legal:
                    ns = st | {(i, o, mm)}
                    if ns not in seen:
                        seen.add(ns); stack.append(ns)
        for c in st:
            ns = st - {c}
            if ns not in seen:
                seen.add(ns); stack.append(ns)
    return seen, blocking


def clos_rearrangeable(n, m, r, states):
    """For every reachable state and every free (i,o): is there SOME assignment
    of middles to all calls plus the new one?  (brute force via matching search)"""
    NI = n * r
    def feasible(calls):
        # calls: list of (i,o); assign middles by backtracking
        assign = []
        usedA, usedB = set(), set()
        def rec(k):
            if k == len(calls):
                return True
            i, o = calls[k]
            for mm in range(m):
                a, b = (i // n, mm), (o // n, mm)
                if a in usedA or b in usedB:
                    continue
                usedA.add(a); usedB.add(b)
                if rec(k + 1):
                    return True
                usedA.discard(a); usedB.discard(b)
            return False
        return rec(0)
    bad = 0
    for st in states:
        used_in = {c[0] for c in st}
        used_out = {c[1] for c in st}
        base = [(c[0], c[1]) for c in st]
        for i in range(NI):
            if i in used_in:
                continue
            for o in range(NI):
                if o in used_out:
                    continue
                if not feasible(base + [(i, o)]):
                    bad += 1
    return bad


def clos_theory_checks():
    out = {}
    for m in (2, 3):
        states, blocking = clos_states(2, m, 2)
        out[f"n2_r2_m{m}"] = dict(states=len(states), blocking_states=len(blocking))
        if m == 2:
            # smallest blocking example
            ex = min(blocking, key=lambda t: len(t[0]))
            out["n2_r2_m2_smallest_blocking"] = dict(
                calls=sorted(ex[0]), new_call=(ex[1], ex[2]))
            out["n2_r2_m2_rearrangement_failures"] = clos_rearrangeable(2, 2, 2, states)
    assert out["n2_r2_m2"]["blocking_states"] > 0           # m = n  blocks
    assert out["n2_r2_m3"]["blocking_states"] == 0          # m = 2n-1 never blocks
    assert out["n2_r2_m2_rearrangement_failures"] == 0      # but m = n is rearrangeable
    return out


# ----------------------------------------------------------------------------
# bipartite edge colouring (Konig): routes any permutation conflict-free on a
# 1:1 leaf-spine.  Colour = spine.
# ----------------------------------------------------------------------------
def bipartite_edge_coloring(edges, nL, nR, D):
    cL = [[-1] * D for _ in range(nL)]
    cR = [[-1] * D for _ in range(nR)]
    col = [-1] * len(edges)

    def setc(e, c):
        u, v = edges[e]
        cL[u][c] = e; cR[v][c] = e; col[e] = c

    def clearc(e):
        u, v = edges[e]
        c = col[e]
        cL[u][c] = -1; cR[v][c] = -1; col[e] = -1

    for ei, (u, v) in enumerate(edges):
        a = next(c for c in range(D) if cL[u][c] == -1)
        if cR[v][a] == -1:
            setc(ei, a)
            continue
        b = next(c for c in range(D) if cR[v][c] == -1)
        # walk the a/b alternating path from v:  v -a-> L -b-> R -a-> ...
        path, side, node, c = [], "R", v, a
        while True:
            e = cR[node][c] if side == "R" else cL[node][c]
            if e == -1:
                break
            path.append(e)
            side, node = ("L", edges[e][0]) if side == "R" else ("R", edges[e][1])
            c = b if c == a else a
        old = [(e, col[e]) for e in path]
        for e, _ in old:
            clearc(e)
        for e, c0 in old:
            setc(e, b if c0 == a else a)
        setc(ei, a)
    # verify properness
    for u in range(nL):
        cs = [col[e] for e in range(len(edges)) if edges[e][0] == u]
        assert len(cs) == len(set(cs))
    for v in range(nR):
        cs = [col[e] for e in range(len(edges)) if edges[e][1] == v]
        assert len(cs) == len(set(cs))
    return col


# ----------------------------------------------------------------------------
# Leaf-spine routing experiments (unit-capacity links)
# ----------------------------------------------------------------------------
class LeafSpine:
    def __init__(self, d, u, leaves):
        self.d, self.u, self.L = d, u, leaves
        self.H = d * leaves

    def leaf_of(self, h):
        return h // self.d

    def caps(self):
        c = {}
        for h in range(self.H):
            c[("h>l", h)] = 1.0
            c[("l>h", h)] = 1.0
        for l in range(self.L):
            for s in range(self.u):
                c[("l>s", l, s)] = 1.0
                c[("s>l", s, l)] = 1.0
        return c

    def path(self, src, dst, spine):
        ls, ld = self.leaf_of(src), self.leaf_of(dst)
        if ls == ld:
            return [("h>l", src), ("l>h", dst)]
        return [("h>l", src), ("l>s", ls, spine), ("s>l", spine, ld), ("l>h", dst)]

    def rates(self, pairs, routing, rng=None):
        """routing: 'ecmp' (random spine per flow), 'dmodk' (spine = dst % u),
        'perfect' (conflict-free colouring; only valid for permutations at d == u)."""
        if routing == "ecmp":
            sp = [rng.randrange(self.u) for _ in pairs]
        elif routing == "dmodk":
            sp = [dst % self.u for _, dst in pairs]
        elif routing == "perfect":
            sp = self.colour(pairs)
        else:
            raise ValueError(routing)
        flows = [self.path(s, t, x) for (s, t), x in zip(pairs, sp)]
        return maxmin(flows, self.caps()), sp

    def colour(self, pairs):
        edges, idx = [], []
        for k, (s, t) in enumerate(pairs):
            ls, ld = self.leaf_of(s), self.leaf_of(t)
            if ls != ld:
                edges.append((ls, ld)); idx.append(k)
        col = bipartite_edge_coloring(edges, self.L, self.L, max(self.u, self.d))
        out = [0] * len(pairs)
        for e, k in enumerate(idx):
            out[k] = col[e]
        assert max(col, default=0) < self.u or self.u >= self.d
        return out

    def uniform_lambda_explicit(self, pairs):
        """Largest lam such that a traffic matrix with `lam` units on every pair
        fits when each inter-leaf flow is split evenly over all u spines
        (explicit per-spine directed links, no pooling assumption).
        This is concurrent-flow scaling, NOT max-min fairness."""
        from collections import defaultdict
        load = defaultdict(float)
        for s, t in pairs:
            ls, ld = self.leaf_of(s), self.leaf_of(t)
            load[("h>l", s)] += 1.0
            load[("l>h", t)] += 1.0
            if ls != ld:
                for x in range(self.u):
                    load[("l>s", ls, x)] += 1.0 / self.u
                    load[("s>l", x, ld)] += 1.0 / self.u
        return 1.0 / max(load.values())

    # --- ideal "spray" fluid model: uplink bundle is one pooled resource ------
    def fluid_rates(self, pairs):
        flows, cap = [], {}
        for h in range(self.H):
            cap[("ho", h)] = 1.0; cap[("hi", h)] = 1.0
        for l in range(self.L):
            cap[("up", l)] = float(self.u); cap[("dn", l)] = float(self.u)
        for s, t in pairs:
            ls, ld = self.leaf_of(s), self.leaf_of(t)
            links = [("ho", s), ("hi", t)]
            if ls != ld:
                links += [("up", ls), ("dn", ld)]
            flows.append(links)
        return maxmin(flows, cap)


def permutation_experiment(d, u, leaves, trials, seed=1):
    ls = LeafSpine(d, u, leaves)
    rng = random.Random(seed)
    res = {"ecmp": [], "dmodk": [], "perfect": [], "ecmp_min": []}
    for _ in range(trials):
        perm = list(range(ls.H)); rng.shuffle(perm)
        pairs = list(enumerate(perm))
        pairs = [(s, t) for s, t in pairs if s != t]
        for r in ("ecmp", "dmodk"):
            rates, _ = ls.rates(pairs, r, rng)
            res[r].append(sum(rates) / len(rates))
            if r == "ecmp":
                res["ecmp_min"].append(min(rates))
        if d <= u:
            rates, _ = ls.rates(pairs, "perfect", rng)
            res["perfect"].append(sum(rates) / len(rates))
    return res


# ----------------------------------------------------------------------------
# Dragonfly routing on the canonical arrangement (unit-capacity links)
# ----------------------------------------------------------------------------
class DragonflyModel:
    def __init__(self, a, p, h):
        from topo_graphs import dragonfly
        self.a, self.p, self.h = a, p, h
        self.adj, self.glink, self.info = dragonfly(a, p, h)
        self.g = self.info["g"]

    def rid(self, grp, r):
        return grp * self.a + r

    def term(self, grp, r, t):
        return (grp * self.a + r) * self.p + t

    def group_of_router(self, R):
        return R // self.a

    def router_of_term(self, T):
        return T // self.p

    def min_route(self, Rs, Rd):
        """router path (list of routers) for minimal routing."""
        gs, gd = Rs // self.a, Rd // self.a
        if Rs == Rd:
            return [Rs]
        if gs == gd:
            return [Rs, Rd]
        ra, rb = self.glink[(gs, gd)]
        path = [Rs]
        if ra != Rs:
            path.append(ra)
        path.append(rb)
        if rb != Rd:
            path.append(Rd)
        return path

    def val_routes(self, Rs, Rd):
        """all Valiant routes via every intermediate *group* (entry router fixed)."""
        gs, gd = Rs // self.a, Rd // self.a
        routes = []
        for gm in range(self.g):
            if gm == gs or gm == gd:
                continue
            ra, rb = self.glink[(gs, gm)]         # leave src group
            rc, rd_ = self.glink[(gm, gd)]        # leave intermediate group
            path = [Rs]
            if ra != Rs:
                path.append(ra)
            path.append(rb)
            if rc != rb:
                path.append(rc)
            path.append(rd_)
            if rd_ != Rd:
                path.append(Rd)
            routes.append(path)
        return routes

    def throughput(self, pairs, mode):
        """Max uniform rate lam such that all flows fit (unit capacity on every
        directed router-router channel and every terminal link); flows split
        evenly over their route set."""
        load = defaultdict(float)
        for s, t in pairs:
            Rs, Rd = self.router_of_term(s), self.router_of_term(t)
            load[("inj", s)] += 1.0
            load[("ej", t)] += 1.0
            if mode == "min":
                routes = [self.min_route(Rs, Rd)]
            elif mode == "val":
                routes = self.val_routes(Rs, Rd) if Rs // self.a != Rd // self.a else [self.min_route(Rs, Rd)]
            else:
                raise ValueError(mode)
            w = 1.0 / len(routes)
            for pth in routes:
                for x, y in zip(pth, pth[1:]):
                    load[(x, y)] += w
        mx = max(load.values())
        return 1.0 / mx, load

    def pattern_worst_case(self):
        """Every terminal in group i sends to the same-offset terminal in group i+1."""
        pairs = []
        for gi in range(self.g):
            for r in range(self.a):
                for t in range(self.p):
                    pairs.append((self.term(gi, r, t), self.term((gi + 1) % self.g, r, t)))
        return pairs

    def pattern_uniform(self):
        T = self.info["terminals"]
        return [(s, t) for s in range(T) for t in range(T) if s != t]


# ----------------------------------------------------------------------------
# Channel dependency graph: why a torus needs virtual channels (Dally & Seitz)
# ----------------------------------------------------------------------------
def torus_routes_dor(k, n, dateline):
    """Minimal dimension-order routes on a k-ary n-cube (ties broken towards +).
    Each hop is a channel (node, dim, dir, vc). Returns list of channel lists."""
    nodes = list(itertools.product(range(k), repeat=n))
    routes = []
    for src in nodes:
        for dst in nodes:
            if src == dst:
                continue
            cur = list(src)
            chans = []
            for d in range(n):
                vc = 0
                diff = (dst[d] - cur[d]) % k
                if diff == 0:
                    continue
                step = +1 if diff <= k - diff else -1
                hops = diff if step == 1 else k - diff
                for _ in range(hops):
                    nxt = (cur[d] + step) % k
                    crossing = (step == 1 and cur[d] == k - 1) or (step == -1 and cur[d] == 0)
                    chans.append((tuple(cur), d, step, vc if dateline else 0))
                    if dateline and crossing:
                        vc = 1
                    cur[d] = nxt
            routes.append(chans)
    return routes


def has_cycle(routes):
    dep = defaultdict(set)
    for ch in routes:
        for x, y in zip(ch, ch[1:]):
            dep[x].add(y)
    color = {}
    sys_stack = []
    def dfs(u):
        color[u] = 1
        for v in dep.get(u, ()):
            c = color.get(v, 0)
            if c == 1:
                return True
            if c == 0 and dfs(v):
                return True
        color[u] = 2
        return False
    import sys
    sys.setrecursionlimit(100000)
    for u in list(dep.keys()):
        if color.get(u, 0) == 0 and dfs(u):
            return True
    return False


def deadlock_checks():
    out = {}
    for k, n in ((4, 1), (5, 1), (4, 2)):
        out[f"k{k}_n{n}_no_vc_cycle"] = has_cycle(torus_routes_dor(k, n, False))
        out[f"k{k}_n{n}_dateline_cycle"] = has_cycle(torus_routes_dor(k, n, True))
    # mesh routes never form a cycle with DOR
    assert all(out[f"k{k}_n{n}_no_vc_cycle"] for k, n in ((4, 1), (5, 1), (4, 2)))
    assert not any(out[f"k{k}_n{n}_dateline_cycle"] for k, n in ((4, 1), (5, 1), (4, 2)))
    return out


# ----------------------------------------------------------------------------
# alpha-beta collectives (Hockney-style, as used by Thakur/Rabenseifner/Gropp 2005)
# ----------------------------------------------------------------------------
def t_ring_allreduce(p, n, alpha, beta, gamma=0.0):
    return 2 * (p - 1) * alpha + 2 * (p - 1) / p * n * beta + (p - 1) / p * n * gamma


def t_rabenseifner_allreduce(p, n, alpha, beta, gamma=0.0):
    return 2 * math.log2(p) * alpha + 2 * (p - 1) / p * n * beta + (p - 1) / p * n * gamma


def t_recdbl_allreduce(p, n, alpha, beta, gamma=0.0):
    return math.log2(p) * (alpha + n * beta + n * gamma)


def t_tree_allreduce(p, n, alpha, beta, gamma=0.0):
    """binomial-tree reduce followed by binomial-tree broadcast"""
    return 2 * math.ceil(math.log2(p)) * (alpha + n * beta) + math.ceil(math.log2(p)) * n * gamma


def ring_vs_rabenseifner_crossover(p, alpha, beta):
    """Message size where the ring's extra latency term equals Rabenseifner's
    bandwidth advantage -- they have the *same* bandwidth term, so the ring is
    never faster in this model: report None.  Kept explicit so the video does
    not claim a crossover that the model does not have."""
    return None


# ----------------------------------------------------------------------------
# collectives x placement on an oversubscribed leaf-spine (fluid spray model)
# ----------------------------------------------------------------------------
def place_block(p):
    return list(range(p))                     # rank r -> host r


def place_cyclic(p, ls: LeafSpine):
    """rank r -> leaf (r % L), slot (r // L): maximally scattered rank order."""
    return [(r % ls.L) * ls.d + (r // ls.L) for r in range(p)]


def ring_slowdown(ls: LeafSpine, hosts):
    p = len(hosts)
    pairs = [(hosts[i], hosts[(i + 1) % p]) for i in range(p)]
    return 1.0 / min(ls.fluid_rates(pairs))


def rabenseifner_phase_times(ls: LeafSpine, hosts, order):
    """Reduce-scatter + allgather via recursive halving/doubling, expressed in
    units of n*beta (message of n bytes at link rate 1).  order = 'doubling'
    (partner distance 1, 2, 4, ...; big messages first on short distances) or
    'halving' (partner distance p/2, p/4, ...; big messages first on long
    distances).  Allgather mirrors the reduce-scatter."""
    p = len(hosts)
    steps = int(math.log2(p))
    dists = [2 ** k for k in range(steps)] if order == "doubling" else [p // 2 ** (k + 1) for k in range(steps)]
    t = 0.0
    detail = []
    for k, dist in enumerate(dists):
        bytes_frac = 1.0 / 2 ** (k + 1)
        pairs = [(hosts[i], hosts[i ^ dist]) for i in range(p)]
        rate = min(ls.fluid_rates(pairs))
        t += bytes_frac / rate
        detail.append(dict(dist=dist, bytes=bytes_frac, rate=rate))
    return 2 * t, detail   # reduce-scatter + allgather


def placement_experiments(d=32, u=8, leaves=16):
    """A job that fills the whole cluster (p = d * leaves ranks, a power of two).
    Slowdowns are relative to the same algorithm on a non-blocking network,
    under the idealised 'spray' model (no hash collisions): they isolate the
    effect of *which ranks talk to each other* from the effect of routing."""
    ls = LeafSpine(d, u, leaves)
    p = d * leaves
    assert p & (p - 1) == 0, "p must be a power of two for recursive halving"
    out = {"d": d, "u": u, "ratio": d / u, "leaves": leaves, "ranks": p}
    blk = place_block(p)
    cyc = place_cyclic(p, ls)
    out["ring_block"] = ring_slowdown(ls, blk)
    out["ring_cyclic"] = ring_slowdown(ls, cyc)
    ideal = 2 * (p - 1) / p
    for name, hosts in (("block", blk), ("cyclic", cyc)):
        for order in ("doubling", "halving"):
            t, det = rabenseifner_phase_times(ls, hosts, order)
            out[f"rab_{name}_{order}"] = t / ideal
            out[f"rab_{name}_{order}_detail"] = det
    # random rank order (what you get if the launcher ignores topology)
    rng = random.Random(7)
    shuffled = list(range(ls.H)); rng.shuffle(shuffled)
    out["ring_random_order"] = ring_slowdown(ls, shuffled)
    return out
