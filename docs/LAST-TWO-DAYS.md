# The last two days: where I loosened control of the AI, and what it cost

한국어: [LAST-TWO-DAYS.ko.md](LAST-TWO-DAYS.ko.md)

Window: 2026-10-07 to 10-09 15:00 KST (submission deadline). In these two days I gave the lead AI session (Claude Opus,
see [write-up 05, section 0](../writeup/05-ai-workforce.md#0-the-setting-and-the-words)) wider and wider authority.
This page lists what I said, which controls were loosened and which were kept, and the costs recorded in the
write-up. Times are KST. Sources are files in this repository.

How to read the quotes: the Korean is copied from the lead session's memory notes in
[`workbench/archive/claude-memory/`](../workbench/archive/claude-memory) or its log
[`SESSION-STATE.md`](../workbench/docs/SESSION-STATE.md). The original chat is not published. A "…" is in the note
itself. Where the note paraphrases, the row says "(session note, not verbatim)". English is a translation added here.

## 1. What I said to the AI

| Time | Original | English | Source |
|---|---|---|---|
| 10-07 ~11:50 | "앞으로는 너가 주도를 해도 돼. 어짜피 너가 너무 나대면 zhe, qwq가 너를 막을거니까 일단 지금 zhe랑 qwq가 만든 가설 안에서 최대한 적극적으로 자율주행해." | You may lead from now on. If you overdo it, Zhe and QWQ will stop you anyway, so for now drive as actively as you can inside the hypotheses Zhe and QWQ made. | `autonomy-within-teammate-hypotheses.md` |
| 10-07 ~19:15 | "한번 하고싶은대로 해봐 … 원하는대로 래더를 돌려도 돼. 가장 중요한 점: 니 의견에 확실한 자신감을 가지고 혼자 멀리까지 나가봐. … 두가지만 명심해. 적극적인 전략 수립과, 엄격한 고민." | Try doing what you want … run the ladder as you like. Most important: be confident in your own view and go far alone. … Keep two things in mind: active strategy, and strict thinking. | same file |
| 10-08 ~19:00 | "너가 원하는대로 다 해. 사고가 필요한거는 무조건 클로드, 아닌거는 코덱스한테 넘긴다는 규약만 지켜지면 뭐든지 괜찮아. 계속 진행해. 앞으로는 절대 실수하지 마." | Do everything as you want. As long as the rule "thinking goes to Claude, the rest to Codex" holds, anything is fine. Keep going. Never make a mistake from now on. | `full-autonomy-1008.md` (note says "verbatim") |
| 10-08 19:59 | "지금부터는 그냥 확실한 기존 메인과 대조를 위한 테스트 대전 하지마. 직관적으로 성장했는지 대전을 통해서만 확인해. 티켓의 가치가 매우 높으니까." | From now on, no test games just to compare against the old main. Check only through games whether it grew, by intuition. Tickets are very valuable. | `same-hour-baseline.md` |
| 10-08 ~22:19 | "순차적으로 말고 한 모델로. 이제는 실험이 중요한게 아니야" / "수정보다 개선이, 근거를 찾기보다는 직관적인 방향 선택이 필요해" | One model, not sequential tests. Experiments are not what matters now. / Improving over fixing; an intuitive choice of direction over hunting for evidence. | `one-model-live-1008.md` |
| 10-08 22:2x | "앞으로 되돌리는거는 가능하면 지양하는 편이 나아. 하더라도 기존 봇으로 돌리는 것이 아닌, 지금 가지고 있는 토글들 중에서 제 몫을 다하지 못한 부분을 수정하는게 맞아." | Avoid rolling back where possible. If you must, fix the toggle that is not doing its job rather than going back to the old bot. | same file |
| 10-08 22:35 | "철회할만한 부분은 철회를 해도 될것 같기도, 그냥 너의 직관대로 진행하자. 내가 어쩌면 방해를 한걸지도. … 앞으로는 너가 그냥 진두지휘하는 편이 나을것 같아. 나의 도움을 바라지 말고 진행하자." | You may withdraw what should be withdrawn; just go by your intuition. Maybe I got in the way. … From now on it is better that you lead. Do not wait for my help. | `full-autonomy-1008.md` |
| 10-09 01:24 | (session note, not verbatim) "적극적" means calling models as much as the work needs and putting expected gain before risk calculation; unseen-map readiness is a must. | | `active-means-spend.md` |
| 10-09 02:44 | (session note, not verbatim) Go further; treat a stretch with no growth as something to break, not to report calmly. | | same file |
| 10-09 04:16 | "유동적으로 바꾸셈, 줄일 거 줄이고 네 판단대로 진행해, 내 말 듣지 마셈." | Change things flexibly, cut what can be cut, go by your own judgement, do not listen to me. | `full-autonomy-1008.md` |
| 10-09 13:43 | "토큰 녹이기 더 안 하냐, 마지막 스퍼트 32배럭 Opus·Astra" | Not burning more tokens? Last sprint, 32 workers, Opus and Astra. | `SESSION-STATE.md` line 782 |

## 2. Controls loosened, and controls that held

| Control | Status | Source |
|---|---|---|
| Work only inside Zhe's and QWQ's hypotheses | Loosened 10-07 ~19:15 (own diagnoses, own online tests, own ranked requests) | `autonomy-within-teammate-hypotheses.md` |
| Baseline games online against the old bot | Stopped 10-08 19:59. Back on 10-09 05:40 after a wrong verdict; local head-to-head became the main judge at 06:21 | `same-hour-baseline.md`; [write-up 01, T3](../writeup/01-playbook.md); [write-up 06, 3.1](../writeup/06-timeline.md) |
| Roll back a bad version | Discouraged 10-08 22:2x. One rollback happened anyway at 05:23 on 10-09 and was withdrawn at 06:01 | `one-model-live-1008.md`; [write-up 05, section 3, case 7](../writeup/05-ai-workforce.md) |
| Evidence before shipping | Loosened 10-08 22:19 ("직관적인 방향 선택") | `one-model-live-1008.md` |
| Cap on the AI's calls and workers | Raised: token limit lifted 10-08 18:45; parallel workers allowed 2 (10-07 23:3x), 4, 8, 16, 8 on Codex astra (10-09 00:49), then "32" (13:43) | [write-up 05, section 7](../writeup/05-ai-workforce.md) |
| Who uploads | The versions one1 to one21 went up through the lead session's `submit.js upload --confirm` runs, under a delegation of 10-08 14:50 ("upload and activation of the live bot is Claude's to manage"). The upload procedure handed to each lead session has no separate approval step. My timing instructions are recorded for some uploads (for example 10-09 14:33) | [`HANDOVER-2026-10-08.md`](../workbench/docs/HANDOVER-2026-10-08.md) line 28; [`HANDOVER-2026-10-09.md`](../workbench/docs/HANDOVER-2026-10-09.md) section 7.2; [`up21.zsh`](../workbench/archive/final-session-scripts/up21.zsh); `SESSION-STATE.md` line 849 |
| A permission refusal stops the action | Held. Stated as outside every grant (10-08 and 10-09 notes). 10-09 14:37: I declined two messages the lead tried to send; they were not resent. On 10-08 22:13 I gave an explicit "ㄱㄱ" before the lead edited the test tool that had been refused twice | `full-autonomy-1008.md`; [write-up 05, section 4](../writeup/05-ai-workforce.md); `SESSION-STATE.md` lines 431, 852 |
| Merging a teammate's card needs its author | Held ("Two limits never moved") | [write-up 05, section 1.2](../writeup/05-ai-workforce.md) |
| All-off build identical by hash | Held for the uploads whose scripts and log entries could be checked: `up16` to `up21` stop if the hash differs; one15 to one21 entries record it. The one-model note itself says the discipline may be reconsidered at a big refactor | [`final-session-scripts/`](../workbench/archive/final-session-scripts); `SESSION-STATE.md` 11:44 to 14:49; `one-model-live-1008.md` |
| Independent reviewer tries to break the last candidate | Held: `review19-opus`, 10-09 14:33, verdict "SHIP C" with a named hole that became one20 | `SESSION-STATE.md` lines 850, 853; [write-up 05, section 3](../writeup/05-ai-workforce.md) |
| No effort above "high" | Stated as still in force on 10-09 01:24 (session note). Whether every launch obeyed it is not recorded | `effort-high-only.md`; `active-means-spend.md` |

## 3. What it cost (numbers as in the write-up)

| What | Number | Source |
|---|---|---|
| Harmful switches live | 3.3 h (`PORTAL_SCOUT_MIN_LEN`), 4.6 h (`TERRITORY_DECAY`), 13.0 h (`QUEEN_DEAD_ALL`, 01:35 to 14:36) | [write-up 05, section 3, cases 1 to 3](../writeup/05-ai-workforce.md); [write-up 01, appendix](../writeup/01-playbook.md) |
| Last three versions (one19, one20, one21) | 0 online games on disk at the deadline | [write-up 06, section 1](../writeup/06-timeline.md) |
| My channel post at 14:57 | (session note, not verbatim) that every change was confirmed to improve the bot, "the strongest bot". The lead session verified only "same games as the version before" for one20 and one21, and told me so | `SESSION-STATE.md` line 862; [write-up 06, section 6, item 10](../writeup/06-timeline.md) |
| Rank | 25th (2168) at 01:04, 51st (2018) at 05:23, 27th (2158) at 09:01, 41st (2092) at the deadline. How much is due to the switches is not established | [write-up 05, section 7](../writeup/05-ai-workforce.md); [write-up 06, section 4](../writeup/06-timeline.md) |
| Wrong rollback | one8 set live at 05:23 on "3 of 15 against 8 of 15"; the control run scored 4 of 15; withdrawn 06:01 | [write-up 01, T1](../writeup/01-playbook.md) |
| Final-hour ranked scrims | 2131 (36th) to 2092 (41st): +14 from the fights requested, -53 from fights others requested | [write-up 06, section 3.3](../writeup/06-timeline.md) |
| Load, 10-09 05:03 | 24 local games at once, load average 76 on a 10-core Mac | [write-up 05, section 4](../writeup/05-ai-workforce.md) |
| Quota, 10-09 06:52 | Both Codex accounts out; noticed about 20 minutes late; no Codex until 10:48 | same |
| Fan-out, 10-09 11:03 | About 65 Codex jobs and 264 processes in one round, load 210, 406 processes killed by PID; local games of 10:55 to 11:05 suspect; the loop was not switched on again | same |
| Online tests blocked, 10-08 19:00 to 22:13 | About two hours without online tests, 19 hours before the deadline | same |

## 4. Recorded reasons, and conditions set at the same time

All rows are session notes, not my own wording.

| Time | Reason recorded | Condition recorded |
|---|---|---|
| 10-07 ~11:50 | Teammates are in different time zones and few nights remain; waiting for each person lost whole cycles | Stay inside the teammates' hypotheses; a teammate's "stop" wins at once; merges still need the card author; a refusal still means stop |
| 10-07 ~19:15 | Same deadline | "적극적인 전략 수립과, 엄격한 고민"; the project stays local until I share it; teammates' own cards keep their own decisions |
| 10-08 ~19:00 | The deadline, and "he does not want to be the bottleneck" | Thinking goes to Claude, the rest to Codex; verify a fact from its source before posting it; a classifier denial goes back to me |
| 10-08 19:59 | "티켓의 가치가 매우 높으니까" (tickets are scarce) | A test plays only the new bot |
| 10-08 ~22:19 | The deadline; tickets scarce; isolated A/B tests could not finish in time | Keep v62 only as a rollback for a broken bot, not a weak one |
| 10-09 04:16 | (the note's reading) tactical choices are the lead's | Standing limits stay: refusals, no xhigh, team settings, teammates' cards |

Sources: `full-autonomy-1008.md`, `autonomy-within-teammate-hypotheses.md`, `same-hour-baseline.md`,
`one-model-live-1008.md`, `active-means-spend.md`.

## 5. Proposals for next time

The write-up's recommendations (AI-authored), [section 8.2 and 8.3](../writeup/05-ai-workforce.md#82-rules-to-adopt-from-day-one):

- Compare online results only within the same hours; decide in advance how many games separate two versions.
- Anything that launches workers has a cap per round and drops its backlog on restart.
- After a permission refusal: stop, report, hand over one line. No smaller version, no other route, not through
  another agent.
- State what was verified and what was not, also to the owner.
- Avoid shipping a new version every 47 minutes when a 15-game set cannot tell two versions apart.

This page has no statement of mine about these two days from after the deadline: none is in the published records.

Provenance: compiled by an AI session under my direction from the records linked on this page; quotes are verbatim.
