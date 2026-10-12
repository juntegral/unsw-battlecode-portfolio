"""First eats and starter traces. Online: early.py on <game json> ... ; local: early.py loc <arm folder under solo/runs> <game folder name>"""
import sys, json, re
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, 'data/codex/astra/early-opus')
import scan as S, summ
RUNS = Path.home() / 'meow-redteam/solo/runs'


def show(tag, g, full=True):
    for s in (0, 1):
        E = [e for e in g['eats'] if e['side'] == s]
        print(tag, 'side', s, 'first eats', [(e['r'], tuple(e['xy'])) for e in E[:6]])
    print(tag, 'snap rounds', sorted(int(k) for k in g['snaps'])[-3:], {k: (v.get('heads'), v.get('length')) for k, v in g['snaps'].items() if int(k) in (25, 50, 100)})
    try:
        m = summ.measure(g, 0); o = summ.measure(g, 1)
    except Exception as ex:
        print(tag, 'no measure', repr(ex)); m = None
    if m is None:
        full = full
    else:
      pass
    if m: print(tag, 'ours  eat25/50/100 %d %d %d heads %d %d %d len100 %d' % (m['eat25'], m['eat50'], m['eat100'], m['heads25'], m['heads50'], m['heads100'], m['len100']))
    if m: print(tag, 'theirs eat25/50/100 %d %d %d heads %d %d %d len100 %d' % (o['eat25'], o['eat50'], o['eat100'], o['heads25'], o['heads50'], o['heads100'], o['len100']))
    if full:
        ids = sorted({t['id'] for t in g['turns'] if t['side'] == 0 and t['r'] <= 1})
        for i in ids[:3]:
            tr = [t for t in g['turns'] if t['id'] == i and t['r'] <= 44]
            print('   id', i, ' '.join('%d:%d,%d' % (t['r'], t['h'][0], t['h'][1]) for t in tr))


if sys.argv[1] == 'on':
    for p in sys.argv[2:]:
        p = Path(p); j = json.loads(p.read_text())
        g = S.scan('x', p)
        print('==', p.name, j.get('mapName'), 'A', j.get('teamAId'), 'B', j.get('teamBId'), 'last', g.get('last'))
        if len(sys.argv) < 4: print(' eat keys', list(g['eats'][0].keys()) if g['eats'] else None)
        show(p.stem, g)
else:
    for arm in sys.argv[3:]:
        folder = RUNS / arm / sys.argv[2]
        if not (folder / 'result.txt').exists(): print(arm, 'no game'); continue
        m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name); k = int(m[3])
        j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1])
        g = S.scan(arm, None, j, folder / 'game.replay')
        print('==', arm, (folder / 'result.txt').read_text().strip()[:80])
        show(arm, g)
