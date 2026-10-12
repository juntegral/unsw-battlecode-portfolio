# How long is our longest dragon when it is rammed? A count for card 54's length threshold

Card 54 protects our dragons of 31 or longer from rams. Count whether 31 is where the rams are.
Data: today's online games of current main (`data/online/smoke/agg7-m1-new/`, `sr51-bob1-new/`, and any
`agg7-m2-new/`, `agg7-m3-new/` present; tool `data/analysis/ladder/dossier/online/agg7_report.py` shows how to
read them), our 500 main ladder games (`data/analysis/ladder/dossier/per-game.jsonl`, replays
`data/online/ladder/`, reader `tools/ladder_replay.py`), and the rank-1 team's 597 (`dossier/target/per-game-top1.jsonl`,
`data/online/top1/`, team 306) for comparison. "Rammed" = an enemy head moves into our dragon's head and ours dies.

Count, for the online set and the ladder set apart (and rank-1's own dragons):
1. Every ram on a dragon of ours that was our longest or within 2 of our longest at that moment: its length then
   (bands 2-5, 6-10, 11-15, 16-20, 21-30, 31-50, 51+), the round band (0-100, 101-300, 301-500), the rammer's
   length, steps walked and length paid, and whether our longest after the ram was shorter than the opponent's
   longest at the end of the game (the ram could have decided the game).
2. Length lost to such rams per game by the same bands, and the share of all length we lose to rams that a rule
   for dragons of at least N would cover, for N = 6, 11, 16, 21, 31.
3. Turns: the number of our dragon turns at length at least N for the same N (the price side: how many turns the
   rule would touch), and how many of those turns have an enemy head within 3 steps.
4. Our longest dragon's length at rounds 100, 200, 300, 400, 500 (mean and quartiles), online and ladder, and
   rank-1's.
Output: `data/analysis/ladder/dossier/leader-len.md` (45 lines or fewer, English): the tables and at most five
plain sentences (counts only). Scratch under `dossier/work/` (prefix `ll_`). Last step:
`data/analysis/ladder/dossier/leader-len-done.txt`. Write only those paths. No network, no posts, no games.
`nice -n 10`, at most 3 processes.
