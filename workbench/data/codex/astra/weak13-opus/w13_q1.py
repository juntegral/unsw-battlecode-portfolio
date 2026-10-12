"""The 15-game unranked set one13 v Quaker Qubits (one13-q1-old): result and the home-area lines of w13_home.py per game.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_q1.py > data/codex/astra/weak13-opus/q1.txt"""
import json, subprocess, sys
from pathlib import Path
F = Path('data/online/smoke/one13-q1-old')
for mp in sorted(F.glob('game-*.json')):
    j = json.loads(mp.read_text())
    own = 'a' if j['teamAId'] == 1119 else 'b'
    won = (j.get('winner') or '').lower() == own
    print('%s side %s score us %s them %s' % ('WIN ' if won else 'LOSS', own.upper(), j['scores' + own.upper()], j['scores' + ('B' if own == 'a' else 'A')]))
    out = subprocess.run([sys.executable, '-B', 'data/codex/astra/weak13-opus/w13_home.py', str(F), str(j['id'])], capture_output=True, text=True)
    print(out.stdout.rstrip() or out.stderr[-300:])
