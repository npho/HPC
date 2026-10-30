# Same targets in every project; run `make help`. Fonts and models: ../scripts/fetch_assets.sh
PY := uv run python
SCENE ?= credits
T ?= 10,30
WORKERS ?= 2

.PHONY: help all sim tts render video smoke stills clean

help: ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/'

all: tts render video ## full rebuild

sim: ## rerun the arithmetic and routing models -> data/model_numbers.json
	$(PY) src/model_numbers.py

tts: ## narration -> build/audio/, data/timing.json
	$(PY) src/tts.py --voice af_heart --speed 1.0

render: ## every scene at 4K -> build/video/
	$(PY) src/render.py all --workers $(WORKERS)

video: ## concat scenes + narration + subtitles -> out/ (4K and 1080p)
	$(PY) src/mux.py

smoke: ## half-res 60-frame render of SCENE
	$(PY) src/render.py $(SCENE) --w 960 --h 540 --frames 60

stills: ## PNGs of SCENE at times T (comma-separated) -> build/stills/
	$(PY) src/render.py $(SCENE) --still $(T)

clean: ## remove build/ and out/
	rm -rf build out
