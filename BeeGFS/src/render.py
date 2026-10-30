import sys, os, time, subprocess, json, math
import numpy as np
from common import *

def render_scene(sid, fps, scale, preset, crf, out, max_frames=None):
    T = load_timing()
    dur = T[sid]['dur']
    nf = int(round(dur * fps))
    if max_frames: nf = min(nf, max_frames)
    Wp, Hp = int(1920 * scale), int(1080 * scale)
    surf = skia.Surface(Wp, Hp)
    info = skia.ImageInfo.Make(Wp, Hp, skia.kBGRA_8888_ColorType, skia.kPremul_AlphaType)
    buf = np.empty((Hp, Wp, 4), dtype=np.uint8)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{Wp}x{Hp}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-tune', 'animation', '-pix_fmt', 'yuv420p',
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-g', str(fps * 2), '-threads', '2', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(nf):
        render_frame(surf, sid, f / fps, T, scale)
        if not surf.readPixels(info, buf, Wp * 4, 0, 0):
            raise RuntimeError('readPixels failed')
        p.stdin.write(memoryview(buf).cast('B'))
        if f % 150 == 0:
            print(f'{sid} {f}/{nf} {time.time()-t0:.0f}s', flush=True)
    p.stdin.close(); p.wait()
    print(f'{sid} done {nf} frames in {time.time()-t0:.0f}s', flush=True)

if __name__ == '__main__':
    sids = sys.argv[1].split(',')
    fps = int(sys.argv[2]); scale = float(sys.argv[3]); preset = sys.argv[4]; crf = int(sys.argv[5])
    mx = int(sys.argv[6]) if len(sys.argv) > 6 else None
    for sid in sids:
        render_scene(sid, fps, scale, preset, crf, f'out/{sid}_{scale}_{preset}.mp4', mx)
