# Scratch (diag-stripes): list the games of one layout from the dossier's per-game rows, and all layouts' basics.
# Usage: python3 data/analysis/ladder/dossier/work/st_games.py
import sys, json
from collections import defaultdict

rows = {}
lay = defaultdict(lambda: [0, 0, None])
with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r['relation'] != 'us':
            continue
        k = r['layout_key']
        lay[k][0] += 1
        lay[k][1] += r['our_result'] == 'win'
        lay[k][2] = (r['width'], r['height'], len(r['all_starting_dragons']['us']), r['all_starting_dragons']['us'][0]['length'], r['replay'])
        if k.startswith('Stripes'):
            rows[r['game']] = dict(game=r['game'], battle=r['battle'], replay=r['replay'], rating=r['opponent_rating'],
                                   our_side=r['our_side'], result=r['our_result'], ended_by=r['ended_by'],
                                   last_round=r['last_round'], keys=sorted(r.keys()), rk=sorted(r['ranges'].keys()))
out = sorted(rows.values(), key=lambda r: r['game'])
print('keys', out[0]['keys'])
print('ranges', out[0]['rk'])
for r in out:
    del r['keys'], r['rk']
    print(json.dumps(r))
for k, v in sorted(lay.items()):
    print(k, v)
