# Brief: write the top-team study up for two teammates, organised around what they are working on

You write ONE document: `data/analysis/top1/TEAM-BRIEF.md`. It will be posted as a GitHub issue for the team (three people: Zhe and QWQ write the bot, 준싱 runs the tooling). Work in this repository (unsw-swarm). Write only that file plus scratch files under `data/analysis/top1/brief_scratch/`. No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Do not change any existing file.

## Why
The study (2,343 ladder replays: the top three teams and ours) ended with only small ideas from the AI side. Zhe and QWQ know the bot far better and may see more in the same data. So the job is NOT to argue for an idea. It is to hand them the facts, sorted by the things they are building right now, with replays they can open, so they can draw their own conclusions.

## Sources (use only what is in these; every block of numbers names its source file and section)
- `data/analysis/top1/REPORT.md` (start here), `findings.md`, `hypotheses.md`, `redteam.md`, `redteam-2.md`
- `data/analysis/top1/deep-read.md` (Vibing++), `deep-read-2.md` (SSS, forgot to mention), `deep-read-3.md` (economy), `deep-read-4.md` (our queen; section 7 has numbers for the queen cards), `deep-read-5.md` (the race to the longest dragon)
- Today's counts on our own online games: `data/online/smoke/kg34b-analysis/summary.md` (when and how our queen dies; guards), `data/online/smoke/qw37-analysis/summary.md` (queen wait, Slithery Fight start), `data/online/smoke/qh31b-analysis/summary.md` (queen hunt), `data/analysis/queen-portals/summary.md` and `data/analysis/queen-portals/games.json` (queen portal use; for the per-map table recount from games.json: per map and per team tag, queens, share with at least one jump, wins with a jump and without, share of games ending in elimination).
The numbers are in Korean in some files and English in others; write English.

## What the teammates are building now (sort the material under these headings, in this order)
1. **Queen steps next to an enemy head** (Zhe, card #39 queen-safety: raise the queen's threat multiplier from 1 to 4, big penalty when her next step is right next to an enemy head). Wanted: how and where our queen gets rammed, how often she ends a turn inside a visible enemy's reach although a safe step exists, the same for the top teams, what their queens do instead in such a turn, attacker lengths, distance from her start, early rounds against later rounds.
2. **Queen walks into dead ends or gets boxed in** (Zhe, card #36 queen-dead-end: a 6000 penalty for dead ends, room below length + 8 counts as too tight, count only tiles she has seen; QWQ, PR #37 queen-wait, merged: a stuck queen splits 2 off her tail and waits instead of cutting herself down to 2). Wanted: boxed-in deaths by kind (terrain dead end, team-mate on her last exit, her own body), what SSS and forgot to mention do when boxed in, the small-map queen rules being off, self-inflicted deaths.
3. **Queen loop** (QWQ, card #38 queen-loop: with nothing worth chasing the queen walks a 2x2 loop in a quiet open spot and steps off when a head comes near). Wanted: everything on test4's and SSS's loops, where they loop, when they leave, the one case read closely, how far queens sit from their start, cells moved per 25 rounds.
4. **Queen and portals** (Zhe and QWQ disagreed in chat: stop her going through portals, or does she need to cross on small maps). Wanted: the per-map table, where ours is the odd one out, elimination share per map, deaths after a jump with the caveat that frequent jumpers inflate that number.
5. **Hunting the enemy queen** (Zhe, card #31 queen-hunt: the first small dragon that sees their queen hunts her and pings her position; three builds tested online, wins unchanged). Wanted: how often each team rams an enemy queen it can reach, who does the ramming (lengths), what the study's runner-up idea says, what the three online runs showed.
6. **Guards and intruders near our queen** (준싱's card #34 keep-guards, archived). Wanted: no top team escorts; small intruders near their queens get rammed by ordinary dragons; our rate against theirs; what the online runs showed.
7. **Small dragons circling instead of finding pearls** (QWQ, card #33 blind-circling: with no pearl in view our small dragons run 2x2 circles, top teams walk to where pearls are). Wanted: everything in the economy read that bears on search, eating rates by round, the "pearl zone around the leader" finding (the study's own pick), units and length by round against the top teams.
8. **Late game: feeding and the race to the longest dragon** (QWQ, card #22 late-feed: feeders die where they are, the leader sprints to the corpses). Wanted: when and how the top teams feed, who eats corpse pearls, the leader's share, what decides races, being behind at round 300.
9. **Anything else in the study that fits none of the above** and a teammate should know (keep it short).

## For each heading write
- **What the data says**: 4 to 8 bullets, each one fact with its numbers and sample size, ours against the top three (and against our opponents where the source has it). Plain words. No adjectives doing the work of numbers.
- **What the top teams actually do**: the behaviour described concretely enough that someone could imagine coding it, as far as the sources describe it. Mark anything that is an inference of the study rather than a count.
- **Replays to open**: up to 5 games from the sources that show it best, as a small table: link, map, who against whom, round(s) to look at, what you will see. Link format: `https://game.battlecode.au/visualiser?match=<game id>` (the game id is the number in the source tables, for example 1045200). Only games the sources describe; copy round numbers exactly.
- **Not known**: what the study did not measure or could not settle for this heading, including where its red-team rounds knocked a claim down.

## Top of the document
- Title line: `# Top-team study, 5 Oct: the data sorted by what we are building`
- Three lines: `What we tried:` / `Did it work:` / `Who decides now:` (the last one: nobody has to decide anything; it is reference material; Zhe and QWQ pick what is useful; questions about any number go to 준싱, who can have it recounted).
- "How to read this" in 5 lines or fewer: the data set (games, teams, dates as the sources give them), the words used (queen, leader, feeding, race, ram, small/big map as the sources define them), and that every number is a count from replays unless marked as inference.
- A table of contents with the nine headings and, next to each, the card it belongs to.

## Rules
- Only numbers that are in the sources. If two sources disagree, give both and say which is later.
- Do not recommend what to build and do not rank ideas. The study's own pick and runner-up are reported as what the study concluded, with its expected size and its own doubts, in headings 7 and 5.
- Sentences short, no jargon without a gloss the first time, no code names without saying what they are.
- Length: aim for 25,000 to 40,000 characters; it must stay under 60,000 so it fits one GitHub issue.
- End with "Where the full material is": the file list with one line each.

## Before you finish
Re-open the sources and check 15 numbers of the document against them, spread over the headings; list those 15 checks (claim, source file and section, match yes/no) in `data/analysis/top1/brief_scratch/checks.md`. Fix anything that does not match.
