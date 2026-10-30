# HPC interconnect topologies: video source

Generates a ~24.7 minute explainer (3840x2160, 30 fps) on interconnect topologies: fat trees / Clos, tori, hypercubes, HyperX, dragonfly, collectives and job placement, plus a brief tour of proprietary interconnects.

## Layout
- `src/script.py` narration (15 scenes). `{Display|spoken}` gives on-screen text vs. the pronunciation fed to TTS.
- `src/tts.py` Kokoro-82M narration -> `build/audio/*.wav`, `build/timeline.json`.
- `src/topo_graphs.py`, `topo_flows.py`, `models.py`, `selftest.py` topology builders, flow/throughput models, self-tests; `models.py` writes `build/results.json` (included).
- `src/engine.py`, `common.py`, `scenes_a/b/c.py` skia drawing engine and scenes (pure functions `draw(c, t, ctx)`).
- `src/render.py` `still | scene | all | mux | dry` commands.
- `src/verify_narration_numbers.py` checks every number spoken in the narration against `results.json` (59 checks).
- `notes.md` verification ledger: sources, corrections, what is modeled vs. checked vs. unverified.

## Reproduce
```
pip install --break-system-packages skia-python==144.1 kokoro-onnx==0.6.1 onnxruntime==1.29.0 phonemizer==3.4.0 numpy==2.5.3 pillow==12.3.0 soundfile==0.14.0
# system: ffmpeg 6.1.1 (libx264), espeak-ng
mkdir -p assets/fonts assets/tts
# Kokoro model + voices
curl -L -o assets/tts/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o assets/tts/voices-v1.0.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
# ET Book fonts (Edward Tufte, MIT): fetch the three TTFs used in src/engine.py from
# https://github.com/edwardtufte/et-book (et-book/ directory) into assets/fonts
cd src
python3 models.py && python3 selftest.py     # model results
python3 tts.py                               # narration + timeline
python3 verify_narration_numbers.py
python3 render.py all --res 4k --workers 2   # ~45 min on CPU
python3 render.py mux --res 4k               # -> out/hpc_topologies_4k.mp4, narration.srt
```
Paths assume the project root is the parent of `src/`. Fonts missing a glyph fall back to DejaVu.

## Caveats
Narration is synthetic speech (Kokoro). All throughput figures are my models, not hardware measurements; see `notes.md`.
