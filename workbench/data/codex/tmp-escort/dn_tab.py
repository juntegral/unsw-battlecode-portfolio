"""esc_tab.py <baseline arm> <arm>... : the escort counts side by side on the games every listed arm has played (reads esc-<arm>.jsonl)."""
import sys
sys.dont_write_bytecode = True
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANDS = ((0, 50), (51, 100), (101, 300), (301, 500))


def band(r):
    return 0 if r <= 50 else 1 if r <= 100 else 2 if r <= 300 else 3


def chases(g):
    eps, cur = [], None
    for t in g['qturns']:
        if not t['ids']:
            continue
        if cur is not None and t['n'] == cur[-1]['n'] + 1:
            cur.append(t)
        else:
            cur = [t]
            eps.append(cur)
    return eps


def pairs(g):
    by = defaultdict(list)
    for d in g['deaths']:
        if d['reason'] == 3:
            by[(d['r'], d['mover'])].append(d)
    out = []
    for (r, mover), ds in by.items():
        ours = [d for d in ds if d['s'] == 0]
        theirs = [d for d in ds if d['s'] == 1]
        if len(ours) == 1 and len(theirs) == 1:
            out.append(dict(r=r, mover=mover, ours=ours[0], theirs=theirs[0]))
    return out


def measure(games):
    c = Counter()
    rows = []
    for g in games:
        q = g['queen'][0]
        c['games'] += 1
        c['win'] += int(g['win'] == 1)
        hp = pairs(g)
        for t in g['qturns']:
            b = band(t['r'])
            c['qt%d' % b] += 1
            c['qt'] += 1
            c['own3_%d' % b] += t['own3']
            c['own5_%d' % b] += t['own5']
            c['short5_%d' % b] += t['short5']
            c['thr%d' % b] += int(bool(t['ids']))
            c['thr'] += int(bool(t['ids']))
            c['mate_block'] += int(t['mate_block'] > 0)
            c['free'] += t['free']
            c['free1'] += int(t['free'] <= 1)
        stay = {}
        for t in g['qturns']:
            if t['r'] > 300:
                break
            c['qt300'] += 1
            near = set(m[0] for m in t['mates'] if m[3] <= 5 and m[1] <= 4)
            c['short1'] += int(len(near) >= 1)
            c['short2'] += int(len(near) >= 2)
            for i in list(stay):
                if i not in near:
                    c['stays'] += 1
                    c['stay_turns'] += stay.pop(i)
            for i in near:
                stay[i] = stay.get(i, 0) + 1
                if stay[i] == 10:
                    c['stay10'] += 1
        for i, v in stay.items():
            c['stays'] += 1
            c['stay_turns'] += v
        f = g['fate']
        for ep in chases(g):
            c['chases'] += 1
            c['chase_turns'] += len(ep)
            c['chase4'] += int(len(ep) >= 4)
            c['chase_nomate'] += int(ep[0]['own5'] == 0)
            ids = set(i for t in ep for i in t['ids'])
            hit = [p for p in hp if p['theirs']['id'] in ids and p['ours']['id'] != q and ep[0]['r'] <= p['r'] <= ep[-1]['r'] + 1]
            c['chase_materam'] += int(bool(hit))
            c['chase_materam_moved'] += int(any(p['mover'] == p['ours']['id'] for p in hit))
            ram = f is not None and f['kind'] == 'rammed' and f['qn'] == ep[-1]['n']
            c['chase_rammed'] += int(ram)
            for p in hit:
                rows.append((g['game'], 'mate %d (L%d) and pursuer %d (L%d) head-on r%d, mover %s, chase r%d-%d, queen at %s' % (
                    p['ours']['id'], p['ours']['L'], p['theirs']['id'], p['theirs']['L'], p['r'],
                    'mate' if p['mover'] == p['ours']['id'] else 'enemy', ep[0]['r'], ep[-1]['r'], xy(g, ep[-1]['head']))))
        for p in hp:
            if p['ours']['id'] != q and p['ours']['dq'] <= 5 and p['theirs']['id'] != g['queen'][1]:
                c['near_mate_moved' if p['mover'] == p['ours']['id'] else 'near_enemy_moved'] += 1
                c['near_our_len'] += p['ours']['L']
                c['near_their_len'] += p['theirs']['L']
                if p['mover'] == p['ours']['id']:
                    c['near_L%d' % min(p['ours']['L'], 5)] += 1
                    L0 = p['ours']['L0']
                    target = 'pursuer' if p['theirs']['qsteps'] <= 3 else 'radius'
                    c['dn_L%d_%s' % (min(L0, 5), target)] += 1
                    c['dn_pursuers'] += int(target == 'pursuer')
                    paid = p['ours']['moved'] - (L0 + 3) // 4
                    if L0 >= 5 and paid > 0:
                        c['dn_sprints'] += 1
                        c['dn_paid'] += paid
        for d in g['deaths']:
            if d['reason'] != 3 and d['s'] == 0 and d['id'] != q and d['dq'] <= 5 and d['r'] <= 300:
                c['mate_self'] += 1
                c['mate_self_short'] += int(d['L'] <= 4)
        for k in ('100', '150', 'end'):
            c['qalive_' + k] += int(g['snaps'][k]['queen'] > 0)
        for k in ('100', '300'):
            c['alive_' + k] += g['snaps'][k]['alive']
            c['total_' + k] += g['snaps'][k]['total']
            c['ealive_' + k] += g['snaps'][k]['ealive']
        c['qlen_end'] += g['snaps']['end']['queen']
        c['pearls'] += g['pearls'][0]
        for b in range(4):
            c['pearls%d' % b] += g['pearls_band'][b]
        c['life'] += f['r'] if f is not None else g['end']
        if f is not None:
            c['dead'] += 1
            c['dead_' + f['kind']] += 1
            if f['kind'] == 'boxed':
                c['boxed_nofree'] += int(f['free'] == 0)
                c['boxed_mate'] += int(f['mate_block'] > 0)
            rows.append((g['game'], 'queen dead r%d %s L%d free %d mate tiles %d own5 %d at %s' % (
                f['r'], f['kind'], f['L'], f['free'], f['mate_block'], f['own5'], xy(g, f['head']))))
    return c, rows


def xy(g, cell):
    return '(%d,%d)' % (cell % g['w'], cell // g['w'])


def main():
    arms = [a for a in sys.argv[1:] if not a.startswith('-') and not a.startswith(('cells', 'only='))]
    data = {}
    for a in arms:
        data[a] = {}
        for line in (HERE / ('dn-%s.jsonl' % a)).read_text().splitlines():
            if line.strip():
                g = json.loads(line)
                cells = g['w'] * g['h']
                if 'cells<=700' in sys.argv and cells > 700:
                    continue
                if 'cells>700' in sys.argv and cells <= 700:
                    continue
                only = next((x[5:] for x in sys.argv[1:] if x.startswith('only=')), None)
                if only is not None and g['game'] not in set(Path(only).read_text().split()):
                    continue
                data[a][g['game']] = g
    table = []
    common = sorted(set.intersection(*(set(data[a]) for a in arms)))
    for arm in arms:
        c, rows = measure([data[arm][k] for k in common])
        table.append((arm, c, rows))
    n = lambda c, k: c[k] / max(1, c['games'])

    def line(name, fn):
        print('| ' + name + ' | ' + ' | '.join(fn(c) for _, c, _ in table) + ' |')

    print('| measure | ' + ' | '.join(t[0] for t in table) + ' |')
    print('|---|' + '---|' * len(table))
    line('games; won', lambda c: '%d; %d' % (c['games'], c['win']))
    line('queen turns', lambda c: '%d' % c['qt'])
    line('own heads within 3 tiles r0-50 / r51-100 / r101-300', lambda c: ' / '.join('%.2f' % (c['own3_%d' % b] / max(1, c['qt%d' % b])) for b in range(3)))
    line('own heads within 5 tiles r0-50 / r51-100 / r101-300', lambda c: ' / '.join('%.2f' % (c['own5_%d' % b] / max(1, c['qt%d' % b])) for b in range(3)))
    line('own heads of 4 or less within 5 tiles, same bands', lambda c: ' / '.join('%.2f' % (c['short5_%d' % b] / max(1, c['qt%d' % b])) for b in range(3)))
    line('queen turns to r300 with 1+ / 2+ mates of 4 or less within 5 tiles (%)', lambda c: '%.0f / %.0f' % (100.0 * c['short1'] / max(1, c['qt300']), 100.0 * c['short2'] / max(1, c['qt300'])))
    line('stays of a short mate within 5 tiles: number; turns each; lasting 10+ turns', lambda c: '%d; %.1f; %d' % (c['stays'], c['stay_turns'] / max(1, c['stays']), c['stay10']))
    line('enemy head within 3 steps per 100 queen turns: r0-50 / r51-100 / r101-300 / all (turns)', lambda c: ' / '.join('%.1f' % (100.0 * c['thr%d' % b] / max(1, c['qt%d' % b])) for b in range(3)) + ' / %.1f (%d)' % (100.0 * c['thr'] / max(1, c['qt']), c['thr']))
    line('close chases; turns each; lasting 4+', lambda c: '%d; %.1f; %d' % (c['chases'], c['chase_turns'] / max(1, c['chases']), c['chase4']))
    line('chases that start with no mate within 5 tiles', lambda c: '%d of %d (%.0f%%)' % (c['chase_nomate'], c['chases'], 100.0 * c['chase_nomate'] / max(1, c['chases'])))
    line('chases in which a mate and a pursuer meet head-on (mate moved)', lambda c: '%d (%d) of %d' % (c['chase_materam'], c['chase_materam_moved'], c['chases']))
    line('chases that end in her being rammed', lambda c: '%d' % c['chase_rammed'])
    line('head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved', lambda c: '%d / %d' % (c['near_mate_moved'], c['near_enemy_moved']))
    line('those head-ons: length we lost / they lost; mate moved at length 2 / 3 / 4 / 5+', lambda c: '%d / %d; %d / %d / %d / %d' % (c['near_our_len'], c['near_their_len'], c['near_L2'], c['near_L3'], c['near_L4'], c['near_L5']))
    for length in (2, 3, 4, 5):
        line('mate moved, rammer L0 %s: target was a pursuer / target only in the radius' % ('5+' if length == 5 else length),
             lambda c, length=length: '%d / %d' % (c['dn_L%d_pursuer' % length], c['dn_L%d_radius' % length]))
    line('enemy moved (count)', lambda c: str(c['near_enemy_moved']))
    line('paid hunt sprints by a 5+: count; segments paid', lambda c: '%d; %d' % (c['dn_sprints'], c['dn_paid']))
    line('length lost by us / by them in those pairs', lambda c: '%d / %d' % (c['near_our_len'], c['near_their_len']))
    line('pursuers rammed by a mate', lambda c: str(c['dn_pursuers']))
    line('mates dead on their own move (kelp, body, no action) within 5 tiles of her, to r300: all; 4 long or less', lambda c: '%d; %d' % (c['mate_self'], c['mate_self_short']))
    line('queen alive at the end of r100 / r150 / game', lambda c: '%d / %d / %d' % (c['qalive_100'], c['qalive_150'], c['qalive_end']))
    line('rounds the queen lived, mean (alive at the end = last round)', lambda c: '%.0f' % n(c, 'life'))
    line('queen deaths: rammed / boxed in / ran into a head', lambda c: '%d / %d / %d' % (c['dead_rammed'], c['dead_boxed'], c['dead_into_head']))
    line('boxed-in deaths with a mate body on a neighbour tile of hers', lambda c: '%d of %d' % (c['boxed_mate'], c['dead_boxed']))
    line('queen turns with a mate body on a neighbour tile, per 100; with 0 or 1 free tile, per 100', lambda c: '%.1f; %.1f' % (100.0 * c['mate_block'] / max(1, c['qt']), 100.0 * c['free1'] / max(1, c['qt'])))
    line('own dragons at r100 / r300', lambda c: '%.1f / %.1f' % (n(c, 'alive_100'), n(c, 'alive_300')))
    line('own total length at r100 / r300', lambda c: '%.1f / %.1f' % (n(c, 'total_100'), n(c, 'total_300')))
    line('enemy dragons at r100 / r300', lambda c: '%.1f / %.1f' % (n(c, 'ealive_100'), n(c, 'ealive_300')))
    line('pearls eaten a game: all; r0-50 / r51-100 / r101-300', lambda c: '%.1f; %.1f / %.1f / %.1f' % (n(c, 'pearls'), n(c, 'pearls0'), n(c, 'pearls1'), n(c, 'pearls2')))
    line('queen length at the end (dead = 0)', lambda c: '%.1f' % n(c, 'qlen_end'))
    if '-rows' in sys.argv:
        for name, c, rows in table:
            print('\n' + name)
            for r in rows:
                print('  ', r[0], r[1])


if __name__ == '__main__':
    main()
