# Scratch (diag-drops): compares dr_scan-*.jsonl game by game with the dossier rows (per-game.jsonl, target/per-game-top1.jsonl):
# turns that start with a pearl beside the head and those not taken (both windows), and for rounds 0-100 and 101-300 the
# pearls dropped by deaths (all births minus natural births) and how many each side ate.
# Usage: python3 data/analysis/ladder/dossier/work/dr_check.py
import sys, json
sys.dont_write_bytecode = True
from collections import Counter

BASE = 'data/analysis/ladder/dossier/'
FILES = ['dr_scan-O0.jsonl', 'dr_scan-O1.jsonl', 'dr_scan-O2.jsonl', 'dr_scan-R0.jsonl', 'dr_scan-R1.jsonl', 'dr_scan-R2.jsonl']


def main():
    want = {}
    for who, name in (('O', 'per-game.jsonl'), ('R', 'target/per-game-top1.jsonl')):
        with open(BASE + name) as f:
            for line in f:
                r = json.loads(line)
                if r['relation'] != 'us':
                    continue
                rec = []
                for win in ('0-100', '101-300'):
                    c = r['ranges'][win]
                    rec.append((c['adjacent_pearl_turns'], c['adjacent_pearl_missed'], c['births'] - c['natural_births'],
                                c['cohort_eaten']['us'] - c['natural_eaten']['us'], c['cohort_eaten']['them'] - c['natural_eaten']['them']))
                want[(who, r['game'])] = rec
    seen = Counter()
    off = Counter()
    for name in FILES:
        with open(BASE + 'work/' + name) as f:
            for line in f:
                if not line.strip():
                    continue
                gm = json.loads(line)
                key = (gm['who'], gm['game'])
                seen[gm['who']] += 1
                got = []
                for w, (lo, hi) in enumerate(((0, 100), (101, 300))):
                    n = e0 = e1 = 0
                    for d in gm['deaths']:
                        if lo <= d[0] <= hi:
                            for pr in d[12]:
                                n += 1
                                e0 += pr[7] == 0
                                e1 += pr[7] == 1
                    got.append((gm['chk'][w][0], gm['chk'][w][1], n, e0, e1))
                for w in (0, 1):
                    for k, fname in enumerate(('beside turns', 'not taken', 'drops', 'drops eaten by the side', 'drops eaten by the other side')):
                        if got[w][k] != want[key][w][k]:
                            off[(gm['who'], w, fname)] += 1
                            if sum(off.values()) <= 10:
                                print('MISMATCH', key, w, fname, got[w][k], want[key][w][k])
    print('games compared', dict(seen), 'of', len(want), 'cells that differ', dict(off))


main()
