import sys
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/codex/astra/stuck-opus', 'data/codex/astra/skku']
import json, glob, os
import analyze
want = {1514290: 327, 1533125: 61, 1527401: 57, 1519940: 230, 1527404: 199, 1514289: 22, 1526090: 86}
for mp in glob.glob('data/online/live-one1/b*/game-*.json'):
    gid = int(os.path.basename(mp)[5:-5])
    if gid not in want: continue
    j = json.load(open(mp)); d = analyze.details(os.path.join(os.path.dirname(mp), f'M{gid}.replay'), j)
    q = d['queens'][0]; r0 = want[gid]
    print('==', gid, j['mapName'], 'our queen id', q, 'death r', r0, 'logs total', len(d['logs']))
    for l in d['logs']:
        if l['id'] == q and r0 - 2 <= l['r'] <= r0: print('  ', l['r'], l['text'][:300])
    for t in d['turns']:
        if t['id'] == q and r0 - 3 <= t['r'] <= r0: print('   turn', t['r'], 'L', t['L'], 'h', t['h'], 'path', t['path'], 'eat', t['eat'], 'split', t['split'])
    for rec in d['qturn'][0][-3:]: print('   view', rec['r'], 'h', rec['h'], 'L', rec['L'], 'foes', [(f['id'], f['L'], f['h']) for f in rec['foes']], 'pearls', rec['pearls'][:6], 'units', rec['units'])
