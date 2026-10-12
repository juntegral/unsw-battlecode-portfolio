# Pocket harvest replay study

Write scope is `exp/pocket/**` and `research/observations/pocket-harvest.md`. No network, new games, uploads, commits, or opponent source reads.

Run from the repository root, sequentially:

```sh
node exp/pocket/extract.js
node exp/pocket/finalize.js
node exp/pocket/refine_relay.js
node exp/pocket/aggregate.js
node exp/pocket/occupancy.js
node exp/pocket/verify.js
node exp/pocket/verify.js compare
node exp/pocket/verify_fountains.js
node exp/pocket/blocking.js
node exp/pocket/verify_blocking.js
node exp/pocket/deep.js
python3 exp/pocket/draw_boards.py # requires Pillow
node exp/pocket/finish_tables.js
node exp/pocket/report.js
node exp/pocket/archive.js
node exp/pocket/check.js
node exp/pocket/summary.js
```

`population.json` freezes the full available top index, W0–W12 (15 sets), and all available `exp/v1/*-px4` games. Only the five requested map families are decoded. The nine earlier online families are outside this brief's W0–W12 scope. Elite games with a stalled team (100+ rounds, ping=0, splits<=3) remain in the raw cache and are excluded from tables. Ambiguous layouts remain separate.

`episodes.jsonl` is a per-game event cache: metadata, per-team counts, pocket appearances, physical-head episodes, and pocket-death provenance. Each episode records entry/birth, length, round/sequence, mouth staff (id,length,distance,tile), natural/drop intake, splits and child fate, end/cause/action, sprint cost, drops and later eaters. `episodes.jsonl.gz` is its lossless compressed delivery copy; `archive.json` stores byte sizes and SHA-256 checked against decompressed content. `geometry-*.json` records pocket depth, mouths, tiles and fountain membership. Coordinates use `tile=y*W+x`.

A physical-head episode stops on leaving its pocket, death or game end. `kind=entry` means a geometric crossing; `initial` and `splitBirth` are separate. A root's `family` also includes descendants born in the same pocket until they leave. A child born in another pocket is an immediate export from the old pocket and starts a separate root there. Thus physical intervals and harvest families each partition their own mass flows, rather than double-counting descendants.

`rawNet = natural + ownDrop + enemyDrop - sprintCost - deathLength`.
`recycledNet = rawNet + laterOwnRecovery - ownPocketDrop`.
The last subtraction removes duplicate intake of pearls already credited to another pocket death. Recovery is followed to game end, including outside the pocket. This is an additive contribution of pocket operations to living team mass; it is not a causal score estimate or the final king's mass. `teamDelta` is also saved but includes all other concurrent team actions. Do not sum overlapping whole-team deltas.

`tables.json` includes all pockets, fountain-bearing pockets, physical protocols, harvest families, entry-length/phase/mouth-staff strata, online/local families, and game-length strata. Category `N` is the eligible team-game denominator; `nEpisodeGames` counts games contributing at least one episode. `headRounds` is the round-start head occupation sum; `duration` includes the entry round; both differ from acting turns. Class labels are descriptive, and relay flags overlap the main protocols.

`occupancy.js` adds unique `(game,team,pocket,roundStart)` denominators. These count simultaneous heads only once. Every physical episode's reconstructed interval is checked against its `headRounds`; there are zero mismatches over 10,149 games. Protocol-specific unions overlap when multiple classes occupy one pocket and should not be summed.

`verify.js` shares the validated decoder but uses unchanged `tools/mass_ledger.js` for step simulation, and `exp/spatial/recount.js` for independently constructed geometry/iterative 2-core. It compares every game, not a sample. `verification-initial.json` preserves the first audit: 790 games differed only because its initial sprint attribution counted moves before entry/after exit. `fix_verify.js` reran these games with per-step pocket-boundary costs; the final verification reports the independent and primary map totals.

The current `verify.js` already contains the corrected attribution; `fix_verify.js` is a historical repair of that first audit, not required for a fresh run. `verify_fountains.js` independently recomputes the fountain-component subset (5,929 games, zero differences). `blocking.js` measures own fountain tile/body occupation before the spawn tick; `verify_blocking.js` checks it independently (1,829 games, zero differences). Occupation is not the hidden countdown's actual failed spawn attempts. `finish_tables.js` attaches audit results, body occupation, and deep selection to the main tables. `check.js` checks conservation, class partitions, histograms, deep sample sizes, report column alignment, and links.

Finalization and relay refinement are idempotent rewrites of the cache. Extraction and the first full recount resume by game key; do not mix a newly expanded population with the frozen study. Initial/final v1 cohorts are named separately. All stage logs are retained. Board rendering used `~/.aside/runtime/bin/python3`, which has Pillow, because the default Python did not.

Resource checks pause at free memory <10% or disk free <20 GiB. Extraction and verification each use two workers; other substantial stages run sequentially or alongside one serial verification repair. `SUMMARY.txt` is generated only after the report and final checks.
