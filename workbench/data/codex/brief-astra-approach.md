# Astra analyst: approach

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `approach`.

Question: pearls we see and do not go for. A fix that went live at 00:49 (EAT_FIRST) makes a dragon take a pearl ONE step away when a
mate is nearer to the ground beyond it. Left open by its builder: (a) a pearl TWO steps away is walked away from on 15.9% of such turns
on big maps (18.6% before the fix), cause not traced; (b) of the pearls one step away still not taken (11%), most are the dead-end
test (10 points) and splitting instead (5 points), and nobody checked whether those dead ends are real traps.
1. On the one4 and one5 games and on the local arm `mDo5_vh` (= one5) count, for non-queen dragons: turns with a pearl two free steps
   away and no enemy head within 4 steps: took a step toward it / away / sideways / split; by mate in view or not.
2. For the "away" turns, name the score term from the code (score_step and what it calls): territory handed to a mate, the pocket or
   dead-end test, zone rules (leader zone, ZONE_NEARER), crowd load, SPAWN_CLEAR. The builder's notes: `~/meow-redteam/solo/src/w-eat/`
   (diff, counts.txt) and `data/analysis/ladder/dossier/diag-one1.md` sections 9-10.
3. For pearls one step away refused by the dead-end test: was the tile a real trap (after eating, no way out for the body within its
   length + 2 tiles), from the replay geometry? Share of real traps.
4. Card(s): the smallest change that takes the pearls that were safe to take.
