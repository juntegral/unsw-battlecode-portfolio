# Bot architecture audit artifacts

The Korean report is `research/observations/bot-architecture-audit.md`.
The target is the frozen source in `exp/cand-stack11/bot/`, not a post-verdict configuration.
GH_ON and KX_ON are true in that source; the W12 verdict recommends switching them off.

This audit wrote only new files under `exp/bot-audit/` and the requested report path.
It ran no games, network calls, uploads, or commits and changed no input file.
`SUMMARY.txt` is written last and must contain exactly 20 English lines.

## Scripts

| Script | Inputs | New outputs |
|---|---|---|
| `source_inventory.py` | Baseline and all stack sources, specified docs, local rules, existing patches, analysis tools | SHA manifest, sizes/functions/constants, complete sequential diff |
| `parameter_provenance.py` | Generated constants and all versions' params.hpp | First appearance/wave, value transitions, conservative CONFIG/J/D-J labels |
| `count_replays.js` | Set name, official replay loader, existing parseInd grammar and checked mass ledger | Per-game and aggregate tags/goals/splits/phase/length/gate/health counts; all own turns in gzip TSV |
| `verify_replays.js` | Both original online sets, generated per-game records | Raw-event reconciliation and real BigInt sonar ID inspection; refreshes only generated sonar fields/bundles |
| `inspect_counts.py` | Both generated turn TSVs | Goal overlap, leaf bypass, actual longest split examples |
| `render_tables.py` | Generated totals and constants | Reproducible tables |
| `summarise_populations.py` | Generated per-game bundles, index, existing effect docs | Map/opponent counts, descriptive Wilson intervals, input metadata |
| `validate_audit.py` | All generated records/report and saved input manifests | Final consistency check; never repairs input files |

W11 output lives directly here. W12 output lives in `w12/`.
The `feed` count excludes `conv`; the grammar assigns them different kinds.
F2, gh, kxm, fc and noexit_spare are subsets, not additive actions.
`none` in the explicit-goal table means no F/g/K distance goal, not absence of other pulls.
The ledger's current king breaks equal-length ties by smaller ID.
Source gates asking for a strictly longer ally do not use that tie breaker.

## Reproduction

Run heavy work with `nice -n 15`. Read `memory_pressure` and `df -g /` first.
Stop below 10% reported system-wide free memory or below 20 GB available root disk.
The counter checks those readings before every replay, loads one replay at a time,
uses a 1536 MB V8 heap cap and explicit GC, and pauses one second between games.
The raw verifier also processes one replay at a time and pauses 0.5 seconds.
There is no simulator invocation in these scripts.

The sandbox rejected `setpriority` even when `nice -n 15` was requested.
The inherited actual nice value was 10, saved in generated records.
Do not claim nice 15 was applied successfully.

The source inventory writes new audit outputs only; regenerating it replaces the saved
input snapshot, so keep `source-manifest.json` before rerunning if comparing later changes.
The counter refuses to overwrite an existing turn evidence file.
Use a fresh child directory for a new count:

```sh
nice -n 15 node --max-old-space-size=1536 --expose-gc exp/bot-audit/count_replays.js cand-stack10-online reproduce-w11
nice -n 15 node --max-old-space-size=1536 --expose-gc exp/bot-audit/count_replays.js cand-stack11-online reproduce-w12
```

The completed original counts were checked using:

```sh
nice -n 15 node --max-old-space-size=1536 --expose-gc exp/bot-audit/verify_replays.js
nice -n 15 python3 exp/bot-audit/inspect_counts.py
nice -n 15 python3 exp/bot-audit/render_tables.py
nice -n 15 python3 exp/bot-audit/summarise_populations.py
nice -n 15 python3 exp/bot-audit/parameter_provenance.py
nice -n 15 python3 exp/bot-audit/validate_audit.py
```

The raw verifier is intentionally fixed to the audited root/W12 folders, not the optional
fresh reproduction folders. Counts imported from historical mechanism reports remain
attributed to those reports; this audit did not independently redo their survival/drop
attribution analyses. Tag frequency is not a counterfactual causal effect.

`turn-tags.tsv.gz` contains consecutive gzip members, one header plus one member per game.
Python gzip and standard gzip readers concatenate them correctly. The columns record
game ID, dragon ID, round, length, actual unit counts, current king, visible enemy count,
local d3 including all enemies, normalized action kind, explicit goal, tags and original label.
For a trade's d3 excluding the target, add one to the recorded d3_all_enemies.

Replay files were decoded twice from identical paths. Their entire byte streams were
not hashed again; `replay-input-manifest.json` records sizes and modification times,
plus hashes for the set indices and historical effect reports. Source/document inputs
are SHA-256 checked against `source-manifest.json`.
