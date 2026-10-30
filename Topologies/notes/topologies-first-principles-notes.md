# HPC interconnect topologies: first-principles notes (companion to the explainer video)

Everything below is either (a) checked against a source I fetched, (b) computed by me and reproducible from `src/`, or (c) flagged. "Checked" means a source said it; it does not mean I measured it. Run `python3 src/verify_narration_numbers.py` to re-check every number the narration speaks against the model outputs (59 of 59 match as of the final build).

## Verification status at a glance
- **Re-checked against primary text late in the build:** Seitz, "The Cosmic Cube" (CACM, Jan 1985): 64 nodes, six channels per node, the two quoted claims; the June 2026 TOP500 top-10 table (names and interconnects).
- **Checked in the research pass, from a fetched page or paper but not re-fetched at the end:** Clos 1953 conditions, Leiserson 1985, Dally & Seitz 1987, Dally 1990, Kim et al. 2008, HyperX (SC09) formulas, Domke et al. SC19 abstract, Slingshot (De Sensi, SC20), TPU v4 (arXiv 2304.01433), Blue Gene/L (IBM RC22851), Patarasuk & Yuan, Thakur et al., the NCCL 2.4 blog, Slurm topology docs, Bhatele (SC11), Yang (SC16), Slim Fly, the IETF Dragonfly+ draft. Treat these as "sourced, worth one more look before you cite them."
- **Modeled by me (not measurements):** every throughput percentage, every table in the comparison slide, the placement slowdowns, the α–β allreduce closed forms (my derivation from the standard model), the dragonfly MIN/VAL numbers.
- **Reported by one outlet or by a vendor/author about their own product:** LineShine's "multi-rail fat tree, 1.6 Tb/s per node"; Slingshot 1.3x vs 93x; Myricom's own TOP500 share; Cray's description of Aries; Kim et al.'s 20% / 52% cost estimate (their 2008 cost model).

## Corrections I made during the build (so you can see the mistakes)
- **Cosmic Cube dating (caught in the final pass).** My narration said Seitz and Geoffrey Fox "began building" it in 1981. The primary paper dates modeling to 1980–82 and the first 4-node prototype to winter 1981–82, and Fox appears only in its reference list. The joint "Seitz and Fox from 1981" wording comes from Wikipedia. The narration now says "early nineteen eighties, Seitz and his group at Caltech," and the on-screen label says "4-node prototype 1981–82."
- My first "uniform all-to-all" check compared max-min fair rates, which is not the same as concurrent scaling. I added an explicit solve; it now matches the closed form min(1, (u/d)/f_off).
- Dragonfly per-pair rates in the uniform case needed scaling by (N−1) to be per-node.
- Fat-tree diameter first included the host hop (5); it is 4 switch-to-switch hops (6 links host to host in a 3-level tree).
- I had a "2β uniform ceiling" in the metrics code. It misleads for oversubscribed trees, so I removed it.
- My first placement experiment showed no oversubscription penalty because only 16 hosts sat under each leaf with 16 uplinks. I redesigned it (32 hosts per leaf, 512 ranks).
- A stray `per_node_throughput` field in the results was meaningless; removed.
- Rounding: the narration says the unluckiest hashed flow gets "about a fifth"; the model gives 0.217 (the slide says ≈ 0.22).
- Length: I planned about 21 minutes of narration; the synthesized result runs 24.7 minutes.
- I could not read Fujitsu's own Tofu PDFs (they redirect to the homepage), and the Al-Fares paper host blocks automated fetches. I did not work around either. Tofu details come from The Next Platform and an Ajima conference talk; Al-Fares is not cited on screen.

## History (scene 2)
- Clos, "A study of non-blocking switching networks," BSTJ 32(2):406–424, 1953. Checked via the Clos network reference page.
- Cosmic Cube: Seitz, CACM 28(1):22–33, Jan 1985. 64 nodes, "connected ... to six other nodes," 8086/8087, 128 KB per node, 2 Mbit/s channels. Checked in the paper. Quote used in scene 9: "shown by simulation to provide very good message-flow properties in irregular computations"; "It also contains all meshes of lower dimension."
- Leiserson, "Fat-trees," IEEE Trans. Computers C-34(10), 1985. Dally & Seitz, "Deadlock-free message routing in multiprocessor interconnection networks," IEEE TC C-36(5), 1987. Dally, "Performance analysis of k-ary n-cube interconnection networks," IEEE TC 39(6), 1990.
- Kim, Dally, Scott, Abts, "Technology-driven, highly-scalable dragonfly topology," ISCA 2008, pp. 77–88. Ahn et al., "HyperX," SC09.
- Not used: a claim linking Seitz to Myricom's founding (an uncited Wikipedia statement).

## Measuring sticks and fat trees (scenes 3–5)
- Definitions (diameter, radix, bisection, β = bisection per direction ÷ ((N/2) · injection)) are standard; the cut-around-a-leaf example is my own illustration.
- Two-level fat tree: k²/2 hosts on 3k/2 switches. Three-level: k³/4 hosts on 5k²/4 switches. Verified by constructing the graphs and counting (`selftest.py`). k = 64: 2,048 / 96 and 65,536 / 5,120.
- Oversubscription table (64-port switches, two levels): 32:32 → 2,048 hosts / 96 switches; 48:16 → 3,072 / 80; 56:8 → 3,584 / 72. Switches per 1,000 hosts 46.9 / 26.0 / 20.1. Uplink cables per host 1, 1/3, 1/7.
- Uniform all-to-all per host = min(1, (u/d) / f_off), f_off = (N−d)/(N−1); at 3:1 this is 0.339. Multi-tier ratios multiply.

## Clos and routing (scenes 6–7)
- Strictly non-blocking: m ≥ 2n−1. Rearrangeably non-blocking: m ≥ n. Checked against the Clos network reference and Clos 1953.
- My brute force, n = 2, r = 2: m = 2 has 561 reachable states, 128 of them blocking; m = 3 has 2,497 states, none blocking; with m = 2 a rearrangement always exists (0 failures in all states). The smallest blocking example in the animation is from this search.
- 16×16 leaf-spine, 1:1, 200 random permutations, max-min fair sharing by progressive filling: hashing (ECMP) mean 55.4% (5th–95th percentile 52.5–58.4), unluckiest flow mean 0.217; destination-mod-k 69.2%; edge coloring (König) 100%. Agreement with the figure often quoted for production Clos fabrics is a hint, not validation.

## Tori (scene 8)
- Diameter n·⌊k/2⌋ (mesh n(k−1)); torus bisection 2k^(n−1) links; β = 4/k (mesh 2/k). Checked against BFS and brute-force cuts on small instances. The β-vs-N chart uses k = N^(1/n), so it interpolates smoothly and passes 1 for the 5-D curve where k < 4 (labeled on the slide).
- 8×8×8: β 0.5, diameter 12. 16³: β 0.25, diameter 24. 16×16×32: β 0.125, diameter 32.
- All-to-all, dimension-order routing, 8×8: torus load uniform, saturation 0.984 of injection; mesh max/mean 1.333, saturation 0.492.
- Deadlock: a channel-dependency cycle without virtual channels; none with a dateline and 2 VCs. Checked on k = 4, 5 (n = 1) and k = 4 (n = 2).
- Blue Gene/L: 64×32×32 = 65,536 nodes, 6 links, 1.4 Gb/s per direction per link (IBM RC22851); my cut across the long axis is 2,048 links = 358.4 GB/s per direction, versus the paper's 360. Separate tree network.
- K computer: 24×18×16 groups of 2×3×2 = 82,944 nodes; users see a virtual 3-D torus (e.g. 54×48×32). Tofu D: 6 TNIs, 6.8 GB/s per link (secondary sources).
- TPU v4 (arXiv 2304.01433): 4,096 chips = 64 cubes of 4×4×4; optical circuit switches under 5% of system cost and 3% of power; twisted torus 1.63x and 1.31x all-to-all throughput on two slice shapes; without OCS, host availability must be 99.9%.
- My fragmentation picture (41 free nodes, no free 3×3 or 4×4 box, with or without wraparound) is checked by code, but the busy pattern is invented for illustration.

## Hypercube and HyperX (scene 9)
- Hypercube: diameter log₂N, bisection N/2, β = 1; the 13-cube for 8,192 nodes has radix 14 (13 links + 1 host port) and 6.5 cables per endpoint.
- HyperX: radix T + ΣK(S−1) ≤ R; β = K·S/(2T); diameter ≤ L; S = 2 is a hypercube; L = 1 is a full mesh. 16×16, T = 8 / 16 / 32: radix 38 / 46 / 62, 2,048 / 4,096 / 8,192 terminals, β 1 / 0.5 / 0.25. The paper's savings claim was against the flattened butterfly; it says a folded Clos is generally more efficient at full bisection.
- Domke et al., SC19: one machine built with a 3-level fat tree plane and a 12×8 HyperX plane; with pattern-aware routing the HyperX can challenge or outperform the fat tree.

## Dragonfly (scene 10)
- Router radix k = p + a + h − 1; N = a·p·(a·h + 1); groups g = a·h + 1; balanced a = 2p = 2h; minimal path local–global–local. Slingshot's largest configuration in the SC20 paper: a = 32, p = 16, h = 17, radix 64, 545 groups, 279,040 endpoints (addressing limits real systems to 511 groups).
- Kim et al.'s cost claim: about 20% below a flattened butterfly and 52% below a folded Clos at 16K+ nodes, in their 2008 cost model. The bars on screen are drawn from those two percentages.
- My model, a = 4, p = h = 2 (9 groups, 72 machines): minimal routing on the adversarial pattern 1/(a·p) = 0.125; Valiant routing 0.4375; uniform traffic 1.0 (minimal) and 0.555 (Valiant). The group-split β of 0.504 in the comparison table is an upper bound, not a true bisection.
- Dragonfly paper: local-queue-only UGAL gave limited throughput and high latency on adversarial traffic. Slingshot estimates path load from information carried in acknowledgments, biased to minimal. Dragonfly+ (IETF draft): leaf-spine groups. Slim Fly: diameter 2, about 25% better cost-effectiveness, authors' model.

## Comparison (scene 11)
- All six rows are built as graphs and measured; values on screen come from `data/results.json` (`compare`). Diameter is router-to-router hops.

## Collectives and placement (scenes 12–13)
- α–β model, ring all-reduce 2(p−1)α + 2(p−1)/p · n/B, Rabenseifner 2·lg p · α + the same bandwidth term: standard model (Thakur et al.) with my derivation. p = 1,024, α = 2 µs: ring startup 4.09 ms vs 40 µs. Recursive doubling vs Rabenseifner crossover about 128 KiB on the model's grid.
- Patarasuk & Yuan: ring is bandwidth-optimal on tree-connected networks with one port per node. NCCL 2.4: ring latency is linear in the number of GPUs; NVIDIA reports up to 180x lower latency for double binary trees at 24K GPUs on Summit (NVIDIA's measurement).
- Placement model (idealized fluid spray across spines, no hash collisions; 32 hosts per leaf, 16 leaves, 512 ranks), 4:1: ring in order 1.0x; ring shuffled 4.0x; recursive halving in order 3.82x; halving with big messages kept near 1.09x. 2:1 and 8:1 are in `results.json`.
- Slurm: tree topology (`topology.conf`, `--switches=count[@max-time]`, time in minutes), block topology for contiguous blocks, a torus plugin, multi-topology configuration. Bhatele et al. (SC11): hot spots on a few links. Yang et al. (SC16): a "bully" effect and a hybrid contiguous/non-contiguous placement. Slingshot 1.3x vs 93x worst-case slowdown is the authors' benchmark.

## Proprietary interconnects (scene 14)
- TOP500, June 2026 (re-fetched): #1 LineShine ("the proprietary LingQi interconnect"), #2 El Capitan, #3 Frontier, #4 Aurora, #6 HPC7, #8 HPC6 and #10 Alps on Slingshot-11 (six of ten); #5 JUPITER Booster on quad-rail NVIDIA InfiniBand NDR200; #7 Eagle on NVIDIA InfiniBand NDR; #9 Fugaku on Tofu interconnect D.
- Myrinet (Myricom, first generation 1994; 141 systems = 28.2% of the June 2005 list, per Myricom; one system by June 2014; assets sold 2013). Quadrics QsNet (Meiko heritage, fat tree; six of the ten fastest in June 2003; closed 29 June 2009). Blue Gene L/P 3-D torus, Q 5-D torus. Cray Aries (2012, dragonfly, "at most five hops," as quoted by HPCwire from Cray). Omni-Path (Intel 2015, Trinity and Cori, dropped by 2019; Cornelis Networks spun out 2020, CN5000 at 400 Gb/s in 2025).
- LineShine's "multi-rail fat tree, 1.6 Tb/s per node" is from a single outlet; one second source I tried would not load. The narration says so.
- "My read" at the end of that scene is interpretation, labeled as such on screen and in the narration.

## Not verified / deliberately hedged
- LineShine interconnect topology and per-node bandwidth (single outlet).
- Seitz's role in Myricom (omitted).
- Exact Gemini (Cray XE/XK) topology details (the narration only says "three-dimensional torus").
- The "Close" scene's bar chart is an illustrative shape only (labeled on screen); only the 0.34 end value matches my model.
- No benchmark in this video is a measurement of real hardware by me.

## About the video itself
- Narration is Kokoro-82M (ONNX), voice `af_heart`. It is synthetic and I could not audition it by ear; pronunciation was checked through the phonemizer, with phonetic respellings in `src/script.py` (shown as `{Display|spoken}`).
- Visuals are 2D, drawn with skia-python at 3840×2160, 30 fps, in a Tufte-leaning style (ET Book typography, range-frame axes, direct labels, sources on every slide) with 3Blue1Brown-style motion (smooth easing, progressive drawing, glow). Diagrams are schematic and not to scale, except where an axis says otherwise.
- Subtitles in the video and in `narration.srt` are the narration text, not captions of the on-screen text.
