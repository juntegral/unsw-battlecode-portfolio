# Codex brief: analyse two finished v1.8 test batches and propose the defaults (mechanism criteria only)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §4 step 7: local games are mechanism checks only, and no decision is made on win counts.
- `docs/WORKQUEUE.md`, section Q: the "Q1 다음 일" item 1 and the "Q2 다음 일" item 1.
- `versions/v1.8/VERSION.md`, §1–9.
- `exp/v16/q1/Q1.md`, §10–13.

All games ran on engine 1.2.3. Replay tools must use `UNSW_RULES=123`, or `perGame(R,{rules:'123'})` in `tools/mass_ledger.js`.

## A. The Q1/Q1b2 re-run on v1.8
- **Pre-registration:** `exp/v16/q1/Q1.md` §13.
- **Sets:**
  - `exp/v16/q1/v18-{king,hunter,gen}` (v1.8 as is);
  - `q18-*` (+Q1);
  - `q18b2-*` (+Q1b2);
  - the log is `exp/v16/q1/runq-q18.log`.
- **Tools:** `exp/v16/q1/` (`qmech`, `queenstat`, `ana/`) and `exp/q2/queenstat.js`, `queendeath.js`.
- Report every §13 criterion:
  - feeds land on the queen;
  - queen length curve;
  - late feeds to non-queens;
  - JIT merges only with a living queen, and the share of drops eaten;
  - ally-blocked queen traps;
  - fallback after her death;
  - identity before r300 and with the switches off;
  - CPU and errors.
- **Interactions with Q2:**
  - Q2i stops the queen racing for drops. Does she still eat the feed drops?
  - Q2f/f2 against the gathering: do allies block the queen?
- Propose whether Q1_ON and/or Q1B_ON should be on by default, by the partial-application rule: a purpose that moved the intended way → on.

## B. spec-11 (Q2 cand4 vs cand6, second seed)
- **Sets:** `exp/q2/cand4-king`, `cand4-hunter2`, `cand6-king`, `cand6-hunter2`. See `versions/v1.8/VERSION.md` §6–7 for what they test.
- Report:
  - queen survival to r500;
  - death precursors (`queendeath.js`);
  - start-pocket maps' results against v1.7;
  - pooled with seed 1 where the keys match.
- Confirm or question the current v1.8 default (cand4 + Q2h exemption, Q2k off).

## Deliverables
- `exp/q-analysis/tables.json`.
- `versions/v1.8/ANALYSIS-1002.md`, in Korean:
  - per criterion: value, N, pass/fail against the pre-registration;
  - 2–3 board pictures of queen deaths or merges (`exp/v16/board.js` or `eval/board.js`, with UNSW_RULES=123);
  - a short "proposed defaults" section.
- `exp/q-analysis/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/q-analysis/**` and `versions/v1.8/ANALYSIS-1002.md` only. Do not commit.
- Do not edit the bot or the params.
- No network, no uploads, no games.
- One or two worker processes.
- Keep any code comments short.
- **Target:** about 1–2 hours.
