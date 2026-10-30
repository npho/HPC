# Same targets in every project; run `make help`. Fonts and models: ../scripts/fetch_assets.sh
PY := uv run python
SCENES := s0,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10
SCENE ?= s4
T ?= 10 50 100
comma := ,

.PHONY: help all sim tts render video smoke stills asr clean

help: ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/'

all: tts render video ## full rebuild

sim: ## rerun the stripe-balance simulation -> data/sim_stripe.json
	$(PY) src/sim_stripe.py

tts: ## narration -> build/audio/, data/timing.json
	$(PY) src/tts.py am_michael 1.04

render: ## every scene at 4K -> build/video/
	$(PY) src/render.py $(SCENES) 30 2 veryfast 18

video: ## concat scenes + narration -> out/
	$(PY) src/mux.py

smoke: ## half-res 60-frame render of SCENE
	$(PY) src/render.py $(SCENE) 30 0.5 veryfast 28 60

stills: ## PNGs of SCENE at times T -> build/stills/
	$(PY) src/preview.py $(SCENE) $(T)

asr: ## whisper transcript of the narration -> data/asr_out.json
	uv run --group asr python src/asr.py $(subst $(comma), ,$(SCENES))

clean: ## remove build/ and out/
	rm -rf build out
