# Why do strong teams ram a short enemy head with a long dragon?

A teammate noticed that some top teams deliberately move a long dragon into the head of a short enemy dragon, and
guesses it protects their queen or that a team mate nearby sweeps the pearls both bodies drop. Count it.

Data: `data/analysis/ladder/dossier/work/at_scan.py` already replays our 500 main ladder games and writes every
cross-team head-on with its context (see `data/analysis/ladder/dossier/diag-attack.md`, "Terms" and section 1, and
the `at_*.py` scripts and their output files in `dossier/work/`). Also the rank-1 team's own games: rows in
`data/analysis/ladder/dossier/target/per-game-top1.jsonl`, replays under `data/online/top1/` (team id 306); run the
same scan on those if at_scan can take them (it reads the same replay format), else say so and use ours only.

## Count, for head-ons where the mover is 5 or longer and the victim is shorter than half the mover
(and, as the comparison, movers of 2 to 4 on a head of the same length), split by who the mover belongs to:
our opponents rated 2100+, our other opponents, us, and rank-1 in its own games:
1. how many a game, by round band (0-100, 101-300, 301-499), and the mover's and victim's lengths (medians);
   was the mover its side's longest dragon; was it the queen.
2. where the mover's queen was: alive or not; steps from the victim's head to the mover's queen at the moment
   (within 3, 4 to 8, farther); had the victim moved towards the queen in its last two turns.
3. was the victim itself about to ram something: an own-side head (of the mover's side) of 8 or more parts, or
   the mover's queen, within the victim's sprint reach at that moment.
4. what happened to the pearls: dropped by both bodies, eaten within 15 rounds by the mover's side, by the
   victim's side; how many heads of the mover's side were within 3 tiles (the sweepers); net length for each
   side 15 rounds later.
5. did the mover have another move: a free tile beside its head (not boxed in); and could the victim have reached
   the mover's head on its next turn anyway (so the mover struck first).

## Output: `data/analysis/ladder/dossier/long-rams.md` (45 lines or fewer), English
The tables, then at most five plain sentences: which of the two guesses the counts support (protecting the queen;
a team mate sweeping the drops), or a third reading the counts point to (for example striking first, or being
boxed in), with the numbers. Counts only. Scratch under `dossier/work/` (prefix `lr_`). Last step:
`data/analysis/ladder/dossier/long-rams-done.txt`. Write only those paths. No network, no posts, no games.
