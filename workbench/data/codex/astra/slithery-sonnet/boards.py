"""Draw our queen's last turns. Usage: boards.py <gid> <r0> <r1>"""
import subprocess, sys, json, glob, os
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm/'
gid, r0, r1 = sys.argv[1:4]
f = glob.glob(ROOT + 'data/online/live-one1/b*/game-%s.json' % gid)[0]
j = json.load(open(f))
q = 0 if j['teamAId'] == 1119 else 1
rp = os.path.dirname(f) + '/M%s.replay' % gid
out = subprocess.run([sys.executable, '-B', 'data/analysis/ladder/dossier/work/o1_look.py', rp, gid, str(q), r0, r1], capture_output=True, text=True, cwd=ROOT)
print('\n'.join(l for l in out.stdout.splitlines() if ' eats ' not in l or ('dragon %d eats' % q) in l))
print(out.stderr[-300:])
