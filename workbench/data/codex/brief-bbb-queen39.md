# Brief: add a fifth variant to the Big Bobs Bots queen counts

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/bbb-analysis-3/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Follow `data/codex/brief-bbb-queen36.md` and reuse `data/online/smoke/bbb-analysis-2/count.py` (keep every definition and the same tables A, B, C, E, including the per-death list and the deaths-by-cause rows). Same four variants as there, plus a fifth:
- "main, #39 off" (v31 + #36 + #42): `data/online/smoke/ns39-bob1-new/` (15 games). Code `data/online/smoke/ns39-bot/main.cpp`.
Say how many games you found in each folder. Give every count also per game or as a share.

Add to table E for all five variants: the median and the mean of our final score and of their final score, and the same with the four maps Schooltime, Australia, Around UNSW and Islands left out.

Checks: print the raw events of one head-on queen death for "main, #39 off" and confirm by hand.

Output (write `summary.md` last): `data/online/smoke/bbb-analysis-3/count.py` and `summary.md`, pooled five-variant tables first.
