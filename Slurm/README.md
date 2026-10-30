# Slurm explainer: source
Python 3.13, skia-python, kokoro-onnx, numba, numpy, soundfile, Pillow; ffmpeg on PATH.
Kokoro model files (kokoro-v1.0.onnx, voices-v1.0.bin) go in assets/models/ (kokoro-onnx GitHub release).
  python sim_backfill.py      # toy backfill model -> results/backfill_sweep.json
  python audio.py             # narration (script.py) -> build/timeline.json
  SCALE=2 python render.py all && python render.py final out.mp4   # 4K
  python preview.py <scene> t1 t2 ...   # still frames
