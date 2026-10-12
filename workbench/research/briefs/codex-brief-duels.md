# Codex brief: how elite teams win local 1:1 fights (slither.io-style duels), and how we lose them

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §4 step 7: local games are mechanism checks only, and feedback comes from online behaviour.
- `docs/WORKQUEUE.md`, task W10.
- The rules in `rules/ALL.md`:
  - Movement and Sprinting: moving x steps costs x − 1 segments.
  - Execution order: dragons act in ascending id order within a round, so a later id sees earlier moves of the same round. Children get new, higher ids.
  - Death (`rules/death.md`): Hit Wall (kelp), Hit Self, Hit Other Body (any team), Head to Head (both die), No Valid Action. A dead dragon drops ⌈L/2⌉ pearls, every second segment from the head.
  - Vision is the 7×7 square around the head.

Reuse code from:
- `exp/small/`, especially its head-on extraction (`headons.jsonl`) and reconstruction;
- `exp/w7/reach.js`;
- `exp/spatial/`;
- `tools/top_features.js`;
- `tools/mass_ledger.js`. Its `turn` hook fires at turnStart, before the move.

## Why
The user watched the sprint bracket live (custom unseen maps) and noted that winning local 1:1 fights matters a great deal. The fights look like slither.io duels: cutting in front of an enemy head so it runs into your body, pinning it against kelp, coiling, baiting with pearls. The qualifier is played on unseen maps, so duel skill is map-independent strength we can build. It must be grounded in how elite teams actually fight online.

What we already know:
- From `research/observations/small-maps.md` and `exp/w7`: on Trophy about 93% of our head-to-head deaths online were passive, meaning the enemy moved into us. Elite winners are the mover in 61% of their head-to-head contacts.
- Once we stand in an enemy's reach we are rammed 33.6% of the time, against 16.6% for elite winners.

## Data (the whole population; no sampling)
- **Elite:** every game in `data/top/index.jsonl` (excluding stalled games) and in `data/elite/`. Process the strict top-10-vs-top-10 subset first so early tables come quickly, then all games.
- **Ours, online:** W0–W12, `data/online/v1-w1..3`, and the autoscrim series of 2026-10-01 if they were downloaded.
- **Sprint bracket games (custom maps):** if any appear in `data/elite/` or `data/online/` while you work, add them as a separate cohort.
- **Team UnderTheC (id 328), a separate cohort.** The user flagged it: rated 1796, reached the sprint bracket's round of 16. The user's point concerns the bracket games only: the team is excellent at handling maps it meets for the first time.
  - Its known-map autoscrim games below are therefore only a baseline. Do not read first-encounter skill into them.
  - Data: `data/online/undertheC/`, 30 games from its six sprint autoscrim series on known maps, in the `tools/online.js download` layout (`index.json`, `game-<id>.json`, `M<id>.replay`, `events-<id>.jsonl.gz`).
  - New games also arrive in `data/elite/`, because the collector now follows team 328 too.
  - Besides its duels, write a short profile of what is unusual about it compared with the elite norms, for example:
    - head-count curve and split schedule;
    - piece lengths;
    - where its small pieces sit relative to its king, the enemy and fountains: do they act as observers or scouts?
    - deaths by cause;
    - final longest.

## Definitions (refine them if the data demand it, and say so)
- **Duel episode.** Two dragons of opposite teams whose heads come within BFS distance ≤ 4.
  - Isolated: no other head (ally or enemy) within 5 of either head for the whole episode.
  - Local 1:1: equal head counts within d8 at the start.
  - The episode ends at a death, at separation (> 6 for 3 rounds), or when a third head arrives.
- **Outcome classes:**
  - kill: one dies by Hit Other Body into the other's body, or Hit Wall/Self while within 2 of the other; the other survives;
  - trade: Head to Head;
  - disengage;
  - third party.
- **Kill patterns to separate:**
  - cut-off: the killer's head crosses the victim's path so that its body blocks;
  - sprint cut;
  - wall/kelp pin;
  - coil or encirclement;
  - head-to-head bait;
  - pearl bait.

## Questions
1. **Frequencies.** How often do duel episodes occur, and with what outcomes? Report by cohort (elite winners, elite losers, ours online), by map and by phase (r0–49, 50–149, 150–349, 350–500).
2. **What wins duels.** Outcome against:
   - length difference;
   - sprint budget;
   - who moves first in the round (id order);
   - free space for each side (flood-fill size within 5);
   - distance to kelp and walls;
   - nearby pearls;
   - nearby allies outside the episode.

   Simple tables or a shallow tree, with N everywhere.
3. **Kill patterns.** Give each pattern's share and success rate.
   - Pick 2–3 typical episodes per pattern, with game ids and rounds, and draw board pictures with `node eval/board.js <replay> <Map> <a|b> <A|B> <rounds>`.
   - What did the victim's last 2–3 decisions look like?
4. **Ours.**
   - In our online duels, which patterns killed us, and what did we do in the 2–3 turns before?
   - How often did our pieces cut off or kill in a duel?
   - Our bot has kill-path candidates in `plan.cpp` (line 2 lists "kill paths"). Find their INDICATOR tags in our replays: how often did they fire and succeed?
5. **Recommendations: generic duel rules**, map-independent and computable from the 7×7 view and our own state. When to engage, cut, disengage or accept a head-to-head trade.
   - Give each with N and the expected mechanism effect, labelled as hypotheses.
   - Note which existing planner terms (`docs/arch/terms.md`) each rule would change, and by roughly how much.

## Deliverables
- `exp/duel/tables.json`, written first: the strict-elite tables, then updated with the full population.
- `exp/duel/episodes.jsonl.gz`: one line per episode.
- `research/observations/duels.md`, in Korean:
  - keep [사실] and [해석] apart;
  - give N everywhere;
  - follow the three-stage method: full-population scripts, then classes with sizes, then deep reads with game ids and rounds;
  - end with a rule table.
- `exp/duel/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/duel/**` and `research/observations/duels.md` only. Do not commit; the coordinator commits.
- No network, no uploads, no games.
- At most 3 worker processes, run with `nice -n 10`.
- Pause if free memory falls below 10% or free disk below 21 GB.
- Keep caches compressed.
- Recount the key numbers independently, and report both counts.
- **Target:** strict-elite tables about 2 hours after start; everything about 5 hours after start.
