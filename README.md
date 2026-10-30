# HPC

Narrated, first-principles explainer videos on HPC systems. Each folder holds everything needed to rebuild one video: narration script, animation code, toy models, and research notes with sources.

| Folder | Topic |
|---|---|
| [BeeGFS](BeeGFS/) | BeeGFS parallel file system |
| [Eth-IB](Eth-IB/) | InfiniBand vs Ethernet |
| [GPFS](GPFS/) | GPFS / IBM Storage Scale |
| [Lustre](Lustre/) | Lustre parallel file system |
| [Slurm](Slurm/) | Slurm workload manager |
| [Topologies](Topologies/) | Interconnect topologies |

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
Every project has the same targets: `tts`, `render`, `video`, `all`, `smoke`, `stills`, `sim`, `clean`. Run `make help` in a folder for details.
