"""Scratch (diag-topqueen): prints the report's main table (markdown) from tq2_scan-, tq2_near-, tq2_def-/tq2_chase- and tq2_depth- files.
Usage: python3 tq2_md.py"""
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
SCAN = ['top3-0', 'top3-1', 't91-0', 't91-1', 't264-0', 't264-1', 't306-0', 't306-1', 't842-0', 't454-0', 't0-0', 't0-1', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2']
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)
COLS = ['f454', 'f70', 'f306', 'f157', 'o306', 'o91', 'o264', 'B7Q', 'L1', 'MAIN']
HEAD = ['aAah 454', 'chad gdp 70', 'Cutlery 306', 'larp 157', 'Cutlery 306, to 5 Oct', 'SSS 91, to 5 Oct', '264, to 5 Oct', 'ours B7Q v Bob, Quiz', 'ours B7Q v 157, 306', 'ours main v Bob, Quiz']


def arm_of(g, s):
    src = g['src']
    t = g['t'][s]
    if src == 'top3':
        return 'f%d' % t if t in NAMED else 'fopp'
    if src == 'top1':
        return 'o%d' % t if t in NAMED else 'oopp'
    lab = {'agg8-q1': 'B7Q', 'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'top-l1': 'L1', 'top-l2': 'L2'}[src]
    if s == 0:
        return lab
    return 'v%d' % t if lab in ('L1', 'L2') else 'x' + lab


def band(r):
    return 0 if r <= 50 else 1 if r <= 100 else 2 if r <= 300 else 3


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else -1


def P(a, b):
    return '%.0f' % (100.0 * a / b) if b else '-'


def R(a, b, k=1.0, f='%.1f'):
    return f % (k * a / b) if b else '-'


def lines(tag_list, prefixes):
    for tag in tag_list:
        for pre in prefixes:
            p = W / ('%s-%s.jsonl' % (pre, tag))
            if p.exists():
                with open(p) as fh:
                    for line in fh:
                        if line.strip():
                            yield json.loads(line)
                break


def main():
    C = defaultdict(Counter)
    L = defaultdict(lambda: defaultdict(list))
    PAT = defaultdict(Counter)
    for g in lines(SCAN, ['tq2_scan']):
        w, h = g['w'], g['h']
        Rr = min(8, (w + h) // 8)
        for s in (0, 1):
            a = arm_of(g, s)
            c = C[a]
            c['games'] += 1
            win = g['win']
            f = g['fate'][s]
            fo = g['fate'][1 - s]
            if win is not None:
                mine = win if s == 0 else 1 - win
                c['decided'] += 1
                c['won'] += mine
                k = 'st%d%d' % (int(f is None), int(fo is None))
                c[k] += 1
                c[k + 'w'] += mine
                c['dec_' + g['decided']] += 1
            for r in (50, 100, 150, 300):
                c['dead%d' % r] += int(f is not None and f['r'] <= r)
                sn = g['snaps'].get(str(r))
                if sn is not None and sn[s][0] > 0:
                    c['lenN%d' % r] += 1
                    c['lenS%d' % r] += sn[s][0]
                    c['ownN%d' % r] += sn[s][1]
            if f is None:
                c['alive_end'] += 1
                c['lenSend'] += g['final'][s][0]
            opens = g['scomp'][s] * 2 >= w * h
            for rec in g['recs'][s]:
                r, Lq = rec[0], rec[2]
                b = band(r)
                c['t%d' % b] += 1
                c['turns'] += 1
                if r <= 300:
                    c['t300'] += 1
                    c['lb%d' % (0 if Lq <= 2 else 1 if Lq == 3 else 2 if Lq == 4 else 3 if Lq <= 8 else 4)] += 1
                c['o3_%d' % b] += rec[4]
                c['o5_%d' % b] += rec[5]
                c['ate%d' % b] += rec[22]
                c['od'] += rec[39]
                c['ate'] += rec[22]
                if opens:
                    c['ot'] += 1
                    c['in' if rec[3] <= Rr else 'mid' if rec[3] <= Rr + 4 else 'far'] += 1
                if r in (25, 50, 100, 300):
                    c['dsN%d' % r] += 1
                    c['dsS%d' % r] += rec[3]
                if rec[27] > 0:
                    c['thr'] += 1
                    c['thr%d' % b] += 1
                    paid = max(0, rec[20] - (Lq + 3) // 4)
                    if rec[28] > 0:
                        k = 'split'
                    elif rec[41] > 0:
                        k = 'attack'
                    elif rec[20] >= 2 and paid > 0:
                        k = 'paid'
                    elif rec[20] >= 2:
                        k = 'free'
                    elif rec[25] > 0:
                        k = 'died'
                    elif rec[24] > rec[30]:
                        k = 'away'
                    elif rec[24] == rec[30]:
                        k = 'level'
                    else:
                        k = 'closer'
                    c['thr_' + k] += 1
                    c['thr_ram'] += rec[26]
            for sp in g['splits'][s]:
                c['splits'] += 1
                L[a]['splitround'].append(sp[0])
                PAT[a][(sp[1], sp[2])] += 1
                c['spl_to2'] += int(sp[2] == 2)
            if f is not None:
                L[a]['deathround'].append(f['r'])
                rs = f['reason']
                if rs == 3 and not f['own_move']:
                    c['d_ram'] += 1
                elif rs == 3:
                    c['d_head'] += 1
                else:
                    c['d_box'] += 1
                    c['d_box_free'] += int(g['recs'][s][-1][14] >= 1)
            c['rams'] += sum(1 for x in g['attacks'][s] if x[4])
            c['bodykills'] += len(g['bodykills'][s])
    N = defaultdict(Counter)
    for g in lines(SCAN, ['tq2_near']):
        for s in (0, 1):
            c = N[arm_of(g, s)]
            c['games'] += 1
            c['turns'] += sum(g['turns'][s])
            for r in g['recs'][s]:
                d = r[2]
                c['n' + ('a' if d <= 3 else 'b' if d <= 5 else 'c')] += 1
                if r[7] == 0 and not r[12] and r[6] <= 1:
                    c['s%d' % d] += 1
                    c['s%d_away' % d] += int(r[3] > d)
    E = defaultdict(Counter)
    for g in lines(SCAN, ['tq2_def', 'tq2_chase']):
        dby = defaultdict(list)
        for d in g['deaths']:
            dby[d[1]].append(d)
        for s in (0, 1):
            c = E[arm_of(g, s)]
            c['games'] += 1
            c['qturns'] += g['turns'][s]
            c['mate_moved'] += g['near'][s][0]
            c['enemy_moved'] += g['near'][s][1]
            f = g['fate'][s]
            q = g['queen'][s]
            eps = []
            cur = None
            for r in g['qturns'][s]:
                if cur is not None and r[0] == cur[-1][0] + 1:
                    cur.append(r)
                else:
                    cur = [r]
                    eps.append(cur)
            for ep in eps:
                n = len(ep)
                c['eps'] += 1
                c['epturns'] += n
                c['long'] += int(n >= 4)
                c['none5'] += int(ep[0][4] == 0)
                ram = f is not None and f[4] == ep[-1][0] and f[2] == 3 and not f[3]
                c['ram'] += int(ram)
                c['n8'] += int(n >= 8)
                c['n8ram'] += int(n >= 8 and ram)
                ids = set()
                for r in ep:
                    ids.update(r[2])
                mate = 0
                for i in ids:
                    for d in dby.get(i, ()):
                        if ep[0][1] <= d[0] <= ep[-1][1] + 1 and d[3] == 3 and d[5] >= 0 and d[5] != q and d[4] != i:
                            mate = 1
                c['mate'] += mate
    D = defaultdict(lambda: [[0, 0.0] for _ in range(4)])
    DN = Counter()
    for g in lines(['top3-0', 'top3-1', 't306-0', 't91-0', 't264-0', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2'], ['tq2_depth']):
        for s in (0, 1):
            a = arm_of(g, s)
            DN[a] += 1
            for b in range(4):
                D[a][b][0] += g['acc'][s][b][0]
                D[a][b][1] += g['acc'][s][b][1]

    def row(name, fn):
        print('| ' + name + ' | ' + ' | '.join(fn(a) for a in COLS) + ' |')

    print('| measure | ' + ' | '.join(HEAD) + ' |')
    print('|' + '---|' * (len(COLS) + 1))
    row('games; won (%)', lambda a: '%d; %s' % (C[a]['games'], P(C[a]['won'], C[a]['decided'])))
    row('queen alive at the end of r50 / r100 / r150 / r300 / game (%)', lambda a: ' / '.join(P(C[a]['games'] - C[a]['dead%d' % r], C[a]['games']) for r in (50, 100, 150, 300)) + ' / ' + P(C[a]['alive_end'], C[a]['games']))
    row('her mean length when alive at r50 / r100 / r150 / r300 / end', lambda a: ' / '.join(R(C[a]['lenS%d' % r], C[a]['lenN%d' % r]) for r in (50, 100, 150, 300)) + ' / ' + R(C[a]['lenSend'], C[a]['alive_end']))
    row('share of her turns r0-300 at length 2 / 3 / 4 / 5-8 / 9+ (%)', lambda a: ' / '.join(P(C[a]['lb%d' % k], C[a]['t300']) for k in range(5)))
    row('her splits a game; median round; leaving her 2 (%); commonest (before to after)', lambda a: '%s; r%d; %s; %s' % (R(C[a]['splits'], C[a]['games']), med(L[a]['splitround']), P(C[a]['spl_to2'], C[a]['splits']), ', '.join('%d to %d x%d' % (k[0], k[1], v) for k, v in PAT[a].most_common(2))))
    row('tiles from her start tile at r25 / r50 / r100 / r300', lambda a: ' / '.join(R(C[a]['dsS%d' % r], C[a]['dsN%d' % r]) for r in (25, 50, 100, 300)))
    row('open-start games: her turns inside R / R+1 to R+4 / beyond (%)', lambda a: ' / '.join(P(C[a][k], C[a]['ot']) for k in ('in', 'mid', 'far')))
    row('own heads within 3 tiles; within 5: r0-50 / r51-100 / r101-300', lambda a: ' / '.join(R(C[a]['o3_%d' % b], C[a]['t%d' % b], 1.0, '%.2f') for b in range(3)) + '; ' + ' / '.join(R(C[a]['o5_%d' % b], C[a]['t%d' % b]) for b in range(3)))
    row('depth rank among her side heads r0-50 / r51-100 / r101-300 (games)', lambda a: (' / '.join(R(D[a][b][1], D[a][b][0], 1.0, '%.2f') for b in range(3)) + ' (%d)' % DN[a]) if DN[a] else '-')
    row('enemy head within 3 steps per 100 of her turns: r0-50 / r51-100 / r101-300 / all (such turns)', lambda a: ' / '.join(R(C[a]['thr%d' % b], C[a]['t%d' % b], 100.0) for b in range(3)) + ' / ' + R(C[a]['thr'], C[a]['turns'], 100.0) + ' (%d)' % C[a]['thr'])
    row('then she steps away / level / closer / sprints free / sprints paid / splits / rams (%); rammed before her next turn (%)', lambda a: ' / '.join(P(C[a]['thr_' + k], C[a]['thr']) for k in ('away', 'level', 'closer', 'free', 'paid', 'split', 'attack')) + '; ' + R(C[a]['thr_ram'], C[a]['thr'], 100.0))
    row('nearest enemy head at 1-3 / 4-5 / 6-8 steps, per 100 turns; single steps that open the distance at 3 / 4 / 5 steps (%) [games]', lambda a: ' / '.join(R(N[a][k], N[a]['turns'], 100.0) for k in ('na', 'nb', 'nc')) + '; ' + ' / '.join(P(N[a]['s%d_away' % d], N[a]['s%d' % d]) for d in (3, 4, 5)) + ' [%d]' % N[a]['games'])
    row('close chases a game; per 100 of her turns; turns each; lasting 4+ turns (%) [games]', lambda a: '%s; %s; %s; %s [%d]' % (R(E[a]['eps'], E[a]['games'], 1.0, '%.2f'), R(E[a]['eps'], E[a]['qturns'], 100.0, '%.2f'), R(E[a]['epturns'], E[a]['eps'], 1.0, '%.1f'), P(E[a]['long'], E[a]['eps']), E[a]['games']))
    row('chases that start with no mate within 5 tiles (%); in which a mate rams a pursuer (%, n); that end in her being rammed (%)', lambda a: '%s; %s (%d of %d); %s' % (P(E[a]['none5'], E[a]['eps']), P(E[a]['mate'], E[a]['eps']), E[a]['mate'], E[a]['eps'], P(E[a]['ram'], E[a]['eps'])))
    row('chases of 8+ turns: n, ending in her being rammed', lambda a: '%d, %d' % (E[a]['n8'], E[a]['n8ram']))
    row('head-ons between a mate and an enemy within 5 tiles of her, per 1000 of her turns: mate moved / enemy moved (counts)', lambda a: '%s / %s (%d / %d)' % (R(E[a]['mate_moved'], E[a]['qturns'], 1000.0, '%.1f'), R(E[a]['enemy_moved'], E[a]['qturns'], 1000.0, '%.1f'), E[a]['mate_moved'], E[a]['enemy_moved']))
    row('pearls she eats per 100 turns r0-50 / r51-100 / r101-300 / r301+; a game; from her own side dead (%)', lambda a: ' / '.join(R(C[a]['ate%d' % b], C[a]['t%d' % b], 100.0) for b in range(4)) + '; ' + R(C[a]['ate'], C[a]['games']) + '; ' + P(C[a]['od'], C[a]['ate']))
    row('her deaths: rammed / boxed in on her own move (of which with a free tile) / ran into a head; median round', lambda a: '%d / %d (%d) / %d; r%d' % (C[a]['d_ram'], C[a]['d_box'], C[a]['d_box_free'], C[a]['d_head'], med(L[a]['deathround'])))
    row('she rams an enemy head, per 100 games; enemies dead on her body, per 100 games', lambda a: '%s; %s' % (R(C[a]['rams'], C[a]['games'], 100.0), R(C[a]['bodykills'], C[a]['games'], 100.0)))
    row('games (won): her alive, theirs dead / both dead / her dead, theirs alive / both alive; ended by wipe-out (%)', lambda a: ' / '.join('%d (%d)' % (C[a][k], C[a][k + 'w']) for k in ('st10', 'st00', 'st01', 'st11')) + '; ' + P(C[a]['dec_elimination'], C[a]['decided']))
    row('own dragons alive at r100 / r300 (her alive)', lambda a: '%s / %s' % (R(C[a]['ownN100'], C[a]['lenN100']), R(C[a]['ownN300'], C[a]['lenN300'])))
    print()
    print('their queens against our live build (v157, v306), same rows in short:')
    for a in ('v157', 'v306', 'xB7Q', 'xMAIN'):
        c = C[a]
        e = E[a]
        print(a, 'games', c['games'], 'alive r100/r150/end %', P(c['games'] - c['dead100'], c['games']), P(c['games'] - c['dead150'], c['games']), P(c['alive_end'], c['games']), 'within 3 steps per 100', R(c['thr'], c['turns'], 100.0),
              'chases/game', R(e['eps'], e['games'], 1.0, '%.2f'), 'per 100 turns', R(e['eps'], e['qturns'], 100.0, '%.2f'), 'turns', R(e['epturns'], e['eps']), 'mate-moved head-ons near her per 1000 turns', R(e['mate_moved'], e['qturns'], 1000.0), 'own heads within 5 r51-100/r101-300', R(c['o5_1'], c['t1']), R(c['o5_2'], c['t2']), 'len r100/r300/end', R(c['lenS100'], c['lenN100']), R(c['lenS300'], c['lenN300']), R(c['lenSend'], c['alive_end']), 'turns at 2/3 %', P(c['lb0'], c['t300']), P(c['lb1'], c['t300']), 'no mate %', P(e['none5'], e['eps']), 'mate rams', e['mate'], 'of', e['eps'], 'rammed', c['d_ram'], 'boxed', c['d_box'], 'head', c['d_head'])
    print()
    print('head to head (games, won by the first):')
    pairs = Counter()
    for g in lines(SCAN, ['tq2_scan']):
        if g['win'] is None:
            continue
        for s in (0, 1):
            k = (arm_of(g, s), arm_of(g, 1 - s))
            pairs[k + ('n',)] += 1
            pairs[k + ('w',)] += g['win'] if s == 0 else 1 - g['win']
    for k in sorted(pairs):
        if k[2] == 'n' and k[0] in ('f454', 'f70', 'f306', 'f157', 'o306', 'o91', 'o264') and pairs[k] >= 5:
            print(k[0], 'v', k[1], pairs[k], pairs[(k[0], k[1], 'w')])


main()
