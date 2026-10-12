# The queen now keeps 3 and is still rammed as often. What is left, on the new build's own games

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## Where we are
Read `data/analysis/ladder/dossier/diag-queenhit.md` first (this morning's diagnosis on current main: the queen was
2 long in 19 of 27 rams, the safety rule held as written, cards QS_KEEP_LEN and QS_AHEAD). QS_KEEP_LEN 3 is now
built and played online: label `agg8-q1` (30 games, 14 wins; replays `data/online/smoke/agg8-q1-new/`, bot
`data/online/smoke/agg8-bot/main.cpp`; a second label `agg8-q2` may arrive while you work, use it if present).
Measured (`dossier/online/agg7.md`, tool `online/agg7_report.py`, detail `online/agg7-games.json`): her turns at
length 2 fell from 41% to 9%, she is alive at the end in 8 of 30 games (11 of 60 before), but she still dies to a
head-on hit in 13 of 30 games (25 of 60 before): 8 of those at length 2, 3 at length 3, 2 at length 4. Wall
deaths 5, own body 1, head-on mover 3. Games decided on queen length: 3 won, 9 lost.
QS_AHEAD (look four turns ahead) was built locally and added nothing against a queen-hunting local opponent, so
do not propose it again. Your scripts from this morning are in `dossier/work/` (prefix `qh_`); reuse them.

## Your job
1. Every queen death in the new build's games (all causes), rebuilt as this morning: her length and how she came
   to it (if she is 2: was it the start of the game, a paid sprint, a split the new rule still allows, or a
   forced split), what she could see, the rings, whether a clean step or a paid escape existed, what closed the
   box (kelp on how many sides, enemy heads, team mates' bodies), own heads within 3 and 5 tiles, and the three
   turns before: where could she have gone instead.
2. Exclusive classes with counts, set beside this morning's table, so that what QS_KEEP_LEN removed and what it
   left is plain. Wall and own-body deaths too: were they boxed-in choices or mistakes with a free tile open?
3. The turns before the box closes. This morning: standing on a tile with kelp on two or more sides with an enemy
   head within 3 steps was hit 8 times in 38 turns, on open tiles 5 in 224. Count for the new build's games and
   for main's (labels `agg7-m1`, `agg7-m2`, `agg7-m3` if present): with an enemy head within 3, 4 and 5 steps,
   how often she steps to a tile with fewer open sides than the one she leaves when a tile with more was open and
   unringed, and what follows within 3 turns. Also what a team mate nearby changes: hit rate with 0, 1, 2+ own
   heads within 3 tiles, and whether a team mate's body on the rammer's path ever saves her.
4. Decide: up to TWO default-off switches, each one build round, generic, each tied to main.cpp lines, with the
   count of the deaths in the data it would have changed and its cost (turns it fires with no hit following).
   Candidates to test against the counts, not to assume: with an enemy head within N steps prefer the unringed
   tile with more open sides; do not let a paid sprint take her below 3 when a free alternative exists; keep 4
   instead of 3; a short team mate stays within 2 tiles of her (which existing guard constants do this, and what
   did they cost when they were on?). If nothing reaches a quarter of the remaining deaths, say "no card".

## Hard limits
Read-only on everything existing. No server calls, no posts, no games, no compiling. Write only
`data/analysis/ladder/dossier/diag-queenhit2.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `q2_`). Label every statement measured (script), read from code
(file:line) or estimate. `nice` is refused by the guard, so run scans plainly, at most 3 processes.

## Output: `diag-queenhit2.md`
1. Three lines: what still kills her, the change(s) in one or two sentences (or "no card"), how sure.
2. The class table beside this morning's. 3. The turns-before counts. 4. "The card(s)" (`title:`, `slug:`,
`### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's wrong`) with the diff against
agg8-bot/main.cpp. 5. "Against it".
