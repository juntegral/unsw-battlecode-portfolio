# Reports sent to the lead by qdead-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 02:25:51 — qdead heads-up: cause found, signal switch built

qdead heads-up (11:27): the "their queen is dead" signal fails for two reasons, and QUEEN_DEAD_KNOWN:8 (src/w-qdead/main.cpp, all-off hash 92fb69564fbd ok, one14 profile = mNps hash ok) fixes the second fully and the first partly. NOT ready to go live yet; QUEEN_HOLD_LEN itself looks doubtful.
[M] Cause 1 (ceiling): the rammer dies and a dead dragon's sonar is discarded (rules/sonar.md), so only a third dragon can know. In 240 old local games, 388 queen deaths: a living enemy dragon had her head in view the turn before in only 164 (42%); my proof rules catch 95 (24%), with 0 false "dead" in 1,600 turns where a dragon lost sight of a living queen (replay simulation, timers and walls ignored).
[M] Cause 2 (relay): in one traced game (gx_open_64x16 seed1 side0, her death r73) the EXISTING rule did fire at r74 on dragon 27, but without my switch only 3 dragons ever knew and our queen never; with the switch (dead-ping on all four directions for 8 rounds after learning) our queen knew at r76 and the whole side followed.
[M, 1 game, warning] With the signal working QUEEN_HOLD_LEN:4 did fire (queen splits 6>4 four times, never below 4) and she died EARLIER (r96 at L5, 1 free side, 6 mates within 5: the feeding crowd boxed her; without hold she lived to r200). I added QUEEN_HOLD_FEED (default true = unchanged; false = hold without the feeding) and am playing that arm now. Game slots are shared, about 25 more games by 12:00.

---

## 2026-10-09 02:47:55 — qdead final: signal works, hold not ready

qdead-opus FINAL (11:48): the "their queen is dead" signal now works (QUEEN_DEAD_KNOWN:8), but QUEEN_HOLD_LEN does not keep our queen alive and its feeding part wrecks the side.
Ready to go live: NO. Nothing here should ship today; QUEEN_DEAD_KNOWN alone has no useful consumer yet.
How sure: signal counts are solid (22 traced games, 0 false "dead"); the hold verdict rests on 4 armed maps, enough for the feeding harm, thin for hold without feeding.

HASH: all-off bots/qd_off = 92fb69564fbd (equal); one14 switches on my source = 84497be4d00e = mNps (equal). Diff +154/-2, 0 warnings.
Switches added (all off = base): QUEEN_DEAD_KNOWN (int, 0 off; N = rounds a dragon that learns it sends the dead-ping on all four directions), QUEEN_HOLD_FEED (true = hold as built; false = hold without feeding), QDK_TRACE (local only, writes a file named by env QDK_LOG; never switch on live).

WHY IT NEVER FIRED
1. [C] rules/sonar.md: a dragon that dies casts no sonar, so the rammer can never tell. Only a third dragon can know.
2. [M] 240 old local games, 388 queen deaths: a living enemy dragon had her head in view the turn before in 164 (42%). That is the ceiling.
3. [M] The existing rule (corpse pearl on her last head cell) does fire. The relay is what failed: in gx_open_64x16 seed1 side0 (she dies r73) dragon 27 proved it at r74, two mates heard it, and all three were dead by r76; nobody else ever knew. The old relay sends on 2 directions a round, too thin for witnesses standing in the fight.
4. [M] With QUEEN_DEAD_KNOWN:8, same game: our queen knew at r76, 600+ dragons over the game.

SIGNAL COUNTS [M] (traced bot on both sides, 22 games = 44 sides, gx 24x12 and 64x16 plus 4 ladder maps)
their queen died 38 | a dragon proved it 10 (26%) | ours alive at that time 17 | our living queen learned it 6
proofs logged while she was still alive 0 | retractions 0 | proofs by the old rule 12, by my new rules 2
Simulation of the rules on the 240 old games: 95 of 388 deaths provable (24%), 0 false in 1,600 turns where a dragon lost sight of a living queen (walls and pearl timers not modelled).
False positive excluded how: new rule 1 needs her whole body in view (2 or 3 long, none on the view edge, no portal) and every cell one move can reach in view without her, counting pearls she could eat; rule 2/3 need corpse pearls on her own cells. Any later sighting, own or relayed, cancels the flag. Residual I could not exclude by proof: a corpse pearl dropped beside her between the two turns while she sprints out of view. Not seen in any count.

HOLD, same map, seed 1, side 0, against mNps; off = QUEEN_DEAD_KNOWN:8 only [M]
map            our queen dies r (off/hold no feed/hold+feed)   result            r100 pearls      r100 dragons
open_64x16     101 / 118 / 96                                  loss/loss/loss    323/323/334      59/59/58
islands_24x12  282 / 217 / 180                                 loss/loss/elim    99/100/105       18/17/10
ring_24x12     alive / alive / 117                             win/win/elim      88/88/80         9/9/4
rooms_24x12    71 / 69 / 73                                    win/loss/elim     70/46/30         10/5/2
Queen deaths per 100 rounds after theirs died: off 3 in 322 = 0.93; hold no feed 3 in 272 = 1.10; hold+feed 4 in 207 = 1.93.
Does she still split: never below 4 once she knows (only 6>4), in both hold arms. Does she still pay: yes, 3 paid moves below 4 in the no-feed arm (open r101 L6 pays 4; rooms r46; ring r85), the gate's "trapped / no free run" exits.
She died at L4 in all three no-feed deaths (rammers L3-5 from 2-5 steps, 0-2 free sides, up to 10 mates within 5). Length 4 did not protect her: the 0.08 figure was correlation.
Feeding: mates die beside her, she splits 6>4 again and again, dragons at r100 halve or worse on three maps, three eliminations.
Before the first proof all arms are the same game (events identical in 8 of 8 pairs). rooms_24x12 shows the cost when her queen dies early (r24): hold armed at r25 and our r100 pearls fell 70 to 46.
Noise warning: open_64x16 without any signal (qd_base) had our queen live to r200 and won; with the signal only, r101 and lost. One game, the lines diverge after r74; I cannot say the relay traffic caused it.

NOT DONE: task 4 (queen keeps away from enemy heads). No time to show it firing.
WRONG IF: a "see"/"know" line appears before her death round in more traced games (sig.py prints EARLY); or hold without feeding shows fewer queen deaths over 40+ armed games (mine is 4).
FILES: ~/meow-redteam/solo/src/w-qdead/main.cpp; ROOT/data/codex/astra/qdead-opus/qdead-opus.diff, sig.out, look-nf-dk.out, look-on-dk.out, census.py, sig.py, look.py, qdeath.py. Runs: solo/runs/qd_{dkdk,dkdk2,dk,nf,on,base}. No games of mine are running.
