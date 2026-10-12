# Fifteen checks against reopened sources

Checked after drafting and shortening TEAM-BRIEF.md. Markdown sources were reopened and their exact rows or paragraphs printed. Checks 7–8 independently reopened games.json and recomputed the named counts, rather than reading the generated table. “Match” refers to the claim as written, with its sample and definition.

| # | Brief section and claim | Source file and section | Reopened source result | Match |
|---|---|---|---|---|
| 1 | §1: 104 deaths had a safe alternative; 90 had a roomy non-portal alternative | `data/analysis/top1/deep-read-4.md`, §2, “How good was the safe step she did not take” | meow row: 104 deaths, 92 roomy, 90 roomy without portal | yes |
| 2 | §1: later recount 106 versus earlier 104 avoidable rams | `data/analysis/top1/redteam.md`, Candidate 2 A, counts table | earlier 66 + 38 = 104; later 67 + 39 = 106 | yes |
| 3 | §2: 91 boxed deaths in our 401-game study sample | `data/analysis/top1/deep-read-4.md`, §2, boxed-in subtypes | all row: meow 91; surrounding classification names 401 games | yes |
| 4 | §2: wait-build game 1125139 sheds 25→23+2 at round 0 | `data/online/smoke/qw37-analysis/summary.md`, §6 Slithery Fight first ten rounds | new / WHQ / 1125139 / r0 / length 25 / actual split 25→23+2 | yes |
| 5 | §3: test4 loops 25.2% of queen-rounds against us; long loops in 84/154 games | `data/analysis/top1/deep-read-4.md`, §5f, Circling table | test4 against meow: 25.2%; 84 of 154 | yes |
| 6 | §3: test4 breaks its loop at 147, returns and dies at 149 in 1054795 | `data/analysis/top1/deep-read-4.md`, §5f, Checked against cases | loop 120–146; enemy arrives 147; safe north/west; south return and ram 149 | yes |
| 7 | §4: Portals jumping queens, ours 45/45 versus top three 44/108 | `data/analysis/queen-portals/games.json`, Portals records, queens by tag | independent count: ours 45 queens, 45 with jumps; top three 108, 44 with jumps | yes |
| 8 | §4: Portals elimination share 1/147 unique games | `data/analysis/queen-portals/games.json`, Portals records, game_id and end | independent distinct-game count: 147; elimination 1 | yes |
| 9 | §5: immediate visible chances taken 99/435 later, 99/446 earlier | `data/analysis/top1/redteam.md`, Candidate 1 A, counts table | meow row: earlier 99 of 446; strict and later recount 99 of 435 | yes |
| 10 | §5: portal-fix hunt wins 8/30 against test4+WHQ, same as live | `data/online/smoke/qh31b-analysis/summary.md`, test4 + WeHaveQuizzes, outcome table | live 8/30; new 8/30 | yes |
| 11 | §6: counted guard rams live 1, new 0, 30 games each against test4+WHQ | `data/online/smoke/kg34b-analysis/summary.md`, test4 + WeHaveQuizzes, item 6 | live E=1 G=30; new E=0 G=30 | yes |
| 12 | §7: small-map natural intake 39.5→31.0 per 50 rounds in 99 live games | `data/analysis/top1/REPORT.md`, §3.2(d), fixed-cohort table | 99-game row: before 39.5, first after 31.0, later 29.4 | yes |
| 13 | §7: later economy read reports our units 43/47 at rounds 100/150 | `data/analysis/top1/deep-read-3.md`, Us against the top three, row 1 | pooled meow 43/47; live subset 42/46, candidate 45/52 | yes |
| 14 | §8: Vibing++ final longest is median 59% of final potential in 67 small-map races | `data/analysis/top1/deep-read-5.md`, §2, small-map Table A1 | Vibing++: 67 games, completeness at end 0.59 | yes |
| 15 | §9: walker validated against 81,853 engine steps | `data/analysis/top1/REPORT.md`, §1, Data | explicitly states 81,853 steps | yes |

Additional structure checks: exact title; nine requested headings in order; each has four to eight fact bullets and the four requested subsections; one to five replay rows per section; every linked game appears in an allowed narrative source. Portal table has every map and each of the three stored team tags, with unique-game denominators for elimination. Main document: 39,937 characters at this check, below the 60,000-character issue limit.

Source disagreements are retained explicitly: queen 104/106; hunt 446/435 opportunities; earlier/later economy snapshots; older leader-cut delay versus current recovery; and test4's “never” feeding statement versus its own detailed table. No third distinct hunt build was invented.
