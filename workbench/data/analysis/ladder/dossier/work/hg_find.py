# Scratch (diag-hungry): inside our own hungry turns (hg_scan3 rows), does a dragon that keeps its heading find a
# pearl sooner? For a hungry turn with nothing in view: how many of its last 3 steps (this one included) repeat the
# step before; then a pearl in view on its next turn, and a meal within its next 10 and 20 turns.
# Usage: python3 data/analysis/ladder/dossier/work/hg_find.py <arm|test>
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'


def pct(a, b):
    return '%.1f%%' % (100.0 * a / b) if b else '-'


def main():
    arm = sys.argv[1]
    names = [WORK + 'hg_scan3-test.jsonl'] if arm == 'test' else [WORK + 'hg_scan3-%s-%d.jsonl' % (arm, s) for s in range(4)]
    acc = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    for nm in names:
        seqs = defaultdict(list)

        def flush():
            for i, s in seqs.items():
                for n, r in enumerate(s):
                    if r['np'] > 0 or r['c'] < 0 or n < 3:
                        continue
                    a, b, c0 = s[n - 1], s[n - 2], s[n - 3]
                    if a['r'] != r['r'] - 1 or b['r'] != r['r'] - 2 or c0['r'] != r['r'] - 3 or min(a['c'], b['c'], c0['c']) < 0:
                        continue
                    st = (r['c'] == a['c']) + (a['c'] == b['c']) + (b['c'] == c0['c'])
                    mates = 'no mate' if r['nm'] == 0 else 'mates'
                    nxt = s[n + 1] if n + 1 < len(s) and s[n + 1]['r'] == r['r'] + 1 else None
                    for key in ((mates, st), ('all', st)):
                        v = acc[key]
                        v[0] += 1
                        if nxt is not None:
                            v[1] += 1
                            v[2] += nxt['np'] > 0
                        ate10 = ate20 = 0
                        for m in s[n:n + 20]:
                            if m['r'] - r['r'] >= 20 or m['idle'] < r['idle']:
                                break
                            if m['ate']:
                                ate20 = 1
                                if m['r'] - r['r'] < 10:
                                    ate10 = 1
                                break
                        v[3] += ate10
                        v[4] += ate20
                        v[5] += r['loop']
            seqs.clear()

        with open(nm) as f:
            for line in f:
                r = json.loads(line)
                if r.get('kind') == 'game':
                    flush()
                    continue
                legal = [d for d in range(4) if r['dirs'][d] is not None]
                ch = [d for d in legal if len(r['path']) == 1 and r['dirs'][d][14] == r['path'][0]]
                s = seqs[r['i']]
                recent = [x['h'] for x in s[-12:] if x['r'] >= r['r'] - 12]
                s.append(dict(r=r['r'], np=r['np'], nm=r['nm'], c=ch[0] if ch else -1, ate=r['ate'], idle=r['idle'], h=r['h'],
                              loop=1 if r['path'] and r['path'][0] in recent else 0))
        flush()
    print('hungry turns with nothing in view, by how many of the last 3 steps kept the heading:')
    print('  turns | a pearl in view on the next turn | a meal within 10 turns | within 20 turns | this step lands on a tile of its last 12 turns')
    for key in sorted(acc, key=lambda k: (k[0], k[1])):
        v = acc[key]
        print('  %-8s %d of 3: n %6d | %s | %s | %s | %s' % (key[0], key[1], v[0], pct(v[2], v[1]), pct(v[3], v[0]), pct(v[4], v[0]), pct(v[5], v[0])))


main()
