"""
tts.py - synthesize the narration (Kokoro-82M via kokoro-onnx, runs offline on CPU) and build
data/timing.json: for every scene, the start time of each beat and the scene duration.

  python tts.py            # synthesize everything (cached by text hash)
  VOICE=am_michael python tts.py   # try another voice

Model files (Apache-2.0 Kokoro weights) come from scripts/fetch_assets.sh (assets/models, or set KOKORO_DIR).
"""
import hashlib
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

from script import SCENES
from paths import BUILD, DATA, MODELS

AUD = os.path.join(BUILD, "audio")
VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "0.97"))
SR = 24000
LEAD = {"s00_title": 1.4}          # silence before the first beat (s); default below
DEFAULT_LEAD = 0.9
GAP = 0.55                          # silence between beats
TAIL = 1.3                          # silence after the last beat
FPS = 30

# Respellings so the speech engine says technical tokens the way people say them.
PRON = {
    "slurmctld": "slurm C T L D",
    "slurmdbd": "slurm D B D",
    "slurmstepd": "slurm step D",
    "slurmd": "slurm D",
    "sbatch": "S batch",
    "srun": "S run",
    "QOS": "Q O S",
    "TRES": "T R E S",
    "GRES": "gress",
    "GPUs": "G P Us",
    "GPU": "G P U",
    "MPI": "M P I",
    "GPFS": "G P F S",
    "BeeGFS": "Bee G F S",
    "LSF": "L S F",
    "IBM": "I B M",
    "DPCS": "D P C S",
    "RMS": "R M S",
    "SchedMD": "Sked M D",
    "Nvidia": "En-vidia",
    "NVIDIA": "En-vidia",
    "Mu'alem": "Moo-ah-lem",
    "Feitelson": "Fight-el-son",
    "MariaDB": "Maria D B",
    "MySQL": "My S Q L",
    "TreeWidth": "Tree Width",
    "MUNGE": "munge",
    "IDs": "I Ds",
    "ID": "I D",
    "Top500": "Top five hundred",
    "cgroups": "C groups",
    "LoadLeveler": "Load Leveler",
}
_pat = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(PRON, key=len, reverse=True)) + r")\b")


def respell(text):
    return _pat.sub(lambda m: PRON[m.group(1)], text)


def beat_wav(kokoro, text, voice, speed):
    key = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(AUD, f"beat_{key}.wav")
    if not os.path.exists(path):
        samples, sr = kokoro.create(respell(text), voice=voice, speed=speed, lang="en-us")
        assert sr == SR, sr
        sf.write(path, samples, sr)
    data, sr = sf.read(path, dtype="float32")
    return data


def main():
    os.makedirs(AUD, exist_ok=True)
    from kokoro_onnx import Kokoro
    k = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))
    timeline = []
    t_global = 0.0
    for sc in SCENES:
        parts, cues, ends = [], [], []
        pos = LEAD.get(sc["id"], DEFAULT_LEAD)
        parts.append(np.zeros(int(pos * SR), np.float32))
        for i, txt in enumerate(sc["beats"]):
            w = beat_wav(k, txt, VOICE, SPEED)
            cues.append(pos)
            parts.append(w)
            pos += len(w) / SR
            ends.append(pos)
            print(f"{sc['id']} beat {i}: {len(w)/SR:5.1f}s  ({len(txt.split())} words)", flush=True)
            if i < len(sc["beats"]) - 1:
                parts.append(np.zeros(int(GAP * SR), np.float32))
                pos += GAP
        pos += TAIL
        parts.append(np.zeros(int(TAIL * SR), np.float32))
        audio = np.concatenate(parts)
        # snap the scene to a whole number of video frames
        frames = int(np.ceil(pos * FPS))
        n = int(round(frames / FPS * SR))
        audio = np.pad(audio, (0, max(0, n - len(audio))))[:n]
        out = os.path.join(AUD, f"{sc['id']}.wav")
        sf.write(out, audio, SR)
        timeline.append(dict(id=sc["id"], chapter=sc["chapter"], cues=cues, ends=ends,
                             duration=frames / FPS, frames=frames, start=t_global))
        t_global += frames / FPS
    with open(DATA / "timing.json", "w") as fh:
        json.dump(dict(voice=VOICE, speed=SPEED, fps=FPS, total=t_global, scenes=timeline), fh, indent=1)
    print(f"total {t_global/60:.2f} min")


if __name__ == "__main__":
    main()
