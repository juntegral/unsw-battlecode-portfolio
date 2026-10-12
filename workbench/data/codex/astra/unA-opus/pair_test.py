"""unA-opus: play bot (seat A) v opponent on several maps, one after another. args: bot opp map_stem [map_stem ...]"""
import subprocess, sys
from pathlib import Path
RT = Path.home() / 'meow-redteam'
UN = Path('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unseen/maps')
bot, opp = sys.argv[1], sys.argv[2]
for stem in sys.argv[3:]:
    mp = next(p for p in [RT / 'maps/un2' / (stem + '.map'), RT / 'maps/ladder' / (stem + '.map'), RT / 'maps/gx' / (stem + '.map'), UN / (stem + '.map')] if p.exists())
    out = RT / 'solo/runs' / ('ua_arm_%s_v_%s' % (bot, opp)) / ('%s-seed1-side0' % stem)
    if not (out / 'result.txt').exists():
        out.mkdir(parents=True, exist_ok=True)
        with open(str(out) + '.log', 'w') as f:
            subprocess.run([str(RT / 'play.sh'), str(RT / 'solo/bots' / bot), str(RT / 'solo/bots' / opp), str(mp), '1', str(out)], cwd=str(RT), stdout=f, stderr=subprocess.STDOUT)
    print(bot, opp, stem, (out / 'result.txt').read_text().strip()[:130] if (out / 'result.txt').exists() else 'NO RESULT', flush=True)
