"""Scratch (diag-bigmap): the length account by cause and round band, who rams, who eats the drops, where (job 2).
Usage: python3 data/analysis/ladder/dossier/work/bm_loss.py [O|L|R] [min cells] [max cells]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median, mean

WORK = Path('data/analysis/ladder/dossier/work')
BANDS = ((0, 100), (101, 200), (201, 300), (301, 400), (401, 500))


def load(src, lo, hi):
    rows = []
    for p in sorted(WORK.glob('bm_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if lo < g['cells'] <= hi:
                rows.append(g)
    rows.sort(key=lambda g: g['gid'])
    return rows


def band(r):
    for k, (a, b) in enumerate(BANDS):
        if a <= r <= b:
            return k
    return len(BANDS) - 1


def klass(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'mate head-on'
        return 'rammed' if d['role'] == 'hit' else 'rammer'
    if c == 'other body':
        return 'body:' + d.get('hit', '?')
    if c == 'no action':
        return 'fed' if d.get('fed') else 'no action, boxed' if d.get('free') == 0 else 'no action, other'
    return c


def third(z):
    return 'own' if z < 0.35 else 'their' if z > 0.65 else 'mid'


def report(name, gs):
    n = len(gs)
    if not n:
        return
    print()
    print('=====', name, 'games', n, 'won', sum(g['result'] == 'win' for g in gs))
    for s, nm in ((0, 'OURS'), (1, 'THEIRS')):
        cnt = defaultdict(lambda: [0] * len(BANDS))
        ln = defaultdict(lambda: [0] * len(BANDS))
        for g in gs:
            for d in g['deaths']:
                if d['s'] == s:
                    k = klass(d)
                    cnt[k][band(d['r'])] += 1
                    ln[k][band(d['r'])] += d['L']
        eat = [[0] * len(BANDS) for _ in range(3)]
        paid = [0] * len(BANDS)
        spl = [0] * len(BANDS)
        for g in gs:
            for row in g['rc']:
                b = band(row[0])
                eat[0][b] += row[1 + s * 6 + 2]
                eat[1][b] += row[1 + s * 6 + 3]
                paid[b] += row[1 + s * 6 + 5]
                spl[b] += row[1 + s * 6 + 1]
        print(nm, 'per game, by band', BANDS, '| total')
        tot = [0] * len(BANDS)
        for k in sorted(ln, key=lambda k: -sum(ln[k])):
            print('  %-18s deaths %s | %.1f ; length %s | %.1f' % (k, ' '.join('%.1f' % (x / n) for x in cnt[k]), sum(cnt[k]) / n, ' '.join('%.1f' % (x / n) for x in ln[k]), sum(ln[k]) / n))
            for b in range(len(BANDS)):
                tot[b] += ln[k][b]
        print('  %-18s length %s | %.1f' % ('ALL DEATHS', ' '.join('%.1f' % (x / n) for x in tot), sum(tot) / n))
        print('  %-18s length %s | %.1f' % ('paid in sprints', ' '.join('%.1f' % (x / n) for x in paid), sum(paid) / n))
        print('  %-18s %s | %.1f' % ('eaten natural', ' '.join('%.1f' % (x / n) for x in eat[0]), sum(eat[0]) / n))
        print('  %-18s %s | %.1f' % ('eaten drops', ' '.join('%.1f' % (x / n) for x in eat[1]), sum(eat[1]) / n))
        print('  %-18s %s | %.1f' % ('splits', ' '.join('%.1f' % (x / n) for x in spl), sum(spl) / n))
        print('  %-18s %s' % ('net length', ' '.join('%.1f' % ((eat[0][b] + eat[1][b] - tot[b] - paid[b]) / n) for b in range(len(BANDS)))))
    # rams: detail for each direction
    for s, nm in ((0, 'RAMS ON US (victim ours)'), (1, 'RAMS ON THEM (victim theirs)')):
        rams = [d for g in gs for d in g['deaths'] if d['s'] == s and d['c'] == 'head-on' and d['cross'] and d['role'] == 'hit']
        if not rams:
            continue
        m = len(rams)
        print(nm, '%d, %.1f a game; by band a game %s' % (m, m / n, ' '.join('%.1f' % (sum(1 for d in rams if band(d['r']) == b) / n) for b in range(len(BANDS)))))
        c = Counter(min(d['m']['L0'], 6) for d in rams)
        print('   rammer length at turn start 2/3/4/5/6+: %s' % ' '.join('%.2f' % (c[k] / m) for k in (2, 3, 4, 5, 6)))
        c = Counter(min(d['m']['steps'], 4) for d in rams)
        print('   steps 1/2/3/4+: %s ; mean %.2f' % (' '.join('%.2f' % (c[k] / m) for k in (1, 2, 3, 4)), mean(d['m']['steps'] for d in rams)))
        print('   paid a segment %.2f; segments paid a ram %.2f; ate on the way %.2f' % (sum(d['m']['paid'] > 0 for d in rams) / m, mean(d['m']['paid'] for d in rams), sum(d['m']['ate'] > 0 for d in rams) / m))
        c = Counter(min(d['L'], 10) if d['L'] <= 4 or d['L'] >= 10 else 5 for d in rams)
        print('   victim length 2/3/4/5-9/10+: %s ; mean %.2f ; victim length lost a game %.1f ; rammer length lost a game %.1f' % (' '.join('%.2f' % (c[k] / m) for k in (2, 3, 4, 5, 10)), mean(d['L'] for d in rams), sum(d['L'] for d in rams) / n, sum(d['m']['L'] for d in rams) / n))
        rel = Counter('shorter' if d['L'] < d['m']['L0'] else 'same' if d['L'] == d['m']['L0'] else 'longer<2x' if d['L'] < 2 * d['m']['L0'] else '2x+' for d in rams)
        print('   victim against rammer:', ' '.join('%s %.2f' % (k, rel[k] / m) for k in ('shorter', 'same', 'longer<2x', '2x+')))
        z = Counter(third(d['zo'] if s == 0 else 1 - d['zo']) for d in rams)
        print('   where (victim side own third / mid / other third): %.2f %.2f %.2f' % (z['own'] / m, z['mid'] / m, z['their'] / m))
        print('   victim: queen %.3f; its side longest and 8+ %.3f; own heads within 5: mean %.2f, none %.2f; enemy heads within 5 mean %.2f' % (sum(d['q'] for d in rams) / m, sum(1 for d in rams if d['top'] and d['L'] >= 8) / m, mean(d['o5'] for d in rams), sum(d['o5'] == 0 for d in rams) / m, mean(d['e5'] for d in rams)))
        print('   rammer edge (own heads in view + 1 - enemy heads) at least 1: %.2f' % (sum(d['m']['edge'] >= 1 for d in rams) / m))
        # drops: of the victim and of the rammer (find mover deaths)
        dv = sum(d['drop'] for d in rams)
        print('   victim drops %d: eaten by victim side %.2f, by rammer side %.2f (within 5 rounds %.2f / %.2f); by a 10+ or longest of rammer side %.2f' % (dv, sum(d['eat'][s] for d in rams) / dv, sum(d['eat'][1 - s] for d in rams) / dv, sum(d['eat5'][s] for d in rams) / dv, sum(d['eat5'][1 - s] for d in rams) / dv, sum(d['eatB'][1 - s] for d in rams) / dv))
        mv = [d for g in gs for d in g['deaths'] if d['s'] == 1 - s and d['c'] == 'head-on' and d['cross'] and d['role'] == 'mover']
        dm = sum(d['drop'] for d in mv)
        print('   rammer drops %d: eaten by victim side %.2f, by rammer side %.2f' % (dm, sum(d['eat'][s] for d in mv) / max(dm, 1), sum(d['eat'][1 - s] for d in mv) / max(dm, 1)))
    # all drops by side of the dead
    for s, nm in ((0, 'ours'), (1, 'theirs')):
        ds = [d for g in gs for d in g['deaths'] if d['s'] == s]
        dv = sum(d['drop'] for d in ds)
        print('all drops of %s dead: %.1f a game; eaten by own side %.2f, by the other %.2f, by nobody %.2f' % (nm, dv / n, sum(d['eat'][s] for d in ds) / dv, sum(d['eat'][1 - s] for d in ds) / dv, 1 - sum(d['eat'][0] + d['eat'][1] for d in ds) / dv))
        z = Counter(third(d['zo'] if s == 0 else 1 - d['zo']) for d in ds)
        print('   all deaths of %s by third (own/mid/other): %.2f %.2f %.2f' % (nm, z['own'] / len(ds), z['mid'] / len(ds), z['their'] / len(ds)))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'O'
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    rows = load(src, lo, hi)
    if src == 'O':
        for arm in ('MAIN', 'B7', 'B7Q'):
            report(arm, [g for g in rows if g['arm'] == arm])
        for opp in sorted(set(g['opp'] for g in rows)):
            report('all arms vs ' + opp, [g for g in rows if g['opp'] == opp])
        report('B7+B7Q', [g for g in rows if g['arm'] != 'MAIN'])
    report('ALL', rows)


if __name__ == '__main__':
    main()
