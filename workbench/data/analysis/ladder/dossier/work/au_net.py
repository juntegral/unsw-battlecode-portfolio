"""Scratch (diag-australia): length account of cross-team head-on meetings, with the segments the mover paid for its
sprint added to its loss (the scan stores the length at death). Also queen deaths. Reads au_ev-*.jsonl and per-game.jsonl."""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
games = []
for n in range(4):
    with open(D / ('au_ev-%d.jsonl' % n)) as f:
        for line in f:
            games.append(json.loads(line))


def start_len(e):
    # length at the start of the mover's turn: steps before the hit beyond the free ones were paid with a segment each
    for p in range(0, 8):
        L0 = e['Lm'] + p
        if p == max(0, e['k'] - 1 - (L0 + 3) // 4):
            return L0
    return e['Lm']


def account(gs, lo, hi):
    n = len(gs)
    a = Counter()
    for g in gs:
        for e in g['hos']:
            if not e['cross'] or not lo <= e['r'] <= hi:
                continue
            L0 = start_len(e)
            m, v = e['ms'], ('u' if e['ms'] == 't' else 't')
            a['n_' + m] += 1
            a['lost_' + m + '_as_mover'] += L0
            a['lost_' + v + '_as_victim'] += e['Lv']
            a['back_' + m + '_as_mover'] += e['eat'][m]
            a['back_' + v + '_as_victim'] += e['eat'][v]
            a['drop_' + m] += e['drop']
            a['paid_' + m] += L0 - e['Lm']
            a['sprint_' + m] += int(e['k'] > (L0 + 3) // 4)
    r = {}
    r['they'] = a['n_t'] / n
    r['we'] = a['n_u'] / n
    r['us_net'] = (a['back_u_as_victim'] - a['lost_u_as_victim'] + a['back_u_as_mover'] - a['lost_u_as_mover']) / n
    r['them_net'] = (a['back_t_as_victim'] - a['lost_t_as_victim'] + a['back_t_as_mover'] - a['lost_t_as_mover']) / n
    r['they_start_us'] = (a['back_u_as_victim'] - a['lost_u_as_victim']) / max(1, a['n_t'])
    r['they_start_them'] = (a['back_t_as_mover'] - a['lost_t_as_mover']) / max(1, a['n_t'])
    r['we_start_us'] = (a['back_u_as_mover'] - a['lost_u_as_mover']) / max(1, a['n_u'])
    r['we_start_them'] = (a['back_t_as_victim'] - a['lost_t_as_victim']) / max(1, a['n_u'])
    r['their_drop_share'] = a['back_t_as_mover'] / max(1, a['drop_t'])
    r['our_drop_share_their_rams'] = a['back_u_as_victim'] / max(1, a['drop_t'])
    r['their_sprint'] = a['sprint_t'] / max(1, a['n_t'])
    r['their_paid'] = a['paid_t'] / max(1, a['n_t'])
    r['their_L0'] = a['lost_t_as_mover'] / max(1, a['n_t'])
    r['our_Lv'] = a['lost_u_as_victim'] / max(1, a['n_t'])
    return r


AU = [g for g in games if g['layout'] == 'Australia #1']
for title, gs in (('Australia all 35', AU), ('Australia 26 losses', [g for g in AU if g['result'] == 'loss']),
                  ('Australia 9 wins', [g for g in AU if g['result'] == 'win'])):
    for lo, hi in ((0, 100), (101, 300), (301, 499)):
        r = account(gs, lo, hi)
        print('%s r%d-%d: they ram %.1f, we ram %.1f a game | net length from meetings a game: us %.1f, them %.1f (difference %.1f) | a meeting they start: us %.2f, them %.2f (their start length %.2f, our victim %.2f, paid sprint %.3f, segments paid %.2f; drops eaten by them %.3f, by us %.3f) | a meeting we start: us %.2f, them %.2f' % (
            title, lo, hi, r['they'], r['we'], r['us_net'], r['them_net'], r['us_net'] - r['them_net'], r['they_start_us'], r['they_start_them'],
            r['their_L0'], r['our_Lv'], r['their_sprint'], r['their_paid'], r['their_drop_share'], r['our_drop_share_their_rams'], r['we_start_us'], r['we_start_them']))

print()
print('layout | cells | games | won | r101-300 a game: they ram / we ram | net length from meetings: us / them | difference | total length r100 us/them -> r300 us/them | longest r300 us/them')
by = defaultdict(list)
for g in games:
    by[g['layout']].append(g)
rows = []
for lay, gs in by.items():
    r = account(gs, 101, 300)
    n = len(gs)
    def snap(rr, k):
        us, ts = [], []
        for g in gs:
            s = [x for x in g['snaps'] if x[0] == rr]
            if s:
                us.append(s[0][1][k]); ts.append(s[0][2][k])
        return (sum(us) / len(us), sum(ts) / len(ts)) if us else (float('nan'), float('nan'))
    rows.append((r['us_net'] - r['them_net'], '%s | %d | %d | %d | %.1f / %.1f | %.1f / %.1f | %.1f | %.0f/%.0f -> %.0f/%.0f | %.0f/%.0f' % (
        lay, gs[0]['w'] * gs[0]['h'], n, sum(g['result'] == 'win' for g in gs), r['they'], r['we'], r['us_net'], r['them_net'],
        r['us_net'] - r['them_net'], snap(100, 1)[0], snap(100, 1)[1], snap(300, 1)[0], snap(300, 1)[1], snap(300, 2)[0], snap(300, 2)[1])))
for k, line in sorted(rows):
    print(line)

# within-layout: does the meeting account go with the result? Australia per game
print()
print('Australia per game: result | they ram / we ram r101-300 | net us / them | total r100 u/t | r300 u/t')
for g in sorted(AU, key=lambda g: g['game']):
    r = account([g], 101, 300)
    s = {x[0]: x for x in g['snaps']}
    print('  %d %-4s vs %d | %2.0f / %2.0f | %6.1f / %6.1f | %s | %s' % (
        g['game'], g['result'], g['rating'], r['they'], r['we'], r['us_net'], r['them_net'],
        '%d/%d' % (s[100][1][1], s[100][2][1]) if 100 in s else 'NA', '%d/%d' % (s[300][1][1], s[300][2][1]) if 300 in s else 'NA'))

# queen deaths on Australia from the dossier rows
print()
q = Counter()
with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r['layout_key'] != 'Australia #1':
            continue
        d = r['queen']['death']
        s = r['relation']
        q[s + ' games'] += 1
        if d is None:
            q[s + ' alive at end'] += 1
            continue
        q[s + ' dead'] += 1
        q[s + ' dead by r100'] += int(d['round'] <= 100)
        q[s + ' dead by r300'] += int(d['round'] <= 300)
        q[s + ' ' + d['cause']] += 1
        if d['cause'] == 'head-on hit':
            q[s + ' rammed by r300'] += int(d['round'] <= 300)
            q[s + ' rammed, queen length<=3'] += int(d['length'] <= 3)
print('queen deaths, Australia:', dict(sorted(q.items())))
