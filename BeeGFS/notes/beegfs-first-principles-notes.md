# BeeGFS first-principles notes (companion to the explainer video)

Facts below were checked against the sources fetched during the build. Anything I derived or modeled is flagged. Where sources disagreed or said nothing, I say so.

## History (Wikipedia "BeeGFS", secondary; plus vendor/trade press)
- 2005: in-house project at Fraunhofer ITWM (Kaiserslautern), originally named FhGFS.
- First beta shown at ISC07 / SC07; first stable release about a year later.
- 2014: spin-off company ThinkParQ; file system renamed BeeGFS. About 100 supported customers in 2014 (secondary).
- 2018: CSIRO 2 PB all-NVMe deal (vendor/trade-press quote, not verified).
- Latest version: docs show 8.4; Wikipedia says 8.3 (March 2026). Treat the version as moving.
- Licensing: client GPLv2; server proprietary; Community edition free; Enterprise needs a support subscription.
- Foundational paper: I found none. The video says so rather than inventing one.

## Architecture (doc.beegfs.io architecture, system requirements)
- Services: management (registry + watchdog; very small), metadata, storage, client (patchless kernel module). Optional: monitoring, older admon.
- Servers are user-space daemons on top of local file systems: ext4 for metadata, XFS for storage, typically. Targets typically RAID6 (8+2 or 10+2) or ZFS RAIDz2.
- Client talks to metadata servers for namespace and layout, then does data I/O directly with storage servers.

## Striping
- Pattern RAID0 or mirrored, set per directory: `beegfs entry set --num-targets --chunk-size`. Applies to new files only.
- Chunk size default: the client tuning page says 512 KiB; the striping page example shows 4 targets x 1M. Sources disagree, so the video does not state a default.
- Chunk files are created on write, not preallocated. Targets are chosen randomly by default; capacity pools (Normal / Low / Emergency) steer choice. Threshold values were not given.

## Metadata
- Distributed per directory: a directory is assigned to a metadata server at creation (random). All entries of one directory live on one server. My inference (flagged on screen): one hot directory means one hot metadata server.
- Stored as extended attributes on a zero-byte file. ext4 with `-I 512`, or `-I 1024` if striping over more than 4 targets or using ACLs.
- Sizing guidance: 0.3 to 0.5% of capacity; 500 GB of metadata is about 150M files.
- Cost: a directory costs 2 directories + 2 metadata files; a file costs 1 metadata file.

## Consistency and caching
- I found no locking or consistency semantics in the docs; the vendor says "POSIX compatibility". The video says this is not verified and advises testing your own workload.
- Metadata cache defaults to milliseconds. Knobs named: `tuneFileCacheType`, `sysSyncOnClose`, `tuneRemoteFSync`.
- BeeGFS 8.4 has experimental remote invalidation (InvalWatch): off by default, 50M inodes, about 6 GiB, with trade-offs listed in the docs.

## Network
- ibverbs RDMA: InfiniBand, RoCE, Omni-Path. TCP otherwise; management over TCP. Client multi-rail since 7.3.0 via `connRDMAInterfacesFile`. `beegfs health net` shows TCP fallback.
- Peer formulas (docs): metadata = clients + 2x(meta-1) + storage; storage = clients + meta; client = meta + storage.
- Defaults: `connRDMABufNum` 70, `connRDMABufSize` 8192. Memory per connection = size x num x 2 (about 560 KiB total).
- MY example (not from the docs): 1,000 clients, 4 metadata, 20 storage servers gives 1,026 peers per metadata server, 1,004 per storage server, about 1.18 GB of RDMA buffer memory per metadata server at one connection per pair.

## Mirroring and editions
- Buddy groups (primary + secondary), per directory for storage; equal-size targets on different servers or failure domains; mirrored files take 2x space. Metadata mirroring is also available.
- Resync is automatic or manual. Failover propagation takes about 30 s ("should stay under a minute"); writes during the window may be lost and reads may be stale.
- Mirroring is not a backup (docs say so).
- beegfs.io edition table (vendor): Enterprise-only: high availability, mirroring, quota enforcement, storage pools with auto-tiering, remote storage targets (RST), copy, watch, index, rebalancing. Community capped at 1,000 TB HDD + 200 TB SSD. BeeOND limited to 5 contributing nodes in both editions.

## BeeOND
- `beeond start -n nodefile -d /data/beeond -c /mnt/beeond`; Slurm and Torque prologue/epilogue integration documented; `beegfs copy` for stage in/out.
- ABCI: 1 PB NVMe burst buffer at 1 TB/s (ThinkParQ claim via The Next Platform, 2018). Vendor claim, not verified.

## BeeGFS 8 (release notes 8.0.0)
- Management service rewritten in Rust with an SQL database; gRPC and TLS; SHA256 connection authentication.
- Go-based `beegfs` CLI replaces `beegfs-ctl`; `beegfs-helperd` removed.
- Remote Storage Targets for S3-compatible storage (Enterprise).
- Not compatible with older versions: plan the upgrade.

## My own models (not from sources; labelled on screen)
- sim_stripe.py: 100 targets, 3,000 files with lognormal sizes, each file's stripes on distinct random targets, 300 trials. Fullest target / mean: 3.80 (1 stripe), 2.48 (2), 1.91 (4), 1.56 (8), 1.34 (16). The BeeGFS scene uses the 4-stripe value (1.91x) because the docs example uses 4 targets. It shows the shape of the problem, not observed BeeGFS behaviour: capacity pools steer allocation in real systems.

## Not verified / deliberately hedged
- No founding paper; no locking/consistency description; chunk-size default conflict; capacity-pool thresholds; Wikipedia version/date vs docs.
- CSIRO and ABCI figures are vendor claims.
- No fair same-hardware benchmark of GPFS vs Lustre vs BeeGFS was found, so the comparison is architectural only. Weka, DAOS, CephFS and PanFS are not covered.

## Sources
- BeeGFS documentation (doc.beegfs.io): architecture, striping, mirroring, system requirements, metadata tuning, client tuning, RDMA support, client metadata caching, BeeOND, release notes 8.0.
- beegfs.io: Community vs Enterprise features; HPC solution brief (vendor).
- Wikipedia, "BeeGFS".
- HPCwire (2018) and The Next Platform (Jan 2018).
- NetApp blog, "BeeGFS for Beginners" (2019).
