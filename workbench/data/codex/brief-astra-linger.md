# Astra analyst: linger

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `linger`.

Question: after a dragon of ours eats, does it stay where the pearl comes back? The earlier analyst measured that a pearl goes to
the side whose head is nearer when it is born (82-98%) and that pearls come back on the tile just eaten (45% of births on small maps,
62-67% on big; commonest gap 4 rounds, median 7), and that dev test 1 has a head within 3 steps when a tile it ate from bears again
in 43-61% of cases (WHQ 29-45%). Ours was not measured.
1. Measure it for ours, WHQ and dev test 1 on the same games, by round band (r0-50, r51-150, r151-300) and map size: when a tile a
   side ate from bears again, was a head of that side within 1 / 3 steps, and who ate the new pearl.
2. What do our dragons do in the 8 rounds after a meal (distance from the tile each round; split; walk on toward unseen ground)?
   Which score terms move it away (the never-seen-tile bonus, territory, SPAWN_CLEAR, which keeps a dragon OFF a tile whose countdown
   is low: check that SPAWN_CLEAR steps beside the tile and comes back, and how often the pearl is then eaten by us)?
3. The card, if the numbers support it: a rule that keeps the dragon that just ate within reach of that tile until it bears again
   or N rounds pass, without stopping exploration by the rest of the swarm. Say what it costs (pearls elsewhere not found).
