# 02. The game: what decided matches, how strong teams played, where we lost

Written 2026-10-10 for team meow (team 1119: jun, Zhe, QWQ), after the qualifier deadline of 2026-10-09 15:00 KST.
This chapter is about the game itself. Our method, our bot's code, the tools, the AI workforce and the timeline are in
the other chapters.

## 0. How to read this

- Paths: `S` = jun's private repo `unsw-swarm`, `B` = the team repo worktree with the final bot, `R` = `~/meow-redteam`
  (the local game rig).
- **Measured** means counted from replays by a script that is on disk. **Reading** means an interpretation, mine or an
  analyst's. Where the two are mixed in one paragraph the reading is marked.
- "log HH:MM" means the entry with that time (KST, 2026-10-09 unless a date is given) in `S/docs/SESSION-STATE.md`, the
  lead session's running record, which is in Korean. Analysts that reported by message left tables but no report file;
  for those the log entry is the only prose record.
- Version words that appear in the evidence, because the counts are tied to them:
  - "main" or "old main": the team's bot up to about 10-08. In the last session "old main" is also the final source with
    every optional behaviour switched off, used as the fixed local opponent.
  - "B7", "B7Q": two builds of 10-08 that bundled seven fixes (Q = with queen rules).
  - "one1" to "one21": the builds of the last day and a half (10-08 evening to 10-09 14:49 KST). one21 was the bot at the
    deadline. Most queen counts below are from one11 to one18.
- Team names are the ladder's. Team 306 is called "Vibing++" in the study of 10-05 and "Cutlery" from 10-07 on; the id
  and the game counts match (597 games), so I treat them as one team. That is a reading, not a statement by the server.
- No bracket game is on disk. Everything here comes from ladder games (ranked five-game battles and unranked test sets)
  and local games. How any of it held on the unseen qualifier maps is **not recorded**.

## 1. The rules as the project understood them at the end

Source for every row unless noted: the rule pages fetched from the organisers' site into `S/rules/` on 09-29 and 10-01
(`structure.md`, `movement.md`, `death.md`, `splitting.md`, `pearls.md`, `vision.md`, `sonar.md`, `kelp-and-portals.md`,
`execution-order.md`, `map-info.md`, `map-files.md`, `timeouts.md`, `game-format.md`). The engine in use was `unswbc` 1.2.7
(`R/docs/ENGINE-METADATA.txt`); its own verdict code agrees with the scoring row (`R/docs/README.md`).

| Topic | Rule |
|---|---|
| Board | Rectangular grid that wraps around on both axes. Walls ("kelp") and portals sit on the edges between tiles, not on tiles. Every map is symmetric (mirror or 180 degree rotation). The bot is not told which. |
| Units | Each side controls "dragons": snakes of at least 2 segments. At most 64 living dragons a side. Every dragon runs its own copy of the program and shares no memory with the others. |
| Turn order | Up to 500 rounds. In a round every living dragon acts once, in ascending id. Ids alternate between the sides at the start, so dragons 0 and 1 are on different sides. |
| Queen | A side's lowest-id dragon (id 0 or 1). She is never replaced. |
| Winning | A side with no dragons left loses at once. Otherwise at round 500: (1) longer queen, a dead queen counting as 0; (2) longest living dragon; (3) greatest total length; (4) draw. This is the "Slay Queen" change of 2026-10-01 (engine 1.2.3); before it the longest dragon decided (`S/archive/claude-memory/slay-queen-rules.md`). |
| Moving | One action a turn: a move or a split. A move may be several steps ("sprint"). A dragon of length L takes its first ceil(L/4) steps free; every further step removes one tail segment. A dragon that cannot pay for a step dies. A length-2 dragon cannot pay at all. |
| Pearls | A pearl on the destination tile is eaten and the tail does not advance: plus one length. Eating is the only way to grow. Each tile has a visible countdown to its next spawn attempt; the attempt fails if anything is on the tile; the tile's spawn range is hidden. Mirror tiles share one countdown. |
| Collisions | Moving into kelp, into any body segment (own tail included, checked before the tail moves) or failing to output a valid action kills the mover. Moving into another dragon's head kills **both**, whatever their lengths or sides. Each step of a sprint is checked separately. |
| Death | A dead dragon turns every second segment, starting at the head, into a pearl: ceil(L/2) pearls on its own tiles. |
| Splitting | The rear k segments become a new dragon facing backwards (new highest id, acts later the same round, fresh memory). Parent and child must each keep at least 2. An illegal split kills the parent. |
| Vision | The 7 by 7 square round the head (wrapping). No view through a portal. Per tile: contents, pearl countdown, the four edges, and for a dragon part its side, id, whether it is a head, and its direction. |
| Sonar | Up to four 64-bit values a turn, one per direction, in a straight line through wrap and portals to the first kelp or dragon part; the dragon hit receives it, friend or foe, with no sender information. The sender learns only what kind of thing each ray stopped on. A dragon that died in its move sends nothing. |
| Portals | Paired edges with a shared id; stepping through one comes out of the other. |
| Compute | On the server a bot runs as WebAssembly with 100 million "CPU points" per dragon per turn and 48 MB. Running out kills that dragon. Local runs have no such limit unless `--sandbox` is used. |
| Ladder | A ranked battle is five games on five random maps, the same side for all five. Autoscrims are ranked. A team may request ranked battles only against teams rated no more than 50 below it. Each submission has its own rating. |

Consequences the project drew from these rules (readings, each used by the analysts below):

1. **A ram is a one-for-one trade that ignores length.** A 2-long dragon that moves into the head of an 80-long dragon
   kills it and dies. Under the queen rule this makes the cheapest unit on the board the best weapon against the most
   valuable one. Our own queen ramming a head always gives away the first tiebreak (`movement.md`, `death.md`; log 14:14).
2. **Reach.** A dragon of length L can cover ceil(L/4) free steps plus L-2 paid ones in one turn: 1 for L2, 2 for L3,
   3 for L4, 5 for L5, 8 for L8. A pearl on the way pays for its own step. From length 5 the reach is longer than the
   3 tiles a victim can see. (Derived from `execution-order.md`; the analysts used the same arithmetic, for example
   "length 5, reach 5 = 2 free + 3 paid" in the log at 13:34.)
3. **Queens move first.** Ids 0 and 1 act before everything else each round, so a head that ends its turn inside an enemy's
   reach cannot dodge before that enemy moves (`S/data/analysis/top1/REPORT.md` section 4).
4. **Length turns into pearls and back.** Half of a dead dragon is recoverable by whoever stands nearest. Every strong
   team used this to move length into one dragon late in the game ("feeding").
5. **A dead dragon cannot report its own kill.** The rammer dies in the ram and its sonar is discarded, so "their queen is
   dead" is known only to a third dragon that happened to watch (`S/data/codex/astra/qdead-opus/`, log 11:26).

Not confirmed from a rules file:

- The qualifier format (best of seven on maps nobody had seen) is from jun's notes
  (`S/archive/claude-memory/qualifier-timeline.md`), not from a fetched page.
- `map-info.md` says sides are 10 to 64 tiles. The local engine accepted 7 to 256 (unseen-map audit, log 01:42, and the
  7x7 test maps of 10-09). Ladder maps ran 24 to 64 wide and 12 to 64 high (`S/data/codex/astra/mapgen/ladder-params.md`).
- Pearl spawn ranges of the ladder maps were reconstructed from replays for seven maps and are estimates
  (`S/data/codex/astra/maps-sonnet/`, log 11:32). Local pearl counts on those maps must not be compared with online ones.

## 2. What decides a match

**Answer: after the rule change, the queen. Our queen was dead at the end in nine losses of ten, and a queen of ours
that outlived theirs never lost. Total length, the thing our bot was best at, is the third tiebreak and decided almost
nothing.**

Measured, final-day builds one11 to one15, 474 online games (150 ranked, 324 unranked test sets against a few chosen
opponents), 208 won. Counted for this chapter from the per-game table one analyst left
(`S/data/codex/astra/shed-sonnet/data.json`; script `S/data/retro-work/retro-game/qtable.py`):

| Queens at the end | Games | Won | Lost |
|---|---:|---:|---:|
| ours alive, theirs dead | 65 | 65 | 0 |
| both alive (longer queen wins) | 49 | 26 | 23 |
| both dead (longest dragon, or a wipe-out) | 232 | 117 | 115 |
| ours dead, theirs alive | 128 | 0 | 128 |

- Our queen was dead at the end in 243 of 266 losses (91%). With her alive we won 91 of 114 (80%).
- She died before round 100 in 112 games, in rounds 100 to 299 in 175, from round 300 in 73, never in 114.
- Whose queen died first: ours first 238 games, 69 won; theirs first 179 games, 106 won.
- **Their queen died first and ours died later: 114 games, 41 won. Their queen died and ours never did: 65 games, 65 won.**
  The 73 losses in the first group are games a surviving queen wins outright. That is 15% of all games and the largest
  single prize in the record.

The same picture from independent counts:

| Sample | Finding | Source |
|---|---|---|
| Old main, 400 ladder games, 10-07 | Queen dead at the end in 160 of 180 losses (head-on 120, wall 23, own body 12). | Notice in the channel mirror (not published), 10-07 13:22 |
| Old main and test builds, 401 games against teams rated 2000+, 10-05 | Queen-rule wins: ours 4 of 51 wins where the top three teams take about half their wins that way. Our queen dead before round 300 in 84% of games (the three top teams 43%, 52%, 62%). With her dead and theirs alive: 0 of 73. | `S/data/analysis/top1/REPORT.md` section 2 |
| 150 online games of 10-08 against two mid-table teams | Queen dead and theirs alive: won 0 of 61. | `S/data/analysis/ladder/dossier/diag-theirqueen.md` |
| 95 local games, new build against an older one | We killed their queen first in 27 games and won 12 of them, because ours then died short. | `S/data/codex/astra/h2hloss-opus/`, log 06:48 |
| Games against teams rated 100+ below us, night of 10-09 | 10 losses, our queen dead in all 10 (rammed 8, own body 1, wall 1); in 6 theirs lived to round 499. | `S/data/codex/astra/weak/report.md` |
| Five per-opponent analysts, 10-09 14:42 | Same sentence from each: our queen alive at the end is a win, dead is a loss. | `S/data/guide/px-live-one21.txt` |

Economy is the second factor, and it acts earlier than it looks:

- Measured (10-05, `REPORT.md` section 2): of our games that reach round 300 we hold under two thirds of the enemy's
  total length in 63%; the three top teams are in that position in 16% of theirs. In that row we won 7%.
- Measured (`diag-opening.md`): inside one map, our length lead at round 10 goes with winning at +0.01 and at round 20 at
  +0.12, at round 40 at +0.25 and at round 60 at +0.31. The opening proper does not decide; rounds 20 to 100 do.
- The loss ledgers of 10-09 attach "out-eaten from round 25, 50 or 75" to loss after loss on the small maps where each
  side starts with two short dragons (`S/data/codex/astra/battle-opus/battles.md`, `loss15-sonnet/losses.md`). Nobody
  totalled it; the share is not recorded.
- Reading: a side that is behind in dragons by round 50 has fewer bodies near its queen and more enemy heads near her,
  so the queen death is often the consequence of the economy and not a separate fault. The two cannot be separated in
  this record.

What did not decide matches, although we spent effort on it: total length in games we led. Examples measured on
10-09: 163 against 59 total and lost on the queen (Maze, game 1527400); 75 against 4 and lost on the queen (weakhold,
1528854); 17 dragons and 183 pearls against 3 and 5 at round 100 and lost on the queen (Portals, 1524545)
(`S/data/codex/astra/loss15-sonnet/losses.md`).

Lesson for another game: read the tiebreak order first and count your own results by it before choosing what to
improve. We optimised growth for a week under a rule whose first test is one unit's survival.

## 3. How queens die

**Answer: mostly rammed by a 2- to 4-long dragon that sprints 1 to 4 steps, usually one she could see, and usually
after she herself stepped closer. One death in four is her own move into a dead end. A long, fed queen is lost in two
further ways that are bugs in spirit: cutting herself down to 2, and standing still shedding segments.**

Measured, one11 to one14, 368 online games, 286 queen deaths (`S/data/codex/astra/qexit-opus/classify.py`,
`qdeath-*.jsonl`; log 11:52):

| Class | Count | Detail |
|---|---:|---|
| Rammed, at least 2 free tiles beside her head after her last step ("in the open") | 152 | |
| Rammed with 1 free tile ("from a one-way place") | 41 | |
| Rammed with 0 free tiles | 12 | |
| All rams | 205 | attacker inside her 7x7 view in 158; attacker used paid steps in 140 |
| Died on her own step while trapped (wall, own body, a mate) | 69 | by build: 16 of 59, 7 of 56, 22 of 133, 9 of 38; concentrated on the maps Portals and Maze |
| Other | 12 | |

- Her length at death: 2 in 133 cases, 3 in 89, 4 in 30, 5 in 9, 6 or more in 25. 94 of the 286 came after the enemy
  queen was already dead.
- Of 172 single-step ram deaths, 111 had no safer open step on the last turn. **The deciding turn is two or more turns
  earlier.**
- In 22 of the 286 (8%) she moved into an enemy head herself.

Sub-classes that the later analysts named, with their counts:

| Sub-class | Count | Source |
|---|---|---|
| Her own last step went one tile toward the head that hit her | 19 of 21 rams against one opponent; in three of four losses of one battle she walked from 3 tiles to 2 from a 3-long head, which then needed 1 free + 1 paid step | `S/data/codex/astra/skku-opus/qlast.txt`, log 14:42 |
| She ended a turn inside a visible enemy's reach although a safe step existed (old main) | 104 of 362 deaths: 66 stepped in, 38 stayed. Killers were 2, 3, 4 long in 27, 25, 14 of the 66; none longer. Rate per 1,000 queen-rounds: ours 2.6, top three 0.4. | `S/data/analysis/top1/TEAM-BRIEF.md` section 1 |
| Attacker not visible to her on her last turn | 61 of 253 queen rams among the top ten teams; in our games an attacker of length 5 was first seen at distance 5, one turn after being 8 away | `S/data/codex/astra/topqueen2/report.md`; `qaway-opus`, log 13:34 |
| Sprint paid for by pearls on the way | 44 of 253 among the top ten; 3 of 6 losses in one of our sets | `topqueen2/report.md`; `S/data/codex/astra/sweep/0436/synth/report.md` |
| Enemy body cut off by the edge of view, so its length and reach were underestimated | 5 of 15 losses in one set | `S/data/codex/astra/sweep/0410/synth/report.md` |
| Self-trap through a portal into a closed pearl room | 28 of 30 queen deaths on the map Portals (one-tile pocket 12, four-tile room 14) | `S/data/codex/astra/qbox-opus/`, log 12:14 |
| Self-trap in a dead-end corridor because the only other step led past a mate's body | 3 online games on Maze | `S/data/codex/astra/qtrap-opus/table.txt` |
| Boxed with mates: she walked in beside dragons already there | 19 of 24 such deaths were her own step or split, not a mate arriving | `qmate-opus`, log 14:14 |
| Long queen (10+) splits down to 2 when "exposed with no escape" | 21 times in 474 games, all after round 339; dead within 3 rounds 12, within 20 rounds 16; 18 of the 21 games lost; in 15 she had been the longer queen | `S/data/codex/astra/shed-sonnet/ana.out` |
| Long queen stands still and sheds 2 segments a turn | 70 runs after round 100 in 36 of 474 games, 7.8 length lost per game affected; one game it alone would have flipped | log 14:05; `S/data/codex/astra/late-opus/tables.txt`, `extra.txt` (the files also hold 35 games of a later build: 509 games, 72 runs) |

Things that looked like causes and were not:

- "A queen of 4 or longer hardly dies" (0.08 deaths per 100 rounds against 2.61 at length 2, local, after the enemy
  queen is dead). Measured, but when a build forced the queen to hold length 4 she died as often or sooner (0.93 off,
  1.10 hold, 1.93 hold plus feeding). The analyst's own verdict: correlation, not cause (`qdead-opus`, log 11:48).
- "Keep away from visible heads" as a step rule. Mean gap to the nearest visible head moved from 3.64 to 3.67. By the
  time a head is within 7 steps she has one or two open steps left on 33 of 75 turns. Verdict: the lever is where she
  lives, not which step she takes near a head (`qaway-opus`, log 12:53). A rule that moved a long queen out of full
  reach did not save the target case either: the limit was sight, not the step rule.
- "Top queens dodge better." Measured against six top teams: they step away from a head within 3 steps on 66 to 86% of
  turns, ours on 82 to 85%. What they have is company: a chase starts with a mate within 5 tiles in 54 to 65% of cases
  (ours 29 to 40%), a mate rams a pursuer in 6 to 11% of chases (ours 5 of 275), a chase lasts about 3 turns (ours 4.2
  to 7.5) (`S/data/analysis/ladder/dossier/diag-topqueen.md`).

Two analysts disagree on where the queen should live. `diag-theirqueen.md` (two mid-table opponents): their queens
stay near the start tile, ours walks out unforced, and 77 of her 110 deaths came after she left home with no head near.
`diag-topqueen.md` (six top teams): no top queen is a home queen; she stands where her mates stand. Both were measured.
My reading: a short queen is safe among her own dragons, and for weaker swarms "among her own dragons" happens to be
near the start. The existing home-leash constant was never played, so this stayed open.

## 4. What the strongest teams do differently

### 4.1 First 100 rounds

**Answer: nothing clever in rounds 0 to 20. They split a little sooner, then eat more per turn from round 10 to 30
onward, mostly pearls in cramped places and the pearls of their own dead, and they accept twice our death count to do
it.**

| Behaviour | Them | Us | Source |
|---|---|---|---|
| A starting dragon of 4 or more splits in round 0 | 96 to 100% of games (four top teams); rank 1 on 10-08: 75.9% of such starters | none on maps of 1,200 cells or fewer (old builds); 4.6%, and 90.3% one round later | `diag-topopen.md`, `diag-opening.md` |
| The queen splits like any other dragon in the opening | on 74 to 100% of her turns at length 4+ | 3 to 15% | `diag-topopen.md` |
| A non-queen that reaches 4 splits on that turn | Cache 93%, Preyas 83% | 48 to 62%; with a pearl adjacent ours eats (84%) where Cache splits (82%) | `S/data/codex/astra/early-opus/table-splits.txt` |
| Turns of a short non-queen with a pearl one step away, per game, rounds 0 to 100 | 182 and 150 to 167 | 88 to 110 | `early-opus/table-near-pearl.txt` |
| Share of such turns on which it eats | 82 to 85% | 82 to 85% | same |
| Share of short-dragon turns spent on narrow tiles (two or fewer open sides) | Cache 15.3 to 16.3% | 8.6 to 9.6% across ten of our builds | `early-opus/table-narrow.txt` |
| Pearls of the own dead eaten again, share of the round-100 intake gap | 49.4% of the gap to Cache | | `S/data/codex/astra/open2/report.md` |
| Deaths in rounds 0 to 100, 30 games | Cache 1,527 | 760 | `open2/report.md` |
| Head within one step of a tile when its pearl is born | 17.6% of births | 10.1% | `diag-spawn.md` |
| Steps onto a tile whose countdown shows 1 (which blocks the spawn) | 26.8% | 73.3% | `diag-spawn.md` |
| With no pearl in view | walks on in a straight line | ties broken by noise, turns back | `diag-med20.md`, `diag-walk.md` |

- Measured: the gap opens at rounds 11 to 20 against one opponent and 21 to 30 against another (`open2/report.md`).
  Against two top teams they first hold 1.5 times our total length at rounds 81 to 115 on maps over 700 cells
  (`diag-topopen.md`).
- Measured: rank 1 does not split sooner per pearl than we do (0.36 against our 0.38 splits per pearl). Its higher split
  rate is its higher pearl rate: 84.1 pearls per 1,000 dragon turns against 58.8, all of it in dragons of 2 and 3
  (`diag-split.md`). An earlier reading that "they split earlier" was wrong in that sense.
- Measured: of rank 1's 25 extra pearls per 1,000 turns, 20 are paid back in extra deaths; the net gap is 4.9
  (`diag-economy.md`). Reading: the strong economy is high turnover, many short dragons dying boxed in beside mates that
  eat them, not careful play.
- Never found: the line of our code responsible for the narrow-tile gap. Three suspects were tested and cleared on 10-09
  (`early-opus`, log 11:34 and 11:46). It is a property of the base scoring, present in every build.

### 4.2 Rounds 100 to 300

| Behaviour | Them | Us | Source |
|---|---|---|---|
| Splits, deaths, own-corpse pearls eaten in rounds 101 to 300 | 165 to 224, 153 to 213, 189 to 278 | 119 to 134, 114 to 127, 123 to 136 | `S/data/codex/astra/midgame/report.md` |
| Small dragon takes a free pearl beside its head after "leader mode" starts | 76 to 93%, unchanged | fell from 84% to 51 to 58% at our own switch round (old main) | `REPORT.md` section 3 |
| Head-ons started per game | 29.2 (65.3 on maps over 1,200 cells) | 12.8 (19.2) | `diag-attack.md` |
| A 3-long rams a 2-long when not outnumbered | 0.44 to 0.77 of chances | 0.03 | `diag-topfight.md` |
| Enemy queen's head in view and in reach: rammed | 265 of 266, 250 of 252 (two top teams); our opponents on our queen 197 of 228 | 99 of 435 (old main) | `REPORT.md` section 4 |

- Measured: a head-on costs every team the same, and the attacker always dies (55,331 of 55,331). Five rounds later the
  attacker's side is down 0.8 to 1.5 length and the target's side 2.4 to 3.1. They start two to three times as many,
  and their side eats 27 of the dropped pearls a game where ours eats 15 (`diag-topfight.md`, `diag-toprams.md`).
- Measured: nobody hunts in groups, walks far for the queen, escorts the queen or screens a long dragon
  (`diag-topfight.md`, `diag-topqueen.md`). Our trials of guards and escorts changed nothing or made it worse
  (`S/docs/HANDOVER-2026-10-09.md` section 3).
- The one behaviour found that only we had: from a fixed round small dragons left pearls near the dragon they believed
  was our longest. It cost 22 to 33% of our natural intake from that round on, and half the reserved zones were around a
  dragon already dead (`REPORT.md` section 3, 10-05). It was that study's best-measured finding, and its estimated
  worth was about one point of win rate.

### 4.3 Late game

**Answer: the queen stays 2 to 4 long, inside the swarm, until round 200 to 400 depending on the team. Then small
dragons die next to her on purpose and she eats them. The latest feeders were the highest ranked.**

Measured on 10-07 and 10-08, top ten teams' games among themselves, queens that lived to the end
(`S/data/codex/astra/topqueen2/report.md`):

| Team (rank on 10-07) | Mean queen length at round 99 / 199 / 299 / 399 / 499 | Reading |
|---|---|---|
| chad gdp (1) | 2.6 / 2.6 / 2.5 / 2.7 / 22.7 | feeds only in the last 100 rounds |
| team 55 (4) | 3.3 / 4.3 / 4.6 / 4.8 / 41.5 | same, harder |
| aAah (5) | 2.7 / 2.9 / 3.0 / 3.4 / 2.4 | never feeds; wins by killing queens and wipe-outs |
| larp stock zi balls (3) | 2.7 / 3.3 / 15.9 / 31 / 46 | feeds from about round 200 |
| forgot to mention (6) | 2.8 / 2.8 / 23 / 38.2 / 42.1 | feeds from about round 200 |
| Sponge (7) | 6.9 / 14.9 / 24.6 / 34 / 41 | feeds from the start |
| Cutlery (9) | 3.3 / 4.9 / 10.9 / 14.3 / 31.5 | steady |

- Measured: of 75 queen-rule wins among the top ten, 52 were with the enemy queen dead and 23 with both alive and a
  longer queen. Top queens' intake in rounds 300 to 499: 830 natural pearls, 3,626 pearls of their own dead, 51 of the
  enemy's dead. The donor is 3 long at the median, dies within 3 tiles of her, and is eaten 2 rounds later.
- Measured: how the donors die differs by team and is visible in the death reasons: standing still with no action
  (WeHaveQuizzes, Computers), moving into their own body (Cache me outside, Codehammer, acegi), an illegal split of
  size 1 (Preyas: 439 such deaths in 15 games) (`S/data/codex/astra/band/report.md`, `open2/report.md`).
  Correction to an earlier belief: in rounds 0 to 300 most "no action" deaths are not sacrifices; 75% are dragons with
  no free tile, the same death ours take by stepping into a wall (`diag-sacrifice.md`).
- Measured: when both queens are dead the race for the longest dragon is not won by killing our leader. In 27 of 28
  such losses on 10-08 no dragon of ours was ever longer than their final longest; they passed us for good at round 208
  to 374 and then folded the swarm into it (one team from 53 dragons to 13). We ended those games with 29 to 40 dragons
  alive, most of them more than 15 tiles from our longest (`diag-longest.md`, `diag-whq.md`).
- Measured: our own long queen was unsafe. In 50 of 474 games she was alive and ahead at round 350; we lost 25 of them,
  24 by her death after round 350. That is 5.3% of all games (`late-opus`, log 14:05).
- Our early feeding hurt: with 56 or more dragons our bot started feeding at round 200, 150 rounds before the other side
  folded; natural intake fell by a third at once and the leader it built was rammed by dragons of 2 to 5 in 6 of 7
  games (`diag-one1.md`). Moving that round to 350 was one of the few changes with a clear mechanism.

Reading for reuse: keep the scoring unit small and unremarkable while enemies can still reach it, and convert late.
Length held early is exposure, not an asset, because a ram ignores length.

## 5. Map features and how our bot behaved on each

Ladder maps, with our results for one11 to one15 (474 games; opponents were not the same on every map, so the win
column is a description, not a rating). Sizes and starts from `S/data/codex/astra/mapgen/ladder-params.md`; results
from `shed-sonnet/data.json` via `S/data/retro-work/retro-game/maptable.py`.

| Map | Cells | Starters a side (lengths) | Portal pairs | Won / games | Our queen dead at end (before r100) | What happened there |
|---|---:|---|---:|---:|---:|---|
| Tower Defense | 512 | 2 (2, 2) | 0 | 6 / 30 | 27 (10) | Pearls sit in one-door rooms of 4 to 6 tiles. Ours walked to the door and stepped back. First pearl at round 64 to 73 against 39. Round 100: 1 dragon, total 3, in game after game. |
| Maze | 1,152 | 2 (4, 4) | 16 | 5 / 25 | 23 (4) | One-tile-wide corridors with pearls in dead ends. Queen self-traps; games lost on the queen while far ahead on total. |
| Trauma | 1,152 | 2 (4, 4) | 6 | 6 / 29 | 15 (0) | The pearl corridor is behind a portal 8 steps from the start. Ours crossed at round 29 to 85, theirs at 9. Their queen died in 0 of 29, so no loss here could be turned by anything but our own queen's length. |
| Australia | 4,096 | 9 | 4 | 9 / 31 | 31 (3) | Both queens usually dead; decided by the longest dragon, twice lost by one tile. |
| Portals | 512 | 3 (3, 3, 3) | 20 | 10 / 34 | 34 (14) | Start areas connect only through portals. Queen went through a portal into a closed pearl room, grew, and could not get out. |
| Slithery Fight | 1,701 | 7 (25, 7, 4, ...) | 2 | 11 / 33 | 27 (0) | The queen starts 25 long, coiled. Opening shed 25 to 3 over 11 turns. Long queens cut down or rammed after round 340. |
| Stripes | 288 | 2 (2, 2) | 8 | 15 / 35 | 27 (19) | 86% of pearls are born in rooms of 1, 3 and 4 tiles behind portals. Nearly every game ends by wipe-out. |
| Queen Of Spades | 875 | 2 (3, 3) | 2 | 14 / 28 | 20 (6) | Out-eaten from round 50 in the two losses read closely. |
| Around UNSW | 4,096 | 10 | 4 | 14 / 27 | 25 (2) | Both queens usually dead; longest-dragon race. |
| Schooltime | 2,400 | 3 (4, 4, 4) | 12 | 18 / 34 | 4 (0) | Both queens are sealed in a room. Decided by queen length, longest, total. |
| Islands | 2,240 | 5 | 12 | 17 / 31 | 31 (7) | Old main won 1 of 24 here (stopped growing at its leader round). |
| Default | 1,024 | 4 (4, 4, 4, 4) | 12 | 17 / 30 | 19 (4) | |
| Trophy | 625 | 2 (3, 3) | 1 | 16 / 28 | 20 (13) | Games can end by wipe-out before round 50 (two of three in one check), which makes round-100 totals misleading. |
| weakhold | 600 | 2 (4, 4) | 0 | 18 / 30 | 23 (5) | |
| Devil | 512 | 3 (4, 4, 4) | 0 | 19 / 29 | 24 (23) | Our queen dies before round 100 in 23 of 29 and we still win 19. Reading: decided by wipe-out (all 7 Devil games of an older sample were). |
| Autarky | 972 | not recorded | not recorded | 10 / 15 | 7 (2) | |
| Prisoners Dilemma | not recorded | not recorded | not recorded | 3 / 5 | 3 (0) | |

By feature, what changes the game:

| Feature | Effect | Evidence |
|---|---|---|
| Two short starters a side on 1,200 cells or fewer | The game is a race for the first pearls, lost by round 30, then a pick-off. All 7 wipe-outs of one 45-game sample were on such maps; they eat their second pearl at round 15, we at round 30, and hold twice our count for good from round 33. 66 of our 77 "never grew" games started with two dragons. | `diag-wipeout.md`; notice of 10-07 13:22 |
| Size over about 1,200 cells | Nobody is wiped out; decided by queen or longest dragon. Head-ons a game: 65 started by them, 19 by us (old main). Ours stopped growing at its own leader round. | `diag-attack.md`, `diag-bigmap.md` |
| Pearls behind portals | By round 40 the whole intake gap on medium maps lies behind portals (1.4 pearls against 6.3 to 9.5). A rule that kept short dragons out of unseen portals cut our round-100 pearls on Portals from 238 to 71 and on Trauma from 41 to 4, because if nobody crosses, the far side is never seen. | `diag-med20.md`; log 10:24 (one14) |
| Portal into a closed room | Fatal for a growing dragon: the exit portal lands on her own neck or on the child she just split off. | `qbox-opus` |
| Narrow corridors and dead ends | A dragon that eats grows and cannot turn in a one-wide dead end. Our penalties for this also kept us away from the pearls there, which is where the opponents' extra intake was. | `early-opus`; `tiny-opus`; `diag-economy.md` (cramped tiles: 6.9 of the 25-pearl gap) |
| Closed start room | On four ladder maps with a closed-off start, rank 1 held 48.9 total length at round 100 against our 24.6; on the other 15 maps 66.5 against 64.8. | `diag-opening.md` |
| Sealed queen room | Queens cannot be killed; the game falls to queen length. | Schooltime row above; `REPORT.md` section 1 |
| A very long starter | Needs its own opening: every team sheds or cuts it at once. | `TEAM-BRIEF.md` section 2; `late-opus` |
| Seat | Against one opponent on 11 matched maps we won 75.8% as side A and 27.3% as side B; on local 24x12 maps the seat decided the game whatever the build. Cause not established. | `S/data/codex/astra/skku-opus/tables2.txt`; `h2hloss-opus`, log 06:48 |
| Pearl supply | Maps differ from 70 to 1,024 pearl-bearing tiles and from 1-round to 3,849-round timers. Fast tiles reward standing beside, not on, the tile. | `ladder-params.md`; `diag-spawn.md` |

Unseen-map probes on the last day (local games of the final builds against old main; each cell is one to four games,
so these are warnings, not rates):

| Family | Result | Evidence |
|---|---|---|
| 7x7 and 7x9 maps (49 to 63 cells) | Lost 3 of 3 before round 25; from 9x9 up fine. The open 7x7 had been lost to old main since earlier builds. No fix shipped. | `unC-opus`, log 13:59, 14:14 |
| Closed start room, 3x3 with a 3-tile exit | Second starter killed itself at round 1 and the queen circled the room for 57 rounds. Old main left at round 24. | `S/data/codex/astra/unB-opus/`, log 14:05 |
| Closed start room on a map just over 1,000 cells | Never left the room in 500 rounds; the same design at 968 cells left at round 22 to 26. Cause: a centre-pull rule that switched off above 1,000 cells. Fixed in one19 by one constant. | `unB-opus`, log 14:14 |
| Start box whose only exit is a portal into a closed pearl room | Never left in 500 rounds; with all switches off it left at once and won 181 to 7. Cause: a queen dead-end rule switched on for all map sizes. Removed in one19. | `unA-opus`, log 14:18 |
| Start box with no pearls and a blind portal as the only exit | 0 pearls to round 50, wiped out at 55. Cause: that day's own fix for the Portals map. Patched in one19 and one20; still lost in the probe. | `unA-opus`, log 14:26, 14:28 |
| Large room where only non-queens leave | Queen stays behind and the side is wiped out. No constant helps. | `unB-opus`, log 14:17 |
| Comb and spiral dead ends | Queen walks into a deep dead-end tooth. Old main does the same. | `unB-opus` |
| Sides of 129 tiles or more | The bot's sonar switches off entirely. Never played. | `S/data/codex/astra/audit-unseen/report.md` |
| 64 new generated maps, 10-09 01:38 | The then-live build against its own all-off baseline: 31 wins, 3 draws, 40 losses (on 100 cells or fewer 4-1-11), while on the 8 familiar maps it won 12 to 14 of 16. | `S/data/codex/astra/mapgen/`; log 01:38 |

Reading: three of the four red results were caused by our own queen-safety rules or map-size thresholds, two of them
added that same day. Rules written against one known map (do not enter blind portals, treat small rooms as dead ends)
were exactly what failed on a map built differently. Every hard threshold on cell count (600, 700, 1,000, 1,200) was a
cliff on some probe map.

## 6. Opponent archetypes, by behaviour

| Archetype | Seen in | How it plays | How it did against us | What worked against it |
|---|---|---|---|---|
| Flat swarm, no feeding | aAah (rank 5 on 10-07) | Stops splitting at about 50 dragons; no leader; a pearl beside a head taken on 86% of turns; queen 3 long, rammed in 26% of games; 54% of its wins are wipe-outs. | Its queen lived in 9 of 15 games against ours in 1; a mate rammed her pursuer in 8 of 35 chases. | Nothing of ours recorded. |
| Swarm, then feed the queen very late | chad gdp, team 55 | Queen under 5 long to round 399, then fed in the last 100 rounds. | Not played directly in the record. | Not recorded. |
| Swarm, then feed from round 200 | larp, forgot to mention, WeHaveQuizzes | Queen walks inside the swarm and is fed first; swarm folds into a few long dragons after round 300; a 3-long pays a segment to ram a head two tiles off (45% of one team's rams). | WeHaveQuizzes took 72 of 90 games on 10-08: 25 wipe-outs, 26 on queen length (their queen rammed in none), 21 on longest. | Not beaten. Moving our own feeding start from round 200 to 350 stopped one self-inflicted loss mode. |
| Fast out-eater | Cache me outside, Preyas | Splits a 4-long at once, works narrow tiles, re-eats its own dead, takes twice our deaths; feeds late by self-collision or illegal splits. | We won 3 to 8 of every 15 across a dozen builds, with the same bot scoring 8 and then 4. | Nothing; and a 15-game set cannot tell two builds apart against it. |
| Queen hunter rated below us | kraken (about 1975) | Rams our queen with 3-longs on paid steps, often eating pearls on the way, sometimes from outside her view; own queen alive in 7 of 10. | Beat us 3-2 in three ranked battles in one night; in a 15-game set all 6 of our losses were on the queen while we led on everything else (42 dragons and 481 length against 10 and 82 in one). | Better reach estimates (pearl-fed sprints, bodies cut off by the view edge) took our queen's rams from 9 to 4 in 15 games; we reached 14 of 30. The sample is inside the noise band. |
| Home queen | Team SKKU, Big Bobs Bots; test4 as a loop | Queen stays near her birth tile (median 2 tiles against our 9) or circles four tiles at length 2 for a quarter of her rounds. A looping queen was rammed on the loop once in 38 rams. | SKKU: 2 of 10 early on 10-09, later about level; all four losses of one battle were queen rams. | Being side A (70% in 30 games), and killing their queen: on 11 matched maps she died in 93% of our side-A games. A looping queen must leave the loop when a head comes within 2 to 3 steps; one that returned was rammed. |
| Big-map specialist | Ballers | Not analysed beyond results. | We wiped them out on maps of 972 cells or fewer and won 1 of 5 at 1,152 or more. | Small maps. |
| Much stronger all-round | Sponge (2543), SSS (2528) | Queen fed from the start (Sponge). | One 0-5 battle each on the afternoon of 10-09; our queen died in all 5 against Sponge. Over the whole ranked record against Sponge we won 6 of 20 games. | Nothing found. |

- Measured: seven teams ranked just above us did not share one style, and no single weakness of ours explained losing
  to all of them; queen problems and longest-dragon problems split by opponent (`band/report.md`, 10-09 06:14).
- Measured: we did worse than our rating predicted against teams rated well below us and better against equals and
  above (`S/docs/SESSION-STATE.md`, 13:48). Reading: weak teams that happen to ram queens beat a bot whose only weakness
  is the queen; the rating gap then costs far more than a win returns (one 2-3 loss cost 98 points where a 3-2 win
  paid about 25).
- One opponent was suspected of hard-coding map paths. An analyst tested for it and could not tell either way
  (`S/data/codex/astra/hardcode/report.md`). Another appeared to change its bot mid-night; it had not, and the swing was
  seed noise (`S/data/codex/astra/cachechange/report.md`).

## 7. Open problems at the deadline, by games cost

Ranked by the count the record supports. "Games" are of the 474-game sample unless stated. The classes overlap.

| # | Problem | Games it cost, as recorded | State at the deadline |
|---|---|---|---|
| 1 | Our queen dies after theirs is already dead | 73 losses of 474 (15%) that a living queen wins outright | Open. A working "their queen is dead" signal was built on 10-09 and not shipped, because the only rule that used it (hold length 4, feed her) killed her sooner. |
| 2 | Queen rammed by a short dragon, usually after stepping toward it | 205 of 286 queen deaths in 368 games; queen dead and theirs alive in 128 of 474 games, all lost | Open. one19 and one20 were meant to stop her ramming heads herself (not seen online); the step toward a visible head (19 of 21 against one team) was not fixed. |
| 3 | Out-eaten in rounds 20 to 100, worst on two-starter maps | 77 of 400 older games never grew, 56 lost; Tower Defense 6 of 30, Trauma 6 of 29 on the final builds | Open. Mechanisms found for three maps (room entry, far portal, pearl rooms); every constant tried cost more elsewhere. |
| 4 | Longest-dragon race with both queens dead | 115 losses of 232 such games | Open. Rally and earlier feeding tried locally: no gain or a loss. |
| 5 | Queen self-trap in pockets, corridors, behind portals | 69 of 286 queen deaths | Partly fixed (one16 for blind portals, one18 for the corridor case). Local Portals games still lost the queen in 6 of 8. |
| 6 | Long queen lost late | 25 of 474 (5.3%) lost from a lead at round 350 | Partly fixed. The cut to 2 was removed in one17; that sent her down the next branch, walking into paid reach, patched in one21, which went up 11 minutes before the deadline after four short local games and was never seen online. Standing still and shedding remains. |
| 7 | Long non-queen dragons rammed because a partly visible enemy looks short | 33 rams on dragons of 8+ in two battles, attacker fully visible in 3 | Open. The fix made long dragons timid and lost the longest-dragon race; dropped. |
| 8 | Unseen-map families (section 5) | Not measurable: no qualifier game on disk | 7x7, closed rooms where the queen stays, room entry, sonar off on very large maps: all open. |

What was verified about the final bot: one19 to one21 played the same games as their predecessor on 17 to 20 local
checks. No online game of one19, one20 or one21 was on disk at the deadline (`watch19-opus/verdicts.md`), so their
behaviour against real opponents is not recorded.

## 8. Findings that were later corrected

| Earlier statement | Later version | Source |
|---|---|---|
| "Ram the enemy queen whenever she is in reach" is worth 2 to 3 points (first study run) | About 1 point; half of it had already been online twice with no change in results | `REPORT.md` section 7 |
| Our 401 study games are one bot | Eleven runs of several builds | same |
| Top teams split earlier | They eat more; split timing per pearl is the same | `diag-split.md` |
| Their "no action" deaths are sacrifices | Before round 300, three in four are boxed-in deaths | `diag-sacrifice.md` |
| We are wiped out in 11 of 30 games | 5; the 11 counted wipe-outs of either side | `diag-wipeout.md` |
| A short dragon's narrow-tile gap comes from the no-way-to-tail penalty | Removing it changed nothing for 48 rounds | `early-opus`, log 11:34 |
| Trophy is broken in the live build | Not broken: the games ended by wipe-out before round 50, so the round-100 totals stopped early | `S/data/codex/astra/trophy-sonnet/table.txt`, log 12:05 |
| The queen is trapped in her start room on Portals | She leaves through a portal and is trapped in a pearl room | `qbox-opus`, log 12:14 |
| Banning all queen portal use was dropped because she got stuck | It was dropped on one report that it cut small-map intake; that report was right (Stripes round-100 pearls 54 to 32.5) | log 12:27, 12:29 |
| A cliff at 600 cells explains one probe map pair | Moving only the constant gave the same game; not the cause | `unD-opus`, log 14:05 |
| Queen self-trap is a new class in one15 | It was in every build | `loss15-sonnet`, log 12:34 |
| A build "improved against the queen hunter" on a 15-game set | Unknowable: the same bot scored 8 and 4 of 15 against an unchanged opponent | `cachechange/report.md` |
| The log says our queen was alive at round 300 in 133 of 474 games | Its own parts (112 dead before round 100, 175 in rounds 100 to 299) leave 187; my recount gives 187 | log 14:05; `qtable.py` |

## 9. How these findings were found, in case the game is different

1. A count by decision rule comes first: for every game, which of the win conditions decided it and what state the
   deciding unit was in. Every later question in this chapter hangs off that one table. We had it on 10-05 and still
   spent the next days mostly on economy.
2. The same script on both sides of the same games. Nearly every "they do X" claim that survived compares our side and
   theirs with one definition. Claims that died had compared our number with a remembered one.
3. Death classification by the board at the victim's last two turn starts (free tiles beside the head, attacker in view
   or not, steps and paid steps of the attacker). That is what separated "rammed in the open" from "one-way place" from
   "self-trap", and it showed that the last turn is usually too late.
4. Follow a behaviour to the round it starts. Two of our worst habits began on a round our own code chose (150 or 300;
   200). A step in a curve at a round number is a rule of ours, not the opponent.
5. Check whether the game ended before the checkpoint before reading a "pearls at round 100" figure.
6. Per-opponent analysts were told to answer in one fixed set of class names so that the lead could add them up. That
   is why section 3 can be a table.
7. Local games against one fixed weak opponent on generated maps could not see three whole problem classes (portal
   rules, idle loops on big maps, anything that needs a strong enemy). They were good for "is this the same game as
   before" and for nothing finer.

## 10. What to do next time

- On day one, write the win conditions as a table and build the counter of section 2 before any bot work. Re-run it
  after every rule change.
- If one unit decides the game, give it its own rules from the start and decide where it lives, not how it dodges.
  Measure its company (own units within a few tiles), not its distance to enemies.
- Treat any rule that says "never enter X" as a liability on unseen maps. Test it on a map where X is the only way out.
- Avoid thresholds on map size. Where one is needed, generate probe maps on both sides of it at once.
- Copy the turnover economy only with the death accounting beside it: gross pearls flatter it by a factor of five.
- Expect the cheapest unit to be the best attacker whenever a collision ignores size, and count your own "chance
  taken" rate against the opponents' early.
- Do not ship a branch-closing fix without reading which branch the unit takes next. Three of our last five uploads
  were repairs of the previous one.

## 11. Looked for and not established

- How the final bot played in the qualifier and the bracket: no games on disk.
- Any online game of one19, one20 or one21.
- Why seat A did so much better than seat B against one opponent, and whether it holds in general.
- The code cause of our low time on narrow tiles in rounds 0 to 100.
- Whether a queen kept near her start, or kept inside her own swarm, would live longer: the constant exists and was
  never played.
- What beats the flat swarm that never feeds, and the teams above 2,400: we have their fingerprints and no win recipe.
- The true pearl timers of seven ladder maps, and the size and start layout of Autarky and Prisoners Dilemma.
- A game-by-game account of the scene jun and Zhe flagged at 14:48 on 10-09 (game 1532570, round 469): looked at,
  not identified.
