# Scratch (diag-topopen): tables from to_scan-*.jsonl. Usage: python3 to_agg.py <mode> [args]
# modes: inv | curve | x15 | mech | deaths | layout
import sys, json
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

W = Path('data/analysis/ladder/dossier/work')
ROUNDS = (10, 20, 30, 40, 60, 80, 100, 150, 200, 300)
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse', 1119: 'ours'}


def size(c):
    return 'S' if c <= 700 else 'M' if c <= 1200 else 'L'


def load():
    recs, seen = [], set()
    for f in sorted(W.glob('to_scan-*.jsonl')):
        if 'test' in f.name:
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            g = json.loads(line)
            if 'error' in g or g['game'] in seen:
                continue
            seen.add(g['game'])
            recs.append(g)
    return recs


def sides(recs):
    # one row per (game, side) with a group label
    out = []
    for g in recs:
        src = g['src'][:2]
        for s in 'ut':
            d = g['sides'][s]
            team = d['team']
            if src == 'T3':
                lab = NAMES.get(team, None)
                lab = (lab + ' today') if lab and team != 1119 else None
                if lab is None:
                    lab = 'T3 opp'
            elif src == 'T1':
                lab = NAMES.get(team, None) if s == 'u' else None
                lab = (lab + ' old') if lab else 'T1 opp'
            elif src == 'OQ':
                lab = 'ours B7Q' if s == 'u' else 'our opp today'
            elif src == 'OM':
                lab = 'ours main' if s == 'u' else 'our opp today'
            elif src == 'OB':
                lab = 'ours B7' if s == 'u' else 'our opp today'
            elif src == 'OT':
                lab = 'ours vs top' if s == 'u' else (NAMES.get(team, 'top') + ' vs us')
            else:
                lab = 'ours ladder' if s == 'u' else 'ladder opp'
            out.append(dict(lab=lab, g=g, d=d, o=g['sides']['t' if s == 'u' else 'u'], size=size(g['cells']), lay='%s %dx%d k%d' % (g['map'].split(' #')[0], g['w'], g['h'], g['walls'])))
    return out


def groups(rows, labs):
    return {l: [r for r in rows if r['lab'] in ((l,) if isinstance(l, str) else l)] for l in labs}


TOP = ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'Cutlery old', 'SSS old', 'ftm old', 'horse old', 'aAah old']
OURS = ['ours B7Q', 'ours main', 'ours B7', 'ours vs top', 'larp vs us', 'Cutlery vs us', 'aAah vs us', 'top vs us', 'ours ladder']


def ours_today(rows):
    return [r for r in rows if r['lab'] in ('ours B7Q', 'ours main', 'ours B7')]


def at(r, name, rd):
    v = r['d']['series'][name]
    return v[rd] if len(v) > rd else None


def col(rs, name, rd):
    v = [at(r, name, rd) for r in rs]
    v = [x for x in v if x is not None]
    return (mean(v), len(v)) if v else (None, 0)


def fm(x, nd=1):
    return '-' if x is None else ('%.' + str(nd) + 'f') % x


def inv(rows):
    c = Counter((r['lab'], r['size']) for r in rows)
    labs = sorted({r['lab'] for r in rows})
    for l in labs:
        print('%-16s S %4d  M %4d  L %4d' % (l, c[l, 'S'], c[l, 'M'], c[l, 'L']))
    lays = defaultdict(Counter)
    for r in rows:
        lays[r['size'], r['lay']][r['lab']] += 1
    for k in sorted(lays):
        print(k, 'cells', dict(lays[k]))


def curve(rows, sz, labs, names=('alive', 'total', 'longest', 'eaten', 'nat', 'splits', 'deaths', 'ql')):
    print('== size', sz)
    for name in names:
        print('--', name)
        for l in labs:
            rs = [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]
            if not rs:
                continue
            cells = []
            for rd in ROUNDS:
                m, n = col(rs, name, rd)
                cells.append(fm(m))
            n100 = col(rs, name, 100)[1]
            n300 = col(rs, name, 300)[1]
            print('%-15s n=%3d/%3d/%3d  %s' % (l, len(rs), n100, n300, '  '.join('%6s' % c for c in cells)))


def layout_matched(rows, a_labs, b_labs, name, rds=ROUNDS, sz=None):
    # mean over layouts present on both sides (equal weight) of the per-layout means
    A = defaultdict(list)
    B = defaultdict(list)
    for r in rows:
        if sz and r['size'] != sz:
            continue
        if r['lab'] in a_labs:
            A[r['lay']].append(r)
        if r['lab'] in b_labs:
            B[r['lay']].append(r)
    common = sorted(set(A) | set()) if False else sorted(k for k in A if k in B)
    res = []
    for rd in rds:
        xs, ys = [], []
        for k in common:
            ma, na = col(A[k], name, rd)
            mb, nb = col(B[k], name, rd)
            if ma is not None and mb is not None:
                xs.append(ma)
                ys.append(mb)
        res.append((mean(xs) if xs else None, mean(ys) if ys else None, len(xs)))
    return common, res


def x15(rows, ours_labs):
    for sz in 'SML':
        ob = [r for r in rows if r['lab'] in ours_labs and r['size'] == sz]
        print('== size', sz, 'ours n', len(ob))
        for l in TOP:
            rs = [r for r in rows if r['lab'] == l and r['size'] == sz]
            if len(rs) < 3:
                continue
            line = []
            for name in ('alive', 'total', 'longest', 'eaten'):
                first = None
                streak = 0
                ratios = {}
                for rd in range(1, 301):
                    ma, na = col(rs, name, rd)
                    mb, nb = col(ob, name, rd)
                    if ma is None or mb is None or mb == 0 or na < 3 or nb < 3:
                        streak = 0
                        continue
                    q = ma / mb
                    if rd in (20, 40, 60, 100, 200, 300):
                        ratios[rd] = q
                    if q >= 1.5:
                        streak += 1
                        if streak >= 5 and first is None:
                            first = rd - 4
                    else:
                        streak = 0
                line.append('%s 1.5x@%s [%s]' % (name, first, ' '.join('%d:%.2f' % (k, v) for k, v in ratios.items())))
            print('%-15s n=%3d  %s' % (l, len(rs), ' | '.join(line)))
            # layout matched
            line = []
            for name in ('alive', 'total'):
                common, res = layout_matched(rows, (l,), ours_labs, name, rds=(20, 40, 60, 100, 200, 300), sz=sz)
                line.append('%s matched(%d lay) %s' % (name, len(common), ' '.join('%s/%s' % (fm(a), fm(c)) for a, c, n in res)))
            print('                ', ' | '.join(line))


def tsum(rs, pred):
    tot = [0] * 13
    for r in rs:
        for k, v in r['d']['turns'].items():
            w, lb, ctx, q = k.split('|')
            if pred(int(w), lb, ctx, int(q)):
                for i in range(13):
                    tot[i] += v[i]
    return tot


def pct(a, b, nd=1):
    return '-' if not b else ('%.' + str(nd) + 'f') % (100.0 * a / b)


def mech(rows, labs, sz):
    print('==== mechanics, size', sz)
    for l in labs:
        rs = [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]
        if len(rs) < 3:
            continue
        n = len(rs)
        print('##', l, 'games', n)
        # splits r0-60
        sp = [s for r in rs for s in r['d']['splits'] if s[0] <= 60]
        if sp:
            pl = Counter(min(s[1], 9) for s in sp)
            cl = Counter(min(s[2], 5) for s in sp)
            ctx = Counter(s[4][:2] if s[4][0] == 'P' else s[4] for s in sp)
            print('  splits r0-60 per game %.1f; parent len 4:%s 5:%s 6-7:%s 8+:%s mean %.2f; child len 2:%s 3:%s 4+:%s mean %.2f; pearl in view %s%% enemy %s%% nothing %s%%; queen share %s%%' % (
                len(sp) / n, pct(pl[4], len(sp)), pct(pl[5], len(sp)), pct(pl[6] + pl[7], len(sp)), pct(pl[8] + pl[9], len(sp)), mean(s[1] for s in sp),
                pct(cl[2], len(sp)), pct(cl[3], len(sp)), pct(cl[4] + cl[5], len(sp)), mean(s[2] for s in sp),
                pct(ctx['P1'] + ctx['P2'] + ctx['P3'], len(sp)), pct(ctx['E'], len(sp)), pct(ctx['N'], len(sp)), pct(sum(s[3] for s in sp), len(sp))))
            sp0 = [s for r in rs for s in r['d']['splits'] if s[0] <= 20]
            print('  splits r0-20 per game %.2f; first split round median %s; share of games with a split in r0: %s%%' % (
                len(sp0) / n, median([r['d']['splits'][0][0] for r in rs if r['d']['splits']] or [0]),
                pct(sum(1 for r in rs if r['d']['splits'] and r['d']['splits'][0][0] == 0), n)))
        # split turns as a share of turns at length >= 4 (r0-60)
        t4 = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb in ('4', '5', '9'))
        t4x = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb == '4')
        t5 = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb == '5')
        t9 = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb == '9')
        print('  turns r0-60 at length 4: %d, split on %s%%; at 5-8: %d, split %s%%; at 9+: %d, split %s%%' % (
            t4x[0], pct(t4x[1], t4x[0]), t5[0], pct(t5[1], t5[0]), t9[0], pct(t9[1], t9[0])))
        # children born r1-40
        ch = [d for r in rs for d in r['d']['dragons'] if 1 <= d[0] <= 40]
        if ch:
            fed10 = sum(1 for d in ch if d[2] is not None and d[2] - d[0] <= 10)
            fed20 = sum(1 for d in ch if d[2] is not None and d[2] - d[0] <= 20)
            dead10 = sum(1 for d in ch if d[3] is not None and d[3] - d[0] <= 10)
            dead20 = sum(1 for d in ch if d[3] is not None and d[3] - d[0] <= 20)
            waits = sorted((d[2] - d[0]) if d[2] is not None else 999 for d in ch)
            d5 = [d[9] for d in ch if d[9] is not None and d[9] < 9999]
            d10 = [d[10] for d in ch if d[10] is not None and d[10] < 9999]
            pd5 = [d[11] for d in ch if d[11] is not None and d[11] < 9999]
            l10 = [d[12] for d in ch if d[12] is not None]
            l20 = [d[13] for d in ch if d[13] is not None]
            resplit = [d[8] - d[0] for d in ch if d[8] is not None]
            print('  children born r1-40: %.1f a game; first pearl within 10 rounds %s%%, 20 rounds %s%%, median wait %s; dead within 10 %s%%, 20 %s%%' % (
                len(ch) / n, pct(fed10, len(ch)), pct(fed20, len(ch)), waits[len(waits) // 2], pct(dead10, len(ch)), pct(dead20, len(ch))))
            print('    path steps from birth tile at +5: %s, +10: %s; from parent head at +5: %s; length at +10: %s, +20: %s (of those alive); own first split after %s rounds (median, %s%% of children)' % (
                fm(mean(d5)) if d5 else '-', fm(mean(d10)) if d10 else '-', fm(mean(pd5)) if pd5 else '-', fm(mean(l10), 2) if l10 else '-', fm(mean(l20), 2) if l20 else '-',
                median(resplit) if resplit else '-', pct(len(resplit), len(ch))))
        # starters
        st = [d for r in rs for d in r['d']['dragons'] if d[0] == 0]
        if st:
            f10 = sum(1 for d in st if d[2] is not None and d[2] <= 10)
            f20 = sum(1 for d in st if d[2] is not None and d[2] <= 20)
            print('  starters %.1f a game: fed by r10 %s%%, by r20 %s%%' % (len(st) / n, pct(f10, len(st)), pct(f20, len(st))))
        # spread, seen
        for rd in (10, 20, 30, 40, 60):
            pass
        nn = []
        for rd in (10, 20, 30, 40, 60, 100):
            v = [r['d']['samp'][str(rd)]['nn'] for r in rs if str(rd) in r['d']['samp'] and r['d']['samp'][str(rd)]['nn'] >= 0]
            nn.append('%d:%s' % (rd, fm(mean(v)) if v else '-'))
        sn = []
        for rd in (10, 20, 30, 40, 60, 100):
            v = [100.0 * r['d']['samp'][str(rd)]['seen'] / r['g']['cells'] for r in rs if str(rd) in r['d']['samp']]
            sn.append('%d:%s' % (rd, fm(mean(v)) if v else '-'))
        print('  nearest mate (wrapped tiles) ' + ' '.join(nn) + ' ; board seen % ' + ' '.join(sn))
        # portals
        pr = [r for r in rs if r['g']['pairs'] > 0]
        if pr:
            by = lambda rd: sum(1 for r in pr if r['d']['pfirst'] is not None and r['d']['pfirst'] <= rd)
            ps = []
            for rd in (20, 40, 60, 100):
                v = [r['d']['samp'][str(rd)]['pstep'] for r in pr if str(rd) in r['d']['samp']]
                u = [r['d']['samp'][str(rd)]['pusers'] for r in pr if str(rd) in r['d']['samp']]
                ps.append('%d:%s steps/%s dragons' % (rd, fm(mean(v)) if v else '-', fm(mean(u)) if u else '-'))
            pf = [r['d']['pfirst'] for r in pr if r['d']['pfirst'] is not None]
            print('  portal layouts %d games: first portal step by r10 %s%%, r20 %s%%, r40 %s%%, r60 %s%%; median first round %s; %s' % (
                len(pr), pct(by(10), len(pr)), pct(by(20), len(pr)), pct(by(40), len(pr)), pct(by(60), len(pr)), median(pf) if pf else '-', ' '.join(ps)))
        # sprints r0-60
        for lbs, nm in ((('2', '3', '4'), 'len<=4'), (('5',), 'len5-8'), (('9',), 'len9+')):
            t = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb in lbs)
            if not t[2]:
                continue
            p2 = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb in lbs and ctx == 'P2')
            p1 = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb in lbs and ctx == 'P1')
            nn_ = tsum(rs, lambda w, lb, ctx, q: w <= 3 and lb in lbs and ctx == 'N')
            print('  sprint r0-60 %s: move turns %d (%.0f a game); 2+ steps per 100: %s; paid turns per 100: %s (%.2f a game), paid steps a game %.2f; paid turns that ate %s%%; free extra used %s%% of %d on offer' % (
                nm, t[2], t[2] / n, pct(t[4], t[2], 2), pct(t[6], t[2], 2), t[6] / n, t[5] / n, pct(t[10], t[6]), pct(t[7], t[8]), t[8]))
            print('     pearl 1 step away: %d turns, pearls eaten that turn per 100: %s; pearl 2 steps away: %d turns, eaten that turn per 100: %s, paid turns %s%%, 2+ steps %s%%; nothing in view: paid per 100 %s' % (
                p1[0], pct(p1[9], p1[0]), p2[0], pct(p2[9], p2[0]), pct(p2[6], p2[0]), pct(p2[4], p2[0]), pct(nn_[6], nn_[2], 2)))
        pd = [p for r in rs for p in r['d']['paid'] if p[0] <= 60]
        if pd:
            cx = Counter(p[5] for p in pd)
            print('  paid turns r0-60: %d (%.2f a game); context %s; ate %s%%; died that turn %s%%; by length %s; queen %s%%' % (
                len(pd), len(pd) / n, dict(cx.most_common(8)), pct(sum(1 for p in pd if p[4] > 0), len(pd)), pct(sum(p[6] for p in pd), len(pd)),
                dict(sorted(Counter(min(p[1], 9) for p in pd).items())), pct(sum(p[7] for p in pd), len(pd))))
        # deaths r0-60
        dl = [d for r in rs for d in r['d']['deaths'] if d[0] <= 60]
        cz = Counter(d[2] for d in dl)
        lz = Counter('2' if d[1] <= 2 else '3' if d[1] == 3 else '4+' for d in dl)
        print('  deaths r0-60 a game %.2f: %s; by length %s; queen deaths per game %.3f' % (
            len(dl) / n, ' '.join('%s %.2f' % (k, v / n) for k, v in cz.most_common()), ' '.join('%s %.2f' % (k, v / n) for k, v in sorted(lz.items())),
            sum(d[4] for d in dl) / n))
        dl2 = [d for r in rs for d in r['d']['deaths'] if d[0] <= 20]
        print('  deaths r0-20 a game %.2f: %s' % (len(dl2) / n, ' '.join('%s %.2f' % (k, v / n) for k, v in Counter(d[2] for d in dl2).most_common())))
        # natural pearl share
        for rd in (60, 100, 300):
            v = [(at(r, 'nat', rd), r['d']['samp'][str(rd)]['born']) for r in rs if str(rd) in r['d']['samp'] and at(r, 'nat', rd) is not None]
            if v:
                print('  natural pearls by r%d: eaten %.1f of %.1f born (%s%%), per 1000 cells born %.1f' % (
                    rd, mean(a for a, c in v), mean(c for a, c in v), pct(sum(a for a, c in v), sum(c for a, c in v)),
                    mean(1000.0 * r['d']['samp'][str(rd)]['born'] / r['g']['cells'] for r in rs if str(rd) in r['d']['samp'])))
        print('  won %s%% of %d' % (pct(sum(1 for r in rs if r['d']['won']), n), n))


def deaths(rows, labs, sz):
    for l in labs:
        rs = [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]
        if len(rs) < 3:
            continue
        print('##', l, sz, len(rs))
        for rd in ROUNDS:
            v = [r['d']['samp'][str(rd)]['dc'] for r in rs if str(rd) in r['d']['samp']]
            if not v:
                continue
            tot = Counter()
            for c in v:
                tot.update(c)
            print('  r%-3d n=%3d  %s' % (rd, len(v), ' '.join('%s %.1f' % (k, x / len(v)) for k, x in tot.most_common())))


def main():
    rows = sides(load())
    maps = [a[4:] for a in sys.argv if a.startswith('map=')]
    nomaps = [a[6:] for a in sys.argv if a.startswith('nomap=')]
    if maps:
        rows = [r for r in rows if any(r['g']['map'].startswith(m) for m in maps)]
    if nomaps:
        rows = [r for r in rows if not any(r['g']['map'].startswith(m) for m in nomaps)]
    sys.argv = [a for a in sys.argv if not a.startswith('map=') and not a.startswith('nomap=')]
    mode = sys.argv[1]
    if mode == 'inv':
        inv(rows)
    elif mode == 'curve':
        labs = TOP + OURS + ['our opp today', 'T3 opp', 'T1 opp', 'ladder opp']
        for sz in (sys.argv[2:] or ['S', 'M', 'L']):
            curve(rows, sz, labs)
    elif mode == 'x15':
        for r in rows:
            if r['lab'] in ('ours B7Q', 'ours main', 'ours B7'):
                r['lab2'] = 'ours today'
        print('#### against ours B7Q')
        x15(rows, ('ours B7Q',))
        print('#### against ours today (B7Q + B7 + main)')
        x15(rows, ('ours B7Q', 'ours main', 'ours B7'))
        print('#### against ours ladder')
        x15(rows, ('ours ladder',))
    elif mode == 'mech':
        labs = sys.argv[3:] or (TOP + OURS + ['our opp today', 'T3 opp'])
        if 'today' in labs:
            for r in rows:
                if r['lab'] in ('ours B7Q', 'ours main', 'ours B7'):
                    r['lab'] = 'ours today'
            labs = TOP + ['ours today', 'ours vs top', 'ours ladder', 'our opp today', 'T3 opp']
        mech(rows, labs, sys.argv[2] if len(sys.argv) > 2 else 'all')
    elif mode == 'deaths':
        labs = TOP + OURS
        for sz in (sys.argv[2:] or ['S', 'M', 'L']):
            deaths(rows, labs, sz)


main()
