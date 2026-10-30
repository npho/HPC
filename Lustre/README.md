# Lustre explainer video: reproducible build archive

Output: 3840x2160, 30 fps, 1098.5 s (~18.3 min), narrated, 10 scenes (s0..s9). The video file is delivered separately; this archive rebuilds it.

## Layout
- src/    code. script.py = narration (one line = one visual beat). fx.py = style/drawing helpers (same as GPFS video, plus an alpha fix). lx.py = Lustre-specific helpers (topology, packets). scenes_a.py (s0-s3), scenes_b.py (s4-s6), scenes_c.py (s7-s9) = animations. tts.py, render.py, mux.py = pipeline. sim_stripe.py = toy placement-balance simulation (needs numpy). asr.py = whisper pronunciation check. preview.py / contact.py = still / contact-sheet QA.
- data/   timing.json (per-scene durations and cue times that drive sync; ground truth for the delivered video), sim_stripe.json (simulation output), asr_out.json, model_sha256.txt, versions.txt, fonts_used.txt
- audio/  the 10 narration WAVs used (24 kHz).
- notes/  lustre-first-principles-notes.md (verified facts, sources, conflicts, caveats), build-notes.md
- logs/, qa/  render/TTS logs, final contact sheet

## Environment
Python 3.13, ffmpeg 6.1.1 (libx264), requirements.txt (skia-python 144.1, kokoro-onnx 0.6.1, onnxruntime, numpy, soundfile, scipy; faster-whisper + av for asr.py). Fonts: Lora variable, Inter (Regular/Medium/SemiBold), DejaVu Sans Mono at the paths in fx.py (`_FD`); edit if yours differ. Kokoro model files kokoro-v1.0.onnx + voices-v1.0.bin (not included; checksums in data/model_sha256.txt; I believe they come from the kokoro-onnx GitHub releases, unverified).

## Rebuild
```
mkdir work && cd work
cp ../src/*.py . ; cp ../data/timing.json ../data/sim_stripe.json . ; mkdir audio out frames ; cp ../audio/*.wav audio/
# reuse the exact audio (skip TTS), or re-synthesize:
#   KOKORO_MODELS=/path/to/models/ python3 tts.py am_michael 1.04      # rewrites audio/*.wav + timing.json
python3 render.py s0,s1,s2,s3,s4,s5,s6,s7,s8,s9 30 2 veryfast 18       # CPU only; I measured ~8 frames/s per process, ~33k frames: run two processes on different scenes
python3 mux.py out/Lustre_first_principles_4K.mp4
python3 sim_stripe.py                                                    # regenerates sim_stripe.json (scenes_b.py reads it at import)
```
Quick check: `python3 render.py s4 30 0.5 veryfast 28 60` (half-res, 60 frames); `python3 preview.py s4 10 50 100` writes stills to frames/.

## Caveats
- If you re-run TTS, use the timing.json it writes. Re-synthesized audio may differ slightly.
- Animations are deterministic given timing.json; I did not verify bit-identical frames across machines/versions.
- I smoke-tested a short half-res render and sim_stripe.py from this archive layout; I did not re-run the full 4K render from it.
