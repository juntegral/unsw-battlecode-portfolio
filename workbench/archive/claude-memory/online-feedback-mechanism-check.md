---
name: online-feedback-mechanism-check
description: User rule — feedback comes from online behaviour (does each mechanism fire and work vs elite); win rate is not a criterion; local proxy games are mechanism checks only, "numbers are poison"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-30T01:18:12.719Z
---

User, 2026-09-30 10:10 KST: "승률은 보지 않아도 돼. 승패는 우리가 검증하려는 가설과는 아직 한참 영향을 받는 단계가 아니야. 가설 20개 정도가 모여야 승패가 흔들리는 거지, 특히 극상위권한테는. 앞으로는 대전 이후에 승률 분석보다는 그 웨이브(1시간마다 도는 것)에서 우리가 이 봇으로 구현한 바가 실제 완성도 높은 상대에게 적용되는지를 확인해야 한다. 이걸 기반으로 온라인 대전 피드백 양상을 완전히 바꿔."

- A "wave" is the hourly online set (one ticket window).
- After each wave, check every mechanism the bot implements:
  - Did it fire against the elite teams, and where (team × map × phase)?
  - Was the situation the one it was designed for?
  - Did the designed immediate effect happen?
  - How did the elite opponents defeat it? List the failure cases for replay study.
- Win rate and G are not adoption criteria. Mechanisms that apply as designed are **stacked** into `bot/`; the user expects about 20 stacked hypotheses before wins move.
- **Instrument each mechanism.** The bot's INDICATOR text survives in server replays; the current bot already writes `feed`, `esc`, `PORTAL?`, `TRADE`, `pocket-eat`, `escape-split` and `split`. Give every new mechanism its own tag, so the tagged replays can be counted.
- **Pre-register before each wave:** for each new mechanism, write down its trigger situation, the expected effect and a threshold, taken from the hypothesis.
- **Partial application (user-confirmed 2026-09-30 17:16 KST; the user had meant to propose it):** a mechanism that misses part of its gate but whose purpose (hypothesis-level indicator) moved the intended way stays on and is refined from its failure cases. If the purpose did not move either, switch it off and redesign.
- **Survival is judged by body, not dragon id (user-confirmed, same time):** count the dragon plus descendants born after it (its family). Corridor loops and split U-turns hand a body to a new id. Report the id-based value only for reference.

- **Outcome metric (user, 2026-10-01 00:25 KST):** "레이팅은 우리랑 상관이 없음. 그리고 우리는 승률을 상위 7팀 기준으로 해야하는거임. 저 이상한 짜바리 1500대 팀들이 아니라."
  - Judge outcomes only by results against the top-7 wave opponents (rated about 1900+), split by map family.
  - Ignore rating, ladder rank and autoscrim or low-rated scrim results.
  - Through W11 the top-6 wins held flat at 2–8 of 60 per wave; only the eliminations fell (36–40 to 23–29 of 70).
- **Local games (user, 2026-10-01 14:37 KST, online requests paused):** "우리는 피드백 자체는 온라인 대전에서의 행동을 통해서 해야하니까 ... 우리가 구현한 가설이 실제로 작동하는지 정도만 확인해야지 그걸로 이겼다고 위안삼고 넘어가면 안돼. 수치정보는 독이다."
  - Local proxy games only verify that a hypothesis fires and produces the intended board state; never adopt/reject on, or report comfort from, local win/length numbers.
  - I had drifted that day: W1/W4 decisions and my reports were phrased as proxy win counts. Pre-registrations I hand to agents/Codex must use mechanism criteria (fired, board state, breakage), not outcome thresholds; user reports lead with mechanism facts and board evidence.
  - More unseen test maps for mechanism checks: approved ("대찬성"). More local opponents just for more numbers: not approved ("잘 모르겠음").
**Why:** single hypotheses are far below outcome sensitivity against elite teams, so outcome gating stalls growth. What can be learned per wave is whether the implementation works in the real environment.
**How to apply:** the hourly online set is followed by a mechanism application report, not an outcome comparison. Local checks only confirm that a mechanism fires and runs safely. Related: [[feedback-core]], [[past-judgments-not-direction]], [[heuristic-repo]].
