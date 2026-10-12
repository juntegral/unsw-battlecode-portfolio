# Reports sent to the lead by qcut-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:42:38 — qcut heads-up: code path and mismatch

qcut heads-up (13:43): the 19->17->15->13 on Slithery seed1 seat1 r344-346 is the queen_wait split in act (`if (queen_wait()) ... split_off(MIN_SIZE)`, base line ~1854) [M, file-logged debug build]. But at those turns she is NOT boxed: head (18,5), N and E cells are free (enter_time 0), S is her own segment 3, W is her neck; she waits because the pocket is "cramped" (room < length+2). So Zhe's rule as written would not help there: the only own-body blocker is segment 3 (cut = queen of 3), and with your 2-turn bound it does not fire at all.
Where the rule does fire: the opening on Slithery (queen 25 coiled, all 4 sides her own segments 1/3/5/7, same queen_wait site, sheds 2 a turn for 9 turns, units 7) - so value 1 rewrites the opening (single games: bound-2 version queen dead r75; unbounded version cuts 18 at r0 and she ends alive at 80, wins on queen); value 60 leaves the opening alone. Switch QUEEN_CUT_BLOCK is built (all-off 92fb69564fbd OK, one17 values = d6d14e1f8f53 byte-identical to mD17); I added a tuning constant QUEEN_CUT_TURNS (2 = your bound, 99 = Zhe's literal rule). Now running the pairs at 60 for both to count how often the boxed-by-own-body case occurs at all.
