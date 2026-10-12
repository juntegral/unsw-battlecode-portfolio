"""Queen deaths in the online Portals games. Usage (from ROOT): on1.py [boards] [ids...]"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/qbox-opus')
import qd
nb = int(sys.argv[1]) if len(sys.argv) > 1 else 0
ids = [int(x) for x in sys.argv[2:]]
if not ids:
    ids = [int(l.split()[0]) for l in open('data/codex/astra/slithery-sonnet/qd-portals.txt').read().splitlines()[1:31]]
for g in ids:
    fs = glob.glob('data/online/live-one1/b*/game-%d.json' % g) + glob.glob('data/online/smoke/*/game-%d.json' % g)
    if not fs:
        print(g, 'not found')
        continue
    j = json.loads(open(fs[0]).read())
    own = 0 if j['teamAId'] == 1119 else 1
    qd.run(fs[0].replace('game-%d.json' % g, 'M%d.replay' % g), own, nb, nb == 0)
