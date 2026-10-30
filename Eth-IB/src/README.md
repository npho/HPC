# Source for "InfiniBand vs Ethernet: first principles"

Pipeline: script.py (narration) -> tts.py (Kokoro-82M, per-beat WAVs + timings.json) -> render.py (skia, 4K30, per scene, stateless time-functions) -> assemble.py (concat, narration track at beat offsets, loudnorm, SRT, 1080p proxy).

- model_numbers.py : every number I derived myself (arithmetic, topology sizing, ECMP toy model). Writes build/model_numbers.json.
- engine.py        : drawing primitives, easing, palette, Tufte furniture.
- scenes_a..e.py   : the 15 scenes; scenes.py fixes their order.
- sheet.py         : contact sheets of stills for QA.

Setup: pip install skia-python kokoro-onnx soundfile numpy pillow; ffmpeg; ET Book fonts (MIT, github.com/edwardtufte/et-book) into assets/fonts/;
Kokoro model files (kokoro-v1.0.onnx, voices-v1.0.bin) in $KOKORO_DIR.
Run: python3 model_numbers.py; python3 tts.py; python3 render.py all --workers 2; python3 assemble.py
Stills: python3 render.py <scene> --still 10,20   (DEBUG_GLYPHS=1 reports characters missing from a font)
Font paths for Inter / DejaVu / Latin Modern are hard-coded in engine.py; adjust for your system.
