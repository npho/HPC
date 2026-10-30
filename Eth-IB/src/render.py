#!/usr/bin/env python3
"""
Render scenes.

  python3 render.py open                    # -> build/video/open.mp4  (video only, 4K30)
  python3 render.py open --still 3,10.5     # -> build/stills/open_<t>.png (fast QA, 1920x1080 by default)
  python3 render.py all --workers 2
  python3 render.py open --w 960 --h 540 --frames 60   # smoke test -> build/video/open_smoke.mp4

Static-frame reuse: every frame is first drawn on a tiny 480x270 surface; if it is identical to the previous
tiny frame the previous full-resolution bytes are re-sent to ffmpeg instead of re-rasterising 4K.
"""
import argparse, json, os, subprocess, sys, time
import numpy as np, skia
from engine import LW, LH
from paths import BUILD, DATA

TIM = json.load(open(DATA / "timing.json")) if (DATA / "timing.json").exists() else {}

def timing(sid):
    """Narration timing of a scene; before tts.py has run, estimate it from word counts (~2.7 words/s)."""
    if sid in TIM: return TIM[sid]
    from script import SCENES
    sc = next((s for s in SCENES if s["id"] == sid), None)
    if sc is None: return {"beats": [[0.7, 5.0]], "dur": 14.0}     # unnarrated scene (refs)
    beats, t = [], 0.7
    for text in sc["beats"]:
        d = len(text.split()) / 2.7; beats.append([t, t + d]); t += d + 0.42
    return {"beats": beats, "dur": t + 0.48}

def load_scenes():
    from scenes import REGISTRY
    return REGISTRY

def make_surface(w, h):
    s = skia.Surface(w, h)
    c = s.getCanvas(); c.scale(w / LW, h / LH)
    return s, c

def frame_bytes(surf):
    return surf.makeImageSnapshot().tobytes()

def render_scene(sid, W, H, fps, out, limit=0):
    reg = load_scenes()
    sc = reg[sid](timing(sid))
    n = int(round(sc.dur * fps))
    if limit: n = min(n, limit)
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
    sc = reg[sid](timing(sid))
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
    ap.add_argument("--frames", type=int, default=0, help="render only the first N frames")
    ap.add_argument("--force", action="store_true", help="with all: re-render scenes that already exist")
    a = ap.parse_args()
    outdir = os.path.join(BUILD, "video"); os.makedirs(outdir, exist_ok=True)
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
            if os.path.exists(o) and not a.force:
                continue
            tmp = o + ".part.mp4"
            procs.append(subprocess.Popen([sys.executable, __file__, sid, "--w", str(a.w), "--h", str(a.h),
                                           "--fps", str(a.fps)], stdout=open(os.path.join(BUILD, f"render_{sid}.log"), "w"),
                                          stderr=subprocess.STDOUT))
        for p in procs: p.wait()
    else:
        name = f"{a.scene}_smoke" if a.frames else a.scene
        o = os.path.join(outdir, f"{name}.mp4")
        tmp = os.path.join(outdir, f"{name}.part.mp4")
        render_scene(a.scene, a.w, a.h, a.fps, tmp, a.frames)
        os.replace(tmp, o)
