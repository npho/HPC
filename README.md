# HPC

Narrated, first-principles explainer videos on HPC systems. Each folder holds everything needed to rebuild one video: narration script, animation code, toy models, and research notes with sources.

| Folder | Topic | Length |
|---|---|---|
| [BeeGFS](BeeGFS/) | BeeGFS parallel file system | ~20 min |
| [Eth-IB](Eth-IB/) | InfiniBand vs Ethernet | ~16 min |
| [GPFS](GPFS/) | GPFS / IBM Storage Scale | ~16 min |
| [Lustre](Lustre/) | Lustre parallel file system | ~18 min |
| [Slurm](Slurm/) | Slurm workload manager | ~16 min |
| [Topologies](Topologies/) | Interconnect topologies | ~25 min |

## Setup
Requires [uv](https://docs.astral.sh/uv/) and ffmpeg with libx264 (macOS: `brew install uv ffmpeg`).
```
uv sync --all-packages      # one shared .venv for all projects
scripts/fetch_assets.sh     # fonts + Kokoro TTS models -> assets/ (~370 MB)
```

## Build a video
```
cd GPFS
make tts render video       # -> out/*.mp4
```
Every project has the same targets: `tts`, `render`, `video`, `all`, `smoke`, `stills`, `sim`, `clean`. Run `make help` in a folder for details. Rendering is CPU-only and takes hours at 4K; use `make stills` or `make smoke` for quick checks.

## Contributing
Conventions for layout, paths, environment, verification and commits are in [AGENTS.md](AGENTS.md).
