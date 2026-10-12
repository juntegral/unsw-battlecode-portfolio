# Verify two claims of report.md from the replays (read-only check)

Work only in this directory. Write only `verify/check.md` (30 lines or fewer) and a script under `verify/`.
Do not change any other file, call no model, no network. Use `tools/show.py` or the replay decoder in `tools/`.

## Claim W1 (sealed queen)
Replay `runs/eval-final/sqheld_blobs_large_90030/seed-1-A-side-0/game.replay`: side 0's queen (dragon id 0)
"closed" a ring at round 186 and held it to the end at length 23 with 47-64 enemy dragons alive.
Check from the replay, for every turn start from round 186 to the end:
- is dragon 0 alive at the end, and what is its length at rounds 186, 300, 400, 500;
- at each of its turn starts, how many of the 4 neighbouring cells of its head are free (not wall, not a body);
  list the distribution;
- the smallest path distance from any enemy head to her head cell through free cells only (bodies block), and how
  many times an enemy head was on a cell next to her head;
- how many enemy dragons were alive at rounds 200, 300, 400, 500, and how many enemy heads came within 3 cells of
  any part of her body;
- how the game ended (rule and numbers).
Do the same for `runs/eval-final/sqheld_portalrooms_large_90006/seed-1-A-side-0/game.replay` from round 56.

## Claim W2 (late self-thinning)
Replay `runs/eval-final/sqheld_portals_medium_90020/seed-1-A-side-0/game.replay`: side 1 (the opponent) has 59
dragons at round 320, 39 at 360, 26 at 440, 5 at 480 and is gone at 489. Check those counts, and for side 1's
deaths from round 320 on give the causes (head hit by an enemy, ran into a wall, ran into a body, no action) with
counts, and the length of its longest dragon at rounds 320, 400, 440, 480.

## Output
`verify/check.md`: each claim, what the replay shows, confirmed yes/no, and any number that differs.
