"""sheet.py <scene> t1 t2 ... -> build/stills/sheet_<scene>.png (2-col contact sheet at 960 px per frame)"""
import sys, subprocess, glob, os
from PIL import Image
from paths import BUILD
sid, ts = sys.argv[1], sys.argv[2:]
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.py"), sid, *ts, "--w", "960"], check=True, capture_output=True)
ims = [Image.open(BUILD / "stills" / f"{sid}_{float(t):06.2f}.png") for t in ts]
cols = 2; rows = (len(ims) + 1) // 2
W, H = ims[0].size
sh = Image.new("RGB", (W * cols, H * rows))
for i, im in enumerate(ims): sh.paste(im, ((i % cols) * W, (i // cols) * H))
out = BUILD / "stills" / f"sheet_{sid}.png"; sh.save(out); print(out)
