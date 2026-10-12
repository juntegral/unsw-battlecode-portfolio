# g2: map-aware forager with survival lookahead

Bot: `lineages/g2/bot/` (C++: `main.cpp` + generated `mapdb.hpp`; `helper.hpp` is unused but kept). Own protocol reader.
Rules come from the live docs (protocol 3.0.0). The bot never sends `PROTOCOL 3`: it reads protocol-2 input, and its parser also accepts ECHOES.

## Version history
- **r1** = submission 8410 (main.cpp sha256 4c40eb1d…), frozen copy in `versions/r1/`.
- **r2** = snapshot `lineages/_releases/g2-r2` (main.cpp 861d9c0a…, mapdb.hpp 02741700…), frozen copy in `versions/z5/`.
- **r3** = r2 plus Trophy swarm mode plus the stuck-split cascade guard (main.cpp 2e6da06f…). Frozen copy in `versions/r3a/`. Never uploaded as its own version.
- **r4** = r3 plus a dynamic "hunted" swarm trigger (main.cpp a8e5a0aa…). Frozen copy in `versions/r4/`. Never uploaded as its own version.
- **r5** = current `bot/` (main.cpp sha256 ccad0740…, mapdb.hpp unchanged 02741700…). r4 plus calm mode on Trauma. Ready to upload.

## Online batch 20260927-g2-r2-b1 (r2 = submission 8611, 54 unranked games)
- **Overall: 21W / 33L** (r1: 19W / 32L). 15 losses were eliminations (r1: 17).
- **Improved:**
  - Prisoners 5/6 (r1 2/6).
  - Slithery 3/5 (r1 1/4).
  - Portals 2/5 (r1 1/4).
- **Regressed:**
  - Trauma 3/8 (r1 6/8). Our longest was 7–12 against the opponents' 12–30.
  - Cause: r2's insurance splits (U<4, L 8–24 → split 3) keep chopping the one slow-growing champion. Locally the Trauma champion fell from about 30 (pre-insurance variants) to about 10.
- **Eliminations** by map: Trophy 5, Default 3, Devil 3, Queen 3, Autarky 1. Almost all come from rams (202 plain, 165 sprint).
- **Ally head-ons: 176.** Nearly all are on Portals (18–29 per game). Two of our dragons jump blind through portals into the same tile.
  - A "portal fog" penalty (`versions/pf1`) did not reduce them locally, so it was not adopted.
- **Length gaps against strong teams:**
  - Macleans school 84, bibobibo school 62, Bad Subtraction school 36.
  - JKS portals 29 / slithery 38, uhhhhhhhh portals 18 / slithery 27.
  - Sabotage-d trauma 30 / prisoners 35, "1" trauma 29.

## What changed in r5 (vs r4)
- **Calm mode on Trauma.** Only the last-dragon insurance split stays; the U==2 and U<4 insurance splits and the hunted swarm trigger are off.
  - Locally on Trauma (seeds 1–3, both sides): vs v8 5/6 with longest 29–37 in most games (r4 ~10); vs hunter 6/6.
  - Trauma had 0 eliminations online in both batches.
- **r5 regression check**, 10 maps × 2 seeds × both sides, same seeds as the earlier rows:

  | Opponent | r5 | r4 | r2 |
  |---|---|---|---|
  | archetype_hunter | 35/40 (88%) | 88% | 75% |
  | replay_rules_v8 | 23/40 (58%) | 55% | 48% |

  - Still weak vs v8: Prisoners 0/4 (14–14 tie, lost on total), Slithery 0/4, Autarky 1/4.
- Tried and not adopted:
  - Calm mode on Schooltime: no clear effect.
  - Champion flee for L>=15 (`versions/ch1`): mixed.
  - Region-harvest term (`versions/hv1`): Schooltime −60..−110.
  - Swarm-mode cutoff at round 300 on Trophy: worse.
  - Insurance only with no enemy in view (`versions/ins6`): much worse vs hunter.

## What changed in r4 (vs r3)
- **Dynamic swarm mode ("hunted").**
  - Trigger: a dragon sees >=3 small enemy heads (visible length <=5) at once.
  - Effect: that dragon uses Trophy's swarm-mode insurance for the next 60 rounds, on any map except Autarky and Prisoners. Swarm-mode insurance means split off 2 when L>=5 and U<14.
  - Reason: in the online meta most opponents field 30–60 small dragons, and eliminations were r1's biggest online loss mode (17/51).
- Local results, 10 maps × 2 seeds × both sides:

  | Opponent | r4 | r3 |
  |---|---|---|
  | archetype_hunter | 35/40 (88%) | 30/40 (75%) |
  | replay_rules_v8 | 22/40 | 21/40 |

  - Hunter gains: queen 0/4 → 3/4, schooltime 2/4 → 4/4.
  - Caveat: on Queen with seeds 3–7 vs v8 the trigger also fires, and r4 went 2/10 against r3's 5/10. It is a trade-off aimed at the swarm-heavy online field. If online data shows v8-like opponents dominate, set `HUNTED` to 0.

## What changed in r3 (vs r2), two small changes
1. **Trophy swarm mode.** On Trophy only (identified map), any dragon with L>=5 splits off 2 while U<14 (rounds <440).
   Trophy is a small open map where r1 lost 6/6 online, 5 of them by elimination to swarms, and r2 still lost it locally.
   Trophy, 7 seeds × both sides, r2 → r3:

   | Opponent | r2 | r3 |
   |---|---|---|
   | v8 | 1/14 | 4/14 |
   | hunter | 0/12, eliminated 12 times | 2/12, eliminated 3 times |
   | swarm | 5/10 | 8/10 |
2. **Stuck-split cascade guard.** When every move is instantly fatal, the bot splits L-2 only if the tail (the child's head) has a free neighbour. r2 sometimes cascaded 20→18→…→8 in one round, with each child born stuck.

Local check of r3, 10 maps, both sides:

| Opponent | Games | r3 | r2 |
|---|---|---|---|
| replay_rules_v8 | 60 (3 seeds) | 55% | 48% (40 games) |
| archetype_hunter | 20 | 75% | 75% |
| archetype_swarm | 20 | 100% | 100% |

- Against v8, r3 wins every game on devil and portals. Prisoners 0/6 (14–14 tie, lost on total length) and slithery 0/6 are still open.
- Tried and not adopted:
  - Swarm mode on Queen/Default: Queen vs hunter improved (3/4), but Queen vs v8 got worse (1/4, one elimination).
  - Exit mode after repeated escape splits, plus a static openness penalty for long dragons (`versions/d1`): 9/24 vs 10/24 on the six hardest maps.

## What changed in r2 (vs r1)
1. **Embedded public maps** (`tools/genmaps.py` → `bot/mapdb.hpp`, 15 maps: the 10 online maps + old/bundled ones). The map is identified from the first 7x7 view: never-spawn flags + 112 edge kinds must all match. Once identified, the bot knows every kelp edge, every portal pair, every tile's spawn gap, and the map symmetry. Every turn the view is checked against the loaded map; on any mismatch the map is dropped and the bot falls back to r1-style learning. The fallback was tested with the `NODB` build and does not crash.
   Portals shows the effect most: r1 lost 3/4 there online (longest 3–5), while locally r2 now wins 4/4 against v8.
2. **Survival fixes**
   - A move opposite to our facing (into our own neck, possibly through a portal) is always illegal. r1 died this way at the Prisoners start.
   - Initial bodies are loaded from the map file.
   - Own-body segments whose order is unknown are resolved by following their facings.
   - Tail-reachability (can the head reach our own tail after the move) counts as safe. The space requirement is now L+3 with no cap (r1 capped it at 40).
   - The survival DFS counts pearls eaten along its path (the tail stalls). When it runs out of budget it returns the deepest level reached instead of assuming the move is fine.
3. **Less fragmentation**
   - Escape split only when every move is physically doomed, the body is fully known and L>=6 (L>=4 inside a 1-wide tile).
   - When every move is instantly fatal, the bot splits L-2 anyway, so the child keeps most of the body.
   - After a split, the parent sends the child's first 12 body steps over sonar: a 32-bit message, fired in the direction whose ray hits the child first. The child decodes it.
4. **Anti-ram / elimination defence.** Online, r1 lost 17 of 51 games by elimination, mostly to head rams, 97 of them sprint rams.
   - Tiles next to enemy heads are penalised, scaled by our length and by vulnerability (3x when U<=2, 1.6x when U<=4).
   - Tiles an enemy can reach by sprinting (2..min(4,len-1) steps) are penalised too.
   - An ally head is never a destination (r1 had 629 ally-on-ally head collisions online).
   - Moving next to an ally head costs 300. Ally-head neighbours count as danger in the lookahead.
   - Trades (moving into an enemy head) only happen when we have units to spare.
   - Insurance splits: U==1 & L>=6 → split max(2,min(5,L/3)); U==2 & L>=6 → split 3; U<4 & 8<=L<=24 → split 3.
5. **Corridor logic.**
   - Through-corridors (1-wide) are penalised when a head sits near the far exit.
   - On Autarky and Prisoners only, the bot may enter a 1-wide dead end with >=2 expected pearls at L>=4, eat, then split L-2 at the end so the body walks out. Enabling this on every map hurt Trauma.
6. **Other dragons' tails.** For fully visible dragons (chain from the head proven complete), body segments free up on schedule (index-based, +1 margin) instead of acting as permanent walls.
7. **Pearl model.** On a known map, a tile never observed gets pearl probability 0.5·P(initial countdown <= arrival).

Tried and switched off, because A/B tests showed no gain:
- `FARMW` (a spawn-rate potential): lured dragons into Trauma's maze.
- `GROWP` (assume nearby pearls get eaten).
- `SUICIDE` (tiny split fragments kill themselves).
- `SPLITWHEN=1` (split only when stuck).

## Local evidence
All games run in the official sandbox (unswbc 1.1.0) on the 10 online maps, 2 seeds, with g2 playing both sides. `tools/g2eval.py` drives the engine API directly; `tools/summ.py` summarises.

| Opponent | r1 | r2 (z5 = bot/) |
|---|---|---|
| replay_rules_v8 | 42% (60 games) | 48% (40 games; other r2 variants 48–52%) |
| archetype_hunter | 70% | 75% |
| archetype_swarm | 90% | 100% |
| h2 | 100% | 100% |

- Against v8 we win every game on default, devil and portals (12/12). The weak maps are prisoners, trophy, schooltime, slithery and queen, which are length races where v8's champion is longer.
- On Prisoners both sides ping-pong one tube dragon at length 14; v8 wins on total length.
- CPU is about 4–6M points per turn at p50 and max (limit 100M). Memory is small.

## Online batch b1 (r1, 51 unranked games vs 17 teams)
- Result: 19W / 32L. 17 losses were eliminations, almost all from head rams by swarm teams (38–60 small dragons).
- Strongest length teams: Just Keep Swimming (portals 29, slithery 53, default 38), "1" and Sabotage-d (trauma 29/35), uhhhhhhhh (portals 25), Bit by Bit (trophy 31).
- `tools/online_an.py <batch-dir>` and `tools/rams.py <batch-dir>` rebuild these tables from the events files.

## Tools (all local, read-only w.r.t. the server)
- `tools/genmaps.py`: regenerate `bot/mapdb.hpp` from the public map files.
- `tools/g2eval.py OUT.jsonl BOT OPP[,OPP] SEEDS [maps] [--jobs 2] [--one-side]`: at most 2 concurrent games.
- `tools/traj.py`, `tools/capture.py`: trajectories and 7x7 views for debugging.
- `versions/`: frozen variants that were A/B tested (r1, r2a…, x1/x2, y0–y3, z1–z5).

## Open problems / next ideas (not in r2)
- **Trophy against swarms.** We are still eliminated there (hunter 0/4). None of these helped: a next-turn escape check (`ESCN`, neutral), a flee potential (`FLEE`, worse), more insurance splits.
- **Length race** on schooltime, slithery, trophy and queen: v8's champion (and Just Keep Swimming's online) farms the rich band/cluster and gets much longer than ours.
- **Prisoners** ties 14–14 and is lost on total length: v8's secondary dragons grow more.
- `dev/` holds the work-in-progress branch after r2 (per-map insurance tweak for Autarky/Prisoners). It is not yet shown to be better, so it is not in `bot/`.
