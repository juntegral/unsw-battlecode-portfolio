"""Queen timeline per game: snapshots from r250, queen splits after r250, queen death. Usage: qline.py "Slithery Fight" [loss|all]"""
import sys
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
MAP = sys.argv[1]
SEL = sys.argv[2] if len(sys.argv) > 2 else 'loss'
for r in table.rows:
    if r['map'] != MAP or (SEL != 'all' and r['result'] != SEL):
        continue
    sn = r['snaps']
    ks = sorted(int(k) for k in sn)
    print('=== %d %s %s one%s opp %s %s' % (r['gid'], r['map'], r['result'], table.VER[r['bot']][3:], r['opp'], table.klass(r)))
    for s, lab in ((0, 'us  '), (1, 'them')):
        print(' ', lab, 'Q@', ' '.join('%d:%d' % (k, sn[str(k)][s][3]) for k in ks if k >= 250 and k % 50 == 0 or k == ks[-1]),
              '| longest@', ' '.join('%d:%d' % (k, sn[str(k)][s][2]) for k in ks if k >= 250 and k % 50 == 0 or k == ks[-1]),
              '| n@', ' '.join('%d:%d' % (k, sn[str(k)][s][0]) for k in ks if k >= 250 and k % 50 == 0))
        qs = [(x[0], x[2], x[3], x[4]) for x in r['splits'] if x[1] == s and x[5] and x[0] >= 150]
        print('    queen splits >=r150 (round, before, kept, child):', qs)
        qd = [(d[0], 'L%d' % d[2], d[4], d[18]) for d in r['deaths'] if d[1] == s and d[6]]
        print('    queen death:', qd)
