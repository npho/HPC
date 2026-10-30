"""Narration script.

Markup:  {Display|spoken}  -> subtitles show `Display`, the TTS receives `spoken`.
Numbers are written out as words on purpose (the TTS front-end is unreliable with
digits, symbols and math).  Every factual sentence is traced in notes/claims.md.
Each scene is a list of *beats*; scene code keys animations to beat start times.
"""
import re

SCENES = [
    dict(id="open", title="Topology", beats=[
        "Picture a thousand machines that all have to agree on one number. Every machine holds a piece, and to combine them, data has to move. How fast it moves depends less on the machines than on the wires between them: how many there are, and the pattern they make.",
        "That pattern is called a topology. This video is about the handful that supercomputers actually use, why each one exists, and what each one quietly assumes about the traffic it will carry.",
        "We'll spend most of our time on fat trees and their blocking factors, then tori, hypercubes, {HyperX|Hyper X} and dragonflies, and then on how collective algorithms and schedulers have to cooperate with them. The proprietary names get a short tour at the end.",
    ]),

    dict(id="history", title="Where these ideas came from", beats=[
        "Start in a telephone exchange. In nineteen fifty-three, Charles {Clos|Kloh} published a study of non-blocking switching networks in the Bell System Technical Journal. His three-stage design is the ancestor of nearly every data center fabric today.",
        "In the early nineteen eighties, Charles {Seitz|Sites} and his group at Caltech built the opposite kind of machine: many small computers wired directly to each other. The Cosmic Cube had sixty-four processors, each linked to six neighbors.",
        "Then, in quick succession: fat trees from Charles {Leiserson|Lyzerson} in nineteen eighty-five, virtual channels for deadlock-free torus routing from Dally and {Seitz|Sites} in nineteen eighty-seven, and Dally's argument, in nineteen ninety, that under the wiring limits of the time, low-dimensional networks win.",
        "Then the constraint flipped. By two thousand eight, routers with dozens of ports were practical, but long cables were not cheap. Kim, Dally, Scott and Abts proposed the dragonfly, and {HyperX|Hyper X} followed in two thousand nine.",
        "Every topology you'll meet is an answer to one question, asked under different constraints: what is cheap, what is expensive, and what traffic do you expect?",
    ]),

    dict(id="metrics", title="Four measuring sticks", beats=[
        "To compare topologies we need a few measuring sticks. Model the machine as a graph: endpoints, switches, and links.",
        "Diameter: the largest number of hops any message ever needs. It sets the floor on latency.",
        "Radix: how many ports a switch has. Silicon fixes it, and it's the constraint that shapes everything, because radix decides how many ways you can split your wires.",
        "Bisection bandwidth. Cut the machine into two equal halves, whichever way gives the smallest cut, and add up the bandwidth across it. If everything in one half talks to the other, all of it crosses that cut, so the cut is a ceiling. Divide by the bandwidth the endpoints can inject and you get a ratio I'll call beta. A beta of one means a full-speed permutation can, in principle, fit.",
        "But a ceiling is only a ceiling. A network can have a wide bisection and a narrower cut somewhere else, and for your traffic, the narrowest cut counts.",
        "The last stick is cost: ports, and cables, especially the long ones that need optics.",
    ]),

    dict(id="tree", title="Fat trees", beats=[
        "Start with a tree: machines on the leaves, switches climbing to a root. It's cheap, and it falls over the moment the left half talks to the right half, because everything squeezes through the root. The cut is one link wide.",
        "{Leiserson's|Lyzerson's} fix: make the links fatter as you climb, so capacity at each level matches the traffic below it. Now bisection grows with the machine.",
        "Nobody builds a fat link, though. You build a folded {Clos|Kloh}: many identical switches with k ports each. Half the ports face down to machines, half face up, and every leaf has one link to every spine. A spine can serve k leaves, each leaf has k over two machines, so a two-level tree holds k squared over two machines on three k over two switches.",
        "With sixty-four-port switches: two thousand forty-eight machines, ninety-six switches. Add a level and you get k cubed over four: sixty-five thousand five hundred thirty-six machines, five thousand one hundred twenty switches.",
        "And any two machines are at most six links apart, however large the cluster. Latency barely grows with scale. That's the fat tree's great trick.",
    ]),

    dict(id="oversub", title="Blocking factors", beats=[
        "Now the part people argue about. Those numbers assume half of every switch's ports go up. That's one-to-one, or non-blocking, and it's expensive: roughly one more cable per machine for every level of the tree.",
        "So designers cheat. Give each leaf forty-eight ports down and only sixteen up. The leaf now has three times as much bandwidth facing its machines as facing the network. Downlink over uplink bandwidth is the blocking factor, or oversubscription ratio. This one is three-to-one.",
        "The savings are real. With sixty-four-port switches, three-to-one reaches three thousand seventy-two machines on eighty switches, where one-to-one reached two thousand forty-eight on ninety-six. Switches per thousand machines fall from about forty-seven to about twenty-six, and uplink cables per machine fall from one to one third.",
        "What you give up shows up at one leaf. If all forty-eight machines send upward, they share sixteen uplinks, and each gets a third. How much that hurts depends on how much traffic leaves the leaf. A job that fits under one leaf never touches an uplink. A job spread across the cluster and talking to everyone gets about one over the blocking factor: in my model, thirty-four percent of line rate for this cluster.",
        "And the factors multiply: three-to-one at the leaf and three-to-one above it is nine-to-one across the top. So the question to ask about any cluster isn't whether it's a fat tree. It's the blocking factor at each level, and whether the scheduler packs jobs beneath it.",
    ]),

    dict(id="clos", title="What non-blocking really means", beats=[
        "There's a subtlety in the word non-blocking that took me a while to appreciate. {Clos|Kloh} proved it in nineteen fifty-three. Take a three-stage network, and build it with exactly n middle switches, where n is the number of inputs per switch. One-to-one.",
        "Watch. Two calls are up. A third arrives. Its input switch already uses the first middle switch; its output switch already uses the second. Every route is taken, though both ends are idle. The network has blocked.",
        "{Clos's|Kloh's} guarantee: use two n minus one middle switches. The new call's input switch blocks at most n minus one middle switches, its output switch at most n minus one more, so one is always free. That's strictly non-blocking, and it costs nearly twice the middle switches.",
        "A cheaper promise: with just n middle switches, any set of calls can be routed, if you may move calls already in progress. That's rearrangeably non-blocking. I checked both by brute force on the smallest case. With two middle switches, a hundred twenty-eight blocking states are reachable. With three, none. And with two, a rearrangement always exists.",
        "Every one-to-one fat tree is the rearrangeable kind. In a data center the calls are flows, and the rearranging is routing. Whether the wires you paid for get used depends on how flows are routed.",
    ]),

    dict(id="routing", title="Hashing versus planning", beats=[
        "Real switches mostly don't rearrange; they hash. Each flow picks a spine from its headers, blind to every other flow. Take a one-to-one fat tree, sixteen leaves of sixteen machines, and a random permutation. In my simulation, hashing gives the average flow about fifty-five percent of line rate, and the unluckiest flow about a fifth. Static routing by destination does better, around seventy percent.",
        "Now color the same traffic on purpose. {König's|Kernig's} theorem: a bipartite graph whose busiest node has n edges can be colored with n colors, so no node sees a color twice. Let leaves be nodes, flows be edges, spines be colors. A proper coloring is a conflict-free schedule. Across two hundred random permutations, every flow got full line rate.",
        "So a one-to-one fat tree has enough wire for any permutation. Whether it delivers depends on routing: hashing, adaptive routing in the switches, or a central planner like the InfiniBand subnet manager. The topology says what's possible. The routing decides what you get.",
    ]),

    dict(id="torus", title="Meshes and tori", beats=[
        "Now flip the whole idea. Put a small router in every node and wire each node to its neighbors. These are direct networks, and the simplest family is the k-ary n-cube: n dimensions, k nodes along each. A line is a one-dimensional mesh; join the ends and it's a ring. Wrap the rows and columns of a grid and you have a torus, and add a third dimension for the shape behind a lot of famous machines.",
        "The appeal: every node has just two n links, however big the machine. No giant switches, no growing radix, and almost every cable runs between neighbors.",
        "The price shows up in the measuring sticks. Diameter is n times k over two, so the worst-case path grows with the machine. Cut across one dimension, and wraparound means two planes of links are cut: two times k to the n minus one, which as a fraction of injection is four over k. Every time k doubles, beta halves. An eight by eight by eight torus has beta one half and diameter twelve. Sixteen cubed, four thousand ninety-six nodes, has one quarter and twenty-four.",
        "Here's all-to-all traffic with dimension-order routing. On a torus, symmetry spreads the load perfectly: every link carries the same. On a mesh, the central links carry a third more than average and saturate first. In my model, the torus sustains about twice the injection rate.",
        "Wraparound has a catch: deadlock. Four packets, each waiting for the channel the next one holds. Nobody moves. Dally and {Seitz's|Sites's} cure: two virtual channels per physical channel, and a packet switches to the second when it crosses a dateline. The cycle breaks. I built the channel dependency graph for small tori to check: a cycle without virtual channels, none with the dateline.",
        "Why build tori? Because a lot of science talks mostly to its neighbors, and a torus hands it short, dedicated links. Blue Gene L was a sixty-four by thirty-two by thirty-two torus, sixty-five thousand five hundred thirty-six nodes. Cut it across the long dimension and you cross two thousand forty-eight links at one point four gigabits per second per direction. By my arithmetic, three hundred fifty-eight gigabytes a second, close to the three hundred sixty in IBM's paper. Notice it also carried a separate tree network for reductions: a torus is built for neighbors.",
        "Fujitsu's Tofu went to six dimensions. The K computer was twenty-four by eighteen by sixteen groups of two by three by two: eighty-two thousand nine hundred forty-four nodes. Users ask for a three-dimensional shape, and the system guarantees that neighbors in their virtual torus are neighbors in the real network.",
        "Google's {TPU|T P U} version four pods: four thousand ninety-six chips as sixty-four cubes of four by four by four, joined through optical circuit switches that reconfigure in milliseconds, so a slice can be assembled from whichever cubes are healthy. Google's paper says all-reduce maps well onto tori while all-to-all strains the bisection, and that a twisted torus improved all-to-all throughput by one point six three and one point three one times on two slice shapes.",
    ]),

    dict(id="hyper", title="Hypercubes and HyperX", beats=[
        "Squeeze the torus's k down to two and you get the hypercube. Two nodes make a link, two links a square, two squares a cube, two cubes a four-dimensional hypercube. Each doubling adds a dimension, and a link per node. {Seitz|Sites} built the Cosmic Cube this way and wrote that simulation showed good message flow for irregular computations, and that a hypercube contains all the lower-dimensional meshes.",
        "The sticks look wonderful. With N nodes: diameter log two N, bisection N over two, beta of one. The catch is radix. Every node needs log two N links: for eight thousand nodes, thirteen links, and six and a half cables per node. The wiring is what hurts.",
        "{HyperX|Hyper X} generalizes it. Put switches on a grid and, along every row and column, connect each switch to every other: a full mesh instead of a ring. Two switches per row is a hypercube. One dimension is a fully connected graph. The diameter is just the number of dimensions.",
        "And you choose how many machines hang off each switch. On a sixteen by sixteen grid of two hundred fifty-six switches, eight machines per switch gives beta of one, sixteen gives one half, thirty-two a quarter. Fewer machines per switch buys bisection, at the price of more switches per machine.",
        "The authors are careful: a folded {Clos|Kloh} is generally more efficient when you need full bisection; {HyperX|Hyper X} shines with high-radix switches when you can live with less. And a research machine built with both a fat tree and a twelve by eight {HyperX|Hyper X} reported that, with pattern-aware routing, the {HyperX|Hyper X} can challenge or even outperform the fat tree.",
    ]),

    dict(id="dragonfly", title="Dragonflies", beats=[
        "By two thousand eight the problem had flipped again. Routers with dozens of ports were practical. Cables were the expense: the long ones, between cabinets, are optical and dominate the cost.",
        "The dragonfly's idea: wire all the routers in a group to each other with short cables, and treat the whole group as one giant virtual router. Then connect groups to each other, all to all, with one long cable per pair.",
        "Three numbers describe it: a routers per group, p machines per router, h global links per router. A group can reach a times h other groups, so the machine has a times p times, a times h plus one, machines. Load balances across machine, local and global channels when a equals two p equals two h.",
        "Take a of four, p and h of two: nine groups, seventy-two machines, any two at most three router hops apart. Slingshot is the same formula scaled up: a sixty-four-port switch, sixteen machines, thirty-one local links, seventeen global, for five hundred forty-five groups and two hundred seventy-nine thousand forty machines, the largest configuration in {HPE's|H P E's} paper.",
        "Kim and colleagues estimated that, from sixteen thousand nodes up, this cut cost by about twenty percent against a flattened butterfly and fifty-two against a folded {Clos|Kloh}, in their two thousand eight cost model.",
        "Now the weak spot: the single cable between two groups. If every machine in one group sends to the next, all of it needs that one link. With minimal routing, throughput falls to one over a times p: one eighth in my example.",
        "The cure is randomized routing: send each packet via a random intermediate group. Load spreads over every global link, at the price of a longer path. In my model the adversarial pattern improves from thirteen percent to forty-four, but uniform traffic falls from full rate to fifty-five.",
        "So real dragonflies are adaptive, choosing between minimal and non-minimal paths using queue depths. The details matter: the dragonfly paper found that local queues alone gave limited throughput and high latency on adversarial traffic. Slingshot estimates load from acknowledgments carried back with each packet. Variants chase the same goal: dragonfly-plus replaces the all-to-all group with a leaf-spine network, and Slim Fly pushes diameter down to two, with about twenty-five percent better cost-effectiveness in its authors' model.",
    ]),

    dict(id="compare", title="Side by side", beats=[
        "Side by side, then: concrete designs near eight to sixteen thousand endpoints, every number from building the graph and measuring it.",
        "The torus has no switches, but pays in cables and distance: three links per node, diameter thirty-two, beta of an eighth. The hypercube has full bisection and low diameter, but radix fourteen and six and a half cables per node.",
        "{HyperX|Hyper X} and dragonfly sit between: diameter two or three, under one and a half cables per endpoint, but switches with thirty to sixty ports. The one-to-one fat tree pays two cables per endpoint for full bisection.",
        "Nobody wins every column. Each topology is a bet on the traffic it will carry.",
    ]),

    dict(id="collectives", title="Collectives meet topology", beats=[
        "So far, wires. But the traffic on them isn't random. In {HPC|H P C} and {AI|A I} it's collective operations like all-reduce, and the shape of the algorithm decides which wires get used.",
        "The simplest cost model: sending n bytes costs alpha plus n over B, a startup plus time per byte. It ignores topology on purpose. In all-reduce, every one of p processes ends with the sum of everyone's vectors. The ring algorithm cuts the vector into p chunks and passes them around, in two times p minus one steps. Its bandwidth term, two times p minus one over p, times n over B, is the minimum possible; Patarasuk and Yuan proved the ring bandwidth-optimal on any tree-connected network, with one port per node.",
        "The price is latency: two times p minus one alphas. With a thousand processes and two microseconds per message, that's four milliseconds of startup. Recursive halving and doubling moves the same data in two log two p steps: forty microseconds.",
        "That gap is why trees came to {GPU|G P U} collectives. NVIDIA's {NCCL|N C C L} team wrote that ring latency grows linearly with the number of {GPUs|G P U's}, and reported up to a hundred eighty times lower latency with a double binary tree at twenty-four thousand {GPUs|G P U's} on Summit.",
        "Across message sizes: for small messages, startup dominates and the logarithmic algorithms win. For large ones the bandwidth term dominates, and ring and halving-doubling converge.",
        "But the model left something out: it assumes every pair can talk at full speed at once. A ring only talks to neighbors, which is gentle on any network that can lay a ring over itself. Recursive halving starts by swapping half the vector with a partner half a machine away.",
        "Put both on an oversubscribed tree: sixteen leaves of thirty-two machines, four-to-one. Ring with ranks in order: no slowdown, since each leaf sends one stream upward. Same ring with ranks shuffled across leaves: four times slower. Recursive halving with ranks in order sends its biggest messages the farthest, through the uplinks: three point eight times slower. Reorder so big messages go to near neighbors first, and it's one point oh nine.",
        "Same cluster, same algorithms, a factor of four, decided entirely by who talks to whom. That's why topology-aware libraries exist, and why your launcher's rank order is not a detail. These numbers are from my idealized model, which sprays traffic perfectly across the spines, isolating placement from hashing.",
    ]),

    dict(id="place", title="Placement", beats=[
        "Collectives assume you know where the ranks live. Placing them is the scheduler's job, and each topology asks something different of it.",
        "On a fat tree, the scheduler must know which nodes share a leaf. In Slurm you describe the switch hierarchy in {topology.conf|topology dot conf}; the tree plugin finds the lowest switch that can hold the job and allocates best-fit beneath it. Users can cap the number of leaf switches, and say how long they'll wait for it: trading queue time for locality. A newer block topology allocates contiguous blocks of nodes, aiming to limit fragmentation.",
        "On a torus, the problem is geometric: a job wants a contiguous box, and free nodes can add up to enough without forming one. Slurm has a torus plugin; Tofu lets users ask for a shape; and Google's optical switches remove contiguity entirely. Their paper says that without them, host availability would need to be ninety-nine point nine percent for reasonable slice goodput.",
        "Dragonflies tolerate scattered placement if routing is adaptive, but studies found limits. {Bhatele|Bah-tay-lay} and colleagues found hot spots on a few links for applications with few neighbors per task. Yang and colleagues found that random placement with adaptive routing balances load, but communication-heavy jobs can degrade lighter ones, a bully effect, and a hybrid placement reduced the worst case.",
        "{HPE's|H P E's} answer was to fight interference in the network. In its paper, worst-case congestion slowdown was one point three times on Slingshot against ninety-three on Aries. Those are the authors' benchmarks, so treat them as a claim to test. Across all of these, topology isn't a property of the cables alone: it's cables, routing, algorithm and placement, agreeing.",
    ]),

    dict(id="zoo", title="The proprietary interconnects", beats=[
        "Now a quick tour of the proprietary interconnects: what existed, why it was built, whether it still matters.",
        "Myrinet, from Myricom: a cluster network with low-overhead switching and link-level flow control, when mainstream Ethernet was a hundred megabits. In June two thousand five, Myricom reported a hundred forty-one {TOP500|Top five hundred} systems, twenty-eight percent. By June two thousand fourteen, one. Its assets were sold in two thousand thirteen. History. Quadrics {QsNet|Q S net}, a fat-tree network with adapters that took communication work off the processor, powered six of the ten fastest machines in June two thousand three, and the company closed in June two thousand nine. Also history.",
        "IBM's Blue Gene put tens of thousands of simple nodes behind a torus, with tree and barrier networks; its last generation, Q, used a five-dimensional torus, and IBM then moved to other platforms. Fujitsu's Tofu is the six-dimensional torus we met; the {Fugaku|Foogahkoo} version has six network interfaces per node and six point eight gigabytes a second per link, and {Fugaku|Foogahkoo} is number nine on the June two thousand twenty-six list.",
        "Cray went from a three-dimensional torus to Aries in two thousand twelve, a dragonfly it described as fat-tree all-to-all bandwidth at torus-like cost, with at most five hops at any size. Then Slingshot: sixty-four ports at two hundred gigabits, Ethernet-compatible, with hardware congestion management, aimed at InfiniBand's tuning difficulty and the gateways Ethernet needed. It's the live one: El Capitan, Frontier, Aurora, and six of the top ten.",
        "Intel's Omni-Path launched in two thousand fifteen as a lossless alternative to InfiniBand, ran Trinity and Cori, and was dropped by two thousand nineteen. Cornelis Networks spun out in two thousand twenty, and launched four-hundred-gigabit {CN5000|C N five thousand} in two thousand twenty-five. And the new number one, {LineShine|Line Shine}, is reported to use a proprietary interconnect called {LingQi|Ling Chee}, described by one outlet as a multi-rail fat tree. I couldn't confirm that from a second source.",
        "My read, which is interpretation, not a sourced claim: the ones that died were out-competed on cost and volume by Ethernet and InfiniBand; the ones that survive are tied to a builder's whole machine.",
    ]),

    dict(id="close", title="Three ideas", beats=[
        "Three ideas to keep. One: bisection is a ceiling, not a promise. The narrowest cut for your traffic decides what you get, and routing decides whether you reach it.",
        "Two: every topology is a bet on traffic. Neighbor-heavy science favors tori. Permutations and collectives favor fat trees. Cable-limited scale favors dragonflies and {HyperX|Hyper X}, if you trust the adaptive routing.",
        "Three: wires, routing, algorithm and placement have to agree. Change any one, and the same hardware can be several times faster or slower.",
        "To test this on a real cluster, here's a suggestion of mine, not a standard method: measure all-to-all bandwidth inside one leaf, then across leaves, then across the whole machine. The drop-offs are the blocking factors, measured.",
        "Sources, and the status of every number, verified or modeled, are in the notes that come with this video.",
    ]),
]

_RX = re.compile(r"\{([^|{}]+)\|([^|{}]+)\}")


def split_sentences(text):
    """Split into sentences for subtitles (keeps markup intact)."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z{])", text.strip())
    return [p for p in parts if p]


def display(text):
    return _RX.sub(lambda m: m.group(1), text)


def spoken(text):
    return _RX.sub(lambda m: m.group(2), text)


def word_count():
    return sum(len(spoken(b).split()) for s in SCENES for b in s["beats"])


if __name__ == "__main__":
    n = word_count()
    print(f"{len(SCENES)} scenes, {sum(len(s['beats']) for s in SCENES)} beats, {n} words, ~{n/175:.1f} min at 175 wpm")
    for s in SCENES:
        w = sum(len(spoken(b).split()) for b in s["beats"])
        print(f"  {s['id']:12s} {len(s['beats']):2d} beats {w:4d} words  ~{w/175*60:5.0f}s")
