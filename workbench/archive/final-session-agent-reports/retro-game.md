# Reports sent to the lead by retro-game

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-10 09:42:35 — Retro chapter 02 game knowledge done

Chapter 02 (game knowledge) is written: ~/01. Project/개인 프로젝트/unsw-swarm/docs/retro/02-game-knowledge.md (451 lines, English, tables checked).

Summary (five lines):
1. Rules as understood at the end, from S/rules and the 1.2.7 engine notes, as one table plus five consequences the analysts relied on (a ram ignores length, reach = ceil(L/4) free + L-2 paid, queens move first, length converts through corpses, a dead dragon cannot report its kill), and what no rules file confirms.
2. What decides a match: a 2x2 table of queen fates against results for one11 to one15 (474 online games). Our queen was dead in 243 of 266 losses (91%); ours alive and theirs dead was 65 of 65 won; their queen died first and ours later in 114 games, 41 won. Four older independent counts say the same. Economy is second and acts in rounds 20 to 100.
3. How queens die: qexit's classes with counts (368 games, 286 deaths: 152 rammed in the open, 53 from a one-way place or boxed, 69 self-trap, 12 other), ten sub-classes with sources, and three "causes" that turned out not to be causes.
4. What strong teams do (opening, mid-game, late feeding with the top-ten queen-length timeline), a per-map table with features and our results, the unseen-map probes, eight opponent archetypes by behaviour, and open problems ranked by games cost.
5. A table of 13 corrected findings, how the findings were found, a next-time checklist, and the not-established list.

Two things you should know:
- The Q1 table and the per-map table are my own recount from shed-sonnet/data.json (scripts in S/data/retro-work/retro-game/: qtable.py, maptable.py). They are labelled as such in the chapter. That file holds one11 to one15, not one16 as the log entry says.
- The log entry at 14:05 says our queen was alive at round 300 in 133 of 474 games; its own parts (112 dead before r100, 175 in r100-299) leave 187, and my recount gives 187. I used 187 and listed it under corrections.

Looked for and could not establish:
- Any qualifier or bracket game, and any online game of one19, one20 or one21 (none on disk).
- Why seat A did so much better than seat B against Team SKKU (75.8% against 27.3% on 11 matched maps), and whether it is general.
- The code cause of our low time on narrow tiles in rounds 0 to 100 (early-opus cleared three suspects).
- Whether a home or in-swarm queen lives longer: two dossier diagnoses disagree and the leash constant was never played.
- What beats the flat no-feeding swarm and the teams above 2400.
- A pooled count of "out-eaten from round N" losses (the ledgers tag games one by one; nobody totalled it).
- True pearl timers for seven ladder maps; size and start layout of Autarky's starters and of Prisoners Dilemma.
- The scene in game 1532570 round 469 that jun and Zhe flagged.
- Reports for opp-ballers, opp-uncancel, unA, unC, unD, trauma-opus and review19-opus exist only as your log entries; their folders hold scripts or logs but no prose, so those rows cite the log.

Scratch files are only in S/data/retro-work/retro-game/. Nothing else was changed.
