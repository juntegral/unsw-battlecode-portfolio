"""Wrap-up, read-only: size of what git ignores in unsw-swarm outside data/ (old study caches and the like)."""
import os, subprocess
S = '~/01. Project/개인 프로젝트/unsw-swarm'
out = subprocess.run(['git', '-C', S, 'status', '--ignored', '--short', '-z'], capture_output=True).stdout.decode().split('\0')
rows, tot = [], 0
for l in out:
    if not l.startswith('!! ') or l[3:].startswith('data/'):
        continue
    rel = l[3:]
    p = os.path.join(S, rel)
    n = 0
    if os.path.isdir(p):
        for dp, dn, fn in os.walk(p):
            for f in fn:
                try:
                    n += os.path.getsize(os.path.join(dp, f))
                except OSError:
                    pass
    elif os.path.isfile(p):
        n = os.path.getsize(p)
    tot += n
    rows.append((n, rel))
for n, l in sorted(rows, reverse=True)[:16]:
    print(f'{n/1e6:8.1f}MB {l}')
print('total ignored outside data', f'{tot/1e6:.0f}MB', len(rows), 'entries')
