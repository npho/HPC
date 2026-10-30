import sys
from common import *
import numpy as np
from PIL import Image
T = load_timing()
sid = sys.argv[1]
fr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.93
info = T[sid]
S = 1/3
W_, H_ = int(1920*S), int(1080*S)
surf = skia.Surface(W_, H_)
imgs = []
for i, (cu, en) in enumerate(zip(info['cues'], info['ends'])):
    t = cu + fr * (en - cu)
    render_frame(surf, sid, t, T, S)
    a = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    imgs.append(Image.fromarray(a[:, :, :3]))
cols = 3
rows = (len(imgs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W_, rows * H_), (0, 0, 0))
for k, im in enumerate(imgs): sheet.paste(im, ((k % cols) * W_, (k // cols) * H_))
sheet.save(f'frames/contact_{sid}.png'); print(sid, len(imgs), sheet.size)
