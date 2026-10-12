# Brief: queen counts for two more runs against Big Bobs Bots

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/bbb-analysis-2/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Reuse `data/online/smoke/bbb-analysis/count.py` (read it and the "파일 수 및 정의" section of its `summary.md`; keep every definition). Run tables A, B, C and E for four variants side by side, all against team 946 on the same 15 maps, 6 Oct:
- "v31": `data/online/smoke/ie43-bob1-old/`, `data/online/smoke/ie43-bob2-old/` (30 games).
- "main" (v31 + #36 + #42 + #39): `data/online/smoke/main-bob1-new/` (15 games).
- "main, #36 off" (v31 + #42 + #39): `data/online/smoke/nd36-bob1-new/` (15 games). Code `data/online/smoke/nd36-bot/main.cpp`.
- "main + idle-exit": `data/online/smoke/ie43-bob1-new/`, `data/online/smoke/ie43-bob2-new/` (30 games).
Say how many games you found in each folder.

Because the variants have different game counts, give every count also per game or as a share. Add to table A, per variant: every queen death as a list (game id, map, round, cause, boxed in at her last turn yes/no, her length), and the queen's deaths by cause as counts (enemy head-on, boxed in, wall, own body, other; a death can be both boxed in and one of the causes, say how you count it).

Checks: print the raw events of one boxed-in queen death for "main" and one for "main, #36 off" and confirm by hand.

Output (write `summary.md` last): `data/online/smoke/bbb-analysis-2/count.py` and `summary.md`, pooled four-variant tables first.
