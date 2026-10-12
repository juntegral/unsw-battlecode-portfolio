# [Idea] Nobody leaves a pearl lying for the leader

DRAFT, not posted anywhere. Written from the top-team study of 5 Oct (`unsw-swarm/data/analysis/top1/REPORT.md`).

What we tried: Nothing built yet. In 2,343 ladder replays we counted every turn on which a small dragon had a free pearl right next to its head, and whether it took it, for us, for our opponents and for the top three teams.
Did it work: Not tested. The count says our dragons take such a pearl in about 84% of turns until our own "leader" switch round and in 51–58% after it; nobody else's rate moves, and our natural-pearl intake falls by a fifth to a third from that round on.
Who decides now: The team. One OK from any member puts it in the queue. It touches the same switch as #14 and the big-map economy card #7, so their owners should say whether it becomes a new card or part of one of those.

**Idea by:** AI, from the top-team study

**Area:** economy (leader and pearl rules)

## Claim

Until the team starts to feed one dragon, no dragon of ours passes up a pearl for the sake of another dragon. Once feeding has started, a small dragon leaves the pearls within a few cells of a leader it can see, and no others.

Today, from round 150 on maps over 1,200 cells and round 300 on smaller ones, a small dragon of ours may not take, or walk to, any pearl within 9 cells of the place where it believes our longest dragon is. That rule costs the team a fifth to a third of its natural pearls and gives the leader almost nothing until feeding starts. The claim has no map name and no map size in it; the switch round, the split stop and the start of feeding stay as they are.

Words:
- **leader**: our longest dragon; each dragon keeps one record of who and where it is, from what it sees and hears by sonar.
- **switch round**: `grow_round` in `mybot2/main.cpp`: 150 on maps over 1,200 cells, 300 otherwise.
- **pearl zone**: the 9-cell area around the believed leader (`LEADER_PEARL_RADIUS 9`) in which other dragons do not take pearls after the switch round.
- **feeding**: small dragons die on purpose next to the leader, which eats the pearls they drop. In our bot it starts at round 400, at 300 in queen-feeding mode, or at 200 when we have 56 dragons.
- **free pearl turn**: a dragon of length 2–4 that is not the queen, no enemy head in its 7x7 view, and a pearl on a free cell right next to its head with a way out behind it.
- **natural pearl / corpse pearl**: one a tile produced / one a dead dragon left.
- **race**: a game that reaches round 500 with both queens dead; the longest single dragon wins.
- **top three**: Vibing++, SSS, forgot to mention. **small / big maps**: 1,200 cells or fewer / more (only because our code switches there).

## Evidence

### Measured (ladder replays, opponents rated 2000+, the map Schooltime left out; 401 games of ours, 1,637 of the top three)

Free pearl turns taken, around our switch round:

| | 20 rounds before | first 10 rounds after | 20–50 rounds after | later (to round 300 on big maps, 400 on small) |
|---|---|---|---|---|
| meow live bot, big maps (switch at 150) | 84% | 64% | 60% | 58% |
| meow live bot, small maps (switch at 300) | 83–85% | 64% | 51% | 53% |
| our opponents in the same games | 81–86% | 82–85% | 79–84% | 76–85% |
| forgot / SSS / Vibing++ | 91–93 / 82–84 / 89–90% | the same | the same | the same |

- Every one of our eleven runs (two ladder downloads, live and candidate halves of the smoke pairs) shows the step. Four separate counts by different scripts agree (`recount3.py`, `c_adj.py`, `h_c3.py`, `y_c3a.py`).
- By what each dragon itself believes (82 games of an earlier live bot whose sonar pings can be read): after the switch it takes a free pearl in 16–35% of turns when the pearl is within 9 cells of its believed leader and in 70–96% when it is 10 or more cells away. Before the switch the rate is 72–93% at every distance.
- Half of the zone turns are around nobody: turns inside a believed zone are 51–56% of all free pearl turns on small maps and 33–38% on big maps, but the zone of our true longest dragon covers only 32% and 14%. The rest sit around the last known place of a dragon that is dead or short.
- Our natural pearls per 50 rounds, same games: small maps 39.5 before the switch, 31.0 and 29.4 after (the other side 51.4, 48.7, 44.4); big maps 81.1, then 54.0 and 47.1 (the other side 130.6, 130.8, 127.8). Per small dragon the drop is 20% and 38% within 25 rounds, so it is not a matter of having fewer dragons.
- Our total length stops growing at the switch: small maps 60, 61, 61, 62 at rounds 250 to 400 (the other side 95 to 99); big maps 109, 126, 125, 122, 122 at rounds 100 to 300 (the other side 152, 207, 260, 300, 327).
- What happens to a natural pearl left in a zone: 62–75% are eaten by another small dragon of ours about 10 rounds later, 11–26% by a leader, 4–17% by the enemy. A pearl left lying also blocks its tile from producing the next one.
- The leader does not eat more natural pearls after the switch (3.2 then 3.2 per 50 rounds on small maps, 4.1 then 3.8 on big). Leaders of teams with no zone eat as many (3.0 and 4.6).
- Nobody else leaves pearls for a leader before feeding: within 9 cells of their own longest dragon their small dragons take 80–96% of natural pearls (ours 29% on small maps, 48% on big).
- Late in the game the zone does help the leader a little: per small-map race the dragon that ends as our longest eats 3.4 corpse pearls and 2.4 natural pearls that a small dragon next to them had left alone (2.2 and 0.9 on big maps). 7 of our 41 race wins were closer than that. This is why the claim keeps a small zone next to a visible leader once feeding has started.
- Games: 1029033 and 1045374 (weakhold, against WeHaveQuizzes). At round 300 we have 65 total length against 34 and 94 against 43. Natural pearls per 50 rounds from round 250: 40, 16, 9, 3 and 47, 26, 4. Total length falls to 44 and 59 by round 400 with nobody feeding yet; both lost on the longest dragon.
- From the code: `refresh_leader_zone()` sets the zone from the leader record whenever `round > grow_round`; `in_leader_pearl_zone()` is read in seven places (`survey_from()` four times: zone pearls, tiles about to produce a pearl and fountain tiles are not targets; `look_cell_value()`; `score_step()` twice: no `EAT_BONUS 300`, and `ZONE_PEARL_PENALTY 600` for anyone but the leader). There is no toggle.

### Not measured

- The effect on wins. No game was played. Estimate from played games: +1 to +8 wins in 401 (+0.3 to +2 points on 27.9%), most likely about +1 point; 8–10 more natural pearls by round 400 on small maps and 30–45 more by round 300 on big maps.
- Whether more length turns into wins for our bot at all. Twice it did not: "stride" (+14% economy locally, no more wins) and the trade-on-contact build (+21% length at round 300 on big maps, 0 wins of 12 online).
- The exact form proposed for the feeding phase (a zone of about 4 cells around a leader in view). It was designed from the counts above; only "zone off in every phase" was counted.
- What a dragon believed in games after the earlier live bot. Later builds seal their sonar pings; the belief numbers are from 82 games. The rate step itself is in every build.
- Why a dragon declined any particular pearl. Replays have no scores; the code reading fits every number but is not proven turn by turn.
- Anything against the top three (21 games of ours) or on maps nobody has seen.
- Earlier trials did not test this: `GB300` and `LC_LEAD_ROUND 200` moved the whole switch (leader status, zone and split stop together); card #14 replaced only the split stop.

## Expected signal

- Free pearl next to the head taken, after the switch round: from 51–58% to over 80%, on both kinds of map. This is the direct check and it can be counted in any set of replays, local or online (thousands of such turns in 20 games).
- Natural pearls per 50 rounds after the switch: from 54 to 70 or more on big maps, from 31 to 37 or more on small maps.
- Total length at round 300 on big maps: from about 122 to 150 or more. On small maps total length keeps rising from round 300 to 400 instead of standing at 61.
- The share of feeder pearls our final longest dragon eats stays where it is (39% on small maps, 25% on big), and our longest dragon at round 400 and at the end is not shorter.
- In the "why" table: our longest against theirs at the end should be level or better on big maps and unchanged on small maps; total length up on both.

## What would show it's wrong

- The free-pearl rate stays under 70% after the switch: the rule is not firing, and the build is not done (look for the other six places that read the zone).
- The rate rises but natural pearls per 50 rounds do not: the pearls were being eaten by other dragons of ours anyway and the zone only delayed them.
- Our final longest dragon eats a smaller share of feeder pearls, or our longest at the end is shorter by 2 or more on small maps: small dragons are eating what the feeders drop, and the zone in the feeding phase is too small.
- Total length rises and our losses on big maps look the same, with more of our dragons rammed in rounds 150–300: the extra length is lost at contact, and the limiting rule is how we fight, not how we eat.
- More of our leaders die boxed in by own small dragons than today (today small own dragons are 8% of a leader's blocked neighbour cells).

## Test plan

1. **Build**, behind a new toggle that is off by default. In `refresh_leader_zone()`: the zone is active only when `feeding_phase()` is true and the leader's head is in the dragon's own view, with a radius of about 4 instead of 9 (our feeders die within 3 cells of the leader's head). Leave `grow_round`, `is_leader()`, `split_child_size()` and the feeding code alone. Keep a second setting for the plain variant (zone off in every phase; note that radius 0 leaves one cell, radius −1 or an early return switches it off) so the two can be compared in step 2. Toggle off must replay identically on the old 10 maps.
2. **Behaviour check with replays** (small local run). Count free pearl turns taken before and after the switch round with the counting class in `unsw-swarm/data/analysis/top1/recount3.py` (it walks one replay file at a time, so it works on local replays too), and natural pearls per 50 rounds. Pass: over 80% after the switch on both kinds of map. Keep three replays: a small dragon eating next to the leader before feeding, a feeder's pearls being left for a leader in view after feeding has started, and one pearl still declined (to see which rule did it). Compare the amended and the plain variant on the leader's share of feeder pearls and on our longest at the end.
3. **Sparring pool, including the queen hunter.** Usual held-out, transposed and old-10 sets. Local games are mirror-like for this rule (neither side eats what the other leaves), so read them for harm, not for gain: wins not clearly down on any map family, our longest at the end not shorter, wipe-outs not up. The queen hunter is in the pool to check that a longer, hungrier team around the leader does not get our queen or leader killed more often.
4. **Online 30:30 comparison** (`tools/smoke.py pair`, same opponents and maps for base and candidate). Judge on the behaviour numbers under "Expected signal", by map family, with the "why" table (our longest against theirs, total length). Report wins too, but 30 games each cannot show a one-point change (one point is 0.3 wins in 30; chance alone moves two halves of the same bot 3.5 wins apart), so wins alone neither pass nor fail it.

Related, as its own card if the team wants it (safe to run next to this one, different code and a different number to read): any dragon of ours with the enemy queen's head in view and in reach rams her, at any length (`QUEEN_HUNT` on, and `real_queen()` instead of `is_queen()` in the first line of `mark_hunt_targets()`). We take 23% of such chances; Vibing++ and SSS take 99%, our opponents take 86% of theirs on our queen. About +1 point as well; details in `REPORT.md` section 4.
