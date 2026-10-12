"""unA-opus: build bots/<name> = one18 minus the named constants. args: name CONST [CONST ...]"""
import subprocess, os, sys
S = os.path.expanduser('~/meow-redteam/solo')
items = open('~/.claude/jobs/e2109d93/tmp/one18.switches').read().strip().split(',')
name, drop = sys.argv[1], set(sys.argv[2:])
assert drop <= {i.split(':')[0] for i in items}, drop
sel = [i for i in items if i.split(':')[0] not in drop]
print(len(items), 'switches, kept', len(sel), flush=True)
subprocess.run(['python3', 'tools/mkbots.py', '%s=%s' % (name, ','.join(sel))], cwd=S, env=dict(os.environ, MKSRC='src/solo/main.cpp'))
