# Analyst: skku (why a peer team beats the live bot 4-1 twice)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Data, Rules: [M] measured / [C] code with lines / [E] inferred; never state a
number you did not compute) and `data/codex/astra/CARDS.md`. Write only under `data/codex/astra/skku/` (scripts, tables,
`report.md`). No games, no uploads, no source edits. Keep scripts light, one process.

The question: Team SKKU (rated about 2157, the same as us; we are team 1119) beat us 4-1 in two ranked battles within 80
minutes: battle 1514288 (our bot one13, submission 21377) and battle 1519937 (our bot one14, submission 21497, the live bot).
Replays and per-game json: `data/online/live-one1/b1514288/` and `data/online/live-one1/b1519937/` (`M<id>.replay`,
`game-<id>.json`). Live source: `data/online/smoke/one14-bot/main.cpp`. Readers: `tools/ladder_replay.py`,
`data/analysis/ladder/dossier/work/o1_scan.py`, `o1_look.py` (7 by 7 boards). Earlier loss analyses for the form and for what
is already known: `data/codex/astra/weak13-opus/` (ledger.txt, queen-boards.txt), `data/codex/astra/stuck-opus/` (a detector
for dragons that circle without eating: `detect.py`, `cls.py`).

Deliver `report.md`, under 70 lines:
1. For each of the 10 games: the map, how it was decided (queen / longest / total / wiped out), the final state of both
   sides, the round from which we were behind for good, and a ledger every 50 rounds (dragons, total length, longest, queen
   length; both sides). Confirm the bot id of each game.
2. For the 8 lost games: the single event or habit of ours that lost it, with rounds and dragon ids. If our queen died: round,
   her length, the attacker's path (free and paid steps, through a portal or not, in her view at her last turn start or not),
   whether their queen was already dead, and which live switch should have applied and the condition that did not hold.
   If we were out-eaten: from which round, and what our dragons were doing instead (use the circling detector's patterns).
3. What Team SKKU does that we do not: their split timing, how their queen behaves (length over time, where she stays), how
   they attack our queen (who, from how far, paid steps), measured with the same script on both sides.
4. Verdict for the lead: one cause shared by most of the 8 losses, or several; is any of it a BUG (something no version should
   do) with a constant remedy `CONST:value` among the existing switches; and which of these candidate switches, being tested
   right now, would have changed the outcome of which game: THREAT_HIDDEN_PARTS 8 (a long dragon sizes an enemy whose body
   leaves its view as 8 parts), QS_HEAD_CLEAR 4 (the queen does not split with an enemy head within reach, and steps away
   from an adjacent head), POCKET_PEARL_SKIP 40 (a dragon drops a pearl it is not allowed to enter for), TERRITORY_DECAY 0,
   HARVEST_SPLIT true (non-queen dragons of 4 or longer split at once instead of holding to eat).
Your final message = the first 25 lines of the report.
