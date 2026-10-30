import sys, time, json
from faster_whisper import WhisperModel
m = WhisperModel('base.en', device='cpu', compute_type='int8', cpu_threads=2)
out = {}
for sid in sys.argv[1:]:
    t0 = time.time()
    import soundfile as sf, numpy as np
    a, sr = sf.read(f'audio/{sid}.wav', dtype='float32')
    a16 = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype('float32')
    segs, _ = m.transcribe(a16, language='en', beam_size=1)
    out[sid] = ' '.join(s.text.strip() for s in segs)
    print(sid, round(time.time() - t0), 's', flush=True)
json.dump(out, open('asr_out.json', 'w'), indent=1)
