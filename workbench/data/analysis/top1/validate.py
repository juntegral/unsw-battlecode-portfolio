"""Independent event-stream checks against the supplied replay.parse implementation."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root.parent/'battlecode'))
import replay
out = root/'data/analysis/top1'
results = [json.loads(p.read_text())['result'] for p in sorted((out/'cache').glob('*.json'))]
selected = {}
for r in reversed(results):
    g = r['game']
    key = (g['map'], 'top1' in g['sources'])
    if key not in selected:
        selected[key] = r
checks = 0
for res in selected.values():
    g = res['game']
    info, events, teams = replay.parse(g['replay_path'])
    counts = {s: Counter() for s in 'AB'}
    lengths = {}
    for line in info['map'].splitlines():
        p = line.split()
        if p and p[0]=='DRAGON':
            lengths[len(lengths)] = int(p[2])
    for e in events:
        s = teams.get(e.get('id'))
        if e['kind']=='split':
            counts[s]['splits'] += 1
            lengths[e['id']] = e['parentLength']
            lengths[e['child']] = e['childLength']
        elif e['kind']=='death':
            counts[s]['deaths'] += 1
            lengths.pop(e['id'])
        elif e['kind']=='action' and e['action']=='suicide':
            counts[s]['suicides'] += 1
        elif e['kind']=='update':
            counts[s]['length_gained'] += max(0,e['length']-lengths[e['id']])
            lengths[e['id']] = e['length']
    for side in 'AB':
        rs = [r for r in res['timeline'] if r['side']==side]
        # A game ending exactly on a boundary repeats its last interval at end.
        if len(rs)>1 and rs[-1]['round_start']==rs[-2]['round_start']:
            rs = rs[:-1]
        for kind in ('splits','deaths'):
            actual = sum(sum(r[f'{kind}_{c}'] for c in ('le4','5_9','10plus')) for r in rs)
            assert actual==counts[side][kind], (g['game_id'],side,kind,actual,counts[side][kind])
            checks += 1
        for kind in ('suicides','length_gained'):
            assert sum(r[kind] for r in rs)==counts[side][kind], (g['game_id'],side,kind)
            checks += 1
        assert sum(r['bucket_rounds'] for r in rs)==g['rounds']
        checks += 1
for res in results:
    g = res['game']
    for r in res['timeline']:
        assert 0 <= r['cells_visited'] <= g['cells']
        assert r['round_end'] <= g['rounds']
        assert sum(r['deaths_'+c] for c in ('wall','self','body','headon','other'))==sum(r['deaths_'+c] for c in ('le4','5_9','10plus'))
        assert r['feeding_near_longest'] <= r['suicides']
        for c in ('le4','5_9','10plus'):
            assert sum(r[f'deaths_{cause}_{c}'] for cause in ('wall','self','body','headon','other'))==r['deaths_'+c]
        checks += 7
report = dict(cache_games=len(results),independent_replay_samples=len(selected),assertions=checks,
              game_ids=[r['game']['game_id'] for r in selected.values()],status='passed')
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
