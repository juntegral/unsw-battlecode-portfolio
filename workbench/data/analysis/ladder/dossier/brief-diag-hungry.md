# Our short dragons go hungry twice as long as rank-1's. Find the line by tracing our own bot's scores

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured, `data/analysis/ladder/dossier/diag-economy.md` part 3b; read the whole file first)
37.4% of our short-dragon turns (length 2 and 3, rounds 0-300) are by a dragon that has not eaten for 26 rounds
or more, 25.1% of rank-1's; such dragons have no pearl in view on 57 to 59% of turns against 48 to 50%. The
analyst saw ours circle a patch of 4 by 3 tiles with a pearl in view on 15 of 18 turns and two or three team
mates in view, and could not tie it to one line from replays alone. Estimated worth: 2.7 pearls per 1,000 turns.

## What is new for you: you can make our bot say why
The local bench is `~/meow-redteam/` (`./play.sh <botA dir> <botB dir> <map> <seed> <out dir>`, two game slots,
it queues by itself; opponent bot dir `bot`). Our current best local build is `~/meow-redteam/solo/bots/m3b7/`
(main.cpp = team main a358ec8 plus seven switches on; headers beside it). Maps: `maps/dev`, `maps/eval`
(held-out, generated) and `maps/ladder/ladder_*_1.map`. Existing games of this build, both sides, two seeds:
`~/meow-redteam/solo/runs/m3b7/<map>-seed<S>-side<K>/game.replay` (128 games; reader `tools/ladder_replay.py`
in unsw-swarm, local counting examples in `data/analysis/ladder/dossier/local/`).
1. From those 128 replays find the spells: a dragon of length 2 or 3, rounds 0-300, 26 rounds or more without a
   meal. Count them and describe where the time goes: turns with a pearl in view not taken (how far, who is
   nearer, is it in a small room, is it in a leader zone), turns with nothing in view (does it walk straight or
   circle; tiles revisited), turns boxed in. Check that the picture matches the ladder one in 3b.
2. Make a tracing copy of the bot (`~/meow-redteam/solo/bots/tr_*/`, copy m3b7's files, compile with
   `c++ -std=c++20 -O2 main.cpp -o bot`): log, for a dragon that has not eaten for 26 rounds or more, each
   direction's score split into its terms (space, territory, cramped, pearl target, hot, unseen, far gain, zone,
   threat, whatever pick_direction and score_step add) and the chosen step. Find out how a bot can write a log
   under play.sh (stderr or a file); the log must not change play: check that a traced game's replay equals the
   untraced one on the same map, seed and side. Replay a dozen games that hold long spells (several map kinds
   and sizes) and read the logs at the spell turns.
3. Name the term or terms that hold the dragon where it is, with counts over the traced spells (for example:
   "the pearl a team mate reaches sooner is worth nothing but the tile beside it still scores", "territory
   shares to zero beside mates so every step scores the same and the tie goes to the first direction", "unseen
   weight 0.2 is below the noise of space"). Tie each to main.cpp lines.
4. Decide: ONE default-off switch that fits a single build round, generic (no map names, no per-map numbers),
   with a mechanism check a replay can show. Build it in a second copy (`bots/tr_fix*/`), play it on at least
   16 map-and-side pairs against the same seeds as m3b7's games, and report: spells of 26+ rounds per game,
   share of short-dragon turns inside such spells, pearls eaten by round 300, deaths by cause, wins. If nothing
   moves the spells, say "no card" and what the trace ruled out.

## Hard limits
Do not edit `~/meow-redteam/solo/src/`, any existing bot dir or run dir, or anything in the battlecode repo.
Write only: new dirs `~/meow-redteam/solo/bots/tr_*` and `~/meow-redteam/solo/runs/tr_*`, the report
`data/analysis/ladder/dossier/diag-hungry.md` (100 lines or fewer), scratch under
`data/analysis/ladder/dossier/work/` (prefix `hg_`). No server calls, no posts. Games only through play.sh (it
holds the two slots; other batches share them, so expect to wait). Other scans with `nice -n 10`, at most 4
processes at a time. Label every statement measured (script), read from code (file:line) or estimate.

## Output: `diag-hungry.md`
1. Three lines: what holds a hungry dragon in place, the change in one sentence (or "no card"), how sure.
2. The spell account (local, against the ladder numbers). 3. The trace: terms and counts, "Why, in the code".
4. "The card" (`title:`, `slug:`, `### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's
wrong`) with the exact diff of the switch against m3b7's main.cpp and the local result table, or "No card".
5. "Against it".
