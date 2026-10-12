# g2: map-aware forager with survival lookahead

- Bot: `bot/` (C++: `main.cpp` + generated `mapdb.hpp`). Own protocol reader. Protocol-2 input, ECHOES tolerated.
- Full history of r1–r5 (design, A/B tests, online analyses): `versions/NOTES_before_loop.md`.

## Current design (r5)
- **Map knowledge.** The 15 public maps are embedded (`tools/genmaps.py`). The map is identified from the first 7x7 view and re-checked every turn; if the check fails, the bot falls back to learning the map from vision.
- **Per-turn choice.** Each of the 4 moves gets a score from:
  - legality;
  - enemy-head threat, including sprint reach, scaled by our length and by how few dragons we have;
  - a survival DFS that knows when our own body, grown pearls, and fully visible other dragons free up;
  - space and tail reach;
  - food (a pearl probability model plus spawn countdowns);
  - a corridor check (head-on risk; dead-end raids only on Autarky and Prisoners).
- **Splits.**
  - Escape split only when physically doomed.
  - Stuck split (L-2), but only if the tail has room.
  - Insurance splits: U==1; U==2 & L>=6; U<4 & 8<=L<=24.
  - Swarm mode (split 2 at L>=5 while U<14): always on Trophy; for 60 rounds on other maps after seeing >=3 small enemy heads. Not on Autarky, Prisoners or Trauma.
  - Calm mode on Trauma: only the U==1 insurance split.
- **Sonar.** Only used on a split: the parent sends the child its first 12 body steps.

## Tools
- `tools/g2eval.py OUT BOT OPP[,OPP] SEEDS [maps] [--jobs 2] [--one-side]`: runs 2 games at a time; plays both sides by default.
- `tools/summ.py` summarises eval results.
- `tools/traj.py`, `tools/capture.py`: trajectories and 7x7 views.
- `tools/online_an.py`, `tools/rams.py`, `tools/batchcmp.py`: online batch analysis.
- Before launching a new eval, wait until the previous eval's line count is complete (limit: 2 concurrent games).

## Baselines (10 maps × 2 seeds × both sides = 40 games per opponent)
- r5: v8 23/40, hunter 35/40.
- Weak vs v8: Prisoners 0/4 (14–14 tie, lost on total), Slithery 0/4 (our champion dies early), Autarky 1/4.
- Trophy vs hunter: 1/4.
- Online r2 batch (54 games): 21W / 33L, 15 eliminations. Portals shows ally head-on collisions through blind portal jumps.

## Log
ready: r5 — r2 + Trophy swarm mode + stuck-split cascade guard + dynamic "hunted" swarm trigger + calm mode on Trauma. Local, 40 games per opponent: vs v8 48%→58%, vs hunter 75%→88%, vs swarm 95–100%, vs h2 100%. main.cpp sha256 ccad0740…
