# Red team: trying to break the five hypotheses

Done by the lead session after writing `hypotheses.md` (no separate sub-session could be started; see REPORT.md, "Limits").
To keep it from being a rubber stamp, every attack below is a new measurement written after the hypotheses, not a re-reading
of the same tables: `redteam_checks.py`, `redteam2.py`, `redteam3.py`, `approach2.py`, `approach3.py`, `whatif.py`, `whatif2.py`, and a
third pass over all replays for the strictest count (`extract3.py`, `an3.py`, `an3b.py`), which changed two things in the report.
Their raw output is in the `.txt` files of the same names. Schooltime (sealed queens) is excluded; opponents are rated 2000+.

A warning that applies to all five: stronger teams have more of everything. A top team near our queen is usually a top team that
is already winning. So I trust only numbers that are counted per chance (per approach, per round in reach) or inside a
stratum where the economy is held equal, and I say so where that was not possible.

---

## H1. Ram the enemy queen whenever in reach; let 5–9-long dragons hunt

**Attack 1: "they kill more queens because they are winning anyway."** Partly true. At the moment of the kill the killer's team had more total length (ratio above 1.1) in 65% of large-map kills, 72% on medium, 77% on small; on small maps the median ratio is 2.6, which is mopping up. So kills per game overstate the habit.
What survives: the count per approach. With a dragon already within 6 steps of the enemy queen, the top three end 7.3% of 2–3-long approaches and 28% of 5–9-long approaches with a ram on her; we end 2.5% and 2.8%. Being near her is the same event for both sides.

**Attack 2: "per approach is still unfair, their approaches are closer or happen when she is cornered."** Looked only at approaches where the attacker got within 2 steps: top three 21% (2–3-long), we 11%; on maps over 1,200 cells 17% against 4%. Looked only at short queens (4 or less) before round 300: 5–9-long attackers 42%, 2–3-long 8%. The gap stays.

**Attack 3: "the length effect is selection: a long dragon near her is there on purpose, a short one is passing by."** Probably part of it, and replays cannot separate intent from ability. But the mechanics point the same way: a 2–3-long killer began the fatal round 1–3 steps from her in 83% of its kills, a 5–9-long one 4 or more steps away in 86%. Teams outside the top three show the same step up (5–10% for 2–4-long, 20–22% for 5–9-long), and so does every map with enough cases. Either reading leads to the same instruction.

**Attack 4: "it only works against weak queens."** Against another top-three team they still kill her in 79% of large-map games, 56% medium, 50% small. Against test4, an opponent we share (112 of our games, 73 of theirs): they kill her 0.48 times a game, we 0.21; her queen is alive at the end in 29% of their games and 48% of ours (medium maps: 32% and 68%).

**Attack 5: "killing her does not win games; winning kills her" (reverse causation).** A wipe-out win kills the enemy queen by definition, so any table that mixes wipe-outs in is circular. I redid it on round-500 games only (`redteam3.py`). With the own queen dead at the end:

| | she lived | we rammed her | she died another way |
|---|---|---|---|
| Top three | 0 of 108 | 156 of 242 = 64% | 40 of 84 = 48% |
| Top three, behind at round 150 | 0 of 40 | 33 of 65 = 51% | 15 of 35 = 43% |
| Us | 0 of 51 | 12 of 30 = 40% | 16 of 71 = 23% |
| Us, behind at round 150 | 0 of 34 | 4 of 18 = 22% | 9 of 54 = 17% |

The left column is the rule itself, not a correlation: a living enemy queen beats a dead one every time. The kill does not win the game; it turns a certain loss into a longest-dragon contest that we currently win about one time in five when behind and more often when even.
Early kills carry no extra value: in games even at round 150, a kill before round 200 gave 65% wins against 60% without one. Only the state at round 500 counts.

**Attack 6: "the effect is too small to matter."** This one lands. Of our 289 games, 59 were round-500 losses with their queen alive. 30 flip if she dies and nothing else changes. In 19 of those 30 we never got within 6 steps of her (nearly all of them Trauma and Portals games, where she lives behind portals), and none of the 12 Australia and Islands games flips at all, because we are too far behind on length. Applying top-three conversion to the approaches we really made gives about 8 extra wins in 289 games; the strict turn-level count below gives 5 or 6. So +2 to +3 points against 2000+ teams, not +10. A 30:30 online comparison cannot see that (its noise is around 12 points), so the online test has to be judged on the mechanism (kills per game, her survival), not on wins.

**Attack 6b: "an approach is not a chance; maybe she was never really rammable."** This was the weakest point of the first draft, so I measured it turn by turn (`extract3.py`, `an3.py`, `an3b.py`): at the start of a dragon's own turn, after both queens have moved, is there a path of free cells to her head within its reach? It cut two ways.
- It made the behaviour gap sharper. With a 2–3-long dragon, Vibing++ and SSS take 249 of 254 such chances (98%); we take 65 of 183 (36%). With a dragon 4 or longer we take 9 of 466 (2%); Vibing++ and SSS take 26%. When the ram costs at most one paid step and is not by the team's longest: 94% and 96% against our 34%.
- It made the size smaller and corrected an example. "In reach at the start of the round" had given 10.2 rounds a game on big maps; real chance-turns are 4.8. In game 1029030 I had first cited two rounds in which our 2-long stood next to her head at the start of the round. Those were not chances: she moves first, and a 2-long can only reach a neighbouring cell. The real chances in that game were seven turns in rounds 227–248, all by dragons 3 or longer against a 2-long queen. And in 37 games with a cheap chance and no kill, only 9 were round-500 losses with her alive, of which 6 flip.

**Attack 7: "we already tried it and it did nothing."** `work/plan.md`, 13:51 on 2 Oct: hunting by dragons of length 4 or less (H4) scored 59/120 against v57 where the base scored 60, and 57 against 58 versus a hunter sparring bot; rejected. Two reasons this does not settle it: (a) local opponents are our own bot, whose queen is alive at the end in only 11–20% of local games, so there is almost nothing for a kill to change; on the ladder she lives in 41%; (b) the test capped hunters at length 4, the group that converts worst. Card #31's first look (16 games) shows the same thing from the other side: a 2-long tailed her for 60 rounds, one sat next to her head for three rounds and nothing happened, another followed 3 cells behind for 90 rounds. So the earlier work does not contradict H1; it shows that short hunters and local scoring are the wrong tools.

**Attack 8: "could it backfire like the passage change?"** The passage change hurt because it moved our own queen. H1 does not touch her. Costs I can see: one dragon per kill (mean killer length on large maps 5.6, small and medium 3.0–3.5), paid sprint segments on a miss (a 5-long that sprints 5 steps ends 2 long), and dragons wandering after her if the chase part is too eager. Guard rails: never the leader, never our queen, cap the hunter's length, and build the "ram when in reach" part before the "walk to her" part.

**Attack 9: sample size.** Top-three side: 650 queen kills, 7,216 approaches. Our side: 2,817 approaches, 74 kills, 289 games, 59 relevant losses. The conversion gap is far outside noise. The win estimate (8 of 289) rests on 11 games and could easily be 4 or 12.

**Verdict: survives.** The behaviour gap is real, large, shared by all three top teams and by the rest of the 2000+ field, and explained by two lines of our code. The win effect is modest and concentrated on maps where she is reachable. Local win counts will not show it.

---

## H2. Dragons near our queen ram small enemies that come for her

**Attack 1: allies near the queen mean a safe place, not a guard.** The table that looks best for H2 (3+ allies near: queen rammed in 2–4% of approaches instead of 7–10%) is confounded exactly this way: "died in any other way" drops as well (from 12–17% to 4–6%), and a guard cannot explain that.
**Attack 2: a matched check.** For queens with a small enemy within 3 steps at the start of a round, the chance of being rammed in the next 5 rounds was 12.3% with an ally within 3 steps and 14.6% without (top three, queens 4 or shorter; 1,382 and 4,758 rounds). A difference of 2 points.
**Attack 3: earlier experiments.** Escorts (`QUEEN_DEFEND_RADIUS 4`) left the local queen-alive rate at 11–20%; give-way and guard variants cost wins on small maps.
**Attack 4: backfire.** 75 of our queen's 81 self-inflicted deaths happened with no free neighbour cell, and the bot author found our own dragons taking her last free cell in 14 of 16 Portals deaths. Pulling allies towards her could add to that.
**What holds:** our defenders do ram intruders far less than theirs (5% of approaches against 13–17%).

**Verdict: not first.** Plausible, small measured effect, real risk of crowding her. Worth revisiting after H1, since both come down to the same line in `mark_trade_targets()`.

---

## H3. Our queen must never die by her own move

**Attack 1: is the comparison fair?** Vibing++ and forgot record trapped deaths as "no action" (23% and 8.5% of their games), and some of those are deliberate. Against SSS, which crashes the way we do, it is 28% against 11.6%. Still more than double.
**Attack 2: is it general or two bad openings?** 16 of the 81 are the same two openings (Portals round 9–10, Slithery Fight round 3). The qualifier uses unseen maps, so fixing those two by name is worth nothing. The other 65 are spread over 13 maps.
**Attack 3: does she just die later?** Unknown. The what-if assumes she then survives like a top-three queen on that map (9 wins in 289 games). If rams simply replace crashes, the gain is smaller.
**Attack 4: earlier experiments.** Card #25 (`QUEEN_WAIT`) never fired, because she is 2–3 long when boxed in and cannot split; my ladder count agrees (74 of 81). Card #23 (`QUEEN_NO_TRAP`) is being built. Keeping her longer (`QUEEN_KEEP 5`) cost wins locally.
**What is new here:** the size on the ladder (28% of games, 22 of them direct queen-rule losses), that no enemy was near in 68 of 81, that 58 of 81 happened on a cell with one or two open sides, and that 49 of 81 were on maps of 600 cells or fewer where our queen rules are off.

**Verdict: true and worth about as much as H1, but it is already two cards.** I pass the numbers on rather than propose it again.

---

## H4. Keep the queen in the quiet rear of our own swarm

**Attack 1: one team only.** SSS does it; Vibing++ does not and is rated higher; forgot only looks like it while feeding its queen. By the study's own cross-check rule, a thing one team does is a quirk until shown otherwise.
**Attack 2: we already look like that in relative terms** (our queen has 0.6–0.75 of our team's enemy density). Our problem is that the whole team has more enemies around it.
**Attack 3: backfire.** Same crowding risk as H2; safe-zone and corner variants are already on the board (#16).

**Verdict: does not survive as a recommendation.** Keep as a note on how SSS plays.

---

## H5. Ram the enemy's longest dragon late

**Attack: is there a gap?** No. With their leader inside the reach of one of our heads we ram it 20 times per 1,000 such rounds; the top three 22–34. Exposure is the same (13 rounds per large-map game against 12–17). The leader-safety and assassin variants the author tried (BIG_ESCAPE, BIG_TRUE_REACH, ASSASSIN) were all neutral.

**Verdict: dropped.** Late leader kills decide top-team games (51 wins of 55 for the side that alone made one), but we already take those chances at their rate; what we lack is the length to profit from them.

---

## Summary

| | Evidence per chance | All three teams | Survives the economy control | Earlier tests | Backfire risk | Verdict |
|---|---|---|---|---|---|---|
| H1 hunt her queen | 36% vs 98% of legal rams by 2–3-long dragons; 2.5% vs 7–28% per approach | yes (forgot less: 67%) | yes (round-500 only) | local, short hunters, blind to it | low | **survives**, worth +2 to +3 points |
| H2 guard ours | 5% vs 13–17% defender rams | yes | weak (2 points matched) | local null | crowding | later |
| H3 no self-kills | 28% vs 4–12% of games | yes | not applicable | #25 never fired, #23 building | low | true, already owned |
| H4 rear queen | SSS only | no | no | #16 | crowding | dropped |
| H5 leader kills | 20 vs 22–34 per 1,000 | yes | yes | neutral | low | no gap |
