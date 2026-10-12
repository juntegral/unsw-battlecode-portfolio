from pathlib import Path
import json, subprocess, concurrent.futures
root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem2'
review = json.loads((task / 'review-analysis.json').read_text())
keys = {}
for t in review['auditTargets']:
    keys.setdefault(t['key'], set()).update(t['ids'])
jobs = []
for key, ids in keys.items():
    for arm in ['on', 'off']:
        stem = key.replace(':', '_')
        jobs.append((key, arm, sorted(ids), task / 'audit' / f'{stem}-{arm}'))
def run(job):
    key, arm, ids, prefix = job
    replay = task / arm / 'games' / key.replace(':', '_') / 'game.replay'
    args = ['node', str(task / 'replay-audit.js'), str(replay), key.split(':')[2], str(prefix), ','.join(map(str, ids))]
    with open(str(prefix) + '.log', 'w') as log:
        result = subprocess.run(args, cwd=root, stdout=log, stderr=subprocess.STDOUT)
    print(key, arm, len(ids), result.returncode, flush=True)
    return {'key': key, 'history': arm, 'ids': ids, 'prefix': str(prefix.relative_to(root)), 'exit': result.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    rows = list(pool.map(run, jobs))
(task / 'audit-index.json').write_text(json.dumps(rows, indent=2) + '\n')
assert all(r['exit'] == 0 for r in rows)
