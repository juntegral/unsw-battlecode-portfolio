# Current execution checkpoint

The lightweight metadata census is complete: 1,680 games, including the newly arrived
W12. The index and separate game JSON recounts agree on every outcome. No original
file has been modified. This is not the completion marker.

Heavy replay processing and inference are waiting for the user's answer to the
resource exception question. The sandbox refuses `nice -n 15`; inherited niceness
is 10. Never treat elapsed time or the preselected UI choice as acceptance.

Only after explicit acceptance, from the repository root, sequentially:

```sh
nice -n 15 node --max-old-space-size=1024 exp/outcome-review/prepare-v2.js --allow-inherited-10
nice -n 15 node --max-old-space-size=1024 exp/outcome-review/recount.js --allow-inherited-10
nice -n 15 python3 -B exp/outcome-review/analyse-v2.py --allow-inherited-10
nice -n 15 node --max-old-space-size=1024 exp/outcome-review/deep_read.js --allow-inherited-10
nice -n 15 python3 -B exp/outcome-review/render-v3.py
python3 -B exp/outcome-review/finish.py
```

Use one analysis process. Stop and pause if memory_pressure free memory is below
10%, or df -g / available disk is below 20 GiB. Commands still have the requested
nice prefix; the accepted exception must explain that the actual inherited value
stays 10 because setpriority is denied.

The prepared scripts have passed syntax checks, not runtime data verification.
Inspect and resolve every independent-recount mismatch with new script/output paths
before inference. Inspect model convergence and all replay narratives, refine the
report with specific findings, validate completeness, and only then write SUMMARY.txt
last. It must have exactly 20 English lines. Do not rerun builders: their output
versions already exist, and files are exclusively created rather than overwritten.
