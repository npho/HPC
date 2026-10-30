"""Project paths. Scripts resolve every file from here, so they run from any working directory.
This file is identical in every project of the repository."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # the project folder
DATA = ROOT / "data"                            # tracked: timing, simulation and model outputs
BUILD = ROOT / "build"                          # untracked: audio, scene videos, stills, logs
OUT = ROOT / "out"                              # untracked: final videos
ASSETS = Path(os.environ.get("HPC_ASSETS", ROOT.parent / "assets"))
FONTS = ASSETS / "fonts"
MODELS = Path(os.environ.get("KOKORO_DIR", ASSETS / "models"))


def font_path(name):
    """Path of a font file in FONTS, failing loudly if it has not been fetched."""
    p = FONTS / name
    if not p.is_file():
        raise FileNotFoundError(f"{p} not found; run scripts/fetch_assets.sh fonts")
    return str(p)


def build_dir(*parts):
    """BUILD/<parts>, created on first use."""
    p = BUILD.joinpath(*parts)
    p.mkdir(parents=True, exist_ok=True)
    return p
