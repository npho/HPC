# HPC interconnect topologies

Narrated explainer video: 3840x2160, 30 fps, ~25 min, 15 scenes. Fat trees / Clos, tori, hypercubes, HyperX, dragonfly, collectives and job placement, and a tour of proprietary interconnects. The video file is not stored here; this folder rebuilds it.

## Build
Run from this folder, after the one-time setup in the [root README](../README.md).
```
make tts      # narration -> build/audio/, data/timing.json
make render   # 4K scenes -> build/video_4k/ (CPU only, slow; WORKERS=2, RES=1080 for a proxy)
make video    # -> out/hpc_topologies_4k.mp4 + narration.srt
```
Quick checks: `make smoke`, `make stills SCENE=clos T="10 30"`, `make sim`, `make check`. `make help` lists all targets.

## Layout
- `src/script.py` narration (15 scenes); `{Display|spoken}` separates on-screen text from what TTS says.
- `src/engine.py`, `common.py` skia drawing engine; `src/scenes_{a,b,c}.py` the scenes (pure functions `draw(c, t, ctx)`).
- `src/tts.py`, `render.py` (`still | scene | all | mux | dry`) pipeline; `stills_all.py`, `stills_beats.py` contact sheets.
- `src/topo_graphs.py`, `topo_flows.py`, `models.py`, `selftest.py` topology builders, flow models, self-tests -> `data/results.json`.
- `src/verify_narration_numbers.py` checks every spoken number against `data/results.json` (59 checks).
- `data/` model results and `timing.json` (beat and sentence times that drive the animation).
- `notes/` verification ledger: sources, corrections, modeled vs. checked vs. unverified.

## Caveats
- Voice: Kokoro `af_heart`, speed 1.0. The original timing was not archived; `timing.json` was re-synthesized when this folder was restructured.
- Throughput figures are models, not hardware measurements; see the notes.
