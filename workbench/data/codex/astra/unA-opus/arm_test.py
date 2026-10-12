"""unA-opus: replay a map with an arm in seat A against a named opponent. args: map_stem opp arm [arm ...]; waits for the main runner."""
import subprocess, sys, time
from pathlib import Path
RT = Path.home() / 'meow-redteam'
HERE = Path(__file__).resolve().parent
if 0:
    time.sleep(2)
stem, opp = sys.argv[1], sys.argv[2]
mp = next(p for p in [RT / 'maps/un2' / (stem + '.map'), RT / 'maps/ladder' / (stem + '.map')] if p.exists())
for arm in sys.argv[3:]:
    for k in (0,):
        out = RT / 'solo/runs' / ('ua_arm_%s_v_%s' % (arm, opp)) / ('%s-seed1-side%d' % (stem, k))
        if not (out / 'result.txt').exists():
            out.mkdir(parents=True, exist_ok=True)
            a, b = (arm, opp) if k == 0 else (opp, arm)
            with open(str(out) + '.log', 'w') as f:
                subprocess.run([str(RT / 'play.sh'), str(RT / 'solo/bots' / a), str(RT / 'solo/bots' / b), str(mp), '1', str(out)], cwd=str(RT), stdout=f, stderr=subprocess.STDOUT)
        print(arm, opp, out.name, (out / 'result.txt').read_text().strip()[:130] if (out / 'result.txt').exists() else 'NO RESULT', flush=True)
