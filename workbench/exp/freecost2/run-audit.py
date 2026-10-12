from pathlib import Path
import json
import subprocess
root = Path(__file__).resolve().parents[2]
task = root / 'exp/freecost2'
report = json.loads((task / 'firstdiv.json').read_text())
(task / 'audit').mkdir(exist_ok=True)
index = []
for row in report['rows']:
    if row['status'] != 'matched':
        continue
    ids = ','.join(str(c['id']) for c in row['changed'])
    for arm in ['on', 'off']:
        prefix = task / 'audit' / (row['key'].replace(':', '_') + '-' + arm)
        with Path(str(prefix) + '.log').open('w') as log:
            result = subprocess.run(['node', str(task / 'replay-audit.js'), row['files'][arm], row['side'], str(prefix), ids],
                                    cwd=root, stdout=log, stderr=subprocess.STDOUT)
        index.append({'key':row['key'], 'R':row['R'], 'ids':ids, 'history':arm, 'prefix':str(prefix.relative_to(root)), 'exit':result.returncode})
        print(row['key'], arm, result.returncode, flush=True)
(task / 'audit-index.json').write_text(json.dumps(index, indent=2) + '\n')
assert all(x['exit'] == 0 for x in index)
