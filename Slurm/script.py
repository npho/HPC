"""
script.py - the voice-over, scene by scene.

Each scene is a list of "beats": 1-3 sentences that the narrator says in one breath. The video is
timed from the synthesized length of each beat, and every animation is keyed to a beat start, so
picture and voice stay locked together without word-level alignment.

The narration deliberately does NOT read the on-screen labels; it explains what the picture shows.
Technical tokens are written naturally here; audio.py respells them for the speech engine.
"""

SCENES = [
    dict(id="s00_title", chapter="", beats=[
        "Every supercomputer has the same quiet problem: a few thousand identical machines, a few "
        "hundred people who all want them at once, and no obvious way to decide who goes first. "
        "This is a first-principles tour of Slurm, the software that answers that question.",
    ]),

    dict(id="s01_plane", chapter="Q", beats=[
        "Picture the cluster as a plane. Nodes run up the side, time runs along the bottom, and a "
        "job is a rectangle: this many nodes, for this long. Scheduling is packing those rectangles "
        "into the plane without overlap.",
        "But geometry isn't the whole story, because the rectangles come from people, with budgets, "
        "deadlines, and opinions about fairness. So a scheduler really answers four questions.",
        "Who is allowed to run? Who goes first? Where does the job land? And how is it started, "
        "watched, and cleaned up? Everything in Slurm answers one of those four.",
    ]),

    dict(id="s02_history", chapter="H", beats=[
        "Batch scheduling predates Linux clusters. Condor began in Wisconsin in 1988. The Portable "
        "Batch System started as a NASA contract in 1991. LSF, which grew from a Toronto research "
        "project, and IBM's LoadLeveler filled out the field.",
        "Slurm starts around 2002 at Lawrence Livermore National Laboratory, for the large Linux "
        "clusters the lab was buying. Its authors surveyed what existed and, in their words, found "
        "nothing that was simple, highly scalable, and portable. The paper never names the systems "
        "it surveyed.",
        "Their evidence was a launch test on a thousand nodes in November 2002: about as fast as "
        "Quadrics RMS, and roughly eighty times faster than LoadLeveler, at the sizes tested.",
        "Two design choices echo through everything later. The default scheduler was deliberately "
        "plain, first in, first out, with real policy left to an external scheduler like Maui or "
        "Livermore's own DPCS. And every site-specific piece, authentication, interconnect, "
        "scheduling, was a plugin.",
        "Over two decades, priorities, fair-share, backfill and accounting moved inside. The "
        "developers founded SchedMD in 2010, the acronym was retired in 2012, and in December 2025 "
        "Nvidia announced it was acquiring SchedMD, promising Slurm would stay open source and "
        "vendor neutral.",
        "You'll see claims that Slurm runs most of the Top500: about sixty percent in 2021 per "
        "Wikipedia, and more than half of the top ten and top hundred per Nvidia. Treat those as "
        "secondary and vendor figures, not a census.",
    ]),

    dict(id="s03_anatomy", chapter="W", beats=[
        "Now the machinery. A cluster is a handful of daemons. At the center, the controller, "
        "slurmctld, holds the whole queue and the state of every node, and decides what runs. One "
        "is active, with an optional backup.",
        "On every compute node runs slurmd, which accepts work, starts it, and reports back. Off "
        "to the side, slurmdbd sits between Slurm and a MariaDB or MySQL database and keeps the "
        "accounting history.",
        "Every message is authenticated, usually with a shared secret called MUNGE, so clocks, "
        "user IDs, and group IDs have to agree everywhere. Login nodes, where people sit, run the "
        "client commands and need the key too.",
        "Here's a scaling trick. If the controller messaged ten thousand nodes itself, it would "
        "drown. So it messages a few, and each forwards to sixteen more. Sixteen, plus two hundred "
        "fifty-six, plus four thousand ninety-six: three hops reach forty-three sixty-eight nodes. "
        "That width is a setting called TreeWidth.",
        "If the controller dies, a backup sharing its state directory takes over, after two minutes "
        "by default. If the database is down, the controller keeps working and queues accounting "
        "records for later, within limits.",
        "And nobody wants to copy configuration to ten thousand machines, so modern Slurm can run "
        "configless: each slurmd just asks the controller for its configuration at startup.",
        "Now place the hardware around it: login nodes, a controller, a database host, racks of "
        "compute nodes on a management network, and a fast fabric for the jobs. Beside them, the "
        "parallel file system from the earlier GPFS, Lustre and BeeGFS videos. Slurm schedules "
        "compute; the file system is simply something every node mounts.",
    ]),

    dict(id="s04_vocab", chapter="V", beats=[
        "Now the vocabulary, because Slurm's nouns are its design. A node is a machine described by "
        "sockets, cores, threads, memory, and devices like GPUs, plus a state: idle, allocated, "
        "draining, down.",
        "A partition is a named set of nodes with rules: a maximum run time, who may submit, a "
        "priority tier. Think of it as a queue. The 2003 design kept partitions disjoint; today "
        "they may overlap, so one node can serve a short queue and a long one.",
        "A job is an allocation: resources, for a time limit, to a user. Inside it, steps, "
        "launched with srun, are the actual parallel programs.",
        "Now, who is allowed what. An account is a node in a tree, a lab or department, containing "
        "sub-accounts and users. A user under an account, on a cluster, optionally within a "
        "partition, is an association. Limits and fair-share shares live on associations.",
        "A QOS, quality of service, is a named bundle of rules a job can request: a priority bump, "
        "limits, a usage multiplier, who it may preempt. Think normal, high, and preemptible "
        "standby.",
        "Everything measurable is a TRES, a trackable resource: CPUs, memory, nodes, GPUs, "
        "licenses, and a weighted sum called billing. Limits and usage are written in these units.",
        "When limits disagree, Slurm walks a ladder and takes the first place a limit is defined: "
        "partition QOS, then the job's QOS, then the user's association, then parent accounts, "
        "then the cluster root, and finally the partition. The documentation's example: the "
        "partition says twenty jobs, the user's association says four, so twenty wins. One flag "
        "swaps the first two rungs.",
    ]),

    dict(id="s05_job", chapter="L", beats=[
        "Follow one job. You run sbatch. The command packages your request with your user and "
        "group, sends it to the controller, and gets a job number back almost immediately, before "
        "anything has run.",
        "Inside the controller, submit plugins may rewrite the request, then it's validated against "
        "partitions and limits. If it can't start now it becomes pending, with a recorded reason: "
        "priority, resources, a dependency.",
        "When the scheduler picks it, a selection plugin chooses specific cores, memory and "
        "devices, topology permitting. The job is configuring while prologs run, then running.",
        "For a batch script, the first node starts a small process, slurmstepd, which runs your "
        "script. When the script calls srun, a step is born. The controller picks the step's "
        "resources inside your allocation and signs a credential, srun sends the launch to the "
        "first node's slurmd, and that forwards along the same tree. The controller is not "
        "involved in launching tasks, which keeps it light.",
        "Each node's step process sets up the MPI plumbing and network, creates a container to "
        "track processes, drops to your user ID, wires input and output, and forks your tasks.",
        "At the end, or when time runs out, tasks get a polite signal, a grace period, then a "
        "kill. The epilog runs, the node reports in, completing becomes idle, and the accounting "
        "record goes to the database.",
    ]),

    dict(id="s06_priority", chapter="F", beats=[
        "Now, who goes first. Every pending job gets one number, a weighted sum of factors each "
        "between zero and one: how long it has waited, how under-served its account is, its size, "
        "its partition, its QOS, and a few more.",
        "The weights are yours to set, and by default every one is zero, so none of these factors "
        "count until an administrator decides what matters.",
        "One subtlety: priority is not the first comparison. The documented order is: jobs that "
        "can preempt, then jobs in an advanced reservation, then the partition's priority tier, "
        "and only then the priority number, then submit time, then job ID.",
    ]),

    dict(id="s07_fairshare", chapter="F", beats=[
        "The factor that gives Slurm its character is fair-share. Each association holds shares, a "
        "claim on the machine, and usage is charged against it. Under-use your claim and your jobs "
        "rise; over-use it and they sink.",
        "In the classic formula, the factor is two to the minus U over S, usage over shares. Use "
        "exactly your share and you sit at one half. Use nothing and you approach one. Use far "
        "more and you approach zero.",
        "Usage isn't forever. It decays with a half-life, seven days by default, so last month's "
        "burst fades. Reset periods can also zero usage on a schedule, for hard quotas.",
        "Since version nineteen oh five the default is Fair Tree. At each level of the account "
        "tree, siblings are ranked by shares over usage, and then the tree is walked depth first. "
        "So if one account outranks its sibling, every user in it outranks every user in the "
        "other, however heavily any one of them has been running.",
        "It's a hierarchy of promises, not a quota. Fair-share never blocks a job. It only orders "
        "the queue.",
    ]),

    dict(id="s08_backfill", chapter="F", beats=[
        "A priority-sorted queue has a flaw. Suppose the top job needs the whole machine, but half "
        "of it is busy for another three hours. Strict order leaves the other half idle, waiting.",
        "Backfill looks ahead. It knows when running jobs should end, from their time limits, so "
        "it can work out when the top job can start, reserve that slot, and let smaller jobs jump "
        "the line only if doing so doesn't delay anyone ahead of them. Nodes held for those future "
        "reservations show up as planned.",
        "I wanted to test the folklore, so I built a toy: a hundred twenty-eight nodes, a "
        "heavy-tailed mix of job sizes, thirty random workloads. Compared with strict first in, "
        "first out, backfill cut the average wait from about eleven hours to about two.",
        "Then I made everyone pad their time limits, by factors from one and a half to ten. Waits "
        "didn't get worse; they improved slightly, from about one point nine hours to about one "
        "point four, which echoes a 2001 paper by Mu'alem and Feitelson. What got worse was the "
        "forecast: at double the true runtime, promised start times were off by about five hours "
        "on average, and at ten times, more than a day.",
        "So the honest reading is narrow. In this toy, accurate limits buy honest predictions, not "
        "speed. It ignores killing jobs at their limit, partial-node jobs, and the way real users "
        "round their estimates, so don't carry the numbers anywhere. But be suspicious of the "
        "slogan that padding always hurts everyone.",
        "In practice you tune how often backfill runs, how far ahead it looks, and how many jobs "
        "it tests. The defaults are every thirty seconds, one day ahead, at one-minute resolution.",
    ]),

    dict(id="s09_preempt", chapter="F", beats=[
        "Sometimes waiting isn't acceptable. Slurm can preempt, either by partition priority tier, "
        "where a higher tier displaces a lower one, or by QOS rules in the database.",
        "What happens to the victim is a mode: cancel it, requeue it, or suspend it and resume it "
        "later. An optional grace time lets a job that checkpoints save its work first. That's the "
        "machinery behind cheap, interruptible standby queues.",
    ]),

    dict(id="s10_place", chapter="P", beats=[
        "Where does a job land? Today's default selection plugin treats cores, memory, and GPUs as "
        "individually consumable, so several small jobs can share one node, unless a partition is "
        "set to give whole nodes.",
        "Devices are declared as generic resources, GRES: a name, a type, device files, and which "
        "cores sit close to them. NVIDIA GPUs can be auto-detected, though the count is still "
        "configured. Jobs ask by count: per node, per socket, per task.",
        "Declaring isn't enforcing. For that, Slurm leans on Linux cgroups: one plugin confines a "
        "job to its cores, memory, and devices, another tracks every process the job spawns, so "
        "nothing escapes cancellation.",
        "Billing weights, set per partition, turn all that into one currency. If a GPU is worth "
        "ten cores, say so in the weights, and fair-share and limits charge accordingly.",
    ]),

    dict(id="s11_topology", chapter="P", beats=[
        "Placement has geometry too. Tightly coupled jobs talk constantly, and traffic crossing "
        "fewer switches suffers less contention. Describe the network as a tree of switches, and "
        "Slurm finds the lowest switch that can host the job, then fills it best-fit. Users can "
        "even cap the leaf switches they'll accept, and how long they'll wait for that. The docs "
        "suggest describing leaf switches plus one top level, not every link.",
    ]),

    dict(id="s12_setups", chapter="S", beats=[
        "So what does a typical configuration look like? A small lab cluster might be one "
        "partition, no accounting database, and first-in first-out: a few lines in one file. That "
        "is a perfectly good place to start.",
        "A campus-scale cluster adds the database, and with it most of this video: partitions by "
        "hardware class, accounts per research group, a few QOS levels for normal, urgent, and "
        "preemptible work, fair-share weights, and the cgroup plugins to enforce it.",
        "And for clouds, power-saving hooks let Slurm call your scripts to boot nodes when jobs are "
        "waiting and tear them down when idle. That's how a cluster bursts into a cloud, or lives "
        "there entirely.",
        "Whatever the shape, the order of work is the same: nodes, partitions, then accounts and "
        "limits, then priority, then enforcement.",
    ]),

    dict(id="s13_universe", chapter="U", beats=[
        "Zoom out. Slurm sits in the middle of a stack. Above it, your program, perhaps MPI or a "
        "deep-learning framework, which Slurm helps launch and wire together. Below it, Linux and "
        "its cgroups, then the hardware.",
        "It doesn't move your data or tune your file system; those are other worlds. What it owns "
        "is time and ownership on shared hardware. The documentation reports validating five "
        "hundred simple batch jobs per second, sustained.",
        "So, the four questions again. Who may run: accounts, QOS, limits. Who goes first: "
        "priority, fair-share, backfill, preemption. Where: nodes, consumable resources, GPUs, "
        "topology. How: daemons, launch path, cgroups, accounting. Learn those four and any Slurm "
        "configuration becomes readable.",
        "Everything here comes from SchedMD's documentation and source and the original papers; "
        "the models are mine and are marked. The notes file lists what I couldn't verify.",
    ]),
]
