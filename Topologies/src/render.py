#!/usr/bin/env python3
"""Render driver.
  python render.py still <scene_id> <t1> [t2 ...]     1080p PNG stills into build/stills/
  python render.py scene <scene_id> [N] [--res 4k|1080]  render one scene's silent video into build/video_<res>/
                                                     (first N frames only -> <scene>_smoke.mp4)
  python render.py all   [--res 4k|1080] [--workers 2]
  python render.py mux   [--res 4k|1080]              concat videos + padded narration -> out/
"""
import sys, os, json, math, subprocess, time, importlib
import numpy as np
import soundfile as sf
import engine as E

from paths import BUILD, DATA, OUT


def load_scenes():
    SC = {}
    for m in ("scenes_a", "scenes_b", "scenes_c"):
        try:
            SC.update(importlib.import_module(m).SC)
        except ModuleNotFoundError as e:
            if e.name != m:
                raise
    return SC


def timeline():
    return json.load(open(DATA / "timing.json"))


def make_ctx(tl, i):
    s = tl["scenes"][i]
    return E.Ctx(s, i, len(tl["scenes"]), None)


def nframes(s):
    return int(math.ceil(s["dur"] * E.FPS))


def render_scene(sid, res="4k", out_dir=None, limit=None):
    SC = load_scenes(); tl = timeline()
    idx = [s["id"] for s in tl["scenes"]].index(sid)
    s = tl["scenes"][idx]
    ctx = make_ctx(tl, idx)
    size = (E.W, E.H) if res == "4k" else (1920, 1080)
    r = E.Renderer(size=size)
    out_dir = out_dir or os.path.join(BUILD, "video_" + res)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{idx:02d}_{sid}{'_smoke' if limit else ''}.mp4")
    enc = E.open_encoder(path, size[0], size[1], crf=18 if res == "4k" else 20, threads=1)
    n = nframes(s) if limit is None else min(limit, nframes(s))
    t0 = time.time(); changed = 0
    for f in range(n):
        data, ch = r.frame(SC[sid], f / E.FPS, ctx)
        changed += ch
        enc.stdin.write(data)
        if f % 150 == 0:
            print(f"[{sid}] {f}/{n}  full-res frames {changed}  {time.time()-t0:.0f}s", flush=True)
    enc.stdin.close(); enc.wait()
    print(f"[{sid}] done {n} frames, {changed} unique, {time.time()-t0:.0f}s -> {path}", flush=True)
    return path


def cmd_still(sid, ts):
    SC = load_scenes(); tl = timeline()
    idx = [s["id"] for s in tl["scenes"]].index(sid)
    ctx = make_ctx(tl, idx)
    r = E.Renderer(size=(1920, 1080))
    os.makedirs(os.path.join(BUILD, "stills"), exist_ok=True)
    for t in ts:
        p = os.path.join(BUILD, "stills", f"{sid}_{t:06.1f}.png")
        r.png(SC[sid], t, ctx, p)
        print(p)


def srt_time(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"


def cmd_mux(res="4k"):
    tl = timeline(); os.makedirs(OUT, exist_ok=True)
    SR = tl["sr"]
    vdir = os.path.join(BUILD, "video_" + res)
    lst = os.path.join(BUILD, f"concat_{res}.txt")
    wavs, srt, k = [], [], 1
    cum = 0.0
    for i, s in enumerate(tl["scenes"]):
        n = nframes(s); dur_v = n / E.FPS
        a, sr = sf.read(os.path.join(BUILD, "audio", f"{i:02d}_{s['id']}.wav"), dtype="float32")
        pad = int(round(dur_v * SR)) - len(a)
        if pad > 0:
            a = np.concatenate([a, np.zeros(pad, dtype=np.float32)])
        else:
            a = a[:int(round(dur_v * SR))]
        wavs.append(a)
        for b in s["beats"]:
            for sn in b["sentences"]:
                srt.append(f"{k}\n{srt_time(cum + sn['start'])} --> {srt_time(cum + sn['end'])}\n{sn['text']}\n"); k += 1
        cum += dur_v
    sf.write(os.path.join(BUILD, "narration_full.wav"), np.concatenate(wavs), SR)
    open(os.path.join(OUT, "narration.srt"), "w").write("\n".join(srt))
    with open(lst, "w") as f:
        for i, s in enumerate(tl["scenes"]):
            f.write(f"file '{os.path.join(vdir, f'{i:02d}_{s['id']}.mp4')}'\n")
    name = "hpc_topologies_4k.mp4" if res == "4k" else "hpc_topologies_1080p.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
           "-i", os.path.join(BUILD, "narration_full.wav"),
           "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", "-shortest", os.path.join(OUT, name)]
    subprocess.check_call(cmd)
    print("wrote", os.path.join(OUT, name), f"{cum/60:.2f} min")


if __name__ == "__main__":
    a = sys.argv[1:]
    res = "4k"
    if "--res" in a:
        i = a.index("--res"); res = a[i + 1]; del a[i:i + 2]
    workers = 2
    if "--workers" in a:
        i = a.index("--workers"); workers = int(a[i + 1]); del a[i:i + 2]
    cmd = a[0]
    if cmd == "still":
        cmd_still(a[1], [float(x) for x in a[2:]])
    elif cmd == "scene":
        render_scene(a[1], res, limit=int(a[2]) if len(a) > 2 else None)
    elif cmd == "all":
        tl = timeline(); ids = [s["id"] for s in tl["scenes"]]
        # longest-first greedy over workers
        procs = []; pending = sorted(ids, key=lambda i: -[s for s in tl["scenes"] if s["id"] == i][0]["dur"])
        done = set(f for f in os.listdir(os.path.join(BUILD, "video_" + res))) if os.path.isdir(os.path.join(BUILD, "video_" + res)) else set()
        pending = [i for i in pending if f"{ids.index(i):02d}_{i}.mp4" not in done]
        running = []
        while pending or running:
            running = [p for p in running if p.poll() is None]
            while pending and len(running) < workers:
                sid = pending.pop(0)
                running.append(subprocess.Popen([sys.executable, __file__, "scene", sid, "--res", res],
                                                stdout=open(os.path.join(BUILD, f"render_{sid}.log"), "w"), stderr=subprocess.STDOUT))
            time.sleep(2)
        print("all scenes rendered")
    elif cmd == "mux":
        cmd_mux(res)


def dry_scene(sid):
    """record every frame (catches exceptions) and count frames that change at preview resolution"""
    SC = load_scenes(); tl = timeline()
    idx = [s["id"] for s in tl["scenes"]].index(sid)
    s = tl["scenes"][idx]; ctx = make_ctx(tl, idx)
    r = E.Renderer(size=(480, 270)); prev = None; ch = 0; t0 = time.time()
    n = nframes(s)
    for f in range(n):
        pic = r.record(SC[sid], f / E.FPS, ctx)
        pc = r.surf.getCanvas(); pc.save(); pc.scale(0.25, 0.25); pc.drawPicture(pic); pc.restore()
        a = r.surf.makeImageSnapshot().toarray()
        if prev is None or not np.array_equal(a, prev):
            ch += 1
        prev = a
    return sid, n, ch, time.time() - t0


if __name__ == "__main__" and sys.argv[1] == "dry":
    import multiprocessing as mp
    tl = timeline(); ids = [s["id"] for s in tl["scenes"]]
    with mp.Pool(2) as pool:
        tot_n = tot_c = 0
        for sid, n, ch, dt in pool.imap_unordered(dry_scene, ids):
            tot_n += n; tot_c += ch
            print(f"{sid:12s} frames {n:5d}  changing {ch:5d} ({100*ch/n:4.0f}%)  {dt:5.0f}s", flush=True)
        print(f"TOTAL frames {tot_n}  changing {tot_c}")
