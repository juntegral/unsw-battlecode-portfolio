import sys
sys.dont_write_bytecode = True
import ast, json, types, hashlib
from pathlib import Path
from collections import Counter

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
JOBS = [(1498744, 'data/online/smoke/one11-p1-old'),
        (1498747, 'data/online/smoke/one11-p1-old'),
        (1498750, 'data/online/smoke/one11-p1-old'),
        (1498454, 'data/online/live-one1/b1498454'),
        (1498503, 'data/online/live-one1/b1498503')]
rows = []
for gid, folder in JOBS:
    row = reader.scan(gid, folder)
    assert row['bot_ids']['us'] == '21269'
    row['input_sha256'] = hashlib.sha256((Path(folder)/f'M{gid}.replay').read_bytes()).hexdigest()
    rows.append(row)
    print(gid, row['map'], 'final', row['final'], 'lead', row['permanent_lead'],
          'qdeath', row['queen_deaths'], 'counts', row['counts'], flush=True)
(OUT/'measurements.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))

audit_source = Path('data/codex/astra/sweep/0630/win1/audit.py')
audit_tree = ast.parse(audit_source.read_text())
audit_tree.body = [n for n in audit_tree.body if not
    (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'OUT' for t in n.targets)) and not
    (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'print')]
scope = {'OUT': OUT, '__file__': str(OUT/'analyze.py')}
exec(compile(audit_tree, str(audit_source), 'exec'), scope)
audit = json.loads((OUT/'switch-audit.json').read_text())
# Recompute the earlier sample's non-generic feed-cap field for this sample.
cap = []
for g in rows:
    turns = json.loads((OUT/f'{g["gid"]}-turns.json').read_text())
    cap.extend(dict(game=g['gid'], round=t['round'], dragon=t['id']) for t in turns
               if t['side']=='us' and t['action']==2 and 350<t['round']<=400 and t['count']>=56)
audit['FEED_CAP_ROUND_compatible'] = dict(count=len(cap), games=len({t['game'] for t in cap}), examples=cap[:3],
    definition='No-action death at rounds351-400 with team count>=56; leader state and alternative feeding triggers not reproduced.')
audit['note'] = 'Five games, own bot21269 in each; all counts are signatures or exposures, not isolated switch activation. No bot executions or new games.'
(OUT/'switch-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
