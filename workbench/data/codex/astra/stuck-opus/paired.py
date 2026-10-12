"""stuck-opus: our looping share per map, one column per online set (same 15 maps each). Usage (ROOT): python3 -B data/codex/astra/stuck-opus/paired.py [class|tot] <set> <set> ..."""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path('data/codex/astra/stuck-opus')
cls = sys.argv[1]
sets = sys.argv[2:]
tab = {}
for n in sets:
    p = HERE / ('rows-%s.jsonl' % n)
    if not p.exists():
        continue
    for l in p.read_text().splitlines():
        g = json.loads(l)
        alive = sum(g['cnt'][0][ro][ph]['n'] for ro in range(2) for ph in range(3))
        loop = sum(v for ph in range(3) for c, v in g['lc'][0][ph].items() if cls == 'tot' or c == cls)
        oal = sum(g['cnt'][1][ro][ph]['n'] for ro in range(2) for ph in range(3))
        olp = sum(v for ph in range(3) for c, v in g['lc'][1][ph].items() if cls == 'tot' or c == cls)
        tab.setdefault(g['map'], {})[n] = (loop, alive, olp, oal, g['last'])
print('class %s: our looping dragon-rounds / our share %% (their share %%), last round' % cls)
print('%-16s' % 'map' + ''.join('%-24s' % s for s in sets))
tot = {s: [0, 0, 0, 0, 0] for s in sets}
for m in sorted(tab):
    line = '%-16s' % m[:15]
    for s in sets:
        if s in tab[m]:
            lp, al, ol, oa, last = tab[m][s]
            line += '%5d %4.1f (%4.1f) r%-3d   ' % (lp, 100 * lp / max(al, 1), 100 * ol / max(oa, 1), last)
            for z, v in enumerate((lp, al, ol, oa)):
                tot[s][z] += v
            tot[s][4] += 1
        else:
            line += '%-24s' % '-'
    print(line)
print('%-16s' % 'ALL' + ''.join('%5d %4.1f (%4.1f) n=%-3d  ' % (t[0] / max(t[4], 1), 100 * t[0] / max(t[1], 1), 100 * t[2] / max(t[3], 1), t[4]) for t in (tot[s] for s in sets)))
