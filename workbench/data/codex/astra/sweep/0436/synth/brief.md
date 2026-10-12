# Astra analyst: sweep 0436 synthesis

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Rules), `data/codex/astra/CARDS.md`, and every report of this round:
- `data/codex/astra/sweep/0436/loss1/report.md`
- `data/codex/astra/sweep/0436/loss2/report.md`
- `data/codex/astra/sweep/0436/win1/report.md`
- `data/codex/astra/sweep/0436/win2/report.md`
Write only under `data/codex/astra/sweep/0436/synth/`; report `data/codex/astra/sweep/0436/synth/report.md`, under 350 words plus one table. The lead reads ONLY this file, so it
must stand alone. Do not re-analyse replays; check a number only where two reports disagree.
1. One table: cause, games it explains this round (ids), status against CARDS.md (NEW / BEING BUILT / LIVE-BUT-FAILED), the card
   in one line (paste form `CONST:value` if an existing switch does it, otherwise the rule and the lines), which report has the detail.
   Ranked by games explained; merge causes that are the same thing under different names.
2. Losses to teams rated 100 or more below us: each game id with its cause and whether a listed card covers it.
3. Live fixes that failed this round, each with the condition that failed.
4. From the won games: what is working, and the weakest point.
5. The three things the lead should build or switch next, in order.
