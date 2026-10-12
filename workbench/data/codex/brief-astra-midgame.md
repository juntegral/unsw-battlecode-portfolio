# Astra analyst: midgame

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `midgame`.

Question: one5 is level with WeHaveQuizzes at r100 (27.2 dragons / 67.9 length against 26.5 / 70.7) and then loses rounds 101-300
(98.5 against 142.4 at r300; 3 wins of 15). Against Cache me outside it wins 6 of 15 with the same shape (94 against 142 at the end).
Measured already with `data/analysis/ladder/dossier/work/o1_mid.py` (turn classes r0-300, both sides; rows in `work/o1_mid-<set>.jsonl`
for o2 o3 o4 o5 = one2..one5 against WHQ and c5 = one5 against Cache; table `o1_midtab.py <set> all <window 1|2>`, per map `o1_midmap.py`):
- natural pearls per 100 dragon turns, ours / theirs: r101-200 3.5-4.1 / 4.1-4.4, r201-300 2.8-3.1 / 3.2-3.7, in all five sets;
- our dragon turns are 2 to 27% fewer than theirs in r101-200 and more so in r201-300;
- one5 against WHQ r101-200, share of turns ours / theirs: blind (no pearl in the 7 by 7) 47.1 / 43.8%, blind with no mate in view
  13.1 / 8.9%, on the far half of the board 23.6 / 27.8%, a pearl one step away and not taken 1.4 / 0.9% (37.5 against 27.2 turns a
  game, although EAT_FIRST is on), eat given a pearl in view 12.8 / 14.1%.
1. Split the r101-300 gap into its parts with numbers that add up: fewer heads (where do they go: which deaths, per 100 turns, ours
   against theirs, by cause and by our length), fewer pearls per head-turn (which class), and ground (share of pearl-bearing tiles
   whose nearest head is ours). Use one5-w1 and one5-c1; one3-w1 as the check that it is not new in one5.
2. The pearl one step away that is not taken in r101-300: which condition of EAT_FIRST (`one5-bot/main.cpp` 969-973, 6003-6041)
   or which other term blocks it (feeder, leader pearl zone, pocket, dead end, threat, risk)? Count by reason from the replay state.
3. The dragons that are blind with no mate in view: who are they (length, age since split, distance to the nearest pearl-bearing tile
   seen by the side) and what moves them there?
4. At most two cards, the larger part first. A card must be a general rule, name the lines, and say what replay count shows it works.
