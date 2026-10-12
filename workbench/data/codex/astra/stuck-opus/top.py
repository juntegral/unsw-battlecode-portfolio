"""stuck-opus: longest episodes. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/top.py <pattern> <side 0|1> <n> <rows name> [...]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path('data/codex/astra/stuck-opus')
pat, side, top = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
import os
DLO, DHI = float(os.environ.get('DLO', -1)), float(os.environ.get('DHI', 2))
out = []
for n in sys.argv[4:]:
    for l in (HERE / ('rows-%s.jsonl' % n)).read_text().splitlines():
        g = json.loads(l)
        for e in g['eps']:
            if e['p'] == pat and e['side'] == side and DLO <= e['dend'] <= DHI:
                out.append((e['r1'] - e['r0'] + 1, g['key'], g['map'], e))
out.sort(key=lambda t: -t[0])
for d, key, mp, e in out[:top]:
    print('%4d %-28s %-16s id %4d %s r%d-%d L %d>%d cells %d pearl %.2f enemy %.2f portal %.2f eats %d dend %.2f at %s' % (
        d, key, mp, e['id'], 'Q' if e['role'] == 0 else ' ', e['r0'], e['r1'], e['L0'], e['L1'], e['cells'], e['pearl'], e['enemy'], e['portal'], e['eats'], e['dend'], e['xy']))
