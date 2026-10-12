"""First round where our queen's body differs between two local replays. Usage (ROOT): qdiff.py <replayA> <replayB> [r1]"""
import sys, subprocess, re
a, b = sys.argv[1], sys.argv[2]
r1 = sys.argv[3] if len(sys.argv) > 3 else '499'


def heads(p):
    out = subprocess.run([sys.executable, 'data/analysis/ladder/dossier/work/o1_look.py', p, '0', '0', '0', r1],
                         capture_output=True, text=True).stdout
    d = {}
    for l in out.splitlines():
        m = re.match(r'r(\d+) head .* body (\[.*?\]) \|', l)
        if m:
            d[int(m[1])] = m[2]
    return d


A, B = heads(a), heads(b)
for r in sorted(set(A) | set(B)):
    if A.get(r) != B.get(r):
        print('first queen difference r%d' % r)
        for k in range(max(0, r - 2), r + 6):
            print(k, 'A', A.get(k), '| B', B.get(k))
        break
else:
    print('queen identical through r%s' % r1, len(A), len(B))
