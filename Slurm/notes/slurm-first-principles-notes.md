# Slurm first-principles notes (companion to the explainer video)

Facts below were checked against the sources fetched during the build (SchedMD docs and man pages, a clone of the Slurm source tree, the two 2003 papers' bibliographic records). Anything I derived or modeled is flagged. Where sources disagreed or said nothing, I say so.

## Origins (secondary + primary)
- Two 2003 publications describe the original design: Yoo, Jette and Grondona, "SLURM: Simple Linux Utility for Resource Management", JSSPP 2003 (LNCS 2862); and Jette and Grondona's ClusterWorld 2003 / LLNL report (the PDF at slurm.schedmd.com/slurm_design.pdf is this one, not the JSSPP paper; I mixed them up at first and corrected it via Crossref and the repo's publications page).
- The authors' stated gap in 2002: nothing simple, highly scalable and portable. The paper does not name the systems it surveyed; the video says so.
- Launch-time comparison (Nov 2002, 1,000 nodes, trivial program): ratios are from the paper's text (Slurm about equal to Quadrics RMS, IBM LoadLeveler about 80x slower). The paper gives no table of absolute times.
- The 2003 design had disjoint partitions and a plain FIFO scheduler, with priorities and policy delegated to an external scheduler (Maui, LLNL's DPCS) through plugins. Today partitions may overlap.
- Acronym retired: "SLURM" became "Slurm". SchedMD founded about 2010 (SchedMD FAQ). NVIDIA announced it would acquire SchedMD on 15 Dec 2025 (NVIDIA blog).
- Adoption share: Wikipedia cites about 60% of TOP500 systems as of Nov 2021. Secondary, old; shown as such on screen.

## Architecture
- slurmctld (controller; optional backup), slurmd on each compute node, slurmdbd (accounting) in front of MariaDB/MySQL, slurmstepd per job step, login nodes running sbatch/srun/squeue.
- Authentication: MUNGE (auth/munge) or Slurm's own auth/slurm; same key everywhere; clocks and uid/gid must agree.
- Message fan-out: TreeWidth default 16 per slurm.conf(5); the man page's own arithmetic gives 16 + 256 + 4,096 = 4,368 nodes in three hops.
- Backup controller takes over after SlurmctldTimeout (default 120 s). If slurmdbd is down, the controller queues accounting records and drops them if its queue overflows.
- Configless mode (slurmd fetches config from the controller; --conf-server or DNS SRV record) is on by default since 20.02 per the docs.

## Vocabulary
- Node states shown: idle, allocated, draining, down (sinfo man page; extracted by .SH section after a first slice grabbed the wrong section).
- Partition = named node set with limits (MaxTime etc.); may overlap.
- Association = (cluster, account, user [, partition]) in the accounting tree; shares live on associations.
- QOS carries priority, UsageFactor, limits and preemption rules. Values on screen are illustrative.
- TRES: cpu, mem, node, gres/..., license, billing. Billing weights doc example: CPU=1.0, Mem=0.25 per GiB.
- Limit precedence (resource_limits docs, as shown): partition QOS, job QOS, user association, account association(s) walking upward, cluster/root association, partition limit. OverPartQOS flag swaps the first two. The MaxJobs=20 / 4 example is the docs'.

## Life of a job
- Submit returns a job ID immediately; submit plugins may rewrite the request; pending reasons recorded (Priority, Resources, Dependency, ...).
- State codes shown: PD, CF, R, CG, CD; other endings F, CA, TO, NF, PR, OOM (squeue man page, .SH JOB STATE CODES).
- Controller picks step resources and signs a credential; srun contacts the first slurmd, which forwards along the tree (job_launch docs). Controller is not in the task-launch path.
- slurmstepd sequence on screen follows the job_launch doc, in the doc's order. Termination: signal, KillWait grace, SIGKILL, epilog, report, accounting record.

## Priority and fair-share
- Multifactor priority is a weighted sum of factors each in [0,1]. All PriorityWeight* default to 0.
- Documented comparison order: preemption, advanced reservation, partition PriorityTier, priority number, submit time, job ID.
- Classic fair-share: F = 2^(-U/S). Half-life default 7 days (PriorityDecayHalfLife); optional PriorityUsageResetPeriod.
- Fair Tree default since 19.05. Verified in src/plugins/priority/multifactor/fair_tree.c: siblings sorted by level_fs = S/U (normalized shares over normalized usage), tree walked depth-first; each user's fs_factor = rank / (number of user associations), rank counting down from N. So with 5 users the factors are 1.0, 0.8, 0.6, 0.4, 0.2. (I first drew 1, .75, .5, ... and corrected it after reading the source.)
- On-screen worked example (A: shares 60, usage 70 gives 0.857; B: 40 and 30 gives 1.333) is my illustration of the formula, not a doc example.

## Backfill and preemption
- Defaults from the man page (SchedulerParameters): bf_interval 30 s, bf_window 1 day, bf_resolution 60 s. bf_max_job_test not stated on screen (see man page).
- Nodes held for future reservations show as planned (sinfo).
- Preemption: PreemptType preempt/partition_prio or preempt/qos; PreemptMode cancel, requeue or suspend; GraceTime for checkpointing.

## Placement
- cons_tres is the default SelectType per the slurm.conf man page; the cons_tres.html page conflicts with it, so I followed the man page.
- GRES: name, type, device files, cores; NVIDIA autodetect exists but counts are still configured. task/cgroup confines; proctrack/cgroup tracks processes.
- Topology: describe leaf switches plus one top level; lowest-level switch that fits, best-fit; sbatch --switches=count[@max-wait]. Example "1@60" is illustrative (the doc's unit is minutes).
- power_save: ResumeProgram / SuspendProgram. Docs report validating 500 simple batch jobs per second sustained (vendor claim).

## My own models (not Slurm code; labelled on screen)
- sim_backfill.py: 128 homogeneous nodes, whole-node jobs, single queue, lognormal runtimes (median 1 h, sigma 1.2), offered load 0.85, 3,000 jobs per run (jobs 300 to 2,700 measured), 30 seeds, 95% CIs. Backfill is conservative-style: plan rebuilt each pass, every waiting job reserved in priority order.
- Results (mean wait): FIFO 10.85 h (CI +-2.6); backfill with exact estimates 1.86 h (+-0.46); estimates padded x2 1.44 h; x10 1.33 h. Paired difference vs exact: -0.42 h at x2 (CI +-0.11), -0.53 h at x10 (+-0.20).
- Forecast error (mean |planned - actual start|): 0 at x1 (invariant check: no job starts later than its first plan; passed at 0.00%), 2.9 h at x1.5, 5.1 h at x2, 9.4 h at x3, 16.5 h at x5, 27.4 h at x10.
- Reading: in this toy, padding did not hurt waits (consistent in direction with Mu'alem and Feitelson 2001) but made forecasts unreliable. Not modeled: killing jobs at their limit, partial-node jobs, realistic user rounding, preemption, limits, topology. Do not carry the numbers anywhere.

## Not verified / deliberately hedged
- NQS as ancestor, LSF's first release date, the origin of the Slurm name (Futurama), and whether Quadrics RMS was closed source: not verified; kept off screen.
- "Production March 2003" wording and exact timing of the first deployment: tense not confirmed.
- TOP500 share (old, Wikipedia only). Version-specific defaults may have changed; check your version's man page.
- Config shapes in the Lab / Campus / Cloud scene, all weights, share numbers and QOS values are illustrative, not site data.
- No benchmark comparing Slurm with PBS, LSF or others on the same workload was found; the origin story is qualitative.

## Sources
- SchedMD documentation (slurm.schedmd.com): overview, quickstart_admin, priority_multifactor, fair_tree, resource_limits, qos, accounting, preempt, cons_tres, gres, cgroup.conf, topology, job_launch, configless_slurm, power_save; man pages slurm.conf(5), sinfo(1), squeue(1), sbatch(1), sacctmgr(1).
- Slurm source tree (src/plugins/priority/multifactor/fair_tree.c).
- Yoo, Jette, Grondona, JSSPP 2003; Jette and Grondona, ClusterWorld 2003.
- Mu'alem and Feitelson, IEEE TPDS 12(6), 2001.
- Wikipedia (HTCondor, PBS, Platform LSF, Slurm); SchedMD FAQ; NVIDIA blog, 15 Dec 2025.
