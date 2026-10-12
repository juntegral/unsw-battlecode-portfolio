# Timeline and results: what happened when, from the first day to the knockout

Written 2026-10-10. This chapter is the dated record that the other chapters can be read against. It states facts with
the file they come from; where a number is my own arithmetic or reading, it says so.

**Times are KST (UTC+9) unless a source says otherwise.** Teammates' zones: QWQ on AEDT (KST+2), Zhe on
CEST (KST-7). Three logs are in UTC and were converted by me: `data/online/REMOTE-LOG.md` (add 9 hours),
`data/online/requests.jsonl` and `data/online/submissions.jsonl` (the `at` field is UTC). `data/online/park/log.jsonl`
carries a +09:00 offset already.

Path prefixes: `S` = the tools and docs repo (`unsw-swarm`), `B` = the team bot repo (`battlecode`, branch with the final
bot), `R` = the local game rig. Paths below are relative to `S` unless they start with `B/`.

How the contest worked, in four lines, so the dates make sense. Teams upload a bot (a program that plays a snake-like
game of "dragons" eating "pearls" on a grid, one program instance per dragon). A ladder runs ranked 5-game battles; each
uploaded version ("submission") has its own rating and the team's rating is the active submission's
(`rules/elo.md`). Submissions closed 2026-10-09 15:00 KST. After that a seeded single-elimination bracket, best of 7 on
maps nobody had seen, decided who reached the finals (`archive/claude-memory/qualifier-timeline.md`).

---

## 1. One-page summary

**Answer first.** The team (jun, Zhe, QWQ; team 1119 "meow") formed on 2026-10-02, worked on a shared bot for seven
days, uploaded its final bot "one21" (submission 21857) at 14:49:38 on 10-09, about ten minutes before the deadline, stood
41st at 2092 when submissions closed, and was seeded 39th. The result of the bracket match(es) is not in any file in
this repository. Not recorded; jun reports a quarterfinal exit on 2026-10-10. See section 6, item 1 for what the chat
mirror does and does not say.

**Teams and people**

| When | Team | Who | Source |
|---|---|---|---|
| Until 10-02 | "Teto, run!", id 583 | jun, with Claude doing analysis and building; old repos `unsw-heuristic` then `unsw-swarm` | `docs/STATE.md`, `DECISIONS.md` |
| 10-02 evening | jun changed teams: left 583 and agreed with "C--" (team 852, a C++ solo team that was rank 30 at 1894 on 10-01 morning) to form a new team | jun, QWQ | private notes |
| From 10-02 22:48 | team 1119 "meow": rank 32, rating 1800, 3 members, a bot already active | jun, QWQ, Zhe | private notes; team key arrived 22:48 |

- jun: infrastructure, the card loop, tools, the online test harness, and from 10-07 a Claude-driven "aggressive play"
  switch project that produced most of the final bot.
- QWQ (GitHub forrest-gan2005, AEDT): author of the base bot and owner of the team repo (first commit 2026-09-25
  17:23 +1000 in `B`).
- Zhe (GitHub zhex0121, CEST): strategy and intuition, most of the idea cards, sets many test requests.
- The team repo was `github.com/forrest-gan2005/battlecode`; Discord channel #meow (mirror not published) was
  connected 10-02 about 23:55.

**Phases of the work**

| # | Dates | What it was |
|---|---|---|
| 0 | to 10-02 | Old team. Sprint event 10-01: lost round 1 (3-4). Same evening the organisers changed the rules ("Slay Queen", engine 1.2.3) and reset the ladder to 1500. |
| 1 | 10-02 to 10-04 | New team: audit of the bot, issue board, engine/maps to 1.2.7, meowbot and a GitHub-label "card loop" built (first paired online tests 10-04 17:08). |
| 2 | 10-04 to 10-07 | Card loop: one idea per card, built behind an off-by-default switch, tested online 15 games at a time. Live bot moved v61, stride, v22, v31, v36, v47. Rating 1800 to about 1950. |
| 3 | 10-07 evening to 10-08 22:19 | jun's switch project: aggressive-play switches tested online against the old main (MAIN 21/90 against B7 23/60), live as "v62" from 10-08 14:55. Rating 1960 to about 2080. |
| 4 | 10-08 22:19 to 10-09 09:00 | "One model" rule: one combined bot live, improve it forward only. Uploads one1 to one13 (13 uploads in 9.5 hours). |
| 5 | 10-09 09:00 to 15:00 | Announced change freeze at 09:00, then eight more uploads (one14 to one21), mostly fixes for failures found on unseen-style maps, plus ranked "scrims" for seeding from 13:48. |

**Result in numbers (measured)**

- Active at the deadline: submission 21857 "one21", rank 41, rating 2092 (`docs/SESSION-STATE.md` line 861;
  `data/online/park/log.jsonl` last row 14:56:28 shows 2092).
- Peak rating of the last day: 2202 (23rd) at 13:50 after a 4-1 win; 2092 (41st) at 14:37 (section 4).
- 84 uploads (including test copies) were recorded by our tool between 10-04 17:28 and 10-09 14:49
  (`data/online/submissions.jsonl`, counted by me).
- Ranked battles our collector downloaded from 10-08 22:41 to the deadline: 69, of which we won 33 and lost 36; plus
  62 unranked test battles, 19 won and 43 lost (`data/online/live-one1/index.txt`, counted by me; the unranked ones
  were our own test games against named teams).
- Final seed 39 (jun, Discord 10-09 19:19).

**What the dates show (my reading, offered as lessons)**

1. The last day was a series of 21 new versions in 16 hours 19 minutes (10-08 22:30 to 10-09 14:49), about one every
   46 minutes. A
   15-game online set cannot separate versions: the same bot scored 8/15 and 4/15 against the same opponent two hours
   apart (10-09 03:43 and 05:40). Late versions were therefore chosen by local head-to-head and by whether a named
   mechanism fired, not by wins.
2. The three last uploads (one19, one20, one21) went live with no online games of their own on disk
   (`docs/SESSION-STATE.md` line 861 and 863). They were checked only by local games identical to the previous
   version. That is a fact about the record, not a verdict on the bot.
3. A deadline-day bug can hide behind averages: one12 and one13 starved portal maps for about 3 hours (live 07:08 to
   10:24, found then) because versions were not compared map by map
   (`docs/SESSION-STATE.md` line 696). The per-map regression table was only built afterwards (started 10:48).
4. Tool and access limits cost real hours: online tests were blocked from 19:00 to 22:13 on 10-08, and both analysis
   accounts hit usage limits 07:14 to 10:48 on 10-09 (section 3).
5. Final-hour ranked scrims were net negative for the displayed rating: from 2131 (36th) before to 2092 (41st) at the
   deadline, with +14 from the fights we asked for and -53 from fights other teams asked for (section 3.3).

---

## 2. Day-by-day table

The earliest dated entry in the files I was given is 2026-09-25 (rules and engine release; QWQ's repo). jun's own work
before 10-01 lived in the old repos (`unsw-heuristic`, 428 commits, now only on a private GitHub copy); I did not
read it, so 09-25 to 09-30 below is only the organiser and repo events I could source.

| Date | What happened | Bot live | Rating / rank | Source |
|---|---|---|---|---|
| 09-25 | Engine unswbc 1.1.0 published 06:58 UTC; announcement: pearl schedule becomes a random seed per game. QWQ's first commit in the team repo (17:23 +1000). | not recorded | not recorded | `rules/CHANGES-2026-09-29.md`; `B` git log |
| 09-27 | Engine 1.2.0 to 1.2.2; maps and pearl timing tweaked; replays hide pearl intervals; separate quota for "dev" opponents and several pending battles allowed (21:45). | not recorded | not recorded | `rules/CHANGES-2026-09-29.md` |
| 09-28 | Scrim team order made random; organisers answer "judging uses separate architecture"; "Sprint Deadlines" announced (active submission frozen 10-01 08:00 KST). | not recorded | not recorded | same file |
| 09-29 | Autoscrims once per hour, one opponent per batch; rules re-saved by jun's tools. | not recorded | not recorded | same file |
| 09-30 | Old-team overnight loop; rule "upload only, never auto-revert" (02:25). | old swarm line | not recorded | `archive/claude-memory/upload-only-rule.md` |
| 10-01 | 00:xx new `unsw-swarm` lineage; 04:13 upload swarm-v1 13717; 07:24 v1.2 13911; **08:00 Sprint freeze** (v1.2 fixed). Autoscrims 08:18 to 11:13 used the 10 known maps. ~10:45 jun pastes the qualifier format. 16:30 Sprint main bracket: the team had a round-0 bye then lost round 1, 3-4 (battle 804455). 16:52 jun, watching the stream, sees fully custom maps and rules out per-map optimisation. ~19:29 all ratings reset to 1500. **20:08 rules change to 1.2.3 "Slay Queen"** (queen decides the game; free steps). | v1.2 (13911) for the Sprint; none active after the reset | 1500 for all after the reset | `DECISIONS.md` lines 3 to 20, 64 to 70, 195 to 232, 299 to 330 |
| 10-02 | v1.8 queen-rules line built with Codex helpers. 14:14 workflow paused on Claude weekly usage (85%). Evening: jun changed teams (left team 583, agreed new team with C--). 22:48 team 1119 key arrives; repo cloned ~23:00; 23:24 first #meow message; 23:28 QWQ lists the bot's 7 main problems. Organisers updated maps again this day (safer queen spawns); engine 1.2.7. | team 1119 already had "v61" (submission 15011) | rank 32, 1800 (22:5x) | `docs/STATE.md`; private notes; `archive/claude-memory/meow-team-repo.md`; the channel mirror (not published) |
| 10-03 | 00:09 jun proposes splitting work; 00:30 QWQ's issue board; 00:27 official 1.2.7 maps merged (engine itself unchanged). 03:42 overnight local loop starts. 11:57 meowbot (Discord bridge) starts. 19:30 Claude weekly usage hit 95%. | v61 (15011) | not recorded | `B` git log; `archive/claude-memory/overnight-loop-1003.md`, `meowbot.md`; private notes |
| 10-04 | 00:15 to 00:58 card-loop spec and runner (card states: ready, building, look, testing, candidate...). First paired online tests 17:08 on. Stride-test (16577) uploaded 17:28, live bot from 18:04 and the base copy after. 22:25 overnight study of the rank-1 team starts. 20:55 jun notes the displayed rating fluctuates. | 16577 "stride-test" from 18:04 | about 1850 at 10-05 00:20 | `data/online/REMOTE-LOG.md`; `docs/HANDOVER-2026-10-05.md`; `B` git log |
| 10-05 | 07:25 PR #35 (safer stride) merged; 08:21 upload 17184. 10:38 jun sets "humans first": AI-made cards archived. 17:16 PR #37 (queen-wait, QWQ) merged; 18:37 upload 17594 "v22". 23:16 upload 17790 "v31" (queen-hunt). 23:31 to 23:44 eight ranked fights requested at once (a "ladder push"; results not recorded in the files I read). | 17184, then 17594 (18:37), then 17790 (23:16) | about 1850 early; 1853 at 10-06 09:50 | `data/online/REMOTE-LOG.md`; `data/online/requests.jsonl`; `docs/HANDOVER-2026-10-06.md` |
| 10-06 | 05:13 v36 uploaded and live to 05:42 (a teammate set v31 back); 06:11 to 07:25 PRs #44, #45, #46 (cards 36, 42, 39) merged, server left on v31 on purpose. 13:35 jun: a clear request from Zhe or QWQ is done without asking. 15:54 to 16:03 hand-started games flipped the live bot v31/v41 five times (unexplained). 20:36 upload 18570 "v47". 23:50 jun's rule: keep the best-rated copy of the intended code live. | v31 until 20:36, then v47 | 1853, rank 60 (09:50); 1882, rank 54 (16:13) | `docs/HANDOVER-2026-10-06.md`; the channel mirror (not published) line 2347; `archive/claude-memory/elo-defence.md` |
| 10-07 | 01:11 two identical bot copies "parked" so the better-rated one plays; 02:15 to 02:45 an attempt to automate the switch was refused by the permission classifier and the session stopped; ~09:50 jun drops the 10-08 20:00 freeze: work continues to 10-09 15:00; 19:13 one ranked probe against team 82 (0-5 loss); 19:1x to 23:38 jun's switch project (local only at first; told the team 23:38). 22:24 PR #52 (card 48) merged. | v47 (18570), test copies in between | 1885 (rank 58) at 00:22; 1910 to 1970 all day; ladder points quoted at 18:57: 54th = 1953, 35th = 2050 | `docs/HANDOVER-2026-10-07.md` s.12, `07b.md`; `data/online/park/log.jsonl`; `docs/SESSION-STATE.md` lines 12, 324 |
| 10-08 | 02:01 PR #53 merged by Zhe (main a358ec8); 12:15 server stops accepting uploads from engine client 1.2.7 (needs 1.2.9); 14:55 live bot becomes v62 (20366); 17:44 jun: no xhigh anywhere; 18:10 teammates' cards to be merged last; 18:45 token limit lifted; 19:59 no baseline games online; 22:19 "one model" decision; 22:30 one1 up. Evening detail in section 3. | v47 to 14:55; v62 14:55 to 22:30 (test copies in between); one1 to one3 after | 1960 (14:56) to 2062 (18:02); 2113 (23:56) | `data/online/submissions.jsonl`; `docs/SESSION-STATE.md` lines 398 to 482 |
| 10-09 | 18 new versions (one4 to one21), see section 3. 09:00 changes announced frozen; 14:49:38 final upload; 14:59:42 final check; 15:00 deadline. After the deadline: ~15:12 jun posts a score screenshot, QWQ: a new version's rating fluctuates and autoscrims follow; 19:19 jun: "final seed 39". | one3 to one21 (21857 at the end) | 2113 (00:03) to 2092 (14:59); peaks 2168 (01:04), 2202 (13:50) | `data/online/park/log.jsonl`; the channel mirror (not published) lines 5632 to 5740 |
| 10-10 | Qualifier stream scheduled 15:30 KST (17:30 AEDT). 16:32 to 16:37 chat: closing messages and thanks; one message says the team would meet the top seed if it reached the round of 32. | one21 | not recorded | `archive/claude-memory/qualifier-timeline.md`; the channel mirror (not published) last 12 lines |

Repo activity (commits per day in `S`, from `git log`, read only): 10-01 225, 10-02 70, 10-03 16, 10-04 29, 10-05 20,
10-06 9, 10-07 10, 10-08 1, then one wrap-up commit on 10-10. The team repo `B` has 109 commits, the first on 09-25 and
the last on 10-09 14:52:42 (`44fae14`, "Final bot one21").

---

## 3. The final push: 2026-10-08 18:00 to 2026-10-09 15:00

**Answer first.** In 21 hours the live bot received 21 new versions (one1 to one21), two test copies, one deliberate
rollback and one unexplained switch. Online sets of 15 games were used as a smoke test and to see whether a switch
fired, not to rank versions. Three things cost time: online tests were blocked 19:00 to 22:13 on 10-08; the code-analysis
accounts were at their limits 07:14 to 10:48 on 10-09; and one wrong judgment (05:23) set the live bot back to an older
version for 38 minutes.

### 3.1 Hour by hour

Rating = the team rating polled by `tools/park_watch.py` (every ~5 minutes) in the first poll of that hour, except where a
rank is given from a note. "WHQ" is WeHaveQuizzes (team 87), "Cache" is Cache me outside (952), "kraken" is 989,
"dev1" is dev test 1 (545), "Preyas" is 1101, "SKKU" is Team SKKU (249). A score like 4/15 = wins out of the 15 games
of one set against that opponent.

| Hour | Events | Live bot | Rating / rank | Source |
|---|---|---|---|---|
| 10-08 18 | 18:17 PR #57 opened and handover written; 18:22 the "final count" post named team ids as ranks, corrected right away; 18:45 token limit lifted; 18:50 three builder agents; 18:56 online run agg9-a1 aborted with no game played (server queue 632, another team's ranked battle pending 15+ min) | v62 (20366) | 2062; 35th 2076 (18:22) | SESSION-STATE 399 to 408 |
| 10-08 19 | ~19:00 permission classifier refused the change that would move the test tool's 20:00 freeze, so online tests stopped; 19:33 to 19:41 Zhe asks for a card-55 test on v62 and agrees to swaps during ranked play; 19:45 jun: the uploaded bot is always teammates' hypotheses plus the solo switches; 19:59 jun: no more baseline games online | v62 | 2082 | SESSION-STATE 410 to 426 |
| 10-08 20 | 20:00 test-tool freeze in force; hourly ladder snapshot job stops by its own deadline; 20:05 PR #58 opened (solo switches, all off, plus a server profile) | v62 | 2068 | SESSION-STATE 425, 427; `data/analysis/ladder/runner.log` |
| 10-08 21 | no online games (blocked); local work only | v62 | 2052 | park log |
| 10-08 22 | 22:13 jun confirms, test tool fixed (freeze moved to 10-09 14:30); 22:16 queue starts; 22:19:01 test copy 20835 (card 55 on v62) uploaded; **22:19 jun: "one model" decision**; 22:26:27 v62 restored, test 3/15; 22:30:34 **one1** up; 22:34 PR #58 merged | 20835 for 7 min, v62, then one1 | 2080; 40th (22:10); 39th 2078 (22:35) | SESSION-STATE 428 to 448; submissions.jsonl |
| 10-08 23 | 23:02:38 **one2** up; 23:08 PR #60 opened; 23:09 one2 vs WHQ 6/15; 23:24:18 test copy 20905 (cards 54+55 for Zhe); 23:33:05 one2 back, test 3/15; 23:36:36 **one3** up; 23:56 one3 WHQ 2/15, dev1 1/15 | one2, 20905 for 9 min, one3 | 2079; 32nd 2113 (23:56) | SESSION-STATE 449 to 482 |
| 10-09 00 | ~00:10 **one4** live (no ledger line; server zip check failed once, re-checked); 00:21 workflow note and "changes stop 09:00" told to the team; 00:39 one4 dev1 4/15, WHQ 3/15; 00:49:43 **one5** up; 00:55 handover | one4, one5 | 2113 (00:03); 34th 2105 (00:40) | SESSION-STATE 486 to 503 |
| 10-09 01 | 00:57 one5 dev1 0/15; 01:04 WHQ 3/15; ~01:05 dev1 dropped as a yardstick (a teammate suspected hard-coding; a later test could not tell), Cache added; 01:07 PR #60 merged; 01:10 ranked 2-3 loss to team 133; 01:14 one5 Cache 6/15; 01:35:34 **one6** up | one5, one6 | 2168 (01:04, 25th) | SESSION-STATE 507 to 533 |
| 10-09 02 | 01:41 one6 WHQ 1/15; 02:12 Cache 3/15; 02:31:54 **one7** up; 02:46 one7 WHQ 4/15, Cache 5/15; 02:52 jun's rule: any loss to a team 100+ below us must be explained and fixed | one6, one7 | 2071 | SESSION-STATE 538 to 564 |
| 10-09 03 | 03:09:49 **one8** up; 03:26 kraken (989) wins two ranked sets 3-2, one costing 53 points; 03:27 one8 WHQ 3/15; 03:43 Cache 8/15; 03:51 kraken wins again 3-2 (-25); 03:52 one8 vs kraken 9/15 | one8 | 2095; 48th 2042 (03:28) | SESSION-STATE 568 to 586 |
| 10-09 04 | 04:00:00 **one9** up; 04:08 jun: analyse every game; 04:21 one9 kraken 10/15; ranked wins vs kraken 4-1 (+18), Quaker Qubits 4-1 (+41), acegi 3-2 (+9); 04:34:38 live bot is one8 though our ledger has no activation (jun: not from us, cause not established); 04:35:49 **one10** up; 04:55 one10 kraken 12/15 | one9, one8 (1 min), one10 | 2067; 44th (04:01); 2108 at 04:29 | SESSION-STATE 584 to 610 |
| 10-09 05 | 05:17 one10 Cache 3/15; ranked 1-4 (-32); **05:23:44 live set back to one8** after judging one10 worse; 05:40 control: one8 vs Cache 4/15 (it had 8/15 at 03:43), so the judgment was wrong; 51st 2018 (05:23) | one10, one8 | 2050 | SESSION-STATE 614 to 619 |
| 10-09 06 | 06:01:38 **one11** up; 06:11 analysis: Cache is the same bot, so 15-game sets are noise; 06:21 one11 Cache 4/15; local head-to-head becomes the main judge | one11 | 2045 | SESSION-STATE 628 to 635 |
| 10-09 07 | 07:00 one11 kraken 10/15; 07:08:19 **one12** up; 07:14 both code-analysis accounts at their limit; 07:22 one12 Cache 2/15; 07:42 Preyas 4/15 | one11, one12 | 2095 | SESSION-STATE 655 to 668 |
| 10-09 08 | 08:00 one12 kraken 8/15; 08:07:12 **one13** up; 08:24 Cache 6/15; 08:46 Preyas 4/15 | one13 | 2079 | SESSION-STATE 669 to 676 |
| 10-09 09 | 09:01 one13 kraken 8/15; **09:01 changes frozen** (announced); 09:12 PR #61 (final code and server profile) opened; 09:25 Cache 3/15; 09:45 Preyas 5/15 | one13 | 2158; 27th (09:01) | SESSION-STATE 677 to 684 |
| 10-09 10 | 10:04 kraken 6/15 (90 games: Cache 9/30, Preyas 9/30, kraken 14/30); 10:21 Quaker Qubits 7/15; **10:24:55 one14 up**: a rule that kept short dragons out of unseen portals was starving portal maps (a post-freeze fix); 10:46 PR #61 merged | one13, one14 | 2126; 36th (10:04); 42nd 2101 (10:26); 34th 2134 (10:46) | SESSION-STATE 685 to 694 |
| 10-09 11 | 11:03 one14 Preyas 4/15; 11:24 SKKU 1-4 (-31); 11:27 kraken 10/15 (45 games: 21 wins); **11:44:21 one15 up** (a territory term removed, it starved Queen Of Spades); 11:48 Quaker Qubits 2-3 (-7); 43rd 2093 | one14, one15 | 2131; 41st 2100 (11:24) | SESSION-STATE 715 to 734 |
| 10-09 12 | 12:07 one15 Cache 5/15; 12:34 Preyas 6/15; **12:51:01 one16 up** (queen no longer steps through an unseen portal on small maps) | one15, one16 | 2093 | SESSION-STATE 743 to 764 |
| 10-09 13 | 13:15 one16 Cache 3/15; **13:31:15 one17 up** (a long queen no longer splits to length 2 when exposed); 13:35 36th 2131; **13:48 first ranked scrim requests** (SKKU, Sponge); 13:50 SKKU 4-1 (+71) to 23rd 2202; 13:52 jun: deadline is 15:00, upload any time | one16, one17 | 2131; 23rd 2202 (13:50) | SESSION-STATE 770 to 791 |
| 10-09 14 | 14:00 SKKU (2nd) 3-2 (0); Computers (their request) 2-3 (-28): 30th 2174; **14:10:24 one18 up**; 14:11 Sponge 0-5 (-49), Check Raise 3-2 (-25): 42nd 2100; 14:24 five scrims requested; 14:30 SKKU 3-2 (+26), uncancelables 2-3 (-36); 14:33 test4 3-2 (+13), Cybers 3-2 (+20): 37th 2123; 14:36:35 **one19**; 14:37 Ballers 1-4 (-31): 41st 2092; 14:43:49 **one20**; 14:46 SKKU request (one20 active); 14:49:38 **one21**; 14:59:42 active confirmed 21857 | one17 to one21 | 2130 (14:01); 2092 from 14:36 | SESSION-STATE 795 to 863; requests.jsonl |
| 10-09 15 | Deadline 15:00. 15:01 to 15:02 Zhe's two screenshots read "20" while the server record says 21 (section 6, item 2); 15:12 jun posts a score screenshot; 15:15 QWQ: a new version's rating fluctuates and autoscrims run to stabilise it | 21857 | not recorded | the channel mirror (not published) 5601 to 5640 |

### 3.2 Every upload in the window

Times from `data/online/submissions.jsonl` (KST). "Own sets" = wins of 15 games per opponent from that version's own
games (sets taken from `docs/SESSION-STATE.md`; they are tiny samples, see lesson 1). "Rating" = team rating at the
first poll after the upload (`data/online/park/log.jsonl`); a new version inherits the previous version's rating and
moves quickly (`rules/elo.md`), so this column is not a score for the code.

| Time | Name | Submission | What changed from the version before | Own sets (wins/15) | Rating |
|---|---|---|---|---|---|
| 10-08 22:19:01 | c55v3 (test copy) | 20835 | v62 plus Zhe's card 55, third build | WHQ 3 | 2080 |
| 10-08 22:30:34 | one1 | 20850 | v62 plus queen walks with mates, mates ram a head within 3 steps of her, first split at round 0, feeders eat, queen end-room rule | WHQ 4, dev1 1 | 2078 |
| 10-08 23:02:38 | one2 | 20880 | one1 plus two ram switches gated at 56+ dragons | WHQ 6 | 2079 |
| 10-08 23:24:18 | c5455 (test copy) | 20905 | one2 plus Zhe's cards 54 and 55 final | WHQ 3 | 2079 |
| 10-08 23:36:36 | one3 | 20910 | one2 with feeding start at the 56-dragon cap moved from round 200 to 350 | WHQ 2, dev1 1 | 2079 |
| ~10-09 00:10 | one4 | 20941 | one3 plus queen early split (round 20), turn-keeping for short dragons | dev1 4, WHQ 3 | 2105 |
| 10-09 00:49:43 | one5 | 20980 | one4 without the queen's early split, plus "eat a pearl one step away first" | dev1 0, WHQ 3, Cache 6 | 2168 |
| 10-09 01:35:34 | one6 | 21033 | one5 plus end-game rally and queen dead-end terms on every map size | WHQ 1, Cache 3 | 2096 |
| 10-09 02:31:54 | one7 | 21086 | rally limited to fresh reports, short-dragon evasion, hunt their queen once ours is dead | WHQ 4, Cache 5 | 2095 |
| 10-09 03:09:49 | one8 | 21126 | one7 without evasion; sprint reach priced for short dragons, lone queen may split, mates not pinned on walls, unreachable pearls not targeted | WHQ 3, Cache 8, kraken 9 | 2095 |
| 10-09 04:00:00 | one9 | 21165 | one8 plus enemy reach counts pearls eaten on the way, splits beside portals, queen-team threshold 6 | kraken 10 | 2067 |
| 10-09 04:35:49 | one10 | 21200 | one9 plus any dragon rams their queen if it can reach, view-edge bodies count as 4, queen portal ban, boot rule | kraken 12, Cache 3 | 2077 |
| 10-09 05:23:44 | (one8 re-activated) | 21126 | not an upload: set back after a wrong judgment | Cache 4 (control) | 2030 |
| 10-09 06:01:38 | one11 | 21269 | one10 minus evasion, rally and queen portal ban; mates never take the queen's last free cell | Cache 4, Preyas 3, kraken 10 | 2045 |
| 10-09 07:08:19 | one12 | 21330 | one11 plus long-dragon escape, territory decay 16, far-head reports, corridor guard, short-dragon portal rule | Cache 2, Preyas 4, kraken 8 | 2115 |
| 10-09 08:07:12 | one13 | 21377 | one12 with the queen's small-team split threshold back to 2 | Cache 6/3, Preyas 4/5, kraken 8/6, Quaker Qubits 7 | 2079 |
| 10-09 10:24:55 | one14 | 21497 | one13 with the short-dragon portal rule off (a bug) | Cache 7, Preyas 4, kraken 10 | 2093 |
| 10-09 11:44:21 | one15 | 21583 | one14 without territory decay | Cache 5, Preyas 6 | 2093 |
| 10-09 12:51:01 | one16 | 21651 | one15 plus queen no blind portal on small maps | Cache 3, Preyas 6 | 2131 |
| 10-09 13:31:15 | one17 | 21693 | one16 plus no queen shed to length 2 when 10+ long | Cache 5 | 2131 |
| 10-09 14:10:24 | one18 | 21761 | one17 plus corridor guard counts mates' bodies | none | 2100 |
| 10-09 14:36:35 | one19 | 21827 | one18 minus queen dead-end terms (small maps), centre-pull cap 100000 cells, no trapped-queen ram, blind-portal stall rule | none | 2092 |
| 10-09 14:43:49 | one20 | 21843 | one19 with two completions of the same switches | none | 2092 |
| 10-09 14:49:38 | one21 | 21857 | one20 plus an exposed 10+ queen stays and splits 2 off | none | 2092 |

The version names, submission ids and (for one5 to one21) the mapping are also in
`data/online/smoke/versions.tsv`. one4's upload is missing from the tool ledger (see section 6, item 5).

### 3.3 Ranked battles

**Requested by us** (`data/online/requests.jsonl`, converted to KST; results from `docs/SESSION-STATE.md`). There were
nine in the window, all after 13:48; before that the harness only used unranked games. Rating change = the "catch-up"
the site shows per battle, as quoted in the notes.

| Requested | Opponent (team id, rank, rating then) | Bot active | Result | Rating change | Rank after |
|---|---|---|---|---|---|
| 13:48 | Team SKKU (249, 23rd, 2200) | one17 | 4-1 win | +71 | 23rd, 2202 |
| 13:48 | Sponge (213, 8th, 2450) | one17 | 0-5 loss | -49 | 42nd, 2100 (14:11, after Check Raise -25 too) |
| 13:55 | Team SKKU (249, 29th, 2171) | one17 | 3-2 win | 0 | 30th, 2174 (after Computers) |
| 14:24 | Team SKKU (22nd, 2231) | one18 | 3-2 win | +26 | 40th, 2090 (14:30) |
| 14:24 | the uncancelables (899, 31st, 2156) | one18 | 2-3 loss | -36 | 40th, 2090 |
| 14:24 | test4 (19, 21st, 2248) | one18 | 3-2 win | +13 | 37th, 2123 (14:33) |
| 14:24 | Cybers (1148, 32nd, 2150) | one18 | 3-2 win | +20 | 37th, 2123 |
| 14:24 | Ballers (1149, 34th, 2142) | one18 | 1-4 loss | -31 | 41st, 2092 (14:37) |
| 14:46 | Team SKKU (23rd, 2222) | one20 | in progress at 14:59: "L L W . L" | not recorded | 41st, 2092 |

My arithmetic: the requested fights net +14 (+71, 0, -49, +26, -36, +13, +20, -31). Battles other teams requested in the
same period: Computers 2-3 (-28), Check Raise 3-2 (-25), BambooCode 4-1 (0), which is -53; a SKKU-requested battle with
one18 (b1536232, 1-4) has no recorded change. The rating went from 2131 (13:35) to 2092 (14:37), which is -39 = +14 - 53,
so the recorded numbers add up. The target stated at 14:26 was a seed in the mid 2200s; the best moment was 2202.
Extra requests were stopped after 14:11 (SESSION-STATE line 800 and 818: jun also judged it risky) and resumed at 14:26
with one18 active (line 841).

**Earlier ranked requests by us:** 10-05 23:31 to 23:44, eight fights vs teams ranked 33 to 49 with v31 active (results
not recorded in the files I read; the rating read 1853 on 10-06 09:50, and the push's own effect is not isolated);
10-07 19:13, one fight vs team 82 (rank 23, 2138): 0-5 loss (`docs/SESSION-STATE.md` line 12).

**Requested by others in the window (selected, with the change when the notes give it):** v62: 946 -14, SSS -12,
WeLikCoding -12 and -5 (all 2-3 losses), then three wins (+12, +8, +8) (10-08 19 to 21); the test copy 20835 happened
to play Nitronics 2-3 (-2) and SHINK 2-3; one1: Jingling Munmin 2-3 (0 and 0), Cache me outside 2-3 (-2); 10-09 kraken
beat us 3-2 twice (03:26, one cost 53) and again at 03:51 (-25); we beat Quaker Qubits 4-1 (+41), acegi 3-2 (+9) and
kraken 4-1 (+18); Computers 1-4 and Preyas 1-4 against one8 (04:34); Adrak vali chai 1-4 (-32). one13's sets from
08:07: wins vs Spearhead, Ballers, Heartbreaker, Jingling Munmin, ouroboros (5-0), Cybers; losses to Sponge (twice),
Quaker Qubits (-33), Team SKKU (-19), WeLikCoding (-6). one14: Check Raise 3-2, kraken 3-2, Sponge 2-3 (+25), SKKU
1-4 (-31). (`docs/SESSION-STATE.md` lines 448 to 457, 575 to 586, 685, 690, 694, 715, 734.)

**Totals from the collector** (`data/online/live-one1/index.txt`; 10-08 22:41 to the end; it lists battles it
downloaded, so battles that finished between its 5-minute polls or after 14:55 may be missing): ranked 33 wins and
36 losses (69), unranked 19 and 43 (62). Ranked by hour, wins-losses: 22h 0-2, 23h 1-2, 00h 1-2, 01h 2-1, 02h 2-0,
03h 2-3, 04h 1-3, 05h 1-2, 06h 2-2, 07h 2-3, 08h 6-1, 09h 1-2, 10h 3-3, 11h 1-2, 12h 1-2, 13h 1-1, 14h 6-5.

---

## 4. Rating and rank history

**Answer first.** The displayed team rating followed the active submission's own rating, so it jumped when the active
copy changed and moved 25 to 70 points per hour on the last day. Rating rose from 1800 (10-02) to about 1960 (10-07)
to 2062 (10-08 evening) to a peak of 2202 (10-09 13:50) and ended at 2092 (41st). The rank is more volatile than the
rating because teams around us moved too.

| Date | Time | Rank | Rating | Source |
|---|---|---|---|---|
| 10-01 | morning | 30 (team 852, old ladder, before the reset) | 1894 | private notes |
| 10-01 | ~19:29 | all teams | 1500 (ladder reset) | `DECISIONS.md` lines 304 to 310 |
| 10-02 | 22:5x | 32 | 1800 | private notes |
| 10-05 | 00:20 | about 40 | about 1850 | `docs/HANDOVER-2026-10-05.md` |
| 10-06 | 09:50 | 60 (best 1918) | 1853 | `docs/HANDOVER-2026-10-06.md` |
| 10-06 | 16:04 / 16:13 | 54 at 16:13 | 1859 / 1882 | the channel mirror (not published) line 2347 |
| 10-07 | 00:22 | 58 | 1885 (day's best 1939) | `docs/HANDOVER-2026-10-07.md` |
| 10-07 | 18:57 | 54th place = 1953; 35th place = 2050 | team v47 1953 | SESSION-STATE line 324; park log |
| 10-08 | 14:56 | not recorded | 1960 (v62 live) | park log |
| 10-08 | 16:01 / 17:01 / 18:02 | not recorded / not recorded / 35 | 1992 / 2022 / 2062 | park log; HANDOVER-2026-10-08 |
| 10-08 | 18:22 | 35 | 2076 | SESSION-STATE line 400 |
| 10-08 | 19:02 / 20:02 / 21:03 / 22:03 | 40 at 22:10 | 2082 / 2068 / 2052 / 2080 | park log; SESSION-STATE 428 |
| 10-08 | 22:35 / 22:53 | 39 / 39 | 2078 / 2076 | SESSION-STATE 448, 457 |
| 10-08 | 23:56 | 32 | 2113 | SESSION-STATE 482 |
| 10-09 | 00:40 | 34 | 2105 | SESSION-STATE 493 |
| 10-09 | 01:04 | 25 | 2168 (one5, the day's high until 13:50) | SESSION-STATE 511 |
| 10-09 | 02:04 / 03:04 | not recorded | 2071 / 2095 | park log |
| 10-09 | 03:28 | 48 | 2042 | SESSION-STATE 575 |
| 10-09 | 04:01 / 04:29 | 44 | 2067 / 2108 | SESSION-STATE 586, 603 |
| 10-09 | 05:04 / 05:23 | 51 at 05:23 | 2050 / 2018 | park log; SESSION-STATE 614 |
| 10-09 | 06:04 / 07:00 / 08:00 | not recorded | 2045 / 2095 / 2079 | park log |
| 10-09 | 09:01 | 27 | 2158 | SESSION-STATE 679, 681 |
| 10-09 | 10:04 / 10:26 / 10:46 | 36 / 42 / 34 | 2126 / 2101 / 2134 | SESSION-STATE 685, 690, 694 |
| 10-09 | 11:24 / 11:48 | 41 / 43 | 2100 / 2093 | SESSION-STATE 715, 734 |
| 10-09 | 13:35 | 36 | 2131 | SESSION-STATE 779 |
| 10-09 | 13:50 | 23 | 2202 | SESSION-STATE 788 |
| 10-09 | 14:00 / 14:11 | 30 / 42 | 2174 / 2100 | SESSION-STATE 804, 818; Discord 5512 |
| 10-09 | 14:30 / 14:33 / 14:37 | 40 / 37 / 41 | 2090 / 2123 / 2092 (10th = 2411, 30th = 2162) | SESSION-STATE 847, 849, 852 |
| 10-09 | 14:59 | 41 | 2092 | SESSION-STATE 861 |
| 10-09 | 19:19 | final seed 39 | not recorded | the channel mirror (not published) line 5735 |

The per-submission series (id, version label, rating) at every change of the active copy from 10-07 01:12 to 10-09 14:51
is `data/online/park/log.jsonl`; hourly means are not needed to read the story: the rating at the end of each upload
is the number in section 3.2.

---

## 5. Rule changes

**Answer first.** Organisers changed the rules once in a way that mattered (10-01 "Slay Queen", engine 1.2.3), reset
the ladder at the same time, announced the qualifier format on 10-01, and forced client upgrades on 10-08. jun's own
rules changed the way work was done several times a day on the last two days; the most consequential were "no baseline
games online" (10-08 19:59) and "one model, forward only" (10-08 22:19).

### 5.1 Organisers

| Date | Change | Source |
|---|---|---|
| 09-25 | Pearl schedule becomes a random seed per game; engine 1.1.0 (local judge). | `rules/CHANGES-2026-09-29.md` |
| 09-27 | Engine 1.2.0 to 1.2.2 (map check, viewer); pearl timing variants; replay masks pearl intervals; dev quota separate; several pending battles per opponent allowed (21:45). | same |
| 09-28 | Scrim team order random; "Sprint Deadlines": active submission frozen 10-01 08:00 KST. | same |
| 09-29 | Autoscrims once per hour, one opponent per batch; docs say 60 games an hour, a separate 60 for dev teams. | same |
| 10-01 ~10:45 | Qualifier format (pasted by jun): seeded single elimination, best of 7 on unseen maps; submissions close 17:00 AEDT on 10-09 = 15:00 KST; autoscrims set the seeds; 8 quarterfinalists qualify, round-of-16 losers play a second-chance bracket for two more places; stream starts 17:30 AEDT on 10-10 = 15:30 KST. | `qualifier-timeline.md`; `DECISIONS.md` line 66 to 69 |
| 10-01 20:08 | **Rules 1.2.3 "Slay Queen":** at round 500 the team with the longer queen (lowest-id dragon) wins, a dead queen counts 0; first ceil(L/4) steps of a turn are free; each submission has its own rating with per-map offsets, first submission 1500, autoscrims 3 per hour; all submissions set idle. | `DECISIONS.md` lines 321 to 330; `slay-queen-rules.md` |
| 10-01 ~19:29 | Ladder reset to 1500. | `DECISIONS.md` lines 304 to 310 |
| 10-02 | Maps updated again (safer queen spawns); engine 1.2.7. Teams cannot leave a team after 7 days. | Discord line 52; private notes |
| 10-04 (jun's report) | "Ladder points after a win streak changed" in an announcement after the Sprint; details not recorded. | Discord line 587 |
| 10-06 | Engine 1.2.9 appears; identical play to 1.2.7 (version string and viewer differ). | `docs/HANDOVER-2026-10-06.md` s.8 |
| 10-08 ~12:15 | Server stops accepting uploads from client 1.2.7; "1.2.9 is out". Evening: banner "1.2.10 is out", uploads from 1.2.9 still accepted to the end. | `docs/HANDOVER-2026-10-08.md` s.3.2; SESSION-STATE line 445; Discord line 4228 |
| Rule always in force | A ranked fight is refused against teams more than 50 points below ("50-point rule"); 60 games an hour of allowance, ranked battles included. | `rules/CHANGES-2026-09-29.md`; SESSION-STATE 783 |

### 5.2 jun's working rules (dates when the record gives them)

| Date | Rule | Source |
|---|---|---|
| 10-01 ~15:21 | Qualifier build runs with map recognition off. 16:52: no per-map optimisation, ever. | `qualifier-timeline.md`; `no-fixed-map-optimization.md` |
| 10-03 | Universal logic only: old known maps replay-identical, new behaviour behind an off-by-default switch. | `known-map-preserving-rule.md` |
| 10-04 17:25, 18:55 | Do not hesitate on test uploads; do not ration uploads for rating reasons. | `upload-only-rule.md` |
| 10-04 | Freeze set at 10-08 20:00 (loop spec). | `loop-spec-1004.md` |
| 10-05 10:36 | Human ideas first; AI-made cards archived. | `humans-first-1005.md` |
| 10-06 13:35 | A clear request from Zhe or QWQ is done without asking, report after (uploads and online tests included). | `HANDOVER-2026-10-06.md` s.4 |
| 10-06 23:50 | Keep the best-rated copy of the intended code live. | `elo-defence.md` |
| 10-07 ~09:50 | Freeze dropped; work runs to 10-09 15:00. | `loop-spec-1004.md` |
| 10-07 19:1x to 20:04 | Switch project is local only; 23:38 jun tells the team himself. | `solo-project.md` |
| 10-08 14:50 | The live bot (upload and activation) is Claude's to manage. | `solo-project.md` |
| 10-08 17:44 | No xhigh effort anywhere. | `effort-high-only.md` |
| 10-08 18:10 / 18:45 | Merge teammates' cards last; token limit lifted. | SESSION-STATE 405, private notes |
| 10-08 19:45 | The uploaded bot is always teammates' hypotheses plus solo switches. | SESSION-STATE 423 |
| 10-08 19:59 | **No baseline games online** (tickets are too valuable); judge a new bot from its own games. | `same-hour-baseline.md`; `data/guide/px-jun-notice-2000.txt` |
| 10-08 22:19, 22:2x | **One model live, improve forward; no rollback to an old bot** (v62 only if the build is broken). | `one-model-live-1008.md` |
| 10-09 00:49 | Thinking work may go to the second Codex model, about 8 in parallel. | SESSION-STATE 498 |
| 10-09 01:0x | dev1 dropped as a yardstick (suspected hard-coding); replaced by Cache me outside. | SESSION-STATE 510 |
| 10-09 02:52 | Any loss to a team 100+ below us must be explained and fixed. | `weak-loss-rule.md` |
| 10-09 00:21 / 09:00 | "New fixes stop at 09:00" announced to the team; at 09:01 frozen. | SESSION-STATE 488, 679 |
| 10-09 10:24 | One post-freeze fix allowed only for "broken" (portal bug). | SESSION-STATE 688 |
| 10-09 13:52 | Deadline is 15:00, not 14:30: upload when ready. | SESSION-STATE 789 |
| 10-09 14:00 | Upload one more at 14:15; the next one is the last. (It was not: three more followed.) | SESSION-STATE 803; Discord 14:39 "maybe not last btw" |

---

## 6. Open questions: dates and numbers that conflict or are missing

1. **Bracket result and round.** jun reports a quarterfinal exit on 2026-10-10. The chat mirror has no message between
   10-09 19:56 and 10-10 16:32, so it cannot date or order any match. What it has: "final seed 39" (10-09 19:19);
   QWQ noting that the bracket path led to the top seed and that there is a second-chance bracket (19:21 to 19:22,
   with a screenshot not readable here); on 10-10 16:32 a few closing messages, one of which makes meeting the top
   seed conditional on reaching the round of 32.
   The exchange can be read as a first-round loss (the "if we reach the round of 32" condition was not met) or
   as something else; the screenshot is not in the files. The qualifier format (section 5.1) says eight
   quarterfinalists qualify and round-of-16 losers play a second-chance bracket; nothing in the record says whether
   the second-chance bracket was played or which round ended the run.
2. **Which bot was in the final submission.** Server records: active 21857 (one21) at 14:49:42, confirmed again at
   14:52:49 and 14:59:42 (SESSION-STATE 858, 861). In chat at 15:00 jun: "that bot isnt 21 maybe queued 19 or 20"; Zhe, with
   two screenshots, 15:01 and 15:02: "its 20"; QWQ: "nvm we submit 21". My reading: the screenshots show the
   ranked battle requested at 14:46 (made while one20 was active), not the submitted version. Not confirmed.
3. **When v62 went live.** Upload ledger: activated 14:55:48 on 10-08. HANDOVER-2026-10-08 and the park log: 14:56.
   SESSION-STATE (the 10-08 14:50 entry): 14:59. I use 14:55:48.
4. **Who switched the live bot to one8 at 04:34 on 10-09.** The park log shows 21126 active at 04:34:38 (and two
   ranked battles requested at 04:34:33 and :37 were played by it), but our ledger has no activation. jun said it was
   not them; the cause is not established.
5. **one4's upload.** Live at ~00:10 and polled at 00:13:55, but neither `submissions.jsonl` nor `REMOTE-LOG.md` has the
   upload line (the server zip check failed once during it, per SESSION-STATE line 486). Time is the note's, not the
   ledger's.
6. **Small time differences.** SESSION-STATE gives live times to the minute at which they were noticed, the ledger to
   the second; for example one1 22:29 against 22:30:34. The ledger is used throughout.
7. **"Freeze" dates.** HANDOVER-2026-10-05, 10-06 and `loop-spec-1004.md`: freeze 10-08 20:00. 10-07 evening
   handover: "no freeze" (dropped 10-07 ~09:50). In code, the card loop's freeze constant was moved to 10-09 15:00 on
   10-07 (HANDOVER-2026-10-07b s.5), but the separate online-test tool kept 10-08 20:00 until 22:13 on 10-08, when it
   moved to 10-09 14:30. The team was told 09:00 on 10-09 as the cut-off for new switches and 15:00 as the deadline.
   All of these were in force at some time; sections 3 and 5 list them with their dates.
8. **Ladder reference points on 10-07 18:57.** "54th 1953, 35th 2050" in SESSION-STATE; whether 54th was our own
   position is not stated, though the park log shows our v47 at 1953 then. Treated as a reference, not our rank.
9. **Final rating after the deadline.** jun's 15:12 screenshot and a number "103" are mentioned in chat; the rating
   itself is not recorded. The seed (39) is recorded, but how the seed was computed (final rating, autoscrim results)
   is not; Zhe's claim that seeds follow the final rating is unconfirmed (HANDOVER-2026-10-07 s.12).
10. **Claims of "strongest bot".** At 14:57 jun wrote in #meow that every change had been confirmed to improve the
    bot. What was verified for one19 to one21: local games identical to the previous version for the changed paths and
    audits of control flow (SESSION-STATE lines 845 to 862). No online game of those three versions is on disk. The
    stronger claim is not in the record.
11. **Ranked results before 10-09 13:48.** The 10-05 eight-fight push (23:31 to 23:44) has no per-fight results in the
    files I read; per-fight outcomes for 10-06 to 10-08 are partial (section 3.3).
12. **Discord mirror duplicates.** The mirror sometimes stores a message twice with the same id (HANDOVER-2026-10-07
    s.10); counts of messages are not reliable, times are.
13. **Bracket size.** The number of teams and rounds in the seeded bracket is not recorded in any file I read, so a seed
    of 39 cannot be turned into a first opponent or a number of rounds to the quarterfinal.

---

## 7. Use of this chapter next time

- Keep a signed append-only ledger of uploads and activations with the second, from the start. Ours missed one upload
  and one activation, and the time of a live change is the most-needed fact when analysing games after the fact.
- Log the team rating and rank at least every five minutes on the last two days, with the active submission id; the
  park log did this from 10-07 01:12 and is the most reliable rating series here. Before that the series is made
  of notes.
- Plan the last 36 hours as a schedule with a date, a cut-off and a person for each upload; write the cut-off down
  once and do not move it. Here it moved three times (10-08 20:00, 10-09 09:00, 10-09 14:30 to 15:00).
- Whether any of this applies to a different contest depends on the ladder: here the team rating was the active
  submission's and new uploads inherited the previous one's, which made frequent uploads cheap for rating but
  expensive for evidence.
