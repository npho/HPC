# Build notes (how it was made, what went wrong)
- Request: 3Blue1Brown x Tufte style explainer on GPFS / Spectrum Scale: history, FAST'02 paper, internals (most time), configs/hardware, HPC context; 4K; natural voice-over.
- Manim could not be installed in the sandbox (no pango dev libs) -> custom skia-python 2D renderer at 1920x1080 logical, scaled 2x to 3840x2160, raw BGRA piped to ffmpeg libx264 (veryfast, crf 18, tune animation), 30 fps.
- Audio: Kokoro-ONNX am_michael, speed 1.04, per-line synthesis; each line = one visual beat; cue times in timing.json drive animation.
- Mux: audio padded to exact frame counts per scene, concat, loudnorm I=-16 TP=-1.5 LRA=9, AAC 192k.
- Style: dark canvas; blue=data/clients, amber=tokens/metadata, green=healthy/spare, red=failure/contention, violet=servers; Tufte sidenotes, direct labels, hairlines, small multiples.
- Fixes: first script ran ~17 min -> trimmed; GFS Baskerville lacked Latin glyphs -> Lora; arrow glyph fallback to Inter; s1 had 6-line script vs 5 beats -> rewrote to 5; ASR check found "inode"/"Almaden" mispronounced -> respelled, re-synthesized s1,s3,s4,s7.
- Self-corrections: toy sim (6.0x at 60 disks) exceeds IBM's documented 3-4x; narration says to trust IBM's number. Block-size model is illustrative.
- Not done: full 4K re-render from this archive (only a half-res 60-frame smoke test + sim run); no human end-to-end viewing by me.
