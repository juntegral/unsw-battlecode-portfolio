import json
from pathlib import Path
P=Path('data/analysis/ladder/dossier');S=json.loads((P/'work/lr_summary.json').read_text());cs=S['groups']
def num(v):return '—' if v is None else f'{v:g}'
def pair(v,fmt=None):return '/'.join(num(x) if fmt is None else ('—' if x is None else format(x,fmt)) for x in v)
lines=['| Mover group/type | Games | Head-ons (per game) | r0–100: N (per game); median M/V | r101–300: N (per game); median M/V | r301–499: N (per game); median M/V | Median M/V, all | Longest (ties count) | Queen |',
'|---|---:|---:|---|---|---|---|---:|---:|']
for c in cs:
    cells=[f"{n} ({n/c['games']:.3f}); {pair(m)}" for n,m in zip(c['band'],c['band_medians'])]
    lines.append(f"| {c['group']}/{c['type']} | {c['games']} | {c['n']} ({c['n']/c['games']:.3f}) | "+' | '.join(cells)+f" | {pair(c['median_lengths'])} | {c['longest']} | {c['queen']} |")
lines+=['','| Group/type | Mover queen alive/dead | Queen steps ≤3 / 4–8 / >8 / unreachable (alive only) | Victim approached queen: either/both of last 2 turns (eligible N) | Victim can reach ≥8 head / queen | Other mover-side heads ≤3 tiles: 0/1/≥2 (mean) | Free adjacent tile at turn start: yes/no | Victim can reach mover turn-start head |',
'|---|---|---|---|---|---|---|---:|']
for c in cs:
    lines.append(f"| {c['group']}/{c['type']} | {c['queen_alive']}/{c['queen_dead']} | {pair(c['queen_distance']+[c['queen_unreachable']])} | {c['toward_any']}/{c['toward_both']} ({c['history2']}) | {c['victim_big']}/{c['victim_queen']} | {pair(c['sweep3_bins'])} ({c['sweep3_mean']:.2f}) | {c['free_start']}/{c['n']-c['free_start']} | {c['first_start']} |")
lines+=['','| Group/type | All drops M/V | Fully observed / censored meetings | Full-cohort drops M/V | Eaten within 15 rounds by M/V side | M-body drops eaten by M/V; V-body drops eaten by M/V | Mean collision length account M/V | Mean whole-team length Δ after 15 rounds M/V |',
'|---|---|---|---|---|---|---|---|']
for c in cs:
    lines.append(f"| {c['group']}/{c['type']} | {pair(c['drop_all'])} | {c['full']}/{c['censored']} | {pair(c['drop_full'])} | {pair(c['eaten'])} | {pair(c['eaten_origin'][0])}; {pair(c['eaten_origin'][1])} | {pair(c['collision_account'],'.2f')} | {pair(c['net15'],'.2f')} |")
lines+=['', '| Counting rule | Definition |', '|---|---|',
'| Types and lengths | Long: mover turn-start length ≥5, victim impact length < half; Equal: mover turn-start length 2–4, victim impact length equal; M/V: mover/victim |',
'| Data and checks | Opp2100+/OtherOpp: rating split of 500 main games; Us: all 500; Top1: team 306, 597 unique games (1,194 side rows deduplicated); all 1,097 final states verified; all 500 main games match the existing scan on meetings, lengths, drops and eaters |',
'| Location and reach | Queen distance: shortest wall/portal path; sweepers: wrapped Manhattan distance, mover excluded; approach: completed turn reduces distance to impact queen position, queen alive and 2 prior turns required; reach: frozen impact bodies/pearls, free ceil(L/4) steps plus paid length down to 2, no 8-step cap; ≥8 target includes mover; strike-first target is mover’s turn-start head |',
'| 15-round accounting | Recovery and length means use complete windows only; collision account: −length at death + side’s recovery from both bodies; whole-team Δ: total at end of impact round +15 minus total immediately before collision, includes all intervening events |']
(P/'work/lr_report-base.md').write_text('\n'.join(lines)+'\n')
print('base lines',len(lines))
