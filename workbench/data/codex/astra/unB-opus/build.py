"""build one-constant arms off one17. usage: build.py name=CONST:value|-CONST ..."""
import sys, subprocess, os
from pathlib import Path
sw = Path('~/.claude/jobs/e2109d93/tmp/one17.switches').read_text().strip().split(',')
solo = Path.home() / 'meow-redteam/solo'
ps = []
for a in sys.argv[1:]:
    name, ch = a.split('=')
    vals = list(sw)
    for c in ch.split('+'):
        if c.startswith('-'):
            vals = [v for v in vals if v.split(':')[0] != c[1:]]
        else:
            vals = [v for v in vals if v.split(':')[0] != c.split(':')[0]] + [c]
    ps.append((name, subprocess.Popen(['python3', 'tools/mkbots.py', name + '=' + ','.join(vals)], cwd=solo,
                                      env=dict(os.environ, MKSRC='src/solo/main.cpp'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
for name, p in ps:
    out = p.communicate()[0].decode()[-300:]
    print(name, p.returncode, out.strip().replace('\n', ' | '))
