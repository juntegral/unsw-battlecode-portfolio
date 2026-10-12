"""Which opponents pay in ranked battles: per opponent, our game wins and rating change over recent ranked battles, and our
win share in unranked sets. Expected score from the rating gap (Elo, 400 scale) beside the actual share."""
import json, subprocess, collections, os
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
bs = json.loads(subprocess.run(['node', 'tools/online.js', 'battles', '--limit', '200', '--json'], capture_output=True, text=True).stdout)
us_elo = json.loads(subprocess.run(['node', 'tools/online.js', 'leaderboard', '--json'], capture_output=True, text=True).stdout)['us']['elo']
R = collections.defaultdict(lambda: dict(rw=0, rg=0, rb=0, elo=0.0, uw=0, ug=0, oe=0, id=None))
for b in bs:
    if (b.get('at') or '') < '2026-10-08T15':
        continue
    res = [r for r in (b.get('results') or []) if r in ('win', 'loss')]
    if not res:
        continue
    o = R[str(b.get('opponent'))[:22]]
    o['oe'] = b.get('opponentElo') or o['oe']; o['id'] = b.get('opponentId')
    w = sum(1 for r in res if r == 'win')
    if b.get('ranked'):
        o['rw'] += w; o['rg'] += len(res); o['rb'] += 1; o['elo'] += b.get('eloChange') or 0
    else:
        o['uw'] += w; o['ug'] += len(res)
print('our rating', us_elo)
print('%-22s %5s %5s  ranked games  share  expect  rating change (battles)   unranked' % ('opponent', 'id', 'elo'))
rows = []
for n, o in R.items():
    g = o['rg'] + o['ug']
    if g < 5 or not o['oe']:
        continue
    exp = 1 / (1 + 10 ** ((o['oe'] - us_elo) / 400))
    share = (o['rw'] + o['uw']) / g
    rows.append((share - exp, n, o, exp, share))
for d, n, o, exp, share in sorted(rows, reverse=True):
    print('%-22s %5s %5s  %3d/%-3d       %3.0f%%   %3.0f%%   %+5.0f (%d)              %d/%d   edge %+3.0f%%' % (
        n, o['id'], o['oe'], o['rw'], o['rg'], 100 * o['rw'] / o['rg'] if o['rg'] else 0, 100 * exp, o['elo'], o['rb'], o['uw'], o['ug'], 100 * d))
