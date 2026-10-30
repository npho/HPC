# AGENTS.md

Guide for anyone (human or AI) maintaining this repository. Keep it current when conventions change.

## What this is
An archive of narrated 4K explainer videos on HPC topics. Each top-level folder rebuilds one video from source: narration script -> Kokoro TTS -> skia-python frames piped to ffmpeg -> muxed MP4. Videos, audio and downloaded assets are never committed.

## Repository layout
```
pyproject.toml, uv.lock    uv workspace; one shared .venv; members = the six project folders
.python-version            3.13
scripts/fetch_assets.sh    fonts -> assets/fonts, Kokoro models -> assets/models (untracked)
<Project>/
  pyproject.toml           project deps, exact pins, [tool.uv] package = false
  Makefile                 standard targets (below)
  README.md                user-facing: Build, Layout, Caveats
  src/                     all code; scripts run as `uv run python src/<x>.py` from the project folder
  src/paths.py             ROOT, DATA, BUILD, OUT, FONTS, MODELS, font_path(), build_dir()
  data/                    tracked: timing.json, simulation/model outputs, original build records
  notes/                   <topic>-first-principles-notes.md (facts, sources, corrections) and build notes
  qa/                      tracked QA images (optional)
  build/, out/             untracked: intermediates / final videos
```

## Rules
- **Paths:** never hardcode absolute or cwd-relative paths. Import from `src/paths.py`. Load fonts with `font_path("<file>")`; all fonts live flat in `assets/fonts` under their upstream filenames. Env overrides: `HPC_ASSETS` (assets root), `KOKORO_DIR` (models).
- **`src/paths.py` is byte-identical in every project.** Edit it everywhere or nowhere.
- **Python:** only through uv. Add a dependency to the project's `pyproject.toml` with an exact pin, then `uv lock` at the root. No `requirements.txt`, no `pip install`. Optional tools go in a dependency group (e.g. `asr`).
- **Makefile targets** are the public interface and share names across projects: `help all sim tts render video smoke stills clean`, plus `check` (Topologies) and `asr` (storage videos). Variables: `SCENE`, `T`, and `WORKERS`/`RES` where supported. Each target maps to one existing script call; keep the scripts' own CLIs as they are.
- **Outputs:** scene videos -> `build/video*/`, stills and contact sheets -> `build/stills/`, audio -> `build/audio/`, final MP4/SRT -> `out/`. Timing -> `data/timing.json` (tracked: it pins animation sync to the narration).
- **Determinism:** scenes are pure functions of time and timing; any randomness is seeded. Tracked `data/` files must be reproducible by `make sim`; after changing a model, rerun it and review the `data/` diff.
- **Smoke renders** never overwrite full renders (`*_smoke.mp4` or a scale-tagged filename).
- **Content:** every spoken or on-screen number must trace to a source in `notes/` or to a model in `src/`. Record corrections in the notes. Do not change narration, visuals or `fx.py`/`engine.py` styling during refactors unless asked; such changes alter the delivered video.

## Pipeline families
| Family | Projects | Entry scripts |
|---|---|---|
| Storage | GPFS, Lustre, BeeGFS | `tts.py`, `render.py <ids> fps scale preset crf [frames]`, `mux.py`, `preview.py`, `contact.py`, `asr.py` |
| Engine | Eth-IB, Topologies | `tts.py`, `render.py` (argparse / subcommands), `mux.py` (Eth-IB) or `render.py mux` |
| Slurm | Slurm | `tts.py`, `render.py scene\|all\|smoke\|final`, `preview.py`, `sheet.py`; scenes are the `src/scenes/` package |

In the storage family these files are **byte-identical** across the three projects: `paths.py common.py tts.py render.py mux.py asr.py preview.py contact.py`. `fx.py`, `lx.py`, `script.py`, `scenes_*.py` and the sims are per-video and intentionally differ (e.g. the Lustre/BeeGFS alpha fix in `fx.py`, the BeeGFS "targets" label in `lx.py`). Check before committing:
```
for f in paths.py common.py tts.py render.py mux.py asr.py preview.py contact.py; do
  cmp GPFS/src/$f Lustre/src/$f && cmp GPFS/src/$f BeeGFS/src/$f; done
md5 -q */src/paths.py | sort -u | wc -l     # must print 1
```

Delivered voices: storage family `am_michael` at 1.04; Eth-IB and Topologies `af_heart` at 1.0; Slurm `af_heart` at 0.97. The Makefile `tts` targets encode these.

## Verifying a change
Full renders take hours on CPU; verify cheaply instead:
1. `uvx ruff check --select F821,F822,F823,E9,F63,F7 --ignore F405 .` (undefined names, syntax). Do not reformat: the archived code keeps its original terse style.
2. `make sim` in affected projects; `git diff data/` should be empty unless a model changed on purpose. `make check` in Topologies (59/59).
3. `make stills SCENE=... T=...` and look at the PNGs; `make smoke` for a short encode.
4. TTS on macOS reproduced the archived storage-video scene durations exactly; still review `data/timing.json` diffs after `make tts`.

## Commits
- One project or one concern per commit. Title: one short descriptive sentence ending with a period. Body: optionally 1–3 summary sentences, then a dashed list of short changes.
- No AI attribution of any kind: no `Co-Authored-By` trailers, no tool names, no generated-by lines.
- `git commit` takes the whole index: before committing one project, check `git status` for renames staged by `git mv` in other projects.
- The first commit after the README is the untouched import of the original archives; diff against it to see what refactors changed.
