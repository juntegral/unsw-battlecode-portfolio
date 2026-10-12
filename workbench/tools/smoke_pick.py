#!/usr/bin/env python3
"""Pick online replays with visible queen, split, or feed behaviour (offline)."""
import argparse
from collections import deque
import gzip
import importlib
import json
from pathlib import Path
import sys
import struct

BATTLECODE = Path('~/01. Project/개인 프로젝트/battlecode')
DEATHS = ('wall', 'self', 'body', 'head-to-head', 'invalid-action')
DIRECTIONS = ('N', 'E', 'S', 'W')


def parser():
    sys.path.insert(0, str(BATTLECODE))
    return importlib.import_module('replay')


def raw_events(root, rp):
    round_no = -1
    for event in root.pointer(3):
        kind = rp.EVENT_NAMES[event.u16(0)]
        p = event.pointer(0)
        e = {'type': kind, 'round': round_no}
        if kind == 'roundStart':
            round_no = p.i32(0)
            e['round'] = round_no
        elif kind in ('dragonUpdate', 'dragonAction', 'dragonDeath', 'dragonSplit'):
            e['id'] = p.i32(0)
            if kind == 'dragonUpdate':
                e['head'] = rp.point(p.pointer(0))
            elif kind == 'dragonDeath':
                e['reason'] = DEATHS[p.u16(4)] if p.u16(4) < len(DEATHS) else '?'
            elif kind == 'dragonSplit':
                e['childId'] = p.i32(4)
                e['team'] = 'A' if p.u16(8) == 0 else 'B'
                e['parentBody'] = [rp.point(v) for v in p.pointer(0)]
                e['childBody'] = [rp.point(v) for v in p.pointer(1)]
            else:
                action = p.pointer(0)
                k = action.u16(0) if action else -1
                e['action'] = {'kind': ('move', 'split', 'suicide')[k] if 0 <= k < 3 else '?'}
                if k == 0:
                    e['action']['steps'] = [DIRECTIONS[v] for v in action.pointer(0)]
        yield e


def json_events(path):
    with gzip.open(path, 'rt', encoding='utf-8') as handle:
        for line in handle:
            if line.strip():
                e = json.loads(line)
                if 'meta' not in e:
                    yield e


def point(value):
    return (value['x'], value['y']) if isinstance(value, dict) else tuple(value)


def geometry(text):
    teams, heads, edges = {}, {}, {}
    width = height = None
    name = '?'
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == 'MAP':
            width, height = map(int, p[1:3])
        elif p[0] == 'MAP_NAME':
            name = ' '.join(p[1:])
        elif p[0] == 'DRAGON':
            did = len(teams)
            teams[did] = 'A' if int(p[1]) == 0 else 'B'
            heads[did] = (int(p[3]), int(p[4]))
        elif p[0] == 'EDGE' and int(p[2]) == 2:
            row, x = divmod(int(p[1]), width + 1)
            edges[(x % width, (row // 2) % height, 'N' if row % 2 == 0 else 'W')] = int(p[3])
    if width is None or height is None:
        raise ValueError('replay has no MAP dimensions')
    return name, teams, heads, edges, width, height


def facts(directory, game, rp):
    gid = game.get('id', game.get('gameId'))
    root = rp.load(directory / f'M{gid}.replay').root()
    name, teams, heads, edges, width, height = geometry(root.text(0))
    side = game['_side']
    queens = [did for did in (0, 1) if teams.get(did) == side]
    if len(queens) != 1:
        raise ValueError('cannot identify our queen among ids 0/1')
    queen = queens[0]
    steps = deque()
    death, cause, crossings, splits, suicides, last_round = None, '-', 0, 0, 0, -1
    last_action = {}
    source = directory / f'events-{gid}.jsonl.gz'
    events = json_events(source) if source.exists() else raw_events(root, rp)
    for e in events:
        kind = e.get('type')
        round_no = e.get('round', -1)
        last_round = max(last_round, round_no)
        did = e.get('id')
        if kind == 'dragonAction':
            a = e.get('action') or {}
            last_action[did] = a.get('kind')
            if did == queen:
                steps = deque(a.get('steps', []))
            if teams.get(did) == side and round_no >= 300 and a.get('kind') == 'suicide':
                suicides += 1
        elif kind == 'dragonSplit':
            team = e['team']
            teams[did] = team
            teams[e['childId']] = team
            if team == side and 150 <= round_no <= 300:
                splits += 1
            for key, target in (('parentBody', did), ('childBody', e['childId'])):
                if e.get(key):
                    heads[target] = point(e[key][0])
        elif kind == 'dragonUpdate':
            head = point(e['head'])
            if did == queen and steps:
                direction = steps.popleft()
                x, y = heads[queen]
                if direction == 'S':
                    y, direction = (y + 1) % height, 'N'
                elif direction == 'E':
                    x, direction = (x + 1) % width, 'W'
                if (x, y, direction) in edges:
                    crossings += 1
            heads[did] = head
        elif kind == 'dragonDeath' and did == queen:
            death = e['round']
            reason = e.get('reason', '?')
            reasons = {'W': 'wall', 'S': 'self', 'O': 'body', 'H': 'head-to-head', 'A': 'invalid-action'}
            cause = 'suicide' if last_action.get(did) == 'suicide' else reasons.get(str(reason), str(reason))
    result = root.pointer(4)
    winner = ('A', 'B')[result.u16(6)] if result.u16(4) == 1 else None
    standing = result.pointer(0 if side == 'A' else 1)
    return dict(id=gid, map=game.get('mapName') or name, result='draw' if winner is None else 'win' if winner == side else 'loss',
                queen=queen, death=death, cause=cause, alive=death if death is not None else last_round + 1,
                portals=crossings, splits=splits, suicides=suicides, longest=standing.i32(4))


def rank(row, focus):
    queen = row['alive'] + 100 * row['portals']
    scores = {'queen': queen, 'split': row['splits'], 'feed': row['suicides'],
              'all': queen / 500 + row['splits'] + row['suicides']}
    return (-scores[focus], {'loss': 0, 'draw': 1, 'win': 2}[row['result']], str(row['id']))


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('directory', type=Path)
    cli.add_argument('--us', type=int, default=1119)
    cli.add_argument('--n', type=int, default=5)
    cli.add_argument('--focus', choices=('queen', 'split', 'feed', 'all'), default='all')
    args = cli.parse_args()
    if not args.directory.is_dir() or args.n < 1:
        cli.error('directory must exist and --n must be positive')
    rp = parser()
    index_path = args.directory / 'index.json'
    indexed = json.loads(index_path.read_text()).get('games', []) if index_path.exists() else []
    games = {str(g['gameId']): g for g in indexed}
    for path in sorted(args.directory.glob('game-*.json')):
        g = json.loads(path.read_text())
        gid = str(g.get('id', path.stem[5:]))
        games[gid] = {**games.get(gid, {}), **g}
    rows = []
    for gid, game in games.items():
        side = 'A' if game.get('teamAId') == args.us else 'B' if game.get('teamBId') == args.us else None
        if side is None:
            continue
        game['_side'] = side
        game.setdefault('id', gid)
        try:
            rows.append(facts(args.directory, game, rp))
        except (OSError, ValueError, IndexError, KeyError, TypeError, NotImplementedError, struct.error, EOFError) as exc:
            print(f'Skipping game {gid}: {exc}', file=sys.stderr)
    chosen = sorted(rows, key=lambda r: rank(r, args.focus))[:args.n]
    lines = [f'# Replay picks: {args.focus} (team {args.us}, {len(rows)} games)', '',
             '| Game | Map | Result | Queen | Death round / cause | Alive rounds | Portals | Splits 150–300 | Suicides ≥300 | Final longest |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in chosen:
        death = 'survived' if r['death'] is None else f"{r['death']} / {r['cause']}"
        values = [r['id'], r['map'], r['result'], r['queen'], death, r['alive'], r['portals'], r['splits'], r['suicides'], r['longest']]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    lines += ['', 'Ranking: queen = alive rounds + 100×portal crossings; split/feed = respective counts; all = queen/500 + splits + suicides. Losses first on score ties.',
              'Alive rounds count completed rounds before death, or all rounds when surviving. Suicides are actions, not proof that feeding succeeded.']
    if not rows:
        lines += ['', 'No readable replays for this team.']
    output = '\n'.join(lines) + '\n'
    (args.directory / 'pick.md').write_text(output, encoding='utf-8')
    print(output, end='')
    return 0 if rows else 1


if __name__ == '__main__':
    sys.exit(main())
