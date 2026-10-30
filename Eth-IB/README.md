# InfiniBand vs Ethernet: first principles

Narrated explainer video: 3840x2160, 30 fps, ~16 min, 15 scenes (`open` … `refs`), with SRT subtitles and a 1080p proxy. The video file is not stored here; this folder rebuilds it.

## Build
Run from this folder, after the one-time setup in the [root README](../README.md).
```
make tts      # narration -> build/audio/, data/timing.json
make render   # 4K scenes -> build/video/ (CPU only, slow; WORKERS=2)
make video    # -> out/InfiniBand_vs_Ethernet_{4K,1080p}.mp4 + .srt
```
Quick checks: `make smoke`, `make stills SCENE=routing T=4,30`, `make sim`. `make help` lists all targets. Stills render before `make tts` using word-count timing estimates. `DEBUG_GLYPHS=1` reports characters missing from a font.

## Layout
- `src/script.py` narration, a list of beats per scene; `src/scenes.py` fixes scene order.
- `src/engine.py` drawing primitives, easing, palette; `src/scenes_{a..e}.py` the scenes (stateless functions of time).
- `src/tts.py`, `render.py`, `mux.py` pipeline; `sheet.py` contact sheets of stills.
- `src/model_numbers.py` every derived number (arithmetic, topology sizing, ECMP toy model) -> `data/model_numbers.json`.
- `data/` `timing.json` (beat times that drive the animation) and model results.
- `notes/` verified facts with sources, corrections and caveats.

## Caveats
- Voice: Kokoro `af_heart`, speed 1.0. Narration and timing were re-synthesized when this folder was restructured; the original timing was not archived.
- Throughput figures are toy models, not measurements; see the notes.
