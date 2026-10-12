"""Scratch (diag-topaah): tables from ta_scan-*.jsonl. Pooled numerator / denominator per column.
Columns: a = 454 fresh, a0 = 454 to 5 Oct, l = 157 fresh, c0 = 306 to 5 Oct, c1 = 306 fresh, g = 70 fresh, g0 = 70 old,
q = ours B7Q, m = ours main, t = ours vs top teams.  C@a / C@l = c0 re-weighted to the layouts of a / l.
Usage: python3 ta_agg.py [side]   side 0 = the studied team (default), 1 = its opponents."""
import sys
import json
from collections import Counter, defaultdict
from statistics import median
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
COLS = ('a', 'a0', 'l', 'c0', 'c1', 'g', 'g0', 'q', 'm', 't')
FILES = dict(a=['a'], a0=['a0'], l=['l'], c0=['c0-0', 'c0-1', 'c0-2', 'c0-3'], c1=['c1'], g=['g'], g0=['g0'], q=['q'],
             m=['m'], t=['t'])
S = int(sys.argv[1]) if len(sys.argv) > 1 else 0
W0, W1, W2, ALL = (0,), (1,), (2,), (0, 1, 2)
NONHEAD = (2, 3, 4, 5, 6, 7, 8)


def load():
    data = {}
    for col in COLS:
        rows = []
        for tag in FILES[col]:
            p = Path(WORK + 'ta_scan-' + tag + '.jsonl')
            if p.exists():
                rows += [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        data[col] = rows
    return data


def c(g, key, wins=ALL, s=None):
    s = S if s is None else s
    return sum(g['cnt'][s][w].get(key, 0) for w in wins)


def co(g, key, wins=ALL):
    return sum(g['coh'][S][w].get(key, 0) for w in wins)


def dl(g, wins=ALL, s=None, f=None):
    s = S if s is None else s
    out = 0
    for d in g['deaths']:
        w = 0 if d[0] <= 100 else 1 if d[0] <= 300 else 2
        if d[1] == s and w in wins and (f is None or f(d)):
            out += 1
    return out


def sp(g, f=None):
    return [x for x in g['splits'] if x[1] == S and (f is None or f(x))]


def snap(g, mark, key):
    v = g['snaps'].get(str(mark))
    if v is None:
        return None
    return v[S].get(key)


RATES = []


def R(label, num, den, scale=1000.0):
    RATES.append((label, num, den, scale))


for wn, ws in (('0-100', W0), ('101-300', W1)):
    for cause in ('illegal split', 'wall', 'own body', 'another body', 'no action', 'head-on mover', 'head-on hit'):
        R('Death: %s /1k turns [%s]' % (cause, wn), lambda g, ws=ws, cause=cause: c(g, 'd_' + cause, ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Deaths not head-on, a free tile beside the head /1k [%s]' % wn, lambda g, ws=ws: dl(g, ws, f=lambda d: d[2] in NONHEAD and d[4] == 1), lambda g, ws=ws: c(g, 'turns', ws))
    R('Deaths not head-on, boxed in /1k [%s]' % wn, lambda g, ws=ws: dl(g, ws, f=lambda d: d[2] in NONHEAD and d[4] == 0), lambda g, ws=ws: c(g, 'turns', ws))
    R('Turn starts boxed in %% [%s]' % wn, lambda g, ws=ws: c(g, 'boxed', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Split frequency /1k [%s]' % wn, lambda g, ws=ws: c(g, 'splits', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Pearls eaten /1k [%s]' % wn, lambda g, ws=ws: c(g, 'eaten', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Net length (pearls - length lost) /1k [%s]' % wn, lambda g, ws=ws: c(g, 'eaten', ws) - c(g, 'len_lost', ws) - c(g, 'sprint_paid', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Same-team head-on /1k [%s]' % wn, lambda g, ws=ws: c(g, 'same_head_on', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Cross-team head-on involvement /1k [%s]' % wn, lambda g, ws=ws: c(g, 'cross_head_on', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Repeated-spawn tile nearby %% [%s]' % wn, lambda g, ws=ws: c(g, 'hot', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Blind turns %% [%s]' % wn, lambda g, ws=ws: c(g, 'no_view', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Blind direction kept %% [%s]' % wn, lambda g, ws=ws: c(g, 'keeps', ws), lambda g, ws=ws: c(g, 'keeps_eligible', ws), 100.0)
    R('Blind re-tread %% [%s]' % wn, lambda g, ws=ws: c(g, 'dither', ws), lambda g, ws=ws: c(g, 'nv_moved', ws), 100.0)
    R('Any re-tread (last 12 tiles) %% [%s]' % wn, lambda g, ws=ws: c(g, 'retread', ws), lambda g, ws=ws: c(g, 'moved', ws), 100.0)
    R('Adjacent pearl missed %% [%s]' % wn, lambda g, ws=ws: c(g, 'adj_missed', ws), lambda g, ws=ws: c(g, 'adj_turns', ws), 100.0)
    R('Birth-cohort harvest %% [%s]' % wn, lambda g, ws=ws: co(g, 'e_n', ws) + co(g, 'e_own', ws) + co(g, 'e_foe', ws), lambda g, ws=ws: co(g, 'b_n', ws) + co(g, 'b_own', ws) + co(g, 'b_foe', ws), 100.0)
    R('Natural birth-cohort harvest %% [%s]' % wn, lambda g, ws=ws: co(g, 'e_n', ws), lambda g, ws=ws: co(g, 'b_n', ws), 100.0)
    R('Own-dead cohort harvest %% [%s]' % wn, lambda g, ws=ws: co(g, 'e_own', ws), lambda g, ws=ws: co(g, 'b_own', ws), 100.0)
    R('Their-dead cohort harvest %% [%s]' % wn, lambda g, ws=ws: co(g, 'e_foe', ws), lambda g, ws=ws: co(g, 'b_foe', ws), 100.0)
    R('Birth-cohort wait until eaten (rounds) [%s]' % wn, lambda g, ws=ws: co(g, 'wait', ws), lambda g, ws=ws: co(g, 'wait_n', ws), 1.0)
    R('Sprint turns /1k [%s]' % wn, lambda g, ws=ws: c(g, 'sprint_turns', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Sprint segments paid /1k [%s]' % wn, lambda g, ws=ws: c(g, 'sprint_paid', ws), lambda g, ws=ws: c(g, 'turns', ws))
    R('Turns by dragons of 2 %% [%s]' % wn, lambda g, ws=ws: c(g, 'len2', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Turns by dragons of 3 %% [%s]' % wn, lambda g, ws=ws: c(g, 'len3', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Turns by dragons of 4-5 %% [%s]' % wn, lambda g, ws=ws: c(g, 'len4', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Turns by dragons of 6+ %% [%s]' % wn, lambda g, ws=ws: c(g, 'len6', ws) + c(g, 'len10', ws), lambda g, ws=ws: c(g, 'turns', ws), 100.0)
    R('Own dead eaten by a longer mate %% of own-dead eaten [%s]' % wn, lambda g, ws=ws: c(g, 'own_to_longer', ws), lambda g, ws=ws: c(g, 'eat_own', ws), 100.0)
    R('Own dead eaten by the longest %% of own-dead eaten [%s]' % wn, lambda g, ws=ws: c(g, 'own_to_longest', ws), lambda g, ws=ws: c(g, 'eat_own', ws), 100.0)
    R('Enemy dies on a body of ours /1k enemy turns [%s]' % wn, lambda g, ws=ws: dl(g, ws, s=1 - S, f=lambda d: d[2] == 4 and d[8] == S), lambda g, ws=ws: c(g, 'turns', ws, s=1 - S))
    R('Queen: turns inside R of start %% [%s]' % wn, lambda g, ws=ws: c(g, 'q_inR', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: turns beyond R+4 %% [%s]' % wn, lambda g, ws=ws: c(g, 'q_far', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: path distance from start (tiles) [%s]' % wn, lambda g, ws=ws: c(g, 'q_dist', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 1.0)
    R('Queen: own heads within 5 tiles (mean) [%s]' % wn, lambda g, ws=ws: c(g, 'q_guard', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 1.0)
    R('Queen: 2+ own heads within 5 %% [%s]' % wn, lambda g, ws=ws: c(g, 'q_guard2', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: enemy head within 5 %% [%s]' % wn, lambda g, ws=ws: c(g, 'q_enemy', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: mean length on her turns [%s]' % wn, lambda g, ws=ws: c(g, 'q_len', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 1.0)
    R('Queen: pearls eaten /100 queen turns [%s]' % wn, lambda g, ws=ws: c(g, 'q_eat', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: splits /100 queen turns [%s]' % wn, lambda g, ws=ws: c(g, 'q_split', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: sprints /100 queen turns [%s]' % wn, lambda g, ws=ws: c(g, 'q_sprint', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: portal steps /100 queen turns [%s]' % wn, lambda g, ws=ws: c(g, 'q_portal', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen: blind turns %% [%s]' % wn, lambda g, ws=ws: c(g, 'q_noview', ws), lambda g, ws=ws: c(g, 'q_turns', ws), 100.0)
    R('Queen dies in window %% [%s]' % wn, lambda g, ws=ws: dl(g, ws, f=lambda d: d[5] == 1), lambda g, ws=ws: int(g['last_round'] >= (100 if ws == W0 else 300) or dl(g, ws, f=lambda d: d[5] == 1) > 0) if (ws == W0 or dl(g, W0, f=lambda d: d[5] == 1) == 0) else 0, 100.0)
R('All deaths /1k [game]', lambda g: c(g, 'deaths'), lambda g: c(g, 'turns'))
R('Split frequency /1k [game]', lambda g: c(g, 'splits'), lambda g: c(g, 'turns'))
R('Splits per eaten pearl [game]', lambda g: c(g, 'splits'), lambda g: c(g, 'eaten'), 1.0)
R('Portal steps /1k [game]', lambda g: c(g, 'portal'), lambda g: c(g, 'turns'))
R('Pearls eaten /1k [game]', lambda g: c(g, 'eaten'), lambda g: c(g, 'turns'))
R('Net length /1k [game]', lambda g: c(g, 'eaten') - c(g, 'len_lost') - c(g, 'sprint_paid'), lambda g: c(g, 'turns'))
R('Sonar pings per turn [game]', lambda g: g['logs'][S].get('sonar', 0), lambda g: c(g, 'turns'), 1.0)
R('First contact round (games with contact)', lambda g: g['contact'][S] or 0, lambda g: int(g['contact'][S] is not None), 1.0)
R('Split: parent length (mean)', lambda g: sum(x[2] for x in sp(g)), lambda g: len(sp(g)), 1.0)
R('Split: parent of exactly 4 %', lambda g: len(sp(g, lambda x: x[2] == 4)), lambda g: len(sp(g)), 100.0)
R('Split: parent of 6+ %', lambda g: len(sp(g, lambda x: x[2] >= 6)), lambda g: len(sp(g)), 100.0)
R('Split: child of 2 %', lambda g: len(sp(g, lambda x: x[3] == 2)), lambda g: len(sp(g)), 100.0)
R('Split: by the queen %', lambda g: len(sp(g, lambda x: x[4] == 1)), lambda g: len(sp(g)), 100.0)
R('Round-0 split by 4-long starters %', lambda g: len(sp(g, lambda x: x[0] == 0 and x[2] == 4)), lambda g: sum(1 for x in g['starts'][S] if x[1] == 4), 100.0)
R('Queen splits in round 0 (4+ long queen) %', lambda g: len(sp(g, lambda x: x[0] == 0 and x[4] == 1)), lambda g: int(g['starts'][S][0][1] >= 4), 100.0)
R('Queen splits by round 100 (per game)', lambda g: c(g, 'q_split', W0), lambda g: 1, 1.0)
R('Rams started: mover length (mean)', lambda g: sum(x[2] for x in g['rams'] if x[1] == S and x[6]), lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6]), 1.0)
R('Rams started: target length (mean)', lambda g: sum(x[3] for x in g['rams'] if x[1] == S and x[6]), lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6]), 1.0)
R('Rams started on a longer head %', lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6] and x[3] > x[2]), lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6]), 100.0)
R('Rams started per game', lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6]), lambda g: 1, 1.0)
R('Rams started by round 100 per game', lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6] and x[0] <= 100), lambda g: 1, 1.0)
R('Enemy queen rammed by us (games %)', lambda g: sum(1 for x in g['rams'] if x[1] == S and x[6] and x[4]), lambda g: 1, 100.0)
R('Our queen rammed by them (games %)', lambda g: sum(1 for x in g['rams'] if x[1] != S and x[6] and x[4]), lambda g: 1, 100.0)
R('Our queen dies ramming (games %)', lambda g: sum(1 for x in g['rams'] if x[1] == S and x[5]), lambda g: 1, 100.0)
R('Queen dead at the end %', lambda g: int(g['final'][S]['ql'] == 0), lambda g: 1, 100.0)
R('Queen death: non-head-on with a free tile (games %)', lambda g: dl(g, f=lambda d: d[5] == 1 and d[2] in NONHEAD and d[4] == 1), lambda g: 1, 100.0)
R('Queen death: boxed in (games %)', lambda g: dl(g, f=lambda d: d[5] == 1 and d[2] in NONHEAD and d[4] == 0), lambda g: 1, 100.0)
R('Deaths at 56+ own dragons, not head-on /1k [game]', lambda g: dl(g, f=lambda d: d[6] >= 56 and d[2] in NONHEAD), lambda g: c(g, 'turns'))
R('Deaths not head-on beside a longer mate (4 tiles) %', lambda g: dl(g, f=lambda d: d[2] in NONHEAD and d[7] == 1), lambda g: dl(g, f=lambda d: d[2] in NONHEAD), 100.0)
R('Deaths not head-on: mean length', lambda g: sum(d[3] for d in g['deaths'] if d[1] == S and d[2] in NONHEAD), lambda g: dl(g, f=lambda d: d[2] in NONHEAD), 1.0)
R('Won %', lambda g: int(g['win'] == 1), lambda g: 1, 100.0)
R('Ended by elimination %', lambda g: int(g['end_reason'] == 0), lambda g: 1, 100.0)
R('Won by eliminating them (games %)', lambda g: int(g['win'] == 1 and g['end_reason'] == 0), lambda g: 1, 100.0)
R('Last round (mean)', lambda g: g['last_round'], lambda g: 1, 1.0)
R('Opponent rating (mean)', lambda g: g['opp_elo'] or 0, lambda g: int(bool(g['opp_elo'])), 1.0)
R('Queen tiles visited by round 150 (distinct)', lambda g: g['qtiles'][S], lambda g: 1, 1.0)
for mark in (25, 50, 100, 150, 200, 300):
    for key, name in (('alive', 'Dragons alive'), ('total', 'Total length'), ('longest', 'Longest dragon'), ('second', 'Second longest'),
                      ('n6', 'Dragons of 6+'), ('ql', 'Queen length (0 if dead)'), ('qg', 'Own heads within 5 of queen'),
                      ('qd', 'Queen path distance from start'), ('qlong', 'Queen is the longest (alive queens) x100'), ('half', 'Heads in enemy half')):
        scale = 100.0 if key == 'qlong' else 1.0
        R('%s at r%d' % (name, mark), lambda g, mark=mark, key=key: snap(g, mark, key) or 0, lambda g, mark=mark, key=key: int(snap(g, mark, key) is not None), scale)
for key, name in (('alive', 'Dragons alive'), ('total', 'Total length'), ('longest', 'Longest dragon'), ('second', 'Second longest'), ('ql', 'Queen length (0 if dead)')):
    R('%s at the end' % name, lambda g, key=key: g['final'][S][key], lambda g: 1, 1.0)


PICK = ('Pearls eaten /1k [0-100]', 'Net length (pearls - length lost) /1k [0-100]', 'Pearls eaten /1k [101-300]', 'Net length (pearls - length lost) /1k [101-300]',
        'Natural birth-cohort harvest % [101-300]', 'Their-dead cohort harvest % [0-100]', 'Adjacent pearl missed % [101-300]', 'Birth-cohort wait until eaten (rounds) [0-100]',
        'Split frequency /1k [0-100]', 'Deaths not head-on, boxed in /1k [0-100]', 'Deaths not head-on, a free tile beside the head /1k [101-300]',
        'Death: head-on mover /1k turns [0-100]', 'Death: head-on hit /1k turns [0-100]', 'Death: head-on hit /1k turns [101-300]', 'Rams started by round 100 per game',
        'Sprint turns /1k [101-300]', 'Sprint segments paid /1k [101-300]', 'Turns by dragons of 6+ % [101-300]', 'Blind direction kept % [101-300]',
        'Repeated-spawn tile nearby % [101-300]', 'Portal steps /1k [game]', 'Enemy dies on a body of ours /1k enemy turns [101-300]',
        'Round-0 split by 4-long starters %', 'Queen: turns inside R of start % [101-300]', 'Queen: own heads within 5 tiles (mean) [101-300]',
        'Queen: enemy head within 5 % [101-300]', 'Queen: mean length on her turns [101-300]', 'Queen dead at the end %', 'Enemy queen rammed by us (games %)', 'Our queen rammed by them (games %)',
        'Dragons alive at r100', 'Total length at r100', 'Total length at r200', 'Dragons of 6+ at r200', 'Longest dragon at r300', 'Second longest at r300',
        'Longest dragon at the end', 'Won %', 'Won by eliminating them (games %)', 'Last round (mean)', 'Opponent rating (mean)', 'Same-team head-on /1k [101-300]',
        'Split: parent of exactly 4 %', 'Death: illegal split /1k turns [0-100]', 'Death: wall /1k turns [0-100]', 'Death: own body /1k turns [0-100]', 'Death: no action /1k turns [101-300]',
        'Deaths at 56+ own dragons', 'All deaths /1k [game]', 'Split frequency /1k [game]', 'First contact round')


def mkey(g):
    return '%s|%d|%d|%d' % (g['map'], g['w'], g['h'], len(g['starts'][0]))


def pooled(games, num, den):
    n = sum(num(g) for g in games)
    d = sum(den(g) for g in games)
    return (n / d if d else None), d


def matched(target, base, num, den):
    by = defaultdict(list)
    for g in base:
        by[mkey(g)].append(g)
    tw = defaultdict(float)
    for g in target:
        tw[mkey(g)] += den(g)
    tot, acc = 0.0, 0.0
    for k, wgt in tw.items():
        if k in by and wgt > 0:
            r, d = pooled(by[k], num, den)
            if r is not None:
                tot += wgt
                acc += wgt * r
    return acc / tot if tot else None


def fmt(v, scale):
    return '     NA' if v is None else '%7.2f' % (v * scale)


def med(vals):
    vals = [v for v in vals if v is not None]
    return median(vals) if vals else None


def main():
    data = load()
    cols = [k for k in COLS if data[k]]
    print('side', S, ' games:', {k: len(data[k]) for k in cols})
    for k in cols:
        gs = data[k]
        won = sum(1 for g in gs if g['win'] == 1)
        opp = Counter(g['opp_name'] for g in gs)
        print(' ', k, 'games', len(gs), 'won', won, 'not ok', sum(1 for g in gs if not g['ok']), 'layouts', len({mkey(g) for g in gs}),
              'opponents', dict(opp.most_common(6)))
    base = data.get('c0') or []
    cov = {k: sum(1 for g in data[k] if mkey(g) in {mkey(x) for x in base}) for k in ('a', 'l') if data.get(k)}
    print('layout coverage of c0 for', cov)
    head = '%-62s' % 'rate' + ''.join('%8s' % k for k in cols) + '     C@a     C@l     q@a     q@l'
    print(head)
    table = []
    ours = data.get('q') or []
    for label, num, den, scale in RATES:
        vals = {k: pooled(data[k], num, den)[0] for k in cols}
        ca = matched(data['a'], base, num, den) if data.get('a') and base else None
        cl = matched(data['l'], base, num, den) if data.get('l') and base else None
        qa = matched(data['a'], ours, num, den) if data.get('a') and ours else None
        ql = matched(data['l'], ours, num, den) if data.get('l') and ours else None
        print('%-62s' % label[:62] + ''.join(' ' + fmt(vals[k], scale) for k in cols) + ' ' + fmt(ca, scale) + ' ' + fmt(cl, scale) + ' ' + fmt(qa, scale) + ' ' + fmt(ql, scale))
        table.append((label, vals, ca, cl, scale, qa, ql))
    if len(sys.argv) > 2 and sys.argv[2] == 'md':
        print()
        print('| Rate | ' + ' | '.join(cols) + ' | C@a | C@l |')
        for label, vals, ca, cl, scale, qa, ql in table:
            if any(label.startswith(x) for x in PICK):
                print('| %s | %s | %s | %s |' % (label, ' | '.join(fmt(vals[k], scale).strip() for k in cols), fmt(ca, scale).strip(), fmt(cl, scale).strip()))
    print()
    print('first times (median round over games that reach it; share reaching %)')
    for name, getter in (('first split', lambda g: g['first_split'][S]),
                         ('16 dragons', lambda g: g['first_alive'][S].get('16')), ('32 dragons', lambda g: g['first_alive'][S].get('32')),
                         ('60 dragons', lambda g: g['first_alive'][S].get('60')),
                         ('dragon of 6', lambda g: (g['first_long'][S].get('6') or [None])[0]),
                         ('dragon of 8', lambda g: (g['first_long'][S].get('8') or [None])[0]),
                         ('dragon of 10', lambda g: (g['first_long'][S].get('10') or [None])[0]),
                         ('dragon of 15', lambda g: (g['first_long'][S].get('15') or [None])[0])):
        line = '%-30s' % name
        for k in cols:
            vals = [getter(g) for g in data[k]]
            got = [v for v in vals if v is not None]
            line += ' %5s/%3d%%' % ('NA' if not got else '%d' % median(got), round(100 * len(got) / max(1, len(vals))))
        print(line)
    for th in ('6', '10'):
        line = '%-30s' % ('first %s-long is the queen %%' % th)
        for k in cols:
            vals = [g['first_long'][S].get(th) for g in data[k]]
            got = [v for v in vals if v is not None]
            line += ' %9s' % ('NA' if not got else '%d' % round(100 * sum(v[1] for v in got) / len(got)))
        print(line)
    print()
    for tgt, cm in (('a', 2), ('l', 3)):
        if not data.get(tgt):
            continue
        ranked = []
        for label, vals, ca, cl, scale, qa, ql in table:
            ref = ca if tgt == 'a' else cl
            v = vals.get(tgt)
            if v is None or ref is None:
                continue
            m = max(abs(v), abs(ref))
            if m == 0:
                continue
            ranked.append((abs(v - ref) / m, label, v * scale, ref * scale, (vals.get('c0') or 0) * scale, ((qa if tgt == 'a' else ql) or 0) * scale))
        ranked.sort(reverse=True)
        print('largest gaps of', tgt, 'against layout-matched c0')
        for gap, label, v, ref, c0, qq in ranked[:60]:
            print('  %5.0f%%  %-62s %8.2f vs %8.2f (pooled c0 %8.2f; ours matched %8.2f)' % (100 * gap, label[:62], v, ref, c0, qq))
        print()


main()
