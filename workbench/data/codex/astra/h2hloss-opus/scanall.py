"""Scan every finished head-to-head game once (side 0 = the newer version) and cache one json row per game.
Usage (repo root): python3 -B data/codex/astra/h2hloss-opus/scanall.py [arm ...]"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'tools')
from pathlib import Path
from o1_scan import scan
RUNS = Path.home() / 'meow-redteam/solo/runs'
HERE = Path('data/codex/astra/h2hloss-opus')
ARMS = sys.argv[1:] or ['h2h_mDone11_v8', 'h2h_mDone10_v8', 'h2h_mDone8_v5', 'h2h_mDone11_v5']


def rows(arm):
    cp = HERE / ('scan-%s.jsonl' % arm)
    cache = {}
    if cp.exists():
        for l in cp.read_text().splitlines():
            g = json.loads(l)
            cache[g['folder']] = g
    for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
        if not (folder / 'result.txt').exists() or not (folder / 'game.replay').exists() or folder.name in cache:
            continue
        m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
        k = int(m[3])
        j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
        g = scan(arm, folder / 'game.replay', j)
        g['folder'] = folder.name
        g['resline'] = (folder / 'result.txt').read_text().strip()
        cache[folder.name] = g
    with open(cp, 'w') as f:
        for g in cache.values():
            f.write(json.dumps(g, separators=(',', ':')) + '\n')
    return [cache[k] for k in sorted(cache)]


if __name__ == '__main__':
    for arm in ARMS:
        if not (RUNS / arm).exists():
            continue
        gs = rows(arm)
        print(arm, len(gs), 'games', 'wins', sum(g['result'] == 'win' for g in gs), 'losses', sum(g['result'] == 'loss' for g in gs))
        for g in gs:
            print('  %-42s %-5s %-7s last %d ends %s' % (g['folder'], g['result'], g['how'], g['last'], [e[:4] for e in g['ends']]))
