# Brief: post the online result to Discord as a small monospace table

Work in this repository (unsw-swarm). Edit `tools/pair_report.py` and `tools/test_pair_report.py`. No commits. No network; tests must not call `node`, `online.js` or meowbot. Never read `docs/api.txt` or `docs/discord.txt`. A detached script will run `python3 tools/pair_report.py bl17594b-test` (no `--post`) within the next half hour: write your new version to a temporary file and move it into place in one step, so the file is importable at every moment.

## Why
The team finds the one-line result message hard to read. They want the numbers in a code-block table (Discord renders ``` blocks in monospace), like this:

```
📊 #31 queen-hunt (on new main) online result, same teams + maps
```​
(the block below is the message body; the first line is plain text, then a fenced block)

    📊 #31 queen-hunt (on new main) online result, same teams + maps
    ```
    opponent          wins new   wins live   our score      their score
    all               10/30       4.0/30     54.3 → 65.1    167.8 → 166.8
    test4              8/15       0.0/15     42.9 → 80.1    190.1 → 182.5
    WeHaveQuizzes      2/15       4.0/15     65.6 → 50.1    145.5 → 151.1
    ```
    live baseline 30 games (thin, under 45). about ±4 wins in 30 games is luck

## What to change
- Only the Discord message built for `--post` changes. The printed text, `<label>-result.txt`, the per-opponent `vs` lines, the per-map table and everything else stay exactly as they are now.
- First line: `📊 <ref> online result, same teams + maps`.
- Then one fenced block with a header row and one row per line: `all`, then each opponent in the same order as the `vs` lines. Columns: opponent, wins new (`w/n`), wins live (`x.x/n`), our score (`a → b`), their score (`c → d`). Pad with spaces so the columns line up (compute widths from the content; opponent names can be long or contain non-ASCII characters, so cut names at 18 characters). With a single opponent, print only that one row (no separate `all` row).
- Opponents without a live baseline get a row with `-` in the live and "from" positions.
- Last line, plain text: `live baseline <g> games` plus ` (thin, under 45)` when the pooled live games are fewer than 45, plus, when any opponent has fewer than 30 live games, ` · thin for <names>`; then `. about ±4 wins in 30 games is luck`.
- Keep the whole message under 1,900 characters: if needed drop opponent rows from the end and add a row `…`.
- Update the tests that check the old message string, and add tests for: column alignment (every row of the block has the same position for the second column), single opponent, no-baseline opponent, the thin notes, the character cap.

## Checks
From inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` ends with `OK`. Then, without `--post`, build and print the message string for `qh31d-test` with ref `#31 queen-hunt (on new main)` and for `qd36-test` with ref `#36 queen-dead-end` (their game files are on disk; no network).

## Output
Write `data/codex/report-result-table.md` last: what changed, the two sample messages exactly as they would be sent, the last 4 lines of the test run.
