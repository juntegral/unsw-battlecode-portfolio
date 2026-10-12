# Our Philosophy and Method

Faithful English translation of the Korean master, `docs/PHILOSOPHY.md`.
This document consolidates existing principles and methods learned from experiments. It introduces no new experimental criteria.
The user's principles came directly from the instructions for this document and are authoritative. They are explicitly identified below.
Brackets contain source paths relative to the repository; `../` refers to another repository used in the same work.
Historical records retain the rules and judgement methods of their time. Current user principles take precedence; old verdicts do not become current criteria. [AGENTS.md §1·§4; DECISIONS.md]

## Purpose

The goal is to keep finding better logic and keep growing.
Site scores, win rates, and results against specific opponents are observational signals. They alone do not establish growth or justify adoption. [../unsw-arena/lineages/GROWTH.md]
Growth comes from finding and explaining weak behaviour, implementing a hypothesis, and checking how behaviour actually changed.
A favourable result does not make an unexplained change an understood improvement. Rejection and incomplete work also leave records needed for the next judgement. [../unsw-arena/lineages/LOOP.md; AGENTS.md §4]
The qualifier calls for generally strong logic on unseen custom maps. Decisions use runtime observations rather than map names or memorised scripts. [AGENTS.md §1]

## The User's Principles

The following principles are the user's. File references add related evidence or implementation history.

- **User principle — Keep growing.** The goal is to find better logic. Site performance and results against specific opponents serve as signals. [../unsw-arena/lineages/GROWTH.md]

- **User principle — Feedback is central.** After every test, read replays deeply against the baseline. What changed and how matters more than the result. [DECISIONS.md; AGENTS.md §4]

- **User principle — Real feedback is online behaviour.** Check whether each mechanism fires and works against strong teams. Local proxy opponents are tools for mechanism checks. “Numbers are poison.” Never take comfort from local wins. [DECISIONS.md, 2026-10-01 14:42; AGENTS.md §4·§5]

- **User principle — Carry facts between waves.** Do not carry an earlier verdict as the next wave's answer. Criteria come only from the hypothesis, and registered criteria are enforced mechanically. [../unsw-arena/lineages/GROWTH.md; ../unsw-arena/lineages/LOOP.md; research/briefs/codex-build-template.md]

- **User principle — Large analyses use a census.** Define the population from all accumulated games and count it completely. Convenient samples or memorable games must not determine the conclusion. [../unsw-heuristic/exp/outcome-review/METHOD.md]

- **User principle — Build a generally strong bot.** The qualifier uses unseen custom maps, so map recognition is off. [AGENTS.md §1; DECISIONS.md, 2026-10-01 16:52]

- **User principle — Read the rules first.** Derive mechanics from the rule text and check them with small simulations. Do not assume familiar code implements new rules. [../unsw-arena/lineages/BRIEF.md; DECISIONS.md, 2026-10-02 00:26·09:14]

- **User principle — Upload only; never auto-revert.** Make the first upload late, with a complete build. The user decides when to upload and whether to roll back. [AGENTS.md §2·§5; DECISIONS.md, 2026-10-01 19:34]

- **User principle — Keep code comments short.** Briefly explain what is not obvious, and put rationale and history in `VERSION.md` and `DECISIONS.md`. [AGENTS.md §2; research/briefs/codex-build-template.md]

- **User principle — Test curiosity with data.** Check mechanisms in actual replays and board pictures. Revise suspicions raised by a count as the boards are read. [AGENTS.md §4; research/observations/queen-rammed.md]

## The Cycle

Observe → hypothesise → pre-register → build behind a switch → mechanism check → causal harm check → decide → record.
A cycle produces code, facts, and reproduction paths that support the next judgement. [../unsw-arena/lineages/LOOP.md; research/briefs/codex-build-template.md]

### Observe

Find weak behaviour in our replays and in strong teams' online replays.
For large analyses, first freeze the population, versions, rules, and duplicates from accumulated games, then count the whole population.
Choose cases for deep board reading by a fixed selection rule. Do not replace them with favourable cases after discovery. [../unsw-heuristic/exp/outcome-review/METHOD.md]

### Hypothesise

State which decision should change in which situation.
Write down situations that should improve, possible harm, and what should appear if the hypothesis is wrong.
Distinguish clues from strong teams' behaviour from facts derived from the rules. [../unsw-arena/lineages/GROWTH.md; AGENTS.md §4·§5]

### Pre-register

Locate the change and its overwrite relationships in the flow diagrams, and compare its strength with existing score terms.
Before games, record the expected board, trigger conditions, measurement tools, and judgement criteria in `VERSION.md`.
Criteria concern mechanisms and breakage. Do not change them after seeing results. [AGENTS.md §4; research/briefs/codex-build-template.md]

### Build Behind a Switch

Put the change behind a new `constexpr bool` switch, defaulting to `false`.
Use `if constexpr` to remove the off-path code, and check byte and event identity against the baseline build.
Freeze comparison builds and the specification so that conditions other than switching on or off do not change. [research/briefs/codex-build-template.md; AGENTS.md §4]

### Mechanism Check

Locally, check that the mechanism fires in intended situations and that actual boards show the intended state change.
Check both sides on unseen maps, generated maps, and known maps with recognition off.
Check errors, misrecognition, CPU, and off-build identity. Do not use win counts or final length as adoption gates. [AGENTS.md §4]

### Causal Harm Check

Find the first action divergence between on and off, and verify that the changed dragon's actual turn board is the same.
Investigate the changed choice's immediate and short follow-up outcomes, and the counterfactual for the old choice.
Report post-divergence raw totals in both directions as context; attach a board and cause to each harm case. [tools/firstdiv.js; exp/firstdiv/RESULT.md; research/briefs/codex-build-template.md]

### Decide

If the intended purpose moved and nothing broke, turn the switch on and refine under the partial-application rule. Otherwise, turn it off.
The decision-maker checks the measurements and limits of the registered criteria. Record the analysis recommendation separately from the actual decision.
Mechanism confirmation and final submission approval are separate. Submission also requires online behavioural evidence for each change and build validation. [DECISIONS.md; AGENTS.md §5]

### Record

Preserve raw data, analysis code, conditions, the baseline, what is on or off, and incomplete items.
Give decisions and results actual clock timestamps; put the rationale in `VERSION.md` and `DECISIONS.md`.
Pass facts, limitations, and open questions to the next wave. Preserve earlier failures and decision records. [AGENTS.md §2; ../unsw-arena/lineages/LOOP.md]

## Lessons from Experiments

### Pre-register Before Games

Principle: First record the insertion point, score strength, expected board, and criteria for activation, effect, and breakage.
Why: Changing the meaning of success after seeing results fits an explanation to the result instead of testing the hypothesis.
Example: Replays of the initial CONV2 exposed fragmented beliefs about the king and intercepted drops, among other problems. A revised candidate was separately pre-registered, and the earlier failure remained in the history. [DECISIONS.md, 2026-10-01 12:10·13:01]
Application: Separate exploration from confirmation. A candidate changed after confirmation becomes a new candidate; do not keep tuning on the same confirmation set. [../unsw-arena/lineages/GROWTH.md; AGENTS.md §4]
If a measurement criterion itself is flawed, retain the earlier failure and the reason for correction. Review changes to the common procedure separately and apply them to subsequent experiments; do not rewrite historical records retroactively. [../unsw-arena/lineages/GROWTH.md; DECISIONS.md, 2026-10-02 10:17·12:07]

### Judge by Mechanism Criteria

Principle: Check activation in intended situations, the state change on boards, and absence of breakage.
Why: Beating a proxy opponent does not explain whether the implemented mechanism was correct.
Example: On unknown maps, SWARM lost its map tables, so spreading, frontier, and pocket functions stopped while division remained. The explanation for retaining FORTRESS was rewritten around that structural fact. [DECISIONS.md, 2026-10-01 14:42]
Application: Win/loss or length totals cannot substitute for a mechanism pass. Online, read whether that mechanism actually works against strong opponents. [AGENTS.md §4·§5]

### Maintain Switch Discipline

Principle: Give every change a default-off `constexpr` switch and implement it with `if constexpr`.
Why: A changed off build prevents separation of the baseline from the change. A different execution cost also changes experimental conditions.
Example: A disabled change once reduced search depth and broke identity; `if constexpr` corrected it. [DECISIONS.md, 2026-10-02 00:06; research/briefs/codex-build-template.md]
Application: Identity keys cover known, custom, and generated maps. Check compiled byte identity and physical event identity separately. [research/briefs/codex-build-template.md; AGENTS.md §4]

### Use the Partial-Application Rule

Principle: If the purpose moved and nothing broke, turn the switch on and refine remaining problems. Otherwise, turn it off.
Why: Do not withhold a useful mechanism until every case is perfect, or present an unchanged purpose or actual defect as success.
Example: Q2BOX reduced queen-exit blocking by allies with alternative moves, but did not solve the Around UNSW case where the blocking ally had no alternative. It was enabled, and that failure remained a separate task. [DECISIONS.md, 2026-10-02 05:50]
Application: Distinguish unmet goals from breakage. Do not relax registered minimum criteria after the fact or rewrite remaining failures as passes. [AGENTS.md §4; research/briefs/codex-build-template.md]

### Use First Divergence as a Natural Fork

Principle: The replays diverge from the first changed decision, so a later raw death increase does not establish harm from the change.
Why: Different paths also change later encounters, food, births, and deaths. Per-key increases can be noise at about 50%. This is an observed tendency here, not a universal constant. [research/briefs/codex-build-template.md; DECISIONS.md, 2026-10-02 10:17]
Example: FREECOST was disabled on raw counts, but its first changed dragon's three-round harm/help was 0/2; BODYX's 0/3 supported the decision to enable it. Long-term counterexamples and memory defects remained separate. [exp/firstdiv/RESULT.md; DECISIONS.md, 2026-10-02 12:07]
Application: Use `tools/firstdiv.js` to verify the first divergence round and actual turn board. Even with identical physical boards, sonar or memory histories may already differ; do not automatically claim identical complete inputs. [tools/firstdiv.js; exp/firstdiv/RESULT.md]
The subsequently registered causal gate required harm ≤ help for the changed dragon at three rounds and the queen at fifty rounds, with a board and cause for every harm case. This was a criterion for that experimental procedure, not a promotion score to attach to every new hypothesis. [DECISIONS.md, 2026-10-02 12:07·13:38]

### State the Scope of Causal Checks

Principle: Distinguish choices compared on the same input from subsequent paths under two policies.
Why: After the first divergence, the switch and other dragons' choices continue to act. A long observation window is not an isolated intervention effect of the first action alone.
Example: The first-divergence report labelled long-term queen outcomes as subsequent policy outcomes, and marked living dragons as `censored` when the game ended early. It also interpreted intentional feeding deaths separately with their purpose stated. [exp/firstdiv/RESULT.md]
Application: Define harm as on dead/off alive and help as off dead/on alive, but do not replace observation end with survival. Do not extend the check into proof that every changed decision is safe. [tools/firstdiv.js; exp/firstdiv/RESULT.md]

### Never Gate on a Measurement Produced by Only One Arm

Principle: Apply the same definitions and observability to both arms. Diagnostic tags produced by only one arm cannot form a regression gate.
Why: An absent measurement in the off arm does not mean an absent defect.
Example: BODYX body-memory drift could not be measured in the same way in the off arm because prediction tags were absent. That difference did not establish a newly introduced BODYX defect. [DECISIONS.md, 2026-10-02 10:17]
Application: Remeasure both sides through raw events or a common reconstruction. Leave unobservable values unmeasured. [research/briefs/codex-build-template.md; ../unsw-heuristic/exp/outcome-review/METHOD.md]

### Narrow the Cause by Ablation

Principle: When a changed decision is harmful, separate relevant memory, caches, and components, then test whether the choice is restored under the same history.
Why: When one switch changes several paths, attributing the total effect directly to its main purpose can lead to the wrong fix.
Example: BODYMEM's harmful keys had identical self-body arrays. Substituting off-state ally memory and derived caches restored the first choice in 16/16 cases. The ally-memory part was removed to make BODYMEM2. [exp/firstdiv/RESULT.md; DECISIONS.md, 2026-10-02 12:07·13:38]
Application: This ablation narrows the cause of that choice. It is distinct from claiming complete reproduction of observation history or the full search state. [exp/firstdiv/RESULT.md]

### Distinguish Noise from Power

Principle: A result showing no visible change differs from evidence that no change exists. Local win counts are not adoption criteria.
Why: Small effects can be hidden by game variation, and repetition over the same map and opponent pool does not replace generalisation checks.
Example: Initial CONV2 had equal local win counts, but feeding reaching the final king lineage differed. Reading only wins would have missed the working mechanism and remaining defects. [DECISIONS.md, 2026-10-01 12:10]
Application: When outcome analysis is needed, disclose uncertainty, repeat-wave variation, and power. Distinguish census accuracy from uncertainty under new conditions. [../unsw-heuristic/exp/outcome-review/METHOD.md; ../unsw-arena/lineages/GROWTH.md]

### Inspect When the Change First Acts

Principle: The same change behaves differently depending on the state when it first acts. Consider observed state gates before clock-only gates.
Why: A particular round does not guarantee distance, dispersion, information freshness, or readiness to convert.
Example: Blanket late fortress conversion reduced feeding on dense boards. A later dispersion gate was designed to open only in widely dispersed states. [DECISIONS.md, 2026-10-01 14:20·17:06·19:52]
Application: Record the board and state at first activation. Retain clock conditions needed for deadlines, but use runtime dispersion and fresh reports instead of map names. [AGENTS.md §1; DECISIONS.md]

### Read Boards Before Believing a Count

Principle: A death classification is an observation; calling it a mistake or assigning intent needs further explanation.
Why: Pieces repeatedly dying on the same tile may be part of a design that protects a key dragon.
Example: W15's “58% dead-end deaths” mostly described a designed escape-division loop in starting pockets. Under the old rules at the time, the loop was a vault; the goal of eliminating repeated deaths was misplaced. [DECISIONS.md, 2026-10-01 18:57·19:30]
Application: Read heads, bodies, tails, drops, and action order in board pictures. Mark intent and counterfactuals absent from the replay as unconfirmed. [AGENTS.md §4; ../unsw-heuristic/exp/outcome-review/METHOD.md]

### Verify Assumptions on Flipped Maps

Principle: Verify actual team assignment rather than assuming a relationship between side labels and object IDs.
Why: A convenience convention in the local engine need not hold online.
Example: “Side A's queen is ID 0” was false online. Flipped-team maps checked whether protection attached to the actual queen. [DECISIONS.md, 2026-10-01 23:31; 2026-10-02 00:40]
Application: Define the queen as the team's lowest initial ID. Do not infer queen ID from the side name; verify friendly or enemy membership through observations. [AGENTS.md §1; research/observations/queen-rammed.md]

### Find Correctness Bugs through a Death Census

Principle: Classify deaths across the full population and reproduce repeated types with the same input and command.
Why: What looks like a strategic weakness may be an incorrect rule transition.
Example: All ten queen self-body escape deaths occurred on the third step. The same inputs and commands collided in 10/10 cases under the new rules and completed in 10/10 under the old rules. This exposed the old-rule body-model error. [research/observations/queen-rammed.md §4.3; DECISIONS.md, 2026-10-02 09:14]
Application: Distinguish full-board transition checks from reproducing the bot's internal memory. Establish correct body transitions before designing bunkers or repeated movement. [research/observations/queen-rammed.md]

### Derive from Rules and Check Small Models

Principle: Calculate free movement, costs, collision, tail transitions, and division order from the rules first.
Why: A rule change can invalidate analysis tools too. If familiar counts contradict the rules, revisit extraction first.
Example: Analysis that incorrectly shortened bodies by replaying new free steps under old rules was corrected. Queen-mechanics research derived reach, division, and cycle conditions from the rules. [DECISIONS.md, 2026-10-01 22:14; 2026-10-02 00:26]
Application: Compare body arrays for small inputs with official replay updates. Record which rules were used for reconstruction. [research/observations/queen-rammed.md; exp/firstdiv/RESULT.md]

### Put Terms Where They Change Candidate Rankings

Principle: For this bot's threat changes, treat first-step terms and DFS continuation terms separately. The lesson “only first-step terms change rankings” applies to this diagnosis.
Why: Increasing the same static threat at every search step can burden several candidates' future values together and hide the intended ranking change.
Example: W7a's stronger static threat did not change the rate of entering enemy-reachable tiles when safe alternatives existed. W7a′ strengthened only the first-step endpoint and changed choices, but the final purpose did not move, so it was disabled. [docs/arch/terms.md, threat-strength section; DECISIONS.md, 2026-10-01 17:01]
Application: Do not generalise this into a mathematical law for all search. Decompose each candidate's immediate, safety, and continuation values and check whether its actual ranking changes. [docs/arch/terms.md; research/briefs/codex-build-template.md]

### Use Census Not Samples for Large Analyses

Principle: Freeze the population relevant to the question from all accumulated games, and disclose every inclusion, exclusion, duplicate, and failure.
Why: Keeping only successfully read replays or preferred cases makes conclusions depend on selection.
Example: outcome-review fixed classifications and case-selection rules before deep reading. Queen-death research separated identical and different builds and deduplicated physical replays. [../unsw-heuristic/exp/outcome-review/METHOD.md; research/observations/queen-rammed.md §1]
Application: Combine census counts with deep case reading. Representative pictures explain the evidence; they do not replace the full denominator. Independently reconstruct raw events and disclose mismatches. [../unsw-heuristic/exp/outcome-review/METHOD.md; exp/firstdiv/RESULT.md]

### Limit the Scope of Generalisation

Principle: Act on observable states instead of map names, and limit improvement claims to verified conditions.
Why: Success on known maps and opponent behaviour immediately after a rule change cannot be transferred unchanged to new maps and adapted opponents.
Example: stronghold was misrecognised as Trauma, and map recognition was disabled after seeing custom tournament maps. The early queen-replay verdict “we only need our queen to survive” was also limited to unadapted opponents. [AGENTS.md §1; DECISIONS.md, 2026-10-01 16:52; 2026-10-02 01:09]
Application: Do not claim that new seeds alone verify freedom from map or opponent-pool overfitting. Use online mechanism feedback as evidence for the next hypothesis. [../unsw-arena/lineages/GROWTH.md; AGENTS.md §4]

### Separate Implementation Decisions from Final Submission

Principle: Every enabled change needs its pre-registered mechanism confirmation and online behavioural evidence from strong teams.
Why: A working mechanism does not guarantee that the combined build is complete or ready to submit.
Example: Causal checks supported enabling BODYX, but payment failure and body-memory defects after first divergence were not excused by that check. [exp/firstdiv/RESULT.md]
Application: Verify unseen bundled and generated maps, registered differences on known maps, errors, misrecognition, CPU, and upload tests. Do not select candidates by local wins; uploads and rollback remain the user's decision. [AGENTS.md §5; user principles]

### Divide the Work and Preserve Decision Responsibility

Principle: Codex builds and analyses; the coordinator runs games and judges; the human sets direction.
Why: Analysis recommendations must not become automatic adoption, and measured facts must remain distinguishable from decision responsibility.
Example: BODYX analysis recommended off, but the coordinator enabled it after separating a correctness fix from invalid regression measurements. First-divergence checks then strengthened the evidence for that decision. [DECISIONS.md, 2026-10-02 10:17·12:07]
Application: Codex hands over reproducible implementation, specifications, analysis, and risks. The coordinator records criteria application and decisions; direction, upload, and rollback follow the user's principles. [research/briefs/codex-build-template.md; DECISIONS.md, 2026-10-01 23:25; user principles]

## Anti-patterns

- Adopt or reject based only on local win counts or final length. [AGENTS.md §4]
- Adjust criteria, population, or case selection favourably after seeing results. [../unsw-arena/lineages/GROWTH.md; ../unsw-heuristic/exp/outcome-review/METHOD.md]
- Erase an unfavourable confirmation result by redrawing seeds. [../unsw-arena/lineages/LOOP.md]
- Call post-divergence death increases causal harm from the change. [exp/firstdiv/RESULT.md]
- Compare on-only diagnostic counts with absent measurements in off. [research/briefs/codex-build-template.md]
- Declare repeated deaths mistakes without reading the boards. [DECISIONS.md, 2026-10-01 18:57·19:30]
- Fill early endings with later survival, or count missing and failed runs as normal games. [exp/firstdiv/RESULT.md; ../unsw-arena/lineages/GROWTH.md]
- Combine populations from different builds, rules, or periods without explanation. [research/observations/queen-rammed.md; ../unsw-heuristic/exp/outcome-review/METHOD.md]
- Carry verdicts from known maps and unadapted opponents as facts about the next environment. [AGENTS.md §1; DECISIONS.md, 2026-10-02 01:09]
- Assume a disabled switch makes the build identical to the baseline. [research/briefs/codex-build-template.md]
- Treat enabling a candidate as completion or submission approval, or auto-revert. [AGENTS.md §5; user principles]

## Short Glossary

- **기제 점검 / mechanism check:** A local check of intended activation, actual board state change, and absence of breakage. [AGENTS.md §4]
- **사전 등록 / pre-registration:** A record freezing the hypothesis, insertion point, expected board, measurements, and judgement criteria before games. [research/briefs/codex-build-template.md]
- **부분 적용 규칙 / partial-application rule:** Enable and refine if the purpose moved and nothing broke; otherwise disable. [DECISIONS.md]
- **첫 갈림 인과 점검 / first-divergence causal check:** A check that verifies state at the first on/off action divergence and compares choices and subsequent outcomes, with its causal scope stated. [tools/firstdiv.js; exp/firstdiv/RESULT.md]
- **스위치 규율 / switch discipline:** Separation of a change through a default-off `constexpr` switch, `if constexpr`, and off-build identity. [research/briefs/codex-build-template.md]
- **표본 대신 전수 / census not samples:** Counting the whole frozen population and selecting cases for deep reading by a rule set in advance. [../unsw-heuristic/exp/outcome-review/METHOD.md]
- **기준선 / baseline:** The previous build and conditions frozen for comparison of the change's effect. [../unsw-arena/lineages/GROWTH.md]
- **반사실 / counterfactual:** A comparison checking what would happen with a different choice in the same situation. Distinguish the full board from the bot's knowledge at the time. [exp/firstdiv/RESULT.md; research/observations/queen-rammed.md]
- **관측 종료 / censoring:** An outcome remains unknown because the game ended before the observation window. Do not replace it with survival. [exp/firstdiv/RESULT.md]
