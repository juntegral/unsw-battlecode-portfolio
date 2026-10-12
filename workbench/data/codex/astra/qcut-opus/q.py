"""qcut: our queen per round in local runs. Usage (from ROOT): python3 -B data/codex/astra/qcut-opus/q.py <ourseat> <lo> <hi> <folder> [...]"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from pathlib import Path
import ladder_replay as L


def one(folder, seat):
    folder = Path(folder).expanduser()
    j = dict(id=0, teamAId=1119 if seat == 0 else 1, teamBId=1 if seat == 0 else 1119, mapName=folder.name, teamAName='A', teamBName='B')
    g = L.scan(folder / 'game.replay', j, folder.name, set())
    s = g['snapshots']
    last = g['last_round']
    ql = {r: s[r]['us']['queen_length'] for r in s}
    dead = next((r for r in sorted(ql) if r > 0 and ql[r] == 0), None)
    return g, ql, dead, last


if __name__ == '__main__':
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    for f in sys.argv[4:]:
        seat = int(sys.argv[1]) if sys.argv[1] in '01' else int(f.rstrip('/')[-1])
        g, ql, dead, last = one(f, seat)
        fin = g['final']
        res = (Path(f).expanduser() / 'result.txt').read_text().strip()
        def at(r):
            return ql.get(min(r, max(ql)), 0)
        print(Path(f).name, 'qdead', dead, 'L300', at(300), 'L400', at(400), 'end', fin['us']['queen_length'], 'units_end', fin['us']['alive'], 'total', fin['us']['total'], fin['them']['total'], '|', res)
        if hi > lo:
            print('   ', ' '.join('%d:%d(u%d)' % (r, ql.get(r, -1), s['us']['alive']) for r, s in sorted(g['snapshots'].items()) if lo <= r <= hi))
