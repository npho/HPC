# Narration script. Each scene = list of lines; each line = one visual "beat".
# Written to be spoken (not read off the screen). Numbers spelled out for TTS.
SCRIPT = [
("s0", [
 "Picture ten thousand processes running one simulation. At some instant, every one of them finishes a timestep and says: I need to save my piece of the answer. Right now.",
 "One disk can't take that. One server can't either. A single box has a ceiling, and ten thousand writers hit it immediately.",
 "So the question behind high performance storage isn't really how to store bytes. It's this: how do thousands of machines share one file system, reading and writing it at the same time, and still agree on what's in it?",
 "In this video we'll look at one of the oldest, most widely deployed answers: G P F S, the General Parallel File System, which IBM now calls Storage Scale. A little history first, then most of our time on how it works, and finally what real systems look like.",
]),
("s1", [
 "The story starts at IBM in the early nineteen nineties, with two research efforts. At the Watson lab, Vesta explored how parallel programs could partition files across disks. At Al muh den, in California, Tiger Shark was built for something that sounds unrelated: streaming multimedia.",
 "But video means many steady streams, served from an array of disks. So you stripe everything, and never let one disk become the hot spot. That's exactly what a scientific code writing a checkpoint wants, too.",
 "The two lineages merged into G P F S, around nineteen ninety eight, with the standard Unix interface, so ordinary programs just worked. The foundational document is a two thousand two paper at the FAST conference, from two Al muh den researchers. Its three big ideas, shared disks, wide striping, and distributed locking, are still the skeleton of the system.",
 "It describes A-S-C-I White, a five hundred twelve node machine with a hundred and forty terabytes of disk, where sixteen nodes could drive the machine's entire twelve gigabytes per second of I O bandwidth. Hold on to those numbers. We'll compare them with a modern system later.",
 "Since then: Spectrum Scale in twenty fifteen, when IBM put that prefix on its storage products, and Storage Scale in early twenty twenty three, when the prefix was dropped. Same lineage, same core design.",
]),
("s2", [
 "Let's start with the first big idea: striping. Take a file and chop it into blocks. Now take the disks, and deal the blocks out round-robin, like cards.",
 "A file written this way isn't on one disk; it's on all of them. Read it, and every disk works at once, so bandwidth adds up. The paper is explicit that this happens inside the file system itself, across several thousand disks in the largest installations of the day.",
 "Block size matters enormously. Disks are great at streaming and terrible at repositioning. If every request pays a fixed positioning cost, small blocks spend their time moving, and big blocks spend it transferring. In the two thousand two paper, a typical block was two hundred fifty six kilobytes, configurable up to a megabyte. On Oak Ridge's Summit, it's sixteen megabytes.",
 "There's a catch: most files are small. If each consumed a whole sixteen megabyte block, you'd waste nearly everything. So blocks are divided into subblocks, as small as one thirty second of a block in the paper, and small files and file tails get only the fragments they need.",
]),
("s3", [
 "Now, who does what? In the purest shared-disk setup, every node sees every disk through a storage network. That works, but it gets impractical with thousands of compute nodes.",
 "So big systems add a layer. Disks are exposed as N S D's, network shared disks. A smaller set of N S D servers attach to the storage, and everyone else reaches the disks across the network, through them. To a client it still looks like one shared pool, which is why the paper calls the design shared-disk.",
 "The N S D servers are not the brains, though. They move blocks. The intelligence is spread across ordinary nodes in assigned roles. A few are quorum nodes, and one of those is the cluster manager: it hands out leases, detects failures, and runs recovery.",
 "Each file system also gets a file system manager, for disk configuration, space allocation and quotas. Then there are token managers, several of them, each owning a slice of the lock state, divided up by eye-node number.",
 "Apart from the quorum role, every node is identical, and roles can move. If the cluster manager dies, the quorum nodes elect another. To avoid a split brain, only the group holding a majority of nodes may keep using the file system. The minority is fenced off from the disks.",
]),
("s4", [
 "Here's the problem everything else is built around. Posix promises that if one process writes and another then reads, the reader sees the write, even across machines. G P F S keeps that promise across the whole cluster; the paper's phrase is single-node-equivalent semantics. How, without asking a central server for permission on every operation?",
 "The answer is tokens. A token is a permission slip: this node may cache and operate on this object, in this way. The token manager hands them out, and each node's local lock manager makes fine-grained decisions with no network round trip, for as long as the node holds the right token.",
 "For file data, tokens are byte ranges. The first node to write a file gets a token for the entire file. If nobody else shows up, it never talks to the token manager again. Now a second node wants to write the back half. The first node is asked to give up part of its range, the range splits, and now both write in parallel with no further coordination.",
 "Notice that the ranges get rounded to block boundaries. That's deliberate, and it's why alignment matters. If two nodes write different bytes inside the same block, they need the same token, and the token, along with the dirty data, ping-pongs between them.",
 "The eye-node has a similar problem. Every writer changes the file's size and modification time, and if each updated the eye-node on disk, it would be a stampede. So G P F S elects a metanode for each open file. Writers send eye-node changes to it, and it alone reads and writes that eye-node on disk. For truly fine-grained sharing, the paper also describes data shipping, where each block has an owner and everyone else sends their I O to it.",
 "You can see all of this in a benchmark. On Summit's file system, the I O five hundred test, with five hundred and four nodes, has an easy mode, where every process writes its own file, and a hard mode, where all of them write small, unaligned, interleaved chunks into one shared file. Easy: about two terabytes per second. Hard: about half a gigabyte per second. A factor of roughly thirty eight hundred, on identical hardware.",
 "The slide doesn't break down why, but the cost of sharing blocks, token traffic and partial block read-modify-write, is the usual suspect. Reads are far more forgiving: about sixty five times slower, instead of thirty eight hundred.",
]),
("s5", [
 "Three more mechanisms keep this from falling over at scale. First, directories. A directory with millions of entries can't be a linear list. G P F S uses extensible hashing, so finding a name takes a single directory block access, however large the directory gets.",
 "Second, space allocation. The free-space map is cut into many independently lockable regions. An allocation manager hands a region to a node, and from then on that node can allocate blocks from it without asking anyone. Nodes spread out across regions, instead of colliding on one.",
 "Third, failure. Every node writes a write-ahead log for each file system it mounts, and that log lives in the file system, on the shared disks. That detail matters. When a node dies, any other node can read its log off the shared disks and replay it, restoring consistency without waiting for the dead node to come back. The paper is careful to note that user data isn't logged, only the metadata structures.",
 "Put those together and there's no single metadata server, no single lock server, and no one place where the whole system has to wait.",
]),
("s6", [
 "So far, nodes and locks. What about the disks? At scale, disks fail constantly. In a traditional RAID group, a rebuild hammers the few disks in that group, and every rebuilt byte lands on one spare. With today's drive sizes that takes a long time, and the array is exposed the whole way.",
 "IBM's answer is G P F S Native RAID, later called Spectrum Scale RAID. It moves the RAID function out of a hardware controller and into software on the N S D servers. The key technique is declustering.",
 "Instead of fixed groups, each stripe is spread across disks chosen all over the array, and the spare space is spread too. When a disk dies, its data is rebuilt by reading from every surviving disk and writing into spare space on every surviving disk. Everybody shares the work. IBM's documentation says this can make the impact of a rebuild three to four times smaller than with conventional RAID.",
 "To build intuition, I ran a toy simulation: same disks, one failure, eight plus two coding. A rebuild can go only as fast as its busiest disk. With sixty disks, declustering cuts that load about six-fold, and the gain grows with the disk count. That's bigger than IBM's three to four times, as expected, since real systems also have networks, processors, and live application traffic. Trust the documentation's number; use the model for the shape of the idea.",
 "Data is protected by Reed-Solomon codes, eight data strips plus two or three parity strips, or by plain three-way or four-way replication. The trade is capacity: eighty percent, seventy three percent, thirty three, and twenty five percent efficiency, before spare space.",
 "And because silent corruption is real, the client appends an eight byte checksum to data before it leaves, and the server verifies it, and checks again on read. Flaky disks aren't kicked out immediately: a disk hospital times out an operation after about ten seconds, then diagnoses whether the disk or its path is at fault, while redundancy keeps serving reads.",
 "All of that runs on IBM's Elastic Storage Server: two POWER servers physically connected to the same disk enclosures. Each serves a recovery group and stands ready to take over the other's. Enclosures come in flavors like five-U boxes with eighty four nearline SAS bays for capacity, and two-U boxes with twenty four SSD slots for speed.",
]),
("s7", [
 "Let's zoom out to what a real deployment looks like. The common HPC shape has three tiers. On the left, hundreds or thousands of compute nodes running the Scale client. In the middle, a fast fabric, InfiniBand or Ethernet. On the right, a set of building blocks: servers with storage behind them.",
 "Inside the file system, you carve storage into pools. Typically a fast pool for metadata, and larger, cheaper pools for data. A policy engine, which scans eye-nodes in parallel, places new files in the right pool, and migrates or deletes old ones based on attributes like age, size, or owner.",
 "Filesets carve the namespace into subtrees with their own quotas, and independent filesets can have their own eye-node space. Failure groups tell the system which disks share a fate, a power supply, an enclosure, a rack, so two replicas land in different groups.",
 "Clusters can reach beyond themselves, too. Remote cluster mounts let one cluster mount a file system owned by another, and A F M, Active File Management, caches data asynchronously between sites, for disaster recovery or data sharing.",
 "There's even a shared-nothing flavor, File Placement Optimizer, released in twenty twelve, where each node's local disks contribute to the pool. And a software-only edition, Erasure Code Edition, that runs the declustered RAID on ordinary servers.",
 "The biggest example I can verify from public sources is Alpine, Oak Ridge's file system for the Summit supercomputer: two hundred fifty petabytes, served by a hundred fifty four N S D servers on a hundred gigabit InfiniBand, with a sixteen megabyte block size. Its peak is about two and a half terabytes per second sequential, and two point two random.",
 "Compare that with A-S-C-I White. Capacity is about eighteen hundred times bigger; bandwidth, about two hundred times. So reading the entire file system once took A-S-C-I White about three hours, and would take Alpine about twenty eight. Capacity has outrun bandwidth, a basic fact of HPC storage and a big reason tiers and policies exist. It's a rough comparison, since machines, years, and measurements differ, but the direction is the point.",
]),
("s8", [
 "Where does this sit in the larger HPC picture? In the middle of a hierarchy. Fast memory and node-local storage near the compute. A big parallel file system like this one for scratch and project data. And below it, campaign storage, object stores, and tape, with policy engines moving data between the layers.",
 "G P F S isn't the only parallel file system. Lustre, BeeGFS and others make different architectural choices. Lustre, for example, separates dedicated metadata servers from object storage servers. Those are different design philosophies, and that deserves its own video.",
 "And the file system is only half of performance. Your I O pattern is the other half. In one Oak Ridge example, tuning M P I I O collective buffering hints took a benchmark's write rate from about fifteen hundred megabytes per second to as high as thirty five thousand, roughly twenty three times faster, on the same hardware.",
]),
("s9", [
 "So, what to carry away. G P F S stripes everything across everything. It shares the disks, but distributes the intelligence: tokens instead of one lock server, a metanode instead of a metadata bottleneck, and logs on shared disks, so anyone can recover anyone.",
 "It protects the disks with declustered RAID in software. And when it's configured well, an application that writes large, aligned, mostly independent chunks sees close to the full bandwidth of the hardware, while one that fights over small shared blocks does not.",
 "If you want to go deeper, start with the original paper, then IBM's Spectrum Scale RAID administration guide, and Oak Ridge's published Alpine slides. All of them are cited on screen. A natural next step is Lustre, and seeing exactly where the philosophies diverge.",
]),
]
