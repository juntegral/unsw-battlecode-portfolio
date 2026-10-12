---
name: analysis-population-all-games
description: "User rule (2026-09-30 11:17 KST) — every large-scale per-hypothesis analysis uses the whole accumulated population of games, never a sample; don't save tokens"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-30T02:24:03.934Z
---

User, 2026-09-30 11:17 KST: "각 가설별로 대규모 분석을 할 때 항상 분석 모집단은 우리가 누적한 전체 판수야. 토큰 아끼지 말고." Then: "물론 이거는 기보 연구를 하는 경우에도 항상 해당되는거야." — the rule covers every replay study too (failure-case studies, per-wave replay analysis, territory/timing studies), not only statistics.

- **Population for every large-scale analysis behind a hypothesis:** all accumulated games.
  - Every top-vs-top replay in `data/top` (8.5k+ on 2026-09-30, growing about 400 per hour).
  - Every online set of ours against the elite in `data/online/*`: baseline, candidates and waves.
- **No stratified samples** (such as `sample-top1500.keys`) as the final basis. A sample may be used only for quick exploration, and every reported number must then be recomputed on the full population.
- **Refresh before each analysis:** new games arrive every hour, so first extend the caches with the new games (`mass_ledger.js extract top --keys all`, `decisions.js refresh --top all`, `extract online <new sets>`).
- **Interpretation, not confirmed with the user:** "our games" means our games against the top teams and DEV. Autoscrims and mid-team games (`r1-autoscrim`, `r1-online`, `g1`, `g2`) are left out, because the user called autoscrim results garbage. Include them if the user says otherwise.
- **Don't economise on tokens or agent effort** for these analyses. The limits are machine capacity (6 local games, memory) and the 20 GB disk floor.
  - The user repeated this at 2026-09-30 21:06 KST: "토큰 아끼지 않는거 꼭 명심해라".
  - Token cost is never a reason to trim anything. That includes verification (independent recounts from raw replays by a separate agent, not one spot check), deep replay reading, deep-research verification votes, agent prompts and agent counts. The only limits are machine limits.
- **Method (user, 11:25 KST):** "대규모 분석을 하는 경우에는 모집단을 전체로 두고, 이때 이후 기보 분석을 할 기보를 분류, 이후에 선별된 기보를 통해서 분석을 하면 토큰 양은 엄청나게 낭비하지 않으면서 할 수 있어." So the work runs in three stages:
  1. **Scripts over the full population.** Compute the statistics on every game, which costs few tokens.
  2. **Classify with scripts.** Sort the games or events into classes by situation, failure type, team, map and so on, and record the size of each class.
  3. **Deep replay study on a selection.** Pick replays from each class with a stated rule, such as representative cases, extreme cases or a fixed number per class. Only these selected replays are read closely, so this is where the tokens go.
  - Reports state the population N, the class sizes and how the replays were selected.
- **Most important sample (user, 11:28 KST):** "해당 가설의 선행된 실험체(ex. merge2 같은 봇)가 있으면 그게 가장 중요한 표본이긴 하지. 아무튼 확실한 연구가 중요해."
  - When our bot has already implemented the hypothesis, that bot's games against the elite are the primary evidence. Example: merge2's games for its mechanisms. Always include all of them.
  - Top-vs-top games are the reference.
  - Rigour comes first: recount key numbers independently, fix criteria before looking at results, and state N, the classes and the selection rule.

**Why:** samples miss rare situations and team-specific behaviour, and the user wants maximum-scale elite learning.
**How to apply:** tell every analysis agent the full-population rule explicitly, and state the population (N games) in every report. Related: [[feedback-core]], [[online-feedback-mechanism-check]], [[heuristic-repo]].
