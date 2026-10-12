# Codex brief: opening book per map (how elite winners take space in r0–50)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`, the new lineage of our UNSW Battlecode 2026 bot (deep-sea dragon game; team 583; the score is the longest single dragon alive at round 500).

Read first:
- `CLAUDE.md`, `research/KNOWLEDGE.md`
- the rules in `rules/ALL.md`: movement, splitting (the child is the rear segments reversed and leaves head first from the old tail), turn order by id, and multi-moves
- your earlier studies: `research/observations/spatial-occupancy.md` and `pocket-harvest.md`, with their tables in `exp/spatial/`, `exp/spatial-all/tables.json` and `exp/pocket/`
- `research/observations/map-atlas.md`

`legacy/` = `../unsw-heuristic`, and `data/` and `.cache/` link to its data.

## Why
Our v1 bot (online waves 1–2 against the top 7) improved on 500-round maps. It is still eliminated in 77% of games on the elimination maps: Default, Devil a/b, Queen Of Spades a/b, Trophy, Schooltime b.

The atlas and the spatial study agree that the r0–100 space race decides those maps. For example, on Devil a elite winners have 54% of their heads in the middle frontier bin (f in [.4, .6)) by r25 and 58% by r50, with 8.2 → 16.2 heads. Elite losers are at 24% → 17%, and our v1 at 7%. Our v1.1 dispersal changes did not move the heads, because the opponent already holds the middle at r25.

So we need the **opening**: the exact early sequence of splits and moves by which winners reach the middle first.

## Question (per map/layout: Devil a/b, Default, Trophy, Queen Of Spades a/b, Schooltime b, Trauma; also Slithery a/b and Schooltime a for comparison)
1. **Split schedule, r0–50.** For elite winners vs elite losers vs ours (W0–W12, v1 online waves `v1-w1`, `v1-w2` and later ones, plus local):
   - who splits, when, the parent length, the child length, and where the child's head is;
   - splits per round by round;
   - the order: whether the start king splits first, or the pieces.
2. **Head trajectories.** Where the heads are at r5, 10, 15, 20, 25, 35 and 50:
   - frontier bin and actual tiles, as heatmaps normalised to side A;
   - the path each early child takes to the middle (distance, turns, detours);
   - which dragons reach the middle first, and by what round.
3. **First contact.** When and where the first head-on or body contact with the enemy happens (round, f-bin, lengths), and who wins it: winners vs losers.
4. **Movement cost of splitting.** Does splitting early slow the space race (the child starts at the tail)? How do winners sequence split and move so the front reaches the middle by r25?
5. **Canonical opening.** Find the most common opening sequence among winners, and cluster the openings. Give it per map/layout and side as a small script the bot can follow for r0–50: split rounds and sizes, waypoints per child, and the target head count per frontier bin at r10/r25/r50. Say how much variation there is (the cluster sizes) and whether it depends on the opponent's opening.
6. **Ours vs theirs.** Where exactly our W12 and v1 openings fall behind: split timing, path choice, waiting, or retreat.

## Deliverables
- `exp/opening/tables.json`, written first (per map/layout: split schedules, trajectories, first-contact stats, opening clusters with N).
- `research/observations/opening-book.md`, in Korean:
  - separate [사실] and [해석], and give N everywhere;
  - the three-stage method: full-population scripts → clusters with sizes → deep reads with game ids and rounds, including 2–3 board pictures of r0/r10/r25 for a winner on Devil a and Trophy;
  - the per-map opening script table at the end.
- `exp/opening/SUMMARY.txt`, written last (15 lines).

## Rules
- **Write scope:** only `exp/opening/**` and `research/observations/opening-book.md`. Do not write in `bot/`, `versions/`, `eval/`, other `exp/*`, `legacy/`, `data/` or `.cache/`. Do not commit; the coordinator commits.
- **Code:** reuse code from `exp/spatial/`, `exp/pocket/` and `tools/mass_ledger.js`. Its `turn` hook fires at turnStart, before the move. Use the fast decoder `legacy/exp/intake-gap/rawload.js`.
- **Population:** all top-vs-top games for these maps in `data/top/index.jsonl`, excluding stalled games as before, plus all our sets. No sampling.
- **No network and no uploads.** Do not read `unsw-arena-clean-control/operator-only/` or opponent bot sources.
- **Resources:** at most 2 worker processes. Two agents run local games; pause if free memory is under 10% or disk free is under 21 GB. Keep large caches compressed and delete uncompressed duplicates.
- **Verification:** independently recount the key per-map numbers (split schedule and r25 middle share) and report both results.
- **Target:** tables by 08:00 KST, everything by 09:00 KST. If you must stop early, leave the tables and a partial report that says what is missing.
