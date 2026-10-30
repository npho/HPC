#!/usr/bin/env python3
"""
Render scenes.

  python3 render.py open                    # -> ../build/scenes/open.mp4  (video only, 4K30)
  python3 render.py open --still 3,10.5     # -> ../build/stills/open_<t>.png (fast QA, 1920x1080 by default)
  python3 render.py all --workers 2

Static-frame reuse: every frame is first drawn on a tiny 480x270 surface; if it is identical to the previous
tiny frame the previous full-resolution bytes are re-sent to ffmpeg instead of re-rasterising 4K.
"""
import argparse, json, os, subprocess, sys, time
import numpy as np, skia
sys.path.insert(0, os.path.dirname(__file__))
from engine import LW, LH

BUILD = os.path.join(os.path.dirname(__file__), "..", "build")
TIM = json.load(open(os.path.join(BUILD, "audio", "timings.json")))

def load_scenes():
    from scenes import REGISTRY
    return REGISTRY

def make_surface(w, h):
    s = skia.Surface(w, h)
    c = s.getCanvas(); c.scale(w / LW, h / LH)
    return s, c

def frame_bytes(surf):
    return surf.makeImageSnapshot().tobytes()

def render_scene(sid, W, H, fps, out, workers_hint=""):
    reg = load_scenes()
    sc = reg[sid](TIM.get(sid, {"beats": [[0.7, 5.0]], "dur": 14.0}))
    n = int(round(sc.dur * fps))
    surf, c = make_surface(W, H)
    ts, tc = make_surface(480, 270)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-threads", "1", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    prev_thumb, prev_bytes, reused = None, None, 0
    t0 = time.time()
    for k in range(n):
        t = k / fps
        sc.render(tc, t)
        th = ts.makeImageSnapshot().tobytes()
        if prev_thumb is not None and th == prev_thumb:
            reused += 1
        else:
            sc.render(c, t)
            prev_bytes = frame_bytes(surf); prev_thumb = th
        pr.stdin.write(prev_bytes)
        if k % 150 == 0:
            print(f"[{sid}] {k}/{n} frames, {time.time()-t0:.0f}s, reused {reused}", flush=True)
    pr.stdin.close(); pr.wait()
    print(f"[{sid}] done {n} frames in {time.time()-t0:.0f}s (reused {reused}) -> {out}", flush=True)

def still(sid, times, W, H, outdir):
    reg = load_scenes()
    sc = reg[sid](TIM.get(sid, {"beats": [[0.7, 5.0]], "dur": 14.0}))
    os.makedirs(outdir, exist_ok=True)
    surf, c = make_surface(W, H)
    for t in times:
        sc.render(c, t)
        p = os.path.join(outdir, f"{sid}_{t:06.2f}.png")
        surf.makeImageSnapshot().save(p, skia.kPNG)
        print(p)
    from engine import MISSING
    for m in sorted(MISSING): print("MISSING GLYPH:", m)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--still", default="")
    ap.add_argument("--w", type=int, default=3840)
    ap.add_argument("--h", type=int, default=2160)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    outdir = os.path.join(BUILD, "scenes"); os.makedirs(outdir, exist_ok=True)
    if a.still:
        w, h = (a.w, a.h) if a.w != 3840 else (1920, 1080)
        still(a.scene, [float(x) for x in a.still.split(",")], w, h, os.path.join(BUILD, "stills"))
    elif a.scene == "all":
        from scenes import REGISTRY
        ids = list(REGISTRY.keys())
        procs = []
        for sid in ids:
            while len([p for p in procs if p.poll() is None]) >= a.workers:
                time.sleep(2)
            o = os.path.join(outdir, f"{sid}.mp4")
            if os.path.exists(o) and "--force" not in sys.argv:
                continue
            tmp = o + ".part.mp4"
            procs.append(subprocess.Popen([sys.executable, __file__, sid, "--w", str(a.w), "--h", str(a.h),
                                           "--fps", str(a.fps)], stdout=open(os.path.join(BUILD, f"render_{sid}.log"), "w"),
                                          stderr=subprocess.STDOUT))
        for p in procs: p.wait()
    else:
        o = os.path.join(outdir, f"{a.scene}.mp4")
        tmp = os.path.join(outdir, f"{a.scene}.part.mp4")
        render_scene(a.scene, a.w, a.h, a.fps, tmp)
        os.replace(tmp, o)
