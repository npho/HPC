import sys
from common import *
from paths import build_dir
sid = sys.argv[1]; ts = [float(x) for x in sys.argv[2:]]
T = load_timing()
S = 0.5
D = build_dir('stills')
surf = skia.Surface(int(1920 * S), int(1080 * S))
for t in ts:
    render_frame(surf, sid, t, T, S)
    p = str(D / f'{sid}_{t:06.1f}.png')
    surf.makeImageSnapshot().save(p, skia.kPNG)
    print('saved', p)
