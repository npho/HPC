# Same targets in every project; run `make help`. Fonts and models: ../scripts/fetch_assets.sh
PY := uv run python
SCENE ?= clos
T ?= 10 30
WORKERS ?= 2
RES ?= 4k

.PHONY: help all sim check tts render video smoke stills clean

help: ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/'

all: tts render video ## full rebuild

sim: ## rerun the topology models and self-tests -> data/results.json
	$(PY) src/models.py

check: ## verify every spoken number against data/results.json
	$(PY) src/verify_narration_numbers.py

tts: ## narration -> build/audio/, data/timing.json
	$(PY) src/tts.py

render: ## every scene at RES (4k|1080) -> build/video_$(RES)/
	$(PY) src/render.py all --res $(RES) --workers $(WORKERS)

video: ## concat scenes + narration -> out/ (+ narration.srt)
	$(PY) src/render.py mux --res $(RES)

smoke: ## 1080p 60-frame render of SCENE
	$(PY) src/render.py scene $(SCENE) 60 --res 1080

stills: ## PNGs of SCENE at times T -> build/stills/
	$(PY) src/render.py still $(SCENE) $(T)

clean: ## remove build/ and out/
	rm -rf build out
