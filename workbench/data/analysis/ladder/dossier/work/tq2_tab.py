"""Scratch (diag-topqueen): tables per arm from tq2_scan-*.jsonl. Usage: python3 tq2_tab.py [arm ...]
Arms: f<team> = fresh (top3) games of that team's queen, o<team> = older (top1) games, B7Q / MAIN / L1 / L2 = ours,
x<label> = our opponents' queens in those games, fopp / oopp = the other side in top-team games."""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
FILES = ['top3-0', 'top3-1', 't91-0', 't91-1', 't264-0', 't264-1', 't306-0', 't306-1', 't842-0', 't454-0', 't0-0', 't0-1', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2']
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)
BANDS = ((0, 50), (51, 100), (101, 300), (301, 999))


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
    if lab in ('L1', 'L2'):
        return 'v%d' % t
    return 'x' + lab


def band(r):
    for k, (a, b) in enumerate(BANDS):
        if a <= r <= b:
            return k
    return 3


def lbin(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 8 else 4


class Arm:
    def __init__(self):
        self.c = Counter()
        self.lists = defaultdict(list)
        self.pat = Counter()
        self.cause = Counter()

    def add(self, g, s):
        c = self.c
        c['games'] += 1
        win = g['win']
        if win is not None:
            c['decided'] += 1
            c['won'] += win if s == 0 else 1 - win
        f = g['fate'][s]
        if win is not None:
            k = 'st%d%d' % (int(f is None), int(g['fate'][1 - s] is None))
            c[k] += 1
            c[k + 'w'] += win if s == 0 else 1 - win
            c['dec_' + g['decided']] += 1
        for r in (50, 100, 150, 300):
            if f is not None and f['r'] <= r:
                c['dead%d' % r] += 1
            sn = g['snaps'].get(str(r))
            if sn is not None and sn[s][0] > 0:
                c['lenN%d' % r] += 1
                c['lenS%d' % r] += sn[s][0]
                c['isLong%d' % r] += int(sn[s][0] >= sn[s][2])
                c['ownN%d' % r] += sn[s][1]
        if f is None:
            c['alive_end'] += 1
            c['lenSend'] += g['final'][s][0]
            self.lists['endlen'].append(g['final'][s][0])
        w, h = g['w'], g['h']
        R = min(8, (w + h) // 8)
        opens = g['scomp'][s] * 2 >= w * h
        c['open_games'] += int(opens)
        recs = g['recs'][s]
        for rec in recs:
            r, L = rec[0], rec[2]
            b = band(r)
            c['t%d' % b] += 1
            c['turns'] += 1
            if r <= 300:
                c['lb%d' % lbin(L)] += 1
                c['t300'] += 1
            c['o3_%d' % b] += rec[4]
            c['o5_%d' % b] += rec[5]
            c['ate%d' % b] += rec[22]
            c['sp%d' % b] += rec[38]
            c['od%d' % b] += rec[39]
            c['ed%d' % b] += rec[40]
            c['Lsum%d' % b] += L
            c['ram%d' % b] += rec[26]
            c['own%d' % b] += int(rec[25] > 0)
            c['fx0_%d' % b] += int(rec[14] == 0)
            c['inr%d' % b] += int(rec[17] > 0)
            c['e5_%d' % b] += int(rec[31] > 0)
            c['kelp2_%d' % b] += int(rec[13] >= 2)
            if rec[16] >= 0:
                c['mnN%d' % b] += 1
                c['mn%d' % b] += rec[16]
            if opens:
                c['ot'] += 1
                d = rec[3]
                c['in' if d <= R else 'mid' if d <= R + 4 else 'far'] += 1
            if r in (25, 50, 100, 300):
                c['dsN%d' % r] += 1
                c['dsS%d' % r] += rec[3]
            if rec[27] > 0:
                c['thr'] += 1
                c['thr%d' % b] += 1
                Lk = 'L2' if L <= 2 else 'L3' if L == 3 else 'L4' if L == 4 else 'L5'
                c['thr' + Lk] += 1
                free = (L + 3) // 4
                paid = max(0, rec[20] - free)
                if rec[28] > 0:
                    k = 'split'
                elif rec[41] > 0:
                    k = 'attack'
                elif rec[20] >= 2 and paid > 0:
                    k = 'paid'
                    c['paidseg'] += paid
                elif rec[20] >= 2:
                    k = 'free'
                elif rec[25] > 0:
                    k = 'diedmove'
                elif rec[24] > rec[30]:
                    k = 'away'
                elif rec[24] == rec[30]:
                    k = 'level'
                else:
                    k = 'closer'
                c['thr_' + k] += 1
                c['thr' + Lk + '_' + k] += 1
                c['thr_ram'] += rec[26]
                c['thr' + Lk + '_ram'] += rec[26]
            else:
                free = (L + 3) // 4
                if rec[20] >= 2:
                    c['calm_sprint'] += 1
                    c['calm_paid'] += int(rec[20] > free)
        for sp in g['splits'][s]:
            c['splits'] += 1
            c['spl%d' % band(sp[0])] += 1
            self.lists['splitround'].append(sp[0])
            self.pat[(sp[1], sp[2])] += 1
            c['spl_to2'] += int(sp[2] == 2)
            c['spl_from4'] += int(sp[1] == 4)
            c['spl_keep5'] += int(sp[2] >= 5)
        if recs and g['splits'][s]:
            self.lists['firstsplit'].append(g['splits'][s][0][0])
        if f is not None:
            self.lists['deathround'].append(f['r'])
            self.lists['deathlen'].append(f['L'])
            rs = f['reason']
            if rs == 3 and not f['own_move']:
                k = 'rammed by a queen' if f.get('mqueen') else 'rammed'
                if f.get('mside') == s:
                    k = 'rammed by a mate'
            elif rs == 3:
                k = 'ran into a head'
            elif rs == 0:
                k = 'wall'
            elif rs == 1:
                k = 'own body'
            elif rs == 2:
                k = 'other body'
            else:
                k = ('unpaid sprint', 'illegal split', 'no action')[f['act']]
            self.cause[k] += 1
            self.cause[k + ' r<=30'] += int(f['r'] <= 30)
            if f['r'] <= 30:
                c['dead30'] += 1
        for a in g['attacks'][s]:
            if a[4]:
                c['rams'] += 1
                c['rams_q'] += a[3]
                self.lists['ramvictim'].append(a[2])
                self.lists['ramlen'].append(a[1])
        c['bodykills'] += len(g['bodykills'][s])


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else -1


def pct(a, b):
    return '%.0f' % (100.0 * a / b) if b else '-'


def per(a, b, k=100.0):
    return '%.1f' % (k * a / b) if b else '-'


def main():
    want = sys.argv[1:]
    arms = defaultdict(Arm)
    pairs = Counter()
    ngames = 0
    for tag in FILES:
        p = W / ('tq2_scan-%s.jsonl' % tag)
        if not p.exists():
            continue
        with open(p) as fh:
            for line in fh:
                if not line.strip():
                    continue
                g = json.loads(line)
                ngames += 1
                for s in (0, 1):
                    arms[arm_of(g, s)].add(g, s)
                if g['win'] is not None:
                    for s in (0, 1):
                        na, nb = arm_of(g, s), arm_of(g, 1 - s)
                        pairs[(na, nb, 'n')] += 1
                        pairs[(na, nb, 'w')] += g['win'] if s == 0 else 1 - g['win']
    order = [a for a in ('f454', 'f70', 'f306', 'f157', 'f91', 'f545', 'f19', 'fopp', 'o306', 'o91', 'o264', 'o842', 'o454', 'o70', 'o545', 'o19', 'o87', 'oopp', 'B7Q', 'MAIN', 'L1', 'L2',
                         'v157', 'v306', 'v454', 'v87', 'xB7Q', 'xMAIN') if a in arms and (not want or a in want)]
    print('games read', ngames)
    print('\n== A. games, wins, queen alive (not dead by the end of round r), mean length when alive')
    print('arm | games | won% | alive r50 r100 r150 r300 end (%) | len r50 r100 r150 r300 end | med end len | queen is her side longest r100 r300 (%) | own dragons r100 r300')
    for a in order:
        A = arms[a]
        c = A.c
        n = c['games']
        print(a, '|', n, '|', pct(c['won'], c['decided']), '|', ' '.join(pct(n - c['dead%d' % r], n) for r in (50, 100, 150, 300)), pct(c['alive_end'], n), '|',
              ' '.join(per(c['lenS%d' % r], c['lenN%d' % r], 1) for r in (50, 100, 150, 300)), per(c['lenSend'], c['alive_end'], 1), '|', med(A.lists['endlen']), '|',
              pct(c['isLong100'], c['lenN100']), pct(c['isLong300'], c['lenN300']), '|', per(c['ownN100'], c['lenN100'], 1), per(c['ownN300'], c['lenN300'], 1))
    print('\n== B. share of her turns r0-300 at length 2/3/4/5-8/9+ (%); mean length by band r0-50, 51-100, 101-300, 301+')
    for a in order:
        c = arms[a].c
        print(a, '|', '/'.join(pct(c['lb%d' % k], c['t300']) for k in range(5)), '|', ' '.join(per(c['Lsum%d' % b], c['t%d' % b], 1) for b in range(4)))
    print('\n== C. her splits: per game; by band per game; median round; median first; leaving her 2 (%); from 4 (%); keeping 5+ (%); commonest')
    for a in order:
        A = arms[a]
        c = A.c
        n = c['games']
        print(a, '|', per(c['splits'], n, 1), '|', ' '.join(per(c['spl%d' % b], n, 1) for b in range(4)), '|', med(A.lists['splitround']), med(A.lists['firstsplit']), '|',
              pct(c['spl_to2'], c['splits']), pct(c['spl_from4'], c['splits']), pct(c['spl_keep5'], c['splits']), '|',
              ', '.join('%d>%d x%d' % (k[0], k[1], v) for k, v in A.pat.most_common(5)))
    print('\n== D. tiles from start r25 r50 r100 r300; open-start share of turns inside R / R+1..R+4 / beyond; own heads within 3, 5 by band; mate nearer nearest enemy % (101-300)')
    for a in order:
        c = arms[a].c
        print(a, '|', ' '.join(per(c['dsS%d' % r], c['dsN%d' % r], 1) for r in (25, 50, 100, 300)), '|', '/'.join(pct(c[k], c['ot']) for k in ('in', 'mid', 'far')), '|',
              ' '.join(per(c['o3_%d' % b], c['t%d' % b], 1) for b in range(4)), '|', ' '.join(per(c['o5_%d' % b], c['t%d' % b], 1) for b in range(4)), '|', pct(c['mn2'], c['mnN2']))
    print('\n== E. enemy heads within 3 steps: per 100 turns by band, all; turns; then away/level/closer/free sprint/paid sprint/split/attack/died on move (%); segments per paid sprint; rammed before next turn %')
    for a in order:
        c = arms[a].c
        t = c['thr']
        print(a, '|', ' '.join(per(c['thr%d' % b], c['t%d' % b]) for b in range(4)), per(t, c['turns']), '|', t, '|',
              '/'.join(pct(c['thr_' + k], t) for k in ('away', 'level', 'closer', 'free', 'paid', 'split', 'attack', 'diedmove')), '|', per(c['paidseg'], c['thr_paid'], 1), '|', per(c['thr_ram'], t))
    print('\n== E2. same by her length (2 / 3 / 4 / 5+): turns; away+level / closer / free / paid / split / attack %; rammed %')
    for a in order:
        c = arms[a].c
        out = []
        for Lk in ('L2', 'L3', 'L4', 'L5'):
            t = c['thr' + Lk]
            out.append('%d: %s/%s/%s/%s/%s/%s; %s' % (t, pct(c['thr' + Lk + '_away'] + c['thr' + Lk + '_level'], t), pct(c['thr' + Lk + '_closer'], t), pct(c['thr' + Lk + '_free'], t),
                                                  pct(c['thr' + Lk + '_paid'], t), pct(c['thr' + Lk + '_split'], t), pct(c['thr' + Lk + '_attack'], t), per(c['thr' + Lk + '_ram'], t)))
        print(a, '|', ' | '.join(out))
    print('\n== F. pearls she eats per 100 turns by band; per game; origin all game spawn/own drop/enemy drop (%); calm sprints per 100 turns (paid share %)')
    for a in order:
        c = arms[a].c
        tot = sum(c['ate%d' % b] for b in range(4))
        print(a, '|', ' '.join(per(c['ate%d' % b], c['t%d' % b]) for b in range(4)), '|', per(tot, c['games'], 1), '|',
              '/'.join(pct(sum(c[k + str(b)] for b in range(4)), tot) for k in ('sp', 'od', 'ed')), '| late 301+:',
              '/'.join(pct(c[k + '3'], c['ate3']) for k in ('sp', 'od', 'ed')), '|', per(c['calm_sprint'], c['turns'] - c['thr']), pct(c['calm_paid'], c['calm_sprint']))
    print('\n== G. how she dies: deaths; by r30; median round; median length; causes (count, of which by r30)')
    for a in order:
        A = arms[a]
        c = A.c
        d = c['games'] - c['alive_end']
        ks = [k for k in A.cause if not k.endswith('r<=30')]
        ks.sort(key=lambda k: -A.cause[k])
        print(a, '|', d, '|', c['dead30'], '|', med(A.lists['deathround']), med(A.lists['deathlen']), '|', ', '.join('%s %d (%d)' % (k, A.cause[k], A.cause[k + ' r<=30']) for k in ks))
    print('\n== H. she rams an enemy head: count, per 100 games, victim a queen, median victim length, her median length; enemies dead on her body per 100 games')
    for a in order:
        A = arms[a]
        c = A.c
        print(a, '|', c['rams'], per(c['rams'], c['games']), c['rams_q'], med(A.lists['ramvictim']), med(A.lists['ramlen']), '|', per(c['bodykills'], c['games']))
    print('\n== K. per 1000 of her turns by band (r0-50, 51-100, 101-300, 301+): rammed | died on her own move | no free tile beside her head | per 100: an enemy (not queen) can reach her head this turn | enemy head within 5 steps | on a tile with kelp on 2+ sides')
    for a in order:
        c = arms[a].c
        print(a, '|', ' '.join(per(c['ram%d' % b], c['t%d' % b], 1000) for b in range(4)), '|', ' '.join(per(c['own%d' % b], c['t%d' % b], 1000) for b in range(4)), '|',
              ' '.join(per(c['fx0_%d' % b], c['t%d' % b], 1000) for b in range(4)), '|', ' '.join(per(c['inr%d' % b], c['t%d' % b]) for b in range(4)), '|',
              ' '.join(per(c['e5_%d' % b], c['t%d' % b]) for b in range(4)), '|', ' '.join(per(c['kelp2_%d' % b], c['t%d' % b]) for b in range(4)))
    print('\n== I. head to head: arm v arm: games, won by the first')
    for k in sorted(pairs):
        if k[2] == 'n' and k[0] in order and pairs[k] >= 5:
            print(k[0], 'v', k[1], pairs[k], pairs[(k[0], k[1], 'w')])
    print('\n== J. games (won) by queens at the end: own alive+theirs alive | own alive+theirs dead | own dead+theirs alive | both dead ; decided by queen/longest/total/elimination')
    for a in order:
        c = arms[a].c
        print(a, '|', ' | '.join('%d (%d)' % (c[k], c[k + 'w']) for k in ('st11', 'st10', 'st01', 'st00')), ';', '/'.join(str(c['dec_' + k]) for k in ('queen', 'longest', 'total', 'elimination')))


main()
