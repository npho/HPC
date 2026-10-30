#!/usr/bin/env python3
"""
Synthesize the narration with Kokoro-82M (ONNX, Apache-2.0) and write per-beat WAVs + timings.

  python3 tts.py [--voice af_heart] [--speed 1.0] [--only open,history]

Outputs:
  build/audio/<scene>_<beat>.wav   one file per beat (24 kHz mono)
  data/timing.json                 per scene: beat start/end (seconds, relative to scene start), scene duration

Model files come from scripts/fetch_assets.sh (assets/models, or set KOKORO_DIR).
"""
import argparse, json, os, re, sys, time
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from script import SCENES
from paths import DATA, MODELS, build_dir

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="af_heart")
ap.add_argument("--speed", type=float, default=1.0)
ap.add_argument("--only", default="")
a = ap.parse_args()

AUD = str(build_dir("audio"))
SR = 24000
LEAD_IN = 0.7          # silence at scene start (fade-in)
GAP_SENT = 0.16        # between sentences inside a beat
GAP_BEAT = 0.42        # after each beat
TAIL = 0.9             # after last beat of a scene (fade-out)

k = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))
tpath = DATA / "timing.json"
timings = json.load(open(tpath)) if tpath.exists() else {}
only = set(filter(None, a.only.split(",")))

def split_sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]

sil = lambda s: np.zeros(int(SR * s), dtype=np.float32)
t0 = time.time()
for sc in SCENES:
    if only and sc["id"] not in only:
        continue
    t = LEAD_IN
    beats = []
    for i, text in enumerate(sc["beats"]):
        parts = []
        for j, sent in enumerate(split_sentences(text)):
            s, sr = k.create(sent, voice=a.voice, speed=a.speed, lang="en-us")
            assert sr == SR
            # trim leading/trailing near-silence from each sentence
            thr = 0.01 * max(1e-6, np.abs(s).max())
            idx = np.where(np.abs(s) > thr)[0]
            s = s[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.05 * SR)]
            if j: parts.append(sil(GAP_SENT))
            parts.append(s.astype(np.float32))
        w = np.concatenate(parts)
        sf.write(os.path.join(AUD, f'{sc["id"]}_{i}.wav'), w, SR)
        beats.append([round(t, 3), round(t + len(w) / SR, 3)])
        t += len(w) / SR + (GAP_BEAT if i < len(sc["beats"]) - 1 else TAIL)
    timings[sc["id"]] = dict(beats=beats, dur=round(t, 3))
    print(f'{sc["id"]:11s} dur {t:6.1f}s   elapsed {time.time()-t0:5.0f}s', flush=True)
    json.dump(timings, open(tpath, "w"), indent=1)

tot = sum(v["dur"] for v in timings.values())
print(f"TOTAL narrated {tot/60:.2f} min over {len(timings)} scenes; voice={a.voice} speed={a.speed}")
