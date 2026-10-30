# BeeGFS: first principles

Narrated explainer video: 3840x2160, 30 fps, ~20 min, 11 scenes (`s0`–`s10`). The video file is not stored here; this folder rebuilds it.

## Build
Run from this folder, after the one-time setup in the [root README](../README.md).
```
make tts      # narration -> build/audio/, data/timing.json
make render   # 4K scenes -> build/video/ (CPU only, slow)
make video    # -> out/BeeGFS_first_principles_4K.mp4
```
Quick checks: `make smoke`, `make stills SCENE=s4 T="10 50"`, `make sim`, `make asr`. `make help` lists all targets.

## Layout
- `src/script.py` narration, one line per visual beat.
- `src/fx.py` style and drawing helpers; `src/lx.py` file-system topology helpers; `src/scenes_{a,b,c}.py` the scenes (s0–s3, s4–s7, s8–s10).
- `src/tts.py`, `render.py`, `mux.py` pipeline; `preview.py`, `contact.py` QA stills; `asr.py` pronunciation check.
- `src/sim_stripe.py` toy model of how evenly random placement fills storage targets per stripe count (writes `data/sim_stripe.json`, read by `scenes_b.py`).
- `data/` `timing.json` (cue times that drive the animation), simulation results, ASR transcript, original build versions and model checksums.
- `notes/` verified facts with sources, and build notes. `qa/` final contact sheet.

## Caveats
- Voice: Kokoro `am_michael`, speed 1.04. Re-synthesized audio may differ slightly; use the `timing.json` that `make tts` writes.
- Bit-identical frames across machines are unverified.
