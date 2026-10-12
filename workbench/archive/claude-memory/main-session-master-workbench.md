---
name: main-session-master-workbench
description: "user rule 10-05: the main session is the master workbench; do not open hands-on work in it unless truly urgent, delegate to Codex or Claude subagents; carry this rule in every handover"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e3d433df-e6c2-41f6-81d4-738b9ea48abd
  modified: 2026-10-04T17:20:08.734Z
---

The main session (named "meow-main02" on 2026-10-05) directs and decides; it does not do hands-on work itself unless it is truly urgent. Simple or routine work (code edits, tool changes, replay counting, log digging, test runs) goes to a Codex subagent or a Claude subagent with a tight brief, and only the conclusion comes back here.

**Why:** The user said on 2026-10-05 ~02:20 KST, after I edited the loop runner, smoke.py and pair_report.py inline: "이 세션에서 바로 작업 열지 마. 진짜 급한거 아니면." The session's context is managed strictly; inline work makes every later turn re-read it, so token use snowballs for about a day. The main session must survive handovers with no loss of work, so it has to stay small. A new session was planned for the night of 10-05.

**How to apply:** Before touching files or running multi-step investigations here, ask "is this urgent enough that a delegate round-trip costs more than doing it?" (my reading of "urgent": a live problem such as the wrong bot active on the server or the loop blocked). If not, delegate. Keep status checks, decisions, Discord drafts and short verifications here. Every handover document must state this rule explicitly. Related: [[claude-usage-budget]], [[codex-outsourcing]], [[handover-1006]], [[loop-first]].

## Model and effort tiers (table confirmed by the user on 2026-10-05 02:24 KST: "어 맞아")
Put this table in every handover document as is; the 10-05 handover shrank it to one line and the session then broke it.

| Work | Who | Model, effort |
|---|---|---|
| Main session (directing, deciding) | Claude | Opus 5.5, high or above |
| Real thinking steps (hypotheses, design review, verdicts, implementation) | Claude | Opus 5.5 high; xhigh/max allowed since 10-04 |
| Light steps (status summaries, triage text, translation) | Claude | Sonnet, medium |
| Plain watching and waiting | script | no model |
| Mechanical work (scripts, wiring, formatting) | Codex | gpt-6.1-sol |
| Counting and tallies from replays or logs when a reference script exists (behaviour counts after an online test) | Codex | gpt-6.1-sol, low effort |
| Work needing judgment (analysis, verdict drafts, tricky design) | Codex | gpt-6-astra, effort high |
| Simple checks (smoke tests, file checks, reruns) | Codex | effort low |
| Deep research only | Claude | Sonnet 5.5, max (changed by the user 10-05 02:28; was Codex max) |
| Ordinary, moderate research | Claude | just use the research skill, no special model or effort |

Also: broad-but-shallow work always goes to Codex; Claude writes the brief, verifies, integrates. Claude subagents are bounded, few, and stopped after their report; pass a `model` when spawning one (an Agent call without it inherits Opus). Ask about the remaining weekly budget before spawning Opus agents. Codex is always called through `unsw-swarm/tools/cx.sh` (Plus account first, then the second account).

What went wrong on 10-05 (facts): loop runner, smoke.py and pair_report.py were edited inline in the main session, and two general-purpose subagents (replay counting, test scheduling) were spawned with no model, so both ran on Opus.

User rule 2026-10-05 02:28 KST: never run gpt-6-astra at max effort ("성능도 그정도 아닌데 너무 토큰 나댐"). astra stays at high at most. When research is needed, use Sonnet 5.5 at max instead. This replaces the older "Codex effort max for deep research" line in [[codex-outsourcing]].
Clarified 02:31: the Sonnet 5.5 max line is for DEEP research only; moderate research just uses the research skill.

10-05 04:42 KST user, angry: I had sent two replay-count jobs (#30, #23) to gpt-6-astra at high. "행동 집계같은 간단한거는 상식적으로 더 싼 모델을 시켜야지. 그래야 더 빠르고. 아스트라는 무겁고 똑똑한거잖아. 호출하기전에 성격을 생각을 하면서 해라. 이번 작업은 두뇌가 필요한거야?" Rule: before every model call ask whether the task needs a brain. Counting with a clear spec does not; astra is for work that needs judgment (deciding what to measure, reading results, design).
