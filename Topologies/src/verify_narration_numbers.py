#!/usr/bin/env python3
"""Cross-check every number the narration speaks against build/results.json (or closed forms).
Each line: (what the narration says, value it must match, computed value, tolerance).
Run:  python3 verify_narration_numbers.py   (exit code 1 on any mismatch)"""
import json, math, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R = json.load(open(os.path.join(ROOT, "build", "results.json")))
checks = []
def chk(name, said, got, tol=0.0):
    checks.append((name, said, got, abs(said - got) <= tol + 1e-12))

ft = R["fat_tree"]; T = {r["down"]: r for r in ft["oversub_table_r64"]}
chk("k=64 two-level hosts", 2048, ft["sizes"]["k64_2level"]["hosts"]); chk("k=64 two-level switches", 96, ft["sizes"]["k64_2level"]["switches"])
chk("k=64 three-level hosts", 65536, ft["sizes"]["k64_3level"]["hosts"]); chk("k=64 three-level switches", 5120, ft["sizes"]["k64_3level"]["switches"])
chk("3:1 hosts", 3072, T[48]["hosts"]); chk("3:1 switches", 80, T[48]["switches"])
chk("switches/1000 hosts 1:1 (~47)", 47, T[32]["switches_per_1000_hosts"], 0.5); chk("switches/1000 hosts 3:1 (~26)", 26, T[48]["switches_per_1000_hosts"], 0.5)
chk("uplink cables/host 3:1 = 1/3", 1/3, T[48]["uplink_cables"] / T[48]["hosts"], 1e-9)
f_off = (3072 - 48) / (3072 - 1); chk("uniform all-to-all at 3:1 (~34%)", 0.34, (1/3) / f_off, 0.005)
P = R["permutations"]["leafspine_16x16_1to1"]
chk("hash mean (~55%)", 0.55, P["ecmp"]["mean"], 0.01); chk("unluckiest flow (~a fifth)", 0.20, P["ecmp_min"]["mean"], 0.02)
chk("static-by-destination (~70%)", 0.70, P["dmodk"]["mean"], 0.01); chk("edge-coloured = line rate", 1.0, P["perfect"]["mean"]); chk("trials", 200, R["permutations"]["trials"])
cl = R["clos"]; chk("m=2 blocking states", 128, cl["n2_r2_m2"]["blocking_states"]); chk("m=3 blocking states", 0, cl["n2_r2_m3"]["blocking_states"]); chk("rearrangement failures", 0, cl["n2_r2_m2_rearrangement_failures"])
cu = {r["name"]: r for r in R["cubes"]["rows"]}
chk("8x8x8 beta", 0.5, cu["3D torus 8x8x8"]["beta"]); chk("8x8x8 diameter", 12, cu["3D torus 8x8x8"]["diameter"])
chk("16^3 beta", 0.25, cu["3D torus 16x16x16"]["beta"]); chk("16^3 diameter", 24, cu["3D torus 16x16x16"]["diameter"]); chk("16^3 nodes", 4096, cu["3D torus 16x16x16"]["N"])
bg = R["cubes"]["bluegene_l"]; chk("BG/L nodes", 65536, bg["nodes"]); chk("BG/L bisection links", 2048, bg["bisection_links"]); chk("BG/L GB/s", 358.4, bg["gbytes_per_s_per_direction"], 0.05); chk("BG/L = 64*32*32", 65536, 64*32*32)
chk("K computer nodes", 82944, 24*18*16*2*3*2); chk("K virtual torus", 82944, math.prod(R["cubes"]["k_computer"]["virtual_torus"]))
AL = R["alltoall_loads"]; chk("mesh max/mean (a third more)", 1.3333, AL["mesh"]["max_over_mean"], 1e-3); chk("torus/mesh saturation (~2x)", 2.0, AL["torus"]["saturation_injection"]/AL["mesh"]["saturation_injection"], 0.02)
chk("hypercube 13-cube cables/node", 6.5, 13/2)
hx = R["hyperx"]["rows"]; chk("HyperX 16x16 T=8 beta", 1.0, hx[2]["beta"]); chk("HyperX T=16 beta", 0.5, hx[1]["beta"]); chk("HyperX T=32 beta", 0.25, hx[0]["beta"]); chk("HyperX 256 switches", 256, hx[0]["switches"])
df = R["dragonfly"]; chk("Slingshot max groups", 545, df["slingshot_max"]["g"]); chk("Slingshot max endpoints", 279040, df["slingshot_max"]["N"]); chk("Slingshot radix 16+31+17", 64, 16+31+17)
s0 = df["sims"][0]; chk("a=4,p=h=2 groups", 9, s0["g"]); chk("a=4 machines", 72, s0["N"]); chk("MIN adversarial 1/(a*p)=1/8", 0.125, s0["wc_min"], 1e-9)
chk("VAL adversarial (~44%)", 0.44, s0["wc_val"], 0.005); chk("VAL uniform (~55%)", 0.55, s0["uni_val"], 0.01); chk("MIN uniform = full rate", 1.0, s0["uni_min"])
co = R["collectives"]; chk("ring startup p=1024 (4.09 ms)", 4.09e-3, co["latency_only"]["1024"]["ring"], 5e-6); chk("halving/doubling startup (40 us)", 40e-6, co["latency_only"]["1024"]["rabenseifner"], 1e-7)
chk("ring startup formula 2(p-1)alpha", 2*1023*2e-6, co["latency_only"]["1024"]["ring"], 1e-9)
pl = R["placement"]["4to1"]; chk("4:1 ring shuffled (4x)", 4.0, pl["ring_cyclic"], 1e-9); chk("4:1 halving in order (3.8x)", 3.8, pl["rab_block_halving"], 0.03); chk("4:1 reordered (1.09x)", 1.09, pl["rab_block_doubling"], 0.005); chk("4:1 ring in order", 1.0, pl["ring_block"])
cm = {r["name"]: r for r in R["compare"]["rows"]}
chk("torus 16x16x32 diameter 32", 32, cm["3D torus 16x16x32"]["diameter"]); chk("torus beta 1/8", 0.125, cm["3D torus 16x16x32"]["beta"]); chk("torus cables/node 3", 3.0, cm["3D torus 16x16x32"]["cables_per_endpoint"])
chk("hypercube radix 14", 14, cm["hypercube (13 dimensions)"]["radix"]); chk("fat tree 1:1 cables/endpoint 2", 2.0, cm["fat tree (3 levels, 32-port, 1:1)"]["cables_per_endpoint"])
chk("HyperX cables/endpoint < 1.5", 1, int(cm["HyperX 16x16, 32 nodes/switch"]["cables_per_endpoint"] < 1.5)); chk("dragonfly cables/endpoint < 1.5", 1, int(cm["dragonfly a=16, p=8, h=8"]["cables_per_endpoint"] < 1.5))
bad = 0
for name, said, got, ok in checks:
    print(("OK   " if ok else "FAIL ") + f"{name:44s} narration/slide: {said:<12.6g} model: {got:.6g}"); bad += (not ok)
print(f"\n{len(checks)-bad}/{len(checks)} narration numbers match the models"); sys.exit(1 if bad else 0)
