"""unA-opus: build bots/<name> = all-off base plus one17 switches [lo:hi] ('plus'), or one17 minus them ('minus'). spec name:mode:lo:hi"""
import subprocess, os, sys
S = os.path.expanduser('~/meow-redteam/solo')
items = open('~/.claude/jobs/e2109d93/tmp/one17.switches').read().strip().split(',')
ps = []
for spec in sys.argv[1:]:
    name, mode, lo, hi = spec.split(':')
    lo, hi = int(lo), int(hi)
    sel = items[lo:hi] if mode == 'plus' else items[:lo] + items[hi:]
    print(name, mode, ' '.join(i.split(':')[0] for i in items[lo:hi]), flush=True)
    ps.append(subprocess.Popen(['python3', 'tools/mkbots.py', '%s=%s' % (name, ','.join(sel))], cwd=S, env=dict(os.environ, MKSRC='src/solo/main.cpp')))
for p in ps:
    p.wait()
print(len(items))
