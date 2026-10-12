import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_qdef import scan as guard_scan

OUT = Path(__file__).resolve().parent
counts, games, detailed = Counter(), Counter(), []
for row in json.loads((OUT/'summary.json').read_text()):
    d = json.loads((OUT/f"{row['gid']}.json").read_text())
    ts = [json.loads(x) for x in (OUT/f"{row['gid']}-turns.jsonl").read_text().splitlines()]
    own = [x for x in ts if x['s'] == 0]
    counts.update(d['signatureCounts'])
    games.update(k for k,v in d['signatureCounts'].items() if v)
    cap = [x for x in own if 350 < x['r'] < 400 and x['ownN'] >= 56 and x['death'] == 4 and x['free'] > 0]
    idle = [x for x in own if not x['split'] and not x['steps'] and x['alive'] and x.get('actionKind') == 0]
    missed = [x for x in own if x['adjp'] and not x['split'] and x['alive'] and not any(z in x['adjp'] for z in x['eaten'])]
    pocket = [x for x in own if x['pocket_pearl_choices'] and x['steps'] and not x['split'] and x['L'] < 4 and not any(c in x['steps'] for c in x['pocket_pearl_choices'])]
    relax = [x for x in own if x['id'] == d['queenIds'][0] and x['split'] and x['L'] == 4 and x['ownN'] < 2]
    guards = guard_scan('win1', Path(d['path']), d['meta'])
    candidates = [x for x in guards['guard'] if x[1] <= 4 and x[5] <= 3 and x[7] <= x[6]]
    defender_rams = [x for x in candidates if x[8]]
    costs = Counter(idle_survived=len(idle), missed_survived=len(missed), pocket_short=len(pocket), cap_context_stops=len(cap), qs_relax=len(relax), guard_candidate=len(candidates), guard_ram=len(defender_rams))
    counts.update(costs)
    games.update(k for k,v in costs.items() if v)
    detailed.append(dict(gid=d['gid'], cap_context_stops=cap, idle=idle, pocket_short=pocket[:3], qs_relax=relax, guard_candidates=candidates, defender_rams=defender_rams, queen_risk=guards['death']))
    print(d['gid'], dict(costs), flush=True)
output = dict(counts=dict(counts), games=dict(games), details=detailed,
              caution='Behavior signatures are not counterfactual switch effects. Guard candidates use the imported static-occupancy reach proxy; leader/private memory exclusions are not reconstructed.')
(OUT/'audit.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
