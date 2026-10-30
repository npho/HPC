import json, subprocess, numpy as np, soundfile as sf, os, sys
from script import SCRIPT
T = json.load(open('timing.json'))
fps = 30; SR = 24000
parts = []
for sid, _ in SCRIPT:
    a, sr = sf.read(f'audio/{sid}.wav', dtype='float32'); assert sr == SR
    nf = int(round(T[sid]['dur'] * fps)); n = int(round(nf / fps * SR))
    a = a[:n] if len(a) >= n else np.concatenate([a, np.zeros(n - len(a), np.float32)])
    parts.append(a)
full = np.concatenate(parts)
sf.write('out/narration_full.wav', full, SR)
print('audio seconds', len(full) / SR)
files = [f'out/{sid}_2.0_veryfast.mp4' for sid, _ in SCRIPT]
open('out/concat.txt', 'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in files))
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'out/concat.txt', '-c', 'copy', 'out/video_only.mp4'])
out = sys.argv[1]
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'out/video_only.mp4', '-i', 'out/narration_full.wav',
    '-filter_complex', '[1:a]loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[a]', '-map', '0:v', '-map', '[a]',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-movflags', '+faststart', '-shortest', out])
print('wrote', out)
