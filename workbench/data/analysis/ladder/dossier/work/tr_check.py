"""Scratch (diag-toprams): independent recount of the head-ons on short non-queen dragons, rounds 0 to 150, in the 45 direct games,
with the shared reader tools/ladder_replay.py (not tr_scan.py). Usage: python3 tr_check.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay
from collections import Counter
from pathlib import Path

K = Counter()
for f in sorted(p for p in (Path('data/online') / 'smoke').iterdir() if p.is_dir() and p.name.startswith('top-l')):
    for gj in sorted(f.glob('game-*.json')):
        j = json.loads(gj.read_text())
        rp = f / ('M%d.replay' % j['id'])
        if not rp.is_file() or j.get('status') != 'completed':
            continue
        out = ladder_replay.scan(rp, j, f.name, set())
        K['games'] += 1
        cross = {c['collision'] for c in out['collisions'] if c['cross_team']}
        for d in out['deaths']:
            if d['cause'] != 'head-on' or d['collision'] not in cross or d['round'] > 150:
                continue
            victim = d['id'] != d['actor']
            if not victim:
                continue
            K['victims ' + d['side']] += 1
            if d['length'] <= 4:
                K['victims of 2-4 ' + d['side']] += 1
                if d['id'] != out['queens'][d['side']]:
                    K['victims of 2-4, not the queen ' + d['side']] += 1
for k in sorted(K):
    print(k, K[k])
