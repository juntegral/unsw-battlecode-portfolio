# Reports sent to the lead by retro-tools

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-10 09:41:02 — closing summary

The tools chapter is written, at `~/01. Project/개인 프로젝트/unsw-swarm/docs/retro/04-tools.md` (537 lines, slightly over the 250–500 target). I ran no server, Discord or GitHub tools.

**What it contains**
1. The chapter is organised by job, in your nine groups, with a table or command block per group. Each entry gives the path, one line on what it does, the command line as used, and a trap if one was recorded. Command lines come from docstrings, `HANDOVER-2026-10-09.md` §7 and the `up*`/`h2h*` scripts.
2. It records the four reusable patterns, with counts from disk:
   - the slot-limited game launcher;
   - `mkbots.py` plus the all-switches-off hash test (`92fb69564fbd`);
   - the "arm vs live bot, both seats, skip finished" shell template;
   - the true-state replay reader (`ladder_replay.py`).
   Over 229 archive scripts, 50 call `play.sh`, 27 call `mkbots.py` and 26 use `shasum`. Locally there are 9,077 finished games, 488 arm folders and 615 builds.
3. It documents the identity protocol (all-off hash, live-values hash, then `cmp -l` on replays, where a 2-byte diff is only the bot name). It also documents the spend-guard design (plan by default, `--confirm`, `--expect-active`, ledger, key redaction).
4. A trap table with dates covers the server refusing the 1.2.7 client, the local slot cap of 2 games until 10-09 13:52, and the hard-coded `smoke.py` freeze time. It also covers `pkill` incidents, the dead `viewer.js` and `replay2map.js`, and `ladder_replay.py` importing a one-off analysis folder.
5. The last parts are "what we would build first next time" (nine steps in priority order) and Appendix A, with one-off scripts counted per folder.

**What I looked for and could not establish**
- Exact date of the server's 1.2.9 refusal. It is about 12:15 KST, most likely 10-07 from its position in the log; `HANDOVER-2026-10-08.md` line 45 repeats the time without a date.
- Who edited the `smoke.py` freeze at 22:13 on 10-08; the files I read don't say.
- Usage counts per tool from the log. `SESSION-STATE.md` mentions outcomes, not tool runs, so I used archive script counts as the proxy.
- Arguments for `astra/mapgen/gen.py` and `sweep_loop.sh`: I read the code but have no recorded invocation, so the chapter marks them "read".
- The bodies of the roughly 1,100 analysis scripts (359 in `dossier/work/` plus 739 under `astra/`). Their purposes come from names, docstrings and the log.
- Whether `fingerprint.js` was ever used after 09-30. I found no use.
- How much `meowbot` and the desk session saved, and how much each one-off analysis script changed a decision. Neither is recorded, and the chapter says so.
