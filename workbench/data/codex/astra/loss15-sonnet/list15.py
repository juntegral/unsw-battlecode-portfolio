"""List one15 games (bot id 21583): python3 -B data/codex/astra/loss15-sonnet/list15.py (from ROOT)"""
import sys, json, glob, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
rows = []
for f in glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/one15-*-old/game-*.json'):
    j = json.load(open(f))
    if j['id'] in globals().setdefault('_seen', set()): continue
    _seen.add(j['id'])
    if 1119 not in (j['teamAId'], j['teamBId']): continue
    d = os.path.dirname(f); rp = '%s/M%d.replay' % (d, j['id'])
    if not os.path.exists(rp): continue
    if (j.get('completedAt') or '') < '2026-10-09T02:30': continue
    a = j['teamAId'] == 1119
    try: bot = replay.load(rp).root().text(1 if a else 2).strip()
    except Exception as e: bot = '?'
    if bot != '21583' and 'all' not in sys.argv: continue
    win = j['winner'] == ('a' if a else 'b')
    print(bot, j['id'], 'WIN ' if win else 'LOSS', 'A' if a else 'B', j['mapName'], j['teamBName'] if a else j['teamAName'],
          j['teamBElo'] if a else j['teamAElo'], j['scoresA'], j['scoresB'], j['completedAt'][11:16], d.split('/')[-1], 'ranked' if j['ranked'] else 'test')
