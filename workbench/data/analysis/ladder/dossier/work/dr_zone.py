# Scratch (diag-drops): before and after the leader round, from dr_scan2-*.jsonl. Layout-equal means inside a size group
# (big = above 1200 cells, where our leader rules start at round 151; small = the rest, where they start at round 301).
# Usage: python3 data/analysis/ladder/dossier/work/dr_zone.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter

BASE = 'data/analysis/ladder/dossier/work/'
FILES = ['dr_scan2-O0.jsonl', 'dr_scan2-O1.jsonl', 'dr_scan2-O2.jsonl', 'dr_scan2-R0.jsonl', 'dr_scan2-R1.jsonl', 'dr_scan2-R2.jsonl']
ACTORS = ('O', 'R', 'OO', 'RO')
PH = ('0-100', '101-150', '151-200', '201-300', '301-350', '351-400')


def actor(who, x):
    return who if x == 0 else who + 'O'


def lm(tab, num, den):
    vals = [tab[l][num] / tab[l][den] for l in tab if tab[l][den]]
    return 100 * sum(vals) / len(vals) if vals else float('nan')


def tot(tab, key):
    return sum(tab[l][key] for l in tab)


def phase(r):
    return 0 if r <= 100 else 1 if r <= 150 else 2 if r <= 200 else 3 if r <= 300 else 4 if r <= 350 else 5


def main():
    adj = defaultdict(lambda: defaultdict(Counter))
    fate = defaultdict(Counter)
    wat = defaultdict(lambda: defaultdict(Counter))
    drop = defaultdict(lambda: defaultdict(Counter))
    ngames = defaultdict(lambda: defaultdict(set))
    for name in FILES:
        with open(BASE + name) as f:
            for line in f:
                if not line.strip():
                    continue
                gm = json.loads(line)
                who, lay = gm['who'], gm['layout']
                size = 'big' if gm['cells'] > 1200 else 'small'
                for ph in range(6):
                    if gm['last_round'] >= (0, 101, 151, 201, 301, 351)[ph]:
                        ngames[(who, size, ph)][lay].add(gm['game'])
                for s, ph, lc, role, nadj, kind, ac, m, did, after, n in gm['adj']:
                    a = actor(who, s)
                    c = adj[(a, size, ph)][lay]
                    miss = n if did else 0
                    feed = m // 256 % 2
                    z = m // 64 % 2
                    top = m // 512 % 2
                    clear = (m % 32) == 0
                    cls = 'Q' if role == 1 else 'F' if feed else 'Z' if z else 'T' if top else 'N'
                    c['n'] += n
                    c['miss'] += miss
                    c[cls] += n
                    c[cls + '_miss'] += miss
                    if clear:
                        c[cls + 'c'] += n
                        c[cls + 'c_miss'] += miss
                    if lc <= 1:
                        c[cls + 's'] += n
                        c[cls + 's_miss'] += miss
                    if cls == 'Z' and m // 128 % 2:
                        c['ZT'] += n
                        c['ZT_miss'] += miss
                    if cls == 'Z':
                        c['Z_split'] += n if did == 2 else 0
                        kd = 'nat' if kind == 0 else 'own' if kind == 1 else 'oth'
                        c['Z' + kd] += n
                        c['Z' + kd + '_miss'] += miss
                    if did and cls == 'Z':
                        fk = (a, size, 'on' if (size == 'big' and ph >= 2) or (size == 'small' and ph >= 4) else 'off' if ph >= 1 else 'early')
                        who2, wb = after // 10, after % 10
                        fate[fk]['n'] += n
                        fate[fk][('never', 'itself', 'a mate of 4 or less', 'the other side', 'a mate of 5 or more')[who2] if after else 'never'] += n
                        if after:
                            fate[fk][('within 3 rounds', 'in 4-15 rounds', 'later')[wb]] += n
                for d in gm['deaths']:
                    ph = phase(d[0])
                    for x in (0, 1):
                        a = actor(who, x)
                        c = drop[(a, size, ph)][lay]
                        own = d[2] == x
                        for pr in d[12]:
                            mine, theirs = pr[1 + x], pr[2 - x]
                            c['n'] += 1
                            c['e'] += pr[7] == x
                            if own:
                                c['own'] += 1
                                c['own_e'] += pr[7] == x
                            if theirs > 5 and mine <= 5:
                                k = 'a' if mine <= 2 else 'b'
                                c[k] += 1
                                c[k + '_e'] += pr[7] == x
                                c[k + '_o'] += pr[7] == 1 - x
                        w = d[13 + x]
                        if w is not None and w[6] and min(pr[2 - x] for pr in d[12]) > 5 and not w[3]:
                            wc = wat[(a, size, ph)][lay]
                            for k in ('d1' if w[1] == 1 else 'd2' if w[1] == 2 else 'd3', ('z1' if w[7] else 'z0') + ('d1' if w[1] == 1 else 'd2' if w[1] == 2 else 'd3')):
                                wc[k] += 1
                                wc[k + '_E'] += w[6][1] == 'E'
                                wc[k + '_T'] += w[6][1] in 'Tt'
                                wc[k + '_got'] += 'E' in w[6]
    print('## second view by phase: not taken % of turns with a pearl beside the head (queens left out of the classes)')
    print('   Z = a longer mate within 9 tiles of the pearl, T = no such mate and the dragon is its side\'s longest, N = neither, F = feeding flag')
    print('   per class: share of turns, not taken %; "clear" = no head beside the tile, no pocket, no threat, room of L+2 or more')
    for size in ('big', 'small'):
        for ph in range(1, 6):
            for a in ACTORS:
                t = adj[(a, size, ph)]
                if not t:
                    continue
                print('%-5s %-8s %-3s | all %5.1f | Z %4.1f %5.1f (longest mate %5.1f; length 2-3 %5.1f; clear %5.1f) | T %4.1f %5.1f | N %4.1f %5.1f (clear %5.1f; length 2-3 %5.1f) | F %4.1f %5.1f | Z split %4.1f | Z natural %5.1f own drop %5.1f their drop %5.1f | turns %d' % (
                    size, PH[ph], a, lm(t, 'miss', 'n'), lm(t, 'Z', 'n'), lm(t, 'Z_miss', 'Z'), lm(t, 'ZT_miss', 'ZT'), lm(t, 'Zs_miss', 'Zs'), lm(t, 'Zc_miss', 'Zc'),
                    lm(t, 'T', 'n'), lm(t, 'T_miss', 'T'), lm(t, 'N', 'n'), lm(t, 'N_miss', 'N'), lm(t, 'Nc_miss', 'Nc'), lm(t, 'Ns_miss', 'Ns'),
                    lm(t, 'F', 'n'), lm(t, 'F_miss', 'F'), lm(t, 'Z_split', 'Z'),
                    lm(t, 'Znat_miss', 'Znat'), lm(t, 'Zown_miss', 'Zown'), lm(t, 'Zoth_miss', 'Zoth'), tot(t, 'n')))
    print()
    print('## per game: turns with a pearl beside the head in class Z, and those not taken (totals over games that reach the phase)')
    for size in ('big', 'small'):
        for ph in range(1, 6):
            for a in ('O', 'R'):
                t = adj[(a, size, ph)]
                g = sum(len(v) for v in ngames[(a[0], size, ph)].values())
                if g:
                    print('%-5s %-8s %-3s games %4d | all turns %6.1f not taken %6.1f | Z turns %6.1f not taken %6.1f | F turns %6.1f not taken %6.1f' % (
                        size, PH[ph], a, g, tot(t, 'n') / g, tot(t, 'miss') / g, tot(t, 'Z') / g, tot(t, 'Z_miss') / g, tot(t, 'F') / g, tot(t, 'F_miss') / g))
    print()
    print('## what became of a pearl left in class Z (pooled turns): rule on / off')
    for fk in sorted(fate):
        c = fate[fk]
        n = max(1, c['n'])
        print(fk, 'turns', c['n'], ' '.join('%s %.1f%%' % (k, 100 * v / n) for k, v in sorted(c.items()) if k != 'n'))
    print()
    print('## watcher (not a queen) of a fresh drop, no enemy head within 5: first turn eats % at 1 step; steps nearer % at 2 steps; ate one within 6 turns at 3-5')
    print('   then the same at 1 step for watchers with (z1) and without (z0) a longer mate within 9 tiles of the drop')
    for size in ('big', 'small'):
        for ph in range(1, 6):
            for a in ACTORS:
                t = wat[(a, size, ph)]
                if not t:
                    continue
                print('%-5s %-8s %-3s | 1 step eats %5.1f (n %5d) | 2 steps nearer %5.1f got %5.1f | 3-5 got %5.1f | z1: 1 step eats %5.1f (n %5d), 2 steps nearer %5.1f | z0: 1 step eats %5.1f (n %5d), 2 steps nearer %5.1f' % (
                    size, PH[ph], a, lm(t, 'd1_E', 'd1'), tot(t, 'd1'), lm(t, 'd2_T', 'd2'), lm(t, 'd2_got', 'd2'), lm(t, 'd3_got', 'd3'),
                    lm(t, 'z1d1_E', 'z1d1'), tot(t, 'z1d1'), lm(t, 'z1d2_T', 'z1d2'), lm(t, 'z0d1_E', 'z0d1'), tot(t, 'z0d1'), lm(t, 'z0d2_T', 'z0d2')))
    print()
    print('## drops by phase: eaten % | own bodies: share, eaten % | own head within 2, no enemy within 5: share, eaten %, other side % | own head at 3-5: same | drops a game')
    for size in ('big', 'small'):
        for ph in range(1, 6):
            for a in ACTORS:
                t = drop[(a, size, ph)]
                if not t:
                    continue
                g = sum(len(v) for v in ngames[(a[0], size, ph)].values())
                print('%-5s %-8s %-3s | %5.1f | %5.1f %5.1f | %5.1f %5.1f %5.1f | %5.1f %5.1f %5.1f | %6.1f' % (
                    size, PH[ph], a, lm(t, 'e', 'n'), lm(t, 'own', 'n'), lm(t, 'own_e', 'own'),
                    lm(t, 'a', 'n'), lm(t, 'a_e', 'a'), lm(t, 'a_o', 'a'), lm(t, 'b', 'n'), lm(t, 'b_e', 'b'), lm(t, 'b_o', 'b'), tot(t, 'n') / max(1, g)))


main()
