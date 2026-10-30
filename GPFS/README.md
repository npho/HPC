# GPFS / IBM Storage Scale explainer video: reproducible build archive

Output: 3840x2160, 30 fps, ~968 s, narrated, 10 scenes (s0..s9). Video file itself is NOT included (126 MB); everything needed to rebuild it is.

## Layout
- src/       all code. script.py = narration (one line = one visual beat). fx.py = drawing helpers/style. scenes_a/b/c.py = animations. tts.py, render.py, mux.py = pipeline. sim_decluster.py = toy rebuild simulation. asr.py = whisper pronunciation check. preview.py/contact.py = still/contact-sheet QA. edit_script.py/edit_s1.py = one-off script edits I applied (history only; script.py is already the final result).
- data/      timing.json (final per-scene timing/cues that drive animations; the ground truth for sync), earlier timing backups, sim results, starts.json (scene start times), asr_out.json, model_sha256.txt, versions.txt, fonts_used.txt
- audio/     the 10 narration WAVs actually used (24 kHz). Using these skips TTS and reproduces the exact audio.
- notes/     verified-facts notes + build notes (including honest caveats)
- logs/, qa/ render/TTS logs and QA contact sheets

## Environment used
Python 3.13, ffmpeg 6.1.1 (libx264), see requirements.txt (skia-python 144.1, kokoro-onnx 0.6.1, onnxruntime, numpy, soundfile, scipy; faster-whisper + av only for asr.py).
Fonts (system-installed; paths hardcoded in fx.py `_FD`, edit if different): Lora variable (serif/title), Inter Regular/Medium/SemiBold (sans), DejaVu Sans Mono.
Kokoro model files (kokoro-v1.0.onnx, voices-v1.0.bin) are not included (350 MB). Checksums in data/model_sha256.txt. I believe they come from the kokoro-onnx GitHub releases (model-files-v1.0); I did not re-verify the URL when packaging, so confirm against the kokoro-onnx README.

## Rebuild
```
mkdir work && cd work
cp ../src/*.py . ; cp ../data/timing.json . ; mkdir audio out ; cp ../audio/*.wav audio/
# (A) reuse the exact audio: skip to render. (B) re-synthesize: 
#   KOKORO_MODELS=/path/to/models/ python3 tts.py am_michael 1.04      # rewrites audio/*.wav + timing.json
python3 render.py s0,s1,s2,s3,s4,s5,s6,s7,s8,s9 30 2 veryfast 18       # -> out/<sid>_2.0_veryfast.mp4 (slow: CPU, ~1 frame/s-ish per scene; parallelize by scene)
python3 mux.py out/GPFS_first_principles_4K.mp4                         # pads audio to frame counts, concat, loudnorm, AAC
python3 sim_decluster.py                                                # toy simulation -> prints ratios, writes sim_n60.json
```
Quick preview: `python3 render.py s4 30 0.5 veryfast 28 60` (half-res, 60 frames). I ran this and sim_decluster.py from this archive layout as a smoke test; it worked. I did NOT re-run the full 4K render or TTS from the archive.

## Reproducibility caveats (be skeptical)
- Animations are deterministic functions of time + timing.json; frames should reproduce, but I did not verify bit-identical output across machines/skia/ffmpeg versions.
- Re-running TTS may not give identical audio (model/onnxruntime versions); timing.json cues come from the audio actually generated, so if you re-synthesize, use the new timing.json that tts.py writes, not the one here.
- Pronunciation respellings in script.py (e.g. "eye-node", "Al muh den", spaced letters) were tuned by ASR check against this voice/speed only.
- tts.py: `python3 tts.py <voice> <speed> [scene,ids]` with an ids arg re-does only those scenes and merges into timing.json. Constants LEAD 0.9 s, GAP 0.42 s, TAIL 1.1 s.
- Synthetic voice: Kokoro am_michael, speed 1.04.
