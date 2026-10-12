import json
from pathlib import Path
D=Path('data/analysis/ladder/dossier');W=D/'work'
screens={(r['who'],r['game']):r['screen'] for f in W.glob('qp_screen_*.jsonl') for s in f.open() for r in [json.loads(s)]};assert len(screens)==1097
for f in W.glob('qp_games_*.jsonl'):
 rows=[json.loads(s) for s in f.open()]
 for g in rows:
  for t,s in g['snaps'].items():
   if 'prox' in s:s['prox'][5]=screens[g['who'],g['game']].get(t)
 f.write_text(''.join(json.dumps(g)+'\n' for g in rows))
paragraphs=[
'O/R = ours (500 games) / rank-1 (597 games, team 306); rates and means pool within each shared layout then average equally over layouts valid for both sides, while n denotes pooled counts; Q is the lowest starting id and D denotes same-side nonqueens matching her length at each checkpoint or turn start.',
'Round 0 is initial state and later checkpoints are round ends; centre distance is torus Manhattan to (floor(width/2), floor(height/2)) divided by floor(width/2)+floor(height/2), path is shortest terrain/portal steps from the starting tile, other distances are torus Manhattan, band rows pool the listed checkpoints, moves count turns ending alive while the queen lives, away uses preturn mate heads with the closest within 8, mate-nearer-enemy means any mate closer than Q to any tied nearest enemy, and ended-live games are excluded after their last round.',
'Our surviving queen is closer than at r0 more often than rank-1 at r20–60 (r30: 66.5%/51.8%), but her normalized centre distance is lower only at r30, and her centreward-turn share in r0–30 is 53.6% versus rank-1’s 53.0% and our same-length others’ 59.0% (r31–60: 49.5%/50.5% versus 50.1%; r61–150: 48.9%/47.5% versus 48.8%).',
'Our queen’s nearest-mate distance is consistently above our same-length others from the r40 checkpoint (6.1 versus 5.4 tiles) and above rank-1 from r80 (5.6/5.2 tiles), reaching 5.3/4.5 versus our others’ 5.0 at r150; her away-turn share is below our others in every band (r61–150: 45.1% versus 45.4%, rank-1 queen 42.7%).',
'Observed deaths by r150 total 217/500 for ours and 275/597 for rank-1, including 144/146 after r60, with 125/164 head-on hits, 48/0 wall deaths, 21/0 own-body deaths and 0/88 illegal-split deaths; 24/21 games ended before r150 with the queen alive.'
]
report=(W/'qp_tables.md').read_text()+'\n'+'\n'.join(paragraphs)+'\n';assert len(report.splitlines())<=50
(D/'queen-path.md').write_text(report)
(W/'qp_methods.md').write_text('''# Queen-path counting details
- Source rows: relation=us only, exactly 500 O and 597 R; original dossier side and queen id checked against replay starts.
- Checkpoint 0: initial board, before any actions; checkpoints 10–150: end of that round.
- Positions are reconstructed from dragonUpdate, dragonSplit, dragonDeath events using the shared replay reader; r100 lengths agree with all 1,033 nonmissing source values and deaths agree with source events.
- Dead queens remain known dead after game end; queens alive when a game ends are censored afterward, with no position extrapolation.
- Centre tile uses floor(width/2), floor(height/2); maximal torus Manhattan distance uses floor(width/2)+floor(height/2).
- Path displacement: shortest directed terrain graph distance, with walls and portal mappings; cumulative actual movement steps also retained as walk in per-game scratch.
- Heads within a radius include the radius boundary, exclude the subject, and include all teammates regardless of length.
- No teammate: radius counts zero, none5=1, nearest-mate distance missing; no enemy: screening percentage missing.
- Screening: any teammate is strictly closer than the queen to any enemy tied as her nearest enemy; an empty teammate set yields false.
- Snapshot D controls have exactly the queen length in the same snapshot; their individual proximity values average within snapshot, then pool queen snapshots within layout.
- Turn D controls match the living queen current length at their own turn start; all subject turns ending alive enter centreward denominators, including stays and surviving splits; dead-ending turns are excluded.
- Away denominator: a preturn teammate within 8; compare nearest distance before/after to the frozen set of preturn teammates, excluding split newborns.
- Movement windows are inclusive 0–30, 31–60, 61–150; grouped snapshots use 0/10/20/30, 40/60, 80/100/150 respectively.
- For each statistic, common layouts with a nonzero denominator for both O and R are equally weighted; qp_detail.json lists every numerator, denominator and valid layout.
- Death incidence denominators are all original games in each layout, counting observed deaths only; mean death rounds use layouts with deaths in both O and R.
- Death causes distinguish head-on hit and head-on mover, following existing dossier classifications; death counts and window counts are pooled, not weighted.
- qp_games_*.jsonl queen screening values are corrected by the independent head-only qp_screen_*.jsonl pass; qp_scan.py also implements that definition for reruns.
- Heavy scans invoked through nice -n 10; sandbox reported setpriority: Operation not permitted, so actual priority reduction could not be applied.
''')
print('report lines',len(report.splitlines()),'English prose sentences',len(paragraphs),'games',len(screens))
