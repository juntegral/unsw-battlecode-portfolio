# Reports sent to the lead by watch19-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:47:33 — SKKU battle was one18, no one19 games yet

watch19 14:45: no one19 game on disk yet. The Team SKKU battle b1536232 (lost 1 of 5, done 14:39 to 14:42 KST) was played by bot 21761 = one18, not one19, so it does not count for the verdict.
Baselines ready from the same folders: one17 45 games, one18 40 games; on maps of 600 cells or fewer neither has a queen dead on wall or own body with 0 free cells before r60 (0 of 16, 0 of 17); timeouts, never-eating sides, one-round collapses: 0 in both. Polling every minute for 21827.

---

## 2026-10-09 05:52:24 — 14:52 still no one19 games on disk

watch19 14:52: still 0 one19 games on disk. Newest folder in live-one1 is b1536232 (14:44, one18); the requests to SKKU, test4 and Cybers have not produced a folder. If nothing lands by 14:57 my verdict will be "cannot tell (0 games)".

---

## 2026-10-09 05:57:07 — Final verdict: cannot tell, 0 one19 games

cannot tell (0 games)
watch19 14:57 KST: no game with bot id 21827 reached ROOT/data/online/live-one1 between 14:36 and 14:57. Last poll 14:56:49; newest folder is still b1536232 (14:44).
- The one battle that landed after the upload, b1536232 against Team SKKU (lost 1 of 5, done 14:39 to 14:42), was played by 21761 = one18. The requests to SKKU, test4 and Cybers produced no folder.
- So nothing about one19 is measured: no BROKEN sign seen, no GOOD sign seen. This is absence of games, not a clean bill.
- Baselines from the same folders, in case a late game arrives: one17 45 games, one18 40 games; on maps of 600 cells or fewer, queen dead on wall or own body with 0 free cells before r60: 0 of 16 and 0 of 17; timeouts 0, never-eating side 0, one-round collapse 0 in both; queen moving into an enemy head on her own turn: 3 games in each.
- Not checked: whether 21827 is actually the active submission on the server (I only read replays on disk).
Files: ROOT/data/codex/astra/watch19-opus/watch.md, lines.txt (per-game lines for one17 and one18), w19.py (rerun from ROOT to add any late one19 game).
