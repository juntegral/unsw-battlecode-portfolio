"""battle-opus: bat.py list | bat.py <battle id> [all]
list: every battle folder with a game completed after 04:31Z: ranked, opponent, ratings, our bot id per game, results.
<battle id>: l15 summary for each lost game (all = every game)."""
import sys, json, glob, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
sys.path.insert(0, 'data/codex/astra/loss15-sonnet')
from pathlib import Path
from ladder_replay import replay

BASE = Path('data/online/live-one1')


def botid(rp, own):
    try:
        return replay.load(rp).root().text(1 if own == 0 else 2).strip()
    except Exception as ex:
        return 'ERR'


def games(bdir):
    out = []
    for f in sorted(bdir.glob('game-*.json')):
        j = json.load(open(f))
        if 1119 not in (j['teamAId'], j['teamBId']):
            continue
        out.append(j)
    return out


def lst():
    for bdir in sorted(BASE.glob('b*')):
        gs = games(bdir)
        if not gs or max((g.get('completedAt') or '') for g in gs) < '2026-10-09T04:31':
            continue
        j = gs[0]
        own = 0 if j['teamAId'] == 1119 else 1
        res = ''
        bots = set()
        for g in gs:
            rp = bdir / ('M%d.replay' % g['id'])
            bots.add(botid(rp, own) if rp.exists() else 'norep')
            res += 'W' if g['winner'] == 'ab'[own] else ('L' if g['winner'] in ('a', 'b') else '?')
        print('%s %s n=%d seat %s vs %s (%s) us %s  %s  bots %s  elo %s  done %s..%s' % (
            bdir.name, 'ranked' if j['ranked'] else 'unranked', len(gs), 'AB'[own],
            j['teamBName'] if own == 0 else j['teamAName'], j['teamBElo'] if own == 0 else j['teamAElo'],
            j['teamAElo'] if own == 0 else j['teamBElo'], res, sorted(bots),
            j['eloChangeA'] if own == 0 else j['eloChangeB'],
            min(g['completedAt'][11:16] for g in gs), max(g['completedAt'][11:16] for g in gs)))


if sys.argv[1] == 'list':
    lst()
else:
    import l15
    bdir = BASE / ('b' + sys.argv[1])
    for g in games(bdir):
        own = 0 if g['teamAId'] == 1119 else 1
        if g['winner'] != 'ab'[own] or 'all' in sys.argv:
            try:
                l15.show(g['id'])
            except Exception as ex:
                print('ERR', g['id'], repr(ex)[:200])
        else:
            print('--- game %d WIN %s scores %s-%s' % (g['id'], g['mapName'], g['scoresA'], g['scoresB']))
