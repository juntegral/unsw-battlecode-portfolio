import re, glob, os
R = os.path.expanduser('~/meow-redteam/solo/runs')
T = '~/.claude/jobs/e2109d93/tmp'
for f in sorted(glob.glob(T + '/one1*.switches')):
    print(os.path.basename(f), 'QUEEN_DEAD_ALL' in open(f).read())
for d in sorted(glob.glob(R + '/qda_mD18/*')):
    n = os.path.basename(d)
    k = int(n[-1])
    out = [n]
    for arm in ('qda_mD18', 'qda_mQDA'):
        p = '%s/%s/%s/result.txt' % (R, arm, n)
        if not os.path.exists(p):
            out.append('-')
            continue
        t = open(p).read()
        w = re.search(r'winner=(\S+)', t)[1]
        how = re.search(r'\((.*?)\)', t)[1]
        fl = re.search(r'final_lengths=(\S+)', t)[1]
        res = 'D' if w == 'draw' else ('W' if int(w) == k else 'L')
        out.append('%s %s [%s]' % (res, how, fl))
    print(' | '.join(out))
