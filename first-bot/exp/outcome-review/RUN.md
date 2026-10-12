# Outcome review execution

Only new files are created. Existing outputs are never overwritten. Run from the
repository root. Do not execute the heavy commands until the user explicitly accepts
inherited niceness 10: the sandbox rejects `nice -n 15` with `Operation not permitted`.
Memory pressure and free root disk are checked before work and periodically.

After acceptance, one worker at a time:

```sh
nice -n 15 node exp/outcome-review/prepare.js --allow-inherited-10
nice -n 15 node --max-old-space-size=1024 exp/outcome-review/recount.js --allow-inherited-10
nice -n 15 python3 -B exp/outcome-review/analyse.py --allow-inherited-10
nice -n 15 node --max-old-space-size=1024 exp/outcome-review/deep_read.js --allow-inherited-10
python3 -B exp/outcome-review/build_render.py
nice -n 15 python3 -B exp/outcome-review/render-v2.py
python3 -B exp/outcome-review/finish.py
```

The independent reconstruction must have zero mismatches before inference or deep
reading. If a guard reports `PAUSE`, stop, wait for resources, and resume with new
output paths; do not overwrite the partial file. If W12 arrives after the manifest,
extend the census before writing the completion marker. `SUMMARY.txt` must be the
last written output and exactly 20 English lines.
