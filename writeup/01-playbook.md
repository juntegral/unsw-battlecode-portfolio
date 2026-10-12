# 01. Playbook: how to run a bot-programming contest

What we would do again and what we would not. This is the method chapter. The game's mechanics, the bot's code, the tools, the AI workforce and the day-by-day timeline are in the other chapters.

Written 2026-10-10 from the project record. All times are KST. Paths start with `S` (jun's private repo `unsw-swarm`), `B` (team repo, branch with the final bot) or `R` (local game rig `~/meow-redteam`).

**How to read the evidence marks.** `[M]` = a number or event that is written in the record (file given). `[R]` = my reading of the record, not something that was measured. "Not recorded" = I looked and the files do not say.

## 0. Twelve lines of context

- **The game.** Two teams of snake-like units ("dragons") on a grid map. Dragons eat pearls to grow, split to multiply, and die when rammed head-on, boxed in or walked into a wall. Each dragon sees only nearby cells. A game lasts 500 rounds. Since the rule change of 2026-10-01 the team whose **queen** (its lowest-numbered dragon) is longer wins; a dead queen counts as zero. Round N is written rN.
- **The contest.** A public ladder with a rating, then a qualifier: single elimination, best of seven, **on maps nobody had seen**. Submissions closed 2026-10-09 15:00.
- **The team.** "meow" (team 1119): jun (infrastructure, tools, AI sessions), Zhe (strategy and intuition, CEST) and QWQ (author of the base bot, AEDT). Formed 10-02, seven days before the deadline. jun's work before 10-02, on a previous team with a different bot, produced the first version of the method (`S/docs/PHILOSOPHY.en.md`, `S/docs/STATE.md`).
- **Words used below.** *Switch*: a named constant in the bot source that turns one behaviour on; every switch is off by default. *Profile*: the list of switch values that defines one version. *Live*: the submission currently active on the server. *Allowance*: the server let us request about 60 games an hour against chosen teams, shared with ranked battles other teams requested against us. *Set*: 15 online games against one team, one per ladder map. *Ranked battle*: five games against one team that move the rating. *Head-to-head (h2h)*: local games between two of our own versions. *Card*: one idea tracked as a GitHub issue through the team's loop.
- **The outcome.** At the deadline the live bot was version "one21", rated 2092, rank 41 `[M: S/docs/SESSION-STATE.md, 14:59 entry]`. Final seed 39 `[M: jun in the team channel, 10-09 19:19, the channel mirror (not published)]`. The team was eliminated on 10-10; the round is not recorded consistently (the brief for this write-up says quarterfinal by jun's account; the channel mirror at 10-10 16:36 reads as if the team went out before the round of 32). Which maps the bracket used and how each game went: not recorded.

## 1. The short version

### What cost us most

| # | What happened | Size `[M]` | What to do instead |
|---|---|---|---|
| 1 | Structured testing on unseen-style maps came last. The first run on 64 freshly generated maps was 13 hours before the deadline; the round that tried to break the bot on odd shapes started 70 minutes before it. | First run: the then-live version lost 31-3-40 to our own old bot on new maps while winning 12 to 14 of 16 on familiar ones. The late round found one live switch that locked the team in its start room (live 13 hours) and classes we could not fix in time (7x7 maps, closed start rooms). | Section 5. Build the map generator and a "break it" map set in week one. |
| 2 | For about eight hours of the last night, versions were judged on single 15-game online sets. | The same bot against the same unchanged opponent scored 8 of 15 and then 4 of 15 two hours apart. Eight of the switches turned on that night were later turned off again (table in the appendix). One rollback was made on a wrong verdict. | Section 3. Know the noise floor of every instrument before using it to decide. |
| 3 | Two harmful switches were live for 3.3 and 4.6 hours, through the declared code freeze. | Pearls eaten by r100 on one portal map fell from 238 to 71; another map was left with 2 to 3 dragons for 100 rounds. Local head-to-head had rated both switches neutral. | Lesson T5. Read a per-map, per-version health table after every upload. |
| 4 | The largest class of losses (falling behind in dragon count in the first 150 rounds) never got a fix; most of the last 14 hours went to queen-protection rules. `[R]` | 41 of 71 classified losses were "decided by dragon count before r150". At the end: no ship-ready fix for the early gap, and the queen still died in 286 of 368 games. | Lesson D1. Rank losses by cause and re-rank after every few fixes. |
| 5 | Ranked battles were requested in the last 70 minutes to raise the seed. | Rating 2131 (rank 36) before, 2092 (rank 41) after: +14 from the eight battles we requested (single results from +71 to −49), −53 from battles other teams requested in the same hour. | Lesson S5. Do not use rating games as a lever when one loss costs twice what one win pays. |
| 6 | The local rig was limited to two games at a time (set on purpose on 10-07 and written in a handover) and the last day's batches were planned as if it were not. | Noticed at 13:52 on the last day: a batch asked for 8 parallel games had been getting 2. | Checklist item 4. Measure rig throughput, and make the batch launcher print the parallelism it actually gets. |

### What we would do again

| # | Practice | Why it earned its place |
|---|---|---|
| 1 | Every new behaviour behind a default-off switch, with the all-off build proven identical to the old program by binary hash. | 21 versions went live in 16 hours; no crash or timeout was recorded in any check, and the code that was live was always known. Removing a harmful change was a one-line edit. |
| 2 | One source file plus a profile of switch values. | The team's main branch, the solo work and the server could always be compared by a text diff. |
| 3 | A per-map, per-version table of health numbers (pearls and dragons at r50 and r100, queen death round). | Found two harmful switches in under an hour each, after eight hours of win counts had found nothing. |
| 4 | Classifying every loss by cause, by script, over all games. | Turned "we lose a lot" into ranked, countable targets. |
| 5 | Proving that the uploaded binary is the tested binary, then checking the server copy and the active id. | Caught a server-side verification that reported failure and an activation that none of our tools had made. |
| 6 | A promises ledger, a session-state memo and written handovers. | 69 promises to teammates were logged and most closed as done or as a posted correction; each of six new sessions resumed from a document. |
| 7 | Posting every correction of our own earlier statement. | About 30 log entries record a correction or a withdrawal. `[R]` Teammates could keep using the numbers because wrong ones were withdrawn in the same channel. |

## 2. Deciding what to build

### D1. Rank losses by cause first, and re-rank as you go

**Rule.** Before choosing work, classify every lost game by what decided it, over all games, by script. Work on the biggest class. Repeat the classification after every few changes.

**What happened.** Three classifications were made and each changed the plan. 10-07, 485 games of the then-live code: four maps held 41% of all losses; in games that reached r500, "only our queen alive" won 18 of 18 and "only their queen alive" won 0 of 58 `[M: S/docs/HANDOVER-2026-10-07b.md §4]`. 10-09 00:2x, 96 games of versions one1 to one3: 71 losses = 41 decided by dragon count before r150 (26 of them wipe-outs, 33 on small maps), 16 lost on longest dragon, 7 queen only, 7 other `[M: S/data/analysis/ladder/dossier/diag-one1.md §13]`. 10-09 13:03, 56 games of one15: 30 losses, the queen dead in 28 of them `[M: S/data/codex/astra/loss15-sonnet/losses.md]`.

The second and third look contradictory and are not. In the lost games of the last ranked battles we had 2 to 8 dragons at r100 against 10 to 38, summarised in the log as "the economy collapses first" `[M: battle-opus, 14:17 entry]`. `[R]` In many losses the queen's death is the last event of a game already lost on numbers. The queen's death is the most visible cause and attracted about twenty switches on the last night; the early gap is the larger cause and ended with "no ship-ready switch" (`S/data/codex/astra/early-opus/`, 11:46 entry: pearls by r100 114 against 162; a non-queen that reaches length 4 splits on its first turn 48% of the time against the opponent's 93%).

**Depends on.** Replays that can be parsed by script, and a few hundred of our own games. Transfers to any game with a replay format.

### D2. No build without a counted behaviour and the code line that produces it

**Rule.** A diagnosis is finished when it names (a) a behaviour counted in real games, (b) the line of our code that causes it and (c) a board where it can be reproduced. "No card" (nothing to build) is a normal and useful result.

**What happened.** The fixes that survived to the final bot all had the three parts. Examples: `EAT_FIRST` (a dragon left a pearl one step away uneaten for 19 to 34 rounds; a debug trace of the direction scores showed the territory term outweighing the eat bonus, 4235 for the pearl step against 4970 for walking away; `R/solo/src/w-eat/`, 10-09 00:27). `QUEEN_NO_BLIND_PORTAL` (on one map the queen died boxed in 30 of 30 games; traced to a size test that excluded maps of 600 cells or fewer from the queen rules; reproduced locally 8 of 8; 12:43). `QUEEN_CORRIDOR_MATE` (three online games with the same mechanism, reproduced locally, 14:10).

The fixes built from a count alone mostly did not survive. Between 01:00 and 01:40 on the last night eleven analyst reports came back; eight said "no card", three proposed a card, and all three resulting switches were later dropped or removed (`QUEEN_DEAD_ALL`, `EAT_FIRST_TWO`, `RALLY_END_FRESH`) `[M: S/docs/SESSION-STATE.md, 01:05 to 01:38 entries; counted by me]`. The other direction holds too: on 10-08, 18 deep diagnoses cost about $300; at least seven ended without a card, and each switch of the first bundle (the one measured gain, section 3.1) is listed with the diagnosis file it came from `[M: S/docs/HANDOVER-2026-10-08.md §3.4, §3.5]`.

**Depends on.** Being able to rebuild the bot's decision at one turn (a debug log of the scores, or feeding a reconstructed board to the real function). Build that tool early; we had it only on the last two days.

### D3. Count how often a switch changes a decision before judging it

**Rule.** The first number for any new behaviour is "in how many turns did it change the move". If that is near zero the win counts that follow are noise by construction.

**What happened** `[M: S/docs/SESSION-STATE.md]`. `SHORT_EVADE` went live on an analyst's count (329 of 559 hits had a free escape), showed no effect online, and only then was found to change 0.10% of turns (03:10). `QUEEN_AVENGE` went live at 02:31; in the five losses checked two hours later the "their queen is dead" signal it waits for had never been produced, so it never armed (04:17). `QUEEN_HOLD_LEN` played 96 local games to 46-4-46 before a replay comparison showed the two bots had made identical moves in every game (08:09). `QUEEN_DEFEND_STEPS` could not fire as built (2 of 39 eligible turns). In the team's card loop, card #48's result test had 391 of 400 game pairs identical, and card #49's target situation arose in 0 of 12 local games.

**Depends on.** Deterministic games (ours were: same map, seed and bots gave the same replay), so "identical replay" is a cheap test for "never fired".

### D4. A correlation in the logs is not a lever

**Rule.** A rate that differs between two groups of games tells you where to look. It does not tell you that forcing the bot into the better group will help.

**What happened.** An analyst measured that, once the enemy queen was dead, our queen died 2.61 times per 100 rounds at length 2, 0.87 at length 3 and 0.08 at length 4 or more (06:48). A switch to hold the queen at length 4 was built. It never fired (above), the signal it needed was then repaired, and with the signal working the queen died *more* often: 0.93 per 100 rounds off, 1.10 holding, 1.93 holding and feeding (11:48). The builder's own conclusion: the 0.08 was a correlation. About five hours of one builder and one analyst `[M: S/data/codex/astra/qdead-opus/, h2hloss-opus/]`.

**Depends on.** Nothing game-specific.

### D5. Each guard moves the death to the next branch

**Rule.** When a safety rule blocks one bad move, check what the code does instead. Count deaths by class before and after, not the number of guards.

**What happened** `[M]`. `QS_SHED_MAX` stopped a long queen from splitting down to length 2 when exposed; the code then fell through to the next branch, "walk to a cell the enemy reaches only by paying", and a teammate saw the queen walk into reach (14:47; fixed by a further switch that went live 11 minutes before the deadline). `QUEEN_NO_BLIND_PORTAL` stopped the queen entering a portal with an unseen far side; on a generated map whose only exit was such a portal the team then starved in its start box (14:26; patched by a further switch). `QUEEN_PORTAL_ALL` fixed one portal map and cut early eating by 40% on another (12:29, two games). Across versions one11 to one14 the queen died in 286 of 368 games and survived to the end in 82 `[M: S/data/codex/astra/qexit-opus/]`. `[R]` The project's own stated principle was "fix the reading of the board, do not stack exceptions" (`S/archive/claude-memory/solo-project.md`, creed 2); under deadline pressure the last night stacked exceptions.

**Depends on.** A bot written as an ordered chain of special cases. A bot built on search or on one scoring function would show the same problem as shifted scores.

### D6. Teammates' reads are leads; test them like anything else

**Rule.** When a teammate with good game sense questions a result, re-cut the data along their angle before defending yours. When their idea tests badly, separate "the build missed the idea" from "the idea is wrong" and tell them which, with numbers.

**What happened.** Zhe spotted that an opponent had changed its bot overnight when the data had not ("looks like they updated their version", 10-06; lesson T3). His last-hour report produced the final fix. His two cards tested 3 of 15 (one card) and 3 of 15 (both together) online against 4 to 6 of 15 for the live bot, and his "start feeding from r200" variants lost local head-to-head 16-2-30, 17-2-29 and 20-2-26; each result was posted to him with a table and the reason `[M: S/docs/SESSION-STATE.md, 23:33 and 07:37 entries]`. Whether intuition-led or data-led ideas had the better hit rate: not tallied; thin evidence either way.

## 3. Testing a change

### 3.1 What each instrument could and could not tell us

| Instrument | Cost | Could tell | Could not tell | Evidence `[M]` |
|---|---|---|---|---|
| One 15-game online set against a named team | A quarter of an hour's allowance, 10 to 20 minutes | Crashes; whether a behaviour fires against a real opponent | Which of two versions is better | Same bot, same unchanged opponent: 8 of 15 then 4 of 15 (final length 129 then 92). 10-09 05:40 and 06:11 |
| Paired online comparison: both versions, same hours, same maps, same opponents, 30 to 90 games each | Three or more hours of allowance | A real difference between versions | Which switch inside a bundle caused it | 60 pairs: new bundle alone won 12, old alone won 3, sign test p = 0.035; win rate 23% to 38%. 10-08, `S/data/analysis/ladder/dossier/online/agg7.md` |
| Local h2h against our own older version on generated maps, 48 to 96 games | CPU only; 1 to 4 minutes a game | Differences of roughly 60-40 or larger | Anything on a map family missing from the set; anything that needs an opponent behaviour our own bot lacks | Section T4 |
| Local sets of 8 to 16 games | Minutes | "Does it fire, does it crash" | Anything about strength | 8-game win counts drifted 8, 7, 6, 4 across versions and single-switch arms then showed no difference. 05:54 |
| Behaviour counts from replays | One script per behaviour | Whether the mechanism did what it was built for | Whether that wins games | The online check of one16: queen portal steps in r0 to r99 went from four to none. 13:25 |
| Per-map, per-version health table | One script over all stored games | A version that broke a map family | Small overall gains | Lesson T5 |
| Loss classification by cause | One script plus reading | What to work on next | Whether a fix worked | Lesson D1 |
| Ladder rating | Free | Nothing within a day | Version quality | Moved between 2018 (05:23) and 2202 (13:50) on 10-09, across versions that 45-game online totals could not tell apart |

### T1. Measure the noise floor of an instrument before deciding with it

**Rule.** Run the same build twice through the instrument. The spread you see is the smallest difference the instrument can report.

**What happened.** The limit was written down three times before it was obeyed: "45 games cannot separate the two" (10-06, `S/docs/HANDOVER-2026-10-06.md` §3); "30 games only catch a difference of 6 wins or more" (10-07, `HANDOVER-2026-10-07b.md` §6); "do not conclude from a 15-game difference" (10-08, `HANDOVER-2026-10-08.md` §9). On the last night versions one1 to one10 were nevertheless each read from one or two 15-game sets, because allowance was short and a decision was wanted every half hour. At 05:23 the live bot was rolled back two versions on "3 of 15 against 8 of 15"; a control run of the older bot then scored 4 of 15 and the rollback was withdrawn at 06:01. An analyst then confirmed the opponent had not changed and concluded that every single-set verdict of the night "may be within noise" (06:11). `[R]` The rule was known; what was missing was a second instrument cheap enough to use instead, which is why 3.1 lists costs.

**Depends on.** High game-to-game variance. Ours came from hidden information, 15 different maps and opponents that mostly beat us; a game with a lower variance would have a lower floor.

### T2. Judge by behaviour for "did it work", by a powered comparison for "is it better", and say so when you cannot tell

**Rule.** Three different questions need three different instruments. (a) Did the mechanism fire and do what it was built for: behaviour counts. (b) Did it break anything: per-map health numbers and identical-replay checks. (c) Is the bot stronger: a paired comparison with enough games, or a large head-to-head. For most single changes the honest answer to (c) is "cannot tell", and the change is kept or dropped on (a) and (b).

**What happened.** jun set this early: "win rate is not a criterion... numbers are poison", after catching reports phrased as local win counts (09-30 and 10-01, `S/archive/claude-memory/online-feedback-mechanism-check.md`). His estimate was that about 20 stacked mechanisms move results against top teams, so gating each one on wins stalls everything. The record supports the first half: local win counts did mislead (T4), and the one bundle that was stacked on behaviour checks alone was also the one clear measured gain of the contest (23% to 38%, above). It also shows the limit: behaviour checks alone passed every version of the last night, and it took outcome counts on newly generated maps (01:38, 04:17) and 48-game head-to-heads (06:40 to 07:26) to show that the versions after one5 were no better than one5 on new maps (one8 against one5 20-2-26, one11 against one5 21-2-24). The form that worked on the last morning was the three-instrument split above.

**Depends on.** How many changes you expect to need. If one change can decide games, test it on outcomes.

### T3. Online comparisons need both sides from the same hours

**Rule.** Opponents upload new bots at any time. A baseline older than a few hours is a different opponent.

**What happened.** 10-06: a merge was held because the candidate scored 4 of 15 against a team whose baseline, from the evening before, was 8 of 15. That team had changed its bot overnight (rating 2109 to 2215); re-run in the same hour, the plain bot scored 2 of 15 `[M: S/archive/claude-memory/same-hour-baseline.md]`. The rule "re-run the baseline in the same hours" followed. It was dropped by jun on 10-08 19:59 because a baseline costs half the allowance ("tickets are very valuable; judge growth from the new bot's own games"). It came back at 05:40 on 10-09 after the wrong rollback in T1.

`[R]` Both decisions were reasonable when made. The way out that emerged late: (1) ranked battles that other teams request cost no allowance and arrive all day, so the live version's own incoming games are a free, continuous baseline if every game is stored with the id of the bot that played it; (2) health numbers per map are far less noisy than wins, so they can be compared across hours when wins cannot.

**Depends on.** A ladder where opponents can change at will and games against a chosen team are rationed.

### T4. Local head-to-head has blind spots; know them before trusting a "neutral"

**Rule.** A local comparison is only as wide as its maps and its opponent. Write down which map families and which opponent behaviours it does not contain.

**What happened** `[M]`.
- *It understated a real gain.* The seven-switch bundle beat the old bot only 35 of 64 locally (55%), and only 6 of 18 on large held-out maps; online it took the win rate against two fixed teams from 23% to 38% (`S/docs/SESSION-STATE.md`, 10-08 06:35 and `HANDOVER-2026-10-08.md` §3.3). Our own bot as opponent did not create the situations the ladder did.
- *It hid two harmful switches.* A leave-one-out test (remove one switch, play 44 to 46 games against the full version) rated five switches neutral, 21 or 22 wins each side (09:01). Two of the five were doing real damage online. The 24 generated maps had portals in only one family, so the portal rule never mattered there; the territory change hurt on one ladder map that was not in the local set at all (11:06 entry).
- *Seat decides symmetric maps.* When two versions behave identically the first mover wins on many symmetric maps, so 46-4-46 can mean "no behavioural difference at all" (08:09).
- *It cannot show what the opponent does not do.* Queen-protection switches showed nothing until a local opponent that hunts queens was built (10-08).

**Depends on.** Having a second, different local opponent would remove part of this. We had an old version of ourselves, a queen-hunting variant and one "red team" bot.

### T5. After every upload, read health numbers per map and per version

**Rule.** Keep one table: rows are maps, columns are versions, cells are a few early-game health numbers from that version's online games (we used pearls eaten and dragons alive at r50 and r100, first portal crossing, first queen split, queen death round). A cell that halves is a bug until shown otherwise. Remove the suspect switch locally on that map to confirm.

**What happened** `[M: S/docs/SESSION-STATE.md, 10:24, 11:01, 11:40 entries; S/data/codex/astra/regress/report.md]`. Version one12 (07:08) added five switches on a local head-to-head that stood at 40-3-29 when it was uploaded and ended 50-5-41. Code changes were frozen at 09:01 with its successor live. At 10:05 an analyst was started on six losses to weaker teams and reported a starving side; the per-map numbers were then recomputed: pearls by r100 on six portal maps, one11 to one13: 238 to 71, 41 to 4, 59 to 30, 92 to 36, 58 to 32, 112 to 66; maps without long portals unchanged. Cause: `PORTAL_SCOUT_MIN_LEN 4` kept short dragons out of any portal nobody had seen through, and since nobody went through, nobody ever saw. Removed at 10:24, 19 minutes after the analyst was started; eight local games on two of those maps then showed pearls by r100 more than doubling. A full table (435 games, 21 numbers, 15 maps, 10 versions) at 11:01 pointed at one more map; removing switches one at a time there showed `TERRITORY_DECAY 16` leaving the side at 2 to 3 dragons at r100 (8 pearls with it, 44 without). Removed at 11:44; over 32 local pairs on ladder maps that second removal alone took wins from 15 to 22. The session's own note: "not comparing versions per map was the mistake of one12 and one13".

**Depends on.** A fixed, known set of ladder maps to use as columns, and health numbers that respond in the first 100 rounds. Transfers to any game where the opening has a measurable economy.

### T6. Check that the game lasted as long as your metric assumes

**Rule.** Before reading "total by round N", check how many games ended before N.

**What happened.** One map's "pearls by r100" stayed low (40) after the fixes and was announced to the team as unexplained. Two of the three games had ended at r47 and r39 because we had wiped the opponent out; the total stopped there. Measured at r50 the map had recovered (50.0 against 25.4) `[M: S/data/codex/astra/trophy-sonnet/table.txt, 12:05 entry]`. The older method notes already listed "filling early endings with later survival" as an anti-pattern (`S/docs/PHILOSOPHY.en.md`).

**Depends on.** Games that can end early. Ours ended on a wipe-out; any game with an early win condition has the same trap.

### T7. Attribute every game to the bot that played it, from the replay

**Rule.** Never infer the version from the clock. Read the submission id out of the replay and keep a table from id to version name.

**What happened.** The server fixes the bot for a ranked battle when the battle is requested, not when it is played. A 4-1 win was reported to jun as the new version's; the replay ids showed the previous version had played it (12:02). An online set that straddled an upload mixed two versions. Earlier, comparison runs of the old main bot showed up in the public battle list under our team name and jun asked why the bot had regressed (`HANDOVER-2026-10-08.md` §9). The fix was `S/data/online/smoke/versions.tsv` (one line per upload) and a collector that stores each battle with the bot id.

**Depends on.** Replays that carry the submission id. If they do not, log upload times and never upload while a test run is in progress.

### T8. Choose the opponent panel on purpose

**Rule.** Test against three or more teams just above you that play differently, and require "not worse against any of them". Drop opponents that cannot separate your builds.

**What happened** `[M]`. Against the organisers' test bot (rated about 2417 against our 1850 to 2100) four versions of the last night won 1, 1, 4 and 0 of 15, so it said nothing (Zhe had said so on 10-06: "too op for our tests"). One top-15 team returned 3, 1, 4 and 3 wins for four different versions. One lower team that hunted queens returned 9, 10, 12 and looked like progress until jun and Zhe asked whether we were overfitting to it (05:34); it then returned 10, 8, 8, 6 and 10 for the next versions. The panel from 05:34 on: three teams of different styles just above us.

**Depends on.** Being able to choose opponents. The panel must be re-picked as our own rating moves.

### T9. Verify one key number of every delegated analysis before acting

**Rule.** An analyst's report (human or AI) is a lead. Recompute its central number from the raw games yourself, or reproduce its central case locally, before building on it.

**What happened.** About 30 entries of the log record a correction or a withdrawal, ours or an analyst's `[M: grep of S/docs/SESSION-STATE.md for 정정, 틀림, 철회, 실수; counted by me]`. Typical ones: "11 wipe-outs" was both sides added (ours: 5); "deaths with no action" was a feeding rule, not a timeout; a split "within the same map" was two maps with different start lengths pooled; team ids were posted as ranks. The portal fix in T5 was shipped only after the analyst's hint had been recomputed from cached rows by the main session.

**Depends on.** Delegating analysis at all. The more analysts run in parallel, the more this check is the bottleneck, and it should be budgeted as such.

## 4. Building and shipping

### 4.1 The upload routine used on the last day

Every one of the last eight uploads went through these steps `[M: S/docs/SESSION-STATE.md, e.g. 12:51 and 13:31 entries; scripts in S/archive/final-session-scripts/]`:

1. Diff the candidate source against the current source: only the intended lines.
2. Build with every switch off: binary hash equals the reference hash of the old program.
3. Build with the live version's values: binary hash equals the live version's binary.
4. Build with the new values: binary hash equals the binary that was actually tested.
5. Compile check in the upload folder, upload, compare the server's copy with the folder, read back the active id.
6. Post to the team what changed, why, and the id to go back to.
7. Add the id to the version table; update the profile file in the team repo (the profile applied to the repo source must diff to zero lines against the uploaded folder).

### B1. Default-off switches, proven by hash

**Rule.** New behaviour goes behind a compile-time constant that is off by default, and the all-off build must be byte-identical to the previous program. If the compiler produces a different binary for equivalent code, prove equivalence by replaying fixed games and comparing the replay files byte for byte.

**What happened.** The all-off hash `92fb69564fbd` was checked at every merge from the evening of 10-08 to the final upload, across more than 2,500 added lines `[M: the pull request for version one13 alone was +2,523/−93]`. It caught a real break once: a builder's wrapper function and a rewritten condition changed the all-off binary (07:14); the work was not usable until fixed. In jun's earlier phase a "disabled" change had silently reduced search depth (`S/docs/PHILOSOPHY.en.md`, switch discipline). When two sources with the same values gave different binaries, eight games were replayed and differed only in the two bytes of the bot's name (11:56).

**Why it made the last day safe, and what "safe" covered.** Eight uploads between 10:24 and 14:49 produced no crash and no doubt about what was live, and both harmful switches were removed by one-line edits. The discipline proved "this is the program we tested and nothing else changed". It did not prove "this is better": the last three versions had zero online games before the deadline, and the very last was checked on four short local games (lesson S6).

**Cost.** The source grew to 8,657 lines with 423 constants (`B/mybot2/main.cpp`), the final profile has 49 values (`B/work/server_profile.txt`), and interactions between switches were tested only once, by leave-one-out. jun's note: reconsider the switch-everything rule at each big refactor (`S/archive/claude-memory/one-model-live-1008.md`).

**Depends on.** A compiled bot with deterministic builds, and a deterministic game. With a nondeterministic engine, use the replay comparison on fixed seeds or a decision-trace diff.

### B2. One source, one profile, and the repo default equals the live bot

**Rule.** Keep a single bot source in which everything is off, plus a small text file of the values that are live. Generate the upload from the two. Check "repo equals server" with a tool at the start of every session and after anyone uploads by hand.

**What happened.** 10-04: the team repo's default constants were an old configuration, the loop had been testing cards against it, and the results for two cards were invalid (`S/archive/claude-memory/loop-spec-1004.md`, 18:06). From then on main's defaults had to equal the live release, checked with `S/tools/submit.js check`. From 10-08 the team repo held the all-off source plus `B/work/server_profile.txt` and `B/work/server_bot.py`; teammates' cards and the solo switches shared one base and merged as pull requests #58 to #62. At the last fetch the team's main branch held the profile of version one14; the final version's code and profile are on branch `one15-profile` (commit 44fae14); whether it was merged afterwards is not recorded.

**Depends on.** More than one person or session able to change the bot. A solo author with one branch needs only the profile file.

### S1. Rollback is a human decision; the default direction is forward

**Rule.** Automation uploads and never reverts on its own. When a result is bad, find the switch that is not doing its job and fix or remove it; go back to an old bot only when the new one is broken (crashes, timeouts).

**What happened.** jun set "upload only, rollback is my call" on 09-30 and "no going back to the old bot; fix the switch that fails" on 10-08 22:2x (`S/archive/claude-memory/upload-only-rule.md`, `one-model-live-1008.md`). The one rollback of the last night (05:23) broke that rule and was wrong (T1). The two real regressions were both handled forward, by removing one switch each.

**Depends on.** Switch discipline (B1): going forward is only cheap when the suspect change can be removed alone.

### S2. The live bot can change under you

**Rule.** Read back the active id after every upload, before every test run and before the deadline. Leave a teammate's manual switch alone and record it.

**What happened.** At 04:34 on the last night an older version became active with no record in our tools; jun said it was not him; who made the switch was not established. It played two ranked battles (both lost 1-4). A new upload appears to start from the rating of whatever is active at upload time, and the next version started at 2077 instead of the 2108 the intended version had reached `[M: 04:44 entry; the inheritance rule itself was seen in a few cases, not confirmed]`. A server-side verification also failed once right after an upload ("could not be extracted"); the copy check showed the upload was in fact intact (00:10).

**Depends on.** A server where any team member can activate any stored submission from the website.

### S3. Know how the rating is stored before spending effort on it

**Rule.** Read the rating mechanics from the server's own data in the first days.

**What happened.** On 10-06 a night of online tests seemed to have cost rating (1883 to 1841) and this was written down as a cost of testing. The API showed the same evening that the rating is kept per submission: a test bot plays on its own number and the main copy keeps its number while idle (10-06 20:55, `same-hour-baseline.md`). That allowed the "ratchet": two copies of the same code, the higher-rated parked and untouchable, the lower one playing, swapped automatically when the playing copy led by 5 (`S/tools/park_watch.py`, from 10-07). Whether the ratchet gained rating overall: not measured. jun declared rating parking no longer meaningful on 10-08 14:50, when the live bot became something that changed often. A new submission moved 24 to 33 points per ranked battle against 2 to 10 for one with hundreds of games, so `[R]` uploading 21 versions in 16 hours also meant playing every ranked battle at the most volatile setting.

**Depends on.** A per-submission rating. On a per-team rating none of this applies and every test game costs.

### S4. A loss to a weaker team is the expensive event

**Rule.** Every game lost to a team rated 100 or more below us gets its cause found.

**What happened.** One 2-3 battle lost to a team 165 points lower cost 98 points; a 3-2 win over such a team paid about 25 (`S/archive/claude-memory/weak-loss-rule.md`, 10-09 02:52). All ten such losses that night had our queen dead; in six the enemy queen survived to the end with total lengths level or in our favour. `S/tools/weak_watch.py` started one analyst per battle. Several of the day's real findings came from this stream, including the portal bug. `[R]` In a best-of-seven on unseen maps one silly loss matters in the same way, so the rule fits the format and not only the ladder.

**Depends on.** A rating system that punishes upsets, and enough analyst capacity to read every such game.

### S5. Ranked battles for seeding, with the numbers

**Rule.** Do not request rating games late unless the expected value has been worked out from our own record against that team, and remember that other teams can challenge you while your tickets are tied up.

**What happened** `[M: S/docs/SESSION-STATE.md, 13:48 to 14:59]`. At 13:48 jun proposed using ranked battles to raise the seed. The server does not allow a challenge to a team more than 50 points below, so "hunting weak teams" was impossible; the targets were teams we had beaten more often than the ratings predicted.

| Time | Battle | Result | Rating change |
|---|---|---|---|
| 13:50 | Team SKKU (our request) | 4-1 | +71, to rank 23 at 2202 |
| by 14:00 | Team SKKU again (ours) | 3-2 | 0 |
| by 14:00 | Computers (their request) | 2-3 | −28 |
| by 14:11 | Sponge, rated 2431 (ours) | 0-5 | −49 |
| by 14:11 | Check Raise (theirs) | 3-2 | −25 (a win that lost points; why is not recorded) |
| 14:26 to 14:37 | SKKU, test4, Cybers (ours) | 3-2 each | +26, +13, +20 |
| 14:26 to 14:37 | the uncancelables, Ballers (ours) | 2-3, 1-4 | −36, −31 |
| 14:30 | BambooCode (theirs) | 4-1 | 0 |

Start 2131 (rank 36), deadline 2092 (rank 41). Our own requests summed to +14, battles requested by others to −53. One more battle against Team SKKU, requested at 14:46, was still being played at the deadline (two losses and a win so far) and is not in these sums. The judgment "losing to a much stronger team costs almost nothing" was wrong by 49 points. At about 13:58 jun said "this is risky" and requests paused; at 14:26 he asked to resume. Final seed: 39.

**Depends on.** Seeding read from the final rating (Zhe's statement; never verified by us), a fresh submission whose rating moves 24 to 33 points a battle, and a win rate of 18% against teams rated 2250 or more and 37% against 2100 to 2250 (`S/docs/SESSION-STATE.md`, 11:50 entry). With those three, late rating games are a coin flip with a negative mean.

### S6. Decide the deadline rule early, and write down what the late uploads were checked for

**Rule.** Agree in advance what may still change after the freeze ("only a confirmed bug"), what check a late change must pass, and who says "stop".

**What happened.** The plan written on 10-08: freeze new switches at 09:00, final combination by 11:00, live at 12:00, and "never upload a combination that has not run online right before the deadline" (`HANDOVER-2026-10-08.md` §2). Actual: the freeze was declared at 09:01 and eight versions followed it. The first two removed the harmful switches of T5, so holding the freeze would have submitted a damaged bot. The next six added behaviour: one16 at 12:51 (30-of-30 queen deaths on one map, reproduced, mechanism then confirmed in online games), one17 at 13:31 (21 cases in 474 games), one18 at 14:10 (three online games, one local reproduction), one19 at 14:36 (four changes from the unseen-map round, an independent review and a control-flow audit), one20 at 14:43 (two completions; 17 local games identical to one19), one21 at 14:49 (a teammate's report minutes earlier; four short local games). At 14:57 jun told the team that every change had been confirmed to improve the bot; the session told him that this was stronger than what had been checked: for the last three versions only "plays the same games as before on the test set" was established.

`[R]` Both things are true: the freeze as planned would have been worse, and the last three uploads were bets. A rule of the form "after the freeze, removals of a confirmed regression only; additions need N online games" would have kept the first two and forced a decision on the rest.

**Also.** Two of our own tools had the freeze date hard-coded and blocked all online tests from 20:00 to 22:13 on 10-08, because only one person was allowed to change the guard (`S/tools/smoke.py`, `B/work/loop/runner.py`). Put dates in one config file. The server began refusing uploads from an older client version on 10-08; keep the client current.

**Depends on.** A hard submission deadline with no measurement possible afterwards. Where the final can still be patched between rounds, the trade is different.

## 5. Unseen maps

### U1. No per-map logic, from the first day

**Rule.** No map names, no per-map constants, no layout-specific code, and no verdict that rests mainly on the public maps.

**What happened.** jun's earlier bot recognised maps and looked up tables. The sprint bracket on 10-01 was played on fully custom maps ("completely different maps... optimising by map is not right"), recognition was switched off, and one bundled map had been misrecognised as another (`S/archive/claude-memory/qualifier-timeline.md`). The rule became mandatory for the new team on 10-03 (`no-fixed-map-optimization.md`).

**Depends on.** The organisers saying, or showing, that the finals use new maps. Check how earlier rounds were run before building anything map-specific.

### U2. Size thresholds are cliffs; find them early and replace them

**Rule.** List every place the code branches on map size or shape. Each is a cliff on a map just across the line. Prefer signals measured in the game (first contact round, distance to the enemy start, open space per unit).

**What happened.** On 10-03 a review of the base bot listed its thresholds: queen rules only above 600 cells (three ladder maps have 512), centre pull at 700 and 1000, big-map mode at 1200, a 6.5-step target horizon, an orientation-dependent test (`width >= 2*height`), and noted "on Portals our queen dies at round 9 in 11 of 34 games" (`S/docs/reports/overfit-traces-2026-10-03.md`). jun's rule the same day: replace size steps with game-state signals, one gate at a time (`known-map-preserving-rule.md`). The last-day audit still lists the 600, 1000 and 1200 lines; I found no record of a gate replaced by a game-state signal. On the last day the same items were rediscovered by fresh analysts: the 600-cell test behind the round-9 queen deaths (12:43, six days later), the 6.5-step horizon (13:57), the 1000-cell cliff (a bot that never leaves a closed start room at 1012 cells and leaves at r22 at 968 cells; patched at 14:36 by raising one constant). Sound messaging between dragons stops on maps with a side of 129 or more; open at the deadline.

`[R]` The lesson is less about maps than about lists: a known-issues file that is re-read when choosing work would have saved the rediscovery.

**Depends on.** Inheriting a bot tuned on a fixed map pool. A bot written from scratch for unseen maps should have no size constants to begin with.

### U3. Generate map families, not map counts

**Rule.** Build a generator that covers families (open, corridors, islands, portals, closed rooms, tiny, huge, long and thin), and a second small set made to break the bot at each threshold. Check coverage by family before trusting a "neutral".

**What happened** `[M]`. Held-out generated maps were used for the loop's win-count tests from 10-03. The first structured sets came on the last night: 64 maps in 8 families from 49 to 65,536 cells (01:38, `R/maps/gx/`), 33 threshold probes (01:42, `S/data/codex/astra/unseen/maps/`), and three groups of eight "break it" maps (13:50, `R/maps/un2/`, brief `S/data/codex/astra/UNSEEN-BRIEF.md`). What they showed:
- 01:38: the live version lost 31-3-40 to our own old bot on the 64 new maps while winning 12 to 14 of 16 on the familiar eight. On 7x7 maps one switch alone turned 6-4-6 into 2-1-13.
- The 24 maps used for head-to-head had one portal family, which is why the portal bug of T5 was invisible locally.
- 13:59 to 14:31: on 49 to 63-cell maps the live bot lost 3 of 3 to the old bot before r25; in closed start rooms the queen circled for 57 rounds; one generated map exposed `QUEEN_DEAD_ALL`, live for 13 hours as "harmless, rarely fires" (15 of 16 local games identical when it went in). Turning it off doubled pearls by r100 over 20 pairs (522 to 1036) with no pair worse.
- No crash and no timeout in any of it, up to 65,536 cells.

**Depends on.** A map format you can write and a local engine. The red criteria we used are reusable: crash or timeout, first pearl after r40, three or fewer dragons at r100, queen suicide before r50, more than 10% of dragon-rounds in a no-eat loop.

### U4. Refactors keep known maps replay-identical; real fixes may change them

**Rule.** Two tiers. A generalisation must leave every known map's replay unchanged and may only change behaviour where the old tuning never reached. A real fix may change play on known maps but must show no large loss there and a gain in its target situation. Rules must not depend on orientation; test on rotated and transposed copies of the known maps.

**What happened.** Agreed with QWQ on 10-03 (`known-map-preserving-rule.md`); transposed copies of the test sets were added the same week. `[R]` The first tier was enforced (it is the hash rule of B1). The second had no agreed measure of "no large loss" until the per-map table of T5.

**Depends on.** A base bot that is already strong on the known maps and cannot be rewritten in the time left.

### U5. Maps rebuilt from replays are for relative comparison only

Seven ladder maps were rebuilt from replays at 11:32 on the last day. Walls, portals and starts are exact; pearl supply is estimated from one game's sightings. One fix that worked as designed showed no gain locally because of it (13:57). Do it in the first week, and collect pearl timing over many replays.

## 6. Team process

### P1. Human ideas first; AI findings go to people as data

**Rule.** The shared loop carries the teammates' ideas. Findings from automated studies are posted as numbers and replays, and a person decides what becomes a card.

**What happened.** 10-05: AI-written cards were taking turns in the single build-and-test queue from Zhe's and QWQ's cards; jun archived all AI cards, later his own too, and took the infrastructure role (`humans-first-1005.md`). `[R]` It kept two strong teammates engaged and in charge of direction. The other side: from 10-07 evening jun ran a separate "solo project" in which an AI session stacked switches from replay diagnoses with only behaviour checks as the gate, and by 10-08 jun judged that the team's result rested mostly on it (`solo-project.md`). Its first bundle is the one measured gain in 3.1. The merge path between the two lines was the all-off source and the profile (B2).

### P2. The card loop

**What it was.** One GitHub issue per idea; labels as a state machine (ready, questions to the author, building, author looks at replays, testing, tested, candidate, kept or rejected); a runner script that waits on games and calls a model only when a state changes; the build gate "switch off equals the old program"; merge needs the author plus one more approval (`loop-spec-1004.md`, `B/work/loop/`).

**What worked.** Ideas were built while their authors slept, up to nine hours apart, and any teammate could answer the loop's questions on another's card so the queue kept moving (`proxy-answers.md`). Every card left a build that was provably inert when off. Every teammate's work stayed visible.

**What did not.** The result test was local win counts over hundreds of game pairs against our own bot, and it mostly returned "no difference": 199 against 194 over 400 pairs, 391 of 400 pairs identical, +21 −20 `[M: HANDOVER-2026-10-07.md §6, SESSION-STATE.md]`. The single local game slot was the bottleneck `[M: humans-first-1005.md]`, and a card usually needed several build-and-look rounds before its result test. How long a card took on average, and a tally of cards by outcome: not recorded in the files I read.

**Next time.** Keep the state machine and the inert-build gate; replace the win-count result test with D3 (did it change decisions) and T5 (did any map break), and send survivors to a paired online run in bundles.

### P3. A promises ledger

Every "I'll..." said to teammates went into `S/docs/PROMISES.md` with a number, to be closed as done or corrected in public. 69 entries in seven days (numbered to P73); most are closed, a few early ones were still open at the end. jun's reason: he did not want to say things in the channel and drop them (`discord-promises.md`). Cheap, and worth repeating as is.

### P4. Session-state memo and handovers; the cost of long sessions

**Rule.** The directing session writes down state as it goes (what is live, what is running and how to restart it, rules changed today, open decisions) and is replaced by a fresh session about once a day, from a written handover. After any context compaction, treat remembered numbers as leads and reopen the file.

**What happened** `[M]`. 10-07: the main session reached 340k tokens of context and each wake-up re-read about 1M tokens (`session-state-memo.md`). 10-08: handover "to save tokens; the previous session's record is 18 MB". 10-09 00:39: 134M tokens re-read by the main session in under seven hours, and jun's weekly limit at 17% with 14 hours to go. Six handovers were written (`S/docs/HANDOVER-*.md`); each next session started from the document, the rule files and one project instruction file. What a handover shortens gets lost: one of them cut the model-assignment table to a single line and the next session broke the rule (`main-session-master-workbench.md`), so standing rules are copied in full. A hands-on rule followed from the same cost: the directing session decides and delegates, it does not edit and count inline (`main-session-master-workbench.md`).

### P5. Facts from the source, clock from the clock

Numbers, ranks and times that go to teammates are read from the file or the server at the moment of writing. Incidents: team ids posted as ranks (10-08 18:22); a line count guessed in a pull request (23:08); guessed timestamps, several times (`HANDOVER-2026-10-08.md` §9). Each was corrected in public within minutes, which is the other half of the rule.

### P6. Every wait needs an end condition on your side; know the machine

- A builder's games finished at 19:31 and nobody looked until 22:10 because the report never arrived (10-08). The analysis service hit its usage limit and four analysts sat dead while only their report files were being watched (01:12); again for 20 minutes at 07:14. Rule adopted: watch the result files *and* the process count, from the directing side.
- Restarting a paused analysis loop released its whole backlog at once: about 65 jobs, 264 processes, load average 210 (11:03). Another overload at 05:03 (load 76).
- The engine's lock allowed two games at a time machine-wide (set on 10-07 to protect the card loop's games; `HANDOVER-2026-10-08.md` §4.1 says so). The last day's batches assumed more until an analyst pointed at the lock at 13:52. Raising it to 7 gave load 44 to 51, because each game uses 4 to 5 cores (every dragon is a process); it was set to 4.
- A builder ran a pattern-based kill and wiped the local game queue (19:06). Rule: stop processes by id only.

### P7. Teammates are the brake; timezones are a schedule

Autonomy for the AI sessions was widened step by step and always inside one limit: a teammate's objection stops it, and merging a card needs its author (`autonomy-within-teammate-hypotheses.md`). Times given to a teammate are in their zone. Nobody is tagged outside their waking hours. `[R]` With three people in three zones and seven days, this is what let work continue around the clock without anyone being overruled while asleep.

**What section 6 depends on.** A small team spread over time zones, with AI sessions doing most of the hands-on work and one person directing them. The ledger, the corrections habit and the end conditions on waits transfer to any team. The card loop and the handover routine are worth their overhead only when work must continue while people sleep or when sessions are too long-lived to trust from memory.

## 7. Day one of the next contest: checklist

**Read and measure (first day)**
1. Read the rules for how the final is played: map pool (seen or unseen), match length, tie-breaks, seeding. Read how earlier rounds were actually run.
2. Read the rating mechanics from the server's data: per team or per submission, what a new upload starts from, what a loss to a weaker team costs, who can challenge whom.
3. Find the rationed resource (ours: 60 online games an hour, shared with incoming ranked battles) and plan the test budget around it.
4. Measure the local rig: games in parallel, cores per game, minutes per game on the largest map. Check for hidden locks.
5. Check that the engine is deterministic. If it is, "identical replay" becomes your cheapest test.

**Build before the bot (first two days)**
6. Switch scaffold: every behaviour behind a default-off constant; a script that builds a named variant from "name = switch:value, ..." and prints its binary hash; a reference all-off hash.
7. One source plus a profile file plus a script that makes the upload folder; a "repo equals server" check.
8. Upload script that ends by reading back the server copy and the active id, and appends to a version table (id, name, time, profile).
9. A collector that stores every game we play, online and ranked, with the id of the bot that played it.
10. Replay parser, then three reports: loss classification by cause; per-map, per-version health table; a behaviour counter that takes a switch name.
11. A decision trace: for one dragon at one turn, the score of every candidate move by term.
12. Map generator by family, plus a small "break it" set at every size or shape threshold in the code. List those thresholds in a known-issues file.
13. At least two local opponents that play differently from our own bot.

**Calibrate (before the first verdict)**
14. Run the same build twice through every instrument and write down the spread. Decide how many games a version verdict needs.
15. Pick the online panel: three teams just above us with different styles. Drop any that all our builds lose to or that never move.

**Rules to agree with the team (first meeting)**
16. Who may upload, who may roll back, and that the default is forward.
17. Freeze time, what may change after it (removal of a confirmed regression only) and what check a late addition needs.
18. No per-map logic if the final is on unseen maps.
19. How ideas are tracked, who approves a merge, and that anyone may answer a blocked question for a sleeping author.
20. A promises ledger and a correction habit: wrong numbers are withdrawn in the same channel.

**Every day**
21. Re-rank losses by cause; pick the biggest class with a traceable cause.
22. For each change: decision-change count, identical-replay check elsewhere, per-map table after upload.
23. Run the generated and "break it" maps on whatever is live.
24. Re-read the known-issues file before choosing work.
25. New directing session from a written handover.

## 8. Things we never resolved

- **How to rank two versions cheaply.** The only clear version-level result of the contest cost 180 online games. The last 13 versions were, by our own measures, indistinguishable from each other online (17, 14, 18 and 21 wins of 45 for four of them). We do not know whether one21 was stronger than the version of sixteen hours earlier; local head-to-head between the early and late versions was level (25-2-21 at best).
- **Whether stacking small behaviour-checked changes works.** jun's estimate was that about 20 are needed before results move. The first 8 moved them (23% to 47% against two fixed teams over 30 to 90 games). The next 40 values did not visibly move them. Whether that is a ceiling of this bot's design, interference between switches, or the noise floor: not established.
- **The early economy gap.** Measured in detail (pearls by r100 114 against 162; first-turn split rate 48% against 93%; time spent in narrow cells 9% against 16%), cause not found in code.
- **Queen survival.** Dead in roughly three games of four in every version. The late finding that the lever is "where she lives, not which step she takes near an enemy head" was never built. Known open cases at the deadline: walking one step toward a visible enemy head (19 of 21 queen deaths against one opponent), shrinking in place through a second split branch, a mate closing her last exit.
- **Unseen-map classes left red:** 7x7 and similar tiny maps, closed start rooms where the queen stays behind, a room whose only exit is a portal with an unseen far side, sound messaging off on maps with a side of 129 or more, an unbounded search in one queen-exit check.
- **Opponent modelling.** Five per-opponent analysts in the last half hour all answered "no constant to change". Whether adapting to an opponent inside a best-of-seven is possible at all in this format was not explored.
- **The value of the rating ratchet and of ranked scrims for seeding.** The first was never measured; the second lost 39 points on the one afternoon it was tried.
- **What the bracket maps were and how the bot behaved on them.** Not recorded. Without it we cannot say which of the lessons in section 5 actually decided the result.
- **Whether switch-everything should survive a rewrite.** It bought safety and cost a source of 8,657 lines with 49 live values whose interactions were tested once.

## 9. Sources

| What | Where |
|---|---|
| Chronological log of the last three days (Korean) | `S/docs/SESSION-STATE.md` (sections "meow-main06", "meow-main07") |
| Handovers, each with a "traps" section | `S/docs/HANDOVER-2026-10-05.md` to `-10-09.md` |
| Standing rules jun gave, one per file, each with its reason | `S/archive/claude-memory/` |
| Method notes from the earlier solo phase | `S/docs/PHILOSOPHY.en.md`, `S/docs/STATE.md`, `S/DECISIONS.md` |
| Size-threshold review of the base bot | `S/docs/reports/overfit-traces-2026-10-03.md` |
| Card ledger of the last night (live, building, dropped, open) | `S/data/codex/astra/CARDS.md` |
| Analysts' outputs cited above | `S/data/codex/astra/<name>/` (regress, early-opus, qexit-opus, qdead-opus, h2hloss-opus, loss15-sonnet, trophy-sonnet, late-opus, unA-opus to unD-opus) |
| Online comparison of the first bundle | `S/data/analysis/ladder/dossier/online/agg7.md` |
| Version table, uploaded bot folders | `S/data/online/smoke/versions.tsv`, `S/data/online/smoke/one<N>-bot/` |
| Last-day scripts and switch lists | `S/archive/final-session-scripts/` |
| Final source and profile | `B/mybot2/main.cpp`, `B/work/server_profile.txt`, `B/work/server_bot.py` |
| Promises ledger | `S/docs/PROMISES.md` |
| Team channel mirror | not published |

### Appendix: switches turned on and off again during the last 16 hours

All `[M]` from `S/docs/SESSION-STATE.md`; hours are time live.

| Switch (what it did) | On | Off | Hours | Evidence used to turn it on | How the harm was found |
|---|---|---|---|---|---|
| `QS_KEEP_ROUND 20` (queen may split early) | 00:10 | 00:49 | 0.7 | A builder's local games: more dragons until r40 | One online set: queen at length 2 in 28% of her turns against 4 to 5%; an analyst confirmed it in 12 of 15 games |
| `RALLY_END_FRESH 25`, then 5 (late gathering toward the longest dragon) | 01:35 | 06:01 | 4.4 | One analyst card and 16 local games | Generated maps: 14-2 without it, 8-7 with it |
| `SHORT_EVADE` (short dragons dodge reachable cells) | 02:31, again 04:00 | 03:09, 06:01 | 2.7 | An analyst's count: 329 of 559 hits had a free escape | Online hit rate unchanged; changed 0.10% of turns |
| `QUEEN_PORTAL_ALL` (queen never takes a portal) | 04:35 | 06:01 | 1.4 | One loss report | One analyst report of less eating on small maps; later shown to fix one map and break another |
| `QS_KEEP_MIN_UNITS 6` (queen splits while the team is small) | 04:00 | 08:07 | 4.1 | 22 local games on two-dragon-start maps: 13.3 dragons at r100 against 10.6 | 48-game head-to-head 29-2-17 for the old value; queen at length 2 in 31% of her first 100 rounds against 13% |
| `PORTAL_SCOUT_MIN_LEN 4` (short dragons avoid unseen portals) | 07:08 | 10:24 | 3.3 | An analyst's count of 2,005 avoidable portal deaths | Per-map table: pearls by r100 collapsed on six portal maps |
| `TERRITORY_DECAY 16` (near ground weighs more) | 07:08 | 11:44 | 4.6 | Local sweep on 1024-cell maps: +2 to +9% length at r150 over 16 games (it had read +10 to +17% at 8 games) | Per-map table, then single-switch removal on one map |
| `QUEEN_DEAD_ALL` (queen dead-end rule on every map size) | 01:35 | 14:36 | 13.0 | "Harmless, rarely fires": 15 of 16 local games identical | Bisection on a generated map; 20 pairs with it off: pearls by r100 522 to 1036 |
