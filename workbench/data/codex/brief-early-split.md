# Why is our first split late in the games where we never grow? (2-dragon-start layouts)

Read-only count on replays. Do not edit existing files, call no model, post nowhere, no server calls.
Write only inside `data/analysis/ladder/losses/split/`. Reuse the parsing in
`data/analysis/ladder/losses/counts/` (scripts and `growth.json` from the previous count) and its definitions:
`our_code == "main"`, layouts where each side starts with 2 dragons, "never grew" = 6 or fewer of our dragons at the
end of round 100 or gone before it, "grew" = more than 6 on the same layout.
Background: on these layouts the first meal comes at the same time in both groups (median round 19 against 21) but
the first split does not (median round 27 against 5.5), and by round 50 we have eaten 4.1 pearls against 14.0 while
the opponents have 13.7 in both.

## Per game (all main games on 2-dragon-start layouts), for OUR side and for THEIR side separately
- group (never grew / grew, by OUR count), our side (A or B), layout key, result;
- round of the first split, of the second split, and of the first three meals;
- for each of the two starting dragons at rounds 0, 5, 10, 20, 30: alive or not, length, number of dragons that side has;
- the length of the dragon that made the first split, at the moment it split, and what it had eaten before;
- rounds 0 to 30: turns with an enemy head inside the view (7x7) of one of the side's dragons, deaths of the side's
  dragons (round and cause), and whether the queen (the dragon with id 0 or 1) is the one that split first;
- the starting length of each starting dragon and the smallest length at which any dragon in the whole data set
  ever split (to learn the rule from the data: say what you find).

## Tables for `summary.md` (60 lines or fewer, numbers only, no advice)
1. First split round in classes (0-10, 11-30, 31-60, later or never) by group, for us and for them.
2. The same by our side (A or B) and by layout key (so we can see whether it follows the start position).
3. For games where our first split is after round 10: the lengths of our two starting dragons at rounds 5 and 10,
   whether either had eaten, whether an enemy head was in view before round 10, and whether a starting dragon died
   before round 30. Next to it the same four numbers for games where our first split is at round 10 or earlier.
4. Who splits first on each side: the queen or the other starting dragon, and at what length.
5. Opponents on the same layouts: their first split round against ours in the same game (earlier / same / later).
Definitions and limits at the end. `per-game.json`, the script, and `last.txt` written last (5 lines or fewer, with
the check that game counts match the previous count: 66 never grew and 52 grew).
