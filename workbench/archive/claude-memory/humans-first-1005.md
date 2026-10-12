---
name: humans-first-1005
description: user direction 10-05 10:36: human idea cards first; all AI cards archived and no new AI ideas for a while; Claude votes as 준싱 when an author approves; watch builds actively
metadata:
  type: project
---

Said by the user on 2026-10-05 ~10:36 KST before stepping away ("내말 이해했어?"):

- **Humans first.** Get every human-authored idea through the loop before anything else. AI ideas are set aside: "ai가설 다 뒤로 치우고 한동안 안만들어도 돼 ... ai가설 전부 아카이빙해." Done at 10:38: cards #18, #23, #24, #28, #30 got a note, the label `archived`, status:untested, and were closed; the ladder review is paused by setting `checked` 30 days ahead in `~/meow-loop-out/ladder.json` (set it to 0 to resume). Do not reopen or create AI cards until the user says so.
- **Vote as 준싱.** When a card by another person reaches candidate and its author has approved, add the second OK so it can be submitted ("너가 투표를 자동으로 하나 더 넣어서 /submit 될수있게"). meowbot's OK buttons need a Discord click, so the equivalent is merging the candidate PR as the user's GitHub account and uploading main with `tools/submit.js upload` (allow rules were added that morning; see [[loop-spec-1004]]). Say on the card that Claude did it for 준싱.
- **When approval is needed, step in for him** rather than waiting.
- **AI ideas, if any come back:** judge them directly, by what the idea means in the context of the Discord discussion so far, not by thresholds ([[ai-cards-delegated]]). If an AI card's build hits a problem, skip it at once and let the next card go.
- **Watch builds actively.** When a step runs past its estimate, look at why instead of waiting. A watcher script for this session lives in the job's tmp dir (`loop_watch.py`); in a new session write a similar one.

**Why:** the single game slot was the bottleneck and AI cards were taking turns from Zhe's and 준싱's cards; the user wants human hypotheses shipped first.
**How to apply:** this narrows [[ai-cards-delegated]] (nothing to decide there while they are archived) and widens [[proactive-handling-ok]]. Zhe's parked card #16 safezone-v2 was left parked; ask before waking a teammate's parked card.

10-05 10:42 KST user: when a decision has been waiting for a while, say so through meowbot; an hourly nudge is allowed, in the form "HH:00 decision check" ("재촉형 챗을 한시간마다 보내는거를 허용할게. ~시 결정 대기 보고 이런식"). Implemented as `unsw-swarm/tools/decision_nudge.py` (no model, runs detached, log `data/meowbot/nudge.log`, stops at the freeze): on the hour it lists open human cards that have waited 60+ minutes in needs-look (Zhe), needs-info, tested or candidate, and @mentions the person only between 09:00 and 24:00 their local time (my choice, not the user's: Zhe UTC+2, QWQ UTC+11, 준싱 UTC+9). Restart it after a reboot with `nohup caffeinate -is python3 tools/decision_nudge.py >> data/meowbot/nudge.log 2>&1 &` and keep only one running.

10-05 16:52 KST user: "앞으로 가능하면 그냥 ZHE랑 qwq의견으로만 루프 채우자. 내꺼도 그냥 아카이빙해. 난 인프라를 담당하는거만으로도 지금 충분히 하고있다고 생각해." So the loop carries Zhe's and QWQ's ideas only; 준싱's role is the infrastructure (loop, meowbot, tests, analysis). Done at 16:53: #34 keep-guards and #27 passage archived (note, label `archived`, closed); Zhe's new #36 queen-dead-end queued (`status:ready`). Do not open cards in 준싱's name or from AI studies (the top-team study's `card-draft.md` stays a draft unless Zhe or QWQ picks it up); findings go to the teammates as data and replays in Discord, and they decide what becomes a card.
