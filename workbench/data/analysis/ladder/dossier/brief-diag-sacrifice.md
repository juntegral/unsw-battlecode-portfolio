# Their dragons die on purpose from the first rounds and ours never do. What is it for, and should we?

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured, `dossier/fingerprint.md`, 500 main ladder games)
- Deaths by "no action" (a dragon gives no move and no split, and dies) per 1,000 dragon turns in rounds 0-100:
  theirs 2.98, ours 0.00; theirs is the higher one on 18 of 19 layouts. Against opponents rated 2100 and above:
  theirs 5.48. Rounds 101-300: theirs 3.27 (2100+: 7.98), ours 1.15.
- Head-on meetings with a team mate per 1,000 dragon turns: theirs 0.37, ours 0.11 (15 of 19 layouts).
- Deaths by illegal split: theirs 0.95 and 0.70 per 1,000 turns, ours 0, but only against opponents under 1900.
- Context: their queen is longer than ours at round 100 and 200 on the layouts we lose; 51 of our losses are on
  the queen rule with only their queen alive (`losses/plan.md`). Our own bot feeds only late
  (`dossier/diag-feeding.md`: no feeder dies before round 201).
The game is decided at round 500 by the longer queen (a dead queen counts 0), then the longest dragon, then total
length. A dead dragon drops a pearl for every second segment.

## Already counted (read first)
`dossier/summary.md`, `per-game.jsonl` (schema in `count_dossier.py`), `fingerprint.md` and `fingerprint.json`,
`findings.md`, `dossier/diag-feeding.md`, and the top-team study in `data/analysis/top1/` if it is there.
Replays under `data/online/`. Bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`
(pick_feed_target, is_feeder, feeding_phase, FEED_EARLY_ROUND and FEED_EARLY_MAX, which are off, harvestable,
escape_child_size).

## Your job
1. For every "no action" death and every same-team head-on of theirs in rounds 0-300, over all 500 games: the
   round, the dragon's length, where it was (in a dead end or small room, beside a team mate, in the open), the
   nearest team mate and its length and whether it is their queen or their longest, who ate the dropped pearls
   and within how many rounds, and whether an enemy head of ours was near. Sort them into the few kinds they
   are (for example: the rest of a dragon left in a dead end after a split; a short dragon fed to the queen; a
   short dragon fed to the longest; a trapped dragon with no move; a crash of the bot).
2. Which kinds do the teams rated 2100 and above use, and how early? What does each kind buy them by round 100,
   200 and 300 in the terms the game is decided on (queen length, longest dragon, dragons alive, total length)?
   Compare, inside the same layouts, the games in which they do it much against the games in which they do it
   little, and against what we have at the same rounds.
3. Read what our bot does in the same situations and why it never does this before round 201 (lines).
4. Decide with confidence: ONE default-off switch that fits a single build round, with a mechanism check a
   replay can show (their rate is the mark), or "no card". Our rule for adopting anything of theirs: the swarm
   comes first while the board is not full, a dragon eats what it safely can, and we do not make dragons timid.
   If the kind that pays is "feed the queen early", say so plainly and say what it costs the swarm.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-sacrifice.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `sc_`). Label every statement measured (script), read from code
(file:line) or estimate.

## Output: `diag-sacrifice.md`
1. Three lines: what their deliberate deaths are for, the change in one sentence (or "no card"), how sure.
2. The table of kinds (job 1) and what each buys (job 2). 3. "Why, in the code". 4. "The card": `title:`, `slug:`,
   `### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's wrong`. 5. "Against it".
