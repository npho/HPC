import json, subprocess, numpy as np, soundfile as sf, sys
from script import SCRIPT
from paths import BUILD, DATA, OUT, ROOT
T = json.load(open(DATA / 'timing.json'))
fps = 30; SR = 24000
parts = []
for sid, _ in SCRIPT:
    a, sr = sf.read(BUILD / 'audio' / f'{sid}.wav', dtype='float32'); assert sr == SR
    nf = int(round(T[sid]['dur'] * fps)); n = int(round(nf / fps * SR))
    a = a[:n] if len(a) >= n else np.concatenate([a, np.zeros(n - len(a), np.float32)])
    parts.append(a)
full = np.concatenate(parts)
sf.write(BUILD / 'narration_full.wav', full, SR)
print('audio seconds', len(full) / SR)
files = [BUILD / 'video' / f'{sid}_2.0_veryfast.mp4' for sid, _ in SCRIPT]
open(BUILD / 'concat.txt', 'w').write(''.join(f"file '{f}'\n" for f in files))
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', BUILD / 'concat.txt', '-c', 'copy', BUILD / 'video_only.mp4'])
OUT.mkdir(exist_ok=True)
out = sys.argv[1] if len(sys.argv) > 1 else OUT / f'{ROOT.name}_first_principles_4K.mp4'
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', BUILD / 'video_only.mp4', '-i', BUILD / 'narration_full.wav',
    '-filter_complex', '[1:a]loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[a]', '-map', '0:v', '-map', '[a]',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-movflags', '+faststart', '-shortest', out])
print('wrote', out)
