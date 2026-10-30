import sys, json, os, traceback
import engine as E
from paths import BUILD
from render import load_scenes, timeline, make_ctx
from PIL import Image
SC = load_scenes(); tl = timeline()
only = sys.argv[1:] 
os.makedirs(BUILD / 'stills', exist_ok=True)
r = E.Renderer(size=(1920, 1080))
for i, s in enumerate(tl['scenes']):
    if only and s['id'] not in only: continue
    ctx = make_ctx(tl, i)
    # pick 4 times: late in beats spread across the scene
    nb = len(s['beats'])
    ends = [b['end'] - 0.3 for b in s['beats']]
    picks = [ends[int(k * (nb - 1) / 3)] for k in range(4)] if nb >= 4 else ends[:4]
    sheet = Image.new('RGB', (1920, 1080))
    for k, t in enumerate(picks):
        try:
            p = str(BUILD / 'stills' / '_tmp.png')
            r.png(SC[s['id']], t, ctx, p)
            im = Image.open(p).convert('RGB').resize((960, 540), Image.LANCZOS)
            sheet.paste(im, ((k % 2) * 960, (k // 2) * 540))
        except Exception as e:
            print('ERR', s['id'], t); traceback.print_exc(); break
    sheet.save(BUILD / 'stills' / f"sheet_{i:02d}_{s['id']}.png")
    print('ok', s['id'], [round(x, 1) for x in picks], flush=True)
