"""watch19-opus: one line per game for one17/one18/one19 and the BROKEN / GOOD counts.
Usage (from ROOT): python3 -B data/codex/astra/watch19-opus/w19.py   (caches per game in cache.json, writes lines.txt)"""
import sys, json, glob, time
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from pathlib import Path
from collections import defaultdict
import o1_scan
import qdeath
from ladder_replay import replay

HERE = Path('data/codex/astra/watch19-opus')
src = Path('data/codex/astra/watch17-opus/w.py').read_text().split('\ndef main():')[0]
W17 = {}
exec(compile(src, 'w17', 'exec'), W17)
VER = {'21693': 'one17', '21761': 'one18', '21827': 'one19'}
W17['VER'] = VER
RS = {0: 'wall', 1: 'own body', 2: 'body', 3: 'headon'}


def one(lab, f, j):
    gid = j['id']
    rp = Path(f).parent / ('M%d.replay' % gid)
    own = 0 if j['teamAId'] == 1119 else 1
    bot = replay.load(rp).root().text(1 if own == 0 else 2).strip()
    if bot not in VER:
        return dict(id=gid, ver=None)
    row = o1_scan.scan(lab, rp, j)
    h = W17['run'](rp, j)
    q = qdeath.scan(rp, own)
    s100 = row['snaps'].get('100')
    e = [sum(1 for x in row['eats'] if x[0] < 100 and x[1] == k) for k in (0, 1)]
    eall = sum(1 for x in row['eats'] if x[1] == 0)
    qd = None
    if q['deaths']:
        d = q['deaths'][-1]
        qd = {k: d.get(k) for k in ('r', 'L', 'reason', 'own_turn', 'f0', 'f1', 'att', 'hit', 'att_gap', 'their_q_dead')}
    return dict(id=gid, ver=VER[bot], set=lab, opp=row['opp'], map=j['mapName'], cells=row['cells'], seat='AB'[own],
                res=row['result'], how=row['how'], last=row['last'], qd=qd, qalive=q['qalive'], qlen=q['qlen'],
                eats100=e, eatall=eall, n100=[s100[0][0], s100[1][0]] if s100 else None,
                tot100=[s100[0][1], s100[1][1]] if s100 else None,
                timeouts=h['acts'][0].get('timeout', 0), noact=h['acts'][0].get('none', 0),
                collapse=[c for c in h['collapse'] if c[1]], eqfin=h['eqfin'], done=j.get('completedAt'), ranked=bool(j.get('ranked')))


def cause(g):
    d = g['qd']
    if not d:
        return 'queen alive L%s' % g['qlen']
    if d['reason'] == 3:
        c = 'OWN-TURN HEADON' if d['own_turn'] else 'rammed'
    elif d['reason'] == 2:
        c = 'body(%s)' % (d['hit'][0] if d.get('hit') else '?')
        if d.get('hit') and d['hit'][0] == 'mate':
            c = 'mate'
    else:
        c = RS.get(d['reason'], str(d['reason']))
    return 'queen died r%d L%d %s%s free %s' % (d['r'], d['L'], c, '' if d['reason'] == 3 else (' own turn' if d['own_turn'] else ' not own turn'), d['f1'])


def broken(g):
    d = g['qd']
    return bool(d and g['cells'] <= 600 and d['r'] < 60 and d['reason'] in (0, 1) and d['f1'] == 0)


def line(g):
    odd = []
    if broken(g):
        odd.append('BROKEN-SIGN queen 0-free wall/own <r60 small map')
    if g['timeouts']:
        odd.append('TIMEOUTS %d' % g['timeouts'])
    if g['eatall'] == 0:
        odd.append('NEVER EATS')
    for c in g['collapse']:
        odd.append('COLLAPSE r%d from %d' % (c[0], c[2]))
    if g['qd'] and g['qd']['reason'] == 3 and g['qd']['own_turn']:
        odd.append('queen moved into enemy head')
    r1 = 'r100 pearls %d v %d, dragons %s' % (g['eats100'][0], g['eats100'][1], '%d v %d' % tuple(g['n100']) if g['n100'] else 'ended r%d' % g['last'])
    return '%d %s %-17s %-15s %4d %s %-4s by %-7s r%-3d | %s | %s | odd: %s' % (
        g['id'], g['ver'], (g['opp'] or '')[:17], g['map'][:15], g['cells'], g['seat'], g['res'].upper(), g['how'], g['last'],
        cause(g), r1, '; '.join(odd) or 'none')


def main():
    cp = HERE / 'cache.json'
    cache = json.loads(cp.read_text()) if cp.exists() else {}
    files = [('live', f) for f in sorted(glob.glob('data/online/live-one1/b*/game-*.json'))]
    for lab in ('one17-c1', 'one17-s1', 'one17-p1', 'one18-c1', 'one18-s1', 'one18-p1', 'one18-w1'):
        files += [(lab, f) for f in sorted(glob.glob('data/online/smoke/%s-old/game-*.json' % lab))]
    new = []
    for lab, f in files:
        gid = Path(f).stem.split('-')[1]
        if gid in cache:
            continue
        j = json.load(open(f))
        if 1119 not in (j['teamAId'], j['teamBId']) or j.get('status') != 'completed':
            continue
        if (j.get('completedAt') or '') < '2026-10-09T04:25':
            continue
        if not (Path(f).parent / ('M%d.replay' % j['id'])).exists():
            continue
        try:
            cache[gid] = one(lab, f, j)
            new.append(gid)
        except Exception as ex:
            print('ERR', lab, gid, repr(ex)[:200])
    cp.write_text(json.dumps(cache))
    G = [g for g in cache.values() if g.get('ver')]
    out = []
    for ver in ('one19', 'one18', 'one17'):
        gs = sorted((g for g in G if g['ver'] == ver), key=lambda g: g['id'])
        out.append('## %s: %d games, %d wins' % (ver, len(gs), sum(1 for g in gs if g['res'] == 'win')))
        out += [line(g) for g in gs]
        out.append('')
    out.append('## counts per version')
    out.append('ver    n  win loss | q dead  own-turn(0 free)  own-turn headon | small<=600: n  BROKEN-sign  qdead<r60 | timeouts never-eat collapse | losses with own-turn 0-free death')
    for ver in ('one17', 'one18', 'one19'):
        gs = [g for g in G if g['ver'] == ver]
        sm = [g for g in gs if g['cells'] <= 600]
        ls = [g for g in gs if g['res'] != 'win']
        z = lambda g: bool(g['qd'] and g['qd']['own_turn'] and g['qd']['reason'] != 3 and g['qd']['f1'] == 0)
        out.append('%-6s %2d %4d %4d | %6d %17d %16d | %13d %12d %10d | %8d %9d %8d | %d of %d' % (
            ver, len(gs), sum(1 for g in gs if g['res'] == 'win'), len(ls), sum(1 for g in gs if g['qd']), sum(1 for g in gs if z(g)),
            sum(1 for g in gs if g['qd'] and g['qd']['reason'] == 3 and g['qd']['own_turn']),
            len(sm), sum(1 for g in sm if broken(g)), sum(1 for g in sm if g['qd'] and g['qd']['r'] < 60),
            sum(1 for g in gs if g['timeouts']), sum(1 for g in gs if g['eatall'] == 0), sum(1 for g in gs if g['collapse']),
            sum(1 for g in ls if z(g)), len(ls)))
    out.append('')
    out.append('## maps of 600 cells or fewer: mean pearls before r100 (us v them) and dragons at r100 (us v them), games that reached r100 for dragons')
    by = defaultdict(lambda: defaultdict(list))
    for g in G:
        if g['cells'] <= 600:
            by[g['map']][g['ver']].append(g)
    for m in sorted(by):
        cells = []
        for ver in ('one17', 'one18', 'one19'):
            gs = by[m].get(ver, [])
            if not gs:
                cells.append('%s -' % ver)
                continue
            r = [g for g in gs if g['n100']]
            cells.append('%s n%d w%d pearls %.1f v %.1f drag %s' % (
                ver, len(gs), sum(1 for g in gs if g['res'] == 'win'), sum(g['eats100'][0] for g in gs) / len(gs), sum(g['eats100'][1] for g in gs) / len(gs),
                ('%.1f v %.1f (n%d)' % (sum(g['n100'][0] for g in r) / len(r), sum(g['n100'][1] for g in r) / len(r), len(r))) if r else 'none reached'))
        out.append('%-15s %s' % (m[:15], ' | '.join(cells)))
    txt = '\n'.join(out)
    (HERE / 'lines.txt').write_text(txt + '\n')
    print(time.strftime('%H:%M:%S'), 'new', new)
    if '--all' in sys.argv:
        print(txt)
    else:
        for gid in new:
            if cache[gid].get('ver') == 'one19':
                print(line(cache[gid]))
        print('\n'.join(out[out.index('## counts per version'):]))


main()
