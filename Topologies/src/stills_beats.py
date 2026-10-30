import sys, os
import engine as E
from paths import BUILD, build_dir
from render import load_scenes, timeline, make_ctx
from PIL import Image
SC = load_scenes(); tl = timeline(); ids = [s['id'] for s in tl['scenes']]
r = E.Renderer(size=(1920, 1080))
build_dir('stills'); name = sys.argv[1]; pairs = sys.argv[2:]
sheet = Image.new('RGB', (1920, 1080))
for k, p in enumerate(pairs[:4]):
    sid, b = p.split(':'); b = b.split('@'); frac = float(b[1]) if len(b) > 1 else 0.97; b = int(b[0])
    i = ids.index(sid); ctx = make_ctx(tl, i); s = tl['scenes'][i]
    b0, b1 = s['beats'][b]['start'], s['beats'][b]['end']
    t = b0 + (b1 - b0) * frac
    r.png(SC[sid], t, ctx, str(BUILD / 'stills' / '_tmp.png'))
    sheet.paste(Image.open(str(BUILD / 'stills' / '_tmp.png')).convert('RGB').resize((960, 540), Image.LANCZOS), ((k % 2) * 960, (k // 2) * 540))
sheet.save(BUILD / 'stills' / f'{name}.png'); print(name)
