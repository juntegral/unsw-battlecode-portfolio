"""watch19-opus: rebuild watch.md = verdicts.md + lines.txt. Usage (from ROOT): python3 -B .../mk19.py"""
from pathlib import Path
H = Path('data/codex/astra/watch19-opus')
(H / 'watch.md').write_text('# watch19-opus: one19 (21827) live watch\n\n' + (H / 'verdicts.md').read_text() + '\n```\n' + (H / 'lines.txt').read_text() + '```\n')
print('watch.md written')
