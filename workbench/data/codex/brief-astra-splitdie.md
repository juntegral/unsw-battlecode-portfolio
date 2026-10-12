# Astra analyst: splitdie

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `splitdie`.

Question: analyst `smallmap` (`data/codex/astra/smallmap/report.md`, `tables.md`, `collisions.csv`) counted our deaths in r0-150 on
maps of 1200 cells or fewer over 73 games: wall 779, rammed 355, own body 333, our own rams 129, mate body 128; and 722 deaths that
happen on the round of a split or the next one, with no free exit, not head-on. It did not count the same for the opponents, did
not say who dies (the child or the parent) and did not read the code. Earlier tonight relaxing the length-4 split check was tried
and dropped (children died 40-80%), so a check exists.
1. The same table for the opponents (WeHaveQuizzes, Cache me outside in `one5-c1`, dev test 1 as a second sample) in the same games:
   deaths by cause per 100 dragon turns, and deaths within one round of a split per split. Is ours higher, and by how much?
2. For our split-then-die cases: who dies (child or parent), its length, was the exit already closed when the split was made (the
   rule could have seen it) or closed after (by whom: mate, enemy, own body), was it a wait-split of the queen or a feeder
   (deliberate) or an ordinary growth split. Give the share of each.
3. Read the split decision in `data/online/smoke/one5-bot/main.cpp` and say which check lets the avoidable ones through.
4. A card only if the avoidable share is large: the rule, the lines, the count that shows it works, what it costs (splits delayed).
   Also say what the same deaths cost us in pearls (the body drops pearls; who eats them).
