# Codex brief: the mechanics of the queen rules, worked out from the rules (offline, no games)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read carefully:
- `rules/movement.md`, `execution-order.md`, `splitting.md`, `death.md`, `structure.md`, `vision.md`, `sonar.md`;
- `rules/ALL.md` for anything referenced from them.

The current rules (unswbc 1.2.3):
- the longer queen (lowest id: 0 or 1) wins at r500, and a dead queen counts 0;
- the first ceil(L/4) steps per turn are free;
- dragons act in ascending id order, so both queens act first in every round.

## Why
We need exact, rule-derived facts for designing queen safety, assassination, feeding and splitting. These will also go into an idea book for a possible new team. Derive each fact from the rule text, and check it with small simulations written against the rules.

## Questions
1. **Reach tables.** For a dragon of length L (2–40), list:
   - free steps;
   - the maximum steps it can take in one turn when paying (cost per step beyond the free ones, and the minimum length it must keep);
   - the set of tiles reachable by its head in one turn on an open board.

   Then, for our queen (who moves first) and an enemy of length L that moves after her in the same round: what is the minimum head-to-head distance at the end of her move that guarantees no head-to-head that round? Also give the distance for two rounds ahead.
2. **Who keeps the id on a split.** Which part keeps the id (and therefore the queen title)? Where is the child born and which way does it face? What are the consequences: when can the queen safely make workers, and why does an escape split in a dead end leave her as the stub?
3. **Drops and feeding.**
   - Drops are ⌈L/2⌉ pearls on every second segment from the head. Give the efficiency by donor length (L3 drops 2 = 67%, …).
   - Where do the drops land relative to the queen's path, depending on how the donor dies?
   - What is the best way for a feeder to die so the queen collects most of the drops (approach geometry, timing)?
   - What does the queen gain per round from a stream of L3 feeders?
4. **Safe circulation (vault and coil).**
   - A dragon must act every turn, and moving into its own tail tile is death ("including its tail").
   - What is the minimal cycle on which a queen of length L can circulate forever?
   - Which room shapes let her circulate with a single entrance? Who can attack her there, and how?
   - Enumerate small configurations (a grid search on small boards) and give the safe ones with pictures.
5. **Assassination geometry.**
   - With the queen moving first, when can a hunter of length H force a head-to-head with a queen of length Q in open space, in a corridor, or at a room mouth?
   - How many hunters are needed to corner a queen of length Q on an open board?
6. **Tiebreak arithmetic.** When both queens die, the longest living dragon decides. Compare the expected value of keeping a backup versus feeding everything into the queen, as a function of the queen's survival probability p (give a small model and a table).
7. **Summary table:** rule fact → design consequence → planner term or gate.

## Deliverables
- `exp/queen-math/`: scripts, tables and small-board enumerations.
- `research/observations/queen-mechanics.md`, in Korean:
  - every fact cites the rule line it comes from;
  - keep [사실] and [해석] apart;
  - include ASCII pictures for the vault and assassination cases.
- `exp/queen-math/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/queen-math/**` and `research/observations/queen-mechanics.md`. Do not commit.
- No network, no uploads, no local games. Simulate the rules in your own scripts.
- One worker process.
- **Target:** about 2–3 hours.
