# Slurm: first principles

Narrated explainer video: 3840x2160, 30 fps, ~16 min, 14 scenes (`s00_title` … `s13_universe`). The video file is not stored here; this folder rebuilds it.

## Build
Run from this folder, after the one-time setup in the [root README](../README.md).
```
make tts      # narration -> build/audio/, data/timing.json
make render   # 4K scenes -> build/video/ (CPU only, slow; SCALE=1 for 1080p)
make video    # -> out/slurm_first_principles_4k.mp4
```
Quick checks: `make smoke`, `make stills SCENE=s08_backfill T="10 30"`, `make sim`. `make help` lists all targets.

## Layout
- `src/script.py` narration, a list of beats per scene; `src/tts.py` respells technical tokens for the speech engine.
- `src/engine.py` drawing canvas, palette, easing; `src/scenes/` the scenes (`common.py` shared furniture, `a.py`–`d.py`).
- `src/tts.py`, `render.py` (`scene | all | smoke | final`) pipeline; `preview.py`, `sheet.py` QA stills.
- `src/sim_backfill.py` toy FIFO vs backfill scheduler (numba) -> `data/backfill_sweep.json`, read by scene `s08`.
- `data/` simulation results and log, and `timing.json` (beat times that drive the animation).
- `notes/` verified facts with sources and caveats.

## Caveats
- Voice: Kokoro `af_heart`, speed 0.97. The original timing was not archived; `timing.json` was re-synthesized when this folder was restructured.
- The scheduler model is a toy, not Slurm code; see the notes.
