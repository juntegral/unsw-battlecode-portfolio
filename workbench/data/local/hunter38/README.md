# hunter38: card #38 queen-loop against a queen-hunting spar

QWQ's condition for card #38: test `QUEEN_LOOP` not only against main but against a spar that hunts queens
(main with `QUEEN_HUNT=true`, `QUEEN_CHASE_DIST=8`). The card loop's own A/B plays main only, so this runs beside it.

## The test
- Two arms against the same hunter, paired by map, seed and side: switch off (`base`) and switch on (`candidate`).
- 17 maps x 4 games per arm = 68 pairs, 136 games. `SEED0=3000`: seeds 3000 and 3001, both starting sides.
- Maps (QWQ's list in `work/qm_small.sh`, branch `origin/claude/sweet-pasteur-shawil`): default, trauma,
  queen_of_spades, schooltime, portals_v0, slithery_fight_v0, autarky_v0, devil_v0, prisoners_dilemma_v0, trophy
  (the old 10), around_unsw, australia, islands, maze, stripes, tower_defense, weakhold (7 new).
- Engine unswbc 1.2.7 (`battlecode/work/bc127`), `NOSANDBOX=1`, `WORKERS=6`, `KEEP=1`, `nice -n 10`: the card loop's
  mechanism-step settings, through the same `ab3.py`.

## What is what
| path | what |
|---|---|
| `run_hunter38.py` | the whole run: wait for the loop, games map by map, check, `result.md` |
| `bots/off` | switch off: main `0e03867` `mybot2` as it is |
| `bots/on` | switch on: copy of the loop's `~/meow-loop-out/card-38/attempt-1/on-src` = main `0e03867` + card commit `c1c2c29` with `QUEEN_LOOP = true` |
| `bots/hunter` | the spar: main `0e03867` `mybot2` with two constants changed |
| `bots/hunter.diff` | `diff -ru off hunter`: exactly `QUEEN_CHASE_DIST 0 -> 8` and `QUEEN_HUNT false -> true` |
| `compile/` | `c++ -std=c++20 -O2` compile check of the three bots (logs empty = clean) |
| `harness/` | `work/ab2.py`, `work/ab3.py`, `replay.py` from main `0e03867`; `work/card_38_check.py` from `c1c2c29`; the 17 map files copied from the team repo; `base`, `candidate`, `hunter` link to `bots/`; `work/ab2` links to `replays/` |
| `SHA256SUMS` | hashes of the bots, tools and maps as prepared |
| `rows/<map>.json`, `.log` | game rows and ab3 output per map |
| `replays/` | `base_<map>_<seed>_<side>.replay`, `candidate_...` (our bot is side 0 = team A, side 1 = team B) |
| `hunt.json` | all 136 game rows |
| `check.json`, `check.log` | output of `card_38_check.py` on the replays |
| `result.md` | wins per arm, paired flips, queen numbers |
| `run.log` | progress; last line is `DONE` when everything finished, `FAILED: ...` or `GAVE UP ...` otherwise |
| `run.pid`, `nohup.out` | pid of the run, anything it printed |

## Waiting for the card loop
The script reads `~/meow-loop-out/status.json` every 60 s. It starts only when `batch_running` is false and card 38's
`step_kind` is not `outcome` (gives up after 3 hours), and checks the same thing before every map and before the
check (gives up after 6 hours in one wait). It never touches the loop's files.

## Commands
Start or resume (finished maps are skipped):

    cd "~/01. Project/개인 프로젝트/unsw-swarm/data/local/hunter38" && nohup /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 run_hunter38.py > nohup.out 2>&1 &

Progress: `tail run.log`. Stop: `kill $(cat run.pid)` (then `pkill -f hunter38/harness` for games in flight).

Re-run the check alone (the copy taken at `c1c2c29`):

    cd "~/01. Project/개인 프로젝트/unsw-swarm/data/local/hunter38" && python3 harness/work/card_38_check.py --replays replays --base base --candidate candidate --output check.json

The same with the card tree's current script, without writing into the tree:

    PYTHONDONTWRITEBYTECODE=1 python3 ~/meow-cards/card-38/work/card_38_check.py --replays "~/01. Project/개인 프로젝트/unsw-swarm/data/local/hunter38/replays" --base base --candidate candidate --output "~/01. Project/개인 프로젝트/unsw-swarm/data/local/hunter38/check.json"

## Differences from QWQ's setup
- His base and hunter were built from main `fa61861`; here both are main `0e03867` (so #39 queen safety and later
  merges are in both arms and in the hunter). His 36 of 68 for base against the hunter is a neighbour, not a repeat.
- His candidates were built from his own branch; here the candidate is the card loop's build of card #38.
- `ab3.py` is called once per map, not once for all maps, so the run can step aside for the loop between maps. Seeds
  and sides per map are the same as in one call.
- The opponent is `harness/hunter` (prepared once), not `tune_runs/ab2/HQ` built by `ab2.build`; the two constants are
  set with the same substitution.
- The check's pass rule was fixed for games against main. Against the hunter its verdict is for reference; the
  queen counts (alive, rammed, death round, loop share, lap steps under a close head) are the point.
