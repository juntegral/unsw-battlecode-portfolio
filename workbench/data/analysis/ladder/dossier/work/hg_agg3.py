# Scratch (diag-hungry): reads hg_scan3-<arm>-*.jsonl (the offline rebuild of score_step on hungry turns) and prints
# how often the rebuilt score names the step the dragon took, what the step taken is aimed at, which term decides it
# (the step changes when the term is removed) and how far apart the steps are on each term.
# Usage: python3 data/analysis/ladder/dossier/work/hg_agg3.py <arm|test>
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

WORK = 'data/analysis/ladder/dossier/work/'
TERMS = ('territory', 'pearl target', 'soon', 'hot', 'unseen', 'far gain', 'look', 'mate head beside', 'spawn clear')


def tb(d):
    return max(0.0, 260.0 - 40.0 * d) if d >= 0 else 0.0


def parts(v, drop=None):
    room, terr, dp, ds, dh, du, eat, adj, sc, cr, look, portal = v[:12]
    if drop == 'pearl target':
        dp = -1
    if drop == 'soon':
        ds = -1
    if drop == 'hot':
        dh = -1
    if drop == 'unseen':
        du = -1
    b = [2.0 * tb(dp), 0.45 * tb(ds), 1.2 * tb(dh), 0.2 * tb(du)]
    near = [x for x in (dp, ds, dh, du) if x >= 0]
    far = 2.0 * max(0, 80 - min(near)) if near else 0.0
    return dict(space=1.5 * room, territory=0.0 if drop == 'territory' else 1.5 * terr, cramped=-cr, bonus=max(b), which=b.index(max(b)) if max(b) > 0 else -1,
                far=0.0 if drop == 'far gain' else far, eat=300.0 * eat, look=0.0 if drop == 'look' else look,
                adj=0.0 if drop == 'mate head beside' else -450.0 * adj, sc=0.0 if drop == 'spawn clear' else -300.0 * sc, leap=-150.0 * portal,
                nearest=[dp, ds, dh, du].index(min(near)) if near else -1, dists=(dp, ds, dh, du))


def total(pp):
    return pp['space'] + pp['territory'] + pp['cramped'] + pp['bonus'] + pp['far'] + pp['eat'] + pp['look'] + pp['adj'] + pp['sc'] + pp['leap']


def pct(a, b):
    return '%.1f%%' % (100.0 * a / b) if b else '-'


def aim(v, pp):
    """What the step is aimed at: the term that sets the target bonus, or the nearest thing named beyond 6 steps."""
    k = pp['which']
    far = ''
    if k < 0:
        k = pp['nearest']
        if k < 0:
            return 'nothing named'
        far = ' (over 6 steps: far gain only)'
    if k == 0:
        return ('a pearl in view' if v[12] == 2 else 'a remembered pearl, still there' if v[12] == 1 else 'a remembered pearl, gone') + far
    if k == 1:
        return ('a remembered spawn tile, pearl on it now' if v[13] == 2 else 'a remembered spawn tile, spawns within 6 rounds' if v[13] == 1 else 'a remembered spawn tile, nothing due (stale)') + far
    if k == 2:
        return 'a hot tile' + far
    return 'the nearest never-seen tile' + far


def main():
    arm = sys.argv[1]
    names = [WORK + 'hg_scan3-test.jsonl'] if arm == 'test' else [WORK + 'hg_scan3-%s-%d.jsonl' % (arm, s) for s in range(4)]
    agree = defaultdict(lambda: [0, 0, 0.0])
    aims = defaultdict(Counter)
    decide = defaultdict(Counter)
    spread = defaultdict(lambda: defaultdict(list))
    n_all = 0
    for nm in names:
        with open(nm) as f:
            for line in f:
                r = json.loads(line)
                if r.get('kind') == 'game':
                    continue
                n_all += 1
                legal = [d for d in range(4) if r['dirs'][d] is not None]
                ch = [d for d in legal if r['path'] and r['dirs'][d][14] == r['path'][0]]
                view = 'pearl in view' if r['np'] > 0 else 'nothing in view'
                mates = 'no mate' if r['nm'] == 0 else '1-2 mates' if r['nm'] <= 2 else '3+ mates'
                if not ch or len(legal) < 2 or r['box'] < 7:
                    agree[('left out: no step, one step on offer or boxed in', '')][0] += 1
                    continue
                if r['ne'] > 0:
                    agree[('left out: enemy head in view (threat terms not rebuilt)', '')][0] += 1
                    continue
                c = ch[0]
                pp = {d: parts(r['dirs'][d]) for d in legal}
                tot = {d: total(pp[d]) for d in legal}
                top = max(tot.values())
                ok = tot[c] >= top - 1.0
                keys = ((view, mates), (view, 'all'), ('all', 'all'))
                for key in keys:
                    a = agree[key]
                    a[0] += 1
                    a[1] += ok
                    a[2] += sum(1 for d in legal if tot[d] >= top - 1.0) / len(legal)
                what = aim(r['dirs'][c], pp[c])
                for key in keys:
                    aims[key][what] += 1
                    aims[key]['n'] += 1
                if ok:
                    changed = []
                    for term in TERMS:
                        p2 = {d: total(parts(r['dirs'][d], term)) for d in legal}
                        if p2[c] < max(p2.values()) - 1.0:
                            changed.append(term)
                    for key in keys:
                        decide[key]['n'] += 1
                        for term in changed:
                            decide[key][term] += 1
                        sp = spread[key]
                        for t, f in (('territory', 'territory'), ('target bonus', 'bonus'), ('far gain', 'far'), ('look', 'look'), ('room', 'space'), ('mate head beside', 'adj')):
                            xs = [pp[d][f] for d in legal]
                            sp[t].append(max(xs) - min(xs))
    print('hungry turns', n_all)
    print('\n== the rebuilt score names the step taken (within 1 point of its best step)')
    for key in sorted(agree):
        a = agree[key]
        print('  %-62s n %6d  agrees %s  (by chance %s)' % (' | '.join(key), a[0], pct(a[1], a[0]) if a[1] else '-', pct(a[2], a[0]) if a[2] else '-'))
    print('\n== what the step taken is aimed at (all rebuilt turns)')
    for key in sorted(aims):
        c = aims[key]
        print('  [%s] n %d' % (' | '.join(key), c['n']))
        for k, v in c.most_common():
            if k != 'n':
                print('      %-74s %6d %s' % (k, v, pct(v, c['n'])))
    print('\n== the step changes when the term is removed (turns the rebuilt score explains)')
    for key in sorted(decide):
        c = decide[key]
        print('  [%s] n %d: %s' % (' | '.join(key), c['n'], ', '.join('%s %s' % (t, pct(c[t], c['n'])) for t in TERMS)))
    print('\n== points between the best and the worst step on each term: median, 75th, 90th percentile')
    for key in sorted(spread):
        sp = spread[key]
        line = []
        for t in ('room', 'territory', 'target bonus', 'far gain', 'look', 'mate head beside'):
            xs = sorted(sp[t])
            if xs:
                line.append('%s %.0f/%.0f/%.0f' % (t, xs[len(xs) // 2], xs[3 * len(xs) // 4], xs[9 * len(xs) // 10]))
        print('  [%s] %s' % (' | '.join(key), '; '.join(line)))


main()
