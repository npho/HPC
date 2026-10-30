# Lustre first-principles notes (companion to the explainer video)

Facts below were checked against the sources fetched during the build. Anything I derived or modeled is flagged. Where sources disagreed I say so.

## History (Wikipedia "Lustre (file system)" unless noted; secondary source, dates approximate)
- Name: portmanteau of "Linux" and "cluster".
- 1999: Peter J. Braam (Carnegie Mellon) starts the research; builds on Coda / InterMezzo. 2001: Cluster File Systems, Inc. founded. Funded under the US DOE's ASCI Path Forward (with HP and Intel involved).
- Mar 2003: first production use (MCR Linux cluster, LLNL). Dec 2003: Lustre 1.0.0.
- Sep 2007: Sun acquires CFS assets. 2010: Oracle manages it; Dec 2010 Oracle announces end of 2.x development. 2010-11 Whamcloud formed (Barton, Dilger and others); Jul 2012 Intel acquires Whamcloud. Feb 2013 Xyratex acquires the trademark from Oracle. Jun 2018 DDN acquires the Intel Lustre team. Nov 2019 OpenSFS and EOFS jointly receive the trademark.
- Wikipedia also says Lustre was used by "more than 60 of the top 100" since June 2005, but the page is inconsistent about this ("six of the top 10" in another section). The video calls it approximate.
- Release highlights (Wikipedia): 1.0.0 Dec 2003; 1.8.0 May 2009 (OST pools); 2.0 Aug 2010; 2.2 Mar 2012 (stripe counts up to 2000); 2.4 May 2013 (DNE, ZFS backend); 2.5 Oct 2013 (HSM); 2.10 Jul 2017 (PFL, LNet Multi-Rail); 2.11 Apr 2018 (FLR, DoM); 2.13 Dec 2019 (up to 64 MB RPCs); 2.15 Jun 2022.

## Foundational documents
- Cluster File Systems, Inc., "Lustre: A Scalable, High-Performance File System," white paper v1.0, 11 Nov 2002 (copy hosted at cse.buffalo.edu/faculty/tkosar/cse710/papers/lustre-whitepaper.pdf). Clients ask the MDS for namespace operations, do file I/O directly with OSTs; files can be striped across OSTs "in a RAID pattern"; object-based; "strong file and metadata locking"; locks distributed across OSTs; intent-based locking; recovery goals (no single point of failure for an MDS or OST). Scale labels: "up to 10,000's" of clients (figure), "100's of OSTs, routers and clients". No bandwidth numbers.
- P. Schwan, "Lustre: Building a File System for 1,000-node Clusters," Proceedings of the Linux Symposium, Ottawa, July 2003 (kernel.org/doc/ols/2003/ols2003-pages-380-386.pdf). Key points used: block-level inode/allocation locking limits shared-block designs to "a dozen or two" nodes; LDLM "just over 4,000 lines"; locks managed by a single node and do not migrate; policy function can grant a larger lock than requested (sole user gets whole-file lock); intent locks; high-contention directories (/tmp) get no lock, low-contention would get a write-back lock but the client write-back cache was "planned"; Portals-based networking with a NAL per interconnect; >300 MB/s between two nodes over Elan, PCI-bound; parallel I/O to one file scaled to >1,100 nodes ("the limit of available hardware"); Lustre on 3 of the 8 largest clusters on the June 2003 TOP500; goal "tens of thousands of clients and petabytes."
- Caveat: the "dozen or two nodes" limit is the Lustre authors' argument about shared-block file systems in 2003. GPFS, a shared-disk design, scales to thousands of nodes by distributed tokens, so treat it as a design-philosophy claim, not a universal law.

## Architecture (wiki.lustre.org "Lustre Architecture for Admins", Wikipedia)
- MGS/MGT: configuration logs for all file systems; MGT "less than 100 MB even on the largest systems"; usually co-located with the first MDS. MDS/MDT: namespace (names, directories, permissions, timestamps, layouts, xattrs, ACLs); not involved in file I/O; up to 256 MDTs via DNE. OSS/OST: file data as objects; typically 2-8 OSTs per OSS (up to 32); an OST is one block device or ZFS pool/dataset; typical OST 24-48 TB; max 1024 TiB; up to 8150 OSTs. Clients: POSIX mount via kernel module.
- Open: client asks MDS for metadata+layout; reads/writes go directly to OSSs in parallel; MDS not in the data path.
- Striping: stripe_count default 1; -1 = all OSTs; max 2000. The admin wiki gives a default stripe_size of 4 MiB; I recall 1 MiB from the manual but did not verify, so the video does not state a default stripe size. Round-robin example (3 stripes, 1 MB): chunks 1,2,3 to OST0,1,2; chunk 4 back to OST0; each OST holds one object per file.
- Failure behaviour (admin wiki): OSS failure makes its OSTs' files unavailable until an HA partner takes over (if configured); MDS failure stalls new opens/creates/renames while open files continue I/O; MGS failure leaves the running FS up, new mounts/config changes fail; default eviction timeout 100 s, locks revoked, dirty cache discarded.
- Limits (admin wiki): 2+ EiB FS size; 256 MDTs; 8150 OSTs; 131,072 clients (30,000+ tested in production); max file 31.25 PiB (ldiskfs) / 8 EiB (ZFS); 2000 stripes.
- LNet (Wikipedia, admin wiki): originally Sandia Portals; LNDs for TCP, InfiniBand, Omni-Path, RoCE, iWARP, proprietary; NID = address@network_type; TCP port 988; ksocklnd and ko2iblnd; Multi-Rail in 2.10; RPC sizes 4 MB (2.4), 16 MiB (2.9), 64 MB (2.13). My interpretation (flagged on screen): larger requests amortize fixed per-request cost.
- DNE (2.4: subtrees on separate MDTs; 2.7+: striped directories; 2.15: round-robin/space-balanced default directory layouts). PFL 2.10, FLR 2.11, DoM 2.11. ldiskfs = enhanced ext4; ZFS backend since 2.4.

## Orion (Frontier, ORNL)
- OLCF Orion page: Lustre + ZFS, HPE ClusterStor, ~500 server nodes, 50 cabinets, ~700 PB total. Performance tier: 5,400 NVMe, 11.5 PB, 10 TB/s. Capacity tier: 679 PB on hard disk. Metadata: 480 NVMe, 10 PB. insideHPC adds 47,700 HDDs.
- Conflict: OLCF page says capacity tier 5.5 TB/s read, 4.6 TB/s write; insideHPC says reads 4.6 and writes 5.5. The video says "about five" and says the sources disagree.
- LUG 2023 "Orion" slides (opensfs.org/wp-content/uploads/LUG23_Orion_v3.pdf): MGS 2; MDS 40; OSS 450; LNet routers 169; ZFS 2.1.7; dRAID within an enclosure (NVMe: draid2:9d:12c:1s; HDD: draid2:11d:53c:2s); Lustre 2.15 with vendor patches; pools "performance" and "capacity"; default PFL: 0-256K DoM; 256K-8M 1 stripe on performance pool; 8M-128G 1 stripe on capacity; 128G-EOF 8 stripes on capacity; 1M stripe size; Self-Extending Layouts. Raw sizes there (9.7 / 11.4 / 667.6 PB) differ slightly from the OLCF page figures.
- Not found: OST/MDT counts, client count.

## My own models (not from sources; labelled on screen)
- Bandwidth vs stripe count: min(stripes x 2 GB/s, 25 GB/s). Pure illustration of shape.
- sim_stripe.py: 100 OSTs, 3,000 files with lognormal sizes (sigma 1.5), each file's stripes on distinct uniformly random OSTs, size split evenly, 300 trials. Fullest OST / mean: 3.80 (1 stripe), 2.48 (2), 1.91 (4), 1.56 (8), 1.34 (16). Result is dominated by the heavy-tailed sizes; real MDS allocators steer toward emptier OSTs, so this shows the problem, not observed behaviour. The bar picture on screen is a single "typical" trial chosen to be close to the mean.
- Orion vs the 2002 GPFS machine (ASCI White, 140 TB, 12 GB/s): capacity 679 PB / 140 TB ≈ 4,850x; flash-tier bandwidth 10 TB/s / 12 GB/s ≈ 830x. Different machines and decades: direction only.

## Not verified / deliberately hedged
- No fair same-hardware GPFS vs Lustre benchmark was found; the comparison in the video is architectural.
- Why Lustre locks "call back" a holder on conflict: the mechanism is standard DLM behaviour; the fetched sources mention lock-cancellation callbacks only briefly.
- Intent-lock and write-back-lock descriptions are from the 2003 paper and may not match current implementations.
- The callout that "a file under 8 MB never touches a hard disk" follows from the default PFL above; individual users or projects can have different layouts.
- Wikipedia's Top500 usage claim is internally inconsistent (see above).
