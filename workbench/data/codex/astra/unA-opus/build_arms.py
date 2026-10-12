"""unA-opus: one17 with one switch changed back, built into solo/bots/ua_<arm>."""
import subprocess, os, sys
S = os.path.expanduser('~/meow-redteam/solo')
base = open('~/.claude/jobs/e2109d93/tmp/one17.switches').read().strip()
arms = dict(a.split('=') for a in sys.argv[1:])
specs = []
for name, change in arms.items():
    k, v = change.split(':')
    items = [i for i in base.split(',') if i.split(':')[0] != k]
    if v != 'default':
        items.append('%s:%s' % (k, v))
    specs.append('%s=%s' % (name, ','.join(items)))
env = dict(os.environ, MKSRC='src/solo/main.cpp')
ps = [subprocess.Popen(['python3', 'tools/mkbots.py', s], cwd=S, env=env) for s in specs]
for p in ps:
    p.wait()
