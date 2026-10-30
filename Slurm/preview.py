"""preview.py - dump still frames for layout review:  python preview.py s03_anatomy 12 30 48 [--w 1920]"""
import os, sys
from engine import Cv, LW, LH
import render

args = sys.argv[1:]
width = 1920
if "--w" in args:
    i = args.index("--w"); width = int(args[i + 1]); del args[i:i + 2]
sid, times = args[0], [float(x) for x in args[1:]]
reg = render.load_registry()
tl = render.timeline()
entry = next(s for s in tl["scenes"] if s["id"] == sid)
spec = reg[sid]
cv = Cv(width, width * 9 // 16)
os.makedirs(os.path.join(render.BUILD, "preview"), exist_ok=True)
for t in times:
    render.draw_frame(cv, entry, spec, t)
    p = os.path.join(render.BUILD, "preview", f"{sid}_{t:06.2f}.png")
    cv.save_png(p)
    print(p)
