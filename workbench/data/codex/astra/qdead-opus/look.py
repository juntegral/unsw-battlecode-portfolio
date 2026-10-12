"""look.py <on arm> <off arm>: per game, enemy-queen death round against the QDK trace file, our queen afterwards,
r100 economy, and whether the two arms are the same game up to the first trace line.
Run from the repo root: python3 -B data/codex/astra/qdead-opus/look.py qd_on qd_base"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'tools')
from pathlib import Path
from o1_scan import scan
RUNS = Path.home() / 'meow-redteam/solo/runs'
HERE = Path('data/codex/astra/qdead-opus')


def rows(arm):
    cp = HERE / ('scan-%s.jsonl' % arm)
    cache = {}
    if cp.exists():
        for l in cp.read_text().splitlines():
            g = json.loads(l)
            cache[g['folder']] = g
    for folder in sorted((RUNS / arm).glob('*-seed*-side?')):
        if not (folder / 'result.txt').exists() or folder.name in cache:
            continue
        m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
        k = int(m[3])
        j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
        g = scan(arm, folder / 'game.replay', j)
        g['folder'] = folder.name
        t = Path(str(folder) + '.qdk')
        g['logs'] = [l.split() for l in t.read_text().splitlines()] if t.exists() else []
        cache[folder.name] = g
    with open(cp, 'w') as f:
        for g in cache.values():
            f.write(json.dumps(g, separators=(',', ':')) + '\n')
    return {k: cache[k] for k in sorted(cache)}


def snap(g, r):
    r = min(r, g['last'])
    r -= r % 25
    return g['snaps'].get(str(r), g['snaps'][str(g['last'])])


def info(g):
    qd = {0: None, 1: None}
    for d in g['deaths']:
        if d[6] and qd[d[1]] is None:
            qd[d[1]] = d
    foe, own = qd[1], qd[0]
    rf = foe[0] if foe else None
    ro = own[0] if own else None
    L = [[l[0]] + [int(x) for x in l[1:]] for l in g['logs']]
    by = lambda w: [l for l in L if l[0] == w]
    see, rule, know, knowq, unknow = by('see'), by('rule'), by('know'), by('knowq'), by('unknow')
    early = [l for l in see + know + knowq if rf is None or l[1] < rf]
    return dict(rf=rf, ro=ro, foe=foe, own=own, see=see, rule=rule, know=know, knowq=knowq, unknow=unknow, early=early,
                first=min([l[1] for l in L], default=None),
                pearls100=sum(1 for e in g['eats'] if e[1] == 0 and e[0] < 100), u100=snap(g, 100)[0][0],
                qsplit=[s for s in g['splits'] if s[1] == 0 and s[5] and rf is not None and s[0] > rf],
                qpaid=[p for p in g['paids'] if p[1] == 0 and p[6] and rf is not None and p[0] > rf])


if __name__ == '__main__':
    on, off = rows(sys.argv[1]), rows(sys.argv[2])
    for arm, gs in ((sys.argv[1], on), (sys.argv[2], off)):
        print('==', arm, len(gs), 'games')
        tot = dict(games=0, foedead=0, seen=0, qknow=0, early=0, unknow=0, expo=0, qdeaths=0, first=0, wins=0)
        for name, g in gs.items():
            i = info(g)
            rf, ro = i['rf'], i['ro']
            tot['games'] += 1
            tot['wins'] += g['result'] == 'win'
            tot['early'] += len(i['early'])
            tot['unknow'] += len(i['unknow'])
            after = ''
            if rf is not None and (ro is None or ro > rf):
                tot['first'] += 1
                tot['expo'] += (ro if ro is not None else g['last']) - rf
                tot['qdeaths'] += ro is not None
                after = ' ourQ at +0/+25/+50/+100/end %s/%d' % ('/'.join(str(snap(g, rf + x)[0][3]) for x in (0, 25, 50, 100)), g['ends'][0][3])
            if rf is not None:
                tot['foedead'] += 1
                tot['seen'] += bool(i['see'])
                tot['qknow'] += bool(i['knowq'])
            print(' %-26s %-4s %-7s foeQ dies %s (%s L%s) ourQ dies %s (%s L%s) | see %d first %s rules %s | know %d knowq %s unknow %d EARLY %d | q splits after %s paid %s |%s | r100 pearls %d units %d' % (
                name.replace('gx_', '').replace('-seed', ' s').replace('-side', ' k'), g['result'], g['how'],
                rf, i['foe'][4] if i['foe'] else '-', i['foe'][2] if i['foe'] else '-',
                ro, i['own'][4] if i['own'] else '-', i['own'][2] if i['own'] else '-',
                len(i['see']), i['see'][0][1] if i['see'] else None, sorted(l[4] for l in i['rule']),
                len(i['know']), i['knowq'][0][1] if i['knowq'] else None, len(i['unknow']), len(i['early']),
                [(s[0], s[2], s[3]) for s in i['qsplit']], [(p[0], p[2], p[3]) for p in i['qpaid']], after, i['pearls100'], i['u100']))
        print('  TOTAL', tot, 'our queen deaths per 100 rounds after theirs died first: %.2f' % (100.0 * tot['qdeaths'] / max(1, tot['expo'])))
    print('== same game before the first trace line? (%s against %s)' % (sys.argv[1], sys.argv[2]))
    for name, g in on.items():
        if name not in off:
            continue
        h = off[name]
        first = info(g)['first']
        keys = sorted(set(int(r) for r in g['snaps']) | set(int(r) for r in h['snaps']))
        diff = next((r for r in keys if g['snaps'].get(str(r)) != h['snaps'].get(str(r))), None)
        ev = lambda x, lim: [d[:5] for d in x['deaths'] if d[0] < lim] + [s for s in x['splits'] if s[0] < lim] + [e[:4] for e in x['eats'] if e[0] < lim]
        lim = first if first is not None else 10 ** 6
        same = ev(g, lim) == ev(h, lim)
        i, k = info(g), info(h)
        print(' %-26s first trace r%s | events before it identical: %s | first differing 25-round snapshot: %s | r100 pearls %d/%d units %d/%d' % (
            name.replace('gx_', '').replace('-seed', ' s').replace('-side', ' k'), first, same, diff, i['pearls100'], k['pearls100'], i['u100'], k['u100']))
