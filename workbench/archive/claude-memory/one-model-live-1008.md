---
name: one-model-live-1008
description: user decision 10-08 22:19 KST — stop experiments; ONE combined model goes live now, then improve its weaknesses from its own games by intuition; no evidence-hunting, no sequential A/B
metadata:
  type: project
---

User, 2026-10-08 ~22:19 KST (he called it a big decision): upload to the server now, as one model, not sequential tests ("순차적으로 말고 한 모델로. 이제는 실험이 중요한게 아니야"). No live upload had happened since 15:00. From here: improve the weaknesses of the uploaded model and trust intuition ("수정보다 개선이, 근거를 찾기보다는 직관적인 방향 선택이 필요해"). If a fix has to change existing logic, just change it; the toggle/identity discipline is something to reconsider only at each big refactor.

**Why:** the deadline is 2026-10-09 15:00 KST, tickets are scarce ([[same-hour-baseline]] update), and isolated A/B tests could not finish in time.

**How to apply:** build one bot from everything I believe in, make it live, announce it in #meow with the rollback id, then loop: read the live model's own games (incoming ranked games cost no tickets), pick the biggest weakness, fix, upload the next version. Keep v62 (submission 20366) as the rollback. Split work as in [[codex-outsourcing]] and decide alone as in [[full-autonomy-1008]]. Teammates' approved cards go into the model; an unapproved card (e.g. Zhe's #55 on 10-08) waits for its author.

**22:2x update (user):** "앞으로 되돌리는거는 가능하면 지양하는 편이 나아. 하더라도 기존 봇으로 돌리는 것이 아닌, 지금 가지고 있는 토글들 중에서 제 몫을 다하지 못한 부분을 수정하는게 맞아." So no rollback to v62 as the response to a bad result: find which switch in the live model is not doing its job and fix or re-tune that switch, then upload the next version forward. v62 (20366) is only for a broken bot (crashes, timeouts), not for a weak one. This replaces the earlier "눈에 띄게 나쁘면 v62로 되돌린다" in my own plan and [[upload-only-rule]] still holds.
