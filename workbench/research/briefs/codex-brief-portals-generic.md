# Codex brief: how elite teams use portals online, and how fast an unseen map's portal links can be learned (input for W3)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §4 step 7: local games are mechanism checks only; feedback comes from online behaviour.
- `docs/WORKQUEUE.md`, task W3 and its portal item.
- The rules in `rules/ALL.md`:
  - "# Kelp and Portals", around line 259. A portal edge has an id shared with its partner edge. Vision does not extend through a portal; the far side is visible only within 3 tiles by ordinary distance. Sonar travels through portals.
  - "Vision", around line 312.
  - Movement through a portal, around line 790.

## Why
The qualifier build runs with map recognition off, so our map-specific Portals module (MODE3, V7, the W1 pocket ban) never runs. On an unseen map with portals the bot sees portal edges and their ids, but it does not know where each one leads until it has seen both ends or crossed it. The user's concern is that the bot may move sluggishly on portal-heavy maps.

We want generic portal rules that trigger on observed portals, grounded in how elite teams actually use portals online.

## Data
- **Elite games.** All Portals games in `data/top/index.jsonl` (top-vs-top, excluding stalled games) and in `data/elite/`.
- **Our online games** on Portals: W0–W12 and `data/online/v1-w1..3`.
- **Maps.** `maps/online-20260927/portals.map`, and any other map with portal edges (`maps/`, `maps/generated/gen_M_03`, `gen_M_04`). These are the ground truth for the portal pairs.
- **Code you may reuse.** `exp/portals/` (the earlier Portals-module extraction), `exp/spatial/` and `tools/top_features.js`.

## Questions
Report elite winners, elite losers and ours (online) separately.

1. **Learning the links.** For each portal pair, find:
   - the first round both ends had been inside the team's vision (the union of all its dragons' 7×7 windows);
   - the first round any team dragon crossed it.
   - Then estimate what a single process can know. It knows its own windows, its own crossings and the ends it can see within 3 tiles.
   - With the symmetry type known, how much earlier would mirror inference give each link? (The mirror of a linked pair is a linked pair.)
2. **How the elite use portals (generic behaviours).** Measure:
   - crossings per game by phase (r0–49, 50–149, 150–349, 350–500);
   - who crosses (length; king or piece);
   - the situation before crossing:
     - a threat: an enemy head within distance 3;
     - foraging: pearls within 3 of the exit;
     - an attack: an enemy head within 3 of the exit after crossing;
   - deaths within 3 rounds after crossing, by cause;
   - how far pieces stay from portal ends whose other side is unknown to them, or enemy-held.
3. **Threats through portals.** What share of our online deaths had a killer that came through a portal within its last 3 moves? Compare with elite winners and elite losers.
4. **Pockets behind portals.** How do elite teams harvest pockets whose only exit is near a portal? What happens to those who do? This is the basis of the W1 pocket ban; check whether it holds as a generic rule.
5. **Recommendations.** Generic portal rules that trigger on observed portals, each with N and the expected mechanism effect, labelled as hypotheses. Examples:
   - link learning and mirroring;
   - the risk value of tiles next to an unlinked portal end;
   - when to cross;
   - pocket rules near portals.

## Deliverables
- `exp/portals-generic/tables.json`, written first.
- `research/observations/portals-generic.md`, in Korean:
  - keep [사실] and [해석] apart;
  - give N everywhere;
  - follow the three-stage method: full-population scripts, then classes with their sizes, then deep reads with game ids and rounds;
  - end with a rule table.
- `exp/portals-generic/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/portals-generic/**` and `research/observations/portals-generic.md` only. Do not commit.
- No network, no uploads, no games.
- At most 2 worker processes. Keep caches compressed.
- Pause below 10% free memory or 21 GB free disk.
- Recount the key numbers independently.
- **Target:** about 3 hours after start.
