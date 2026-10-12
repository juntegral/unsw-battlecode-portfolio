# Codex brief: how do elite teams harvest dead-end pocket fountains?

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. It is the new lineage of our UNSW Battlecode 2026 bot (deep-sea dragon game; team 583; the score is the longest single dragon alive at round 500).

Read first:
- `CLAUDE.md`, `research/KNOWLEDGE.md`
- the rules in `rules/ALL.md`, especially movement, self-collision, splitting and death
- `research/observations/spatial-occupancy.md` and `exp/spatial/` (your previous study)
- `exp/spatial-all/tables.json`, the same pipeline extended to all ten maps

`legacy/` = `../unsw-heuristic`, and `data/` and `.cache/` link to its data.

## Why
**Pocket tiles** are tiles outside the 2-core of the passable graph (dead-end corridors). Moving into your own body, tail included, kills (rules). So a dragon that reaches the end of a 1-wide dead end cannot turn around. It can still split: the child is the rear segments in reverse order, and it leaves head first from the old tail.

| Map | Pocket pearls per game | Elite share eaten | Our share | Notes |
|---|---|---|---|---|
| Slithery Fight a (N = 881 top games) | about 428 | winners 49.5%, losers 47.1% | about 5% (W0–W12) | Pocket deaths are about 0.77 per pocket pearl for winners. Opponents eat about 90% of these pearls in our games. v1 now excludes pocket tiles from all targets (0% of sd turns). |
| PD6 (N = 810) | – | winners 68.9%, losers 27.7% (about 81 per game) | stack families 224–250 per game | All 12 fountains are pockets. Our deaths in pockets roughly equal our pocket pearls eaten (about 1 death per pearl); winners about 0.59. |
| PD10 | – | – | exactly 169.0 per game in almost every family | Check whether that constant is real. |

## Questions (per map/layout with pocket fountains: Slithery Fight a/b, PD6, PD10, Schooltime a/b if any, Trauma, QoS)
1. **Entry episodes.** For every episode where a dragon's head enters a pocket (elite winners, elite losers, ours W0–W12, v1 local), record:
   - dragon length at entry, round, the pocket's depth/shape and fountain;
   - the team's other heads near the mouth;
   - pearls eaten inside, split(s) inside (child length, whether the child exits);
   - how it ends: exits alive / dies inside (cause) / is still inside at game end;
   - net team mass change over the episode, counting drops and who later eats them.
2. **Classes.** Group the episodes into harvest protocols. For example: suicide runner (enter, eat, die); split-escape (enter, eat, split, the child leaves with the mass); relay (a queue of pieces at the mouth); long dragon (does not enter). Give counts, rates and net mass per episode and per round of pocket occupation, for winners, losers and ours.
3. **Which protocol wins.** Report net mass per pocket pearl and per death. Include timing (phase), the length at entry that works best, and how many heads the elite station at a mouth.
4. **Our failure.** Why v0/stack11 dragons park at pocket mouths without entering on Slithery a. The earlier finding was the sd target inside the pocket plus a safety veto. Why PD harvesting costs us about one death per pearl.
5. **Recommendation.** A concrete harvest protocol per map/layout for the bot: when to enter, at what length, when and how to split, the relay order, and the expected net mass per game. Also say when to ignore pockets.

## Deliverables
- `exp/pocket/episodes.jsonl` (or a compact cache) and `exp/pocket/tables.json`, written first.
- `research/observations/pocket-harvest.md` (Korean): [사실] / [해석], N everywhere, the three-stage method (full-population scripts → classes with sizes → deep reads with game ids and rounds, including 2–3 board pictures), and the final protocol table.
- `exp/pocket/SUMMARY.txt`, written last (15 lines).

## Rules
- **Write scope:** only `exp/pocket/**` and `research/observations/pocket-harvest.md`. Do not write in `bot/`, `versions/`, `eval/`, `exp/v1/`, `exp/v11/`, `exp/portals/`, `exp/spatial*/`, `legacy/`, `data/` or `.cache/`. Do not commit; the coordinator commits.
- **Reuse code:** you may reuse code from `exp/spatial/` and `tools/mass_ledger.js` (its `turn` hook fires at turnStart, before the move), and the fast decoder `legacy/exp/intake-gap/rawload.js`.
- **No network, no uploads.** Do not read `unsw-arena-clean-control/operator-only/` or opponent bot sources.
- **Resources:** at most 2 worker processes. Two agents run local games; pause if free memory falls under 10% or disk free under 20 GB.
- **Verification:** recount the key per-map numbers with an independent script and report both.
- **Target:** tables by 06:45 KST, everything by 07:45 KST. If you must stop early, leave the tables and a partial report that says what is missing.
