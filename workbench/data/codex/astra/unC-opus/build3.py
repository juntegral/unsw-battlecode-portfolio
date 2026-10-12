"""unC-opus: one17 arms for the tiny-map bisect. Usage: python3 build3.py <arm> ...   (arms defined below; 'list' prints them)"""
import os, subprocess, sys
S = open('~/.claude/jobs/e2109d93/tmp/one17.switches').read().strip().split(',')
names = [s.split(':')[0] for s in S]
G1 = ['SPLIT_ROUND0', 'EAT_FIRST', 'HEADING_TIE', 'HEADING_TIE_ROUNDS', 'FEEDER_EAT', 'SPLIT_PORTAL_OK', 'ZONE_NEARER', 'POCKET_LOOP',
      'HARVEST_PORTAL', 'SPAWN_CLEAR', 'FEED_CAP_ROUND', 'POCKET_KEEP_OUT', 'TARGET_REACHABLE', 'PORTAL_ID_GUARD', 'MATE_UNPIN']
G3 = ['TRADE_EVEN', 'TRADE_SHORT_BY', 'HUNT_SMALL_RATIO', 'ATTACK_MIN_UNITS', 'LEADER_FULL_UNITS', 'LUNGE_PEARL', 'QUEEN_SURE_LEN',
      'QUEEN_SURE_STEPS', 'QUEEN_AVENGE']
G2 = [n for n in names if n not in G1 and n not in G3]
ARMS = dict(uc_xs=['QUEEN_EXIT_STRICT'], uc_xsk=['QUEEN_EXIT_STRICT', 'QUEEN_EXIT_KEEP'], uc_g1=G1, uc_g2=G2, uc_g3=G3, uc_off=names)
extra = {}
for a in sys.argv[1:]:
    if '=' in a:
        k, v = a.split('=')
        extra[k] = v.split('+')
ARMS.update(extra)
if sys.argv[1:] == ['list']:
    for k, v in ARMS.items():
        print(k, len(v), v)
    sys.exit()
os.chdir(os.path.expanduser('~/meow-redteam/solo'))
procs = []
for arm in [a.split('=')[0] for a in sys.argv[1:]]:
    drop = ARMS[arm]
    assert all(d in names for d in drop), [d for d in drop if d not in names]
    vals = ','.join(s for s in S if s.split(':')[0] not in drop)
    procs.append((arm, subprocess.Popen(['python3', 'tools/mkbots.py', '%s=%s' % (arm, vals)], env=dict(os.environ, MKSRC='src/solo/main.cpp'),
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)))
for arm, p in procs:
    out = p.communicate()[0].strip().splitlines()
    print(arm, out[-1] if out else '', len(ARMS[arm]), 'removed')
