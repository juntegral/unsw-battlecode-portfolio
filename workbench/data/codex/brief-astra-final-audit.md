# Final audits of the live bot (deadline 15:00 KST; report by 14:12 KST)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules: [M] measured / [C] code with lines / [E] inferred) and the State
section of `data/codex/astra/CLAUDE-COMMON.md`. You write only under the folder your task names. No games, no uploads, no edits
of sources. The live bot is `data/online/smoke/one17-bot/main.cpp` (one C++ file, about 9,000 lines; `helper.hpp` and
`sonar_codec.hpp` beside it). The last version that ran for hours without incident is `data/online/smoke/one11-bot/main.cpp`;
`data/online/smoke/one5-bot/main.cpp` is the version of yesterday evening.

Your task is the ONE named on the command line that started you:

**audit-diff** (folder `data/codex/astra/audit-diff/`): `diff` one11-bot against one17-bot. For every changed or added line that
is active with the live constants: what it does, and whether it can crash (out-of-range index, division by zero, empty
container access, uninitialised read), loop without bound, or return no action for a turn. Pay most attention to today's
additions: QUEEN_NO_BLIND_PORTAL (the `blind[k] = false` lines), QS_SHED_MAX (the exposed-queen split condition), and the code
that became reachable or unreachable when PORTAL_SCOUT_MIN_LEN and TERRITORY_DECAY went back to 0. `report.md`: first line
"SAFE" or "UNSAFE: <line, reason>"; then one row per change.

**audit-time** (folder `data/codex/astra/audit-time/`): the engine gives each dragon a time limit per turn and the qualifier
maps are unseen (up to 256 by 256 cells, hundreds of dragons). Find every loop or search in the live source whose cost grows
with map cells, with the number of dragons in view, or with the dragon's own length, and that is reachable with the live
constants; give its worst-case cost in words and whether a cap exists. Say which were added since one5 (diff against one5-bot).
`report.md`: first line "NO TIME RISK FOUND" or "RISK: <function, why>"; then the list, worst first.

**audit-unseen** (folder `data/codex/astra/audit-unseen/`): list every constant threshold in the live source that switches
behaviour on map size, round number, dragon count or portal presence (for example QUEEN_MIN_CELLS 600, the centre pull at
1000 cells, LEADER_GROW_ROUND, FEED_CAP_ROUND 350, QUEEN_SAFE_ROUND 300), with its live value and what flips at the threshold.
For each, the kind of unseen map on which the flip would be wrong (tiny, huge, all corridors, no portals, portals everywhere,
asymmetric starts, very rich or very poor in pearls). `report.md`: first lines = the three riskiest cliffs with the one-constant
change that would soften each (`CONST:value`) and why; then the full table.
