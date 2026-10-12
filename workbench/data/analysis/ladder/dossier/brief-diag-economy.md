# Rank-1's short dragons eat 43% more pearls per turn than ours. Account for every part of that gap

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured, `dossier/diag-split.md`): rank-1 eats 84.1 pearls per 1,000 dragon turns and we 58.8, and
the whole gap sits in dragons 2 and 3 long. Everything else found tonight is a piece of this one number.

## Pieces already traced to a code line (read them; quantify each, do not rediscover)
- `diag-spawn.md`: we step onto a tile that is about to spawn and stop the pearl (card SPAWN_CLEAR; built: locally
  it gave +12% natural pearls eaten).
- `diag-drops.md`: after the leader round a short dragon leaves the pearl beside its head when a longer mate is
  within 9 tiles (card ZONE_NEARER).
- `diag-islands.md`: above 1200 cells the leader rules start at round 151 and eating halves when we hold fewer
  than 56 dragons (card LEADER_FULL_UNITS).
- `diag-stripes.md`: pearls in small rooms behind portals (cards POCKET_LOOP and HARVEST_PORTAL).
- `diag-walk.md`, `sweep.md`: re-treading with nothing in view; judged not worth pearls.
- `diag-opening.md`: closed starts; `diag-attack.md`: who eats the drops of a head-on.
Also `dossier/target/scoreboard.md`, `fingerprint.md`, `per-game.jsonl`, `target/per-game-top1.jsonl`
(replays `data/online/ladder/` and `data/online/top1/`, rank-1 is team 306), shared reader `tools/ladder_replay.py`,
scan scripts in `dossier/work/`. Bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`.

## Your job
1. A full account. For dragons of length 2 and 3 on the 19 shared layouts (each layout weighted equally), rounds
   0-300: split every dragon turn into exclusive situations and give, for us and for rank-1, the share of turns
   in each and the pearls eaten per turn in each. Suggested situations, refine as the data asks: a pearl on a
   neighbouring tile; a pearl 2 to 3 steps away; a pearl in view farther off; no pearl in view but a tile in view
   that spawns within 3 rounds; nothing in view; an enemy head within 3 steps; boxed in or in a dead end; just
   split (first 3 turns of life); in the last 3 turns before death. Then decompose the 25.3 gap into "we are in
   the situation less often" and "we eat less in the same situation", per situation. The parts must sum to the gap.
2. For each part, say which of the traced pieces above explains it and how much of it (an estimate with its
   basis), and what is left unexplained.
3. For the two largest unexplained parts: open replays of both teams, find what our dragon does differently in
   that situation, count it over all games, and tie it to main.cpp lines.
4. Decide: ONE default-off switch for the largest unexplained part that fits a single build round, with a
   mechanism check a replay can show (rank-1's rate is the mark). If the remainder is spread too thin for one
   switch, say "no card" and rank the three best leads with their sizes.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-economy.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `ec_`). Label every statement measured (script), read from code
(file:line) or estimate. Run heavy scans with `nice -n 10`.

## Output: `diag-economy.md`
1. Three lines: where the 25 pearls per 1,000 turns go, the change in one sentence (or "no card"), how sure.
2. The account table (situations; share of turns ours / rank-1; pearls per turn ours / rank-1; contribution to the
   gap from frequency and from rate; which traced piece covers it). 3. The two unexplained parts, with counts and
   "Why, in the code". 4. "The card" (`title:`, `slug:`, `### Claim`, `### Evidence`, `### Expected signal`,
   `### What would show it's wrong`) or "No card" with the ranked leads. 5. "Against it".
