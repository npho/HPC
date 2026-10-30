# GPFS / IBM Storage Scale: first principles

Narrated explainer video: 3840x2160, 30 fps, ~16 min, 10 scenes (`s0`–`s9`). The video file is not stored here; this folder rebuilds it.

## Build
Run from this folder, after the one-time setup in the [root README](../README.md).
```
make tts      # narration -> build/audio/, data/timing.json
make render   # 4K scenes -> build/video/ (CPU only, slow)
make video    # -> out/GPFS_first_principles_4K.mp4
```
Quick checks: `make smoke`, `make stills SCENE=s4 T="10 50"`, `make sim`, `make asr`. `make help` lists all targets.

## Layout
- `src/script.py` narration, one line per visual beat.
- `src/fx.py` style and drawing helpers; `src/scenes_{a,b,c}.py` the scenes.
- `src/tts.py`, `render.py`, `mux.py` pipeline; `preview.py`, `contact.py` QA stills; `asr.py` pronunciation check.
- `src/sim_decluster.py` toy declustered-RAID rebuild model (writes `data/sim_*.json`, read by scene `s6`).
- `data/` `timing.json` (cue times that drive the animation), simulation results, ASR transcript, original build versions and model checksums.
- `notes/` verified facts with sources, and build notes.

## Caveats
- Voice: Kokoro `am_michael`, speed 1.04. Re-synthesis on macOS reproduced the archived scene durations; bit-identical frames are unverified.
- Pronunciation respellings in `script.py` (e.g. "eye-node", spaced letters) were tuned for this voice and speed.
