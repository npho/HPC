#!/usr/bin/env python3
"""
Every number in the video that is *derived by me* (not quoted from a source) is computed here,
so it is reproducible and can be audited.  Output: ../build/model_numbers.json

Sections
  1. first-principles arithmetic (serialization, propagation, buffers, PCIe, headers)
  2. topology sizing (fat-tree, dragonfly) and checks against vendor / paper claims
  3. ECMP-collision toy model (leaf-spine, max-min fair sharing)  -- MODEL, not a measurement
"""
import json, math, os, random
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "build")
os.makedirs(OUT, exist_ok=True)
R = {}

# ---------------------------------------------------------------- 1. arithmetic
C_FIBER_NS_PER_M = 4.9            # ~ n/c with n ~ 1.47  (physics, approximate)
R["fiber_ns_per_m"] = C_FIBER_NS_PER_M

def ser_ns(nbytes, gbps):          # serialization time of nbytes at gbps, in ns
    return nbytes * 8 / gbps

R["serialize_4KiB_ns"] = {g: ser_ns(4096, g) for g in (1, 10, 100, 400, 800)}
R["fiber_m_during_4KiB_at_400G"] = ser_ns(4096, 400) / C_FIBER_NS_PER_M

# bandwidth-delay buffer per link: BW x RTT, propagation only (a lower bound; ignores pause/credit turnaround)
def bdp_bytes(gbps, meters):
    rtt_ns = 2 * meters * C_FIBER_NS_PER_M
    return gbps * rtt_ns / 8        # (Gb/s * ns) / 8 = bytes
R["bdp_400G_bytes"] = {m: bdp_bytes(400, m) for m in (3, 50, 100, 500, 2000)}

# PCIe (values from Wikipedia PCIe table, GB/s per direction for x16)
PCIE_X16_GBps = {"Gen4": 31.508, "Gen5": 63.015, "Gen6": 121.0}
R["pcie_x16_Gbps_per_dir"] = {k: v * 8 for k, v in PCIE_X16_GBps.items()}

# header efficiency at 4 KiB payload
hdr = {"InfiniBand (LRH8+BTH12+ICRC4+VCRC2)": 26,
       "RoCEv2, Slingshot-paper count": 62,
       "RoCEv2, Hoefler et al. count": 66}
R["header_efficiency_4KiB"] = {k: 4096 / (4096 + b) for k, b in hdr.items()}
R["header_overhead_pct_4KiB"] = {k: 100 * b / (4096 + b) for k, b in hdr.items()}

# ---------------------------------------------------------------- 2. topology sizing
def fat2(k):   # 2-level, k-port switches, 1:1
    return dict(hosts=k * k // 2, switches=k + k // 2)
def fat3(k):   # 3-level (Al-Fares): k^3/4 hosts, 5k^2/4 switches
    return dict(hosts=k ** 3 // 4, switches=5 * k * k // 4)
R["fat_tree"] = {k: {"two_level": fat2(k), "three_level": fat3(k)} for k in (4, 8, 36, 48, 64, 128, 144, 512)}
# checks against claims
R["checks"] = {
    "Q3400 144-port two-level -> NICs (datasheet says 10,368)": fat2(144)["hosts"],
    "Al-Fares k=48 three-level hosts (paper says 27,648)": fat3(48)["hosts"],
    "Al-Fares k=48 switches (paper says 2,880)": fat3(48)["switches"],
    "TH6 at 200G: 512 ports two-level hosts (Broadcom says >100,000)": fat2(512)["hosts"],
}
def dfly(p, a, h):
    g = a * h + 1
    return dict(groups=g, terminals=a * p * g, radix=p + a + h - 1)
R["dragonfly"] = {
    "Kim fig5 p=h=2,a=4": dfly(2, 4, 2),
    "Frontier-like a=32,p=16,h=16 (max)": dfly(16, 32, 16),
    "Slingshot paper 1D example a=32,p=16,h=17": dfly(16, 32, 17),
}
R["frontier_global_links_used_per_group"] = 73 * 4   # 4 links to each of 73 other groups
R["frontier_global_ports_per_group"] = 32 * 16
R["frontier_nodes"] = 74 * 128
R["frontier_injection_GBps_per_node"] = 4 * 25

# ---------------------------------------------------------------- 3. ECMP toy model
def maxmin(flows_links, ncap):
    """Progressive filling. flows_links: list of tuple(link ids); all links capacity 1.0."""
    nf = len(flows_links)
    rate = np.zeros(nf)
    cap = np.full(ncap, 1.0)
    active = np.ones(nf, bool)
    link_flows = [[] for _ in range(ncap)]
    for f, ls in enumerate(flows_links):
        for l in ls:
            link_flows[l].append(f)
    while active.any():
        best, bl = None, None
        for l in range(ncap):
            fl = [f for f in link_flows[l] if active[f]]
            if not fl:
                continue
            share = cap[l] / len(fl)
            if best is None or share < best:
                best, bl = share, l
        if best is None:
            break
        for f in [f for f in link_flows[bl] if active[f]]:
            rate[f] += best
            active[f] = False
            for l in flows_links[f]:
                cap[l] -= best
        # others: they also grew by `best` while active; handle by adding to remaining active flows
        for f in np.where(active)[0]:
            rate[f] += best
            for l in flows_links[f]:
                cap[l] -= best
        cap = np.maximum(cap, 0)
    return rate

def _selftest():
    # two flows sharing one unit link -> 0.5 each; a disjoint flow -> 1.0
    r = maxmin([(0,), (0,), (1,)], 2)
    assert abs(r[0] - 0.5) < 1e-9 and abs(r[1] - 0.5) < 1e-9 and abs(r[2] - 1.0) < 1e-9, r
    # classic max-min example: flow A uses links 0,1 ; B uses link 0 ; C uses link 1 ; D uses link 1
    # link0 shared by A,B  link1 shared by A,C,D  -> bottleneck link1: A=C=D=1/3 ; then B gets 1-1/3 = 2/3
    r = maxmin([(0, 1), (0,), (1,), (1,)], 2)
    assert np.allclose(r, [1/3, 2/3, 1/3, 1/3]), r
    # three flows over a 2-link chain with different bottlenecks
    r = maxmin([(0,), (0,), (0,)], 1)
    assert np.allclose(r, [1/3, 1/3, 1/3]), r
_selftest()
print("maxmin self-test passed")

def leafspine_trial(L, H, U, pattern, route, rng):
    N = L * H
    if pattern == "shift":
        dst = [(i + H) % N for i in range(N)]
    else:
        dst = list(range(N)); rng.shuffle(dst)
    flows = []
    for s in range(N):
        d = dst[s]
        ls, ld = s // H, d // H
        if s == d:
            continue
        if ls == ld:
            flows.append(())          # same leaf: no spine link, rate 1
            continue
        if route == "ecmp":
            sp = rng.randrange(U)
        elif route == "dmodk":
            sp = (d % H) % U
        else:
            raise ValueError
        up = ls * U + sp                          # uplink  leaf->spine
        down = L * U + sp * L + ld                # downlink spine->leaf
        flows.append((up, down))
    rate = maxmin([f for f in flows], 2 * L * U) if any(flows) else np.ones(len(flows))
    rate = np.array([1.0 if not f else r for f, r in zip(flows, rate)])
    return rate.mean()

def run_model(L=16, H=16, trials=300, seed=7):
    out = {}
    rng = random.Random(seed)
    U = H
    for pattern in ("random_permutation", "shift"):
        for route in ("ecmp", "dmodk"):
            vals = [leafspine_trial(L, H, U, pattern, route, rng) for _ in range(trials if not (pattern == "shift" and route == "dmodk") else 3)]
            out[f"{pattern}/{route}"] = dict(mean=float(np.mean(vals)), p5=float(np.percentile(vals, 5)), p95=float(np.percentile(vals, 95)), trials=len(vals))
    out["ideal_per_packet_spraying"] = dict(mean=1.0, note="each flow split evenly over all uplinks: every link carries exactly H/U = 1 flow-equivalent")
    return out

R["ecmp_model_16x16"] = run_model(16, 16, trials=300)
# sensitivity to fabric size (random permutation, flow-level ECMP)
sens = {}
for (L, H) in ((8, 8), (16, 16), (32, 32)):
    rng = random.Random(11)
    v = [leafspine_trial(L, H, H, "random_permutation", "ecmp", rng) for _ in range(120 if L < 32 else 40)]
    sens[f"{L}x{H} ({L*H} hosts)"] = float(np.mean(v))
R["ecmp_model_sensitivity_random_perm"] = sens

with open(os.path.join(OUT, "model_numbers.json"), "w") as f:
    json.dump(R, f, indent=2, default=lambda o: float(o))
print(json.dumps(R, indent=2, default=lambda o: float(o)))
