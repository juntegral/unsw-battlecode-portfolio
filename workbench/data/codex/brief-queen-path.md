# Where does our queen walk in the first 150 rounds, and who is near her? Ours against the rank-1 team

A teammate reports that our queen walks straight to the middle of the map on her own and seems to keep away from
our other dragons. Count it. Data: our 500 main ladder games (`data/analysis/ladder/dossier/per-game.jsonl`,
replays `data/online/ladder/`) and the rank-1 team's 597 games (`dossier/target/per-game-top1.jsonl`, replays
`data/online/top1/`, team id 306); shared reader `tools/ladder_replay.py`; scan scripts in `dossier/work/` show how
to pass over all games (for example `wk_scan.py`, `op_*.py`). The queen is the side's dragon with the lowest
starting id (0 or 1). Use the 19 shared layouts and weight each layout equally, as `dossier/target/scoreboard.md`.

## Count, for our queen and for rank-1's queen, at rounds 0, 10, 20, 30, 40, 60, 80, 100, 150 (while she lives)
1. distance from her head to the centre of the map (torus Manhattan, as a share of the largest possible), and
   path steps from her own starting tile; the share of queens that are nearer the centre than at round 0.
2. own heads within 3, within 5 and within 8 tiles of her head (means, and the share with none within 5); the
   distance to her nearest team mate; whether a team mate is nearer than she is to the nearest enemy head.
3. her moves: the share of her turns that end nearer the centre, the share that end farther from her nearest team
   mate than they began (when one is within 8), and the same two shares for the side's other dragons of the same
   length, so that "the queen does it more than the others" can be told from "everybody does it".
4. enemy heads within 5 tiles of her; her length; alive or not. Her death round and cause by round 150.
5. split the above for layouts of 700 cells or fewer, 701 to 1200, and above 1200, and by rounds 0-30, 31-60,
   61-150 (our bot pulls short dragons to the centre for the first 30 or 60 rounds on small or long layouts).

## Output: `data/analysis/ladder/dossier/queen-path.md` (50 lines or fewer), English
The tables (ours against rank-1), then at most six plain sentences: does our queen go to the middle more than
rank-1's and more than our other dragons; is she farther from team mates than rank-1's queen and than our other
dragons; from which round; and how it goes with her dying by round 150. Counts only. Scratch under
`dossier/work/` (prefix `qp_`). Last step: `data/analysis/ladder/dossier/queen-path-done.txt`.
Write only those paths. No network, no posts, no games. Run heavy scans with `nice -n 10`.
