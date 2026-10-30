"""Topology builders and exact graph metrics used by the video.

Everything here is plain Python (stdlib + numpy). No networkx.
Conventions
-----------
* A topology is an undirected simple graph over *routers* (adjacency list of sets)
  plus a number of endpoints ("terminals") attached to each router.
* Link = one bidirectional cable. Channel = one direction of a link.
* "Relative bisection" beta = (bisection bandwidth per direction) /
  ((N/2) * injection bandwidth). beta = 1 means a bisection-crossing
  permutation can in principle run at full injection rate.
"""
from __future__ import annotations
import itertools
from collections import deque


# ----------------------------------------------------------------------------
# generic graph helpers
# ----------------------------------------------------------------------------
def bfs_dist(adj, src):
    dist = [-1] * len(adj)
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def eccentricity(adj, src):
    d = bfs_dist(adj, src)
    assert min(d) >= 0, "graph is disconnected"
    return max(d)


def diameter_exact(adj, sources=None):
    """Max over BFS from `sources` (default: every vertex)."""
    srcs = range(len(adj)) if sources is None else sources
    return max(eccentricity(adj, s) for s in srcs)


def avg_distance(adj, sources=None):
    srcs = list(range(len(adj)) if sources is None else sources)
    tot = 0
    cnt = 0
    for s in srcs:
        d = bfs_dist(adj, s)
        tot += sum(d)
        cnt += len(d) - 1
    return tot / cnt


def n_links(adj):
    return sum(len(a) for a in adj) // 2


def cut_size(adj, side):
    """Number of links with one end in `side` (a set) and one outside."""
    c = 0
    for u in side:
        for v in adj[u]:
            if v not in side:
                c += 1
    return c


def min_bisection_bruteforce(adj):
    """Exact minimum balanced cut by enumeration. Only for len(adj) <= 20."""
    n = len(adj)
    assert n % 2 == 0 and n <= 20
    best = None
    # fix vertex 0 on side A to halve the enumeration
    for comb in itertools.combinations(range(1, n), n // 2 - 1):
        side = set(comb) | {0}
        c = cut_size(adj, side)
        if best is None or c < best:
            best = c
    return best


# ----------------------------------------------------------------------------
# k-ary n-cube (torus / mesh) and hypercube
# ----------------------------------------------------------------------------
def kary_ncube(k, n, wrap=True):
    coords = list(itertools.product(range(k), repeat=n))
    idx = {c: i for i, c in enumerate(coords)}
    adj = [set() for _ in coords]
    for c in coords:
        for d in range(n):
            for s in (-1, 1):
                x = c[d] + s
                if wrap:
                    x %= k
                elif not (0 <= x < k):
                    continue
                c2 = c[:d] + (x,) + c[d + 1:]
                if c2 != c:
                    adj[idx[c]].add(idx[c2])
                    adj[idx[c2]].add(idx[c])
    return adj, coords


def torus_nd(dims, wrap=True):
    """General torus/mesh with different extent per dimension."""
    coords = list(itertools.product(*[range(k) for k in dims]))
    idx = {c: i for i, c in enumerate(coords)}
    adj = [set() for _ in coords]
    for c in coords:
        for d, k in enumerate(dims):
            for s in (-1, 1):
                x = c[d] + s
                if wrap:
                    x %= k
                elif not (0 <= x < k):
                    continue
                c2 = c[:d] + (x,) + c[d + 1:]
                if c2 != c:
                    adj[idx[c]].add(idx[c2])
                    adj[idx[c2]].add(idx[c])
    return adj, coords


def torus_diameter_formula(dims):
    return sum(k // 2 for k in dims)


def mesh_diameter_formula(dims):
    return sum(k - 1 for k in dims)


def torus_bisection_links_formula(dims):
    """Cut perpendicular to the longest even dimension.
    Two cut planes (wraparound) for k>2; a single plane when k == 2."""
    kmax = max(dims)
    N = 1
    for k in dims:
        N *= k
    per_plane = N // kmax
    planes = 2 if kmax > 2 else 1
    return planes * per_plane


def mesh_bisection_links_formula(dims):
    kmax = max(dims)
    N = 1
    for k in dims:
        N *= k
    return N // kmax


def hypercube(n):
    return kary_ncube(2, n, wrap=True)[0]


# ----------------------------------------------------------------------------
# HyperX (Ahn et al., SC09), regular case: L dims, S switches per dim, K trunking
# ----------------------------------------------------------------------------
def hyperx(L, S):
    coords = list(itertools.product(range(S), repeat=L))
    idx = {c: i for i, c in enumerate(coords)}
    adj = [set() for _ in coords]
    for c in coords:
        for d in range(L):
            for x in range(S):
                if x != c[d]:
                    c2 = c[:d] + (x,) + c[d + 1:]
                    adj[idx[c]].add(idx[c2])
    return adj, coords


def hyperx_formulas(L, S, K, T):
    """Formulas as printed in Ahn et al. (radix bound, size, relative bisection)."""
    P = S ** L
    radix = T + L * K * (S - 1)
    N = T * P
    beta = K * S / (2 * T)          # (4) with uniform S, K
    return dict(switches=P, radix=radix, terminals=N, beta=beta,
                bisection_channels=P * K * S // 4)


# ----------------------------------------------------------------------------
# Dragonfly (Kim, Dally, Scott, Abts; ISCA 2008)
#   a routers / group (all-to-all), p terminals / router, h global ports / router
#   max groups g = a*h + 1  -> one global link between every pair of groups
# ----------------------------------------------------------------------------
def dragonfly(a, p, h):
    g = a * h + 1
    R = g * a
    adj = [set() for _ in range(R)]
    rid = lambda grp, r: grp * a + r
    # local all-to-all
    for grp in range(g):
        for r1 in range(a):
            for r2 in range(r1 + 1, a):
                adj[rid(grp, r1)].add(rid(grp, r2))
                adj[rid(grp, r2)].add(rid(grp, r1))
    # global: group i, index j in [0, g-2] connects to group (i + j + 1) % g,
    # carried by router j // h of that group.  The matching index at the far
    # end is j' = g - 2 - j.
    glink = {}   # (grp_i, grp_k) -> (router_i, router_k)
    for i in range(g):
        for j in range(g - 1):
            k = (i + j + 1) % g
            j2 = g - 2 - j
            ri, rk = j // h, j2 // h
            glink[(i, k)] = (rid(i, ri), rid(k, rk))
            adj[rid(i, ri)].add(rid(k, rk))
            adj[rid(k, rk)].add(rid(i, ri))
    info = dict(a=a, p=p, h=h, g=g, routers=R, terminals=R * p,
                radix=p + (a - 1) + h)
    return adj, glink, info


def dragonfly_formulas(a, p, h):
    g = a * h + 1
    return dict(g=g, N=a * p * g, radix=p + a + h - 1, virtual_radix=a * (p + h),
                balanced=(a == 2 * p == 2 * h))


# ----------------------------------------------------------------------------
# Folded-Clos / fat tree
# ----------------------------------------------------------------------------
def leaf_spine(d, u, leaves, links_per_pair=1):
    """Two-level fat tree. Vertex layout: hosts, then leaves, then spines.
    d hosts per leaf, u spines (each leaf has links_per_pair links to each)."""
    H = d * leaves
    n = H + leaves + u
    adj = [set() for _ in range(n)]
    leaf = lambda l: H + l
    spine = lambda s: H + leaves + s
    for l in range(leaves):
        for i in range(d):
            adj[l * d + i].add(leaf(l)); adj[leaf(l)].add(l * d + i)
        for s in range(u):
            adj[leaf(l)].add(spine(s)); adj[spine(s)].add(leaf(l))
    return adj, dict(hosts=H, leaves=leaves, spines=u, d=d, u=u)


def fat_tree_k(k):
    """Al-Fares style 3-level k-ary fat tree built from k-port switches.
    Returns adjacency (hosts first), and an info dict."""
    assert k % 2 == 0
    half = k // 2
    pods = k
    hosts = pods * half * half
    edge0 = hosts
    agg0 = edge0 + pods * half
    core0 = agg0 + pods * half
    n = core0 + half * half
    adj = [set() for _ in range(n)]
    def link(a, b):
        adj[a].add(b); adj[b].add(a)
    for p in range(pods):
        for e in range(half):
            E = edge0 + p * half + e
            for hh in range(half):
                link(p * half * half + e * half + hh, E)
            for a_ in range(half):
                link(E, agg0 + p * half + a_)
        for a_ in range(half):
            A = agg0 + p * half + a_
            for c in range(half):
                link(A, core0 + a_ * half + c)
    return adj, dict(hosts=hosts, edge=pods * half, agg=pods * half,
                     core=half * half, switches=pods * half * 2 + half * half)


def fat_tree_formulas(k, levels):
    if levels == 2:
        return dict(hosts=k * k // 2, switches=3 * k // 2)
    if levels == 3:
        return dict(hosts=k ** 3 // 4, switches=5 * k * k // 4)
    raise ValueError


def oversub_table(radix, splits):
    """Two-level leaf-spine at maximum scale for each (down, up) port split.
    Spine radix == leaf radix, one link from every leaf to every spine."""
    rows = []
    for d, u in splits:
        assert d + u <= radix
        leaves = radix                 # each spine port feeds one leaf
        spines = u
        hosts = leaves * d
        sw = leaves + spines
        rows.append(dict(down=d, up=u, ratio=d / u, spare_ports=radix - d - u,
                         leaves=leaves, spines=spines, hosts=hosts, switches=sw,
                         switches_per_1000_hosts=1000 * sw / hosts,
                         uplink_cables=leaves * u,
                         cables_per_host=(hosts + leaves * u) / hosts))
    return rows
