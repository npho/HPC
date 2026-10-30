"""Scenes 12-15: hardware, universe, close, refs"""
import math
from engine import *


# ---------------------------------------------------------------------------------------------- hardware
class Hardware(Scene):
    id = "hardware"
    title = "Hardware: adapter, switch, cable"
    sources = ("NVIDIA ConnectX-7/-8 and QM9700 documentation; Broadcom Tomahawk 6 release; PCIe throughput per the PCIe table (x16, per direction: Gen5 63.0 GB/s, Gen6 ~121 GB/s).  "
               "Cable reach figures are typical vendor values at 400G.  Arithmetic in src/model_numbers.py")

    def draw(self, c, t):
        B = self.B
        # ---- beat 0 : adapter in a slot
        if t < B(1) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.5))
            rect(c, 300, 600, 1000, 90, fill=BG2, stroke=FAINT, sw=1.2, r=4, a=a)
            text(c, "server motherboard", 320, 590, 22, DIM, "serifi", "l", a)
            rect(c, 760, 560, 240, 20, fill=BG, stroke=DIM, sw=1.4, a=a)
            text(c, "PCIe slot", 880, 548, 20, DIM, "sans", "c", a)
            ca = a * P(t, B(0) + 2, B(0) + 3.5)
            y = 330 + 230 * (1 - ease_out(P(t, B(0) + 2, B(0) + 4.5, lin)))
            rect(c, 780, y - 160, 200, 230, fill=BG2, stroke=IB, sw=2, r=6, a=ca)
            text(c, "ConnectX-7", 880, y - 100, 28, IB, "serif", "c", ca)
            text(c, "400 Gb/s per port", 880, y - 66, 20, DIM, "serifi", "c", ca)
            for k in range(2): rect(c, 1000, y - 130 + k * 70, 90, 50, stroke=IB, sw=1.6, r=3, a=ca)
            text(c, "port", 1045, y - 98, 18, IB, "sans", "c", ca * P(t, B(0) + 5, B(0) + 6))
            text(c, "a host adapter: where RDMA lives in hardware", 960, 860, 30, INK, "serifi", "c", a * P(t, B(0) + 6, B(0) + 7.5))
        # ---- beat 1 : PCIe arithmetic
        if B(1) - 0.3 < t < B(2) + 0.5:
            a = P(t, B(1), B(1) + 1.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            text(c, "the slot has to keep up: PCIe x16, per direction", 960, 250, 34, INK, "serif", "c", a)
            gx, gy, gh = 560, 820, 460
            axis_range_frame(c, gx - 20, gy - gh, gx + 900, gy, a)
            vals = [("Gen5 x16", 504, IB, "63 GB/s = 504 Gb/s"), ("Gen6 x16", 968, GOOD, "~121 GB/s = ~968 Gb/s")]
            sc_ = gh / 1000.0
            for i, (nm, v, colr, lab) in enumerate(vals):
                ts = B(1) + 1.5 + i * 5
                h = v * sc_ * P(t, ts, ts + 1.4)
                x = gx + 80 + i * 330
                rect(c, x, gy - h, 190, h, fill=colr, a=a)
                text(c, lab, x + 95, gy - h - 14, 22, colr, "sansm", "c", a * P(t, ts + 1, ts + 2))
                text(c, nm, x + 95, gy + 34, 24, DIM, "serif", "c", a)
            for v, lab, colr in [(400, "400 Gb/s: fits", GOOD), (800, "800 Gb/s: does not fit Gen5", BAD)]:
                la = a * P(t, B(1) + (5 if v == 400 else 8), B(1) + (6 if v == 400 else 9))
                line(c, gx - 20, gy - v * sc_, gx + 900, gy - v * sc_, colr, 1.8, la, dash=(8, 6))
                text(c, lab, gx + 900, gy - v * sc_ - 10, 22, colr, "serifi", "r", la)
            text(c, "ConnectX-8 moves to PCIe Gen6", 1500, 500, 24, DIM, "serifi", "c", a * P(t, B(1) + 10, B(1) + 11))
        # ---- beat 2 : QM9700
        if B(2) - 0.3 < t < B(3) + 0.5:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.5))
            x0, y0, w, h = 260, 420, 1400, 110
            rect(c, x0, y0, w, h, fill=BG2, stroke=INK, sw=2, r=6, a=a)
            text(c, "QM9700  ·  1U", x0, y0 - 24, 30, IB, "serif", "l", a)
            for k in range(32):
                cx = x0 + 40 + (k % 16) * 82; cy = y0 + 18 + (k // 16) * 48
                on = P(t, B(2) + 2 + k * 0.06, B(2) + 2.5 + k * 0.06)
                rect(c, cx, cy, 64, 34, fill=BG, stroke=IB, sw=1.4, r=3, a=a * on)
                line(c, cx + 32, cy + 4, cx + 32, cy + 30, IB, 1.0, a * on * 0.7)
            text(c, "32 twin-port OSFP cages", 960, 600, 34, INK, "serif", "c", a * P(t, B(2) + 5, B(2) + 6))
            text(c, "=  64 ports at 400 Gb/s", 960, 650, 34, IB, "serif", "c", a * P(t, B(2) + 7, B(2) + 8))
            text(c, "~750 W with passive copper", 600, 780, 28, GOOD, "serifi", "c", a * P(t, B(2) + 10, B(2) + 11))
            text(c, "up to 1,700 W with active cables", 1300, 780, 28, ETH, "serifi", "c", a * P(t, B(2) + 12, B(2) + 13))
        # ---- beat 3 : spec-sheet conventions
        if B(3) - 0.3 < t < B(4) + 0.5:
            a = P(t, B(3), B(3) + 1.0) * (1 - self.Pb(t, 4, 0.0, 0.5))
            text(c, "a word on spec sheets", 960, 250, 40, INK, "serifi", "c", a)
            bx, by = 480, 380
            sc_ = 1000 / 105.0
            rows = [("QM9700 as NVIDIA quotes it", 51.2, ETH, "counts both directions"), ("Tomahawk 6 as Broadcom quotes it", 102.4, SLING, "counts one direction"), ("QM9700, same footing", 25.6, IB, "per direction")]
            for i, (nm, v, colr, note) in enumerate(rows):
                ts = B(3) + 2 + i * 4
                yy = by + i * 130
                w = v * sc_ * P(t, ts, ts + 1.4)
                rect(c, bx, yy, w, 60, fill=colr, a=a)
                text(c, nm, bx - 20, yy + 28, 24, colr, "serif", "r", a)
                text(c, note, bx - 20, yy + 54, 18, DIM, "serifi", "r", a)
                text(c, f"{v:g} Tb/s", bx + w + 14, yy + 42, 30, colr, "serif", "l", a * P(t, ts + 1, ts + 2))
            text(c, "same word, different convention", 960, 840, 30, DIM, "serifi", "c", a * P(t, B(3) + 12, B(3) + 13))
        # ---- beat 4 : cable reach (log scale)
        if B(4) - 0.3 < t < B(5) + 0.5:
            a = P(t, B(4), B(4) + 1.0) * (1 - self.Pb(t, 5, 0.0, 0.5))
            text(c, "cables set the layout", 960, 250, 40, INK, "serif", "c", a)
            items = [("passive copper (DAC)", 3, GOOD), ("active copper", 5, GOOD), ("multimode optics", 50, ETH), ("single-mode optics", 500, IB)]
            bx, by = 560, 380
            for i, (nm, m, colr) in enumerate(items):
                ts = B(4) + 1.5 + i * 2.2
                yy = by + i * 90
                w = (math.log10(m) + 0.2) * 300 * P(t, ts, ts + 1.2)
                rect(c, bx, yy, w, 50, fill=colr, a=a)
                text(c, nm, bx - 20, yy + 34, 26, colr, "serif", "r", a)
                text(c, (f"{m} m" if m < 500 else "500 m and up"), bx + w + 14, yy + 34, 26, colr, "sansm", "l", a * P(t, ts + 1, ts + 2))
            text(c, "log scale", bx + 1000, by + 340, 18, FAINT, "serifi", "r", a)
            text(c, "copper inside the rack, optics between racks", 960, 830, 34, INK, "serifi", "c", a * P(t, B(4) + 10, B(4) + 11.5))
        # ---- beat 5 : generations
        if B(5) - 0.3 < t:
            a = P(t, B(5), B(5) + 1.0)
            text(c, "the same curve, on both sides", 960, 250, 38, INK, "serif", "c", a)
            gens = [("NDR", "400 Gb/s", "100G lanes (4x/port 400G)", IB, 400), ("XDR", "800 Gb/s", "200 Gb/s per lane", IB, 800)]
            for i, (nm, rate, d, colr, v) in enumerate(gens):
                ts = B(5) + 1.5 + i * 3
                aa = a * P(t, ts, ts + 1)
                x = 140 + i * 380
                rect(c, x, 360, 340, 200, fill=BG2, stroke=colr, sw=1.4, r=8, a=aa)
                text(c, "InfiniBand " + nm, x + 170, 420, 30, colr, "serif", "c", aa)
                text(c, rate, x + 170, 490, 48, INK, "serif", "c", aa)
            text(c, "XDR doubles the lane rate to 200 Gb/s", 140, 640, 24, DIM, "serifi", "l", a * P(t, B(5) + 4, B(5) + 5))
            for i, (nm, rate, ts) in enumerate([("800G standardized", "2024", B(5) + 7), ("1.6 T in IEEE work", "in progress", B(5) + 10)]):
                aa = a * P(t, ts, ts + 1)
                x = 1000 + i * 380
                rect(c, x, 360, 340, 200, fill=BG2, stroke=ETH, sw=1.4, r=8, a=aa)
                text(c, "Ethernet", x + 170, 420, 30, ETH, "serif", "c", aa)
                text(c, nm, x + 170, 490, 28, INK, "serif", "c", aa)
                text(c, rate, x + 170, 530, 22, DIM, "serifi", "c", aa)


# ---------------------------------------------------------------------------------------------- universe
class Universe(Scene):
    id = "universe"
    title = "Where it fits: the larger HPC universe"
    sources = ("TOP500, June 2026 list (interconnect families as TOP500 lists them: Slingshot-11 57, 100G Ethernet 56, InfiniBand NDR400 48 and NDR 35 = ~16 %); IBTA press count of 293 InfiniBand systems is across all generations.  "
               "Meta: Gangidi et al., SIGCOMM 2024.  UEC 1.0 (2025).  Lustre LNet, BeeGFS docs, OLCF Frontier docs.")

    def draw(self, c, t):
        B = self.B
        # ---- beat 0 : four networks
        if t < B(1) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.5))
            nets = [("compute fabric", "collectives run here", IB, 0), ("storage fabric", "usually separate", GOOD, 1), ("in-band management", "ordinary Ethernet", ETH, 2), ("out-of-band management", "isolated", DIM, 3)]
            # nodes row
            for n in range(6):
                x = 400 + n * 220
                rect(c, x - 55, 760, 110, 70, fill=BG2, stroke=INK, sw=1.4, r=5, a=a)
                text(c, "node", x, 802, 20, DIM, "sans", "c", a)
            for name, d, colr, i in nets:
                ts = B(0) + 2.0 + i * 2.6
                aa = a * P(t, ts, ts + 1.0)
                yy = 300 + i * 100
                line(c, 300, yy, 1620, yy, colr, 3, aa)
                text(c, name, 300, yy - 14, 30, colr, "serif", "l", aa)
                text(c, d, 1620, yy - 14, 22, DIM, "serifi", "r", aa)
                for n in range(6):
                    x = 400 + n * 220
                    line(c, x - 30 + i * 20, yy, x - 30 + i * 20, 760, colr, 1.4, aa * 0.8)
        # ---- beat 1 : file systems share the RDMA machinery
        if B(1) - 0.3 < t < B(2) + 0.5:
            a = P(t, B(1), B(1) + 1.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            text(c, "file systems ride the same machinery", 960, 250, 38, INK, "serif", "c", a)
            rows = [("Lustre", "LNet: an InfiniBand driver and a TCP one", B(1) + 2), ("BeeGFS", "ibverbs, falling back to TCP", B(1) + 5.5), ("Frontier’s Orion", "sits directly on Slingshot", B(1) + 9)]
            for i, (nm, d, ts) in enumerate(rows):
                aa = a * P(t, ts, ts + 1.0)
                yy = 380 + i * 130
                rect(c, 300, yy, 1320, 90, fill=BG2, stroke=FAINT, sw=1.2, r=6, a=aa)
                text(c, nm, 340, yy + 56, 34, IB if i < 2 else SLING, "serif", "l", aa)
                text(c, d, 700, yy + 54, 28, INK, "serifi", "l", aa)
        # ---- beat 2 : TOP500
        if B(2) - 0.3 < t < B(3) + 0.5:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.5))
            text(c, "TOP500, June 2026: interconnect family", 960, 250, 36, INK, "serif", "c", a)
            tag(c, "COUNTS BY DIFFERENT GROUPINGS", 700, 295, HI, a * P(t, B(2) + 14, B(2) + 15), 16)
            bx, by = 560, 360
            rows = [("Slingshot-11 (HPE)", 57, SLING, "57 systems"), ("100G Ethernet", 56, ETH, "56 systems"),
                    ("InfiniBand NDR400", 48, IB, "48 systems"), ("InfiniBand NDR", 35, IB, "35 systems")]
            for i, (nm, v, colr, lab) in enumerate(rows):
                ts = B(2) + 3 + i * 2.6
                w = v * 9 * P(t, ts, ts + 1.2)
                yy = by + 60 + i * 84
                rect(c, bx, yy, w, 50, fill=colr, a=a)
                text(c, nm, bx - 18, yy + 35, 26, colr, "serif", "r", a)
                text(c, lab, bx + w + 14, yy + 35, 24, colr, "sansm", "l", a * P(t, ts + 1, ts + 2))
            ba = a * P(t, B(2) + 11, B(2) + 12.5)
            line(c, 1190, by + 60 + 2 * 84, 1190, by + 60 + 3 * 84 + 50, IB, 2, ba)
            text(c, "together: about 16 % of systems", 1206, by + 60 + 2.5 * 84 + 30, 24, IB, "serifi", "l", ba)
            ia = a * P(t, B(2) + 15, B(2) + 16.5)
            text(c, "IBTA, which has an obvious stake, counts 293 InfiniBand systems across all generations", 960, 760, 26, DIM, "serifi", "c", ia)
            text(c, "different groupings, so all of it can be true", 960, 810, 28, INK, "serif", "c", a * P(t, B(2) + 20, B(2) + 21.5))
        # ---- beat 3 : Meta
        if B(3) - 0.3 < t < B(4) + 0.5:
            a = P(t, B(3), B(3) + 1.0) * (1 - self.Pb(t, 4, 0.0, 0.5))
            text(c, "2024: two clusters of 24,000 GPUs at Meta", 960, 300, 40, INK, "serif", "c", a)
            for i, (nm, colr) in enumerate([("RoCE", ETH), ("InfiniBand", IB)]):
                ts = B(3) + 3 + i * 3
                aa = a * P(t, ts, ts + 1)
                x = 560 + i * 800
                for r in range(6):
                    for k in range(8):
                        rect(c, x - 140 + k * 36, 430 + r * 34, 26, 20, fill=colr, fa=aa * 0.55, r=3, a=aa)
                text(c, nm, x, 700, 40, colr, "serif", "c", aa)
            text(c, "large jobs ran on both without network bottlenecks — after tuning", 960, 840, 28, DIM, "serifi", "c", a * P(t, B(3) + 9, B(3) + 10.5))
        # ---- beat 4 : not settled
        if B(4) - 0.3 < t:
            a = P(t, B(4), B(4) + 1.0)
            text(c, "and it is not settling", 960, 260, 44, INK, "serif", "c", a)
            items = [("Slingshot", "Ethernet-compatible", SLING, 2), ("Ultra Ethernet 1.0", "June 2025;  1.1 this month", ETH, 6), ("IBTA’s next release", "multipath transport for RoCE", IB, 11)]
            for i, (nm, d, colr, dt) in enumerate(items):
                aa = a * P(t, B(4) + dt, B(4) + dt + 1.0)
                x = 330 + i * 480
                rect(c, x - 200, 400, 400, 200, fill=BG2, stroke=colr, sw=1.4, r=8, a=aa)
                text(c, nm, x, 480, 32, colr, "serif", "c", aa)
                para(c, d, x - 160, 540, 320, 24, DIM, "serifi", 1.3, aa)


# ---------------------------------------------------------------------------------------------- close
class Close(Scene):
    id = "close"
    title = "So, honestly"
    sources = ""

    def draw(self, c, t):
        B = self.B
        if t < B(2) + 0.5:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 2, 0.0, 0.5))
            rich(c, [("RDMA", INK), (", not ", DIM), ("InfiniBand", IB), (",", DIM)], 960, 380, 64, "serif", a, "c")
            text(c, "is what removed the software tax", 960, 460, 48, INK, "serif", "c", a * P(t, B(0) + 3.5, B(0) + 5))
            text(c, "and Ethernet has it", 960, 540, 48, ETH, "serif", "c", a * P(t, B(0) + 6, B(0) + 7.5))
            # two columns
            if t > B(1):
                ca = P(t, B(1), B(1) + 1.0)
                rect(c, 0, 300, LW, 560, fill=BG, fa=ca)
                cols = [("InfiniBand still offers", IB, ["an end-to-end design", "credit-based links", "a central routing brain", "in-network reduction", "a long record of tuning at scale"], B(1) + 2),
                        ("Ethernet offers", ETH, ["an open ecosystem", "enormous switch radix", "a standards effort aimed squarely at those gaps"], B(1) + 12)]
                for ci, (h, colr, items, ts) in enumerate(cols):
                    x = 330 + ci * 700
                    text(c, h, x, 400, 38, colr, "serif", "l", ca * P(t, ts - 1, ts))
                    for k, it in enumerate(items):
                        text(c, it, x, 470 + k * 56, 28, INK, "serifi", "l", ca * P(t, ts + k * 1.8, ts + k * 1.8 + 0.8))
        if t > B(2) - 0.3:
            a = P(t, B(2), B(2) + 1.0) * (1 - self.Pb(t, 3, 0.0, 0.6))
            text(c, "what I couldn’t find", 960, 280, 36, DIM, "serifi", "c", a)
            text(c, "a fair, same-hardware benchmark of the two, at scale", 960, 350, 40, INK, "serif", "c", a * P(t, B(2) + 2, B(2) + 3))
            text(c, "so measure your own workload", 960, 440, 40, HI, "serif", "c", a * P(t, B(2) + 5, B(2) + 6))
            tools = [("latency, bandwidth", "perftest"), ("collectives", "NCCL tests · OSU micro-benchmarks"), ("watch for", "pause frames · retransmits · link flaps")]
            for i, (k, v) in enumerate(tools):
                aa = a * P(t, B(2) + 8 + i * 3, B(2) + 9 + i * 3)
                text(c, k, 880, 560 + i * 70, 28, DIM, "serifi", "r", aa)
                text(c, v, 910, 560 + i * 70, 28, INK, "mono", "l", aa)
        if t > B(3) - 0.3:
            a = P(t, B(3), B(3) + 1.0)
            text(c, "sources, and every number I modeled myself,", 960, 500, 40, INK, "serif", "c", a)
            text(c, "are in the notes that come with this video", 960, 556, 40, INK, "serif", "c", a * P(t, B(3) + 1, B(3) + 2))


# ---------------------------------------------------------------------------------------------- refs
class Refs(Scene):
    id = "refs"
    title = "Sources and what is modeled"
    sources = "Full notes, verification flags and the generating code ship with this video."
    extra_tail = 0.0

    LINES = [
        ("Ethernet", "Metcalfe & Boggs, CACM 1976"),
        ("InfiniBand", "InfiniBand Trade Association; Architecture Specification"),
        ("RDMA vs TCP, PFC, DCQCN", "Zhu et al., SIGCOMM 2015 (CPU, latency, victim flow)"),
        ("PFC deadlock, ECMP in production", "Guo et al., SIGCOMM 2016"),
        ("Ethernet & RDMA at hyperscale", "Hoefler et al., 2023 (header sizes)"),
        ("SHARP", "Graham et al. (original paper; authors’ best case)"),
        ("Slingshot", "De Sensi et al., SC20"),
        ("Fat tree / dragonfly", "Al-Fares et al., SIGCOMM 2008;  Kim, Dally, Scott, Abts, ISCA 2008"),
        ("Hardware", "NVIDIA QM9700, ConnectX, Quantum-X800 Q3400; DGX SuperPOD reference architecture; Broadcom Tomahawk 6"),
        ("Meta clusters", "Gangidi et al., SIGCOMM 2024"),
        ("Rankings", "TOP500, June 2026;  Ultra Ethernet Consortium 1.0"),
    ]

    def draw(self, c, t):
        for i, (k, v) in enumerate(self.LINES):
            a = P(t, 1.0 + i * 0.35, 1.8 + i * 0.35)
            text(c, k, 520, 200 + i * 56, 24, IB, "serif", "r", a)
            text(c, v, 550, 200 + i * 56, 24, INK, "serifi", "l", a)
        a = P(t, 5.5, 6.5)
        tag(c, "MODELED BY ME, NOT MEASURED", 96, 810, HI, a, 18)
        text(c, "ECMP / routing throughput (leaf-spine max-min model); all serialization, buffer, header and topology arithmetic", 96, 850, 24, INK, "serifi", "l", a)
        tag(c, "VENDOR CLAIM, UNVERIFIED", 96, 910, BAD, a * P(t, 7, 8), 18)
        text(c, "Nvidia “up to 9×” for SHARPv4", 96, 950, 24, INK, "serifi", "l", a * P(t, 7, 8))
