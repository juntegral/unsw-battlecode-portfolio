"""summarise rows-<label>.jsonl from detect.py: per game, our episodes of patterns c/c0/b/a2n/d (our side only, side 0) with round ranges.
Usage (via run2.sh): detsum.py <label> [pattern ...]"""
import sys, json
from pathlib import Path
label = sys.argv[1]
pats = sys.argv[2:] or ['c', 'b']
for l in open(Path('data/codex/astra/loss15-sonnet') / ('rows-%s.jsonl' % label)):
    g = json.loads(l)
    eps = [e for e in g['eps'] if e['side'] == 0 and e['p'] in pats and e['r1'] - e['r0'] >= 14]
    print('%s %s %s eps=%d  our-nsplit=%d' % (g['gid'], g['map'], g['opp'], len(eps), g['nsplit'][0]))
    for e in sorted(eps, key=lambda e: e['r0']):
        print('   %-3s id%-3d q%d r%d-%d L%d-%d cells%d portal%.2f pearl%.2f enemy%.2f eats%d dend%.2f xy%s' % (
            e['p'], e['id'], 1 - e['role'], e['r0'], e['r1'], e['L0'], e['L1'], e['cells'], e['portal'], e['pearl'], e['enemy'], e['eats'], e['dend'], e['xy']))
