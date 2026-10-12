from pathlib import Path
import json, collections
root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem2'
index = json.loads((task / 'audit-index.json').read_text())
out = {'scope': 'same recorded observations/actions replayed through both native Worlds; native clock is not judge clock', 'histories': [], 'resync': [], 'decisions': []}
forks = {r['key']: r for r in json.loads((task / 'firstdiv.json').read_text())['rows'] if r['status'] == 'matched'}
for job in index:
    prefix = root / job['prefix']
    meta = json.loads(Path(str(prefix) + '.json').read_text())
    snaps = json.loads(Path(str(prefix) + '.snapshots.json').read_text())
    models = {a: [json.loads(s) for s in Path(str(prefix) + '.' + a + '.jsonl').read_text().splitlines()] for a in ['on', 'off']}
    assert all(len(v) == len(snaps) for v in models.values())
    counts = {'turns': len(snaps), 'startDriftOn': 0, 'startDriftOff': 0, 'commonExactMultiNextN': 0, 'nextDriftOn': 0, 'nextDriftOff': 0, 'postDriftOn': 0, 'postDriftOff': 0}
    previous = {}
    for i, s in enumerate(snaps):
        for a in ['on', 'off']:
            if models[a][i]['body'] != s['body']: counts['startDrift' + a.title()] += 1
        if s['id'] in previous:
            j = previous[s['id']]
            p = snaps[j]
            if not p['actual'].startswith('split') and len(p['actual']) > 1 and p['actualOracle']['survived'] and all(models[a][j]['body'] == p['body'] for a in ['on', 'off']):
                counts['commonExactMultiNextN'] += 1
                case = {'key': job['key'], 'history': job['history'], 'id': s['id'], 'moveRound': p['round'], 'nextRound': s['round'], 'action': p['actual'], 'start': p['body'], 'actualEnd': p['actualOracle']['body'], 'nextActual': s['body'], 'indicator': p['indicator']}
                for a in ['on', 'off']:
                    bad = models[a][i]['body'] != s['body']
                    counts['nextDrift' + a.title()] += bad
                    counts['postDrift' + a.title()] += models[a][j]['post'] != p['actualOracle']['body']
                    case[a] = {'post': models[a][j]['post'], 'next': models[a][i]['body'], 'nextDrift': bad}
                out['resync'].append(case)
        previous[s['id']] = i
        f = forks.get(job['key'])
        if f and s['round'] == f['R'] and any(c['id'] == s['id'] for c in f['changed']):
            c = next(c for c in f['changed'] if c['id'] == s['id'])
            out['decisions'].append({'key': job['key'], 'history': job['history'], 'R': s['round'], 'id': s['id'], 'actualBody': s['body'], 'models': {a: models[a][i] for a in ['on', 'off']}, 'production': {a: c[a]['text'] for a in ['on', 'off']}, 'uncertain': meta['uncertain']})
    out['histories'].append({**job, **counts, 'uncertain': meta['uncertain'], 'reproduction': {a: meta['arms'][a]['choicesReproduced'] for a in ['on', 'off']}})
out['totals'] = {k: sum(h[k] for h in out['histories']) for k in ['turns', 'startDriftOn', 'startDriftOff', 'commonExactMultiNextN', 'nextDriftOn', 'nextDriftOff', 'postDriftOn', 'postDriftOff']}
(task / 'audit-summary.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({'histories': len(out['histories']), 'totals': out['totals'], 'decisions': len(out['decisions']), 'uncertain': sum(sum(h['uncertain'].values()) for h in out['histories'])}, indent=2))
