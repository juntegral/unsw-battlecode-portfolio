# Case study 4: measurement, and learning the noise the hard way

## Problem

A change to a game-playing agent is only as good as the instrument that judges it. We had three instruments: local
games against our own bots, online test games against named teams, and the ranked ladder. Each lied in its own way,
and most of what went wrong in the last two days was a decision made on an instrument whose noise we had not
measured.

## The instruments I built

**Local rig** ([`local-rig/`](../../local-rig)). Games are deterministic: the same two bots, map and seed give the
same game. [`play.sh`](../../local-rig/play.sh) and [`run_game.py`](../../local-rig/engine/run_game.py) run a game
under a machine-wide slot limit; batch scripts play "arm against the live bot, both seats, skip finished games" and
print a tally. About 9,000 local games were played in the final phase.

**Online harness** ([`smoke.py`](../../workbench/tools/smoke.py), [`pair_report.py`](../../workbench/tools/pair_report.py),
[`fair_queue.py`](../../workbench/tools/fair_queue.py)). Uploads a test copy, requests a fixed set of games against
chosen opponents, downloads the replays, attributes every game to the bot that actually played it, and reports
pairs. Test tickets were scarce, so requests go through a queue shared fairly between cards.

**Ladder study** ([`ladder_collect.py`](../../workbench/tools/ladder_collect.py),
[`ladder_replay.py`](../../workbench/tools/ladder_replay.py), [`ladder_rows.py`](../../workbench/tools/ladder_rows.py),
[`workbench/data/analysis/ladder/`](../../workbench/data/analysis/ladder)). An hourly collector, a replay reader
that rebuilds the true game state from the replay format, and scripts that classify every loss by cause over all
games, not a sample.

**Live watchers.** [`park_watch.py`](../../workbench/tools/park_watch.py) keeps two copies of the same code on the
server: the higher-rated one stays parked and the lower one plays, and they swap when the playing copy passes the
parked one, so rating only ratchets up. [`weak_watch.py`](../../workbench/tools/weak_watch.py) flags every ranked
loss to a team rated 100 or more below us and starts an analyst on it.

**Map generator** ([`workbench/tools/mapgen/`](../../workbench/tools/mapgen), [`local-rig/maps/`](../../local-rig/maps)).
Map families with controlled size, wall and portal density, for testing on maps the bot has not seen.

## What the measurements showed

- **The queen decided matches.** Our queen was dead in 243 of 266 losses. With our queen alive and theirs dead we
  won 65 of 65.
- **The early economy decided the queen's chances.** 41 of 71 classified losses were decided by unit count before
  round 150.
- **A 15-game online set cannot separate versions.** The same bot against the same unchanged opponent scored 8 of
  15, then 4 of 15 two hours later. Eight switches turned on during the last night on such sets were turned off
  again.
- **Averages hide broken maps.** A table of pearls and units at rounds 50 and 100 and the queen's death round, per
  map and per version, found two harmful switches within an hour each. On one portal map pearls eaten by round 100
  had fallen from 238 to 71. Hours of win counts had found nothing, and local head-to-head had rated both switches
  neutral.
- **Familiar maps flatter the bot.** On 64 freshly generated maps the then-live version lost 31-3-40 to our own old
  bot while winning 12 to 14 of 16 on the familiar set. That run came 13 hours before the deadline.

## What I would do differently

1. Measure the noise floor of every instrument in the first week, by running the same bot against itself and
   against a fixed opponent at different hours.
2. Build the map generator and a "break it" set in week one, and ban per-map logic from the start.
3. Read the per-map health table after every upload, before looking at wins.
4. Rank losses by cause and re-rank after every few fixes, so effort follows the largest class.
5. Do not use rating games as a lever near a deadline: one loss cost about twice what one win paid.

Sources: [write-up 01, sections 1, 3 and 5](../../writeup/01-playbook.md),
[write-up 02](../../writeup/02-game-knowledge.md), [write-up 06, section 3](../../writeup/06-timeline.md).
