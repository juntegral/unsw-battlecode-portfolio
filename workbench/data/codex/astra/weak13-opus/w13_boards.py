"""Draws our queen's last own turns in the six lost games with o1_look.py (7 by 7 boards) into queen-boards.txt.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_boards.py"""
import subprocess, sys
LOOK = 'data/analysis/ladder/dossier/work/o1_look.py'
JOBS = [('b1508960', 1508962, 'Slithery Fight', 1, 371, 374), ('b1508960', 1508963, 'Islands', 0, 336, 339),
        ('b1513119', 1513119, 'Queen Of Spades', 0, 72, 74), ('b1513119', 1513120, 'Trauma', 1, 351, 353),
        ('b1513119', 1513121, 'Stripes', 0, 147, 149), ('b1513119', 1513123, 'Slithery Fight', 0, 283, 285)]
with open('data/codex/astra/weak13-opus/queen-boards.txt', 'w') as f:
    for b, g, m, q, r0, r1 in JOBS:
        f.write('== %d %s, our queen #%d, r%d-%d (H head, b own body, M/m mate head/body, E/e enemy head/body, o pearl; '
                'capital NESW kelp edge, small nesw portal edge)\n' % (g, m, q, r0, r1))
        out = subprocess.run([sys.executable, '-B', LOOK, 'data/online/live-one1/%s/M%d.replay' % (b, g), str(g), str(q), str(r0), str(r1)],
                             capture_output=True, text=True)
        f.write(''.join(line + '\n' for line in out.stdout.splitlines() if ' eats ' not in line or ('dragon %d eats' % q) in line))
        f.write(out.stderr[-300:])
