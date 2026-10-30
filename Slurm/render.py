"""
render.py - render scenes to 4K H.264 with hold-frame detection, then mux narration.

  python render.py scene s05_job          # render one scene (video only) -> build/video/s05_job.mp4
  python render.py all                    # all scenes
  python render.py final                  # concat + audio mux -> out/slurm_first_principles_4k.mp4
Env: SCALE=2 (4K), 1 (1080p); CRF; PRESET
"""
import json, os, subprocess, sys, time
import importlib
import skia
from engine import Cv, LW, LH, PAL, col
from scenes.common import hud, Timing

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SCENE_MODULES = ["scenes.a", "scenes.b", "scenes.c", "scenes.d"]


def load_registry():
    reg = {}
    for m in SCENE_MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name == m:
                continue
            raise
        reg.update(mod.SCENES)
    return reg


def timeline():
    with open(os.path.join(BUILD, "timeline.json")) as fh:
        return json.load(fh)


def draw_frame(cv, entry, spec, t):
    S = Timing(entry["cues"], entry["ends"], entry["duration"])
    cv.clear("bg")
    spec["draw"](cv, t, S)
    hud(cv, entry["chapter"], spec.get("sources"), t, entry["duration"])
    # global fades through the background colour
    fade = 0.45
    a = 0.0
    if t < fade:
        a = 1 - t / fade
    elif t > entry["duration"] - fade:
        a = 1 - (entry["duration"] - t) / fade
    if a > 0:
        cv.rect(-5, -5, LW + 10, LH + 10, fill="bg", a=min(1.0, a))


def pixfmt(cv):
    ct = cv.surface.imageInfo().colorType()
    return "bgra" if ct == skia.kBGRA_8888_ColorType else "rgba"


def render_scene(sid, scale=None, out=None, preset=None, crf=None, fps=30):
    scale = int(os.environ.get("SCALE", "2")) if scale is None else scale
    preset = preset or os.environ.get("PRESET", "veryfast")
    crf = crf or os.environ.get("CRF", "20")
    reg = load_registry()
    tl = timeline()
    entry = next(s for s in tl["scenes"] if s["id"] == sid)
    spec = reg[sid]
    W, H = LW * scale, LH * scale
    cv = Cv(W, H)
    probe = Cv(LW // 2, LH // 2)
    os.makedirs(os.path.join(BUILD, "video"), exist_ok=True)
    out = out or os.path.join(BUILD, "video", f"{sid}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", pixfmt(cv), "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-g", "60", "-tune", "animation",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-r", str(fps), out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames = entry["frames"]
    last_probe, last_full = None, None
    n_full = 0
    t0 = time.time()
    for f in range(frames):
        t = f / fps
        draw_frame(probe, entry, spec, t)
        pb = probe.rgba()
        if pb == last_probe and last_full is not None:
            ff.stdin.write(last_full)
            continue
        draw_frame(cv, entry, spec, t)
        last_full = cv.rgba()
        last_probe = pb
        n_full += 1
        ff.stdin.write(last_full)
        if f % 150 == 0:
            print(f"  {sid}: frame {f}/{frames}  unique={n_full}  {time.time()-t0:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"{sid}: {frames} frames, {n_full} rendered at full res ({100*n_full/frames:.0f}%), {time.time()-t0:.0f}s")


def final(out_path, with_audio=True):
    tl = timeline()
    vids = [os.path.join(BUILD, "video", f"{s['id']}.mp4") for s in tl["scenes"]]
    lst = os.path.join(BUILD, "concat.txt")
    with open(lst, "w") as fh:
        for v in vids:
            fh.write(f"file '{v}'\n")
    # audio: concatenate scene wavs
    awl = os.path.join(BUILD, "audio_concat.txt")
    with open(awl, "w") as fh:
        for s in tl["scenes"]:
            fh.write(f"file '{s['wav']}'\n")
    full_wav = os.path.join(BUILD, "narration_full.wav")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", awl,
                           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", full_wav])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                           "-i", full_wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                           "-b:a", "192k", "-movflags", "+faststart", "-shortest", out_path])
    print("wrote", out_path)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "scene":
        for sid in sys.argv[2:]:
            render_scene(sid)
    elif cmd == "all":
        for s in timeline()["scenes"]:
            render_scene(s["id"])
    elif cmd == "final":
        final(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "out", "slurm_first_principles_4k.mp4"))
