# InfiniBand vs high-bandwidth Ethernet: first-principles notes (companion to the explainer video)

Everything below is either (a) checked against a fetched source, (b) derived by me and reproducible from `src/model_numbers.py`, or (c) flagged. "Checked" means a source said it; it does not mean I independently measured it.

## Verification status at a glance
- **Re-checked against primary text late in the build:** Zhu et al. (DCQCN, SIGCOMM 2015) CPU / latency / victim-flow numbers; Guo et al. (SIGCOMM 2016) 60 % ECMP figure and deadlock mechanism; NVIDIA DGX SuperPOD H100 reference architecture (SU size, leaf/spine counts, separate fabrics); Ultra Ethernet 1.1 release date (Network World: 12 October 2026).
- **From earlier research in this build, not re-fetched in the final pass:** history dates, TOP500 counts, IBTA count, Meta clusters, Frontier parameters, QM9700 power, Slingshot 1.3x / 93x, SHARP latencies, Tomahawk 6 bandwidth, JUPITER, 800G / 1.6T status. Treat these as "sourced, worth one more look before you cite them."
- **Modeled by me (not measurements):** ECMP / routing throughput percentages, serialization, buffer, header-efficiency and topology-sizing arithmetic.
- **Vendor claims I could not verify:** Nvidia "up to 9x" for SHARPv4.

## Corrections I made during the build (so you can see the mistakes)
- A fetch summary said the QM9700 has "32 ports". NVIDIA documents 64 NDR ports through 32 twin-port OSFP cages. The 51.2 Tb/s figure counts both directions (25.6 Tb/s per direction).
- My first narration said light travels "sixteen meters" during a 4 KiB packet at 400 Gb/s. 81.92 ns / 4.9 ns per metre = 16.7 m, so it now says seventeen.
- I wrote that InfiniBand headers cost "about half a percent". 26 B / (4096 + 26) = 0.63 %. It now says "about six tenths of a percent", and RoCEv2 is 1.5 %. The difference is under one percentage point either way.
- An on-screen citation attributed the victim-flow numbers (20 -> 10 -> 4.5 Gb/s) and the CPU / 2 KB latency numbers to Guo et al. 2016. They are in Zhu et al. 2015 (Section 2.1, Fig. 1; Section 2.2). Fixed on screen. Guo 2016 is the source for the PFC deadlock and the ~60 % ECMP result.
- I had narrated "each [adapter] goes to a different leaf switch" for the SuperPOD. NVIDIA's page says the fabric is rail-aligned and that same-rail traffic is one hop away, but does not spell out the port-to-leaf wiring. The narration now says "rail-aligned".
- The 144-port two-level example is the XDR Quantum-X800 Q3400 (10,368 adapters), not Quantum-2. A footer said Quantum-2; fixed.
- TOP500 lists InfiniBand NDR400 (48) and NDR (35) as separate families, so no single InfiniBand family beats Slingshot-11 (57). Together they are about 16 % of systems.
- CACM 1976 volume / issue numbers disagreed between two fetches. The video cites "CACM 1976" only.

## History
- Ethernet: Metcalfe & Boggs, CACM 1976. Shared coax, about 3 Mb/s, carrier sense with collision backoff.
- Late 1990s: shared I/O buses (arbitration, shared failure domain, processor-stalling loads). 1999: Next Generation I/O (Intel) and Future I/O (Compaq, IBM, HP) merge into the InfiniBand Trade Association; spec 1.0 in October 2000.
- Not the universal server bus; PCI Express took over inside the box. Virginia Tech System X (2003) used InfiniBand.
- RoCE 2010; RoCEv2 (routable, UDP 4791) 2014. Nvidia-Mellanox deal announced 2019. Ultra Ethernet 1.0 in 2025; 1.1 on 12 October 2026.
- I did not verify a Pfister-era book/paper citation, so none appears on screen.

## Why RDMA, and why that is not the same as InfiniBand
- Zhu et al. 2015, 40 Gb/s NICs: 4 MB messages, TCP uses over 20 % of CPU cycles across all cores; RDMA client under 3 %, server almost none. 2 KB messages: TCP 25.4 us, RDMA 1.7 us (read/write) and 2.8 us (send). One testbed, one study; not a general law.
- Verbs life of a message: register memory (pinned, lkey/rkey), queue pair, work request + doorbell, adapter DMA, packets up to 4 KiB (MTU), remote adapter writes the buffer (one-sided: remote CPU not involved), ACK/sequence numbers/retransmit in reliable mode, completion queue entry, application polls.
- Queue pair numbers are 24 bits, so about 16 million per adapter (spec limit; real adapters support fewer).

## The three things left once Ethernet has RDMA
1. **Loss.** InfiniBand: credit-based, per-virtual-lane link-level flow control; a packet is sent only if the receiver advertised buffer space. Ethernet normally drops on overflow; RoCE needs PFC, which pauses a whole priority class on a link.
   - Zhu 2015 victim flow: expected 20 Gb/s, got 10; with two more senders the median fell to 4.5 Gb/s (testbed).
   - Guo 2016 deadlock: incomplete ARP / MAC entries caused lossless traffic to flood, forming a pause-frame cycle across four switches. Microsoft chose to drop lossless packets with incomplete ARP entries.
   - Caveats I put in the video: credit loops can deadlock InfiniBand too (routing must avoid them), and buffers must cover the round trip. 400 Gb/s x 2 x 100 m x 4.9 ns/m = 49 kB, propagation only (a lower bound; ignores turnaround).
2. **Routing.** One master subnet manager discovers the fabric, assigns 16-bit LIDs, computes routes (OpenSM engines: min-hop, up/down, ftree, dfsssp, lash, nue) and programs linear forwarding tables. Ethernet usually hashes flows over equal-cost paths (ECMP).
   - Guo 2016, production Clos (two podsets, 40GbE, 3,074 RDMA connections): 60 % of the 5.12 Tb/s leaf-spine capacity, attributed to ECMP hash collisions.
3. **Arithmetic.** SHARP in-network reduction. Original paper, 128 hosts: 8 B all-reduce 6 us -> under 3 us; 4 KiB 47 -> 14.5 us. Authors' numbers on pre-release hardware tuned for low noise: a best case. The paper's text and table disagreed in places; I used the table's headline figures.
   - Nvidia claims up to 9x for the fourth generation. Vendor claim, unverified.
- Header overhead is a wash: InfiniBand 26 B (LRH 8 + BTH 12 + ICRC 4 + VCRC 2) = 0.63 % at 4 KiB; RoCEv2 62 B (Slingshot paper) to 66 B (Hoefler et al.) = 1.5 %.

## Congestion control
- InfiniBand marks packets (FECN) and the receiver notifies the sender (BECN); RoCE uses ECN + DCQCN (rate cut by up to half per notification, then recovery in steps); PFC remains the backstop (DCQCN authors say so).
- Slingshot (HPE): hardware tracks in-flight packets per endpoint pair and applies backpressure only to the sources causing congestion. Paper-reported worst-case victim slowdown 1.3x vs 93x on Cray's previous network (authors' measurements).

## Topology
- Fat tree (full bisection, k-port switches): 2 levels k^2/2 hosts with 1.5k switches; 3 levels k^3/4 hosts with 5k^2/4 switches. k = 64: 2,048 hosts / 96 switches; 65,536 hosts / 5,120 switches.
- Cross-checks: 144^2 / 2 = 10,368 (Quantum-X800 Q3400 datasheet says 10,368). Al-Fares k = 48 -> 27,648 hosts, 2,880 switches (their paper's numbers).
- DGX SuperPOD H100 (NVIDIA docs): SU designed for 32 nodes (31 listed in the 1-SU row, one slot goes to UFM); 8 leaf switches per SU; spines 4 (1 SU), 8 (2 SU), 16 (3 SU), 16 (4 SU); rail-aligned, same-rail traffic one hop; storage, in-band and out-of-band management are separate fabrics.
- Dragonfly (Kim, Dally, Scott, Abts, ISCA 2008): N = a*p*(a*h + 1); balanced a = 2p = 2h. Example p = h = 2, a = 4 -> 9 groups, 72 terminals (computed).
- Frontier (Slingshot dragonfly): p = 16, a = 32, h = 16 gives 63-port switches (16 + 31 + 16). 74 groups, 4 links per group pair (73 x 4 = 292 of 512 global ports used per group). Node counts: 74 x 128 = 9,472 versus a commonly quoted 9,408; the sources disagree, so the video says "up to 128 nodes per group" and avoids a total.
- Minimal routing is at most three switch hops (local, global, local); adversarial patterns squeeze through one global link; hence Valiant routing and adaptive (UGAL-style) routing. Dragonfly+ (each group a fat tree): JUPITER at Juelich, NDR200 InfiniBand.

## Hardware
- ConnectX-7: 400 Gb/s per port, PCIe Gen5 x16 ~63 GB/s per direction = ~504 Gb/s. 800 Gb/s does not fit Gen5; ConnectX-8 uses Gen6 (x16 ~121 GB/s, ~968 Gb/s).
- QM9700: 1U, 64 x 400 Gb/s ports via 32 twin-port OSFP cages; about 750 W with passive copper, up to 1,700 W with active cables (vendor figures).
- Spec-sheet conventions: Nvidia's 51.2 Tb/s counts both directions; Broadcom's Tomahawk 6 102.4 Tb/s counts one. Same footing: QM9700 = 25.6 Tb/s.
- Cable reach at 400G (typical vendor values): passive copper ~3 m, active copper ~5 m, multimode optics ~50 m, single-mode 500 m and up.
- XDR doubles lane rate to 200 Gb/s (800 Gb/s per port). Ethernet 800G standardized in 2024; 1.6T under IEEE work.

## In the larger HPC universe
- Lustre LNet has InfiniBand and TCP drivers; BeeGFS uses ibverbs with TCP fallback; Frontier's Orion file system is on Slingshot. See the companion Lustre, GPFS and BeeGFS notes.
- TOP500, June 2026 (as I fetched it): Slingshot-11 57 systems; 100G Ethernet 56; InfiniBand NDR400 48 + NDR 35 (about 16 %). The IBTA, which has a stake, counts 293 InfiniBand systems across all generations. Different groupings.
- Meta (2024): two clusters of 24,000 GPUs, one RoCE, one InfiniBand; large jobs ran on both without network bottlenecks after tuning (Gangidi et al., SIGCOMM 2024).
- Ultra Ethernet 1.0 (June 2025), 1.1 (12 October 2026). IBTA's next release includes a multipath transport for RoCE (MRC).

## My own models (toy models, not measurements)
- `src/model_numbers.py`, section 3: leaf-spine, max-min fair sharing by progressive filling (self-tested on three hand-checkable cases), unit-capacity links, 16 leaves x 16 hosts, 1:1, 300 random permutations.
  - Flow-level hashing (ECMP), random permutation: 55.6 % of ideal (5th-95th percentile 52.7-58.9).
  - Destination-mod-k table, random permutation: 69.2 %; on the shift pattern it is tuned for: 100 %.
  - ECMP on the shift pattern: 64.4 %.
  - Ideal per-packet spraying: 100 % by construction (every link carries exactly one flow-equivalent). Real adaptive routing gets less.
  - Sensitivity of flow-level ECMP to fabric size (random permutation): 8x8 = 61 %, 16x16 = 56 %, 32x32 = 53 % (fewer trials at 32x32; the trend is the point).
- Agreement with Microsoft's ~60 % is a hint, not validation: different topology, traffic and NICs.

## Not verified / deliberately hedged
- No same-hardware, fair, at-scale benchmark of InfiniBand vs Ethernet was found. The comparison is architectural plus cited anecdotes.
- Exact adapter-to-leaf wiring in the SuperPOD (NVIDIA's page is silent; narration says only "rail-aligned").
- Exact node total for Frontier (9,408 vs 9,472).
- Items listed above under "from earlier research... not re-fetched".

## About the video itself
- Narration is Kokoro-82M (ONNX, Apache-2.0) with voice af_heart. It is synthetic and I could not audition it by ear; pronunciation was checked through the phonemizer, with phonetic spellings for acronyms (see `src/script.py`).
- Visuals are 2D, drawn with skia-python at 3840x2160, 30 fps, in a Tufte-leaning style (ET Book typography, range-frame axes, direct labels, sources on every slide) with 3Blue1Brown-style motion (smooth easing, progressive drawing, glow). Diagrams are schematic, not to scale, except where an axis says otherwise.
