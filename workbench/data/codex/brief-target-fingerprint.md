# The target: the same behaviour fingerprint for the rank-1 team, next to ours

`data/analysis/ladder/dossier/fingerprint.md` and `fingerprint.json` (yours, built by the scripts `work/fp_*.py`
from `dossier/per-game.jsonl`) hold 109 behaviour rates for our bot and for its opponents in 500 of our ladder
games. Now measure the same rates for the strongest team, from its own games.

Input: `data/online/top1/` holds about 1,870 replays of the rank-1 team's games (against other teams; see
`data/analysis/top1/a_head.md` and the scripts there for how sides and the team are identified, and
`data/online/requests.jsonl` / `source-hashes.json` if useful). The per-game counter is `dossier/count_dossier.py`
(same replay format); run its counting on these replays for the rank-1 team's side and for its opponent's side,
writing rows to `data/analysis/ladder/dossier/target/per-game-top1.jsonl`. Reuse your `fp_*.py` rate definitions
unchanged.

## Output: `data/analysis/ladder/dossier/target/scoreboard.md` (90 lines or fewer), English
1. Which games went in: how many replays, layouts and their game counts, the rank-1 team's record, date range,
   and how many of its opponents are rated 2100 and above if that can be told.
2. The scoreboard, one line per behaviour rate and window (same 30 lines as the ranked table in fingerprint.md,
   then any other rate where rank-1 differs from us by a quarter or more): ours (our 500 ladder games), rank-1
   (its own games), the opponents of rank-1 in those games, and our ladder opponents rated 2100+ (from
   fingerprint.json). To keep layouts from deciding it, also give "ours" and "rank-1" restricted to the layouts
   both have played, each layout weighted equally, and the number of shared layouts on which rank-1 is the higher.
   Mark each line: gap = (rank-1 minus ours) over the larger of the two, on the shared layouts.
3. "Where we differ most from rank-1", the 12 largest consistent gaps in plain words (what a dragon of theirs does
   more or less often than ours), each with the fields it comes from; and "Where we already match" (gap under a
   tenth), as a short list.
Also `target/scoreboard.json` with every number, and keep the scripts under `dossier/work/` (prefix `tg_`) so the
scoreboard can be re-run later with one command on new games (say the command at the end of scoreboard.md).
Counts and rates only; no advice. Last step: `data/analysis/ladder/dossier/target/done.txt`.
Write only under `data/analysis/ladder/dossier/target/` and `dossier/work/tg_*`. No network, no posts, no games.
