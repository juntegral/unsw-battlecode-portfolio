# Astra analyst: lossmap5

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `lossmap5`.

Question: where does one5 lose now? The earlier loss map (one1 to one3, 96 games, 72 losses; `data/analysis/ladder/dossier/diag-one1.md`,
grep "loss map") had four buckets: decided by dragon count before r150 (41, of which wiped out 26, small maps 33), longest dragon
(16), queen only (7), other (7). one5 changed the opening (level with WHQ at r100). Rebuild the same buckets, same definitions,
for one5 only: `one5-w1` (3 wins of 15) and `one5-c1` (against Cache me outside, 6 of 15), 30 games, 21 losses; `one5-d1` as a
separate column.
1. The bucket table, and for every loss one line: map, cells, how it was decided, the round at which the game was lost for good
   (the last round at which we were level or ahead on the measure that decided it), and what happened in the 30 rounds before it
   (dragons and total length both sides every 10 rounds, the largest single loss: who died, how).
2. The six wins against Cache me outside and the nine losses on the same footing: what is different by r100, r200, r300?
3. Which single bucket is now the largest, and is there one behaviour of ours that appears in most of its games? Name it with
   replay moments. A card only if that behaviour is a rule you can point to in `one5-bot/main.cpp`.
