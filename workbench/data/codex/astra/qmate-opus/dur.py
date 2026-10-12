"""qmate-opus: how long local games took today (log file birth to result.txt), by map."""
from pathlib import Path
from collections import defaultdict
import re, time
R = Path.home() / 'meow-redteam/solo/runs'
d = defaultdict(list)
now = time.time()
for res in R.glob('*/*/result.txt'):
    f = res.parent
    log = f.parent / (f.name + '.log')
    if not log.exists() or now - res.stat().st_mtime > 3 * 3600:
        continue
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', f.name)
    if m:
        d[m[1]].append(res.stat().st_mtime - log.stat().st_birthtime)
for k, v in sorted(d.items()):
    v.sort()
    print('%-34s n=%3d median %4.0fs max %4.0fs' % (k, len(v), v[len(v) // 2], v[-1]))
