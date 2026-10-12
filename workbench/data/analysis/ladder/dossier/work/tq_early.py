"""Scratch (diag-theirqueen): a test less open to "she is far because she was chased": her distance from start at an early
round (before most first contacts), within layout and opponent, against what happens later.
Usage: python3 tq_early.py [online|ladder] [round, default 30]"""
import sys
import json
from collections import defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    cp = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    tags = ('m1', 'm2', 'b1', 'b2', 'q1') if mode == 'online' else ('L0', 'T0')
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    lay = defaultdict(lambda: defaultdict(list))
    flat = defaultdict(list)
    for g in games:
        R = min(8, (g['w'] + g['h']) // 8)
        for s in (0, 1):
            if g['scomp'][s] * 2 < g['cells']:
                continue
            recs = g['recs'][s]
            at = next((t for t in recs if t[0] == cp), None)
            if at is None:
                continue
            # no enemy head within 5 steps of her on any turn up to the checkpoint: her place is her own choice
            clean = not any(t[31] > 0 for t in recs if t[0] <= cp)
            f = g['fate'][s]
            row = (at[3], f is not None and f['r'] <= cp + 70, f is not None and f['r'] <= 300, f is None,
                   g['win'] is not None and (g['win'] == 1) == (s == 0), at[3] > R + 2, clean, g['game'])
            if mode == 'online':
                who = 'ours' if s == 0 else ('Bob' if g['opp'].startswith('Big') else 'Quiz')
            else:
                who = ('ours ladder', 'ladder opp')[s] if g['label'] == 'ladder' else ('rank1', 'rank1 opp')[s]
            lay[who][(g.get('layout') or g['map'], g['w'], g['h'], g.get('opp'))].append(row)
            flat[who].append(row)
    for who in sorted(lay):
        for name, pick in (('all games alive at r%d' % cp, lambda r: True), ('no enemy head within 5 steps of her up to r%d' % cp, lambda r: r[6])):
            lo, hi = [], []
            for key, v in lay[who].items():
                v = sorted((r for r in v if pick(r)), key=lambda r: (r[0], r[7]))
                if len(v) < 4:
                    continue
                half = len(v) // 2
                lo += v[:half]
                hi += v[len(v) - half:]
            if not lo:
                continue
            n = len(lo)
            print('%-11s %-46s within layout, NEAR half vs FAR half, %3d games each: tiles from start %4.1f vs %4.1f | dead within 70 rounds %3d vs %3d | dead by r300 %3d vs %3d | alive at the end %3d vs %3d | side won %3d vs %3d' % (
                who, name, n, sum(r[0] for r in lo) / n, sum(r[0] for r in hi) / n, sum(r[1] for r in lo), sum(r[1] for r in hi), sum(r[2] for r in lo),
                sum(r[2] for r in hi), sum(r[3] for r in lo), sum(r[3] for r in hi), sum(r[4] for r in lo), sum(r[4] for r in hi)))
        for name, pick in (('all', lambda r: True), ('no enemy head within 5 steps up to the round', lambda r: r[6])):
            num = den = 0.0
            used = nin = nout = din = dout = win_in = win_out = 0
            wnum = 0.0
            for key, v in lay[who].items():
                a = [r for r in v if pick(r) and not r[5]]
                b = [r for r in v if pick(r) and r[5]]
                if not a or not b:
                    continue
                wgt = len(a) * len(b) / (len(a) + len(b))
                num += wgt * (sum(r[1] for r in b) / len(b) - sum(r[1] for r in a) / len(a))
                wnum += wgt * (sum(r[4] for r in b) / len(b) - sum(r[4] for r in a) / len(a))
                den += wgt
                used += 1
                nin += len(a)
                nout += len(b)
                din += sum(r[1] for r in a)
                dout += sum(r[1] for r in b)
                win_in += sum(r[4] for r in a)
                win_out += sum(r[4] for r in b)
            if den:
                print('%-11s stratified by layout and opponent (%s): %d strata with both; inside R+2 at r%d: %d games, dead within 70 rounds %d, won %d | beyond: %d games, dead %d, won %d | weighted difference beyond minus inside: death %+.0f points, wins %+.0f points' % (
                    who, name, used, cp, nin, din, win_in, nout, dout, win_out, 100.0 * num / den, 100.0 * wnum / den))
        v = flat[who]
        a = [r for r in v if not r[5]]
        b = [r for r in v if r[5]]
        if a and b:
            print('%-11s pooled at r%d: at most R+2 from start %3d games, dead within 70 rounds %3d (%2.0f%%), won %3d (%2.0f%%) | beyond R+2 %3d games, dead %3d (%2.0f%%), won %3d (%2.0f%%)' % (
                who, cp, len(a), sum(r[1] for r in a), 100.0 * sum(r[1] for r in a) / len(a), sum(r[4] for r in a), 100.0 * sum(r[4] for r in a) / len(a),
                len(b), sum(r[1] for r in b), 100.0 * sum(r[1] for r in b) / len(b), sum(r[4] for r in b), 100.0 * sum(r[4] for r in b) / len(b)))


main()
