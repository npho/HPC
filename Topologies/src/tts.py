#!/usr/bin/env python3
"""Synthesize the narration with Kokoro-82M (ONNX), sentence by sentence, cached.
Produces build/audio/<scene>.wav and data/timing.json:
  scenes[i] = {id, title, start, dur, lead, beats:[{start,end,sentences:[{start,end,text}]}]}
All times in seconds; beat/sentence times are relative to the scene start; the
scene start is absolute in the final video.
"""
import hashlib, json, os, sys, time
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from script import SCENES, spoken, display, split_sentences

from paths import BUILD, DATA, MODELS
CACHE = os.path.join(BUILD, "tts_cache")
AUDIO = os.path.join(BUILD, "audio")
VOICE, SPEED, LANG = "af_heart", 1.0, "en-us"
SR = 24000
GAP_SENT = 0.28       # seconds of silence between sentences in a beat
GAP_BEAT = 0.55       # silence after each beat
LEAD, TAIL = 0.9, 1.1  # silence at the start / end of each scene

# extra hold (seconds) after specific beats, for animations that need room: (scene_id, beat_index)
EXTRA = {
    ("clos", 1): 1.2,
    ("clos", 3): 0.8,
    ("torus", 4): 1.0,
    ("hyper", 0): 0.8,
    ("compare", 0): 1.0,
    ("routing", 0): 0.8,
}


def synth(kokoro, text):
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()
    p = os.path.join(CACHE, key + ".npy")
    if os.path.exists(p):
        return np.load(p)
    samples, sr = kokoro.create(text, voice=VOICE, speed=SPEED, lang=LANG)
    assert sr == SR
    samples = samples.astype(np.float32)
    np.save(p, samples)
    return samples


def main():
    os.makedirs(CACHE, exist_ok=True); os.makedirs(AUDIO, exist_ok=True)
    k = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))
    sil = lambda s: np.zeros(int(s * SR), dtype=np.float32)
    t_abs = 0.0
    out = []
    t0 = time.time()
    for si, sc in enumerate(SCENES):
        chunks = [sil(LEAD)]
        t = LEAD
        beats = []
        for bi, beat in enumerate(sc["beats"]):
            sents = split_sentences(beat)
            bstart = t
            sl = []
            for j, s in enumerate(sents):
                a = synth(k, spoken(s))
                chunks.append(a)
                sl.append(dict(start=t, end=t + len(a) / SR, text=display(s)))
                t += len(a) / SR
                if j < len(sents) - 1:
                    chunks.append(sil(GAP_SENT)); t += GAP_SENT
            gap = GAP_BEAT + EXTRA.get((sc["id"], bi), 0.0)
            chunks.append(sil(gap)); t += gap
            beats.append(dict(start=bstart, end=t - gap, sentences=sl))
        chunks.append(sil(TAIL)); t += TAIL
        wav = np.concatenate(chunks)
        sf.write(os.path.join(AUDIO, f"{si:02d}_{sc['id']}.wav"), wav, SR)
        out.append(dict(id=sc["id"], title=sc["title"], index=si, start=t_abs, dur=len(wav) / SR, beats=beats))
        t_abs += len(wav) / SR
        print(f"{sc['id']:12s} {len(wav)/SR:6.1f}s  (total {t_abs/60:5.2f} min, {time.time()-t0:5.0f}s elapsed)", flush=True)
    tmp = DATA / "timing.json.tmp"
    json.dump(dict(scenes=out, total=t_abs, voice=VOICE, speed=SPEED, sr=SR), open(tmp, "w"), indent=1)
    os.replace(tmp, DATA / "timing.json")
    print(f"total {t_abs/60:.2f} min")


if __name__ == "__main__":
    main()
