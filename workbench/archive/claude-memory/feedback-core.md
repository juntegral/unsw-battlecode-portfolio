---
name: feedback-core
description: "User's core research principle: every test must be followed by an in-depth replay analysis against the baseline; feedback matters more than results"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-29T23:27:20.587Z
---

On 2026-09-30 03:10 KST the user said: "우리한테는 결과보다도 피드백, 즉 기보를 돌려보면서 기존 기준에 대한 딥러닝 분석을 해야하는걸 기억해. 그건 우리 연구의 핵심임을 절대 잊지마."

- A win/loss or G number alone is not a finding.
- After every online or local test, replay the games and analyse them in depth against the baseline's replays of the same team and map.
  - Where did the games diverge, and what did the candidate do differently?
  - Which mechanism caused each gain or loss, and which maps and situations were affected?
- Write the analysis down and feed it into the next hypothesis.
- "딥러닝 분석" most likely means deep and thorough analysis (깊이 있는 분석), not necessarily neural-network training. Ask if that becomes ambiguous.

**Final core direction (user, 03:20 KST):** "우리가 하는 것은 단순한 승률 판독이 아니다. 승률 판독할 거면 그냥 넓게 온라인 테스트 했을 것이다. 상위권 기보를 학습해라. 연구로는 이게 마지막 핵심 방향이다." Also: "매 리프레시 후 극상위권과 상대한 기보를 축적해서 우리 로직에 우려내야 한다."
- Online test sets exist to **accumulate our games against the elite teams**, not to hand down verdicts.
- Logic changes come from **decision rules learned from top-team replays**: top vs top, compared with our own decisions against them. The pipeline is `tools/decisions.js` and `research/observations/top-decisions.md`.
- The proxies beat our bot because they were coded directly from measured top-team behaviour.

**Scale (user, 2026-09-30 08:30 KST):** "초 거대 규모의 극상위권 대전 분석 및 가설 생성, 이걸 기반으로 하는 성장은 언제나 환영이고 우리가 지향해야할 방향임."
- Prefer the largest feasible analysis of elite games: all collected top-vs-top replays plus every online set against the top teams.
- Generate hypotheses from it systematically, and let the bot grow from them.

**Why:** the research is learning why things work. Outcome-only testing repeats the loop's mistake of judging "strategy + trigger" pairs without understanding them ([[g5-timing-divergence-analysis]], [[past-judgments-not-direction]]).
**How to apply:** every online test in the heuristic loop gets a replay-analysis step before the next candidate is designed. Record it in `research/experiments/` and cite it in the progress log. Related: [[heuristic-repo]], [[user-research-style]].
