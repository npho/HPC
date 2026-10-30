#!/usr/bin/env bash
# Download the fonts and Kokoro TTS model files every project needs into assets/ (untracked).
#   scripts/fetch_assets.sh            fonts + models
#   scripts/fetch_assets.sh fonts      fonts only (enough for stills and renders)
# Override the destination with HPC_ASSETS=/path/to/assets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="${HPC_ASSETS:-$ROOT/assets}"
FONTS="$ASSETS/fonts"
MODELS="$ASSETS/models"
WHAT="${1:-all}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

get() { # url dest
  [ -s "$2" ] && return 0
  echo "fetch $(basename "$2")"
  curl -fsSL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"
}

fonts() {
  mkdir -p "$FONTS"
  local GF=https://github.com/google/fonts/raw/main/ofl/lora
  get "$GF/Lora%5Bwght%5D.ttf" "$FONTS/Lora-Variable.ttf"
  get "$GF/Lora-Italic%5Bwght%5D.ttf" "$FONTS/Lora-Italic-Variable.ttf"

  local ET=https://github.com/edwardtufte/et-book/raw/gh-pages/et-book
  for f in et-book-roman-line-figures et-book-bold-line-figures et-book-display-italic-old-style-figures; do
    get "$ET/$f/$f.ttf" "$FONTS/$f.ttf"
  done

  local CTAN=https://mirrors.ctan.org/fonts
  for f in lmroman10-regular lmroman10-italic lmmono10-regular; do
    get "$CTAN/lm/fonts/opentype/public/lm/$f.otf" "$FONTS/$f.otf"
  done
  get "$CTAN/lm-math/opentype/latinmodern-math.otf" "$FONTS/latinmodern-math.otf"
  for f in texgyrepagella-regular texgyrepagella-bold texgyrepagella-italic texgyrepagella-bolditalic texgyreheros-regular; do
    get "$CTAN/tex-gyre/opentype/$f.otf" "$FONTS/$f.otf"
  done

  if [ ! -s "$FONTS/Inter-SemiBold.otf" ]; then
    get https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip "$TMP/inter.zip"
    unzip -qjo "$TMP/inter.zip" extras/otf/Inter-Regular.otf extras/otf/Inter-Medium.otf extras/otf/Inter-SemiBold.otf -d "$FONTS"
  fi

  if [ ! -s "$FONTS/DejaVuSerif-Italic.ttf" ]; then
    get https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.tar.bz2 "$TMP/dejavu.tar.bz2"
    tar xjf "$TMP/dejavu.tar.bz2" -C "$TMP"
    for f in DejaVuSansMono DejaVuSerif DejaVuSerif-Bold DejaVuSerif-Italic; do
      cp "$TMP/dejavu-fonts-ttf-2.37/ttf/$f.ttf" "$FONTS/"
    done
  fi
}

models() {
  mkdir -p "$MODELS"
  local KR=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
  get "$KR/kokoro-v1.0.onnx" "$MODELS/kokoro-v1.0.onnx"
  get "$KR/voices-v1.0.bin" "$MODELS/voices-v1.0.bin"
  # Checksums recorded when the videos were built.
  (cd "$MODELS" && shasum -a 256 -c "$ROOT/GPFS/data/model_sha256.txt")
}

case "$WHAT" in
  fonts) fonts ;;
  models) models ;;
  all) fonts; models ;;
  *) echo "usage: $0 [all|fonts|models]" >&2; exit 2 ;;
esac
echo "assets in $ASSETS"
