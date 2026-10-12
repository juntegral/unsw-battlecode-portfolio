# Cards so far (kept by the lead; read before proposing a card)

Live versions and their switch sets: `docs/SESSION-STATE.md`, grep "라이브 = one". Bot sources: `data/online/smoke/one<N>-bot/main.cpp`.
A card already listed here is only worth repeating if you show that the shipped fix did NOT prevent the case in a game played
by a bot that had it: then say so in one line ("fix X was live and failed because ...").

## Live at the deadline (one21, submission 21857, since 14:49 KST) = one19 + two completions (one20) + QS_LONG_WAIT true
## Before that: one19 (submission 21827, since 14:36 KST) = one18 - QUEEN_DEAD_ALL + CENTER_MAX_CELLS 100000 + QUEEN_NO_RAM + QUEEN_BLIND_STALL 20
## Before that: one18 (submission 21761, 14:10 to 14:36 KST) = one17 + QUEEN_CORRIDOR_MATE true
(the queen's corridor guard no longer keeps a fatal step into a pocket because a mate's body stands in her other way.)
## Before that: one17 (submission 21693, 13:31 to 14:10 KST) = one16 + QS_SHED_MAX 9
(a queen of 10 or longer no longer splits down to 2 when exposed with no escape: 21 such splits in 474 games, 18 lost.)
## Before that: one16 (submission 21651, 12:51 to 13:31 KST) = one15 + QUEEN_NO_BLIND_PORTAL true
(on maps of 600 cells or fewer the real queen no longer takes a portal with an unseen far side; on Portals she died boxed in 30 of 30 games.)
## Before that: one15 (submission 21583, 11:44 to 12:51 KST) = one14 with TERRITORY_DECAY 0
(TERRITORY_DECAY 16 left our side at 2-3 dragons for 100 rounds on Queen Of Spades; dropped. Read every mention below as OFF.
Also dropped after a local head to head: THREAT_HIDDEN_PARTS 8, long dragons turn timid and lose the longest-dragon decision.)
## Before that: one14 (submission 21497, 10:24 to 11:44 KST) = one13 with PORTAL_SCOUT_MIN_LEN 0
(PORTAL_SCOUT_MIN_LEN 4 kept the whole side out of unseen portals: our pearls by r100 on Portals fell 238 to 71, Trauma 41 to 4,
Australia 92 to 36. Dropped. Read every mention of it below as OFF.)
## Before that: one13 (submission 21377, 08:07 to 10:24 KST) = one12 with QS_KEEP_MIN_UNITS 2 instead of 6
(one13 beat one12 29-2-17 in 48 local head-to-head games; with 6 the queen was 2 long in 31% of her first 100 rounds.)
Below: the switch list of one12, which one13 shares except for that constant.
Everything of one11 (EAT_FIRST; HEADING_TIE r0-11; FEED_CAP_ROUND 350; QUEEN_HERD; QUEEN_DEFEND_STEPS 3; QUEEN_DEAD_ALL;
QUEEN_EXIT_KEEP; QUEEN_AVENGE 8 (never arms); PORTAL_ID_GUARD; SMALL_SPRINT_THREAT; MATE_UNPIN; POCKET_KEEP_OUT; TARGET_REACHABLE;
QS_KEEP_MIN_UNITS 6; SPLIT_PORTAL_OK; REACH_EATS; QUEEN_SURE_LEN 64 / STEPS 5; CUT_BODY_LEN 4 / QS_PAY_REACH 4 / CUT_BODY_STRIDE;
QUEEN_BOOT_LEN 6; QUEEN_PORTAL_LAST; QUEEN_EXIT_STRICT) plus, new in one12: BIG_ESCAPE_STEPS 6 / BIG_ESCAPE_MIN_LENGTH 8 (long
dragons step out of reach of short enemies); TERRITORY_DECAY 16 (near ground weighs more than far ground); QUEEN_FAR_HEADS 2
(the queen's rings use enemy heads her mates saw in the last 2 rounds); QUEEN_CORRIDOR_GUARD 6 (she refuses a visible dead-end
corridor when she has another move); PORTAL_SCOUT_MIN_LEN 4 (a non-queen under 4 does not enter an unseen portal when an
ordinary way with a visible exit is open).
How versions are judged now: a 15-game online set cannot separate two versions (the same bot scored 8 and then 4 of 15 against
the same unchanged opponent). Versions are compared by local head-to-head on new maps (48 or more games) and by 45 or more
online games each. Local head-to-head: one12 beats one11 40-3-29; one11 v one8 17-2-29; one11 v one5 21-2-24; one8 v one5 20-2-26.
The main finding on losses (95 local games): we kill their queen first in 27 of 47 games and win only 12 of them, because our
own queen then dies short: after their queen is dead ours dies 2.61 times per 100 rounds at length 2, 0.87 at 3, 0.08 at 4+.

## Being built or waiting (do not re-propose; do report games they would not have covered)
QUEEN_HOLD_LEN (built; 46-4-46 against one12 in 96 local games, no effect: the "their queen is dead" signal rarely reaches our dragons); QUEEN_WAR (built, held back);
QUEEN_EDGE_REACH (built, not live). A teammate's idea, feeding and leader growth from round 200, is losing its local
head-to-head so far (5-13 and 5-11). Open: the first-100-round pearl gap (half of it is corpse pearls the opponents re-eat and
we do not); a mate longer than 3 closing the queen's exit; the queen closing her own exit by a split.

## Tried and dropped (do not re-propose without new evidence)
Always-on queen hunt (QUEEN_HUNT); early queen split by round (QS_KEEP_ROUND); EAT_BONUS; wide queen defence radius; QUEEN_ESCORT;
HERD_BEHIND; unconditional rams; QUEEN_FALLBACK and LONG_SAFETY (teammate's cards, worse online); two-step pearl EAT_FIRST_TWO;
RALLY_END_FRESH 25 (gave up 26 length for 6 on the longest); staying beside an eaten tile (linger); banning even trades.

## Known open causes without a fix yet
Our queen stays about 3 long while a surviving enemy queen grows (we lose "both alive" games on queen length); a long dragon with
an unseen tail cannot escape-split before it is rammed; the mid-game eating gap (4.1-4.4 natural pearls per 100 turns for the
top teams against our 3.5-4.1); late longest-dragon decisions on big maps.
