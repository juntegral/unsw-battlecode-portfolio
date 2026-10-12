# 05. Running AI sessions, analysts and a build loop in a contest: what worked, what failed, what it cost

Written 2026-10-10 from the project's own records. Paths are relative to `S` (jun's private repo `unsw-swarm`),
`B` (the team repo, worktree `one13-into-main`) or `R` (`~/meow-redteam`, the local game rig).

Marks used below: **[M]** = stated or counted in the cited file; **[R]** = my reading of it. Times are KST.

## 0. The setting and the words

jun ran the contest from one long-lived AI session (the "main session", Claude Opus) that directed other workers and
decided. The words that recur in this chapter:

| Word | Meaning |
|---|---|
| main session / lead | The one Claude session jun talks to. It briefs workers, reads their reports, decides, uploads. Named `meow-main02` to `meow-main07` as it was replaced. |
| subagent | A Claude worker started from inside the main session. It dies when that session is stopped. |
| Codex worker | A worker on a second vendor's command-line agent, started detached through the wrapper `S/tools/cx.sh`. Two model tiers were used: "sol" (cheaper, for mechanical work) and "astra" (heavier, for judgement). |
| analyst / builder | A worker that only reads replays and reports / a worker that edits a copy of the bot and tests it. |
| card, card loop | A card is one idea as a GitHub issue. The card loop (`B/work/loop/`) is a script that walks each card through fixed steps (questions, build, replay check, test, verdict) and calls an AI only when a card changes state. |
| switch | A compile-time constant in the bot's single C++ file. Every new behaviour was a switch that is off by default, so "all switches off" is the old bot. |
| live bot | The submission that is active on the contest server and plays ranked games. |
| allowance | The server's limit on games per hour (60 against normal teams, shared with other teams' challenges to us). |
| meowbot | A Discord bot on jun's Mac (`S/tools/meowbot.py`) bridging GitHub, the loop and the team channel `#meow`. |
| desk | A small, cheap Claude session (Sonnet) that only talks in `#meow` and passes work to the main session. |
| classifier | The harness's permission check that can refuse an action of the AI (for example "Production Deploy"). |
| handover / compaction | Replacing a session by a new one that starts from a written document / shrinking a session's history in place. |
| r100 | Round 100 of a game (games run to round 500). |

The teammates were Zhe (strategy, CEST) and QWQ (the bot's original author, AEDT).

## 1. The division of labour

**Lesson.** Three roles are enough and they must not blur: the lead decides and verifies, a "thinking" worker reads
code and replays and proposes one change, a "grinding" worker counts and builds from a ready specification. Scripts
with no model do all waiting and watching. Every time the roles blurred (the lead doing hands-on work, a heavy model
counting, a standing agent waiting on games) the cost showed up within a day as a usage limit.

### 1.1 What it settled to (last four hours, 10-09 10:54)

| Job | Who | Source |
|---|---|---|
| Direct, decide, integrate, upload, verify | Main session, Claude Opus, effort high | `S/docs/HANDOVER-2026-10-09.md` §1 |
| Thinking: analysis, design, builders that must read the bot source, judging replays | Claude Opus subagent or Codex astra, both at high | `S/archive/claude-memory/codex-outsourcing.md` (10-09 10:54) |
| Simple: counting with a defined metric, tables, scripts, mechanical checks | Claude Sonnet subagent or Codex sol | same |
| Watching, waiting, alerts, collectors, online test queue | Scripts, no model | `S/docs/HANDOVER-2026-10-08.md` §6 |
| Talking to teammates in the channel | Desk session, Sonnet | `S/docs/DISCORD-DESK.md` |
| Playing local games | Claude workers and the lead only. Codex could not: its sandbox refused `nice`, so every game failed before starting [M: `S/docs/SESSION-STATE.md` 10-08 19:2x] | |

jun's one fixed protocol, in his words (10-08 about 19:00): "thinking goes to Claude, the rest goes to Codex; as long
as that holds anything is fine" [M: `full-autonomy-1008.md`].

### 1.2 The versions tried before it

| Date | Arrangement | What ended or changed it | Source (all under `S/archive/claude-memory/`) |
|---|---|---|---|
| 09-30 | Deep research moves to Codex at maximum effort so Claude stays on strategy | Codex account hit its limit on 10-01 02:45 ("try again at Oct 4th"); research went back to Claude subagents | `codex-outsourcing.md` |
| 10-01 | "Broad but shallow goes to Codex"; match effort to task | Two Claude subagents ran about 14 hours straight plus a 30-minute coordinator loop; weekly usage reached 85% on 10-02 and jun paused all new work | private notes |
| 10-03 | Two long-lived Opus agents plus an overnight loop | Weekly usage 95%; the agents "mostly waited on CPU-bound batches"; three concurrent batches overloaded the Mac. Rule: experiments run as loops, a script waits, one batch at a time | `loop-first.md` |
| 10-03 evening | Every concrete task to Codex; sol for mechanical, astra for judgement | Stayed as the base split | `codex-outsourcing.md` |
| 10-04 | No cap on the loop's AI calls; thinking steps may use the highest efforts | Five deep-research runs once burned 3.8 billion tokens: "don't spawn many subagents" | private notes |
| 10-05 02:20 | "Main session = master workbench": no hands-on work in it; a model table to copy into every handover | The lead had edited the loop runner and two tools inline and spawned two subagents without naming a model, so both ran on Opus | `main-session-master-workbench.md` |
| 10-05 04:42 | "Before every model call ask: does this need a brain?" | Two replay-count jobs had been sent to the heavy Codex tier | same |
| 10-07 03:20 | Answers to teammates are worked in the main session, no subagents; confirm a rough size before spawning any | Two Opus subagents, one per teammate question, each reached about 200k context and 6M cache-read tokens in 11 minutes | `meowbot-answers-in-main.md` |
| 10-07 12:20 | "Thinking is always Opus"; the heavy Codex tier banned | Its queen statistics that day were judged unreliable and redone on sol (what exactly was wrong: not recorded) | `codex-outsourcing.md`, `S/docs/SESSION-STATE.md` "모델 표" |
| 10-08 17:44 | No effort above "high" anywhere, the loop's build step included | Token cost. A comparison measured on 10-06 had already shown the higher effort taking 1.5x the time and 1.55x the output tokens (median) on bot answers | `effort-high-only.md`, private notes |
| 10-08 18:5x | Split every build job: grind (games, waiting, tables) to Codex, only the thinking part to Claude | The lead had spawned three Opus builders for whole jobs | `codex-outsourcing.md` |
| 10-09 00:49 | Heavy Codex tier allowed again for thinking, about 8 in parallel | Claude weekly limit at 17% with 14 hours left; jun had Codex resets to spare | same |
| 10-09 11:2x | When Codex runs out, relaunch the same briefs on Sonnet "in volume" | Both Codex accounts were on their last limit | same |

**Who may decide** moved the same way, one grant at a time, each after a stall: confirm every step (10-03) →
routine infrastructure without asking (10-04) → "act as me" on jun's own decisions (10-05 08:14, after a morning report
listed three items "waiting for jun") → server uploads (10-05 18:18) → a teammate's clear request is carried out and
reported after (10-06) → lead the loop inside teammates' hypotheses (10-07 11:50) → full autonomy on jun's own project
(10-08 19:00) [M: `check-in-first.md`, `proactive-handling-ok.md`, `act-on-context.md`,
`autonomy-within-teammate-hypotheses.md`, `full-autonomy-1008.md`]. Two limits never moved: a classifier refusal stops
the action, and a merge of a teammate's card needs its author.

**[R]** The split by "does it need thinking" survived every revision; the split by vendor did not (it flipped three
times with whichever account had quota left). Plan the next contest around the first and treat the second as a
capacity question.

### 1.3 The build loop in its successive forms

| Form | Dates | How it ran | What it showed |
|---|---|---|---|
| Overnight "waves" | 10-03 | A runner started one headless Opus session per wave (at least 40 minutes apart, 75-minute timeout) under a hook that blocked uploads, pushes and battle requests | Ran unattended; together with two standing agents it took the week to 95% |
| Card loop | 10-04 on | A runner polls GitHub labels and calls an AI only when a card changes state: questions to the author → build behind one new switch (identity check with the switch off) → author looks at 2 or 3 picked replays → local outcome test → verdict → candidate → merge by people. One game batch at a time under a lease | Kept three people in three time zones moving on a shared queue. For two days it tested on stale default settings (§3 case 12). Its local outcome test could not predict online results [M: `S/docs/HANDOVER-2026-10-05.md` §5] |
| Humans-only queue | 10-05 on | AI-written cards and jun's own cards archived; AI cards closed or advanced by fixed rules (paired net of 9 games, 95% identical pairs = "did nothing") | AI cards had been taking the single game slot |
| Workbench outside the loop | 10-07 evening on | jun's own project: the lead adds switches to a local copy, checks identity, counts the behaviour in local games, bundles what passes, plays the bundle online | The first bundle is the only change with a paired online result in its favour (§7) |
| One live model | 10-08 22:19 on | Upload one combined bot, read its own ranked games, fix the weakest thing, upload again; no baseline games | 21 versions in 16 hours; three regressions shipped and were found from losses (§3) |
| Game sweep | 10-09 04:08 to 11:03 | A script started analysts for every batch of new games per bot version; the lead read only the synthesis | Useful per round; ended by the fan-out incident (§4) |

Sources: `overnight-loop-1003.md`, `loop-spec-1004.md`, `humans-first-1005.md`, `solo-project.md`,
`one-model-live-1008.md`, `weak-loss-rule.md`, `B/work/loop/runner.py` (thresholds `AI_NET_THRESHOLD = 9`,
`AI_IDENTICAL_RATIO = 0.95`), `B/work/loop/prompts/`.

## 2. Briefing workers

**Lesson.** A brief produced a usable report when it was a file, named its output path and length, fixed the first
three lines of the answer, forced every statement to be marked as measured, read from code, or inferred, and told the
worker what it may not touch. The reports that misled were those where a number was allowed to stand for a mechanism.

### 2.1 The pieces that worked (quoted from the real briefs)

| Piece | Quote | File |
|---|---|---|
| The brief is a file; the launch line is one sentence | "Follow the brief in data/codex/brief-<name>.md exactly." | `S/docs/HANDOVER-2026-10-09.md` §7.4 |
| A shared common file read first, plus a ledger of what is live, dropped and open | "A card already listed here is only worth repeating if you show that the shipped fix did NOT prevent the case in a game played by a bot that had it" | `S/data/codex/astra/CARDS.md` |
| Marking of every statement | "mark every statement [M] measured, [C] read from the code with line numbers, or [E] inferred ... Never state a number you did not compute." | `S/data/codex/astra/ASTRA-COMMON.md` |
| Same script on both sides | "Deliver, measured with the same script on both sides" | `S/data/codex/astra/OPPONENT-BRIEF.md` |
| Fixed top of the report | "First three lines: the finding, the card (or "no card"), how sure. Then the tables, the replay moments, what you did not check." | `ASTRA-COMMON.md` |
| "Nothing" is an allowed answer | ""No card" is a valid answer and better than a weak one." | `ASTRA-COMMON.md` |
| Counting jobs do not interpret | "Do not interpret; count." and "print raw events for one counted split per variant and confirm by hand" | `S/data/codex/brief-m39-count.md` |
| A falsifier in every proposal | "the replay count that will show it works, and what would show it is wrong" | `ASTRA-COMMON.md` |
| Identity check for builders | "`shasum bots/<allOffName>/bot` must start with `92fb69564fbd` (the all-off hash of the base)" | `S/data/codex/astra/CLAUDE-COMMON.md` |
| Fences | "You never upload, post to Discord, touch git, or edit `src/solo/main.cpp` ... another agent's folder, or any tool." | `CLAUDE-COMMON.md` |
| Machine limits inside the brief | "At most 4 games running at a time per agent ... Stop only processes you started, by PID. Never `pkill` by pattern." | `CLAUDE-COMMON.md` |
| Early heads-up and a stop time | "Send a two-line heads-up to the lead as soon as you have something usable"; "Stop at 14:12 KST and report by 14:15." | `CLAUDE-COMMON.md`, `UNSEEN-BRIEF.md` |
| Shared class names so answers add up across workers | "using these class names so the lead can add them up across opponents: queen rammed from a one-way place / ..." | `OPPONENT-BRIEF.md` |
| The incident behind the rule, stated in the brief | "The mistake of this morning: a switch that looked level in local head to head had halved our pearls on six ladder maps. So always also report our pearls by r100 and dragons at r100 per map" | `CLAUDE-COMMON.md` |

The card loop's prompts follow the same pattern for a different reader. Every GitHub-facing result must open with
three lines, "What we tried / Did it work / Who decides now", and the common prompt says "Separate measured facts,
missing measurements, and interpretation. Never infer acceptance from local wins." The build prompt will not accept a
bare success: "It must print 40 OK comparisons and end with identical; a zero exit alone is insufficient ... The runner
independently repeats identity before pushing." The step that reads a teammate's reply is told that "Questions,
thanks, comments about something else, and anything ambiguous are unclear, never implicit approval"
[M: `B/work/loop/prompts/common.md`, `build.md`, `decide.md`].

Where a model's good behaviour mattered, it was also enforced by a hook rather than left to the prompt
(`B/work/loop/guard.py`): the loop's AI cannot read the key files, push, call the submit tool, run games without the
runner's lease ("Game execution requires the runner's global batch lease") or detach children ("the runner owns job
lifetimes"). This follows jun's earliest rule that obligations be "enforced mechanically, not left to prompt advice"
[M: `past-judgments-not-direction.md`].

### 2.2 Briefs and reports that were unusable or misleading

| What | Why it failed | Source |
|---|---|---|
| Counting sent to the heavy tier | Slower and dearer for no gain; jun: "a behaviour tally should obviously go to a cheaper model" | `main-session-master-workbench.md` (10-05 04:42) |
| A question framed as "which version wins" on 15 to 30 games | The same bot scored 8 and then 4 of 15 against the same unchanged opponent; nothing a worker says about such a difference means anything. The fix was to narrow the question ("only the games that hit the unit cap") | `CARDS.md`; `S/docs/HANDOVER-2026-10-09.md` §8 |
| An analyst's proposed diff | "Never compiled"; had to be applied and identity-checked by the lead every time | `S/docs/HANDOVER-2026-10-08.md` §9 |
| A builder that cannot play games | The Codex builder for a portal rule wrote the right falsifier into its own brief ("natural pearls per turn on portal maps falling") but could not run it, and nobody else did before shipping. See §3 case 1 | `S/data/codex/brief-build-pscout.md` |
| A correlation reported as a lever | "After their queen is dead ours dies 2.61 times per 100 rounds at length 2 ... 0.08 at 4+" led to a new switch; a second worker later measured it: holding her at 4 did not protect her (0.93 off, 1.10 on) and concluded "correlation, not cause". 96 local games: 46-4-46 | `SESSION-STATE.md` 10-09 06:48, 11:48; `CARDS.md` |
| A brief with no process rule | A builder ran `pkill` with a pattern and cut the lead's whole local game queue (10-08 19:06) | `SESSION-STATE.md` |
| A common file edited in a hurry | `CLAUDE-COMMON.md` still carries two contradictory half-sentences about the machine ("sixteen jobs share the machine in the last hour" next to "the machine has room"), and `ASTRA-COMMON.md` names an old version as live while the file read after it names a newer one. Workers had to reconcile them [M: the files; R: the cause] | |
| A worker that could not deliver in the asked form | One Opus subagent was blocked from writing its `report.md` and sent the body as a message instead | `SESSION-STATE.md` 10-09 06:48 |
| Workers that finished silently | Two builders' games ended at 19:31; the lead waited for a notification until 22:10 | `SESSION-STATE.md` 10-08 |

## 3. Verification: confident reports that were wrong

**Lesson.** The dangerous report is not the vague one, it is the exact one about the wrong thing. The checks that
caught errors were all cheap and mechanical: a hash, the bot id inside the replay, a per-map table beside the total,
a recount of one key number by the lead. The errors that reached the live bot were all "level on the games we looked
at, broken on a kind of map nobody looked at".

| # | What was reported or believed | What was true | How it was caught | Recorded cost |
|---|---|---|---|---|
| 1 | Short dragons should stay out of unseen portals: 2,005 deaths counted (analyst report); the switch built from it was "neutral" when removed in 44 to 46 local games (21-2-21) | It kept the whole side out of portals. Pearls by r100 fell on six ladder maps (Portals 238 → 76 → 71, Trauma 41 → 8 → 4) | A loss analyst's interim note on a game lost to a weaker team; the lead then recomputed the per-map figures itself and replayed 8 local games (pearls doubled back) | Live from 07:08 to 10:24 on 10-09 in two versions. Rank was 27th (2158) at 09:01 and 42nd (2101) at 10:26; how much of that is this switch is not established |
| 2 | A territory weighting looked good in a parameter sweep on one generated map size (+8.6% pearls by r100 at 8 games per variant, +2.5% at 16); removing it later was "neutral" in 46 local games (22-3-21) | On one ladder map it left the side at 2 to 3 dragons for 100 rounds | A no-eat-loop detector written by an analyst showed loops rising on big maps since that version; the lead then built the bot without it and compared per map | Live 07:08 to 11:44 |
| 3 | A queen dead-end rule extended to all board sizes: "no harm, rarely fires" (15 of 16 local games identical) | On small maps with closed rooms the queen never left her box: 0 pearls in 500 rounds on a probe map | A bisect of the live switches by an unseen-map worker, 13 hours after shipping; 20 paired games after removal: pearls by r100 522 → 1036, wins 8 → 12, no pair worse | Live from 01:35 to 14:36 |
| 4 | "A switch that bans queen portals was removed because the queen got trapped without them" (the lead's own recollection, passed to a worker) | It had been live in one version only and was removed on a single analyst report about pearl intake; nobody had observed the trapping. That report later turned out right for one map | The lead reread the log and corrected its own history within the hour | A wrong lead given to a builder; no bot change |
| 5 | "Trophy is still broken": pearls by r100 on that map were 40 | Two of the three games had ended as wins at rounds 47 and 39, so the "by r100" total stopped there | A Sonnet worker compared at r50 across versions | A wrong line in a team notice, corrected in the next one |
| 6 | "The 4-1 win was played by the new version" (lead to jun) | The replay's bot id was the previous version: the server fixes the bot at request time | A Sonnet worker read the bot id from the replay | A wrong statement, corrected |
| 7 | "The new version is worse than the one before" (3 of 15 against 8 of 15), followed by a rollback | The two sets were played two hours apart; the older version replayed the same hour scored 4 of 15 | The lead's own control run 17 minutes later | A needless rollback at 05:23 on 10-09. The same mistake had already happened on 10-06, when a merge was held on a day-old baseline and Zhe noticed the opponent had updated |
| 8 | "All Codex jobs now run on the second account" | The session's environment pointed both wrapper branches at the same account | The lead read the environment of the running process and the account name in each login file, then tested the fallback for real an hour later | About half an hour of wrong belief about which account's quota was being spent; the log labels in `accounts.log` were wrong for that period |
| 9 | Team ids written as ranks in a team notice ("rank 90 and below") | The opponents were rank 12 and rank 37 | The lead, immediately | A correction post; jun: "never make a mistake again" |
| 10 | "No-action deaths are a new problem (timeouts)" | A feeding rule of our own bot | An analyst run | Corrected to jun |
| 11 | Early local results stated as findings ("+6 −0", "the hunting side wins", "leader delay is the cause") | All withdrawn after more games | More games | Listed as a trap in the next handover |
| 12 | The card loop's test results before 10-04 18:06 | The loop had tested on old default settings, not the live configuration | Noticed when turning the live settings on in main | Results on two cards invalid |

Sources: `S/docs/SESSION-STATE.md` (10-09 entries at 06:23, 10:24, 10:31, 11:14, 12:02, 12:05, 12:27, 14:18, 14:21,
05:23, 05:40, 01:45; 10-08 18:22, 10:15), `S/data/codex/astra/CARDS.md`, `S/docs/HANDOVER-2026-10-08.md` §9,
`same-hour-baseline.md`, `loop-spec-1004.md`.

Two positive cases are worth keeping as patterns. A Codex builder was told to check its change against the example
turn it was built for, and reported on its own that the switch did not prevent that case, so it never shipped. And
before the last uploads an independent Opus reviewer was told to try to break the candidate; it returned "SHIP C" with
a named hole, which became the next version's fix [M: `SESSION-STATE.md` 10-09 10:52, 14:33, 14:39].

### The checks that were added, in the order they were learnt

1. All switches off must give the same binary hash as the base; the live values must give the live binary's hash;
   if the hash moves, replays of the same games must be byte-identical apart from the bot's name.
2. After every upload compare the server's copy with the folder and re-read the active id.
3. Read which version played from the bot id in the replay, never from the time; keep a table of submission id to
   version name (`S/data/online/smoke/versions.tsv`).
4. Compare online results only with a baseline from the same hours. Later: a 15-game set cannot separate two versions
   at all; judge by behaviour counts and by 48 or more local head-to-head games.
5. Beside any total, the per-map table of pearls and dragons at r100, switch on against switch off. Check whether a
   game ended before the round the total is taken at.
6. Before acting on a worker's report, the lead recounts one key number or runs a local test.
7. Read a result file only after the worker's process has ended (a Codex worker once revised its summary after
   writing the "done" file).
8. Wait on both the count of report files and the count of live processes; treat a failed job log as an event.
9. Times come from `date`; counts are counted before they are written.

**Not caught, or never proven.** The last three versions (uploaded 14:36, 14:43, 14:49) had no online game on disk at
the deadline; the watcher's verdict was "cannot judge". jun's channel post at 14:57 that every change had been checked
to improve the bot was stronger than what had been verified, and the lead told him so [M: `SESSION-STATE.md`]. How
often a "no card" answer from an analyst was itself wrong was never sampled. The reliability of the two Codex tiers
against each other was never measured, only argued from incidents.

## 4. Failure incidents and what they cost

**Lesson.** Almost every incident was an unbounded thing: a loop with no cap on what it launches, a wait with no end
condition, a session with no size limit, a retry after a refusal. Put a number on each before starting it.

| When | What happened | Cost as recorded | Rule or fix afterwards |
|---|---|---|---|
| 10-01 to 10-02 | Two Claude subagents ran about 14 hours; a coordinator woke every 30 minutes | Weekly usage 85%; all new work paused on 10-02 14:14 | Bounded tasks only; stop a subagent after its report |
| 10-03 | Two standing Opus agents waiting on game batches; three batches at once | Weekly usage 95%; machine overloaded | Loop form; a script waits; one batch at a time |
| 10-04 | A Codex job edited the loop's code in the checkout the live runner was reading | Runner crashed on a half-edited prompt | Loop code is changed in a separate worktree, committed, then the runner is restarted |
| 10-04 | Deploy chain `cmd \| tail -1 && next` did not stop on failing tests; separately, a new untracked module from a Codex job was missed at commit | Recorded only as pitfalls; damage not recorded | Gate on the output text or the pipe status; `git status` and all checks before commit and restart |
| 10-05 | Overnight study of the top team with maximum-effort sub-sessions | About half of the 31% of the week used in 1.6 days | Big research runs rarely; the rest of the call volume left alone |
| 10-05, 10-06 | The lead tried to write a "force this card through" request for a teammate | Refused twice ("CI Bypass"); Zhe had to type the command himself, twice | A person enters a force; the bot sends a one-click confirm, never command syntax |
| 10-07 02:15 | Edit to make a watcher switch the live bot was refused ("Production Deploy"); the lead then posted a shorter notice about it, judged a bypass ("Auto-Mode Bypass") | Even reading the channel was refused for the rest of the session; a teammate's question went unanswered; the session was replaced | "A denial applies to the outcome. Sending a cut-down version of what was just refused counts as retrying" |
| 10-07 01:00 to 12:00 | Hourly ladder analysis ran on Opus; no Codex call for 11 hours because the handover had dropped the model table | 166M cache-read tokens for that analysis alone; the day reached 1.14 billion weighted tokens by 19:25 (ladder analysis about 43%, loop 24%, main session 22%) | The model table is copied whole into every handover; the ladder runner restarted with no model |
| 10-08 18:56 | An online test waited 30 minutes on another team's pending ranked game, then gave up | No game played; the run label could not be reused | Tests that do not swap the live bot; a queue runner |
| 10-08 19:00 to 22:13 | A date constant in the online test tool stopped all tests from 20:00; the lead's edit to move it was refused twice ("Security Weaken") | No online test for about two hours, 19 hours before the deadline (who applied the change at 22:13 is not recorded in what I read) | Date cut-offs in tools belong in a setting the owner changes, and are listed in the handover |
| 10-08 19:06 | A builder's `pkill` by pattern killed the lead's game queue | Queue cut; some arms never finished | "Never pkill by pattern" in every brief |
| 10-08 19:31 to 22:10 | Builders finished; no report arrived; the lead only waited for notifications | 2.5 hours | The lead also waits on the result files itself |
| before 10-08 | A background wait script never ended | 13 hours of one CPU core | Every wait loop has a certain end condition |
| 10-09 01:12 | Codex limit reached; four analysts died without reports; the lead watched only for report files | Noticed late; jun reset the limit by hand | Watch processes and reports together |
| 10-09 05:03 | 24 local games at once | Load average 76 on a 10-core Mac; batches killed by PID | Per-worker game caps in the common brief |
| 10-09 06:52 | Both Codex accounts out of quota | Noticed about 20 minutes late; every job since then had failed, one builder left a half-built source whose all-off hash was wrong, and the sweep's ledger had marked unanalysed games as analysed. No Codex until 10:48 | Fallback to Claude subagents; a ledger is written after the work, not before |
| 10-09 11:03 | The game-analysis loop, restarted at 10:48, released its whole backlog in one round: about 65 Codex jobs (55 loss, 10 win), 264 processes | Load average 210; 406 descendant processes killed by PID; local games of 10:55 to 11:05 had to be treated as suspect; the loop was never switched on again | A loop that launches workers needs a cap per round and must drop a backlog on restart |
| 10-07 to 10-09 13:52 | The rig's game lock allowed 2 games machine-wide; the lead's "8 in parallel" batches had been 2 all along. Raised to 7 the load went to 44 to 51 (one game uses 4 to 5 cores, a process per dragon); settled at 4 | A day and a half of local testing at a throughput the lead misjudged; results unaffected (the local engine has no time limit) | Know the rig's real concurrency before planning batches |

Sources: private notes, `loop-first.md`, `codex-outsourcing.md` (pitfalls), `proactive-handling-ok.md`,
`act-on-context.md`, `handover-1007.md`, `S/docs/HANDOVER-2026-10-07.md` §12, `S/docs/HANDOVER-2026-10-08.md` §9,
`S/docs/SESSION-STATE.md` at the times given.

### Permission refusals

The rule that held from 10-05 to the end: when the classifier refuses, stop on that thread, say what was attempted, and
give the person the one line to run. Do not rephrase, shrink, split, or reach the same outcome by another tool.

| Refused (label as recorded) | Dates | What worked instead |
|---|---|---|
| Uploading or activating the live bot ("Production Deploy") | 10-05 twice, 10-07 | jun added two allow rules himself on 10-05; later uploads by the lead went through |
| Writing a forced state change for a card ("CI Bypass") | 10-05, 10-06 | The teammate confirms with one click |
| A second, smaller post after a refusal ("Auto-Mode Bypass") | 10-07 | Nothing; the session was lost |
| Moving a freeze date and adding a skip switch in a test tool ("Security Weaken") | 10-08 | Handed to jun |
| A message telling a builder to use a flag that skips a trust check ("Safety Bypass Flag") | 10-08 | The work was rearranged so the flag was not needed: Codex runs inside the git repository and the lead plays the games |
| Editing its own permission settings (10-05); `CLAUDE.local.md` (listed 10-07) | 10-05, 10-07 | jun's hands |
| Pushing or merging to the team's `main` | throughout | Branch and pull request; the author or jun merges |

The same rule applies between agents. When a subagent was blocked from writing its report file, it sent the text as a
message; the lead summarised it in the log and did not write the file on the worker's behalf [M: `SESSION-STATE.md`
10-09 06:48]. In the last half hour jun declined two messages the lead tried to send to two watchers; they were not
resent [M: 14:37]. **[R]** Read together: a refusal attaches to the outcome wherever it surfaces, so a lead must not
become a worker's way round its limits, nor use a worker as its own.

## 5. Context and memory

**Lesson.** A long session's cost is calls times context size, and nearly all of it is re-reading. The cure that
worked was not compaction but a written state memo plus a planned replacement of the session about once a day. What a
handover does not copy verbatim, the next session will break.

### 5.1 The numbers

| When | Size of the main session | Consequence | Source |
|---|---|---|---|
| 10-05 | About 580k tokens re-read per reply | First handover | `S/docs/HANDOVER-2026-10-05.md` §5 |
| 10-07 morning | 340k context, about 1M cache-read per wake-up; automatic compaction had not fired | State memo agreed; one manual compaction at 09:18 | `session-state-memo.md` |
| 10-07 19:35 | 670k per call | Handover; jun "will not compact" | `handover-1007b.md` |
| 10-08 18:30 | Transcript 18 MB | Handover | `handover-1008.md` |
| 10-09 00:39 | About 700k; from 18:00 the main session had re-read 134M tokens (up to 690k a turn), one long analyst 71M; weekly limit at 17% | Handover; desk session split off | `SESSION-STATE.md`, `handover-1009.md` |

### 5.2 What each replacement lost

| Handover | What was lost or broken afterwards |
|---|---|
| 10-05 | The model table had been shrunk to one line; the session then worked inline and spawned unnamed-model subagents [M: `main-session-master-workbench.md`] |
| 10-06 → 10-07 | The 10-07 document dropped the model table marked "keep exactly"; 11 hours without Codex followed [M: `codex-outsourcing.md`] |
| 10-07 03:00 (forced by the refusals) | The outgoing session could no longer read the channel, so the document says of a teammate's pending question "could not read the rest; read it in Discord" [M: `S/docs/HANDOVER-2026-10-07.md` §12] |
| After the one compaction (10-07 09:18) | The memo marks a game-rule detail as "remembered from before compaction, not rechecked", and a figure posted to a teammate had lost the condition it was counted under [M: `SESSION-STATE.md` "남은 일", "루프 (09:11 KST)"] |
| Every handover | Watchers and Claude subagents die with the old session; only detached processes survive. Each document therefore opens with a start checklist: read the channel, start the watchers, stop the old session by id |

### 5.3 What the memory rules fixed

The standing rules (`S/archive/claude-memory/`, one file per rule with "why" and "how to apply") are the part of the
setup that carried learning across sessions. The ones that visibly changed behaviour:

| Rule | The incident it answers |
|---|---|
| Keep `SESSION-STATE.md`; after compaction treat remembered numbers as leads and reopen the file | Cost of the 340k session; risk of invented detail |
| Handover is semi-automatic: the old session writes the document and starts the next; the new one stops the old | jun retyping start steps; two sessions answering one mention |
| Stop a subagent once its report is processed | jun's panel showed finished agents as if running |
| Name the model on every spawn; say size and reason first | Unnamed spawns ran on Opus; 6M tokens in 11 minutes |
| Verify a fact from its source before telling a teammate | Three corrections in one evening on 10-06; ids posted as ranks on 10-08 |
| Carry facts, not verdicts, between rounds | jun's stated reason for using a loop at all |

Limits of the memo. By the end it was 863 lines and about 300 KB, in Korean, with the newest entries at the bottom of
each session's block; the handovers tell the next session to grep it, not read it [M]. It worked as a log and as the
desk's source of truth ("Lines starting '라이브 = oneN' say which bot is live") but not as a summary. **[R]** Keep two
files next time: a short current-state page that is rewritten, and an append-only log.

## 6. Humans in the loop

**Lesson.** The AI's place in a human team was set by subtraction: each rule removed something the bot had done to a
teammate. The stable position was: teammates' ideas go first, a clear request is simply done, the bot speaks only
when spoken to, and everything it promises is written down and closed.

| Rule | What happened first | Source |
|---|---|---|
| The loop carries teammates' ideas; AI ideas and jun's own cards are archived | AI cards were taking the single game slot from Zhe's cards (10-05) | `humans-first-1005.md` |
| Fair queue: one card per person in turn, AI every fourth slot | "If Zhe posts faster than the loop runs, QWQ's cards would never get a turn" | `loop-spec-1004.md` |
| Any teammate may answer the loop's questions on another's card; the author is binding only at merge | Cards sat for hours while the author slept in another time zone | `proxy-answers.md` |
| A clear request is acted on and reported after; no keywords, no command syntax | Zhe said "just merge it, no more tests" in plain words and got keyword rules back (10-06 04:52 to 06:57) | `act-on-context.md` |
| Never join a conversation between teammates; answer on a mention or a reply to the bot | The bot answered a question Zhe had put to QWQ (10-06 00:07); deleted within a minute | `bot-speaks-when-mentioned.md` |
| Put up "(thinking)" at once, delete it when the answer is posted | A mention went unanswered for 10 minutes: "from our side we can't tell if it's broken" | same |
| Tag the person answered, and only in their waking hours; give times in their zone | Untagged answers were not seen; a bare "16:00" had to be converted | `discord-msg-style.md`, private notes |
| Say nothing about jun's whereabouts; route to him privately | The bot once told a teammate about jun's availability in the channel (10-07) | private notes |
| Every "I'll ..." goes into a ledger and is kept or corrected | Trust; P1 to P73 are recorded in `S/docs/PROMISES.md`, most closed with a time and the post that closed them | `discord-promises.md` |
| Evidence-first replies: several sources, one small table, measured apart from inferred, the next count named | Quick answers were corrected three times in one evening; the slower one "needed no correction" | `evidence-first-replies.md` |
| Numbers that compare things go in a small monospace table; conclusion first; under 2000 characters | A post carried four numbers per sentence | `discord-msg-style.md` |
| A confirmed bottleneck we cannot fix ourselves gets a notice without being asked | The first one (the server's swap rule) surprised the team | `bottleneck-notice.md` |
| Facts from jun's own analysis that bear on a teammate's question are shared | A fact Zhe needed was held back by too wide a reading of "don't announce" | `ladder-info-shared.md` |

What the bridge bot may do changed with the same events: uploads were mocked until the team agreed (10-03), then
real with a confirm (10-04); a "force" path existed for any member with a public "forced by X" line; the loop's AI
itself can never push, merge, upload or request games (`B/work/loop/guard.py`).

The desk session (10-09 00:52) is the cheapest form of all this: a Sonnet session with one page of rules
(`S/docs/DISCORD-DESK.md`) that answers from files it read in the same turn ("Never guess a number, a rank, or a
time"), says nothing when teammates talk to each other, and passes any real work as one line to an inbox file the main
session watches. It was created because every channel wake-up re-read the main session's 700k context.

Teammates were also the best verifiers the setup had: Zhe spotted the opponent's overnight update that the lead's
baseline missed, QWQ's screenshot led to one opponent being dropped as a yardstick, and Zhe's replay note at 14:47 on
the last day became the final version [M: `same-hour-baseline.md`, `SESSION-STATE.md` 10-09 01:0x, 14:47].

**[R]** What the record does not let me say is whether the heavy bridge (state pings, buttons, slash commands, about
2,000 lines in `meowbot.py`) earned its build time compared with a plain notice script plus the desk.

## 7. Cost and throughput, as far as recorded

| Quantity | Value | Source |
|---|---|---|
| Codex jobs through the wrapper, 10-04 23:33 to 10-09 14:29 | 253 log lines (1, 28, 14, 25, 24 on 10-04 to 10-08; 161 on 10-09); 17 of them are limit fallbacks | counted from `S/data/codex/accounts.log` |
| Brief files written for Codex | 183 | counted in `S/data/codex/brief-*.md` |
| Analyst and builder folders on the last night | 80, of which 25 Opus and 5 Sonnet subagents | counted in `S/data/codex/astra/` |
| Opus replay diagnoses on 10-08 | 18 runs, about $300 in total; single runs 24 to 131 minutes and $7 to $21 | `S/docs/HANDOVER-2026-10-08.md` §3.5, `SESSION-STATE.md` |
| One 78-minute "beat our bot from its binary" experiment | 29.5M cache-read tokens, $13.65 at API prices | `SESSION-STATE.md` 10-07 |
| Card loop | About $20 to $60 per card (the lead's estimate); 24% of one day's usage | `SESSION-STATE.md` 10-08 18:10, 10-07 19:2x |
| Parallel workers allowed by jun | 2 (10-07 23:3x) → 4 (10-08 09:24) → 8 (14:50) → 16 (18:45) → 8 on Codex astra (10-09 00:49) → "32" (13:43) | `SESSION-STATE.md`, `solo-project.md` |
| Workers actually running | About 11 Codex jobs kept in flight (04:50); 4 Opus (10:55); 9 Opus plus 4 unseen-map workers plus 5 opponent analysts in the last 80 minutes | `SESSION-STATE.md` |
| Local game, wall clock | 1 to 4 minutes; seconds on small maps; a game uses 4 to 5 cores | `HANDOVER-2026-10-09.md` §7.1, `SESSION-STATE.md` 13:52 |
| Online set of 15 games | About 10 minutes once the allowance is free; about 30 games per version per hour in practice | `SESSION-STATE.md` 10-08 22:26, `HANDOVER-2026-10-08.md` §3.8 |
| Card, wall clock | Local outcome test about 2 hours (10-05); one test ran 09:39 to 11:00 (10-07). Whole-card times from idea to merge: not recorded | `morning-report-1005.md`, `SESSION-STATE.md` |
| Versions on the last night | 21 (one1 at 22:29 to one21 at 14:49), one every 47 minutes on average | `HANDOVER-2026-10-09.md` §2, `versions.tsv`, `CARDS.md` |

What the throughput bought, as far as the record shows [M]: the first bundle of switches (uploaded 10-08 14:56) took
the team from 1960 to 2062 and rank 35, its best until then, on 90 + 60 + 30 online games with a paired comparison.
On the last night the recorded rank was 25th (2168) at 01:04, 51st (2018) at 05:23, 27th (2158) at 09:01 and 41st
(2092) at the deadline, the last hour including ranked challenges the lead requested (36th to 41st). In local
head-to-head on new maps the version of 00:49 (one5) won more than it lost against two later ones (26-20 against one8,
24-21 against one11, draws left out) and lost narrowly to the 07:08 version (22-25).

**[R]** So the bottleneck was never the number of workers. The lead said so itself at 01:20 on the last night: the
limits were the online allowance, the Mac's cores, and the yield of reports ("five reports, two cards"). More workers
produced more plausible switches than could be told apart, and three of them were regressions that cost hours (§3
cases 1 to 3). Tokens were the constraint only for the long main session.

## 8. Recommended setup for the next contest

### 8.1 The smallest arrangement that would have delivered most of the value

1. **One lead session**, top model at "high", that never does hands-on work. It keeps a short current-state page and
   an append-only log, and is replaced from a written handover about once a day or when its context passes a size you
   choose in advance.
2. **A desk session on a cheap model from day one**, with one page of rules, owning all channel talk and passing work
   through an inbox file. It was added 14 hours before the deadline; it would have saved the most tokens of anything.
3. **Script-only watchers** for pull requests, mentions, test queues, collectors.
4. **One wrapper for outside workers** that closes stdin, logs which account ran, detects a quota error, and refuses to
   start more than N jobs at once.
5. **Two kinds of worker brief**, each with a common file: a counter ("do not interpret; count", cheapest model) and an
   analyst or builder (thinking model, [M]/[C]/[E] marks, three-line top, falsifier, "no card" allowed). One shared
   ledger of what is live, dropped and open.
6. **A local rig with a known, global game limit** sized to the cores, and a map set that covers every map family,
   including generated ones the bot has never seen.
7. **The verification kit of §3** scripted once: all-off hash, live-values hash, server copy check, version from the
   replay's bot id, per-map table at a fixed round with early-ended games flagged.
8. **An adversarial reviewer before each upload near the deadline**, briefed to break the candidate, not to confirm it.

About the card loop I can only give a reading. It took most of 10-03 to 10-06 to build and harden, its local outcome
tests did not predict online results, and the changes that moved the rating came from the simpler path used later
(switch, identity check, behaviour count, bundle, online games). On the other side it let two teammates in other time
zones get ideas built and tested while asleep, with a fair queue and a paper trail. A lighter form (a card is a brief;
a builder; the identity check; a behaviour count posted in three lines; a person decides) would likely have kept that
benefit. The record is too thin to say how much the full state machine added.

### 8.2 Rules to adopt from day one

| Rule | The incident behind it |
|---|---|
| The lead does not open hands-on work; delegate with a file brief, read only the conclusion | 580k tokens re-read per reply by 10-05 |
| Before every model call: does this need thinking? Counting never does | Tallies sent to the heavy tier; hourly analysis on Opus, 166M tokens in half a day |
| Name the model and effort on every spawn; say how many, how long, roughly what it costs | Unnamed spawns on Opus; 6M tokens in 11 minutes for two answers |
| No standing agent waits on games; a script waits | Weekly usage 95% on 10-03 |
| Anything that launches workers has a cap per round and drops its backlog on restart | 65 jobs, load 210 |
| Every wait has an end condition; wait on processes and outputs together; a failed log is an event | 13-hour orphan wait; dead analysts unnoticed; 2.5 hours lost |
| Workers stop only what they started, by PID | A builder killed the lead's queue |
| A worker's change ships only after: all-off identity, the per-map table on every map family, one number recounted by the lead | The portal rule that halved pearls on six maps |
| "Identical on the maps we have" is not "safe on maps we have not seen"; keep a standing unseen-map check | A rule live for 13 hours that starved the bot on closed-room maps |
| Compare online results only within the same hours; decide in advance how many games separate two versions | Two wrong verdicts (10-06, 10-09 05:23) |
| The version that played is read from the replay | A wrong attribution told to jun |
| After a permission refusal: stop, report, hand over one line. No smaller version, no other route, not through another agent | A whole session lost on 10-07 |
| Date cut-offs and safety checks in your own tools live in a setting the owner edits | Two hours without online tests on the eve of the deadline |
| Copy standing tables verbatim into every handover; the handover opens with a start checklist | Two handovers dropped the model table and the next session broke it both times |
| After compaction or handover, a remembered number is a lead; reopen the file before telling anyone | A figure posted without its condition |
| In the team channel: speak when spoken to, do what is clearly asked, tag the person, their time zone, nothing about the owner's whereabouts | §6, one incident each |
| Every promise in a ledger, closed with a time and a post | 73 entries; teammates got an answer to each |
| State what was verified and what was not, also to the owner | The last three versions had no online game when they were called verified |

### 8.3 Things to avoid

- Shipping a new version every 47 minutes when a 15-game set cannot tell two versions apart. Fewer versions, each
  with the per-map table and enough head-to-head games, would have found the three regressions before upload.
- Raising the worker count to use up a budget. "Use all the tokens" produced the overload incidents and more
  unverifiable switches, not rating.
- Letting a number stand for a cause in a brief or a report (a rate by queen length; a death count by portal).
- Heavy, maximum-effort research runs as a default. Two of the three usage crises came from them.
- One file that is both the log and the state. It ends up too long to read.
- Building per-person command syntax into a bot. People say what they want in plain words.
- Flipping the vendor rule by mood. Decide by task type; switch vendors only when a quota forces it.

### 8.4 Where the record is too thin to support a recommendation

- Whether the two Codex tiers, Sonnet and Opus differ in report accuracy: only incidents, no sampled comparison.
- What the card loop and the bridge bot contributed to the result, against their build time.
- Total spend for the contest in tokens or money: only daily shares and single runs are recorded.
- How long a card took from idea to merge.
- Whether the last-night versions after 00:49 were stronger online; the local head-to-head says roughly level, and
  the final three have no online games at all.
- What was wrong with the heavy tier's queen statistics on 10-07 that led to its ban.
- Who or what activated an older version on the server at 04:34 on 10-09 (not in our tool logs; two ranked battles
  were lost 1-4 by it).
