"""unA-opus: one health line per game and seat. Run from ROOT: python3 -B data/codex/astra/unA-opus/health.py [keys]"""
import sys, re, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from pathlib import Path
from o1_scan import scan
import detect
RUNS = Path.home() / 'meow-redteam/solo/runs'
BAD = re.compile(r'timeout|timed out|crash|illegal|traceback|exception|killed|invalid', re.I)


def snap(g, r):
    r = min(r, g['last'])
    r -= r % 25 if str(r) not in g['snaps'] else 0
    return g['snaps'].get(str(r), g['snaps'][str(g['last'])])


def line(arm, folder, k, tag):
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=folder.name.split('-seed')[0], teamAName='A', teamBName='B')
    g = scan(arm, folder / 'game.replay', j)
    log = (folder / 'engine.log').read_text(errors='replace') if (folder / 'engine.log').exists() else ''
    bad = len(BAD.findall(log))
    out = []
    for s in (0, 1):
        ea = [e for e in g['eats'] if e[1] == s]
        first = min((e[0] for e in ea), default=-1)
        pe = [sum(1 for e in ea if e[0] <= r) for r in (25, 50, 100)]
        dr = [snap(g, r)[s][0] for r in (25, 50, 100)]
        qd = [d for d in g['deaths'] if d[1] == s and d[6] == 1]
        q = '%d:%s:f%s:L%d' % (qd[0][0], qd[0][4].replace(' ', ''), qd[0][5], qd[0][2]) if qd else 'alive'
        ql = [snap(g, r)[s][3] for r in (100, 300)] + [g['ends'][s][3]]
        dk = Counter = {}
        for d in g['deaths']:
            if d[1] == s and d[0] < 100:
                dk[d[4]] = dk.get(d[4], 0) + 1
        out.append('eat1 %3d | pearls %3d %3d %3d | drag %2d %2d %2d | Q %-22s qL %s | deaths<100 %s' % (first, pe[0], pe[1], pe[2], dr[0], dr[1], dr[2], q, '/'.join(map(str, ql)), ','.join('%s%d' % (a.replace(' ', '')[:4], b) for a, b in sorted(dk.items()))))
    print('%-16s %-7s %-4s last %3d bad %d' % (j['mapName'], tag, g['result'] + ':' + g['how'][:5], g['last'], bad))
    print('    US  ' + out[0])
    print('    OPP ' + out[1])
    return g


if __name__ == '__main__':
    keys = sys.argv[1:]
    for arm in ('ua_m3base', 'ua_mirror'):
        for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
            if not (folder / 'result.txt').exists() or (keys and not any(k in folder.name for k in keys)):
                continue
            k = int(folder.name[-1])
            try:
                line(arm, folder, k, ('mir' if arm == 'ua_mirror' else 'v3b') + '-s%d' % k)
            except Exception as ex:
                print('FAIL', folder.name, repr(ex)[:200])
