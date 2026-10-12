# Astra analyst: queenfeed

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `queenfeed`.

Question: against WeHaveQuizzes the label reports (`data/analysis/ladder/dossier/online/label-one5-w1-old.md` and its `.json`)
show three numbers that moved between one3 and one4 and stayed moved in one5, although one5 took the queen's early split back out:
queen pearls per game 16.3 (one2), 16.9 (one3), 6.1 (one4), 7.3 (one5); FEEDER_EAT events 144, 141, 89, 81; queen turns in r51-300
with no mate within 5 tiles 26%, 12%, 37%, 37%; pearls eaten by r300 517, 533, 454, 450. The source difference one3 to one5 is only
HEADING_TIE 1.5 for rounds 0-11 (non-queen, short dragons keep their heading on ties) and EAT_FIRST (`diff data/online/smoke/one3-bot/main.cpp
data/online/smoke/one5-bot/main.cpp`, 50 lines). one4 = one3 + HEADING_TIE + QS_KEEP_ROUND 20.
1. Is it real or three or four games? Give the per-game queen pearls, queen death round and FEEDER_EAT count for the four sets,
   by map (same 15 maps in each). Say how many maps moved the same way in both one4 and one5.
2. If real: where does it start? Queen position relative to mates and to pearl tiles at r12, r30, r60, r100 in one3 against one5 on
   the same maps (distance to nearest mate head, mates within 5, pearls eaten by the queen by then, her length). Does the swarm
   leave her behind in rounds 0-11 (the heading rule), or does EAT_FIRST let mates take the pearls she used to eat?
3. The same three numbers in the dev test 1 sets (one1, one3 against one4, one5) as a second sample.
4. A card only if the cause is in our code: the smallest rule that gives the queen her meals and company back without undoing
   the early pearl gain (one5 is level with WHQ at r100 for the first time: 27.2 dragons / 67.9 length against 26.5 / 70.7).
