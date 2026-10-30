"""Scenes 1-3: open, history, stack"""
import math, random
from engine import *

# ---------------------------------------------------------------------------------------------- open
class Open(Scene):
    id = "open"
    sources = "Arithmetic: 4096 B x 8 / 400 Gb/s = 81.9 ns;  light in glass ~ 4.9 ns/m (n ~ 1.47).  Reproduced in src/model_numbers.py"

    def draw(self, c, t):
        # ---- beat 0: a link, drawn across the screen
        y0 = 470
        a0 = 1 - self.Pb(t, 2, 0, 1.0)             # whole link stays until beat 2
        x0, x1 = 200, 1720
        pr = self.Pb(t, 0, 0.2, 2.5)
        if t < self.B(3):
            fade = 1 - self.Pb(t, 1, -0.8, -0.2)
            text(c, "400 Gb/s", 960, 300, 120, INK, "serif", "c", P(t, 0.9, 2.0) * fade)
            text(c, "the wire is almost never the problem", 960, 360, 34, DIM, "serifi", "c", self.Pb(t, 0, 3.0, 4.5) * fade)
        # ---- beat 1: ruler + packet + light pulse
        b1 = self.Pb(t, 1, 0.0, 1.0)
        if self.B(1) - 0.3 < t < self.B(2) + 1.0:
            fade = P(t, self.B(1) - 0.3, self.B(1) + 0.5) * (1 - self.Pb(t, 2, 0.2, 1.2))
            m2x = lambda m: 200 + m * 76.0
            y = 560
            line(c, m2x(0), y, m2x(20), y, IB, 3, fade)
            axis_range_frame(c, m2x(0), y + 40, m2x(20), y + 40, fade * 0.0)
            for m in range(0, 21, 5):
                line(c, m2x(m), y + 14, m2x(m), y + 26, FAINT, 1, fade)
                text(c, f"{m} m", m2x(m), y + 52, 20, DIM, "sans", "c", fade)
            # packet being clocked onto wire, time stretched (not to scale in time)
            u = self.Pb(t, 1, 3.2, 3.2 + 6.0, ease_io)
            pw = 110
            # serialization: packet occupies the first 0..16.7 m of wire at the end of the 82 ns
            head = m2x(16.718 * u)
            tail = m2x(0)
            if u > 0:
                rect(c, tail, y - 12, head - tail, 24, fill=ETH if False else IB, r=3, a=0.35 * fade)
                glow(c, head, y, 40, IB, 0.8 * fade * (1 if u < 1 else 0))
                circle(c, head, y, 7, fill=HI, a=fade)
            ns = 81.92 * u
            text(c, f"{ns:5.1f} ns", 960, 400, 84, HI if u < 1 else INK, "serif", "c", fade * P(t, self.B(1) + 2.2, self.B(1) + 3.2))
            text(c, "the time to clock one 4 KiB packet onto the wire", 960, 446, 28, DIM, "serifi", "c", fade * P(t, self.B(1) + 2.2, self.B(1) + 3.2))
            if u >= 1:
                text(c, "16.7 m", head, y - 36, 30, HI, "serif", "c", fade)
                text(c, "how far the first bit has travelled", head, y - 68, 21, DIM, "serifi", "c", fade)
            if t > self.B(1) + 0.4:
                rect(c, tail, y - 12, 0.0001, 24, fill=IB, a=0)
            margin_note(c, "Time is stretched roughly 70-million-fold here so you can watch it.", 1240, 790, 520, 22, DIM, P(t, self.B(1) + 3.5, self.B(1) + 4.5) * fade)
            text(c, "4096 B × 8 ÷ 400 Gb/s  =  81.9 ns", 200, 790, 28, INK, "mono", "l", fade * P(t, self.B(1) + 1.0, self.B(1) + 2.0))
            text(c, "light in glass ≈ 4.9 ns per metre", 200, 835, 28, DIM, "mono", "l", fade * P(t, self.B(1) + 1.6, self.B(1) + 2.6))
        # ---- beat 2: costs are elsewhere
        if self.B(2) + 0.4 < t < self.B(3) + 1.0:
            fade = P(t, self.B(2) + 0.4, self.B(2) + 1.2) * (1 - self.Pb(t, 3, 0.2, 1.2))
            names = [("software", "system calls, copies, interrupts"), ("buffers", "overflow, pause, drop"),
                     ("routing", "hashing, collisions, hot links"), ("queues", "everyone talks at once")]
            for i, (n, d) in enumerate(names):
                x = 240 + i * 410
                a = fade * P(t, self.B(2) + 3.0 + i * 3.0, self.B(2) + 4.0 + i * 3.0) if i < 4 else 0
                rect(c, x, 330, 330, 150, fill=BG2, stroke=FAINT, sw=1.2, r=6, a=a)
                text(c, n, x + 165, 395, 40, INK, "serif", "c", a)
                text(c, d, x + 165, 440, 19, DIM, "sansm" if False else "sans", "c", a)
            # fan-in: many senders -> one receiver, queue growing
            ax = P(t, self.B(2) + 6.0, self.B(2) + 7.5) * fade
            if ax > 0:
                cx, cy = 960, 760
                rnd = random.Random(3)
                for i in range(24):
                    ang = math.pi + (i / 23) * math.pi
                    sx, sy = cx + 560 * math.cos(ang) * 1.0, cy + 160 * math.sin(ang) * -1 - 30
                    sx = 400 + i * 49
                    sy = 600
                    line(c, sx, sy, cx, cy - 40, FAINT, 1, ax * 0.6)
                    circle(c, sx, sy, 6, fill=DIM, a=ax)
                    # packets flowing
                    for k in range(2):
                        u = (t * 0.35 + i * 0.13 + k * 0.5) % 1.0
                        px, py = lerp2((sx, sy), (cx, cy - 40), u)
                        circle(c, px, py, 3.2, fill=ETH, a=ax * 0.9)
                rect(c, cx - 90, cy - 40, 180, 40, fill=BG2, stroke=INK, sw=1.4, r=4, a=ax)
                fill = clamp(0.1 + 0.9 * P(t, self.B(2) + 7.5, self.B(3) + 0.5, lin))
                rect(c, cx - 84, cy - 34, 168 * fill, 28, fill=BAD if fill > 0.7 else ETH, r=3, a=ax * 0.9)
                text(c, "one egress queue", cx, cy + 28, 20, DIM, "serifi", "c", ax)
        # ---- beat 3: title card
        if t > self.B(3) - 0.2:
            a = P(t, self.B(3) - 0.2, self.B(3) + 1.0)
            rich(c, [("InfiniBand", IB), ("  and  ", DIM), ("Ethernet", ETH)], 960, 470, 92, "serif", a, "c")
            text(c, "networking for supercomputers, from first principles", 960, 540, 34, DIM, "serifi", "c", P(t, self.B(3) + 1.0, self.B(3) + 2.0))
            line(c, 660, 580, 660 + 600 * P(t, self.B(3) + 0.8, self.B(3) + 2.2), 580, FAINT, 1, 1.0, cap="butt")


# ---------------------------------------------------------------------------------------------- history
class History(Scene):
    id = "history"
    title = "Where it came from"
    sources = ("Metcalfe & Boggs, “Ethernet: Distributed Packet Switching for Local Computer Networks”, CACM (1976) · InfiniBand Trade Association (formed 1999; spec 1.0, Oct 2000) · "
               "RoCE (2010) and RoCEv2 (2014), IBTA · Ultra Ethernet Consortium spec 1.0 (2025)")

    EVENTS = [(1976, "Ethernet", ETH), (1999, "IBTA formed", IB), (2000, "IB 1.0", IB), (2003, "System X", IB),
              (2010, "RoCE", ETH), (2014, "RoCEv2", ETH), (2019, "Nvidia–Mellanox", DIM), (2025, "UEC 1.0", ETH)]

    def timeline(self, c, t):
        x0, x1, y = 160, 1760, 960
        a = P(t, 0.8, 1.8)
        # nonlinear but monotone scale: show 1976, then 1996..2026 expanded
        def X(yr):
            if yr <= 1976: return x0
            return x0 + 100 + (yr - 1996) / 30.0 * (x1 - x0 - 100)
        line(c, x0, y, x1, y, FAINT, 1.2, a, cap="butt")
        for i, (yr, lab, colr) in enumerate(self.EVENTS):
            ts = {0: self.B(1, 3.0), 1: self.B(3, 2.0), 2: self.B(3, 8.0), 3: self.B(4, 3.0), 4: self.B(5, 0.5),
                  5: self.B(5, 3.0), 6: self.B(5, 6.0), 7: self.B(5, 10.0)}[i]
            ea = P(t, ts, ts + 0.8)
            if ea <= 0: continue
            x = X(yr)
            line(c, x, y, x, y - 18 - (i % 2) * 22, colr, 1.5, ea)
            circle(c, x, y, 5, fill=colr, a=ea)
            text(c, str(yr), x, y + 28, 20, DIM, "sans", "c", ea)
            text(c, lab, x, y - 26 - (i % 2) * 22 - 6, 22, colr, "serif", "c", ea)
        # axis break marker
        text(c, "//", x0 + 50, y + 6, 20, FAINT, "sans", "c", a)

    def bus(self, c, a, t, y=400, collide=True):
        # shared coax with stations; collision flash
        line(c, 300, y, 1100, y, ETH, 5, a)
        for i, x in enumerate([380, 560, 740, 920, 1040]):
            line(c, x, y, x, y + 55, FAINT, 1.2, a)
            host_icon(c, x - 32, y + 55, 64, 40, INK, a)
        ph = (t * 0.5) % 1.0
        if collide:
            # two stations transmit, pulses meet, flash, back off
            u = (t * 0.45) % 2.0
            if u < 1.0:
                for (sx, d) in ((380, 1), (1040, -1)):
                    px = sx + d * u * (710 - 380) * (1 if d == 1 else (1040 - 710) / (710 - 380))
                    dot(c, px, y, 6, HI, a)
            elif u < 1.25:
                glow(c, 710, y, 80 * (1 - (u - 1) * 2), BAD, 0.9 * a)
                text(c, "collision", 710, y - 40, 24, BAD, "serifi", "c", a)
            else:
                text(c, "back off, retry", 710, y - 40, 22, DIM, "serifi", "c", a * (1 - (u - 1.25) / 0.75))

    def draw(self, c, t):
        self.timeline(c, t)
        # ---- beat 0 intro
        if t < self.B(1):
            text(c, "a problem, then a design", 960, 520, 54, INK, "serifi", "c", P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, -0.6, 0.0)))
        # ---- beat 1: Ethernet
        if self.B(1) - 0.2 < t < self.B(2) + 0.3:
            a = P(t, self.B(1), self.B(1) + 1.0) * (1 - self.Pb(t, 2, -0.2, 0.3))
            self.bus(c, a, t - self.B(1))
            text(c, "shared coaxial cable", 700, 360, 28, ETH, "serifi", "c", a)
            margin_note(c, "Metcalfe & Boggs, 1976:", 1300, 400, 440, 24, INK, a)
            para(c, "about 3 Mb/s. Stations listen before sending and back off when they collide.", 1300, 436, 440, 24, DIM, "serifi", 1.3, a * P(t, self.B(1) + 4, self.B(1) + 5))
        # ---- beat 2: shared I/O bus problems
        if self.B(2) - 0.2 < t < self.B(3) + 0.3:
            a = P(t, self.B(2), self.B(2) + 1.0) * (1 - self.Pb(t, 3, -0.2, 0.3))
            by = 520
            line(c, 260, by, 1100, by, DIM, 6, a)
            text(c, "shared I/O bus", 680, by - 20, 26, DIM, "serifi", "c", a)
            chip(c, 280, 280, 180, 100, "CPU + memory", INK, a, 20)
            line(c, 370, 380, 370, by, DIM, 3, a)
            for i, nme in enumerate(["NIC", "disk", "HBA", "card"]):
                x = 520 + i * 150
                bad = (i == 3)
                col_ = BAD if (bad and t - self.B(2) > 12) else INK
                chip(c, x, by + 60, 110, 70, nme, col_, a, 20)
                line(c, x + 55, by, x + 55, by + 60, DIM, 3, a)
            # arbitration tax: a token passing
            u = ((t - self.B(2)) * 0.8) % 4
            dot(c, 520 + int(u) * 150 + 55, by, 7, HI, a)
            lab = [("arbitration: every device waits its turn", 3.0), ("one failing card can take down the bus", 9.0), ("every load and store stalls the processor", 14.0)]
            for k, (s, dt) in enumerate(lab):
                text(c, s, 1220, 350 + k * 52, 26, INK if k != 1 else BAD, "serif", "l", a * P(t, self.B(2) + dt, self.B(2) + dt + 1.0))
        # ---- beat 3: IBTA
        if self.B(3) - 0.2 < t < self.B(4) + 0.3:
            a = P(t, self.B(3), self.B(3) + 1.0) * (1 - self.Pb(t, 4, -0.2, 0.3))
            u = self.Pb(t, 3, 3.0, 8.0)
            text(c, "Next Generation I/O", 480, 300, 28, DIM, "serif", "c", a * (1 - u * 0.0) * P(t, self.B(3) + 1, self.B(3) + 2))
            text(c, "Future I/O", 880, 300, 28, DIM, "serif", "c", a * P(t, self.B(3) + 1.5, self.B(3) + 2.5))
            text(c, "(Compaq, IBM, HP)", 880, 332, 19, FAINT, "serifi", "c", a * P(t, self.B(3) + 1.5, self.B(3) + 2.5))
            text(c, "(Intel)", 480, 332, 19, FAINT, "serifi", "c", a * P(t, self.B(3) + 1, self.B(3) + 2))
            m = P(t, self.B(3) + 3.0, self.B(3) + 5.0)
            rich(c, [("InfiniBand", IB), (" Trade Association", INK)], 680, 300 + 150 * m * 0 + 150, 52, "serif", a * m, "c")
            # bus -> point-to-point morph
            if u > 0:
                cx = 1400
                chip(c, cx - 70, 300, 140, 70, "Host", INK, a, 22)
                sw_y = 520
                switch_icon(c, cx - 60, sw_y, 120, 34, IB, a, 6)
                line(c, cx, 370, cx, sw_y, IB, 3, a * u)
                for i, nme in enumerate(["NIC", "disk", "GPU"]):
                    x = cx - 190 + i * 190
                    chip(c, x - 45, 660, 90, 56, nme, INK, a, 18)
                    line(c, cx - 40 + i * 40, sw_y + 34, x, 660, IB, 3, a * u)
                text(c, "point-to-point links,", 1400, 790, 26, IB, "serifi", "c", a * P(t, self.B(3) + 8, self.B(3) + 9))
                text(c, "queued messages", 1400, 826, 26, IB, "serifi", "c", a * P(t, self.B(3) + 8.6, self.B(3) + 9.6))
        # ---- beat 4: PCIe wins; System X
        if self.B(4) - 0.2 < t < self.B(5) + 0.3:
            a = P(t, self.B(4), self.B(4) + 1.0) * (1 - self.Pb(t, 5, -0.2, 0.3))
            text(c, "not the universal server bus", 520, 380, 36, INK, "serif", "c", a)
            line(c, 360, 410, 360 + 320 * P(t, self.B(4) + 0.5, self.B(4) + 1.8), 410, BAD, 2, a)
            text(c, "PCI Express took over inside the box", 520, 470, 26, DIM, "serifi", "c", a * P(t, self.B(4) + 3, self.B(4) + 4))
            # cluster
            ca = a * P(t, self.B(4) + 7, self.B(4) + 8.5)
            for r in range(6):
                for k in range(8):
                    rect(c, 1120 + k * 70, 330 + r * 62, 52, 40, fill=BG2, stroke=IB, sw=1.0, r=3, a=ca * (0.5 + 0.5 * ((r * 8 + k) % 3 == 0)))
            text(c, "Virginia Tech System X, 2003", 1400, 270, 28, IB, "serif", "c", ca)
            text(c, "a cluster interconnected with InfiniBand", 1400, 760, 24, DIM, "serifi", "c", ca)
        # ---- beat 5: Ethernet borrows
        if self.B(5) - 0.2 < t:
            a = P(t, self.B(5), self.B(5) + 1.0)
            # InfiniBand transport wrapped inside Ethernet frame
            fx, fy = 380, 380
            rect(c, fx, fy, 1160, 140, fill=BG2, stroke=ETH, sw=2, r=6, a=a)
            segs = [("Ethernet", 180, ETH), ("IP", 100, ETH), ("UDP 4791", 190, ETH), ("IB transport (BTH)", 250, IB), ("RDMA payload", 340, INK), ("CRC", 100, ETH)]
            x = fx + 20
            for s, w, colr in segs:
                rect(c, x, fy + 30, w - 8, 80, stroke=colr, sw=1.4, r=3, a=a, fill=BG, fa=a)
                text(c, s, x + (w - 8) / 2, fy + 78, 20, colr, "sansm", "c", a)
                x += w
            e1 = P(t, self.B(5) + 0.5, self.B(5) + 1.5)
            text(c, "2010: the InfiniBand transport, carried over Ethernet — RoCE", 960, 580, 26, INK, "serif", "c", a * e1)
            text(c, "2014: routable, over IP and UDP — RoCEv2", 960, 625, 26, ETH, "serif", "c", a * P(t, self.B(5) + 3.0, self.B(5) + 4.0))
            text(c, "2025: Ultra Ethernet specification 1.0", 960, 670, 26, ETH, "serif", "c", a * P(t, self.B(5) + 10.0, self.B(5) + 11.0))


# ---------------------------------------------------------------------------------------------- stack
class Stack(Scene):
    id = "stack"
    title = "What was actually wrong: software"
    sources = "Zhu et al., “Congestion Control for Large-Scale RDMA Deployments”, SIGCOMM 2015 (Microsoft testbed), §2.1: 40 Gb/s NICs; 4 MB messages (CPU); 2 KB messages (latency: RDMA 1.7 µs read/write, 2.8 µs send). One study’s figures, not a general law."

    def path_diagram(self, c, x, y, kind, a, t0, t):
        w = 700
        text(c, "TCP sockets" if kind == "tcp" else "RDMA", x + w / 2, y - 30, 34, ETH if kind == "tcp" else IB, "serif", "c", a)
        rect(c, x, y, w, 120, fill=BG2, stroke=FAINT, r=5, a=a)
        text(c, "application", x + 14, y + 26, 20, DIM, "sans", "l", a)
        if kind == "tcp":
            rect(c, x, y + 150, w, 150, fill=BG2, stroke=ETH, r=5, a=a)
            text(c, "kernel: socket buffers, TCP, IP, driver", x + 14, y + 176, 20, ETH, "sans", "l", a)
        else:
            rect(c, x, y + 150, w, 150, fill=BG, stroke=FAINT, r=5, a=a * 0.5, dash=(6, 6))
            text(c, "kernel (not in the data path)", x + 14, y + 176, 20, FAINT, "sans", "l", a)
        rect(c, x, y + 330, w, 90, fill=BG2, stroke=INK, r=5, a=a)
        text(c, "adapter", x + 14, y + 356, 20, DIM, "sans", "l", a)
        # data flow
        cx = x + w / 2
        for k in range(3):
            u = ((t - t0) * 0.35 + k / 3.0) % 1.0
            if kind == "tcp":
                pts = [(cx - 60, y + 80), (cx - 60, y + 190), (cx - 60, y + 260), (cx - 60, y + 380)]
                pp = along(pts, u)
                pkt(c, pp[0], pp[1], ETH, 26, 14, a)
                if 0.28 < u < 0.4: circle(c, cx + 60, y + 225, 16 * (1 - abs(u - 0.34) / 0.06), stroke=ETH, sw=1.5, a=a)  # copy
            else:
                pts = [(cx + 60, y + 80), (cx + 60, y + 380)]
                pp = along(pts, u)
                pkt(c, pp[0], pp[1], IB, 26, 14, a)
        if kind == "tcp":
            text(c, "copy · segment · interrupt", cx + 70, y + 235, 22, ETH, "serifi", "l", a)
        else:
            text(c, "register once · post to a queue · adapter does the rest", x + 14, y + 450, 22, IB, "serifi", "l", a)

    def draw(self, c, t):
        # beat0: transition statement
        if t < self.B(1) + 0.6:
            a = P(t, 1.0, 2.0) * (1 - self.Pb(t, 1, 0.0, 0.6))
            text(c, "not the wire.", 960, 500, 90, INK, "serif", "c", a * P(t, 3.0, 4.2))
            text(c, "the software.", 960, 600, 90, ETH, "serif", "c", a * P(t, 5.0, 6.2))
        if self.B(1) < t < self.B(4) + 0.6:
            a = P(t, self.B(1), self.B(1) + 1.0) * (1 - self.Pb(t, 4, 0.0, 0.6))
            if t < self.B(3):
                self.path_diagram(c, 130, 230, "tcp", a, self.B(1), t)
            if self.B(3) - 0.3 < t:
                self.path_diagram(c, 1090 if t > self.B(3) + 0.5 else 130, 230, "rdma", P(t, self.B(3), self.B(3) + 1.0) * a, self.B(3), t)
            if t > self.B(3) + 0.5 and t < self.B(4):
                self.path_diagram(c, 130, 230, "tcp", a, self.B(1), t)
        # beat 2: CPU bars
        if self.B(2) < t < self.B(3) - 0.0:
            a = P(t, self.B(2) + 0.2, self.B(2) + 1.0)
            bx, by, bh = 1100, 780, 400
            axis_range_frame(c, bx, by - bh, bx + 560, by, a)
            text(c, "CPU cycles to fill a 40 Gb/s link", bx, by - bh - 24, 22, DIM, "serifi", "l", a)
            for i, (lab, v, colr) in enumerate([("TCP", 20, ETH), ("RDMA", 3, IB)]):
                h = bh * (v / 25.0) * P(t, self.B(2) + 1.5 + i * 2.5, self.B(2) + 3.0 + i * 2.5)
                rect(c, bx + 80 + i * 240, by - h, 120, h, fill=colr, a=a)
                text(c, lab, bx + 140 + i * 240, by + 34, 24, colr, "serif", "c", a)
                text(c, ("> 20 %" if i == 0 else "< 3 %"), bx + 140 + i * 240, by - h - 14, 28, colr, "serif", "c", a * P(t, self.B(2) + 3.0 + i * 2.5, self.B(2) + 3.8 + i * 2.5))
        # beat 4: latency
        if self.B(4) < t < self.B(5) + 0.4:
            a = P(t, self.B(4) + 0.2, self.B(4) + 1.0) * (1 - self.Pb(t, 5, 0.0, 0.4))
            ly = 520
            text(c, "latency, 2 KB message", 960, 330, 32, DIM, "serifi", "c", a)
            # log-free linear scale to 30 us; RDMA bar is really short -> honest
            sc_ = 36.0
            for i, (lab, v, colr, vs) in enumerate([("TCP", 25, ETH, "about 25 µs"), ("RDMA", 2.8, IB, "under 3 µs")]):
                yy = 420 + i * 110
                w = v * sc_ * P(t, self.B(4) + 1.0 + i * 3, self.B(4) + 2.4 + i * 3)
                rect(c, 400, yy, w, 56, fill=colr, a=a)
                text(c, lab, 380, yy + 38, 30, colr, "serif", "r", a)
                text(c, vs, 400 + w + 16, yy + 38, 28, colr, "sansm", "l", a * P(t, self.B(4) + 2.4 + i * 3, self.B(4) + 3.2 + i * 3))
            line(c, 400, 640, 400 + 30 * sc_, 640, FAINT, 1, a, cap="butt")
            for m in (0, 10, 20, 30):
                line(c, 400 + m * sc_, 640, 400 + m * sc_, 650, FAINT, 1, a)
                text(c, f"{m}", 400 + m * sc_, 676, 18, DIM, "sans", "c", a)
            text(c, "µs", 400 + 30 * sc_ + 30, 676, 18, DIM, "sans", "l", a)
        # beat 5: RDMA is not InfiniBand
        if self.B(5) < t:
            a = P(t, self.B(5) + 0.2, self.B(5) + 1.2)
            circle(c, 960, 520, 250, stroke=INK, sw=1.6, a=a, fill=BG2, fa=a * 0.6)
            text(c, "RDMA", 960, 330, 36, INK, "serif", "c", a)
            for i, (nm, xx, colr) in enumerate([("InfiniBand", 810, IB), ("RoCE", 960, ETH), ("iWARP", 1110, DIM)]):
                aa = a * P(t, self.B(5) + 4 + i * 1.5, self.B(5) + 5 + i * 1.5)
                circle(c, xx, 540, 62, stroke=colr, sw=2, a=aa, fill=colr, fa=aa * 0.12)
                text(c, nm, xx, 546, 22 if i < 1 else 22, colr, "serif", "c", aa)
            text(c, "a way of moving memory, not a particular network", 960, 840, 28, DIM, "serifi", "c", a * P(t, self.B(5) + 9, self.B(5) + 10))
            text(c, "InfiniBand just had it from day one", 960, 885, 28, IB, "serifi", "c", a * P(t, self.B(5) + 10.5, self.B(5) + 11.5))
