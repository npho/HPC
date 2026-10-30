"""
Narration script.  One entry per scene; each scene is a list of 'beats'.
A beat is 1-3 sentences.  Beat start times (from the synthesized audio) are the sync points for the animation.

Spelling in `say` is deliberately phonetic for the TTS engine ("R D M A", "Rocky" for RoCE, ...).
`sub()` converts it back to proper notation for the .srt subtitles.
"""
import re

SCENES = [
 dict(id="open", beats=[
  "Here's the strange thing about a four hundred gigabit link. The wire itself is almost never the problem.",
  "A four kilobyte packet takes about eighty-two nanoseconds to push onto it. In that time, light travels roughly seventeen meters down a fiber.",
  "Everything that really costs you time is somewhere else. In software. In buffers. In routing decisions. In queues that fill up when thousands of machines talk at once.",
  "This video is about the machinery that attacks those costs: InfiniBand, and the Ethernet that has been steadily absorbing its ideas.",
 ]),
 dict(id="history", beats=[
  'A very short history first, because the design makes sense once you know the problem it was born to solve.',
  'Ethernet comes first. Metcalfe and Boggs described it in nineteen seventy-six: a shared coaxial cable at about three megabits per second, where stations listen, and back off if they collide.',
  'By the late nineties, servers had a different headache: processors were outrunning the shared I O bus. Every device pays an arbitration tax, one failing card can take down the rest, and every load stalls the processor.',
  "So in nineteen ninety-nine, Intel's Next Generation I O, and Future I O from Compaq, I B M and H P, merged into the InfiniBand Trade Association. Their answer: point-to-point links instead of a bus, and queued messages instead of memory access. Version one point oh appeared in October of two thousand.",
  "It never became the universal server bus. After the dot-com bust, Intel and Microsoft backed away, and PCI Express took over inside the box. But clusters found a better use: Virginia Tech's System X ran on InfiniBand in two thousand three.",
  "Ethernet, meanwhile, borrowed the trick. In twenty ten, the InfiniBand transport was carried over Ethernet as Rocky, and made routable in twenty fourteen. Nvidia's deal for Mellanox dates to twenty nineteen. And Ultra Ethernet's first specification arrived in twenty twenty-five.",
 ]),
 dict(id="stack", beats=[
  'So what was wrong with ordinary Ethernet and T C P? Not the wire. The software.',
  'With sockets, every message crosses into the kernel, gets copied, segmented, and eventually raises an interrupt. At forty gigabits per second, the C P U itself becomes the bottleneck.',
  'Microsoft measured it. Moving four megabyte messages, T C P burned over twenty percent of the C P U cycles across all cores to fill the link. R D M A used under three.',
  "R D M A flips the model. The application registers memory once, posts a work request into a queue it owns, and the adapter does the rest: reading memory, building packets, writing a note when it's finished. No kernel in the data path.",
  'For two kilobyte messages, the same study measured about twenty-five microseconds on T C P, against under three on R D M A.',
  'But notice what that comparison is: T C P versus R D M A, both on Ethernet. R D M A is not the same thing as InfiniBand. InfiniBand just had it from day one.',
 ]),
 dict(id="three", beats=[
  "So if Ethernet can do R D M A, what's left? Three things. All of them are about what happens after the packet leaves the adapter.",
  "First, loss. An InfiniBand link never sends a packet unless the receiver has advertised room for it. Ethernet normally drops packets when a buffer overflows, and R D M A transports hate that.",
  "Second, routing. InfiniBand has a central subnet manager that computes every route and programs every switch. Ethernet networks usually spread flows across equal-cost paths by hashing, with no global plan.",
  "Third, arithmetic. InfiniBand switches can reduce data as it flows through them.",
  "What's not on the list is header overhead. At four kilobytes, InfiniBand's headers cost about six tenths of a percent, and Rocky's about one and a half. Under one point of difference in wire efficiency. That part is a wash.",
  "Let's take them apart one at a time, starting with how a send actually works.",
 ]),
 dict(id="verbs", beats=[
  "Here's the life of one message. The application first registers a region of memory with the adapter, which pins it and returns a pair of keys. The adapter can now translate that region's addresses on its own.",
  "Next, a queue pair: a send queue and a receive queue, living in the application's own address space. One adapter supports up to about sixteen million of them.",
  'To send, the application writes a work request, and rings a doorbell, a single write to the adapter. The adapter reads the data straight out of memory and splits it into packets of up to four kilobytes.',
  'At the far end, the other adapter writes them directly into the destination buffer. For a one-sided R D M A write, the remote C P U never even wakes up.',
  'In reliable mode, the hardware numbers the packets, acknowledges them, and retransmits if it must. Then it drops a small entry into a completion queue, and the application simply polls for it.',
  "No system call, no copy, no interrupt in the data path. That's the entire trick behind the latency numbers.",
 ]),
 dict(id="credits", beats=[
  'Now the link layer, where InfiniBand is most different. Watch a single hop.',
  'The receiver has a buffer, divided per virtual lane, and tells the sender how many slots are free. Those are credits. The sender spends one per packet, and when it runs out, it stops. Not drops. Stops.',
  'As the receiver drains its buffer, it hands credits back. So a slow receiver slows its sender, hop by hop, back to the source. Nothing is ever thrown away, by construction.',
  "Ethernet's usual answer to overflow is different: drop the packet, and let the transport notice. R D M A hates that, so R D M A over Ethernet adds priority flow control. A switch under pressure sends a pause frame upstream.",
  "It works, but pause is blunt. It stops a whole traffic class on a link, including innocent flows. In Microsoft's testbed, a flow that should have got twenty gigabits got ten. With two more senders, its median fell to four and a half.",
  'Pause can also chase its own tail. In production, Microsoft hit a deadlock: stale address-table entries made lossless traffic flood, and a cycle of paused switches froze. They fixed it. But it shows why this takes care.',
  "To be fair, credits aren't magic. Credit loops can deadlock InfiniBand too, which is why routing must be chosen carefully. And buffers must still cover the round trip: at four hundred gigabits, a hundred meter cable needs about fifty kilobytes per virtual lane. Cable length costs silicon.",
 ]),
 dict(id="routing", beats=[
  'Routing. Each InfiniBand subnet has one master subnet manager. When the fabric comes up, it discovers every switch and adapter by sending management packets, hop by hop.',
  "It gives every port a sixteen-bit local identifier, a L I D, then computes routes and programs each switch with a simple forwarding table: destination in, output port out. A packet's journey is nothing but a series of lookups.",
  'Which algorithm you pick matters. The open source subnet manager offers several: min-hop; Up slash Down, which prevents credit loops by never going up after going down; a fat-tree engine; and others that use virtual lanes to break cycles on any topology.',
  'But static routes have a weakness. When flows share a link, some wait, while parallel links sit idle. I simulated random permutation traffic on a sixteen by sixteen leaf-spine fabric with no oversubscription. Flow-level hashing delivered only about fifty-six percent of ideal throughput.',
  'A destination-based table, like a fat-tree engine builds, does better: sixty-nine percent, and a perfect hundred on the shift pattern it was tuned for. Spreading packets across all paths, as adaptive routing tries to, reaches a hundred in this idealized model. Real hardware gets less.',
  'Microsoft reported about sixty percent in production, and blamed the same effect. Mine is a toy model, so treat that agreement as a hint, not a proof.',
 ]),
 dict(id="congestion", beats=[
  "Lossless doesn't mean congestion-free. When many senders target one receiver, queues still build, and backpressure spreads backward like a traffic jam.",
  "So senders must be told to slow down. InfiniBand marks packets in the switch, and the receiving adapter notifies the sender. Rocky does something similar with E C N marks, in a scheme called D C Q C N: each notification cuts the sender's rate by up to half, then it climbs back in steps. Its authors are clear that pause frames remain the backstop.",
  "H P E's Slingshot hardware tracks every in-flight packet between every pair of endpoints, and applies stiff backpressure only to the sources causing the jam. Their paper reports a worst-case victim slowdown of one point three times, versus ninety-three on Cray's previous network.",
 ]),
 dict(id="sharp", beats=[
  "One more InfiniBand trick, and it changes what a network is for. Imagine summing a number across a hundred and twenty-eight machines. That's an all-reduce, the heartbeat of distributed training, and of many simulations.",
  "Normally, hosts exchange partial results in rounds, and the data crosses the network again and again. With Sharp, the switches do the arithmetic. Data flows up a tree, gets summed at each switch, and the answer flows back down.",
  "In the original paper, an eight byte all-reduce on a hundred twenty-eight hosts dropped from six microseconds to under three. At four kilobytes, from forty-seven to fourteen and a half.",
  "Those are the authors' numbers, on pre-release hardware, tuned for low noise, so treat them as a best case. Nvidia now ships its fourth generation, and claims up to nine times. That's a vendor claim I couldn't verify.",
 ]),
 dict(id="fattree", beats=[
  "Now topology, where arithmetic takes over. The workhorse is the fat tree. Take switches with k ports. Give half of each leaf's ports to hosts, and half to spines. Any host can talk to any other at full speed.",
  "Two levels gives k squared over two hosts. For a sixty-four port N D R switch, that's two thousand forty-eight hosts, using ninety-six switches.",
  "A third level makes it k cubed over four: sixty-five thousand, five hundred thirty-six hosts. But five thousand one hundred twenty switches, and more hops for every message.",
  "The formula holds up against vendor claims. A hundred forty-four port X D R switch should connect ten thousand three hundred sixty-eight adapters in two levels. Nvidia's datasheet says exactly that.",
  "Real AI clusters add a twist: rails. In Nvidia's reference design, each node has eight adapters, and the fabric is rail-aligned. Same-numbered adapters across thirty-two nodes are one switch hop apart.",
  "One scalable unit is up to thirty-two nodes, with eight leaf switches and four spines. Storage and management live on separate networks.",
 ]),
 dict(id="dragonfly", beats=[
  'Fat trees get expensive at scale, mostly in long optical cables. The dragonfly, from Kim, Dally and colleagues in two thousand eight, makes a different trade.',
  'Connect every switch in a group directly to every other with short copper, give each switch a few long links to other groups, and treat each group as one giant virtual router.',
  'Three numbers define it: p terminals per switch, a switches per group, h global links per switch. The biggest network has a times p times a h plus one terminals, and the balanced design has a equal to two p, equal to two h.',
  "Frontier is almost exactly a textbook case: sixteen host links per switch, thirty-one local, up to sixteen global. That's p of sixteen, a of thirty-two, h of sixteen. Seventy-four groups, with four links between each pair.",
  'Any path takes at most three switch hops. But send everything the short way, and a worst-case pattern squeezes through a single global link. So dragonflies route some traffic through a random middle group, or choose per packet by watching queues. They live and die by adaptive routing.',
  'InfiniBand runs dragonfly-plus too: JUPITER, at Jülich, uses N D R two hundred, with each group a fat tree.',
 ]),
 dict(id="hardware", beats=[
  'Now the hardware. At the edge sits the host adapter, today a Connect X seven at four hundred gigabits per port, in a PCI Express slot.',
  "A generation five slot with sixteen lanes carries about sixty-three gigabytes a second each way: five hundred four gigabits. Four hundred fits. Eight hundred doesn't, which is why Connect X eight moves to generation six.",
  'The switch: a Q M ninety-seven hundred is one rack unit, with sixty-four four-hundred-gig ports through thirty-two twin-port O S F P cages. Around seven hundred fifty watts with passive copper, up to seventeen hundred with active cables.',
  "A word on spec sheets. Nvidia quotes that switch at fifty-one point two terabits, counting both directions. Broadcom's Tomahawk six is a hundred two point four terabits, counting one. Same footing, the Q M ninety-seven hundred is twenty-five point six.",
  'Cables set the layout. Passive copper reaches about three meters at this speed, active copper five, multimode optics fifty, single-mode five hundred and up. So copper inside the rack, optics between racks.',
  'X D R doubles the lane rate to two hundred gigabits. Ethernet is on the same curve: eight hundred gigabit was standardized in twenty twenty-four, and the I E E E is working on one point six terabits.',
 ]),
 dict(id="universe", beats=[
  "Zoom out. A supercomputer isn't one network: a compute fabric where collectives run, usually a separate storage fabric, an ordinary Ethernet for in-band management, and another, isolated, for out-of-band.",
  "File systems ride the same R D M A machinery. Lustre's network layer has an InfiniBand driver and a T C P one. BeeGFS can use I B verbs, and falls back to T C P. On Frontier, the Orion file system sits directly on Slingshot.",
  "On the June twenty twenty-six Top five hundred, the most common single interconnect is H P E's Slingshot eleven, on fifty-seven systems, one ahead of hundred-gig Ethernet. InfiniBand's N D R generation is about sixteen percent. The InfiniBand Trade Association, which has an obvious stake, counts two hundred ninety-three InfiniBand systems across all generations. Different groupings, so all of it can be true.",
  'In AI, both camps scale. In twenty twenty-four, Meta built two twenty-four-thousand G P U clusters, one on Rocky, one on InfiniBand, and reported running large jobs on both without network bottlenecks, after tuning.',
  "And it isn't settling. Slingshot is Ethernet-compatible. Ultra Ethernet one point oh arrived in June twenty twenty-five, version one point one this month, and the InfiniBand Trade Association's upcoming release includes a multipath transport for Rocky.",
 ]),
 dict(id="close", beats=[
  "So, honestly. R D M A, not InfiniBand, is what removed the software tax, and Ethernet has it.",
  "What InfiniBand still offers is an end-to-end design: credit-based links, a central routing brain, in-network reduction, and a long record of tuning at scale. What Ethernet offers is an open ecosystem, enormous switch radix, and a standards effort aimed squarely at those gaps.",
  "What I couldn't find is a fair, same-hardware benchmark of the two at scale. So measure your own workload. Latency and bandwidth with perftest. Collectives with N C C L tests, or the O S U micro-benchmarks. And watch for pause frames, retransmits, and link flaps.",
  "Sources, and every number I modeled myself, are in the notes that come with this video.",
 ]),
]

_SUBS = [
 (r"\bR D M A\b", "RDMA"), (r"\bRocky\b", "RoCE"), (r"\bI O\b", "I/O"), (r"\bI B M\b", "IBM"), (r"\bH P E\b", "HPE"),
 (r"\bH P\b", "HP"), (r"\bT C P\b", "TCP"), (r"\bC P U\b", "CPU"), (r"\bG P U\b", "GPU"), (r"\bE C N\b", "ECN"),
 (r"\bD C Q C N\b", "DCQCN"), (r"\bN D R\b", "NDR"), (r"\bX D R\b", "XDR"), (r"\bL I D\b", "LID"),
 (r"\bO S F P\b", "OSFP"), (r"\bI E E E\b", "IEEE"), (r"\bO S U\b", "OSU"), (r"\bN C C L\b", "NCCL"),
 (r"\bQ M ninety-seven hundred\b", "QM9700"), (r"\bConnect X seven\b", "ConnectX-7"), (r"\bConnect X eight\b", "ConnectX-8"),
 (r"\bI B verbs\b", "ibverbs"), (r"\bSharp\b", "SHARP"), (r"\bUp slash Down\b", "Up/Down"),
 (r"\bTop five hundred\b", "TOP500"),
]
def sub(text):
    for pat, rep in _SUBS:
        text = re.sub(pat, rep, text)
    return text

if __name__ == "__main__":
    tot = 0
    for s in SCENES:
        w = sum(len(b.split()) for b in s["beats"])
        tot += w
        print(f'{s["id"]:12s} beats={len(s["beats"]):2d} words={w}')
    print("total words", tot, "~minutes at 147 wpm:", round(tot / 147, 1))
