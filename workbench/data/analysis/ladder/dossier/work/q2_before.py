"""Scratch (diag-queenhit2): the turns before the box closes, per arm. Open sides of the tile she steps to against
the alternatives, by distance of the nearest enemy head; team mates near her; team mates' bodies on a rammer's path;
paid sprints, splits and boxed turns by her length; the last turn with a choice before a death by her own move.
Usage: python3 .../q2_before.py new|main"""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(new=('agg8-q1', 'agg8-q2'), main=('agg7-m1', 'agg7-m2', 'agg7-m3'))
DN = 'NESW'


def load(arm):
    fates, turns = {}, defaultdict(list)
    for label in ARMS[arm]:
        p = WORK / ('q2_scan-%s.jsonl' % label)
        if not p.exists():
            continue
        with p.open() as fh:
            for line in fh:
                r = json.loads(line)
                if r['k'] == 'f':
                    fates[r['game']] = r
                else:
                    turns[r['game']].append(r)
    return fates, turns


def true_reach(n):
    return (n + 3) // 4 + n - 2


def free_of(n):
    return (n + 3) // 4


def near_d(t):
    return t['near'][0][0] if t['near'] else 99


def first_step(t):
    a = t.get('action') or {}
    if a.get('kind') != 'move' or not a.get('dirs'):
        return None
    return [c for c in t['cands'] if c['d'] == a['dirs'][0]][0]


def clean(c):
    return c.get('enterable') and c['risk'] == 0 and not c['closed'] and c['kind'] == 'open'


def pct(a, b):
    return '%d/%d (%.1f%%)' % (a, b, 100.0 * a / b) if b else '0/0'


def main():
    arm = sys.argv[1]
    fates, turns = load(arm)
    hit_games = set(g for g, f in fates.items() if f['fate'] and not f['fate']['mover'] and f['fate']['cause'] == 'head-on')
    dead_games = set(g for g, f in fates.items() if f['fate'])
    print('arm', arm, 'games', len(fates), 'turns', sum(len(v) for v in turns.values()), 'hit deaths', len(hit_games), 'all deaths', len(dead_games))

    def left(g, i):
        return len(turns[g]) - 1 - i

    def hit_in(g, i, n):
        return g in hit_games and left(g, i) < n

    def die_in(g, i, n):
        return g in dead_games and left(g, i) < n

    print()
    print('== A. standing tile: kelp sides of her own tile, turns with an enemy head within N steps: hit that round | hit within 3 turns ==')
    for N in (3, 4, 5):
        c = Counter()
        for g, ts in turns.items():
            for i, t in enumerate(ts):
                if near_d(t) > N:
                    continue
                k = min(t['head_kelp'], 2)
                c['n', k] += 1
                c['h', k] += hit_in(g, i, 1)
                c['h3', k] += hit_in(g, i, 3)
        print('  N<=%d' % N, ' | '.join('kelp %s%s: %s ; %s' % (k, '+' if k == 2 else '', pct(c['h', k], c['n', k]), pct(c['h3', k], c['n', k])) for k in (0, 1, 2)))

    print()
    print('== B. the step: single-step moves with an enemy head within N steps ==')
    print('   narrow = she steps to a tile with fewer open sides than the one she leaves while a clean (unringed, not a closed pocket) tile with more open sides than the one taken was open')
    print('   wider-open = a clean tile with more open sides than the one taken was open (whatever she leaves)')
    fire_rows = defaultdict(list)
    for N in (3, 4, 5):
        c = Counter()
        for g, ts in turns.items():
            for i, t in enumerate(ts):
                f = first_step(t)
                if f is None or not f.get('enterable') or near_d(t) > N:
                    continue
                c['moves'] += 1
                c['moves h3'] += hit_in(g, i, 3)
                c['moves d3'] += die_in(g, i, 3)
                o_t = 4 - f['kelp']
                o_h = 4 - t['head_kelp']
                alts = [x for x in t['cands'] if x is not f and clean(x)]
                wider = [x for x in alts if 4 - x['kelp'] > o_t]
                choice = bool(alts)
                c['choice'] += choice
                if wider:
                    c['wider-open'] += 1
                    c['wider-open h3'] += hit_in(g, i, 3)
                    c['wider-open d3'] += die_in(g, i, 3)
                    c['wider-open took ringed'] += f['risk'] > 0
                    c['wider-open took pearl'] += bool(f.get('pearl'))
                    fire_rows[N].append((g, i, left(g, i), o_h, o_t, max(4 - x['kelp'] for x in wider), f['risk'], bool(f.get('pearl'))))
                    if o_t < o_h:
                        c['narrow'] += 1
                        c['narrow h3'] += hit_in(g, i, 3)
                        c['narrow d3'] += die_in(g, i, 3)
                elif choice:
                    c['had a choice, took widest'] += 1
                    c['had a choice, took widest h3'] += hit_in(g, i, 3)
                    c['had a choice, took widest d3'] += die_in(g, i, 3)
        print('  N<=%d moves %d (hit within 3: %d, any death within 3: %d) | narrow %s hit3, %d any death | wider-open %s hit3, %d any death (took a pearl %d) | had a clean alternative and took the widest %s hit3, %d any death' % (
            N, c['moves'], c['moves h3'], c['moves d3'], pct(c['narrow h3'], c['narrow']), c['narrow d3'], pct(c['wider-open h3'], c['wider-open']), c['wider-open d3'],
            c['wider-open took pearl'], pct(c['had a choice, took widest h3'], c['had a choice, took widest']), c['had a choice, took widest d3']))
    for N in (3, 5):
        rows = fire_rows[N]
        last3 = [r for r in rows if r[0] in dead_games and r[2] < 3]
        games = sorted(set(r[0] for r in last3))
        print('  rule "N<=%d: take the clean tile with more open sides": fires %d; in the last 3 turns of a death %d turns in %d deaths %s (hit deaths %d); fires with no death within 3 turns %d' % (
            N, len(rows), len(last3), len(games), games, len([g for g in games if g in hit_games]), len(rows) - len(last3)))
        for r in last3:
            print('      game %d turns before death %d: leaves %d open, took %d open, could take %d open, taken ring %d pearl %s' % (r[0], r[2], r[3], r[4], r[5], r[6], r[7]))

    print()
    print('== C. team mates: own heads within 3 tiles (manhattan) of her head; hit that round | hit within 3 turns ==')
    for N in (3, 5, 99):
        c = Counter()
        for g, ts in turns.items():
            for i, t in enumerate(ts):
                if near_d(t) > N:
                    continue
                a3 = min(sum(1 for x in t['allies'] if x[0] <= 3), 2)
                a2 = min(sum(1 for x in t['allies'] if x[0] <= 2 and x[2] <= 3), 1)
                c['n', a3] += 1
                c['h', a3] += hit_in(g, i, 1)
                c['h3', a3] += hit_in(g, i, 3)
                c['n2', a2] += 1
                c['h2', a2] += hit_in(g, i, 1)
        print('  enemy head within %s: ' % (N if N < 99 else 'any distance'), ' | '.join('%s%s own heads: %s ; %s' % (k, '+' if k == 2 else '', pct(c['h', k], c['n', k]), pct(c['h3', k], c['n', k])) for k in (0, 1, 2)),
              '|| a short (<=3) own head within 2 tiles: no %s, yes %s' % (pct(c['h2', 0], c['n2', 0]), pct(c['h2', 1], c['n2', 1])))
    c = Counter()
    for g, ts in turns.items():
        for i, t in enumerate(ts):
            e = t.get('end')
            if e is None and t['hit_after'] is None:
                continue
            if e is not None:
                truly = [x for x in t['danger'].get(str(e), []) if x[0] >= 0]
                if truly:
                    c['ended in true reach'] += 1
                    c['ended in true reach, hit'] += t['hit_after'] is not None
                if e in t['shield']:
                    c['ended on a tile only a team mate body keeps out of reach'] += 1
                    c['... and hit that round'] += t['hit_after'] is not None
                    c['... ringed tile'] += e in t['hit'] or e in t['pay']
    print('  team mate body on the path:', dict(c))

    print()
    print('== D. paid sprints (move longer than her free steps) ==')
    c = Counter()
    ex = []
    for g, ts in turns.items():
        for i, t in enumerate(ts):
            a = t.get('action') or {}
            if a.get('kind') != 'move' or len(t.get('path', [])) <= free_of(t['L']):
                continue
            kind = 'no clean step' if t['hit_blocked'] else 'clean step open' if t['open0'] else 'other (no ring, pocket)'
            key = 'L%d %s' % (min(t['L'], 5), kind)
            c[key] += 1
            c[key + ' | after <3'] += t['L_after'] < 3 and t['L_after'] > 0
            c[key + ' | hit within 3'] += hit_in(g, i, 3)
            c[key + ' | hit within 10'] += hit_in(g, i, 10)
            c[key + ' | any death within 10'] += die_in(g, i, 10)
            if t['L'] == 3 and t['L_after'] == 2:
                back = 0
                for j in range(i + 1, len(ts)):
                    if ts[j]['L'] >= 3:
                        break
                    back += 1
                ex.append((kind, back, j == len(ts) - 1 and ts[j]['L'] < 3 if i + 1 < len(ts) else True, near_d(t)))
    for k in sorted(c):
        print('  ', k, c[k])
    for kind in ('no clean step', 'clean step open', 'other (no ring, pocket)'):
        xs = [x for x in ex if x[0] == kind]
        if xs:
            print('   L3 to 2 by a paid sprint, %s: %d; turns she then stayed 2: median %d, never 3 again before the end of her record %d; nearest head at the sprint %s' % (
                kind, len(xs), sorted(x[1] for x in xs)[len(xs) // 2], sum(1 for x in xs if x[2]), sorted(Counter(min(x[3], 9) for x in xs).items())))
    c = Counter()
    for g, ts in turns.items():
        for i, t in enumerate(ts):
            a = t.get('action') or {}
            if t['L'] != 3 or a.get('kind') != 'move' or not t['open0'] or t['hit_blocked']:
                continue
            f = first_step(t)
            if f is None:
                continue
            d = min(near_d(t), 6)
            p = len(t.get('path', [])) > 1
            c['n', d, p] += 1
            c['h3', d, p] += hit_in(g, i, 3)
            c['h10', d, p] += hit_in(g, i, 10)
    print('   L3 turns with a clean step open, by nearest head: (single step: n, hit within 3, within 10) vs (paid sprint: n, hit3, hit10)')
    for d in range(1, 7):
        print('      head at %s%s: single %d %d %d | sprint %d %d %d' % (d, '+' if d == 6 else '', c['n', d, False], c['h3', d, False], c['h10', d, False], c['n', d, True], c['h3', d, True], c['h10', d, True]))

    print()
    print('== E. boxed turns (a ring on a tile, no clean step) by her length ==')
    c = Counter()
    for g, ts in turns.items():
        for i, t in enumerate(ts):
            if not t['hit_blocked']:
                continue
            a = t.get('action') or {}
            L = min(t['L'], 5)
            c['L%d boxed' % L] += 1
            c['L%d boxed, hit that round' % L] += hit_in(g, i, 1)
            c['L%d boxed, hit within 3' % L] += hit_in(g, i, 3)
            c['L%d boxed, clean tile within paid reach' % L] += t['L'] >= 3 and t['esc_open'] <= true_reach(t['L'])
            c['L%d boxed, clean tile 2 steps off' % L] += t['esc_open'] <= 2
            c['L%d boxed, clean tile 3 steps off' % L] += t['esc_open'] == 3
            c['L%d boxed, paid sprint' % L] += a.get('kind') == 'move' and len(t.get('path', [])) > free_of(t['L'])
            c['L%d boxed, split' % L] += a.get('kind') == 'split'
            if a.get('kind') == 'move' and len(t.get('path', [])) > free_of(t['L']):
                c['L%d boxed, paid sprint, hit that round' % L] += hit_in(g, i, 1)
                c['L%d boxed, paid sprint, hit within 3' % L] += hit_in(g, i, 3)
                c['L%d boxed, paid sprint, hit within 10' % L] += hit_in(g, i, 10)
    for k in sorted(c):
        print('  ', k, c[k])

    print()
    print('== F. queen splits by state ==')
    c = Counter()
    for g, ts in turns.items():
        for i, t in enumerate(ts):
            a = t.get('action') or {}
            if a.get('kind') != 'split' or 'split_child' not in t:
                continue
            exposed = t['hit_head'] or t['pay_head']
            state = 'no clean tile, own tile out of reach (638)' if t['hit_blocked'] and not exposed else 'own tile in reach (649/685)' if exposed else \
                'no tile to enter (695/729)' if not t['any_enterable'] else 'only closed pockets to enter (695)' if not t['open0'] else 'routine (768)'
            key = '%s L%d to %d' % (state, min(t['L'], 6), min(t['L_after'], 4))
            c[key] += 1
            c[key + ' | any death within 3'] += die_in(g, i, 4)
            c[key + ' | head within 3'] += near_d(t) <= 3
    for k in sorted(c):
        print('  ', k, c[k])
    c = Counter()
    for g, ts in turns.items():
        for t in ts:
            if t['round'] <= 300:
                c['turns'] += 1
                c['L%d' % min(t['L'], 5)] += 1
    print('   her turns r0-300 by length:', dict(c))

    print()
    print('== G. deaths by her own move: the last turn on which she had another tile to enter ==')
    for g, f in sorted(fates.items()):
        d = f['fate']
        if not d or not d['mover']:
            continue
        ts = turns[g]
        found = None
        for i in range(len(ts) - 1, -1, -1):
            t = ts[i]
            fs = first_step(t)
            alts = [x for x in t['cands'] if x.get('enterable') and x is not fs]
            if alts:
                found = (i, t, fs, alts)
                break
        last = ts[-1]
        enter = [x for x in last['cands'] if x.get('enterable')]
        line = '%d %s %dx%d r%d %s L%d | last turn: tiles to enter %d, nearest head %s, heads in view %d' % (g, f['map'], f['W'], f['H'], d['round'], d['cause'], d['L'], len(enter), near_d(last),
                                                                                                 len([e for e in last['enemies'] if not e['queen']]))
        if found:
            i, t, fs, alts = found
            a = t.get('action') or {}
            line += ' | last choice %d turns before (r%d, L%d, %s, nearest head %s): took %s, left %s' % (
                len(ts) - 1 - i, t['round'], t['L'], a.get('kind'), near_d(t),
                None if fs is None or not fs.get('enterable') else 'ring%d %s open%d exits%d%s' % (fs['risk'], 'pocket' if fs['closed'] else 'free', 4 - fs['kelp'], fs['exits'], ' pearl' if fs['pearl'] else ''),
                ['ring%d %s open%d exits%d%s' % (x['risk'], 'pocket' if x['closed'] else 'free', 4 - x['kelp'], x['exits'], ' pearl' if x['pearl'] else '') for x in alts])
        print('  ', line)


main()
