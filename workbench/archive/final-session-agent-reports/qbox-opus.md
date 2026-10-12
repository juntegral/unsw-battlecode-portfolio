# Reports sent to the lead by qbox-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 03:13:52 — qbox heads-up: cause of Portals queen deaths

qbox heads-up, cause found: on Portals the queen is NOT boxed in at her start (room 39+ cells); she walks THROUGH a portal into a closed pearl room (2x2 room with pearls, or a 1-cell pocket) whose only way out is a portal, eats, grows/splits, and the way-out portal lands on her own neck or on her own child sitting at the mouth. [M] 28/30 online deaths: last turn in a cell with 0 non-portal room and 1 portal side (1504492 r4 steps S-portal (3,6)->(27,9), dead r9; 1516204 r4 N-portal (28,9)->(4,6), dead r10); local same in 8/8 mTd0/mNps Portals games (e.g. lc_mTd0 seed1 side0 r31 W-portal (19,6)->(12,3), dead r33).
[C] Why she may: is_queen() main.cpp:5679 needs cells > QUEEN_MIN_CELLS(600) and Portals is 512, so queen_portal_ban() :6066 is false and score_portal_step :7887 does not shut the portal; entry_portal_dead :4827 excludes the real queen, so the dead-end portal keeps its plain pearl score. Base behaviour, not a live switch. Candidate one-constant fix QUEEN_PORTAL_ALL:true (existing, real queen portal ban on every board size) is being built and tested now, plus a narrower new switch (queen takes a portal only into known room); verdict by 12:55.

---

## 2026-10-09 03:26:32 — qbox: QUEEN_PORTAL_ALL:true keeps queen alive on Portals

qbox interim (12:28): one existing constant QUEEN_PORTAL_ALL:true (no new code; one15 + this = bot solo/bots/qbPA) stops it locally. Portals seed 1, both seats, vs m3base and mD15: queen alive at r500 in 3 of 4 games (L36, L33, L27; 3 wins "longer queen", 4/4 wins) against 0 of 3 alive with one15 (dead r33, r33, r76; 0/3 wins). Pearls by r100 175 vs 185 (vs m3base, -5%), dragons at r100 14.5 vs 14.5.
Why this constant: the queen's portal ban already exists but is_queen() only holds above 600 cells (QUEEN_MIN_CELLS) or in a closed home; Portals is 512 and Stripes 288, the only two ladder maps with portals at or under 600 cells. QUEEN_PORTAL_ALL extends ban + no blind portal scouting + no survey through portals to the real queen on every size; on maps over 600 cells or without portals it should change nothing (identity games running now). My own narrower switch (QUEEN_ROOM_KEEP) only delayed the deaths (r92-r473), not recommended. The one PA death (r45): child's body pinned her only exit, then the emergency portal took her into a 1-cell pocket. Stripes, islands, 8 no-portal identity pairs and seed 2 are playing; final by 12:55.

---

## 2026-10-09 03:29:32 — qbox correction: do not ship QUEEN_PORTAL_ALL yet

qbox CORRECTION to my 12:26 interim: do NOT put QUEEN_PORTAL_ALL:true live on that message. It fixes Portals but on ladder_stripes_1 (288 cells, the other small ladder map with portals) vs m3base seed 1 it cut our pearls by r100 from 54.0 to 32.5 (-40%) and dragons at r100 from 9.5 to 4.5, and seat 1 went from a win to a loss by elimination (queen rammed r41 with 2 units). n=2 games, but it fails the 10 percent rule. Cause as I read it [E]: on Stripes the early pearls sit in rooms behind portals and the queen is the one who opens them (one15 queen steps into a 4-cell room at r9 in both games and it pays).
Also new [M]: every local one15 queen death on Portals (r33, r33, r42, r76) is a step into a 1-CELL walled pocket whose only side is the portal she came through, i.e. certain death at length 2+; online 12 of 30 are 1-cell pockets, 14 of 30 are 4-cell rooms. Now testing a narrow switch QUEEN_ROOM_KEEP:2 (queen refuses a portal only into a known 1-cell pocket) and :5 (also 2x2 rooms) on Portals and Stripes; result by 12:50.

---

## 2026-10-09 03:42:44 — qbox: exact cause is queen blind portal scouting; narrow switch built

qbox 12:43: exact decision found and a narrow switch is built: the queen is used as a BLIND PORTAL SCOUT on maps of 600 cells or fewer. New switch QUEEN_NO_BLIND_PORTAL (bool, off by default, 3 guarded lines; source ~/meow-redteam/solo/src/w-qbox/main.cpp, diff in ROOT/data/codex/astra/qbox-opus/qbox-opus.diff, bot solo/bots/qbNB = one15 + QUEEN_NO_BLIND_PORTAL:true). All-off hash 92fb69564fbd OK; one15 values give the mD15 binary bit for bit (1537f0dc).
[C] base main.cpp:6060 can_scout_portals() lets the queen scout unless is_queen(), and is_queen() :5679 is false at cells <= QUEEN_MIN_CELLS 600; then :8078 marks a portal with unknown exit as blind and :8239 scores it best_base + scout bonus, so she steps through without knowing the other side. Base behaviour, not a live switch.
[M] Portals seed 1, 4 games (2 seats x m3base, mD15): one15 queen dead r33, r33, r76, r42 (3 portal steps a game: r4 blind into the 2x2 pearl room, then a 1-cell pocket), 1 win of 4. With the switch: dead r115, r92, r473 and alive (L5), 3 wins of 4, the r4 step is gone in all 4. On Stripes (2 games), gx_islands_24x12 (2), Devil, Tower Defense, Weakhold the switch plays the SAME GAME as one15 event for event (7 of 7), so the Stripes loss that QUEEN_PORTAL_ALL caused does not happen.
Two things against it: pearls by r100 on Portals 170 vs 185 against m3base (-8%) and 170 vs 205 against mD15 (-17%, over your 10 percent line), dragons at r100 level (15 vs 15); and she still dies in 3 of 4, later, by a different path (boxed by own body + a mate beside a portal, then the no-move emergency at :1858 takes the known portal into a 1-cell pocket). Rest of the no-portal identity pairs are playing; final at 12:55.

---

## 2026-10-09 03:48:19 — qbox final report: queen blind portal scouting, switch QUEEN_NO_BLIND_PORTAL

qbox FINAL (12:48). Found: on Portals the queen is not boxed in at her start; she is used as a blind portal scout and steps through portals into closed pearl rooms. Built QUEEN_NO_BLIND_PORTAL (bool, off by default, 1 constant + 3 guarded lines).
Ready to go live: NOT by your rule as written. Hash, identity, no new early deaths and the mechanism all pass, but pearls by r100 on Portals are down 15 to 17 percent (your line is 10). Value if you take it: QUEEN_NO_BLIND_PORTAL:true.
How sure: cause high (code + 30 online + 15 local games agree); benefit medium (15 Portals games, one map).

CAUSE [C], base behaviour, no live switch involved (lines in src/solo/main.cpp):
- :5679 is_queen() needs cells > QUEEN_MIN_CELLS (600, :206) or a closed home. Portals is 512, Stripes 288: the only two ladder maps with portals at or under 600.
- :6060 can_scout_portals() therefore lets the real queen scout; :8078 marks a portal with unknown exit blind; :8239 scores it best_base + scout bonus. She steps through not knowing the far side.
- The condition that should have stopped it is the queen's portal ban (:6066, :7887), which never applies at this size.
[M] online, 30 Portals deaths: in 26 her last portal step was 1 to 6 rounds before death, into a walled room of 1 cell (12) or 4 cells (14). The six r9/r10 deaths all start with a portal step at r4 into the 2x2 pearl room (1504492: (3,6) S-portal to (27,9), eats to L4, room full, way out lands on her own child at (3,7)). Drawings: on-1504492.txt, on-1516204.txt, on-all-brief.txt.
Reproducing local game: mD15 vs m3base, ladder_portals_1, seed 1, seat 0: r4 into the 2x2 room, r31 W-portal (19,6) to (12,3) (1-cell pocket), dead r33 on her own neck.

HASH: all-off 92fb69564fbd OK. one15 values = mD15 binary bit for bit (1537f0dc), so replay identity holds by construction. (cmp on replays is not usable across bot folders: the replay stores the bot path; I compared event streams, same.py.)

PORTALS, one15 vs switch, seeds 1-2, both seats (one off game vs mD15 missing: 7 vs 8 games):
                    one15          switch
queen dead <= r100  6 of 7         1 of 8
queen alive r500    0 of 7         2 of 8
death rounds        33 33 42 64    92 115 187 271
                    72 76 229      436 473
portal steps/queen  23 (r4 in 7/7) 3 (r4 in 0/8)
wins                2 of 7         5 of 8
pearls<=r100 v m3b  204.0          173.0  (-15%)
pearls<=r100 v mD15 209.0 (n=3)    175.7 same 3 (-16%)
dragons@r100        16.5 / 17.0    17.0 / 15.7

OTHER MAPS, vs m3base seed 1: SAME GAME as one15 event for event in 13 of 13: Stripes x2, gx_islands_24x12 x2, Queen of Spades, and 8 without portals (Devil, Tower Defense, Weakhold, gx open, corridors, rooms, ring, rich). So pearls and dragons are unchanged there by identity.

What is left: she still dies in 6 of 8 on Portals, later. Three by the no-move emergency at :1858 (boxed by own body + a mate beside a portal, takes the known portal into a 1-cell pocket), three boxed with no portal at all (wall r271, r436; mate head r187). That part is your original mate-boxing idea and is not fixed.
Tried and rejected: QUEEN_PORTAL_ALL:true (queen alive 3 of 4 on Portals, islands pearls 75 to 106, but Stripes pearls 54 to 32.5 and a loss by elimination); a known-small-room veto (never fires: she does not know the far side, games identical to one15).

Not checked: seed 2 off the Portals map, Trauma, online play, more than 15 Portals games; win counts here are far below 40 games. ladder_portals_1 may have estimated pearl supply, so the pearl drop is arm against arm only.
Wrong if: online Portals games with the switch still show a queen portal step at r4, or queen deaths at or before r50 do not fall, or Stripes pearls by r100 move at all.

Files: source ~/meow-redteam/solo/src/w-qbox/main.cpp; diff ROOT/data/codex/astra/qbox-opus/qbox-opus.diff (20 lines); bot solo/bots/qbNBf (same binary as qbNB used in all games, e05a74e6); table.txt, psteps.txt, same.txt in my folder; runs solo/runs/qb_off_*, qb_nb_*, qb_pa_*.
One process note: my first runner's throttle failed and about 57 games ran at once for roughly 30 seconds at 12:16; I stopped them and replayed those games. No other agent's process was touched.
