import sys, glob
from PIL import Image
from paths import BUILD
sid = sys.argv[1]; fs = sorted(glob.glob(str(BUILD / "stills" / f"{sid}_*.png")))
if len(sys.argv) > 2: fs = [f for f in fs if any(f"_{int(float(x)):03d}." in f for x in sys.argv[2].split(","))]
cols = 2; w, h = 960, 540
rows = (len(fs) + 1) // 2
S = Image.new("RGB", (cols * w, rows * h))
for i, f in enumerate(fs):
    S.paste(Image.open(f).convert("RGB").resize((w, h)), ((i % cols) * w, (i // cols) * h))
S.save(BUILD / "stills" / f"sheet_{sid}.png"); print(len(fs))
