# Where our ladder losses come from: an exclusive breakdown of lost games

Read-only count on `data/analysis/ladder/rows.jsonl` (one row per ranked game; fields include `our_code`, `result`,
`ended_by`, `queens_at_end`, `final`, `curves`, `queen`, `deaths`, `head_on`, `pearls`, `map_key`, `opponent_rating`,
`last_round`). Do not edit existing files, do not call any model, do not post anywhere, no server calls.
Write only inside `data/analysis/ladder/losses/`. The definitions block at the top of
`data/analysis/ladder/findings.md` (lines 25 to 35) explains the words used in the data; reuse those definitions
("level game", "big", "full game", "queen rule", bands by opponent rating) so the numbers line up with that ledger.
Rules reminder: at round 500 the longer queen wins and a dead queen counts as 0; if that does not decide, the
longest dragon does.

## Population
Two code slices, reported side by side: `our_code == "main"` (the live code) and `our_code == "v31"` (the old bot).
Ignore the test builds. Use every game in the slice, no sampling.

## Part 1: every LOST game goes into exactly one bucket, tested in this order
1. E1: we were wiped out by round 125.
2. E2: we were wiped out after round 125.
3. Q1: lost on the queen rule with only their queen alive, and our longest dragon was at least as long as theirs.
4. Q2: lost on the queen rule with only their queen alive, our longest dragon shorter.
5. Q3: lost on the queen rule with both queens alive (ours shorter).
6. L1: both queens dead at the end, lost on longest dragon (or the rule after it).
7. Other (list how each such game ended).
For each bucket and slice: n, share of that slice's losses, and inside the bucket:
- position at round 100 by total length: behind / level / ahead (level = within 20 percent);
- layouts: big (width times height above 1200) against the rest; 2-dragon-start layouts if the data shows them;
- opponent band (under 1900, 1900-2099, 2100+);
- our queen: alive at the end or not, median death round, death causes (counts), dead by round 100, dead by round 200;
- "thrown lead": we were ahead in total length at round 300 (by more than 20 percent) and still lost.

## Part 2: risk table over ALL games of the slice (wins and losses)
For each condition below: games with it, loss rate with it, loss rate without it, and how many of the slice's losses
carry it. Conditions: behind at round 100; our queen dead by round 100; our queen dead by round 200 while theirs is
alive; we hold the only living queen at some checkpoint; big layout; opponent 2100+; opponent 1900-2099;
our queen's length at round 200 is 3 or less (alive); our alive-dragon count at round 100 below theirs.
Then the same loss rates for the five most common PAIRS of conditions among losses.

## Part 3: stability
Part 1 shares for the main slice split at 2026-10-06 14:48:15 UTC (the ledger's "half 1 / half 2").

## Output (all in `data/analysis/ladder/losses/`)
- `summary.md`, 70 lines or fewer: the Part 1 table (buckets as rows, main and v31 as columns, with n and share),
  the within-bucket numbers for the three largest main buckets, the Part 2 table, the Part 3 line, and a short
  "definitions and limits" block (exact rule used for each bucket, any field that was missing or ambiguous).
  Measured numbers only, no interpretation, no advice.
- `losses.json`: one row per lost game with its bucket and the fields used.
- the script, and `last.txt` (5 lines or fewer: what was done, checks, anything that failed).
- Check: bucket counts sum to the slice's losses; totals match `result` counts (main 169 losses of 375, v31 207 of 410
  at the time of writing; say so if the file has grown).
