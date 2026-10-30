"""Scenes 4-6: three, verbs, credits"""
import math
from engine import *


# ---------------------------------------------------------------------------------------------- three
class Three(Scene):
    id = "three"
    title = "What is left, once Ethernet has RDMA"
    sources = ("Header bytes: IB LRH 8 + BTH 12 + ICRC 4 + VCRC 2 = 26 B; RoCEv2 62–66 B depending on the source (Slingshot paper; Hoefler et al.). "
               "Efficiency = 4096 / (4096 + header).  Computed in src/model_numbers.py")

    def panel(self, c, i, t, a):
        x = 130 + i * 590
        y = 230
        names = [("1  Loss", "who gets to drop a packet?", GOOD), ("2  Routing", "who decides the path?", IB), ("3  Arithmetic", "can the network compute?", HI)]
        nm, q, colr = names[i]
        rect(c, x, y, 540, 560, fill=BG2, stroke=FAINT, sw=1.2, r=8, a=a)
        text(c, nm, x + 30, y + 64, 44, colr, "serif", "l", a)
        text(c, q, x + 30, y + 104, 24, DIM, "serifi", "l", a)
        cx, cy = x + 270, y + 330
        ph = t
        if i == 0:
            # sender -> buffer -> receiver; ethernet drops, IB waits
            rect(c, cx - 190, cy - 30, 70, 60, stroke=INK, sw=1.4, a=a, r=4)
            rect(c, cx + 120, cy - 30, 70, 60, stroke=INK, sw=1.4, a=a, r=4)
            line(c, cx - 120, cy, cx + 120, cy, FAINT, 2, a)
            for k in range(3):
                u = (ph * 0.4 + k / 3) % 1.0
                px = lerp(cx - 120, cx + 120, u)
                pkt(c, px, cy, GOOD if u < 0.7 else (BAD if (ph * 0.4) % 2 > 1 else GOOD), 20, 12, a)
            text(c, "credit: sent only if there is room", cx, cy + 90, 22, GOOD, "serifi", "c", a)
            text(c, "vs. overflow, then drop", cx, cy + 124, 22, ETH, "serifi", "c", a)
        elif i == 1:
            # central brain + switch tree
            circle(c, cx, cy - 90, 30, stroke=IB, sw=2, a=a)
            text(c, "SM", cx, cy - 82, 22, IB, "sansb", "c", a)
            for k in range(3):
                sx = cx - 150 + k * 150
                switch_icon(c, sx - 40, cy + 10, 80, 26, IB, a, 4)
                line(c, cx, cy - 60, sx, cy + 10, IB, 1.2, a * 0.7, dash=(5, 5))
                for j in range(2):
                    hx = sx - 40 + j * 80
                    line(c, sx, cy + 36, hx, cy + 100, FAINT, 1.2, a)
                    circle(c, hx, cy + 106, 7, stroke=INK, sw=1.2, a=a)
            text(c, "one planner, every table", cx, cy + 170, 22, IB, "serifi", "c", a)
        else:
            text(c, "Σ", cx, cy + 30, 150, HI, "mathi", "c", a)
            for k in range(4):
                px = cx - 160 + k * 107
                circle(c, px, cy + 120, 8, stroke=INK, a=a, sw=1.2)
                line(c, px, cy + 112, cx, cy + 50, FAINT, 1.2, a)
            text(c, "reduce data as it flows through", cx, cy + 170, 22, HI, "serifi", "c", a)

    def draw(self, c, t):
        # beat0 text
        if t < self.B(1):
            text(c, "after the packet leaves the adapter", 960, 520, 60, INK, "serifi", "c", P(t, 1.0, 2.2) * (1 - self.Pb(t, 1, -0.6, 0)))
        if self.B(1) - 0.3 < t < self.B(4) + 1.0:
            gl = 1 - self.Pb(t, 4, 0.0, 1.0)
            for i in range(3):
                ts = [self.B(1), self.B(2), self.B(3)][i]
                a = P(t, ts, ts + 1.0) * gl
                if a > 0: self.panel(c, i, t, a)
        # beat 4: header efficiency
        if self.B(4) + 0.5 < t:
            a = P(t, self.B(4) + 0.5, self.B(4) + 1.5)
            text(c, "header overhead at 4 KiB payload", 960, 270, 36, INK, "serif", "c", a)
            bx, by = 420, 420
            sc_ = 560.0  # px per percent
            rows = [("InfiniBand", 26 / (4096 + 26) * 100, IB, "0.63 %"), ("RoCEv2", 62 / (4096 + 62) * 100, ETH, "1.5 %")]
            for i, (nm, v, colr, lab) in enumerate(rows):
                yy = by + i * 100
                w = v * sc_ * P(t, self.B(4) + 2 + i * 2.0, self.B(4) + 3.2 + i * 2.0)
                text(c, nm, bx - 20, yy + 38, 32, colr, "serif", "r", a)
                rect(c, bx, yy, w, 52, fill=colr, a=a)
                text(c, lab, bx + w + 16, yy + 38, 30, colr, "serif", "l", a * P(t, self.B(4) + 3 + i * 2.0, self.B(4) + 4 + i * 2.0))
            line(c, bx, by + 220, bx + 2 * sc_, by + 220, FAINT, 1, a, cap="butt")
            for m in (0, 0.5, 1.0, 1.5, 2.0):
                line(c, bx + m * sc_, by + 220, bx + m * sc_, by + 230, FAINT, 1, a)
                text(c, f"{m:.1f} %", bx + m * sc_, by + 256, 18, DIM, "sans", "c", a)
            text(c, "a wash", 960, 800, 64, DIM, "serifi", "c", a * P(t, self.B(4) + 7, self.B(4) + 8.5))
            margin_note(c, "RoCEv2 header size depends on the source: 62 B or 66 B; 1.5 % either way.", 1320, 460, 440, 22, DIM, a * P(t, self.B(4) + 5, self.B(4) + 6))


# ---------------------------------------------------------------------------------------------- verbs
class Verbs(Scene):
    id = "verbs"
    title = "The life of one message"
    sources = "InfiniBand Architecture Specification (IBTA); verbs semantics as in libibverbs.  Up to ~16 M queue pairs per adapter (24-bit QPN)."

    def draw(self, c, t):
        # geometry
        L, R = 110, 1210           # local host box / remote host box x
        hw = 600
        yH = 190
        # local host
        rect(c, L, yH, hw, 560, fill=BG2, stroke=FAINT, sw=1.2, r=8, a=1)
        text(c, "host A", L + 20, yH + 34, 24, DIM, "serifi", "l")
        rect(c, R, yH, hw, 560, fill=BG2, stroke=FAINT, sw=1.2, r=8, a=1)
        text(c, "host B", R + 20, yH + 34, 24, DIM, "serifi", "l")
        # memory regions
        mrA = (L + 30, yH + 70, 260, 120)
        mrB = (R + hw - 290, yH + 70, 260, 120)
        rect(c, *mrA, stroke=INK, sw=1.4, r=4); text(c, "application buffer", mrA[0] + 130, mrA[1] + 70, 22, INK, "sans", "c")
        rect(c, *mrB, stroke=INK, sw=1.4, r=4); text(c, "destination buffer", mrB[0] + 130, mrB[1] + 70, 22, INK, "sans", "c")
        # adapters
        hcaA = (L + hw - 190, yH + 380, 160, 130); hcaB = (R + 30, yH + 380, 160, 130)
        chip(c, *hcaA, "adapter", IB, 1, 22); chip(c, *hcaB, "adapter", IB, 1, 22)
        # wire
        line(c, hcaA[0] + hcaA[2], hcaA[1] + 65, hcaB[0], hcaB[1] + 65, IB, 3)
        # beat 0: registration
        a0 = P(t, self.B(0) + 1.5, self.B(0) + 2.5)
        if a0 > 0:
            rect(c, *mrA, stroke=IB, sw=3, r=4, a=a0)
            tag(c, "PINNED", mrA[0], mrA[1] - 12, IB, a0)
            arrow(c, (mrA[0] + 200, mrA[1] + mrA[3]), (hcaA[0] + 60, hcaA[1]), IB, 2, a0 * P(t, self.B(0) + 3.5, self.B(0) + 5), P(t, self.B(0) + 3.5, self.B(0) + 5), dash=(6, 5))
            ka = P(t, self.B(0) + 6.0, self.B(0) + 7.5)
            text(c, "lkey  rkey", hcaA[0] + 80, hcaA[1] - 16, 24, HI, "mono", "c", ka)
            text(c, "registered once", mrA[0] + 130, mrA[1] + mrA[3] + 26, 20, DIM, "serifi", "c", a0)
            text(c, "adapter can now translate its addresses", L + 30, yH + 560 - 20, 22, DIM, "serifi", "l", P(t, self.B(0) + 8, self.B(0) + 9.5) * (1 - self.Pb(t, 1, 0.0, 0.8)))
        # beat 1: QP
        if t > self.B(1):
            a1 = P(t, self.B(1) + 0.3, self.B(1) + 1.5)
            qx, qy = L + 30, yH + 260
            text(c, "queue pair", qx, qy - 12, 22, GOOD, "serif", "l", a1)
            for j, nm in enumerate(["send queue", "receive queue"]):
                for k in range(5):
                    rect(c, qx + k * 44, qy + j * 52, 40, 36, stroke=GOOD, sw=1.2, r=3, a=a1)
                text(c, nm, qx + 5 * 44 + 10, qy + j * 52 + 26, 18, GOOD, "sans", "l", a1)
            text(c, "up to ~16 million per adapter", qx, qy + 130, 20, DIM, "serifi", "l", P(t, self.B(1) + 6, self.B(1) + 7.5))
            # remote QP
            rx, ry = R + 30, yH + 260
            for j, nm in enumerate(["send queue", "receive queue"]):
                for k in range(5):
                    rect(c, rx + k * 44, ry + j * 52, 40, 36, stroke=GOOD, sw=1.2, r=3, a=a1 * 0.7)
        # beat 2: post + doorbell + dma + packets
        T2 = self.B(2)
        if t > T2:
            w = P(t, T2 + 1.0, T2 + 2.0)
            qx, qy = L + 30, yH + 260
            rect(c, qx, qy, 40, 36, fill=HI, r=3, a=w)
            text(c, "work request: address, length, rkey…", L + 30, yH + 460, 22, HI, "serifi", "l", w)
            db = pulse(t, T2 + 3.0, T2 + 4.0)
            if db > 0:
                glow(c, hcaA[0] + 80, hcaA[1] + 65, 90 * db + 20, HI, 0.8 * db)
                text(c, "doorbell", hcaA[0] + 80, hcaA[1] + 170, 24, HI, "serif", "c", db)
            u = P(t, T2 + 4.5, T2 + 6.0, lin)
            if u > 0:
                p0 = (mrA[0] + 130, mrA[1] + mrA[3]); p1 = (hcaA[0] + 80, hcaA[1])
                for k in range(3):
                    uu = clamp(u * 1.4 - k * 0.2)
                    if 0 < uu < 1: pkt(c, *lerp2(p0, p1, uu), IB, 22, 12)
            # packets on the wire
            for k in range(4):
                pu = ((t - (T2 + 6.0)) * 0.30 + k * 0.25) % 1.0
                if t > T2 + 6.0:
                    px = lerp(hcaA[0] + hcaA[2], hcaB[0], pu); pkt(c, px, hcaA[1] + 65, IB, 26, 14)
            if t > T2 + 7.0:
                text(c, "up to 4 KiB per packet", (hcaA[0] + hcaB[0] + hcaA[2]) / 2, hcaA[1] + 30, 22, IB, "serifi", "c", P(t, T2 + 7, T2 + 8))
        # beat 3: remote write, remote CPU sleeps
        T3 = self.B(3)
        if t > T3:
            u = P(t, T3 + 0.5, T3 + 2.5, lin)
            p0 = (hcaB[0] + 80, hcaB[1]); p1 = (mrB[0] + 130, mrB[1] + mrB[3])
            for k in range(3):
                uu = clamp(u * 1.4 - k * 0.2)
                if 0 < uu < 1: pkt(c, *lerp2(p0, p1, uu), IB, 22, 12)
            f = P(t, T3 + 2.5, T3 + 3.5)
            rect(c, *mrB, stroke=IB, sw=3, r=4, a=f)
            chip(c, R + 30, yH + 70, 180, 70, "remote CPU", DIM, 1, 20)
            text(c, "z z z", R + 120, yH + 170, 28, DIM, "serifi", "c", P(t, T3 + 4, T3 + 5))
        # beat 4: ack + CQ
        T4 = self.B(4)
        if t > T4:
            for k in range(2):
                pu = ((t - (T4 + 0.5)) * 0.3 + k * 0.5) % 1.0
                if t > T4 + 0.5:
                    px = lerp(hcaB[0], hcaA[0] + hcaA[2], pu); pkt(c, px, hcaA[1] + 85, GOOD, 18, 10, 0.9)
            text(c, "ACK  ·  sequence numbers  ·  retransmit if needed", (hcaA[0] + hcaB[0] + hcaA[2]) / 2, hcaA[1] + 130, 20, GOOD, "serifi", "c", P(t, T4 + 0.8, T4 + 2))
            cqx, cqy = L + 30, yH + 500
            ca = P(t, T4 + 5, T4 + 6)
            text(c, "completion queue", cqx, cqy - 8, 20, HI, "serif", "l", ca)
            for k in range(4):
                rect(c, cqx + k * 44, cqy, 40, 30, stroke=HI, sw=1.2, r=3, a=ca, fill=HI if k == 0 and t > T4 + 6 else None, fa=ca)
            text(c, "poll", cqx + 190, cqy + 22, 22, HI, "mono", "l", P(t, T4 + 7, T4 + 8))
        # beat 5
        T5 = self.B(5)
        if t > T5 - 0.5:
            a = P(t, T5 - 0.5, T5 + 0.5)
            rect(c, 0, 0, LW, LH, fill=BG, fa=a * 0.82)
            for i, s in enumerate(["no system call", "no copy", "no interrupt"]):
                aa = P(t, T5 + 0.6 + i * 1.3, T5 + 1.6 + i * 1.3)
                text(c, s, 960, 450 + i * 90, 64, INK if i != 2 else IB, "serif", "c", aa)
            text(c, "in the data path", 960, 450 + 3 * 90 + 10, 34, DIM, "serifi", "c", P(t, T5 + 4.6, T5 + 5.6))


# ---------------------------------------------------------------------------------------------- credits
def credit_sim(t, slots=6, send_iv=0.55, lat=1.0, drain_fast=0.55, drain_slow=1.6, t_slow=1e9):
    """tiny discrete simulation of one credit-based hop. returns dict for drawing"""
    dt = 1 / 30.0
    credits, buf = slots, 0
    inflight, creds_back = [], []
    last_send, last_drain = -9.0, 0.0
    now = 0.0
    sent_total = 0
    while now < t:
        # arrivals
        for p in [p for p in inflight if p <= now]:
            inflight.remove(p); buf += 1
        for p in [p for p in creds_back if p <= now]:
            creds_back.remove(p); credits += 1
        # drain
        di = drain_fast if now < t_slow else drain_slow
        if buf > 0 and now - last_drain >= di:
            buf -= 1; last_drain = now; creds_back.append(now + lat)
        # send
        if credits > 0 and now - last_send >= send_iv:
            credits -= 1; inflight.append(now + lat); last_send = now; sent_total += 1
        now += dt
    return dict(credits=credits, buf=buf, inflight=[p - t for p in inflight], back=[p - t for p in creds_back], sent=sent_total)


class Credits(Scene):
    id = "credits"
    title = "The link layer: credits versus drops"
    sources = ("Credits: InfiniBand Architecture Spec (link-level flow control, per VL).  Victim-flow numbers: Zhu et al. (DCQCN), SIGCOMM 2015, Microsoft testbed.  PFC deadlock: Guo et al., SIGCOMM 2016.  "
               "Buffer: 400 Gb/s x 2 x 100 m x 4.9 ns/m = 49 kB (propagation only; lower bound)")

    def hop(self, c, t, tt, a, y=470, slots=6, label=True, **kw):
        s = credit_sim(tt, slots=slots, **kw)
        sx, rx = 280, 1240
        rect(c, sx - 110, y - 60, 110, 120, fill=BG2, stroke=INK, sw=1.5, r=5, a=a)
        text(c, "sender", sx - 55, y + 90, 22, DIM, "serifi", "c", a)
        # receiver buffer
        rect(c, rx, y - 60, 330, 120, fill=BG2, stroke=INK, sw=1.5, r=5, a=a)
        for k in range(slots):
            filled = k < s["buf"]
            rect(c, rx + 15 + k * 50, y - 28, 42, 56, fill=IB if filled else None, stroke=IB, sw=1.2, r=3, a=a, fa=a * 0.85)
        text(c, "receiver buffer (one VL)", rx + 165, y + 90, 22, DIM, "serifi", "c", a)
        line(c, sx, y, rx, y, FAINT, 2, a)
        for p in s["inflight"]:
            u = 1 - clamp(p / 1.0)
            pkt(c, lerp(sx, rx, u), y - 12, IB, 24, 14, a)
        for p in s["back"]:
            u = clamp(p / 1.0)
            circle(c, lerp(sx, rx, u), y + 16, 7, fill=GOOD, a=a)
        # credits counter
        text(c, "credits", sx + 40, y - 90, 22, GOOD, "serif", "l", a)
        for k in range(slots):
            circle(c, sx + 160 + k * 30, y - 97, 9, fill=GOOD if k < s["credits"] else None, stroke=GOOD, sw=1.4, a=a)
        if s["credits"] == 0:
            text(c, "STOP", sx + 40, y + 140, 54, BAD, "serifb", "l", a)
        return s

    def draw(self, c, t):
        # beat0 + 1 + 2: credit hop
        if t < self.B(3) + 0.5:
            a = P(t, self.B(0) + 1.0, self.B(0) + 2.0) * (1 - self.Pb(t, 3, 0.0, 0.5))
            tt = max(0.0, t - self.B(1) + 1.0)
            t_slow = self.B(2) - self.B(1) + 1.0
            s = self.hop(c, t, tt, a, drain_fast=0.45, drain_slow=1.8, t_slow=t_slow)
            if self.B(1) < t < self.B(2):
                text(c, "the receiver tells the sender how many slots are free", 960, 700, 28, GOOD, "serifi", "c", P(t, self.B(1), self.B(1) + 1) * a)
            if t > self.B(1) + 6:
                text(c, "not drops.  stops.", 960, 780, 40, INK, "serif", "c", P(t, self.B(1) + 8, self.B(1) + 9) * a)
            if t > self.B(2):
                text(c, "a slow receiver slows its sender, hop by hop, back to the source", 960, 860, 28, IB, "serifi", "c", P(t, self.B(2) + 3, self.B(2) + 4) * a)
        # beat 3-5: PFC on ethernet
        if self.B(3) - 0.3 < t < self.B(6) + 0.0:
            a = P(t, self.B(3), self.B(3) + 1.0) * (1 - self.Pb(t, 6, -0.8, 0.0))
            if t < self.B(4) + 3:
                # switch sends pause upstream
                text(c, "Ethernet: drop, or  PFC", 960, 250, 40, ETH, "serif", "c", a)
                sy = 520
                switch_icon(c, 700, sy, 180, 50, ETH, a, 8, "switch")
                host_icon(c, 330, sy + 5, 80, 40, INK, a)
                line(c, 410, sy + 25, 700, sy + 25, FAINT, 2, a)
                pa = pulse(t, self.B(3) + 8, self.B(3) + 11)
                for k in range(3):
                    u = (t * 0.3 + k / 3) % 1.0
                    pkt(c, lerp(410, 700, u), sy + 25, ETH, 22, 12, a * (1 - 0.8 * (pa > 0.1)))
                if pa > 0:
                    arrow(c, (700, sy + 70), (420, sy + 70), BAD, 3, a * pa, 1.0)
                    text(c, "PAUSE", 560, sy + 110, 30, BAD, "serifb", "c", a * pa)
            if t > self.B(4):
                bx, by = 1080, 760
                aa = P(t, self.B(4) + 0.5, self.B(4) + 1.5) * a
                text(c, "throughput of one victim flow (Mb/s × 1000 = Gb/s)", 960, 280, 1, BG, "sans", "c", 0)
                text(c, "one victim flow, Microsoft testbed", 960, 300, 28, DIM, "serifi", "c", aa)
                vals = [("expected", 20, GOOD), ("with PFC", 10, ETH), ("+2 more senders (median)", 4.5, BAD)]
                for i, (nm, v, colr) in enumerate(vals):
                    x = 540 + i * 330
                    ts = self.B(4) + 2 + i * 2.5
                    h = 300 * (v / 20) * P(t, ts, ts + 1.2)
                    rect(c, x, 790 - h, 120, h, fill=colr, a=aa)
                    text(c, f"{v:g} Gb/s", x + 60, 790 - h - 14, 28, colr, "serif", "c", aa * P(t, ts + 1, ts + 1.8))
                    text(c, nm, x + 60, 830, 20, DIM, "sans", "c", aa)
                line(c, 500, 790, 1520, 790, FAINT, 1, aa, cap="butt")
        # beat 5: deadlock
        if self.B(5) - 0.3 < t < self.B(6) + 0.5:
            a = P(t, self.B(5), self.B(5) + 1.0) * (1 - self.Pb(t, 6, -0.2, 0.5))
            rect(c, 0, 0, LW, LH, fill=BG, fa=a)
            pts = [(760, 380), (1160, 380), (1160, 640), (760, 640)]
            froze = P(t, self.B(5) + 9, self.B(5) + 11)
            for i in range(4):
                p, q = pts[i], pts[(i + 1) % 4]
                arrow(c, lerp2(p, q, 0.22), lerp2(p, q, 0.78), BAD if froze > 0.5 else ETH, 3, a)
                switch_icon(c, p[0] - 60, p[1] - 17, 120, 34, BAD if froze > 0.5 else ETH, a, 6)
            text(c, "a cycle of paused switches", 960, 300, 38, INK, "serif", "c", a * P(t, self.B(5) + 3, self.B(5) + 4))
            text(c, "stale address-table entries made lossless traffic flood", 960, 730, 24, DIM, "serifi", "c", a * P(t, self.B(5) + 5, self.B(5) + 6))
            text(c, "deadlock", 960, 520, 56, BAD, "serifb", "c", a * froze)
        # beat 6: honesty
        if self.B(6) - 0.3 < t:
            a = P(t, self.B(6), self.B(6) + 1.0)
            text(c, "credits aren’t magic", 960, 300, 60, INK, "serif", "c", a)
            text(c, "credit loops can deadlock InfiniBand too — so routing must be chosen carefully", 960, 400, 28, DIM, "serifi", "c", a * P(t, self.B(6) + 3.5, self.B(6) + 4.5))
            # BDP buffer
            ba = a * P(t, self.B(6) + 8, self.B(6) + 9)
            rich(c, [("400 Gb/s", IB, "mono"), ("  ×  round trip over 100 m", INK, "mono"), ("  ≈  ", INK, "mono"), ("49 kB", HI, "mono")], 960, 560, 34, "mono", ba, "c")
            text(c, "per virtual lane, per port — cable length costs silicon", 960, 625, 28, DIM, "serifi", "c", ba * P(t, self.B(6) + 11, self.B(6) + 12))
