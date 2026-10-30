import sys
from common import *
sid = sys.argv[1]; ts = [float(x) for x in sys.argv[2:]]
T = load_timing()
S = 0.5
surf = skia.Surface(int(1920 * S), int(1080 * S))
for t in ts:
    render_frame(surf, sid, t, T, S)
    surf.makeImageSnapshot().save(f'frames/{sid}_{t:06.1f}.png', skia.kPNG)
    print('saved', f'frames/{sid}_{t:06.1f}.png')
