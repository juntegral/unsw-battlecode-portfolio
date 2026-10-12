# Astra analyst: econ

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `econ`. The live bot is one7 (`data/online/smoke/one7-bot/main.cpp`,
submission 21086, since 02:31 KST). Read the first lines of `data/codex/astra/midgame/report.md`, `smallmap/report.md` and
`lossmap5/report.md`: the largest bucket of losses is still "behind on dragons by r150", and the mid-game gap is 60% fewer
dragon-turns and 40% fewer natural pearls per turn. Splits per pearl are the same on both sides (0.37 against 0.35), so the gap
is eating: heads standing where pearls are born. Nobody has yet said which of our own rules to change to eat more.

Question: which constants or score terms of ours decide how the swarm spreads over pearl-bearing ground in r0-150, and which
values would make it eat more? The lead will run every variant you name on 40 unseen maps and count pearls and heads at r100.
1. Measure the spread, ours against WHQ and Cache me outside (one5-w1, one5-c1, one7 sets as they arrive), every 10 rounds to
   r150: share of pearl-bearing tiles (every tile that bore a pearl in the game) whose nearest head is ours; mean distance from
   a bearing tile to our nearest head; heads per bearing tile in view; share of our heads with no bearing tile within 4 steps;
   share with a mate head within 2 steps (crowding). Say where they differ most and from which round.
2. Read the terms that move a dragon with no pearl beside it: territory (`WEIGHT_TERRITORY`, `UNSEEN_DISCOUNT`, `TERRITORY_DECAY`),
   the never-seen bonus, `target_bonus`/`CENTER_*`/`FAR_*`, crowd (`CROWD_MARGIN`), `SPAWN_CLEAR`, `ally_race_steps` sharing,
   `LOOK_DEPTH`, split thresholds (`SPLIT_MIN_LENGTH`, `grow_round`, `board_short`), heading tie, zone terms. For each say what it
   does to spread and whether the replays show it binding.
3. Name up to 12 variants, each a single constant or switch value that exists in the source (no new code), ranked by expected
   gain in natural pearls by r100 and r150, with the direction of the effect you expect and the count that would show it wrong.
   Give them as one line each in the form `NAME=CONST:value[,CONST:value]` so they can be pasted into the build tool.
   If the best lever needs new code, describe it as card 13 with the lines.
