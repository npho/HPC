import json
from paths import DATA
from script import SCRIPT
import skia
from fx import *

def load_timing():
    if (DATA / 'timing.json').exists():
        return json.load(open(DATA / 'timing.json'))
    # estimate from word counts if audio isn't finished yet
    T = {}
    for sid, lines in SCRIPT:
        cur = 0.9; cues = []; ends = []
        for i, l in enumerate(lines):
            d = len(l.split()) / 2.7
            cues.append(round(cur, 3)); ends.append(round(cur + d, 3)); cur += d + 0.42
        T[sid] = dict(dur=cur + 0.7, cues=cues, ends=ends)
    return T

def scene_funcs():
    import scenes_a
    F = {k: getattr(scenes_a, k) for k in ('s0', 's1', 's2', 's3') if hasattr(scenes_a, k)}
    for mod in ('scenes_b', 'scenes_c'):
        try:
            m = __import__(mod)
            for k in dir(m):
                if k.startswith('s') and k[1:].isdigit(): F[k] = getattr(m, k)
        except ImportError:
            pass
    return F

def render_frame(surface, sid, t, T, scale):
    c = surface.getCanvas()
    c.clear(rgba(BG))
    c.save(); c.scale(scale, scale)
    F = scene_funcs()
    info = T[sid]
    A = Anim(t, info['cues'], info['dur'], info.get('ends'))
    F[sid](c, A)
    c.restore()
    fa = max(1 - t / 0.7, (t - (info['dur'] - 0.8)) / 0.8)
    if fa > 0.002:
        c.drawRect(skia.Rect.MakeWH(surface.width(), surface.height()), P(BG, min(1.0, fa)))
