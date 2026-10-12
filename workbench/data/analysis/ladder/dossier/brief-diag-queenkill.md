# Their queen outlives ours. How do queens get killed, and why do we not kill theirs

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule. The winner of a game is the side
with the longer queen (the dragon with starting id 0 or 1; a dead queen counts 0), then the longest dragon, then
total length; a side with no dragon left is eliminated.

## Data
- Fresh online games of the current team main: labels `agg7-m1` (30 games this morning, 7 wins), `sr51-bob1` (15,
  last night) and, as they arrive today, `agg7-m2`, `agg7-m3`: `data/online/smoke/<label>-new/M*.replay` with
  `game-*.json`. Labels `agg7-b*` are another build: use them only as a second sample, reported apart.
  Per-game counts already made: `data/analysis/ladder/dossier/online/agg7.md`, `online/agg7-games.json`, tool
  `online/agg7_report.py` (shows how to read these replays).
- Our 500 main ladder games (`data/analysis/ladder/dossier/per-game.jsonl`, replays `data/online/ladder/`; older
  builds of our bot) and the rank-1 team's 597 games (`dossier/target/per-game-top1.jsonl`, replays
  `data/online/top1/`, team id 306). Shared reader `tools/ladder_replay.py`; scan scripts in `dossier/work/`.
- The bot: `data/online/smoke/sr51-bot/main.cpp` (= team main a358ec8). Earlier diagnoses in `dossier/diag-*.md`
  (read `diag-attack.md`, `diag-feeding.md`, `diag-sacrifice.md` and `queen-path.md` before you start).

## What the online games show
12 of this morning'"'"'s 30 games were decided on queen length and our queen was alive at the end in 5; so in most of
those the opponent'"'"'s queen lived and ours did not. Our queen dies to a short dragon that walks 2 steps into her head.

## Your job
1. Count, for us and for our opponents in the online games, and for us, rank-1 and their opponents on the
   ladder: the enemy queen'"'"'s fate (alive at the end; dead by round 100 / 300 / later; cause: rammed by whom,
   wall, own body, illegal split, other), and who killed her (length of the killer, steps it walked, length paid,
   was the killer lost too). How often does each side kill the other queen first, and how often does that side
   then win.
2. Chances. A chance = an enemy queen'"'"'s head within reach of one of our heads on our turn (free steps, and free
   plus 1 or 2 paid). Count chances, how many we took, and what we did instead; the same for rank-1 against its
   opponents and for our opponents against our queen. Can our dragon tell that a head is the queen (id 0 or 1:
   check what the bot knows, main.cpp) and does any score term treat her differently (QUEEN_HUNT and the
   QUEEN_HUNT_* constants, hunt and trade rules)?
3. What a kill is worth: games won when we killed their queen while ours lived, and the length the killer cost.
4. Tie our refusals to main.cpp lines. Decide: ONE default-off switch (generic, one build round) that makes a
   short dragon of ours take a sure hit on the enemy queen, with the reach rule stated exactly, the mechanism
   check a replay can show, and the count of chances in the data it would have taken. If chances are too rare to
   matter, say "no card" with the counts.

## Hard limits
Read-only on everything existing. No server calls, no posts, no games, no compiling. Write only the report named
below (110 lines or fewer) and scratch scripts under `data/analysis/ladder/dossier/work/` with your prefix. Label
every statement measured (script), read from code (file:line) or estimate. Heavy scans with `nice -n 10`, at
most 3 processes at a time.

## Output: `data/analysis/ladder/dossier/diag-queenkill.md` (scratch prefix `qk_`)
1. Three lines: how queens die on both sides, the change in one sentence (or "no card"), how sure. 2. The fate
and killer tables. 3. The chance table and "Why, in the code". 4. "The card" (`title:`, `slug:`, `### Claim`,
`### Evidence`, `### Expected signal`, `### What would show it'"'"'s wrong`) with the diff against
sr51-bot/main.cpp. 5. "Against it".
