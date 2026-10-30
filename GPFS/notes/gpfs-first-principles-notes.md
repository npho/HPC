# GPFS / IBM Storage Scale: first-principles notes (companion to the explainer video)

Facts below were checked against the sources listed; anything I modeled myself is flagged.

## History
- Vesta (IBM Watson, 1992–95; commercialized as PIOFS ~1994) and Tiger Shark (IBM Almaden, "as early as 1993", multimedia streaming) are the lineages. GPFS first shipped ~1998 on AIX. Source: Wikipedia "GPFS" (secondary; dates are approximate).
- Foundational paper: F. Schmuck & R. Haskin, "GPFS: A Shared-Disk File System for Large Computing Clusters," USENIX FAST '02, pp. 231–244.
- Names: "Spectrum" prefix introduced 2015; dropped Feb 2023 → IBM Storage Scale (Blocks & Files, 24 Feb 2023).

## Core design (from the 2002 paper)
- Shared-disk; files striped across all disks in the file system itself (no separate LVM). Block "typically 256k, configurable 16k–1M"; subblocks as small as 1/32 of a block. Up to 4,096 disks of ≤1 TB (~4 PB) per file system in that design.
- Distributed locking: token manager + per-node local lock managers; first writer gets a byte-range token for the whole file, ranges split on contention and are rounded to block boundaries; elected metanode is the only node that reads/writes a file's inode on disk; "data shipping" mode for fine-grained sharing (MPI-IO).
- Extensible-hashing directories (one directory block access per lookup); allocation map split into separately lockable regions handed out by an allocation manager; per-node write-ahead logs stored on the shared disks, replayable by any node; user data is not logged; only a majority group may access the file system (minority fenced).
- ASCI White (paper): 512 nodes, 140 TB in two file systems; "Sixteen nodes drive the entire 12 GB/s I/O bandwidth."

## Cluster roles (IBM SC19 "Concepts and features" slides)
- Quorum nodes; cluster manager = one of the quorum nodes (leases, failures, recovery); one file system manager per file system (space, quotas, disk config); several token managers, each owning a slice of tokens by inode number. Apart from quorum, all nodes identical.
- NSD = Network Shared Disk; data may flow over a direct path or via NSD servers. Failure groups keep replicas apart. Filesets (independent filesets have their own inode space). AFM = asynchronous caching (DR). Remote cluster mounts are documented by IBM. ECE = software edition of the declustered RAID; FPO (shared-nothing) shipped with GPFS 3.5, Dec 2012.

## Declustered RAID (IBM Spectrum Scale RAID docs)
- Codes: 8+2p and 8+3p Reed-Solomon (80% / 73% efficiency), 3-way and 4-way replication (33% / 25%), before spare space.
- Each recovery group is physically connected to two servers; one active at a time. End-to-end 8-byte checksum from the NSD client; pdisk I/O times out after ~10 s and the pdisk enters the "disk hospital".
- IBM says declustering can make rebuild impact "a factor of three to four times less than a conventional RAID."
- MY toy model (not IBM's): 8+2p, 6,000 strips/disk, random placement, one failed disk, load = strips read + written on the busiest surviving disk. Ratio vs a 10-disk group with a dedicated spare: 3.1× (30 disks), 6.0× (60), 11.9× (120). Idealized; ignores network, CPU, foreground I/O. Script: src/sim_decluster.py.

## Alpine (Oak Ridge, Summit): OLCF "Spectrum Scale on Summit" workshop slides (Dec 2018) and OLCF Summit page
- 250 PB; 154 NSD servers; EDR InfiniBand (100 Gb/s); 16 MB block size; each storage server is also a metadata server.
- Peak ≈ 2.5 TB/s sequential, ≈ 2.2 TB/s random; up to 2.6 M accesses/s for 32 KB files.
- IO500, 504 nodes × 2 processes (GB/s): ior-easy write 2158, ior-hard write 0.57 (≈3,786× lower); ior-easy read 1788, ior-hard read 27.4 (≈65× lower). ior-hard = 47,008-byte interleaved writes to one shared file (G. Klockwood's IO500 notes). The slides do not explain the gap; token traffic and partial-block read-modify-write are hypotheses, not findings.
- NAS BTIO with ROMIO hint tuning: 1,532 MB/s → as high as 35,509 MB/s (≈23×).
- Derived (mine, rough): ASCI White vs Alpine capacity ×1,786, bandwidth ×208; time to read everything once ≈ 3.2 h vs ≈ 27.8 h. Different machines/years/measurements, so direction only.

## Not verified / deliberately hedged
- Exact ESS enclosure counts per building block (video shows a generic example layout).
- Summit/Alpine year placement; the video avoids claiming a specific year.
- Block-size efficiency curves in the video are an illustrative model (assumed 10 ms/40 MB/s for a c. 2002 disk, 8 ms/200 MB/s for a modern HDD), not measurements.

## Source links (homepages in some cases; verify exact pages)
- USENIX FAST '02 paper: https://www.usenix.org/legacy/publications/library/proceedings/fast02/full_papers/schmuck/schmuck.pdf
- Wikipedia GPFS: https://en.wikipedia.org/wiki/GPFS
- OLCF Summit: https://www.olcf.ornl.gov/summit/
- IBM Spectrum Scale RAID / ECE docs: https://www.ibm.com/docs/en/spectrum-scale-ece
- Blocks & Files (rename article, 24 Feb 2023), IBM SC19 slides, OLCF Alpine workshop slides, IBM ESS fault-tolerance blog, Klockwood IO500 notes: exact URLs were not preserved in this archive.
