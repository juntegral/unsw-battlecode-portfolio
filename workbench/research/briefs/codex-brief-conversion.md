# Codex brief: how elite winners turn swarm mass into one king (r250–500) on 500-round maps

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. This is the new lineage of our UNSW Battlecode 2026 bot (the deep-sea dragon game; team 583; the score is the longest single dragon alive at round 500).

Read these first:
- `CLAUDE.md` and `research/KNOWLEDGE.md`.
- The rules in `rules/ALL.md`: movement, splitting, death drops (a dead dragon drops about half its length as pearls), sacrifice, and multi-moves.
- `research/observations/map-atlas.md`. On 500-round maps, winners and losers have the same head counts; conversion into the king line after r250 decides the game.
- The earlier studies in `legacy/research/observations/`: `endgame-king.md`, `conversion-chain.md`, `supply-chain.md`.
- Your earlier studies in `research/observations/`: `spatial-occupancy.md` and `pocket-harvest.md`.

`legacy/` = `../unsw-heuristic`. `data/` and `.cache/` link to its data.

## Why
Our v1 (online, top-7 waves) and v1.2/v1.3 raise heads and intake on the 500-round swarm maps. The link that never moves is conversion. For v1 online vs stack11:
- The line share of our sacrifice drops from r300 is 22% vs 22%.
- Line sacrifice pearls r300–499 are 6.8 vs 5.5, against about 25 for the elite.
- Our final king on Slithery is 25.8 vs the opponent's 58.7 (v1, 18 games).

## Question
Answer per map/layout for Slithery Fight a/b, Schooltime a, Trauma, and Autarky as a fortress comparison.

1. **Sacrifice geometry.** For elite winners vs elite losers vs ours (W0–W12, `v1-w1..3`, `v12-w*` as they arrive), for every sacrifice from r250:
   - who sacrifices (length, distance to the eventual final king, and whether it is on the final king's lineage);
   - where the drops land relative to the king's head (path distance) and how many turns the king takes to eat them;
   - what fraction of the drops the final king eats, other allies eat, and the enemy eats.
2. **Feeding topology.** Does the elite feed:
   - directly (a piece dies next to the king's path);
   - through relays (piece → mid-size → king);
   - by the king touring a field of drops?
   Measure the king's path in r300–500: tiles per drop eaten, and whether it waits.
3. **Timing.** Sacrifice rate by round (the step at r250 the atlas found), and which pieces go first (small, far, near).
4. **King growth curve.** King length at r250/300/350/400/450/500 for winners vs losers vs ours. Where our growth stalls, and why: no feeders near, drops eaten by the enemy, the king dying, or the king never becoming the recipient.
5. **Protocol.** Give a concrete, implementable conversion protocol per map for the bot:
   - who feeds whom, when, and where to die relative to the king's head;
   - how the king moves;
   - how to avoid enemy theft of the drops;
   - expected line pearls per game.
   Say what the elite do that our k8 rule (feed only allies ≥ max(own+4, 8)) and our clock (r250 SE maps) miss.

## Deliverables
- `exp/conversion/tables.json`, written first.
- `research/observations/conversion-protocol.md` (Korean):
  - [사실] / [해석] kept apart, with N everywhere;
  - the three-stage method: full-population scripts → classes with sizes → deep reads with game ids and rounds, including 2–3 board pictures of an elite endgame feed;
  - the per-map protocol table at the end.
- `exp/conversion/SUMMARY.txt`, written last (15 lines).

## Rules
- **Write scope:** only `exp/conversion/**` and `research/observations/conversion-protocol.md`. Do not write in `bot/`, `versions/`, `eval/`, other `exp/*`, `legacy/`, `data/` or `.cache/`. Do not commit; the coordinator commits.
- **Code:** reuse code from `exp/spatial/`, `exp/pocket/`, `tools/mass_ledger.js` (its `turn` hook fires at turnStart, before the move) and `legacy/exp/endgame-king/extract.js`. Use the fast decoder `legacy/exp/intake-gap/rawload.js`.
- **Population:** all top-vs-top games for these maps in `data/top/index.jsonl`, with stalled games excluded as before, plus all our sets. No sampling.
- **No network, no uploads.** Do not read `unsw-arena-clean-control/operator-only/` or opponent bot sources.
- **Resources:** at most 2 worker processes. Another Codex study and an agent with local games are running. Pause if free memory drops below 10% or free disk below 21 GB. Keep large caches compressed and remove uncompressed duplicates.
- **Verification:** recount the key per-map numbers (line share, king curve) with an independent script and report both.
- **Target:** tables by 09:30 KST, everything by 10:30 KST. If you have to stop early, leave the tables and a partial report that says what is missing.
