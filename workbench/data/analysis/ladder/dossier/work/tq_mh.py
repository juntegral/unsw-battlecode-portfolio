"""Scratch (diag-theirqueen): is the per-turn gradient a layout or round artefact? Mantel-Haenszel rate ratio of a queen death
(rammed before her next turn, or dead on her own move) on turns more than R+2 tiles from her start against turns nearer,
stratified by layout, opponent and 50-round band. lag N = her distance N of her own turns earlier (a chase cannot have
moved her yet). Open-start games. Usage: python3 tq_mh.py [online|ladder]"""
import sys
import json
from collections import defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    tags = ('m1', 'm2', 'b1', 'b2', 'q1') if mode == 'online' else ('L0', 'T0')
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    what = sys.argv[2] if len(sys.argv) > 2 else 'far'
    print('exposure:', what, '(far = more than R+2 tiles from start; alone = no own head within 5 tiles; few = under 3 own heads within 5 tiles; ram = rams only)')
    for lag in (0, 10, 20, 40):
        strata = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
        for g in games:
            R = min(8, (g['w'] + g['h']) // 8)
            for s in (0, 1):
                if g['scomp'][s] * 2 < g['cells']:
                    continue
                if mode == 'online':
                    who = 'ours' if s == 0 else ('Bob' if g['opp'].startswith('Big') else 'Quiz')
                else:
                    who = ('ours ladder', 'ladder opp')[s] if g['label'] == 'ladder' else ('rank1', 'rank1 opp')[s]
                recs = g['recs'][s]
                for n, t in enumerate(recs):
                    if n < lag:
                        continue
                    far = recs[n - lag][3] > R + 2
                    if what.startswith('alone'):
                        far = recs[n - lag][5] == 0
                    elif what.startswith('few'):
                        far = recs[n - lag][5] < 3
                    x = strata[who][(g.get('layout') or g['map'], g['w'], g['h'], g.get('opp'), t[0] // 50)]
                    event = 1 if (t[26] or t[25]) else 0
                    if what.endswith('ram'):
                        event = 1 if t[26] else 0
                    elif what.endswith('self'):
                        event = 1 if t[25] else 0
                    if far:
                        x[0] += event
                        x[1] += 1
                    else:
                        x[2] += event
                        x[3] += 1
        for who in sorted(strata):
            num = den = 0.0
            a = t1 = b = t0 = 0
            for x in strata[who].values():
                tot = x[1] + x[3]
                if not tot:
                    continue
                num += x[0] * x[3] / tot
                den += x[2] * x[1] / tot
                a += x[0]
                t1 += x[1]
                b += x[2]
                t0 += x[3]
            print('lag %2d %-11s far: %3d deaths in %6d turns (%.1f per 1000) | near: %3d in %6d (%.1f) | crude ratio %.1f | stratified ratio %s' % (
                lag, who, a, t1, 1000.0 * a / max(1, t1), b, t0, 1000.0 * b / max(1, t0), (a / max(1, t1)) / max(1e-9, b / max(1, t0)),
                '%.1f' % (num / den) if den else '-'))


main()
