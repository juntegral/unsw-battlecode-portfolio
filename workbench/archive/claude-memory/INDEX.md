# Index of the standing rules

One rule per file in this folder, each with why it exists and how to apply it. [`MEMORY.md`](MEMORY.md) is the
original flat list and is unchanged. This page sorts the same 55 files into three groups and by date, and copies
each one-line description from `MEMORY.md` word for word. The groups are an editorial sort made for this index;
a rule can serve more than one purpose, and ambiguous ones are under operating rules. Dates are the day the rule or
decision was given (KST, 2026). A few private rule files cited in the write-up are not published.

How these rules held up, with the incident behind each: [HOW-I-USE-AI.md](../../../docs/HOW-I-USE-AI.md).

## 1. Tightening rules: verification, people first, permission

| Date | Rule | Description (from MEMORY.md) |
|---|---|---|
| 09-29 | [Past judgments ≠ direction](past-judgments-not-direction.md) | user principle: carry facts not verdicts between waves; independent criteria from hypothesis only; enforce mechanically |
| 09-30 | [Feedback is the core](feedback-core.md) | after every test, deep replay analysis vs baseline; feedback matters more than results |
| 09-30 | [Online feedback = mechanism check](online-feedback-mechanism-check.md) | feedback from online behaviour (did each mechanism fire and work vs elite); no win-rate gating; local proxy games = mechanism checks only, "numbers are poison" |
| 09-30 | [Analysis population = all games](analysis-population-all-games.md) | every per-hypothesis large-scale analysis uses all accumulated top games + all our elite sets; no samples; don't save tokens |
| 10-01 | [Upload-only rule](upload-only-rule.md) | online submissions: upload only, never auto-revert; rollback is the user's call; after the 10-01 reset, first upload as late as possible with a complete build |
| 10-03 | [Check in first](check-in-first.md) | user rule 10-03: lightly confirm before each step; one team; propose direction, don't pre-assign |
| 10-03 | [No fixed-map optimisation](no-fixed-map-optimization.md) | user hard rule 10-03: qualifier is unseen custom maps; no per-map logic, judge on held-out sets; closes Oct 9 17:00 AEDT = 15:00 KST |
| 10-03 | [Known-map-preserving rule](known-map-preserving-rule.md) | user rule 10-03: universal logic: refactors keep old-10 maps replay-identical (real fixes: no big regression), changes only uncovered sizes/shapes, orientation-invariant; verify with metamorphic map tests |
| 10-05 | [Humans first 10-05](humans-first-1005.md) | user direction: loop carries Zhe's and QWQ's ideas only (AI cards and 준싱's own cards archived, 16:52 update); 준싱 = infrastructure; Claude votes as 준싱 once an author approves, watch builds actively |
| 10-06 | [Evidence-first replies](evidence-first-replies.md) | user feedback 10-06: the big-map reply form worked; for "why" questions gather evidence from several sources first, split measured from inferred |

## 2. Loosening rules: autonomy, intuition, spending

The grants of 10-07 to 10-09 and what they cost are in [LAST-TWO-DAYS.md](../../../docs/LAST-TWO-DAYS.md).

| Date | Rule | Description (from MEMORY.md) |
|---|---|---|
| 10-05 | [AI cards delegated](ai-cards-delegated.md) | user 10-05: on by:ai cards Claude answers and decides itself to keep them moving; candidate approval and shipping still need a human |
| 10-06 | [Act on context](act-on-context.md) | user rule 10-06: clear teammate request → do it, report after; no magic words or slash syntax; one plain confirmation at most; user holds and classifier refusals still stand |
| 10-07 | [Autonomy within teammate hypotheses](autonomy-within-teammate-hypotheses.md) | user grant 10-07: lead and drive loop + tests actively without asking, only inside Zhe/QWQ hypotheses; they are the brake; merges still need the author (see [LAST-TWO-DAYS](../../../docs/LAST-TWO-DAYS.md)) |
| 10-08 | [Full autonomy 10-08](full-autonomy-1008.md) | user grant ~19:00: solo project, decide everything yourself; only protocol is thinking → Claude, rest → Codex; verify before stating ("no more mistakes"); classifier denials still go to him (see [LAST-TWO-DAYS](../../../docs/LAST-TWO-DAYS.md)) |
| 10-08 | [Same-hour baseline](same-hour-baseline.md) | superseded 10-08 19:59: NO baseline games online any more (tickets too valuable); tests play the new bot only, judged from its own games; older same-hour rule kept in the file (see [LAST-TWO-DAYS](../../../docs/LAST-TWO-DAYS.md)) |
| 10-08 | [One model live 10-08](one-model-live-1008.md) | user decision 22:19: one combined model live, improve its weaknesses from its own games by intuition; no rollback to the old bot, fix the switch that fails instead (v62 only if the bot is broken) (see [LAST-TWO-DAYS](../../../docs/LAST-TWO-DAYS.md)) |
| 10-09 | [Active means spend](active-means-spend.md) | user 10-09: "적극적" = call models as needed, gain before risk calculation; Codex on gpt-6.1-sol; unseen-map readiness is a must (see [LAST-TWO-DAYS](../../../docs/LAST-TWO-DAYS.md)) |

## 3. Operating rules: cost, handover, Discord and GitHub style, team and loop setup

| Date | Rule | Description (from MEMORY.md) |
|---|---|---|
| 09-30 | [Codex outsourcing](codex-outsourcing.md) | build grind and counting go to Codex (gpt-6.1-sol); since 10-09 00:49 thinking may also go to Codex gpt-6-astra, ~8 in parallel, when Claude capacity is short; Codex cannot play games; verify before acting |
| 10-01 | [Subagent cleanup](subagent-cleanup.md) | after processing a finished subagent's report, TaskStop it so the user's panel stays tidy |
| 10-01 | [Report in Korean](report-in-korean.md) | user rule 10-01: all reports/status updates to the user in Korean (agent briefs/code may stay English) |
| 10-01 | [Ranked battles not ours](ranked-battles-not-ours.md) | battles the user didn't mention are other teams' requests; ticket estimate counts only our ledger (team order random since 9/28) |
| 10-01 | [Qualifier timeline](qualifier-timeline.md) | qualifier submissions close 2026-10-09 15:00 KST; bo7 on UNSEEN maps; per-map tables won't apply (earlier 'Jan 10' was wrong) |
| 10-01 | [Slay Queen rules](slay-queen-rules.md) | 10-01 rule change: longer queen (id 0/1) wins, dead queen = 0; ceil(L/4) free steps; ladder reset; v1.8 plan |
| 10-01 | [Brief code comments](code-comments-brief.md) | user rule 10-01: comments short; rationale goes to VERSION.md/DECISIONS, not code |
| 10-02 | [Meow team repo](meow-team-repo.md) | team 1119 "meow": github.com/forrest-gan2005/battlecode (C-- = QWQ) cloned to 개인 프로젝트/battlecode; gh + key symlink wired 10-02; new repo first; Discord #meow mirrored via unsw-swarm/tools/discord_sync.py |
| 10-03 | [Discord first](discord-first.md) | user core rule 10-03: run unsw-swarm/tools/team_watch.py (Discord + GitHub) before every task, background --wait watcher; report lightly; in battlecode/CLAUDE.local.md |
| 10-03 | [Discord message style](discord-msg-style.md) | user rule: English drafts with Korean translation; short, no colons; plain code block; numbers that compare things go in a small monospace table (10-05) |
| 10-03 | [Old docs on request](old-docs-on-request.md) | user rule 10-03: ignore old-team docs/principles (PHILOSOPHY, EVAL, wave rules) unless the user asks; reason from current team context |
| 10-03 | [GitHub in English](github-english.md) | user rule 10-03: all GitHub/team-shareable material in English; Korean only in local chat |
| 10-03 | [Overnight loop 10-03](overnight-loop-1003.md) | ~/meow-loop runner (Opus high, local, no uploads); report in Korean when the user says "일어났어" |
| 10-03 | [meowbot](meowbot.md) | Discord bridge running on the Mac since 10-03: PR/idea posts + candidate approve buttons; uploads mocked until team OK |
| 10-03 | [Loop first](loop-first.md) | user rule 10-03: experiments run as board loops (runner waits, Claude only for short steps), not long-lived agents |
| 10-03 | [Discord promises](discord-promises.md) | user rule 10-03: every 'I'll…' posted in Discord is kept or explicitly corrected; ledger unsw-swarm/docs/PROMISES.md |
| 10-03 | [GitHub readability](github-readability.md) | user rule 10-03: GitHub posts open with a 3-line plain summary (tried / worked? / who decides), jargon glossed, details after |
| 10-04 | [Loop spec 10-04](loop-spec-1004.md) | agreed loop design: label state machine, clarify/look steps, approvals, freeze 10-08 20:00 KST |
| 10-04 | [Top-team study 10-04](top-team-study-1004.md) | overnight background study of the rank-1 team's games vs 2000+ teams; deliverables in unsw-swarm/data/analysis/top1/ by 10-05 morning |
| 10-05 | [Loop status first](loop-status-first.md) | user rule 10-05: every status report opens with the card loop (per card), then Discord etc.; "상황 확인" = Discord + loop status check |
| 10-05 | [Main session = master workbench](main-session-master-workbench.md) | user rule 10-05: no hands-on work in the main session unless truly urgent; delegate to Codex/Claude subagents; state this in every handover |
| 10-05 | [Bottleneck notice](bottleneck-notice.md) | user rule 10-05: confirmed bottlenecks we cannot fix ourselves get a ⚠️ important meowbot notice in #meow, same format as the online-test one |
| 10-05 | [Morning report 10-05](morning-report-1005.md) | trigger "아침 보고 진행해줘": report everything that ran overnight from 04:25 KST (loop, AI card decisions, online tests, top-team study) |
| 10-06 | [Handover 10-06](handover-1006.md) | new session: read unsw-swarm/docs/HANDOVER-2026-10-06.md first (main vs server differ on purpose, open decisions, watchers to start, rules) |
| 10-06 | [Bot speaks when mentioned](bot-speaks-when-mentioned.md) | user rule 10-06: never join Zhe and QWQ's conversations; answer a teammate in #meow only on an @meowbot mention or an /answer |
| 10-06 | [Proxy answers](proxy-answers.md) | user rule 10-06: any teammate may answer loop questions on another's card (author away, queue must move); author binding only at merge |
| 10-06 | [dev1 not informative](dev1-not-informative.md) | Zhe 10-06: dev test 1 (~2417) is too strong to separate our builds; default online tests to normal-team opponents |
| 10-06 | [Handover semi-auto](handover-semi-auto.md) | user decision 10-06: on "인계해" Claude writes the handover doc, starts the next session and reports; the new session takes over and stops the old one |
| 10-06 | [Elo defence](elo-defence.md) | user rule 10-06: when the live bot is put back, keep the best-rated copy of the intended code live; simple, no ceremony; 10-07 update: two copies run as a ratchet (park the higher, play the lower) |
| 10-07 | [meowbot answers in main](meowbot-answers-in-main.md) | user rule 10-07 03:2x: answers to teammates via meowbot are worked in the main session, no subagents (token saving); user will tell teammates to wait; keep context lean with script → file → read summary; confirm with a rough size before spawning subagents |
| 10-07 | [Ladder info is shared](ladder-info-shared.md) | user rule 10-07: jun runs the ladder analysis, but facts from it that bear on a teammate's question or card go to #meow |
| 10-07 | [Session state memo](session-state-memo.md) | user-agreed 10-07: keep unsw-swarm/docs/SESSION-STATE.md, update before every /compact or handover, re-read right after; after compaction reopen files before stating facts |
| 10-07 | [Handover 10-07 evening](handover-1007b.md) | new session: read unsw-swarm/docs/HANDOVER-2026-10-07b.md first (autonomous project, end conditions, model split, loop state) |
| 10-08 | [Effort high only](effort-high-only.md) | user rule 10-08: no xhigh anywhere; loop builds, analysts and subagents at high at most |
| 10-08 | [Handover 10-08](handover-1008.md) | new session: read unsw-swarm/docs/HANDOVER-2026-10-08.md first (live v62, switch list, workbench, token-saving rules, final-day schedule) |
| 10-09 | [Discord desk](discord-desk.md) | 10-09: Sonnet session meow-desk owns #meow talk and the mention/jun-DM watchers; passes work to main via unsw-swarm/data/guide/desk-inbox.txt; rules in docs/DISCORD-DESK.md |
| 10-09 | [Handover 10-09](handover-1009.md) | new session: read unsw-swarm/docs/HANDOVER-2026-10-09.md first (live one5, one-model loop, desk owns Discord, Astra analysts, freeze 09:00, deadline 15:00 KST) |
| 10-09 | [Weak-loss rule](weak-loss-rule.md) | user 10-09: any game lost to a team rated 100+ below us → find the cause and fix it; tools/weak_watch.py automates detection + analyst |

Provenance: compiled by an AI session under my direction from the records linked on this page; quotes are verbatim.
