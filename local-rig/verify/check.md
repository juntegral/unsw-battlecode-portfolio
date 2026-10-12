# Replay verification
Reproduce: `python3 -B verify/check.py`. Uses `tools/replay_format.py`; round tables cross-checked against `tools/show.py`.
Rounds below mean end-of-round. Intervals include every dragon turn start in the stated closing round through r500; free-neighbour distributions use queen turn starts only.
Movement graph respects wall edges, wrapping and portals (every replay update checked). BFS blocks all occupied intermediate cells; source enemy head and destination queen head are allowed endpoints; unreachable = ∞.
“Within 3 cells” means wrapped Manhattan distance ≤3 to any queen segment, ignoring obstacles; counts are distinct enemy IDs, with repeated head observations stated separately.

## W1 — confirmed: NO as stated; survival, length and queen-rule wins: YES.
**blobs_large_90030**, from r186: dragon 0 alive at end; end-round lengths r186/r186/r300/r400/r500 = 23/23/23/23/23.
Free-neighbour distribution: {2: 1, 1: 314} (free neighbours: queen turns). Reachable queen-start distances (round, distance): [(186, 20), (187, 14), (188, 14)]; other 312 queen starts unreachable.
Across all 38769 turn starts: minimum enemy-head path = 12; unreachable at 38521 starts. Enemy heads next to queen head: 0 observations (0 IDs); also zero at queen starts.
Enemy dragons at r200/r300/r400/r500 = 64/60/60/47; range at all turn starts (45, 64), queen starts (46, 64), round ends (46, 64).
Enemy heads within 3 of queen body: 48 distinct IDs; 35763 observations across all turn starts, in 175 rounds. Queen starts alone: 45 IDs, 293 observations.
End: r500 round limit, side 0 wins longer queen 23–0; side 0/1 dragons 60/47, longest 27/42, total length 261/425.
**portalrooms_large_90006**, from r56: dragon 0 alive at end; end-round lengths r56/r186/r300/r400/r500 = 23/23/23/23/23.
Free-neighbour distribution: {2: 1, 1: 444} (free neighbours: queen turns). Reachable queen-start distances (round, distance): [(56, 3), (57, 19)]; other 443 queen starts unreachable.
Across all 54764 turn starts: minimum enemy-head path = 3; unreachable at 54650 starts. Enemy heads next to queen head: 0 observations (0 IDs); also zero at queen starts.
Enemy dragons at r200/r300/r400/r500 = 62/59/61/61; range at all turn starts (52, 64), queen starts (52, 64), round ends (52, 64).
Enemy heads within 3 of queen body: 70 distinct IDs; 62117 observations across all turn starts, in 353 rounds. Queen starts alone: 70 IDs, 505 observations.
End: r500 round limit, side 0 wins longer queen 23–0; side 0/1 dragons 60/61, longest 23/49, total length 211/392.
Differences: blobs has two free neighbours at the r186 queen start; head remains reachable at queen starts r186–188. The reported 47–64 enemies is 45–64 during turns, 46–64 at queen starts/round ends. Portalrooms has two free neighbours at the r56 queen start and reachable head at r56–57. Later sampled queen starts have one free neighbour and no free-cell enemy path.

## W2 — reported dragon counts confirmed: YES; deliberate self-thinning/feed-one-long-dragon interpretation: NOT established.
**portals_medium_90020**, side 1: counts r320/r360/r440/r480/r489 = 59/39/26/5/0; no count differs. Longest lengths r320/r400/r440/r480 = 34/40/8/3.
Deaths r320–489 inclusive: 374 total; head hit by active enemy 327; own turn initiating head-to-head 23 (head-to-head combined 350); wall 0; body 12 (self 2, another dragon 10); no valid action 12.
Replay death codes: 0 wall, 1 self-body, 2 other-body, 3 head-to-head, 4 no valid action; last category does not prove no output was sent. Most deaths are combat; longest length falls to 8 then 3, so these measurements do not establish intentional feeding of one banker.
End: r489 elimination, side 0 wins; side 0/1 dragons 60/0, longest 26/0, total length 309/0, queens 0/0.
