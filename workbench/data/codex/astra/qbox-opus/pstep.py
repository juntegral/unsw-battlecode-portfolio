"""Queen portal steps per game. Usage (from ROOT): pstep.py <arm> ..."""
import sys, glob, os, io, contextlib
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/qbox-opus')
import qd
R = os.path.expanduser('~/meow-redteam/solo/runs/')
for arm in sys.argv[1:]:
    tot = [0, 0, 0, 0]
    for d in sorted(glob.glob(R + arm + '/*-seed*-side*')):
        if not os.path.exists(d + '/result.txt'):
            continue
        k = int(d[-1])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = qd.run(d + '/game.replay', k, 0, True)
        small = [p for p in qd.ALLP if p[1] < 12]
        tot[0] += 1; tot[1] += len(qd.ALLP); tot[2] += len(small); tot[3] += r is not None
        print('%-9s %-42s queen portal steps %2d, into walled rooms under 12 cells %2d %s | %s' % (arm, os.path.basename(d), len(qd.ALLP), len(small), small[:4], 'dead r%d' % r if r is not None else 'alive'))
    print('%-9s TOTAL games %d queen portal steps %d into small rooms %d queen dead %d' % (arm, *tot))
