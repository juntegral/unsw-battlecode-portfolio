## Not proposed, and why

Each line gives the number that decided it. The first block is from the lead's list of mechanisms, the second from
the earlier candidate list (`run1/hypotheses.md`), the third from the close reads.

**From the lead's list**

- **The longest-dragon race: start feeding earlier.** The mechanism is real: in round-500 games with both queens
  dead and total length level at round 400 we win 13 of 36 and the top three 95 of 156, our longest there is 17
  against 27 at round 400, and the gap is made between rounds 300 and 400 (our longest grows by 5, theirs by 18; after
  round 400 both grow by about 20; `h_race.py`). But it has been tried directly: feeding from round 330 instead of 400
  (v46) won 24 of 60 online against dev test 1 where the base won 23, and feeding from 330 and 300 won 70 and 69 of
  152 locally where the base won 76 (`work/plan.md`). And the ceiling is small once the economy is held fixed: inside
  the same band our win rate with both queens dead is 12% against 16% and 41% against 51%, worth +6.9 wins of 268
  (`h_states.py`). Of everything dropped this is the one I was least sure about dropping.
- **Team-mates keep off the queen's last exit** (nose to nose 20, a team-mate's body 14, her own child 11 in A4's
  count). The part not already inside candidate 2 is 31 deaths, +6 strict and +0.5 to +2.5 realistic wins (`h_c2.py`).
  Asking team-mates to give way was tried locally and lost: 84 wins of 156 against 96. Vibing++ has the same problem
  (34 nose-to-nose deaths in 502 games) and is rank 1.
- **The queen rules on every map as a whole** (`QUEEN_MIN_CELLS` to 0). Candidate 2 takes only its own tests off
  the switch (the order of moves, the paid escape, the split near an enemy, the ram, the cut). The portal ban was
  tried on all maps and one small map went to 0 wins of 8, because there the queen is the only dragon that reaches
  the food behind the portal early; its deaths are 14, +0 to +2.7 realistic wins.
- **The queen never steps into a place with no way round** (30 terrain dead-end deaths, +0.4 to +4.0 realistic wins).
  It needs a new terrain test on a map she only partly knows, and the neighbouring online trial (qn23, "no trap")
  had more such deaths, not fewer: 8 of 45 games against 15 of 215.
- **Nobody near our queen rams an intruder** (1.7-4.9% against 9-20%). Not a rule of its own: it is candidate 4
  happening near her. No top team moves towards an intruder (SSS dragons near the queen moved nearer 40 times and
  farther 44, `deep-read-2.md`).
- **The split stop for dragons longer than 4** (card #14's subject). It is inside candidate 3, but it is not where
  we differ: after our switch our dragons of 5-9 split on 5% of their turns, the top three's on 9%, our opponents' on
  3%, and our 4-longs on 26% against 18% (`h_c3.py` part C). The eating is what stops.
- **Ramming the enemy's longest dragon late.** No gap: 20 rams per 1,000 rounds of exposure against 21-33
  (`findings.md` section 5).
- **Stride** (free sprint steps). +14% economy locally and no more wins; online 6 wins against 8 on 30 pairs
  (`safer-stride-test-result.txt`). Sprinting does not separate the teams (forgot makes 10 long moves per 50 rounds,
  SSS 43; `deep-read-3.md`).

**From `run1/hypotheses.md`**

- **H1's second half, hunters of 5-9 that walk to her.** The prize is larger than candidate 1's: 44 of our 84
  round-500 losses with her queen alive flip if she dies, and only 13 of those had an in-view chance. But the one
  trial with a walk (qh31) lost 36 hunters in head-ons with other enemies for 8 rams on her, and kills went from 10 to
  11. H1 also kept our longest dragon out and capped the price at 2 segments; I dropped both limits because Vibing++
  and SSS use the longest (30 of 30, 28 of 28) and 7 of the 13 strict flips need an attacker of 5 or more paying 1 to
  3 segments.
- **H2, dragons near our queen ram small intruders.** See "nobody near our queen" above.
- **H3, our queen never dies by her own move.** Kept as the parts of candidate 2 that have a countable fix (the cut,
  the ram); the portal and dead-end parts are above.
- **H4, the queen lives in the quiet rear.** Where she lives is not what differs: our queen spends 44% of her rounds
  more than 10 cells from her start and SSS's 45%; what differs is the price out there (8.1 rams per 1,000 rounds at
  16-25 cells against 2.9; `deep-read-4.md` 5c), which is candidates 2 and 4. The local safe-zone and home-radius
  toggles (card #16) gave no gain in survival.
- **H5, ram their longest late.** No gap, see above.

**From the close reads**

- **A3: "a small dragon rams alone"** (drop the head count). The top three do not: alone or outnumbered they ram a
  same-length enemy on the next cell in 5-24% of cases and a shorter one in 3-11% (`h_c4walk.py`), and such rams
  lose them 0.2 to 1.3 segments each (`h_c4pearls.py`). Locally the same change won 60 of 118 against 68.
- **A2: feed the queen from round 200 by the clock** (forgot only; it wins 52 of 71 games with both queens alive).
  Only one of three does it, and for us both queens are alive at the end in 14 of 401 games.
- **A, A2: send fresh split children at the enemy queen or leader** (Vibing++ only: 4 of 10 leader kills).
- **A2: broadcast the enemy queen's cell by sonar** (SSS only; found in 26-39% of its pings). No top team rams a
  queen outside the attacker's own view (3 of 697 such chances), so the broadcast does not make kills by itself.
- **Openings on maps whose food lies behind a portal or outside the start room.** Known to the team, large on four
  maps, and not a rule that can be stated without the map.
