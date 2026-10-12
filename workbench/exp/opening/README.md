# Opening replay study

Only `exp/opening/**` and `research/observations/opening-book.md` are writable outputs. No network, uploads, games, commits, or opponent source reads.

Run in order from the repository root:

```sh
node exp/opening/extract.js
node exp/opening/augment.js
node exp/opening/extract.js
node exp/opening/refine.js
node exp/opening/orientation.js
node --max-old-space-size=2400 exp/opening/aggregate.js
node --max-old-space-size=2400 exp/opening/describe.js
node --max-old-space-size=2400 exp/opening/deep.js
~/.aside/runtime/bin/python3 exp/opening/draw.py
node --max-old-space-size=2400 exp/opening/report.js
node --max-old-space-size=2400 exp/opening/check.js
node --max-old-space-size=2400 exp/opening/summary.js
```

`population.json` freezes the top index and all eligible online sets, and includes local replay aliases and excluded diagnostics. `augment.js` inventories earlier own-candidate local experiments beyond the previous spatial study, using the same replay completion-time cutoff. Run it before a fresh extraction, or run extraction again to complete the added tasks. Byte-identical local files are extracted once; aliases are documented separately. Proxy-generation experiments are excluded. Online opponents are the specified top seven; lower-team auto sets are excluded.

`extract.js` runs exactly two workers. Each loads the validated fast decoder once, then performs primary mass-ledger reconstruction and a separate replay-authoritative recount. The primary observes `turnStart` before movement and takes only the first turn of each checkpoint for snapshots. Movement paths use every successful simulated step, including sprint steps. The independent implementation follows `dragonUpdate` and explicit split bodies and uses the previously independent spatial graph implementation. It does not use primary hooks. Both count split rounds/lengths/child heads and r25 frontier bins for all games. Layout identity is shared; it is not an independently verified hidden seed.

`games.jsonl.gz` contains every physical head's r0–50 path and action, exact split records, snapshots, and the first enemy collision anywhere in the replay. `recount.jsonl.gz` contains independently counted split tuples and r25 bins. Concatenated gzip members are intentional and standard gunzip readers support them. No uncompressed copy is retained. `refine.js` checks local map-layout metadata against actual natural spawn support and corrects body-contact accounting if the defender dies in an unrelated later action in the same round. It rewrites the compressed cache atomically and records every correction.

`tables.json` is written before deep reads or the report. It contains complete per-game split schedules, checkpoint tiles, arrival records, pooled counts, conditional checkpoint denominators, tile heatmaps normalized to physical map-file starting side A (DRAGON 0); replay team colors may be swapped, K=5 action-based opening clusters with all member keys (initial roots and the first long reversed child's early actions); separate spaceClusters summarize later space outcomes, opponent contingency counts, observed medoid scripts for each side, and both primary/independent per-map totals. Each root/descendant label in `scripts.json` is stable relative to its parent; server ids are evidence rather than deployment constants. Waypoints and scheduled split sizes are observational templates, not tested policies. Unknown layouts stay separate. Target counts in the report use the largest-remainder rounding of winning cluster mean bin counts.

`deep-selection.json` is written after clusters with sizes. Deep cases are winning medoids of the largest side-specific winner cluster, plus ours nearest its cohort's r25 bin means. Full split/action/path evidence is in `deep-*.json`. `boards.json` and two PNGs show full Devil a and Trophy boards at r0/r10/r25. `heatmap-*.png` shows all requested checkpoint heatmaps on a common within-map scale.

Resource gates stop new work at memory free <10% or disk free <21 GiB (stricter than 21 decimal GB). Extraction has two workers; refinement and later stages are sequential. All indexes and raw replays outside the output scope are read-only. `SUMMARY.txt` is generated last and has exactly 15 lines.
