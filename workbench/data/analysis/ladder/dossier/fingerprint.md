# Behaviour fingerprint

500 games; 19 layouts; 1000 side rows. Rating bands: <1900 (215), 1900–2099 (215), 2100+ (70).
Rates pool numerators/denominators; percentages use 0–100; W/L percentage residuals are points. Ties/missing layouts do not count as higher.
W/L = mean game rate minus its layout mean, then mean within wins/losses; draws excluded; negative values are residuals.
Order: ≥15/19 layouts agree with pooled sign and all three bands, then others; each group by |ours−theirs|/max(|ours|,|theirs|).
The first 19 table rows meet the consistency threshold; the remaining rows do not.
Windows include endpoints; counts use observed turns only. Seen is cumulative at r100/r300; early endpoints are missing.
Blind keep: successful blind turns with a preceding successful direction; re-tread: successful blind turns. Partial 20-round blocks excluded.
Harvest/wait use birth-window cohorts eaten by game end, not eating-window counts; wait excludes uneaten pearls.
Queen incidence: alive at window start and observed through endpoint or death; death/contact rounds are conditional event means.
First-contact incidence excludes still-uncontacted games ending before endpoint. Queen lengths and head-on lengths are JSON context.
Recount: all 500 replays, only pearl origin at eating time (rows lack it) and whole-game turns (portal denominator absent); counts matched rows.
Explained labels apply to traced head-on mover/hit and portal-cohort harvest; mixed-window splitting/harvest stay open (r151 leader regime not isolated).

| Rate (unit) | Window | Ours | Theirs | Higher /19 | 2100+ O/T | <1900 O/T | W/L residual | Status |
|---|---|---:|---:|---:|---|---|---|---|
| Death: no action (/1k turns) | 0-100 | 0.000 | 2.983 | 18 | 0.000/5.475 | 0.000/1.809 | 0.000/0.000 | open |
| Same-team head-on meetings (/1k turns) | 101-300 | 0.107 | 0.374 | 15 | 0.147/0.336 | 0.115/0.452 | 0.012/-0.014 | open |
| Death: head-on mover (/1k turns) | 101-300 | 1.456 | 3.207 | 16 | 1.399/2.443 | 1.307/3.600 | -0.037/0.043 | explained |
| Head-on meetings started (/1k turns) | 101-300 | 1.456 | 3.207 | 16 | 1.399/2.443 | 1.307/3.600 | -0.037/0.043 | explained |
| Death: head-on mover (/1k turns) | 0-100 | 1.510 | 3.047 | 15 | 1.261/2.853 | 1.403/2.982 | -0.062/0.072 | explained |
| Head-on meetings started (/1k turns) | 0-100 | 1.510 | 3.047 | 15 | 1.261/2.853 | 1.403/2.982 | -0.062/0.072 | explained |
| Portal steps (/1k turns) | game | 11.891 | 7.524 | 1 | 12.335/10.304 | 12.567/6.705 | 0.176/-0.205 | open |
| Repeated-spawn tile nearby (%) | 101-300 | 24.242 | 32.497 | 16 | 26.619/35.551 | 24.152/33.695 | 1.261/-1.464 | open |
| Blind direction kept (%) | 0-100 | 39.031 | 50.160 | 18 | 38.588/49.826 | 39.210/49.716 | -0.517/0.608 | open |
| Blind direction kept (%) | 101-300 | 37.382 | 46.321 | 17 | 37.260/46.570 | 37.405/45.888 | -0.343/0.408 | open |
| Splits per eaten pearl (/pearl) | game | 0.366 | 0.312 | 4 | 0.382/0.293 | 0.361/0.317 | -0.006/0.007 | open |
| Splits per eaten pearl (/pearl) | 101-300 | 0.376 | 0.321 | 4 | 0.387/0.291 | 0.371/0.332 | 0.002/-0.002 | open |
| Repeated-spawn tile nearby (%) | 0-100 | 15.740 | 18.358 | 15 | 17.557/20.866 | 15.836/18.441 | 1.146/-1.334 | open |
| Blind turns (%) | 101-300 | 49.968 | 43.058 | 4 | 46.556/41.662 | 49.158/42.783 | -1.539/1.787 | open |
| Blind re-tread (%) | 101-300 | 17.566 | 15.342 | 4 | 17.949/16.011 | 17.483/15.828 | -0.280/0.332 | open |
| Blind tiles visited per 20-round dragon block (tiles/block) | 101-300 | 11.441 | 10.170 | 3 | 11.028/10.343 | 11.490/10.002 | 0.030/-0.036 | open |
| All deaths (/1k turns) | game | 20.804 | 23.262 | 18 | 24.487/25.307 | 20.823/23.896 | -1.611/1.876 | open |
| Split frequency (/1k turns) | game | 22.245 | 24.325 | 15 | 25.296/26.773 | 22.449/24.565 | 0.305/-0.355 | open |
| Blind successful movement (%) | 101-300 | 98.530 | 97.926 | 3 | 98.385/97.697 | 98.531/97.958 | -0.061/0.073 | open |
| Death: illegal split (/1k turns) | 0-100 | 0.000 | 0.952 | 10 | 0.000/0.000 | 0.000/2.340 | 0.000/0.000 | open |
| Death: illegal split (/1k turns) | 101-300 | 0.000 | 0.695 | 13 | 0.000/0.000 | 0.000/1.680 | 0.000/0.000 | open |
| Death: timeout (/1k turns) | 101-300 | 0.000 | 0.001 | 1 | 0.000/0.000 | 0.000/0.002 | 0.000/0.000 | open |
| Death: unpaid sprint (/1k turns) | 101-300 | 0.000 | 0.002 | 4 | 0.000/0.002 | 0.000/0.001 | 0.000/0.000 | open |
| Queen death: illegal split (%) | 101-300 | 0.000 | 0.330 | 1 | 0.000/0.000 | 0.000/0.730 | 0.000/0.000 | open |
| Queen death: no action (%) | 0-100 | 0.000 | 1.826 | 6 | 0.000/1.471 | 0.000/1.878 | 0.000/0.000 | open |
| Queen death: head-on mover (%) | 0-100 | 0.818 | 3.245 | 8 | 1.429/7.353 | 0.476/1.878 | 0.396/-0.442 | explained |
| Queen death: wall (%) | 101-300 | 12.141 | 3.300 | 1 | 16.279/2.564 | 10.294/4.380 | 1.264/-1.209 | open |
| Same-team head-on meetings (/1k turns) | 0-100 | 0.098 | 0.357 | 14 | 0.179/0.296 | 0.118/0.504 | 0.011/-0.013 | open |
| Queen death: own body (%) | 0-100 | 2.658 | 0.811 | 4 | 1.429/2.941 | 2.857/0.939 | 1.026/-1.146 | open |
| Death: no action (/1k turns) | 101-300 | 1.150 | 3.270 | 14 | 1.230/7.978 | 1.234/1.757 | 0.126/-0.146 | open |

## Open gaps, largest first

- 0-100: A dragon of theirs dies after failing to provide a move or split more often than ours; fields: `ranges.0-100.deaths.no action`, `ranges.0-100.turns`.
- 0-100: A dragon of theirs dies after an illegal split more often than ours; fields: `ranges.0-100.deaths.illegal split`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs dies after an illegal split more often than ours; fields: `ranges.101-300.deaths.illegal split`, `ranges.101-300.turns`.
- 101-300: A dragon of theirs dies after an action timeout more often than ours; fields: `ranges.101-300.deaths.timeout`, `ranges.101-300.turns`.
- 101-300: A dragon of theirs dies after a sprint it cannot pay for more often than ours; fields: `ranges.101-300.deaths.unpaid sprint`, `ranges.101-300.turns`.
- 101-300: Their queen dies after an illegal split more often than ours; fields: `queen.death.cause`, `queen.death.round`, `last_round`.
- 0-100: Their queen dies after failing to provide a move or split more often than ours; fields: `queen.death.cause`, `queen.death.round`, `last_round`.
- 101-300: Their queen dies by hitting a wall less often than ours; fields: `queen.death.cause`, `queen.death.round`, `last_round`.
- 0-100: A dragon of theirs starts a head-on meeting with a teammate more often than ours; fields: `ranges.0-100.same_team_head_on_trades`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs starts a head-on meeting with a teammate more often than ours; fields: `ranges.101-300.same_team_head_on_trades`, `ranges.101-300.turns`.
- 0-100: Their queen dies by hitting its own body less often than ours; fields: `queen.death.cause`, `queen.death.round`, `last_round`.
- 101-300: A dragon of theirs dies after failing to provide a move or split more often than ours; fields: `ranges.101-300.deaths.no action`, `ranges.101-300.turns`.
- game: A dragon of theirs takes portal steps less often than ours; fields: `portal_steps_game`, `recount.game.turns`.
- 101-300: A dragon of theirs starts on or beside a tile with at least two prior pearl spawns more often than ours; fields: `ranges.101-300.hot_turns`, `ranges.101-300.turns`.
- 0-100: A dragon of theirs keeps its previous successful direction when no pearl is in view more often than ours; fields: `ranges.0-100.keeps`, `ranges.0-100.keeps_eligible`.
- 101-300: A dragon of theirs keeps its previous successful direction when no pearl is in view more often than ours; fields: `ranges.101-300.keeps`, `ranges.101-300.keeps_eligible`.
- game: A dragon of theirs splits per pearl eaten less often than ours; fields: `game_counts.splits`, `game_counts.pearls_eaten`.
- 101-300: A dragon of theirs splits per pearl eaten less often than ours; fields: `ranges.101-300.splits`, `ranges.101-300.pearls_eaten`.
- 0-100: A dragon of theirs starts on or beside a tile with at least two prior pearl spawns more often than ours; fields: `ranges.0-100.hot_turns`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs starts its turn with no pearl in view less often than ours; fields: `ranges.101-300.no_view_pearl_turns`, `ranges.101-300.turns`.
- 101-300: A dragon of theirs steps onto one of its own last 12 visited tiles when no pearl is in view less often than ours; fields: `ranges.101-300.dither`, `ranges.101-300.no_view_pearl_moved`.
- 101-300: A dragon of theirs visits tiles in a complete 20-round dragon block during blind turns with fewer distinct tiles than ours; fields: `ranges.101-300.no_view_pearl_distinct_per_dragon_20.sum`, `ranges.101-300.no_view_pearl_distinct_per_dragon_20.n`.
- game: A dragon of theirs dies more often than ours; fields: `game_counts.deaths`, `recount.game.turns`.
- game: A dragon of theirs splits on its turn more often than ours; fields: `game_counts.splits`, `recount.game.turns`.
- 101-300: A dragon of theirs makes at least one successful step when no pearl is in view less often than ours; fields: `ranges.101-300.no_view_pearl_moved`, `ranges.101-300.no_view_pearl_turns`.
