You are the lead analyst for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7). Work in this directory: unsw-swarm/data/analysis/top1/. This is an overnight background study, separate from the team's card loop. Be thorough; depth matters more than speed. You run at high effort; for the three deep sub-tasks below, call a sub-session at max effort.

## Goal
Find ONE excellent, well-supported hypothesis for how we can win more, by studying how the rank-1 team plays against teams rated 2000+. Protagonist: the rank-1 team (highest elo in the collected games; currently SSS, id 91; Vibing++ id 306 and "forgot to mention" id 264 are the other two top teams). The other two are (a) opponents that sometimes beat the protagonist: that shows its weaknesses; (b) a cross-check: what all three do is probably a real winning factor, what only one does may be a quirk.

## Material
- Replays of top-team battles: ../../online/top1/<battleId>/ (index: ../../top1/index.jsonl). Our own ladder games: ../../online/dl-*/ and ../../online/smoke/*/.
- Metrics already computed by tools/top_metrics.py (re-run it first to include new games: `python3 ../../../tools/top_metrics.py`): games.csv, timeline.csv, team_summary.md, gap.md, losses.md, notable.json in this directory. Read data/codex/report-top-metrics.md (../../codex/) for what the replay format can and cannot show.
- Our bot: ~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp (the live bot = main; toggles near the top), docs/LOOP.md, work/plan.md (the bot author's experiment log), and replay.py for custom parsing.
- What we already know (don't rediscover, build on it):
  - our weak maps are the new ones (Australia 15%, Tower Defense 17%, Islands 20%, Around UNSW 37%, Stripes 37% win rate);
  - on Tower Defense we leave the start room at round ~180 (opponents ~19) because of a no-tail penalty and a wall-blind centre pull;
  - on big maps we ram in 8% of adjacent turns and opponents in 38%;
  - top teams have about 60 units by round 200 and start feeding around round 300 (the bot author's observation);
  - our late feeding often feeds the opponent;
  - a change that let short dragons through narrow passages got our queen killed online;
  - "stride" (using free sprint steps more) raised our economy 14% without more wins;
  - ../newmaps-2026-10-04.md has an earlier analysis of our losses.
- A public blog series on this game (another team): roles by sonar (champion = longest, plays safe; kamikaze = length ≤3, hunts enemy heads; worker = the rest).

## Method
1. Refresh the metrics. Sanity-check them against two replays by hand (custom parsing) before trusting them. Note sample sizes everywhere.
2. Gap table: protagonist vs us by game phase and map size class; then protagonist vs the other two top teams. Find the 5 largest, most consistent gaps. For each, ask: is it a cause of winning or a consequence? Use the protagonist's own wins vs losses as a control (does the metric separate its wins from its losses?).
3. Sub-session A (max effort): "Read 12–15 notable games closely" (from notable.json, plus any you add). For each, follow the protagonist's queen and its 2–3 most important dragons through the game with custom replay parsing: opening (first 50 rounds: how it expands, when it splits, how it exits the start area), mid-game (unit count growth, how it treats contact: ram, avoid, box in), queen routine (where she stays, who guards her, when she grows), late game (who feeds whom, where, how it protects the leader, how it uses sprint), and the decisive moment. Look for role structure (do different dragons behave differently by length or position?) and for sonar use. Output: `deep-read.md` with per-game notes (game id, rounds, coordinates) and a list of recurring patterns with counts ("seen in 9 of 13 games").
4. Sub-session B (max effort): "Hypotheses". Input: gap table, losses.md, deep-read.md, what we already know. Produce 3–5 candidate hypotheses. Each: the claim as a GENERAL rule (game state or terrain only; never a map name, never a map-size gate), the evidence (numbers, game ids, rounds), the mechanism (why it wins games, tied to the queen rule / longest-dragon rule), the expected size of the effect and on which game types, what in our code would change (functions/toggles in mybot2/main.cpp), and what would show it is wrong. Output: `hypotheses.md`.
5. Sub-session C (max effort): "Red team". Try to break each hypothesis: confounders (stronger teams simply have more of everything), reverse causation, sample size, whether it survives across the other two top teams, whether our earlier failed experiments already contradict it (work/plan.md), and whether it could backfire the way the passage change did (queen safety). Output: `redteam.md` with a verdict per hypothesis.
6. You decide: pick ONE hypothesis (or say honestly that none survives, and what data would settle it). Write:
   - `REPORT.md`: start with a plain summary a teammate can read in 30 seconds (what we studied, the one thing we should try, why, how sure we are). Then the evidence tables, the runners-up, and the limits. Casual, clear English; explain any term on first use; no lab jargon.
   - `card-draft.md`: the chosen hypothesis in the team's Idea-card format: three-line summary (What we tried / Did it work / Who decides now), Idea by (AI, from the top-team study), Area, Claim, Evidence (Measured / Not measured), Expected signal, What would show it's wrong, Test plan (behaviour check with replays, the sparring pool incl. a queen hunter, then an online 30:30 comparison). Do NOT post it anywhere.
   - `SUMMARY-ko.md`: a short Korean summary for 준싱 (요체, 가볍고 짧게): the chosen hypothesis, the three strongest pieces of evidence, the main risk, and what to do next.
   - Finally `touch DONE`.

## How to call a sub-session (at most 3 in total, one at a time, never in parallel)
Write the sub-task prompt to a file here (subA.md etc., self-contained: paths, what to read, the exact output file), then run:
`claude -p --model opus --effort max --permission-mode bypassPermissions --settings "~/01. Project/개인 프로젝트/battlecode/work/loop/settings.json" --output-format text < subA.md > subA.out 2>&1`
Wait for it, read its output file, check its work against the data before using it. Do not start more than three sub-sessions; do the rest yourself. Do not use any other agent or deep-research tooling.

## Rules
- Read-only towards the outside world: no uploads, no battle requests, no GitHub posts or pushes, no Discord. No games need to be run (replays only); don't run local game batches.
- Never read key or token files. Write only inside this directory.
- Be honest about uncertainty: say what is measured, what is inferred, and what could not be seen in the replays.
- Finish before 08:30 KST on 2026-10-05. If time runs short, cut the number of games read closely, not the red-team step.
