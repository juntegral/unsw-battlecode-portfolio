"""watch17-opus: rebuild watch.md = verdicts.md + rep.txt + cmp output. Usage (from ROOT): python3 -B .../mk.py"""
import subprocess, sys
from pathlib import Path
H = Path('data/codex/astra/watch17-opus')
rep = subprocess.run([sys.executable, '-B', str(H / 'rep.py')], capture_output=True, text=True).stdout
cmp_ = subprocess.run([sys.executable, '-B', str(H / 'cmp.py'), 'c1', 's1', 'p1'], capture_output=True, text=True).stdout
v = (H / 'verdicts.md').read_text() if (H / 'verdicts.md').exists() else ''
(H / 'watch.md').write_text('# watch17-opus: one17 (21693) live watch\n\n' + v + '\n```\n' + rep + '\n' + cmp_ + '```\n')
print('watch.md written', len(rep.splitlines()), 'lines')
