## Verdicts (all counts [M] from replays on disk)

### 14:57 KST, final: cannot tell (0 games)
- No game with bot id 21827 (one19) reached `data/online/live-one1` between 14:36 and 14:57 KST. Last poll 14:56:49.
- The one battle that landed after the upload, b1536232 against Team SKKU (lost 1 of 5, done 14:39 to 14:42 KST), was played by
  21761 = one18. The requests to SKKU, test4 and Cybers produced no folder in that time.
- Nothing about one19 is measured: no BROKEN sign seen and no GOOD sign seen, because there were no games.
- Baselines from the same folders (lines below): one17 45 games, one18 40 games. On maps of 600 cells or fewer, queen dead on a wall
  or her own body with 0 free cells before r60: 0 of 16 (one17), 0 of 17 (one18). Timeouts 0, a side of ours that never eats 0,
  collapse from 3 or more dragons to none in one round 0, in both. Queen moving into an enemy head on her own turn: 3 games each.
- Not checked: whether 21827 is the active submission on the server (only replays on disk were read).
- To add a late one19 game: `python3 -B data/codex/astra/watch19-opus/w19.py` from ROOT, then `mk19.py`.

### 14:45 KST: no one19 game yet; b1536232 (Team SKKU) was one18
