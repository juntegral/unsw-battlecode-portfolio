"""Per game rows for local arms: python3 -B data/codex/astra/tiny-opus/table.py <arm> [<arm> ...]  (arms under solo/runs/ty_<arm>)"""
import sys, json, re
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, 'data/codex/astra/early-opus')
import scan as S
RUNS = Path.home() / 'meow-redteam/solo/runs'
OUT = Path(__file__).resolve().parent / 'cache'
OUT.mkdir(exist_ok=True)
print('%-9s %-34s first eat25 eat50 eat100 hd25 hd50 hd100 len100 | opp first eat100 hd100 | result' % ('arm', 'game'))
for arm in sys.argv[1:]:
    for folder in sorted((RUNS / ('ty_' + arm)).glob('*-seed*-side*')):
        if not folder.is_dir() or not (folder / 'result.txt').exists():
            continue
        f = OUT / ('%s__%s.json' % (arm, folder.name))
        if not f.exists():
            m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name); k = int(m[3])
            j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1])
            g = S.scan(arm, None, j, folder / 'game.replay')
            row = dict(eats=[(e['r'], e['side']) for e in g['eats']], snaps={k: (v.get('heads'), v.get('length')) for k, v in g['snaps'].items()},
                       qdeath=[d['r'] for d in g['deaths'] if d['side'] == 0 and d['id'] in (0, 1)], result=(folder / 'result.txt').read_text().strip())
            f.write_text(json.dumps(row))
        g = json.loads(f.read_text())
        E = [[r for r, s in g['eats'] if s == k] for k in (0, 1)]
        ks = sorted(int(k) for k in g['snaps'])

        def sn(r, i, k):
            r = min(r, ks[-1])
            v = g['snaps'].get(str(r))
            return v[i][k] if v and v[i] else -1
        n = lambda k, r: sum(1 for x in E[k] if x <= r)
        print('%-9s %-34s %5s %5d %5d %6d %4d %4d %5d %6d | %9s %6d %5d | q%s %s' % (
            arm, folder.name[:34], E[0][0] if E[0] else '-', n(0, 25), n(0, 50), n(0, 100), sn(25, 0, 0), sn(50, 0, 0), sn(100, 0, 0), sn(100, 1, 0),
            E[1][0] if E[1] else '-', n(1, 100), sn(100, 0, 1), g['qdeath'][:1] or '-', g['result'][:62]))
