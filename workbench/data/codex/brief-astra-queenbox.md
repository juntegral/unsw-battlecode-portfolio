# Astra analyst: queenbox

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `queenbox`.

Question: our queen dies boxed in (walls, bodies) about as often as she is rammed: against WHQ 6 of 15 (one2), 6 (one3), 5 (one4).
1. Every boxed-in queen death in one1 to one5 (all opponents, ranked too): round, her length, map cells, the tiles round her head on
   her last three turns, whether an enemy head was within 6 tiles (pushed) or not (walked in), whether a mate's body or her own
   child from a split closed the exit, and whether she could have left earlier (the turn on which her last exit closed).
2. The code: her dead-end terms (QUEEN_DEAD_END, QUEEN_ROOM, QUEEN_DEAD_PENALTY, `dead_queen()`), the board-size gate (QUEEN_MIN_CELLS
   600 and the switch QUEEN_DEAD_ALL, which applies the dead-end rule on every board size and is OFF), QUEEN_WAIT (she splits to wait),
   QUEEN_HERD (new: she walks toward mates; does it walk her into crowded pockets?), EAT_FIRST (applies to her).
3. For each death: would QUEEN_DEAD_ALL true have vetoed the step that closed her in? Would any existing term?
4. Card: QUEEN_DEAD_ALL true if it reaches them, or the rule that does. Count how many of the deaths it reaches and what it costs
   (her pearls: she must still eat).
