# Scratch (diag-feeding): the rams that decided a game (leader longer than their final longest, game lost). Prints only.
import json
from pathlib import Path

R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
X = {}
for k in range(2):
    for l in Path('data/analysis/ladder/dossier/work/fd_ram-%d.jsonl' % k).open():
        if l.strip():
            x = json.loads(l)
            X[(x['game'], x['r'], x['id'])] = x
n = alone = seen = fed = 0
for r in sorted(R, key=lambda r: r['game']):
    if r['result'] != 'loss':
        continue
    for d in r['lead_deaths']:
        if d['cause'] == 'headon' and d['o_side'] == 't' and not d['mover'] and d['L'] > r['Te'][1] and r['Ue'][1] <= r['Te'][1]:
            x = X.get((r['game'], d['r'], d['id']))
            n += 1
            if x:
                alone += int(x['own5'] == 0) if x['own5'] is not None else 0
                seen += int(bool(x['seen']))
                fed += int(x['fed10'] > 0)
            print(r['game'], r['layout'], r['rating'], r['ended_by'], 'r', d['r'], 'L', d['L'], 'queen' if d['q'] else '', 'rammer L', d['o_len'], 'ours alive', d['n_left'], 'next longest', d['rest'],
                  'end', r['Ue'][1], 'v', r['Te'][1], '| ours within 5:', x and x['own5'], 'rammer in view:', x and x['seen'], 'at', x and x['then_man'], 'from', x and x['ram_from'], 'fed10', x and x['fed10'])
            break
print('decisive rams', n, 'nobody of ours within 5 at the leader last turn', alone, 'rammer in view then', seen, 'a feeder died near in 10 rounds', fed)
