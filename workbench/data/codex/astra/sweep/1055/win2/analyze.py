import sys
sys.dont_write_bytecode = True
import ast, types, json, hashlib
from pathlib import Path

OUT = Path(__file__).resolve().parent
source = Path('data/codex/astra/sweep/0630/win1/analyze.py')
tree = ast.parse(source.read_text())
nodes = []
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'allrows' for t in node.targets):
        break
    nodes.append(node)
reader = types.ModuleType('existing_win_reader')
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), reader.__dict__)
reader.OUT = OUT
JOBS = [(i, 'data/online/smoke/one12-k1-old') for i in (1504483,1504485,1504487,1504488,1504490,1504491)]
JOBS += [(i, 'data/online/live-one1/b1504730') for i in (1504730,1504732,1504733,1504734)]
JOBS += [(i, 'data/online/live-one1/b1501263') for i in (1501263,1501264)]
rows = []
for gid, folder in JOBS:
    row = reader.scan(gid, folder)
    assert row['bot_ids']['us'] == '21330'
    row['input_sha256'] = hashlib.sha256((Path(folder)/f'M{gid}.replay').read_bytes()).hexdigest()
    rows.append(row)
    print(gid, row['map'], row['ours'], 'final', row['final'], 'lead', row['permanent_lead'],
          'qdeath', [(s,d['round'] if d else None,d['cause'] if d else None,d['actor'] if d else None) for s,d in row['queen_deaths'].items()],
          'counts', row['counts'], flush=True)
(OUT/'measurements.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))

audit_source = Path('data/codex/astra/sweep/0630/win1/audit.py')
audit_tree = ast.parse(audit_source.read_text())
audit_tree.body = [n for n in audit_tree.body if not
    (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'OUT' for t in n.targets)) and not
    (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'print')]
exec(compile(audit_tree, str(audit_source), 'exec'), {'OUT': OUT, '__file__': str(OUT/'analyze.py')})
