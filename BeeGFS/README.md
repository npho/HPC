# BeeGFS explainer video: reproducible build archive

Output: 3840x2160, 30 fps, 1199.5 s (~20 min), narrated, 11 scenes (s0..s10). The video file is delivered separately; this archive rebuilds it.

## Layout
- src/    code. script.py = narration (one line = one visual beat). fx.py = style/drawing helpers. lx.py = file-system topology helpers (shared with the Lustre video; the "targets" label fix is included). scenes_a.py (s0-s3), scenes_b.py (s4-s7), scenes_c.py (s8-s10) = animations. tts.py, render.py, mux.py = pipeline. sim_stripe.py = toy placement-balance simulation (numpy). asr.py = whisper pronunciation check. preview.py / contact.py = still / contact-sheet QA.
- data/   timing.json (per-scene durations and cue times that drive sync; ground truth for the delivered video), sim_stripe.json, asr_out.json, model_sha256.txt, versions.txt, fonts_used.txt
- audio/  the 11 narration WAVs (24 kHz).
- notes/  beegfs-first-principles-notes.md (verified facts, sources, conflicts, caveats), build-notes.md
- logs/, qa/  render/TTS logs, final contact sheet

## Environment
Python 3.13, ffmpeg (libx264), requirements.txt (skia-python, kokoro-onnx, onnxruntime, numpy, soundfile, scipy; faster-whisper + av for asr.py). Fonts: Lora, Inter, DejaVu Sans Mono at the paths in fx.py (`_FD`); edit if yours differ. Kokoro model files kokoro-v1.0.onnx + voices-v1.0.bin are not included (checksums in data/model_sha256.txt).

## Rebuild
```
mkdir work && cd work
cp ../src/*.py . ; cp ../data/timing.json ../data/sim_stripe.json . ; mkdir audio out frames ; cp ../audio/*.wav audio/
# reuse the exact audio, or re-synthesize (rewrites audio/*.wav + timing.json):
#   (put kokoro-v1.0.onnx and voices-v1.0.bin in ../models/ relative to the work dir; the path is hardcoded as M='../models/' at the top of tts.py)
#   python3 tts.py am_michael 1.04
python3 render.py s0,s1,s2,s3,s4,s5 30 2 veryfast 18      # CPU only, ~8 frames/s per process; run two processes
python3 render.py s6,s7,s8,s9,s10 30 2 veryfast 18
python3 mux.py out/BeeGFS_first_principles_4K.mp4
python3 sim_stripe.py                                      # regenerates sim_stripe.json (scenes_b.py reads it at import)
```
Quick check: `python3 render.py s4 30 0.5 veryfast 28 60`; `python3 preview.py s4 10 50 100`.

## Caveats
- tts.py's model path is hardcoded to `../models/`; edit `M` at the top of tts.py to change it.
- If you re-run TTS, use the timing.json it writes.
- Animations are deterministic given timing.json; I did not verify bit-identical frames across machines.
- Smoke test (half-res 60-frame render of s4 and a sim_stripe.py rerun) was run on this layout; I did not re-run the full 4K render from the archive.
