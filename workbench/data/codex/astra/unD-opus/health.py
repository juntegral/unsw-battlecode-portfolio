"""unD-opus: one health line per finished game under ~/meow-redteam/solo/runs/<arm>/ (run from ROOT)."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from pathlib import Path
import o1_scan
import detect
RUNS = Path.home() / 'meow-redteam/solo/runs'
HERE = Path('data/codex/astra/unD-opus')
arm = sys.argv[1] if len(sys.argv) > 1 else 'ud_mD17'
cache_path = HERE / ('health-%s.jsonl' % arm)
cache = {}
if cache_path.exists():
    for l in cache_path.read_text().splitlines():
        g = json.loads(l)
        cache[g['folder']] = g


def side_row(g, d, s):
    def sn(r):
        r = min(r, g['last'])
        return g['snaps'].get(str(r), g['snaps'][str(g['last'])])
    eats = [e[0] for e in g['eats'] if e[1] == s]
    qd = [x for x in g['deaths'] if x[1] == s and x[6] == 1]
    lc = sum(sum(c.values()) for c in d['lc'][s])
    n = sum(d['cnt'][s][role][ph]['n'] for role in range(2) for ph in range(3))
    return dict(first=min(eats, default=-1), p=[sum(1 for r in eats if r <= R) for R in (25, 50, 100)], d=[sn(R)[s][0] for R in (25, 50, 100)],
                loop=round(100 * lc / n, 1) if n else 0, qd=[qd[0][0], qd[0][4], qd[0][5], qd[0][2]] if qd else None,
                qL=[sn(100)[s][3], sn(300)[s][3], g['ends'][s][3]], tot=g['ends'][s][1],
                qsplit=sum(1 for x in g['splits'] if x[1] == s and x[5]))


for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
    if not (folder / 'result.txt').exists() or folder.name in cache:
        continue
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
    k = int(m[3])
    log = (folder / 'engine.log').read_text(errors='replace') if (folder / 'engine.log').exists() else ''
    marks = {w: len(re.findall(w, log, re.I)) for w in ('crash', 'timeout|timed out', 'illegal|invalid', 'exception|traceback', 'killed|signal|memory')}
    row = dict(folder=folder.name, map=m[1], k=k, result=(folder / 'result.txt').read_text().strip(), marks={a: b for a, b in marks.items() if b})
    try:
        j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
        g = o1_scan.scan(arm, folder / 'game.replay', j)
        d = detect.scan(folder / 'game.replay', k)
        row.update(cells=g['cells'], res=g['result'], how=g['how'], last=g['last'], us=side_row(g, d, 0), op=side_row(g, d, 1))
    except Exception as ex:
        row['fail'] = repr(ex)[:200]
    cache[folder.name] = row
with open(cache_path, 'w') as f:
    for g in cache.values():
        f.write(json.dumps(g, separators=(',', ':')) + '\n')


def fmt(s):
    q = s['qd']
    return 'eat1 r%-3d p %3d/%3d/%3d d %2d/%2d/%2d loop %4.1f%% q %-18s qL %d/%d/%d qs%d' % (
        s['first'], *s['p'], *s['d'], s['loop'], ('r%d %s f%d L%d' % tuple(q)) if q else 'alive', *s['qL'], s['qsplit'])


for g in sorted(cache.values(), key=lambda g: (g.get('cells', 0), g['map'], g['k'])):
    if 'fail' in g:
        print('%-22s s%d FAIL %s | %s | %s' % (g['map'], g['k'], g['fail'], g['result'], g['marks']))
        continue
    red = []
    u, o = g['us'], g['op']
    if g['marks']:
        red.append('log')
    if u['first'] > 40 or u['first'] < 0:
        red.append('eat')
    if u['d'][2] <= 3 and o['d'][2] >= 3 * u['d'][2]:
        red.append('few')
    if u['qd'] and u['qd'][0] < 50 and u['qd'][1] in ('wall', 'own body', 'mate head', 'mate body'):
        red.append('qself')
    if u['loop'] > 10:
        red.append('loop')
    print('%-20s %5d s%d %-4s %-7s r%-3d %s\n   US %s\n   OP %s  %s' % (g['map'][3:], g['cells'], g['k'], g['res'], g['how'], g['last'], ','.join(red) or '-', fmt(u), fmt(o), g['marks'] or ''))
