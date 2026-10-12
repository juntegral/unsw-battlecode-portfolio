---
name: same-hour-baseline
description: online comparisons need a baseline from the same hours; opponents change their bots (test4 did overnight on 10-06) and a day-old baseline gave a wrong verdict
metadata:
  type: project
---
Fact (2026-10-06): I held the merge of #36 because v31 + #36 scored 4/15 against test4 while v31's baseline was 8/15. The baseline was from the evening before; test4 had changed its bot overnight (rating 2109 to 2215). Re-run the same hour, plain v31 scored 2/15. Zhe spotted it ("looks like they updated their version").

**Why:** opponents upload new bots at any time, so wins against a named team are only comparable when both sides of the comparison played it in the same hours.

**How to apply:** before a verdict that rests on an online comparison, check the opponent's rating/recent record for a jump (`node tools/online.js team <id>`) and, if the baseline is more than a few hours old, re-run the live bot first (`LIVE_ONLY=1 run-pair.sh <label> - "more live bot games" <opps>`). Say in the table when each side was played. Also a cost to weigh (my observation that night, not a user rule): every test swaps the active bot for ~20 min and other teams' ranked challenges then hit the test bot; rating went 1883 to 1841 during a night of tests. Related: [[online-feedback-mechanism-check]], [[zhe-intuition]].

10-06 20:55 KST correction, read from the server API (`online.js submissions --json`): the rating is stored per submission, and the team rating shown is the active submission's. Test uploads carry their own rating, so ranked losses during a swap hit the test bot's number, not the main bot's; the team number comes back when the old submission is activated again (v31 kept 1881 through all of 10-06 while test bots sat at 1822~1875). What a swap still costs is the allowance and whatever ranked games the test bot plays for us. A new submission also moves about 24~33 per ranked battle at first, against 2~10 for one with hundreds of games.

10-06 21:00 KST, from the same API: a new upload seems to start at the rating of the submission that is active at upload time (v38 never played and sits at 1841, uploaded while v36 was live at 1841; v39/v40 at 1854 under v31 at about 1853). One exception seen: v47, a byte-identical re-upload of v44, started at v44's 1843 although v31 was live at 1881. One case, not confirmed. The user's idea is to test on throwaway versions, raise the main one, then re-upload the tested code so it starts higher; on this evidence the re-upload must not be identical to the low-rated copy.

**2026-10-08 19:59 KST update (user decision, announced in #meow as jun's):** "지금부터는 그냥 확실한 기존 메인과 대조를 위한 테스트 대전 하지마. 직관적으로 성장했는지 대전을 통해서만 확인해. 티켓의 가치가 매우 높으니까." From now on no baseline games online at all (no live-bot or old-main replays on the same maps; no `BASELINE=1`, no `LIVE_ONLY=1` runs). A test plays the new bot only, and the change is judged from its own games: did the mechanism fire, did the bot grow. This supersedes the same-hour-baseline requirement above for the rest of the run-up to 2026-10-09 15:00 KST.
