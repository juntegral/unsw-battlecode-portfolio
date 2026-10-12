---
name: ai-cards-delegated
description: "user delegation 10-05: for by:ai cards Claude gives the answers and decisions itself and keeps them moving; shipping still needs a human OK"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e3d433df-e6c2-41f6-81d4-738b9ea48abd
  modified: 2026-10-04T19:09:31.971Z
---

For cards labelled `by:ai` (ideas the loop wrote from ladder games, e.g. #23 queen-no-trap, #30 big-map-trades on 2026-10-05), Claude answers whatever the loop is waiting on and keeps the card moving, without asking the user each time.

**Why:** On 2026-10-05 ~04:08 KST the user said: "일단 ai인거는 너가 답변 제대로 하고 계속 빠르게 넘어가는 방식으로 하자. 내가 너한테 능동적으로 행동한다는 거에서 위임할게." They had just assumed #23 was Zhe's and wanted to wait for him; AI cards have no author to wait for, so waiting only stalls the loop.

**How to apply:**
- Answer the loop's questions on AI cards (clarify defaults, what to watch in the run), run the online pair test when a card is built or sits at "coin flip locally; an online pair test would settle it", read the result on behaviour, and record the decision on the card (candidate, revise, inconclusive, rejected) with a short plain reason.
- Write the answer as mine, not as the user's words: sign it as Claude acting for 준싱 (my choice of wording; the user did not specify one).
- Tell the user afterwards in the status report what was decided and why.
- Not delegated (my reading of the limit in [[proactive-handling-ok]]): approving a candidate for main, uploading or activating a release, and anything on cards by zhe, qwq or junsing. Those wait for the person per the loop rules.
- Check the `by:` label before assuming whose card it is. Related: [[loop-spec-1004]], [[team-dynamics]].

10-05 04:25 KST user, before signing off: when deciding whether to adopt a card after its build and ALL its tests are finished, do not decide by simple number thresholds. Judge independently and objectively, weighing the direction the team set in the Discord conversations and the other context ("수치적인 단순한 판단 말고 ... 독립적이고 객관적인 사고로 판단해줘. 기존 디코 대화를 통한 방향성 등 여러가지"). So: wait until local outcome, online pair and behaviour counts are all in; then write the decision with the reasoning (what the behaviour shows, what the numbers can and cannot tell, how it fits what Zhe and QWQ said), not just the net-win rule.
