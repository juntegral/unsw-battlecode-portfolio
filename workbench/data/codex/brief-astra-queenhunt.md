# Astra analyst: queenhunt

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `queenhunt`.

Question: should we hunt their queen. In all 27 losses that ended with their queen alive and ours dead, no short dragon of ours ever
had her head in reach; where one did (47 turns in 96 games) it rammed on 42. The source has a switch that sends hunters: QUEEN_HUNT
(off; with QUEEN_CHASE_DIST 8 it is the local opponent `m3hunt`, which kills our queen in nearly every local game by r25-r100).
1. Online, one1 to one5: for each game, the distance (steps) from their queen to our nearest dragon of 2-4 every 10 rounds, and how
   their queen lives: mates within 5 tiles of her, her length, where she is (home / in the swarm / front). When our queen dies to a
   ram, was the rammer a hunter (did it walk at her for several turns from far) or a passer-by? How many of their dragons hunt.
2. The code of QUEEN_HUNT, QUEEN_CHASE_DIST, QUEEN_HUNT_STEPS, QUEEN_HUNT_MAX_LEN, QUEEN_CHASE_FRESH: who becomes a hunter, how it
   learns where their queen is, what it gives up. What it would cost: hunters are dragons not eating.
3. Local evidence already on disk: games of our arms against `m3hunt` (for example `mDo5_vh`, `m8o2_vh`, `m9f3_vh`): in how many does
   m3hunt kill our queen, by which round, how many hunters it spends, and its dragon count against ours at r100. That is the price list.
4. A local test is being played now: arm `mDqh_vb` (one5 + QUEEN_HUNT true + QUEEN_CHASE_DIST 8) and `mDl5_vb` (one5) against plain
   main, in `~/meow-redteam/solo/runs/`; when the games are there, count their queen's death round, how each game was decided, our
   dragons and total at r100 and r300, arm against one5.
5. Verdict: put queen hunting in the next live version or not, with which values, and what to watch online.
