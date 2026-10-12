# Reports sent to the lead by loss15-sonnet

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 03:02:34 — 1522311, 1522401, 1522569 are one14, not one15

Heads-up from loss15-sonnet (12:05 KST): the three battles you named are not one15. Replay bot id is 21497 (one14) for 1522311 (Quaker Qubits), 1522569 (WeLikCoding), 1522426 (SKKU). 1522401 isn't on disk. So far the only one15 game (bot 21583) on disk is 1522669 vs tozoman on Autarky: WIN by elimination at r167, 54 dragons / 136 total vs 0. Zero one15 losses so far. Tools are ready and I'm polling for new one15 games; the one14 losses I'll keep in a separate section, labelled as one14.

---

## 2026-10-09 03:09:50 — one15 vs Cache me outside: 6 of 10 losses had their queen dead first

loss15-sonnet, 12:15 KST, early finding [M] from replays. one15 (bot 21583) set one15-c1 vs Cache me outside (2264) is in: 10 losses of 15, all seat A. In 6 of the 10 losses THEIR queen died before ours, so our queen alive at the end would have decided the game on queen length (ours >0 vs their 0):
- Slithery Fight 1523634: their Q dead r42, ours (L44!) rammed r391 by an L3 dragon (id 1478) that used 4 steps (1 free, paid); we then lost on longest dragon (53 vs 78).
- Islands 1523622: theirs dead r57, ours (L3) rammed r222 by L20 (id 462), 7 steps, 5 free; she had moved from 3 to 1 free cell.
- Default 1523627: theirs dead r67, ours (L2) rammed r230 by L4 (id 103), 3 steps (1 free); she had 3 free cells before and after.
- Trophy 1523630: theirs dead r90, ours L3 rammed r137 (L3 attacker, 2 steps, 1 free), 1 free cell.
- Tower Defense 1523625: theirs dead r65, ours L3 rammed r112 (L4 attacker, 2 steps, 1 free), 1 free cell.
- Stripes 1523624: theirs dead r16, ours L3 rammed r47 (L2 attacker, 2 steps, 1 free), 1 free cell.
After the queen died, all of these ended in elimination or a lost longest-dragon count. Common habit: the queen stays short (L2-4 for 100-200 rounds) and is hunted by small dragons paying for extra steps. Other 4 losses: QoS 1523628 (queen rammed r136, unseen, their Q alive), Australia 1523621 (queen rammed r127 by L9, unseen), Trauma 1523632 (lost queen race 35 vs 39, starved: 3 dragons / 10 total at r100 vs 25 / 62), Maze 1523623 (queen of length 2 died on her own move into her own tail at r101, 0 free cells, a split the turn before; I am checking whether that is a bug). Trauma r100: one15 total 10 vs one14 32 on the same opponent, so the starvation did NOT stop there; Tower Defense and Stripes (1 dragon / 3 total at r100) are bad in one13, one14 and one15 alike. Full tables follow in the 12:35 report.

---

## 2026-10-09 03:13:18 — loss15-sonnet first report: 10 one15 losses classified

loss15-sonnet FIRST REPORT (12:25 KST). Full file: ROOT/data/codex/astra/loss15-sonnet/losses.md (5 lines per game, newest first, plus tally and the r100 line).
1. One15 games on disk: 16 = set one15-c1 (Cache me outside 2264, all seat A: 5 W / 10 L) + 1522669 (tozoman, Autarky, WIN). No ranked one15 game yet; the ranked battles you named (1522311, 1522401, 1522569, 1522426) are all one14 (bot 21497). p1 / s1 / q1 not on disk yet.
2. Tally of the 10 losses [M]: queen rammed from a one-way place 6 (Slithery 1523634, Islands 1523622, Trophy 1523630, Australia 1523621, Tower Defense 1523625, Stripes 1523624); queen rammed in the open 2 (Default 1523627, QoS 1523628); queen boxed in / self-trapped 1 (Maze 1523623); out-eaten start, queen alive, lost queen race 35 vs 39 1 (Trauma 1523632). In all 8 rammed deaths the attacker PAID for extra steps (used more than ceil(L/4)); attackers were L2-L4 in 6 of 8 (L20 and L9 in the other two), even against our L44 queen (Slithery r391, id 1478, L3 attacker).
3. The big one: in 6 of the 10 losses their queen died BEFORE ours (r16, r42, r57, r65, r67, r90). A queen alive at r499 would have won every one of those on queen length (dead queen = 0). Our queen was L2-L4 for 100-230 rounds in those games and was hunted down by small dragons. Two more (Maze, Australia) ended with both queens dead and lost on longest dragon.
4. NEW / BUG-like, one game only: Maze 1523623, our queen ate 3 pearls into a 1-wide dead-end row (walls N and S, end wall E) at r96-99, split at r100 with 0 free cells and died on her own tail at r101 (L2). No alarm (1 game), but a split with 0 exits is worth a guard. No standing-still dragons, no illegal actions found. Circling in front of a reachable pearl for 15+ rounds (stuck-opus pattern c) occurs in 8 of 15 games, 25 episodes, only L2-3 dragons, none decisive.
5. r100 (us dragons / total, one15 vs one14 vs one13, same opponent): QoS 16/39 vs 3/6 vs 7/18 (fixed); Australia 31/75 vs 22/54 vs 15/38 (better, still half of theirs 58/141); Trophy 13/31 vs won-early vs 18/43 (theirs 38/93); Trauma 3/10 vs 14/32 vs 5/13: NOT fixed on Trauma, worse than one14 (eats before r100: 7 natural pearls vs their 74; zero eats until r60). Tower Defense and Stripes are 1 dragon / 3 total at r100 in one13, one14 and one15 alike.
Not checked: only one opponent so far (strong, 2264); seats all A. I keep polling for the p1 / s1 / q1 sets and ranked one15 games; second report by 13:30.

---

## 2026-10-09 03:33:34 — New class in 2 games: queen enters cul-de-sac and dies by own move

loss15-sonnet, 12:45 KST. Rule you asked for: same thing in two games now. QUEEN SELF-TRAP, own turn, 0 free cells: (1) Maze 1523623 (test set vs Cache me outside) r96-101: queen L4 ate 3 pearls east along a 1-wide row with walls N and S and an end wall, split at r100, died on her own tail at r101 (f0=0, f1=0). (2) NEW ranked battle 1524544 vs the uncancelables (2162), game Portals 1524545, seat A, r29-31: queen L5 took a portal at r29 from (19,6) into cell (12,3) that has walls on N, S, W and only the portal edge E leading back onto her own body (19,6); r30 she split (5 into 3+2), r31 she died on a wall (reason 0, L3, f0=0, f1=0). Both: queen walks into a cul-de-sac for pearls or a portal, split does not help, next move is lethal. In the Portals game that cost the whole game: they had 3 dragons / 9 total until r125, we had 17 / 48 and eats 183 vs 5 at r100, queen dead r31, and at r499 they won on queen length (their queen 80 vs ours dead) while we held 5 dragons / 52 and top 41. A guard on "do not enter a cell whose other neighbours are all wall / own body / portal back to self" for the queen would have won that game and Maze.
Same battle, other two losses (ranked, bot 21583): Trophy 1524544 (queen L2 rammed r78 by an L3 dragon, 1 free step, in her view; f0=3 then 1 free cell; their queen dead since r20; eliminated r194, behind from r25 on) and Tower Defense 1524548 (2 dragons / 4 total until r50 with 0 eats vs 79 eats of theirs by r100; queen L2 rammed r53 by L3, 2 steps, 1 free, paid; eliminated r183). So the tally is now 13 one15 losses: queen rammed 9, queen self-trap 2 (Maze, Portals), out-eaten with queen alive 1 (Trauma), plus... I will fold everything into losses.md.

---

## 2026-10-09 03:34:32 — Correction: queen self-trap is a known recurring class, plus tally fix

loss15-sonnet, 12:55 KST, correction to my 12:45 message. (1) The queen self-trap (own move, 0 free cells at the start of her last turn, dies on wall / own body / other body) is NOT new: in the qexit-opus rows [M, deduped by game and round] it is 16 of 59 queen deaths in one11, 7/56 in one12, 22/133 in one13, 9/38 in one14 (reasons 0, 1, 2 with f1=0), and many of them are on Portals (unique games: 1496004, 1496711, 1497390, 1497633, 1498750, 1500233, 1501263, 1501678, 1506226, 1507926, 1508919, ...). One15 adds 2 of 11 queen deaths (Maze 1523623, Portals 1524545). Still: it is the class that costs a game outright with no enemy involved, and 1524545 was a game we dominated (16 vs 4 dragons at r100, eats 183 vs 5). (2) Tally fix for all 13 one15 losses: queen rammed 10 (7 from a one-way place, 3 in the open), queen self-trap 2, out-eaten with queen alive 1 (Trauma). Not 9 as I wrote. Updated in losses.md.

---

## 2026-10-09 03:46:52 — loss15-sonnet update: 22 one15 losses now classified, Preyas set in

loss15-sonnet update 12:50 KST (full detail in losses.md). One15 games on disk now 36: c1 vs Cache me outside 5W/10L, p1 vs Preyas 6W/9L (one14 was 4W/11L, one13 4W/11L on p1), ranked vs the uncancelables (b1524544) 2W/3L, tozoman 1W. All 22 losses are seat A. s1 / q1 not on disk yet.
Tally of all 22 losses [M]: queen rammed from a one-way place 7; queen rammed in the open 7; queen boxed in / self-trap 5 (Maze 1523623, Portals 1524545, Portals 1525843, Stripes 1525834, and QoS 1525838 where a foe L2 head closed her last cell at r33); queen split then rammed 1 (Trauma 1525842: at r430 the L19 queen on a 1-free-cell place with two L3 enemy heads 3-4 away split, parent (queen) = 2, child = 17; rammed next round by an L3 unpaid); lost the queen race with the queen alive 2 (Trauma c1 35 vs 39, Slithery p1 14 vs 44).
Queen died in 20 of 22 losses; their queen was already dead when ours died in 8 of them (adds 1524544 Trophy r20 and p1 Australia 1525831 r160 vs ours r171), and died later in 5 more, so 13 games ended with both queens dead. The queen is the whole game: a 3-4 length queen hunted by L2-L4 dragons that pay for extra steps.
Self-trap repeats on Portals: both one15 Portals losses vs Preyas / uncancelables (1524545 r31, 1525843 r288) are a queen that split with f0 = 0 and then died on a wall / own body the next turn. Stripes 1525834 r79 is the same without a split. Not decisive for a rule I can name beyond "queen must not step into a cell with 0 free neighbours beyond where she came from", which I did not test.
r100: Trauma is better vs Preyas (9/22, one14 7/16) but still 3/10 vs Cache me outside (one14 14/32). Trophy vs Preyas 58/135 (one14 2/5): no starvation. Tower Defense and Stripes starve in every version (p1 TD: 1 pearl eaten in the whole game).
No bug (standing still / illegal action / rule backwards) seen in the 22 games. Next report 13:30.

---

## 2026-10-09 04:01:13 — BUG candidate in 2 games: big queen split leaves queen with 2 cells

loss15-sonnet 13:07 KST, BUG-like in TWO games (both Trauma, both lost): the L19-L29 queen splits so that SHE keeps 2 cells and the child gets the rest, with only L2-L3 enemy heads 3-6 cells away.
(1) 1527409 (set one15-s1 vs Team SKKU, seat A): our queen L31 (their queen L4, we led the queen race 31 vs 4). r423 split 31 -> 29 + child 2 (normal tail child), r424 split again: parent (queen) L2, child L27, enemy heads L2 at distance 3, 4, 6. She regrew to 8 and was rammed at r486 (L8, by an L13 at 5 steps, free 4, paid 1, unseen); eliminated r486. Their queen was 26 at the end.
(2) 1525842 (set one15-p1 vs Preyas, seat A): queen L19, r421 split 21 -> 19 + child 2, r430 split 19 -> parent (queen) L2 + child L17, enemy L3 heads at 3, 4, 6; r431 the L2 queen was rammed by an L3 (1 step, free). Lost on queen length (ours dead vs theirs 38).
Scan of all 55 one15 games (script qsplit.py): a queen split that cuts her by 10 or more in one turn happened only in those two (plus the Slithery Fight start, where the queen sheds 25 -> 7 by design, r0-8). Both were losses, none in wins. [M] It looks like the dragon-level split that gives the head side the short part (head-side sacrifice) is being applied to the queen, so the queen score is thrown away while the long body lives on as an ordinary dragon. If a switch controls split position for the queen, "queen keeps the long part" (or no queen split when L>=10 with foes within 6) would have kept a 31 vs 4 queen lead in (1). Only two games, same map; I could not tell from replays which code path chose the cut.
Also new in the s1 set (SKKU, seat A, 6 losses): Portals 1527410 queen died at r10 (L5 split to 3+2, next move hit her own child's tail, f0 = f1 = 0) while we led on total all game; Maze 1527400 queen L2 died r152 colliding with OUR OWN mate's L2 head that had closed her last free cell (f1 = 0), at that point we had 19 dragons / 163 total vs 15 / 59 and their queen lived at 6; Australia 1527398, Slithery 1527411, Stripes 1527401 queen rammed (their queen already dead at r195 and r145 in the first two). Everything is in losses.md; tally update follows in the 13:30 report.

---

## 2026-10-09 04:03:12 — Two corrections to my 13:07 message

loss15-sonnet correction to 13:07: (a) Maze 1527400: the 19 dragons / 163 vs 15 / 59 are the FINAL totals, not r152. At r152 we were 57 dragons / 139 total vs 33 / 77 (still well ahead), her last free cell closed by our own mate dragon 177's L2 head, both died; their queen lived at L2-4 to the end. (b) Portals 1527410: we did NOT lead all game: behind on total to r325 (71 vs 84 at r300), ahead only from r350 (90 vs 59), 60 vs 58 at r499, and lost on queen length because our queen died at r10. Tally now 30 one15 losses (26 wins): rammed from a one-way place 9, rammed in the open 10, queen cut to 2 by her own split then rammed 2 (Trauma 1525842, 1527409), boxed in / self-trap 7, lost queen race alive 2. Queen died in 28 of 30; their queen was already dead when ours died in 10 of them. q1 set and further ranked games still to come.

---

## 2026-10-09 04:21:46 — loss15-sonnet SECOND (final) report: 30 one15 losses classified

loss15-sonnet SECOND REPORT, 13:25 KST. File: ROOT/data/codex/astra/loss15-sonnet/losses.md (5 lines per loss, 30 losses, newest sets first, tally, r100 lines).
Coverage [M]: 56 one15 games (bot 21583) on disk = c1 vs Cache me outside 5W/10L, p1 vs Preyas 6W/9L, s1 vs Team SKKU 9W/6L, ranked b1524544 (the uncancelables) 2W/3L, ranked b1526090 (SKKU, seat B) 3W/2L, tozoman 1W. 26W / 30L. one16 went live after b1526090; there is no one15 q1 set. All losses are seat A except the 2 ranked SKKU ones.
Tally of the 30 losses by class: queen rammed from a one-way place 9; queen rammed in the open (2+ free cells) 10; queen cut to 2 by her own split then rammed 2 (Trauma 1525842, 1527409); queen boxed in / self-trap 7 (Maze 1523623, Portals 1524545, Portals 1525843, Stripes 1525834, Portals 1527410 at r10, Maze 1527400 closed by an own mate's head, QoS 1525838 closed by a foe L2 head); lost the queen race with the queen alive 2 (Trauma 35 vs 39, Slithery 14 vs 44). Queen died in 28 of 30 losses; in 10 of them their queen was already dead when ours died, in 6 more it died later, so 16 games ended with both queens dead and were decided by longest dragon / elimination.
Rammed queens: the attacker paid for extra steps in most cases (all 8 of the first set, 6 of 7 in later sets where the replay record gave it) and was L1-L5 in most; one L34 queen (1526093 r445) and one L44 queen (1523634 r391) fell to L5 / L3 attackers, unseen.
BUG-like (2 games, sent at 13:07): queen split that leaves her 2 cells while the child keeps the rest: 1527409 r424 (L29 -> 2 | 27, we led the queen race 31 vs 4), 1525842 r430 (L19 -> 2 | 17). Both Trauma, both lost, no such cut in any win (scan of 56 games, qsplit.py). Not found in any game: standing still, illegal action, a rule firing backwards other than that.
Games thrown with a big lead because the queen died (all [M]): Maze 1527400 (r152, 57 dragons / 139 vs 33 / 77, died on our own mate's head), Portals 1524545 (r31, 16 vs 4 dragons at r100), Slithery 1526093 (r445, queen L34 vs their 16), Slithery 1523634 (r391, queen L44, their queen dead since r42), Trauma 1527409 (queen 31 vs 4). A rule that says "our queen is the only thing that matters once theirs is dead / she leads" would have changed at least these five.
r100 (us dragons / total, one15; one14 same opponent): QoS fixed vs c1 16/39 (3/6) and p1 10/25 (3/6); Australia c1 31/75 (22/54), p1 30/77 (24/61), s1 46/118; Trophy c1 13/31 (one13 18/43; one14 won early), p1 58/135 (2/5), s1 won; Trauma c1 3/10 (14/32, worse), p1 9/22 (7/16), s1 3/14: Trauma is the one map that still starts with 3 dragons vs three different opponents. Tower Defense and Stripes starve in every version (p1 TD: 1 pearl in the whole game).
Not checked: which code path made the queen cut (replays only); seat B has only 5 games; the one16 games; my pattern-c counts (circling before a reachable pearl, 25 episodes in 8 of the 15 c1 games, L2-3 dragons only) were run on c1 only. Scripts are in the same folder (l15.py, early.py, qtrace.py, qsplit.py, r100.py, selftrap.py).

---

## 2026-10-09 04:22:16 — Correction: paid-step count in final report was wrong

loss15-sonnet correction to the 13:25 report: the sentence "6 of 7 in later sets" paid is wrong. Recounted from the qdeath records [M]: of the 21 rammed queen deaths (8 in c1 + 13 later), the attacker paid for extra steps in 15 and used only free steps in 6 (1524544, 1525830, 1525836, 1525842, 1526090, 1527401). All 8 in c1 were paid; in the later 13, 7 paid and 6 free. Attacker lengths were L1-L5 in most, with exceptions L8 (1525836), L9 (1527411), L13 (1527409), L20 (1523622). Nothing else changes.

---

## 2026-10-09 04:22:16 — closing summary

I classified all 30 one15 losses and sent the lead two reports plus corrections, the second at 13:25. one16 went live after the last one15 ranked battle and no one15 q1 set exists, so I stopped there.

**Coverage.** There are 56 one15 games (bot 21583) on disk, 26 wins and 30 losses. All losses are seat A except the 2 ranked SKKU games. The ranked battles you named (1522311, 1522401, 1522569, 1522426) are one14 (bot 21497).

**Tally of the 30 losses by class:**
- queen rammed in the open: 10
- queen rammed from a one-way place: 9
- queen boxed in or self-trapped: 7
- queen cut to 2 by her own split, then rammed: 2
- lost the queen race with the queen alive: 2

**Findings:**
- **Queen death is the whole game.** The queen died in 28 of 30 losses, and 16 of them ended with both queens dead. In 10 of those, their queen was already dead when ours died, so a surviving queen would have won on queen length.
- **BUG-like, 2 games (both Trauma, both lost).**
  - What happened: the queen splits so she keeps 2 cells and the child keeps the rest (1527409 r424: 29 to 2 and 27; 1525842 r430: 19 to 2 and 17). In 1527409 we led the queen race 31 to 4.
  - How sure: no such cut appears in any win. I could not tell from replays which code path chose it.
- **Self-trap is a known class, not new.** It appears in earlier versions too (9 of 38 queen deaths in one14).
- **Not found:** no standing-still dragons, no illegal actions, no rule firing backwards (other than the queen cut above).

**First 100 rounds on the four maps** (our dragons / total length at r100):

| Map | one15 | Verdict |
|---|---|---|
| Queen Of Spades | 16/39 and 10/25 | fixed |
| Trophy | 13/31 vs Cache me outside, 58/135 vs Preyas | not starving |
| Australia | 30/77 to 46/118 | better, but behind in 2 of 3 sets |
| Trauma | 3/10 vs Cache me outside, 9/22 vs Preyas, 3/14 vs SKKU | the one map that still starts with 3 dragons |

Tower Defense and Stripes starve in every version (one Preyas Tower Defense game ate 1 pearl all game).

**Not checked:** the one16 games, and which code path made the queen cut. I counted circling in front of a reachable pearl only in the Cache me outside set (25 episodes, L2-3 dragons only).

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/loss15-sonnet/`:
- `losses.md`
- `l15.py`
- `early.py`
- `qtrace.py`
- `qsplit.py`
- `r100.py`
- `selftrap.py`

---

## 2026-10-09 04:25:02 — one16 vs one15: queen portal steps, r100, death, Portals and Stripes

loss15-sonnet, answer (1), all [M] from replays, bot ids checked (21651 and 21583). "Portal step" = a head move between cells that are not torus-adjacent. Same opponent (Cache me outside), seat A.
PORTALS
- one16 1528867 (WIN): queen portal steps r0-99: NONE. Her death: r193, L3, own move onto her own body (reason 1), split the turn before (split0 = 1), f0 = 0, f1 = 0 (no free cell at her last two turn starts), i.e. the self-trap class again, 93 rounds after r100. r100: 22 dragons / 59 total, 110 natural pearls eaten (r<100); them 29 / 63.
- one15 1523633 (WIN): queen portal steps at r4, r8, r64, r70 (4). Her death: r212, L2, wall (reason 0) on her own move, split0 = 1, f0 = 0, f1 = 0 (same self-trap). r100: 16 dragons / 44 total, 117 natural pearls; them 29 / 69.
STRIPES
- one16 1528858 (LOSS): queen portal steps at r9 and r13 (2): she STILL takes a portal inside r0-10 (r9), and again at r13. Her death: r87, L2, rammed by dragon 58 (L2, 1 step, free, unpaid), in her view and a mate's; f0 = 1, f1 = 1, f1a = 0 (she was on a 1-free cell and moved to a 0-free cell). Their queen was already dead (r13). r100: 7 dragons / 16 total, 36 natural pearls; them 8 / 21 (59 natural pearls).
- one15 1523624 (LOSS): queen portal steps at r38, r43 (2). Her death: r47, L3, rammed by dragon 20 (L2, 2 steps, free 1, paid), f0 = 1, f1 = 1, f1a = 2. Their queen dead at r16. r100: 1 dragon / 3 total, 17 natural pearls; them 18 / 44.
Reading: Portals: the r0-10 queen step is gone (first step in one15 was r4); she takes none in r0-99; the side does not starve (22 / 59 vs 16 / 44). Stripes: the switch did NOT remove her r9 step (it may count as "seen far side", I cannot tell from the replay); but the Stripes start is much better than one15 (7 / 16 vs 1 / 3, and level with them 8 / 21), so she is not sitting and starving there. Both queens still die by the usual classes (self-trap Portals, rammed from a 1-free cell Stripes). The 12-loss class list follows in a few minutes.

---

## 2026-10-09 04:26:51 — one16-c1: 12 losses by class, one line each, plus what is new

loss15-sonnet, answer (2): the 12 one16 (21651) losses, set one16-c1 vs Cache me outside, all seat A, all [M]. Full lines in losses.md (top section).
1528859 Tower Defense: starved (r100 1 dragon / 3 total, 1 natural pearl), queen L2 rammed r129 by L3 (2 steps, paid) from a 1-free cell. Out-eaten + rammed from a one-way place.
1528863 Schooltime: no queen death (both queens L3, both top dragons 74); lost on total 238 vs 281; out-eaten from r50 (r100 26 / 70 vs 63 / 173).
1528855 Australia: queen L4 rammed r280 by L4 (3 steps, free 1, paid), unseen, open ground; their queen dead since r172; out-eaten from r100 (25 / 57 vs 61 / 149). Rammed in the open.
1528854 weakhold: SELF-TRAP r129 (queen L2 on a wall, split the turn before, f0 = f1 = 0) in a game we dominated (r100 16 / 38 vs 11 / 26, they had 4 total by r300; ended 75 vs 4 and lost on queen length). Thrown game.
1528858 Stripes: queen L2 rammed r87 by L2 (1 step, free) from a 1-free cell; their queen dead since r13; level at r100 (7 / 16 vs 8 / 21), then 1 vs 26 at r200. Rammed from a one-way place.
1528865 Devil: queen L3 rammed r134 by L3 (2 steps, paid) from a 1-free cell; their queen dead since r76; behind from r50 (19 vs 40). Rammed from a one-way place.
1528864 Trophy: queen L4 alone (no mate within 4) among 6 enemy heads within 6 for 12 rounds, split 4 to 2 + 2 at r48, rammed the same round by L3 (2 steps, paid). Rammed in the open, no escort.
1528868 Slithery Fight: queen L19 cut to 2 at r363 with a foe L56 head at distance 3, rammed r476 as L2 by L4 (2 steps, paid); their queen dead since r26; lost on longest 66 vs 91. Cut then rammed.
1528866 Trauma: starved start (7 / 17 vs 25 / 63); queen grew to L33, rammed r390 by L3 (1 step, free) from a 1-free cell; their queen 48 alive. Rammed from a one-way place.
1528861 Default: queen L3 rammed r128 by L3 (3 steps, paid), unseen, open; their queen dead since r66; behind from r50. Rammed in the open.
1528857 Maze: SELF-TRAP r144 (queen L2 onto her own tail, split the turn before, f0 = f1 = 0); 191 vs 93 total at r200, ended 152 vs 94 and lost on queen length (theirs 66). Thrown game.
1528860 Around UNSW: queen L4 rammed r168 by L5 (3 steps, free 2, paid), unseen, open; both queens dead; lost the longest dragon 41 vs 42.
Tally: rammed from a one-way place 4, rammed in the open 4, self-trap 2, cut to 2 then rammed 1, no queen death 1. Queen died in 11 of 12; their queen was already dead when ours died in 5.
New vs one15? Nothing new in kind. Still present: the queen cut to 2 (1528868, the 3rd game after 1525842 and 1527409, here with an L56 enemy head at distance 3), self-trap after a split (2 games that were big leads), Tower Defense starve identical to one15 (1 / 3). Gone: the Portals start collapse (22 / 59 at r100 vs one15 16 / 44). Caveat: Stripes queen still takes portal steps at r9 and r13.
