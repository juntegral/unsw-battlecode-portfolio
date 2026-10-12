# Check the numbers and code references in a plan document

Read-only check. Do not edit existing files, call no model, post nowhere, no server calls.
Write only `data/analysis/ladder/losses/plan-check.md` (40 lines or fewer) and a script under
`data/analysis/ladder/losses/work/` if you need one. Do not reuse `losses/work/recount.py`; count independently.

Document to check: `data/analysis/ladder/losses/plan.md`.
Data: `data/analysis/ladder/rows.jsonl` (use `our_code == "main"`), definitions as in
`data/analysis/ladder/losses/summary.md` ("level" within 20 percent, "big" = width times height above 1200 from
`data/analysis/ladder/maps.json`).
Code: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`.

## A. Recount these claims from rows.jsonl (say the number you get and whether it matches; if the file has grown
since the plan was written, give both the current count and the count restricted to the first 400 main games)
1. 400 main games, 180 lost; buckets L1 50, E2 43, Q2 30, Q1 21, E1 16, Other 14, Q3 6.
2. "In 77 main games we have 6 or fewer dragons at r100 or are gone before it; 56 are lost."
3. "66 of the 77 are on layouts that start with 2 dragons a side."
4. "Above 1200 cells we lose 77 of 127 games (103 of 273 below)."
5. "40 of the 77 were level or ahead in total length at r150; from that position we win only 42 of 82."
6. "Our queen is dead at the end in 160 of 180 losses: rammed 120, wall 23, own body 12, another body 5."
7. "Q1: 21 losses", and in all 21 our longest dragon was strictly longer.
8. "Our longest dragon is 10 or more at r150 in 33 of 126 big-layout games and at r200 in 91 of 125."
9. "A queen dying with no action is 1 of our 295 queen deaths on main and in none of the 180 losses."

## B. Check these code references in main.cpp (quote the line you find, with its number)
1. grow_round is 150 above 1200 cells, else 300 (plan says line 468).
2. QUEEN_GIVE_WAY is 0 (line 195) and QUEEN_ALLY_BLOCK is false (line 163).
3. QH_MAX_LEN 4 and QH_FRESH 20, used around lines 1993-2007, and the hunt starts from round 100 when our queen is dead.
4. EAT_BONUS 300 and ZONE_PEARL_PENALTY 600 near lines 5055-5060, applied within 9 tiles of the leader.
5. is_leader() near line 3328.

## Output
`plan-check.md`: one row per claim (claim, plan's number, your number, match yes/no, note). Then one line listing
every mismatch. Nothing else.
