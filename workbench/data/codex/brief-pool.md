# Brief: a small sparring pool ("our own ladder") for team meow — preparation only

Work ONLY in the worktree ~/meow-dev (branch dev/pool, from battlecode main). Never touch the live checkout at "~/01. Project/개인 프로젝트/battlecode" or anything under work/loop/. Do not push. Commit on dev/pool when done.
Engine: `export PATH=~/meow-dev/work/bc127/bin:$PATH NOSANDBOX=1`.
Read first: work/ab2.py, work/ab3.py (paired batches; rows tag,map,seed,side,win,us,them,how), replay.py, mybot2/main.cpp (the toggles near the top, and how QUEEN_HUNT / QUEEN_CHASE_DIST / QUEEN_HUNT_MAX_LEN / HUNT_* / TRADE_* / STRIDE_* are used), work/plan.md (search "queen-hunting", "hunt", "QUEEN_HUNT" for earlier hunter variants and their settings).

## Why
Today a change (#27 "passage", switch TERRAIN_PASSAGE on branch origin/card/27) scored +15 net over 160 local pairs against our own bot, and then lost online: the live bot won 10/30, the passage build 5/30, against two higher-rated teams, same maps. The likely cause: the rule also applies to our queen (short early on), she leaves the home room and gets killed; a dead queen scores 0. Our local opponent (our own bot) never hunts the queen, so local tests could not see it. We need sparring partners with different styles.
Idea source: a Bradley–Terry "ladder of our own" over a pool of bots, and paired games per opponent. We want the SMALL version: no rating maths needed yet, just per-opponent paired results.

## Deliver
1. `work/pool.json`: 4–5 sparring bots, each = mybot2 at main + a toggle set (plus `v61` = the existing v61/ dir). Required styles:
   - `hunter`: actively hunts the enemy queen with small dragons (use the existing QUEEN_HUNT machinery; pick settings so it really goes for her; check plan.md for what worked);
   - `rammer`: short dragons take head-on trades readily (TRADE_* toggles; "kamikaze" style);
   - `v61`: the old release (dir v61/);
   - `nostride`: the live settings with STRIDE_BUDGET=0, STRIDE_CAP=0, STRIDE_MARGIN=0.0;
   - `live`: mybot2 as is (mirror).
   For hunter and rammer, VERIFY the style shows up: on ~8 games each, count enemy-queen kills / head-on deaths caused, vs `live` in the same seats. If a style doesn't show, adjust the toggles; note what you tried.
2. `work/pool.py`: `python3 pool.py BASE CAND [--maps a,b,…|--set held|new|quick] [--n 2] [--out FILE]`.
   - BASE/CAND are bot dirs or `mybot2:TOGGLE=VALUE,…` specs (same convention as ab3's `tag@src:toggles`).
   - Plays BASE and CAND each against every pool bot on the same (map, seed, side). Reuse ab2.play / ab3 logic; WORKERS from env, default 6.
   - Before running games it takes an exclusive flock on ~/.meow-card-loop-locks/batch.lock (blocking), so it never overlaps with the loop's batches. Print "waiting for the batch lock" while waiting.
   - Output: a per-opponent table: games, BASE wins, CAND wins, CAND-only (+), BASE-only (−), net, our final score (us) BASE→CAND, their score BASE→CAND, and games where our score is 0 (queen dead or wiped) BASE→CAND. Plus a total row, and a per-map-family breakdown.
     Markdown, with a 3-line plain summary on top (what we tried / did it work / who decides).
   - `--set quick`: about 6 maps including a walled-start one (tower_defense), trophy, a big new one (australia or around_unsw), islands, default, schooltime. 2 seeds × 2 sides. For fast checks.
3. **Validation run** (this is the point):
   BASE = live (mybot2), CAND = the passage build = origin/card/27's mybot2 with TERRAIN_PASSAGE=true. Get that source with `git show origin/card/27:mybot2/main.cpp` into a temp bot dir, with the other bot files copied from mybot2.
   Run `--set quick` first, then a wider set (official 17 maps × 2 seeds × 2 sides) if time allows.
   Question to answer: does the pool reproduce the online direction (passage worse, especially vs hunter, with more score-0 games)? Report honestly either way. If it does NOT reproduce, say which sparring style would be needed and try one more hunter setting.
4. `work/POOL.md`, ≤40 lines, plain English, casual: what the pool is, how to run it, the validation result table, and limits.

Constraints: no per-map hardcoding in bots; python3 stdlib only; don't change mybot2/main.cpp; no GitHub posts; no uploads; no ladder requests.
Write a ≤12-line note to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-pool.md with the validation numbers.

## ADDENDUM — settings from QWQ (the bot's author), use these as the pool definitions
All are toggles on top of the live settings (mybot2 on main already carries the v61 set + stride):
- `hunter` (QWQ calls it HQ61): QUEEN_HUNT=true, QUEEN_CHASE_DIST=8. QWQ: "It reproduces ladder-like queen deaths (95 of 151 were rams)."
- `rammer` (kamikaze rammers): AGGRESSIVE_MAX_CELLS=100000, TRADE_LOCAL_EDGE=-10
- `assassin` (big-dragon assassins): ASSASSIN_MOD=2, ASSASSIN_MIN=2, ASSASSIN_TARGET=12
- `nostride`: STRIDE=false
- `v61`: dir v61/ ; `live`: mybot2 as is.
QWQ's caveats: sanity-check the rammer and assassin builds first, they were last used on v54/v55 (make sure they compile, don't time out, and the style shows in a few games). None of these plays like the top teams (about 60 units by round 200, feeding from round 300), so say that clearly in POOL.md as a limit: the online check stays the final word.
If partial work from a stopped attempt exists in this worktree, build on it.
