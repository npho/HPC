# Same targets in every project; run `make help`. Fonts and models: ../scripts/fetch_assets.sh
PY := uv run python
SCENE ?= s08_backfill
T ?= 10 30

.PHONY: help all sim tts render video smoke stills clean

help: ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/'

all: tts render video ## full rebuild

sim: ## rerun the FIFO vs backfill model -> data/backfill_sweep.{json,log}
	$(PY) src/sim_backfill.py | tee data/backfill_sweep.log

tts: ## narration -> build/audio/, data/timing.json
	VOICE=af_heart SPEED=0.97 $(PY) src/tts.py

render: ## every scene at 4K -> build/video/ (SCALE=1 for 1080p)
	$(PY) src/render.py all

video: ## concat scenes + narration -> out/
	$(PY) src/render.py final

smoke: ## 1080p 60-frame render of SCENE
	$(PY) src/render.py smoke $(SCENE) 60

stills: ## PNGs of SCENE at times T -> build/stills/
	$(PY) src/preview.py $(SCENE) $(T)

clean: ## remove build/ and out/
	rm -rf build out
