import sys, json, time, numpy as np, soundfile as sf
sys.path.insert(0,'.')
from script import SCRIPT
from kokoro_onnx import Kokoro
import os
import os
M=os.environ.get('KOKORO_MODELS','./models/')  # dir holding kokoro-v1.0.onnx + voices-v1.0.bin
k=Kokoro(M+'kokoro-v1.0.onnx', M+'voices-v1.0.bin')
VOICE=sys.argv[1] if len(sys.argv)>1 else 'am_michael'
SPEED=float(sys.argv[2]) if len(sys.argv)>2 else 0.97
SR=24000
GAP=0.42      # seconds of silence after each line (a natural breath between ideas)
LEAD=0.9      # silence before first line of a scene (lets the visual establish)
TAIL=1.1      # silence after last line
import os
ONLY=set(sys.argv[3].split(',')) if len(sys.argv)>3 else None
timing=json.load(open('timing.json')) if (ONLY and os.path.exists('timing.json')) else {}
t00=time.time()
for sid,lines in SCRIPT:
    if ONLY and sid not in ONLY: continue
    segs=[]; cues=[]; cur=LEAD
    chunks=[np.zeros(int(LEAD*SR),dtype=np.float32)]
    for i,line in enumerate(lines):
        a,sr=k.create(line, voice=VOICE, speed=SPEED, lang='en-us')
        assert sr==SR
        a=a.astype(np.float32)
        # trim leading/trailing near-silence
        thr=0.003; idx=np.where(np.abs(a)>thr)[0]
        a=a[max(idx[0]-int(0.03*SR),0): idx[-1]+int(0.06*SR)]
        cues.append(round(cur,3))
        chunks.append(a); cur+=len(a)/SR
        g=GAP if i<len(lines)-1 else TAIL
        chunks.append(np.zeros(int(g*SR),dtype=np.float32)); cur+=g
    audio=np.concatenate(chunks)
    sf.write(f'audio/{sid}.wav', audio, SR)
    timing[sid]=dict(dur=round(len(audio)/SR,3), cues=cues, ends=[round(cues[i+1]-GAP,3) if i+1<len(cues) else round(cur-TAIL,3) for i in range(len(cues))])
    print(sid, timing[sid]['dur'], flush=True)
json.dump(timing, open('timing.json','w'), indent=1)
print('total', sum(v['dur'] for v in timing.values()), 'elapsed', time.time()-t00)
