from pathlib import Path
import json, re
root = Path(__file__).resolve().parents[2]
task = root / 'exp/freecost2'
spec = json.loads((task / 'spec.json').read_text())
index = json.loads((task / 'audit-index.json').read_text())
out = {'rows': [], 'nativeDepth': {'N': 0, 'lower': 0, 'same': 0, 'higher': 0, 'missing': 0}, 'productionSameInputPoints': None}
for job in index:
    name = job['key'].split(':')[1]
    entry = next(s for s in spec if s['out'].endswith('/' + job['history']) and name in s['only'])
    mapfile = root / entry['maps'] / (name + '.map')
    spawns = {}
    for line in mapfile.read_text().splitlines():
        parts = line.split()
        if parts and parts[0] == 'TILE': spawns[(int(parts[1]), int(parts[2]))] = int(parts[4])
    prefix = root / job['prefix']
    permanent, unknown = 0, 0
    for line in Path(str(prefix) + '.input').read_text().splitlines()[1:]:
        t = line.split()
        start = 6 + int(t[5]) + 5
        for j in range(49):
            x, y, pearl, countdown = map(int, t[start+4*j:start+4*j+4])
            if countdown == -1:
                if spawns.get((x,y), 0) == 0: permanent += 1
                else: unknown += 1
    meta = json.loads(Path(str(prefix) + '.json').read_text())
    out['rows'].append({**job, 'rawMissingCountdown': meta['uncertain']['missingCountdown'], 'permanentNoSpawnMinusOne': permanent, 'unknownSpawningCountdown': unknown, 'ambiguousFacing': meta['uncertain']['ambiguousFacing']})
    models = {a: [json.loads(s) for s in Path(str(prefix) + '.' + a + '.jsonl').read_text().splitlines()] for a in ['on', 'off']}
    for a, b in zip(models['on'], models['off']):
        x, y = re.search(r'\bd(\d+)\b', a['indicator']), re.search(r'\bd(\d+)\b', b['indicator'])
        if not x or not y: out['nativeDepth']['missing'] += 1
        else:
            out['nativeDepth']['N'] += 1
            d = int(x[1]) - int(y[1])
            out['nativeDepth']['lower' if d < 0 else 'higher' if d > 0 else 'same'] += 1
out['totals'] = {k: sum(r[k] for r in out['rows']) for k in ['rawMissingCountdown', 'permanentNoSpawnMinusOne', 'unknownSpawningCountdown', 'ambiguousFacing']}
(task / 'audit-input-check.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({'totals': out['totals'], 'nativeDepth': out['nativeDepth']}, indent=2))
