# Astra analyst: evade

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `evade`.

Question: analyst `smallmap` (`data/codex/astra/smallmap/report.md`, `collisions.csv`) found that opponents ram us when they are ahead
on the board (they take 49.5% of their chances when ahead, 25% when behind) and then eat what drops with a head that is already
near (of 930 dropped pearls nearer to them they ate 594). On small maps in r0-150 they started 321 rams on us while we were
outnumbered: we lost 838 length, they lost 864 and ate 542 back. Could our dragons have stepped out of the way?
1. For every ram on a non-queen dragon of ours in r0-200 (one5-w1, one5-c1; one3-w1 as a check): on our last turn before it, was the
   attacking head in our 7 by 7 view, how many steps away, how long was each, and was there a free step that would have put our head
   out of its reach next round (its free steps = ceil(L/4), plus paid sprint if it had the length) without entering a dead end?
   Share avoidable / not avoidable / not seen. Same for the opponents when we ram them, as the baseline.
2. What does our bot do on that turn and why: read `threat_at`, `risk_at`, `enemy_can_step_to` and the trade rules in
   `data/online/smoke/one5-bot/main.cpp` and say which term let the dragon stay in reach (a pearl, territory, a trade it expected).
3. After an avoidable ram: who eats the drop, and what did our dragon gain in the two turns before (pearls)?
4. One card at most: a general rule for a short dragon that is outnumbered locally (heads in view) to keep out of reach of an
   equal or longer enemy head unless a mate is nearer to the meeting cell. Name the lines, whether a switch already does part of it,
   the count that shows it works, and what it costs (pearls not eaten on those turns).
