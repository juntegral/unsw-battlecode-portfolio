# Two replay counts on our lost ladder games

Read-only counts. Do not edit existing files, call no model, post nowhere, no server calls (the replays are already
on disk). Write only inside `data/analysis/ladder/losses/counts/`.
Inputs: `data/analysis/ladder/losses/losses.json` (every lost main game with its bucket), `data/analysis/ladder/rows.jsonl`
(all games), `data/analysis/ladder/maps.json`, and the downloaded ladder replays under `data/online/` (find them from
the game ids; `data/analysis/ladder/work/` has earlier replay passes such as `h12_pass.py`, `h13_pass.py`, `h14_pass.py`
whose parsing and path-distance code you may reuse). A dragon sees the 7x7 box around its head. Path steps = shortest
walk on open tiles, walls and portals respected, bodies ignored. Use `our_code == "main"` only. Use every game named.

## Count 1: do our dragons get near their lone queen? (the 21 "Q1" losses, and a reference group)
Q1 = lost on the queen rule with only their queen alive while our longest dragon was the longer one.
Reference = main games in which our queen died first and their queen died later (we then usually won).
For every turn of their queen after round 100 while our queen is dead and theirs is alive:
- how many of our heads are within 12 path steps of her head, and how many of those are dragons of length 4 or less;
- the path distance from her to our nearest dragon of length 4 or less;
- the age in rounds of the freshest sighting of her by any of our heads (she was inside that head's 7x7 view):
  0-20, 21-60, older than 60, never seen;
- per game: the closest any of our short dragons ever got to her, how many times one of our heads moved onto a tile
  next to her head, and how she died if she did (round, cause, length of both).
Report per group: games, queen turns, mean heads within 12 steps, share of turns in each sighting-age class, and
inside the 21-60 class the distribution of the nearest short dragon's distance (20 or less, 21-40, more than 40).
Split by her length (4 or less, 5-12, 13 or more).

## Count 2: why do we not grow early? (the "never grew" games against the games that grew)
Never grew = main games in which we have 6 or fewer dragons at round 100 or are gone before it (77 games when the
plan was written). Compare with main games on the same layouts in which we had more than 6 at round 100.
For rounds 0 to 100, for every turn of one of our dragons that eats nothing:
- did that dragon know of a pearl (a pearl tile it saw inside its own 7x7 view within the last 25 rounds and that
  had not been eaten since)? If yes, the path steps to the nearest such pearl: 6 or less, 7 to 15, more than 15;
- did its step reduce its distance to the centre of the map;
- was an enemy head inside its view.
Also per game: round of our first meal, pearls eaten by round 50 by each side, and the round of our first split.
Report both groups side by side, and separately for layouts that start with 2 dragons a side.

## Output (`data/analysis/ladder/losses/counts/`)
- `summary.md`, 60 lines or fewer: the two tables, exact definitions used, what could not be measured. Numbers only,
  no advice.
- `hunt.json`, `growth.json` (per-game rows), the scripts, and `last.txt` (5 lines or fewer, written LAST, when
  everything else is final).
- Check and state in last.txt: the Q1 game count equals the bucket in losses.json; final standings reconstructed from
  each replay match rows.jsonl for at least the games used.
