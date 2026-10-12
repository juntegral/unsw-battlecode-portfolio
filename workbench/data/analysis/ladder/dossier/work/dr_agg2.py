# Scratch (diag-drops): the watcher tables (job 2) and the "pearl beside the head" tables (second view) from dr_scan-*.jsonl.
# Actors: O ours, OO our opponents, R rank-1, RO rank-1's opponents. Rates are formed inside a layout, then averaged
# over the layouts with equal weight.
# Usage: python3 data/analysis/ladder/dossier/work/dr_agg2.py <watch|adj> [test] [lo hi]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter

BASE = 'data/analysis/ladder/dossier/work/'
FILES = ['dr_scan-O0.jsonl', 'dr_scan-O1.jsonl', 'dr_scan-O2.jsonl', 'dr_scan-R0.jsonl', 'dr_scan-R1.jsonl', 'dr_scan-R2.jsonl']
ACTORS = ('O', 'R', 'OO', 'RO')
DEATH = 'RWOBMNIUZ'


def games(test):
    for name in (['dr_scan-test.jsonl'] if test else FILES):
        with open(BASE + name) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def actor(who, x):
    return who if x == 0 else who + 'O'


def lmean(tab, a, key, den):
    # tab[a][layout][key] / tab[a][layout][den], mean over layouts that have the denominator
    vals = [tab[a][l][key] / tab[a][l][den] for l in tab[a] if tab[a][l][den]]
    return 100 * sum(vals) / len(vals) if vals else float('nan')


def outcome(w, d, x):
    seq = w[6]
    codes = [seq[k + 1] for k in range(0, len(seq), 2)]
    for n, c in enumerate(codes):
        if c == 'E':
            return 'ate on turn 1' if n == 0 else 'ate on turn 2' if n == 1 else 'ate on turn 3-6'
        if c == 'R':
            return 'rammed first'
        if c in DEATH:
            return 'rammed something first' if c == 'M' else 'died first (wall, body, no action)'
    if w[5] == 'G':
        sides = {pr[7] for pr in d[12]}
        return 'the other side ate before it' if (1 - x) in sides else 'a team mate ate it all'
    if len(codes) >= 6:
        return 'six turns, pearl still there'
    return 'game or record ended'


def first(w):
    seq = w[6]
    if not seq:
        return 'none'
    c = seq[1]
    return {'E': 'eats', 'T': 'nearer', 't': 'nearer', 'P': 'as far', 'p': 'as far', 'A': 'farther', 'a': 'farther', 'S': 'splits'}.get(c, 'dies')


def watch(test, lo, hi):
    tab = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    for gm in games(test):
        who, lay = gm['who'], gm['layout']
        for d in gm['deaths']:
            if not (lo <= d[0] <= hi):
                continue
            cross = d[5] in ('H', 'M') and d[6] != d[2]
            for x in (0, 1):
                w = d[13 + x]
                if w is None:
                    continue
                a = actor(who, x)
                own = d[2] == x
                opp = min(pr[2 - x] for pr in d[12])
                dist = w[1]
                dk = '1' if dist == 1 else '2' if dist == 2 else '3-5'
                race = 'no enemy head within 5' if opp > 5 else 'enemy head nearer' if opp < dist else 'enemy head as near' if opp == dist else 'enemy head farther'
                lk = 'watcher 2-4 long' if w[2] <= 4 else 'watcher 5+ long'
                slices = ['all', 'dist ' + dk, ('own body' if own else 'their body'), ('own body' if own else 'their body') + ', dist ' + dk,
                          race, race + ', dist ' + dk, lk, lk + ', ' + race,
                          ('cross head-on' if cross else 'not a cross head-on') + ', ' + ('own body' if own else 'their body'),
                          lk + ', dist ' + dk, lk + ', dist ' + dk + ', ' + race]
                if w[3]:
                    slices.append('watcher is the queen')
                if w[4]:
                    slices.append('watcher is the longest (5+)')
                o, f = outcome(w, d, x), first(w)
                for sl in slices:
                    c = tab[sl][a][lay]
                    c['n'] += 1
                    c['o:' + o] += 1
                    c['f:' + f] += 1
    outs = ['ate on turn 1', 'ate on turn 2', 'ate on turn 3-6', 'a team mate ate it all', 'the other side ate before it', 'rammed first',
            'rammed something first', 'died first (wall, body, no action)', 'six turns, pearl still there', 'game or record ended']
    firsts = ['eats', 'nearer', 'as far', 'farther', 'splits', 'dies', 'none']
    for sl in sorted(tab):
        print()
        print('## watcher slice:', sl, '| n', ' '.join('%s %d' % (a, sum(tab[sl][a][l]['n'] for l in tab[sl][a])) for a in ACTORS))
        print('%-40s' % 'first turn' + ''.join('%8s' % a for a in ACTORS))
        for f in firsts:
            print('%-40s' % ('  ' + f) + ''.join('%8.1f' % lmean(tab[sl], a, 'f:' + f, 'n') for a in ACTORS))
        print('%-40s' % 'outcome')
        for o in outs:
            print('%-40s' % ('  ' + o) + ''.join('%8.1f' % lmean(tab[sl], a, 'o:' + o, 'n') for a in ACTORS))


def mclass(m):
    if m // 256 % 2:
        return 'feeding phase, mate twice as long near'
    if m // 64 % 2:
        return 'longer mate within 9, after the leader round'
    if m // 4 % 2:
        return 'pocket rule'
    if m // 16 % 2:
        return 'no room behind the pearl (under L+2)'
    if m // 8 % 2:
        return 'threat term on the tile'
    if m % 2:
        return 'enemy head beside the tile, no threat term'
    if m // 2 % 2:
        return "team mate's head beside the tile"
    if m // 32 % 2:
        return 'tight room (under 3L+8)'
    return 'nothing in the way'


DID = ('ate it', 'moved elsewhere', 'split', 'died by no action', 'died otherwise', 'ate another pearl')
LC = ('2', '3', '4', '5-7', '8+')
BITS = ((1, 'enemy head can step onto the tile'), (2, "team mate's head can step onto the tile"), (4, 'pocket rule'), (8, 'threat term'),
        (16, 'room under L+2'), (32, 'room under 3L+8'), (64, 'longer mate within 9 after the leader round'),
        (128, 'the longest mate within 9 after the leader round'), (256, 'feeding phase, mate twice as long within 15'))


def decomp(tab, title, a, b):
    # tab[actor][layout][class] = [turns, missed]; N per actor and layout in tab[actor][layout]['*']
    def rows(x):
        lays = [l for l in tab[x] if tab[x][l]['*'][0]]
        out = {}
        for k in {k for l in lays for k in tab[x][l] if k != '*'}:
            w = sum(tab[x][l][k][0] / tab[x][l]['*'][0] for l in lays) / len(lays)
            m = sum(tab[x][l][k][1] / tab[x][l]['*'][0] for l in lays) / len(lays)
            out[k] = (w, m, sum(tab[x][l][k][0] for l in lays))
        return out
    ra, rb = rows(a), rows(b)
    ta, tb = sum(v[1] for v in ra.values()), sum(v[1] for v in rb.values())
    print()
    print('##', title, '|', a, 'against', b, '| not taken: %.1f%% against %.1f%%, gap %+.1f' % (100 * ta, 100 * tb, 100 * (ta - tb)))
    print('class | %s: %% of such turns, not taken %% | %s: same | gap points = mix + rate | n' % (a, b))
    for k in sorted(set(ra) | set(rb), key=lambda k: -abs(ra.get(k, (0, 0))[1] - rb.get(k, (0, 0))[1])):
        wa, ma, na = ra.get(k, (0, 0, 0))
        wb, mb, nb = rb.get(k, (0, 0, 0))
        sa = ma / wa if wa else 0.0
        sb = mb / wb if wb else 0.0
        print('%-62s | %5.1f %5.1f | %5.1f %5.1f | %+5.2f = %+5.2f %+5.2f | %d %d' % (
            k, 100 * wa, 100 * sa, 100 * wb, 100 * sb, 100 * (ma - mb), 100 * (wa - wb) * (sa + sb) / 2, 100 * (sa - sb) * (wa + wb) / 2, na, nb))


def adj(test, win):
    names = ('mask', 'did', 'kind', 'length', 'role', 'mask x did', 'length x did', 'kind x mask', 'after', 'beside', 'length x mask')
    tabs = {n: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0]))) for n in names}
    bits = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0]))))
    for gm in games(test):
        who, lay = gm['who'], gm['layout']
        for s, w, lc, role, nadj, kind, ac, m, did, after, n in gm['adj']:
            if w != win:
                continue
            a = actor(who, s)
            miss = 0 if did == 0 else n
            mc = mclass(m)
            kd = ('natural', 'own drop', 'their drop')[kind] + ', ' + ('0-2 rounds old', '3-15 rounds old', 'older')[ac]
            cls = {'mask': mc, 'did': DID[did], 'kind': kd, 'length': 'length ' + LC[lc], 'role': ('other', 'queen', 'longest 5+')[role],
                   'mask x did': mc + ' / ' + DID[did], 'length x did': 'length ' + LC[lc] + ' / ' + DID[did],
                   'kind x mask': ('natural', 'own drop', 'their drop')[kind] + ' / ' + mc,
                   'after': 'taken' if did == 0 else DID[did] + ' / then ' + ('nobody in 3 rounds', 'itself', 'a team mate', 'the other side', '', '', '', '', 'n/a', 'n/a')[after],
                   'beside': 'one pearl beside' if nadj == 1 else 'two or more beside',
                   'length x mask': ('length 2-4' if lc <= 2 else 'length 5+') + ' / ' + mc}
            for name, k in cls.items():
                t = tabs[name][a][lay]
                t[k][0] += n
                t[k][1] += miss
                t['*'][0] += n
                t['*'][1] += miss
            for bit, bname in BITS:
                on = 'with' if m // bit % 2 else 'without'
                t = bits[bname][a][lay]
                t[on][0] += n
                t[on][1] += miss
                t['*'][0] += n
    for name in names:
        decomp(tabs[name], 'second view, by ' + name + ', window ' + ('0-100', '101-300')[win], 'O', 'R')
    decomp(tabs['mask'], 'second view, by mask, opponents', 'OO', 'RO')
    decomp(tabs['did'], 'second view, by did, opponents', 'OO', 'RO')
    print()
    print('## one flag at a time: share of such turns with the flag, not taken with it, not taken without it')
    for bit, bname in BITS:
        line = '%-48s' % bname
        for a in ACTORS:
            t = bits[bname][a]
            lays = [l for l in t if t[l]['*'][0]]
            sh = sum(t[l]['with'][0] / t[l]['*'][0] for l in lays) / max(1, len(lays))
            n1 = sum(t[l]['with'][0] for l in lays)
            m1 = sum(t[l]['with'][1] for l in lays)
            n0 = sum(t[l]['without'][0] for l in lays)
            m0 = sum(t[l]['without'][1] for l in lays)
            line += ' | %s %4.1f %5.1f %5.1f' % (a, 100 * sh, 100 * m1 / max(1, n1), 100 * m0 / max(1, n0))
        print(line)


def main():
    what = sys.argv[1]
    test = len(sys.argv) > 2 and sys.argv[2] == 'test'
    nums = [int(v) for v in sys.argv[2:] if v.isdigit()]
    if what == 'watch':
        lo, hi = nums[:2] if len(nums) >= 2 else (101, 300)
        watch(test, lo, hi)
    else:
        adj(test, nums[0] if nums else 1)


main()
