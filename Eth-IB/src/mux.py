#!/usr/bin/env python3
"""
Assemble the final video: concat per-scene mp4s, build the narration track from the per-beat WAVs at the
timings.json offsets, loudness-normalise, write SRT subtitles, mux (4K + a 1080p proxy).
  python3 mux.py
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
from script import SCENES, sub
from scenes import ORDER
from paths import BUILD, DATA, OUT

os.makedirs(OUT, exist_ok=True)
SR = 24000
T = json.load(open(DATA / "timing.json"))
REFS_DUR = 14.0

def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip())

def srt_time(s):
    ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

scenes = [s for s in ORDER if os.path.exists(os.path.join(BUILD, "video", f"{s}.mp4"))]
missing = [s for s in ORDER if s not in scenes]
if missing: print("WARNING: missing scene videos:", missing)

# real durations (video is the clock)
vdur = {s: probe(os.path.join(BUILD, "video", f"{s}.mp4")) for s in scenes}
offs, t0 = {}, 0.0
for s in scenes:
    offs[s] = t0; t0 += vdur[s]
total = t0
print(f"total video {total:.1f} s = {total/60:.2f} min")

audio = np.zeros(int(SR * (total + 1)), dtype=np.float32)
srt, n = [], 1
script = {s["id"]: s["beats"] for s in SCENES}
for s in scenes:
    if s not in T: continue
    for i, (b0, b1) in enumerate(T[s]["beats"]):
        w, sr = sf.read(os.path.join(BUILD, "audio", f"{s}_{i}.wav"), dtype="float32")
        a0 = int(SR * (offs[s] + b0)); audio[a0:a0 + len(w)] += w
        # subtitles: split the beat's sentences, time proportionally to character count
        sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", script[s][i]) if x.strip()]
        tot = sum(len(x) for x in sents); cur = offs[s] + b0; span = b1 - b0
        for x in sents:
            d = span * len(x) / tot
            txt = sub(x)
            # wrap to two lines of <= ~60 chars
            words, lines, ln = txt.split(), [], ""
            for wd in words:
                if len(ln) + len(wd) + 1 > 62 and ln: lines.append(ln); ln = wd
                else: ln = (ln + " " + wd).strip()
            lines.append(ln)
            srt.append(f"{n}\n{srt_time(cur)} --> {srt_time(cur + d)}\n" + "\n".join(lines) + "\n"); n += 1; cur += d
audio = audio[: int(SR * total)]
peak = np.abs(audio).max()
print("peak", peak)
sf.write(os.path.join(BUILD, "narration_raw.wav"), audio, SR)
open(os.path.join(OUT, "ib_vs_ethernet.srt"), "w").write("\n".join(srt))

# concat list
lst = os.path.join(BUILD, "concat.txt")
open(lst, "w").write("".join(f"file '{os.path.abspath(os.path.join(BUILD, 'video', s + '.mp4'))}'\n" for s in scenes))
silent = os.path.join(BUILD, "video_silent.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)

final = os.path.join(OUT, "InfiniBand_vs_Ethernet_4K.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(BUILD, "narration_raw.wav"),
                "-i", os.path.join(OUT, "ib_vs_ethernet.srt"),
                "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", final], check=True)
print("wrote", final, os.path.getsize(final) / 1e6, "MB")
proxy = os.path.join(OUT, "InfiniBand_vs_Ethernet_1080p.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", final, "-map", "0:v", "-map", "0:a", "-map", "0:s", "-vf", "scale=1920:1080:flags=lanczos",
                "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "copy", "-c:s", "mov_text", "-movflags", "+faststart", proxy], check=True)
print("wrote", proxy, os.path.getsize(proxy) / 1e6, "MB")
