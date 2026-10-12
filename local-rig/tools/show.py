#!/usr/bin/env python3
"""Print a replay's board and live dragons, at the end of round N (0 = initial).

The packed reader is adapted from the harness; event layouts and state updates
match the replay viewer shipped with engine version 1.2.7.
"""
import argparse
from collections import deque
from pathlib import Path
import sys

from replay_format import load, point


def snapshot(path, requested_round=None):
    root = load(path).root()
    map_text = root.text(0)
    dragons, edges, pearls, countdowns = {}, {}, set(), {}
    width = height = 0
    map_name = ''
    for line in map_text.splitlines():
        fields = line.split('#', 1)[0].split()
        if not fields:
            continue
        if fields[0] == 'MAP':
            width, height = map(int, fields[1:3])
        elif fields[0] == 'MAP_NAME':
            map_name = ' '.join(fields[1:])
        elif fields[0] == 'EDGE':
            edge_id, kind, partner = map(int, fields[1:4])
            edges[edge_id] = (kind, partner)
        elif fields[0] == 'DRAGON':
            team, length = map(int, fields[1:3])
            coords = list(map(int, fields[3:]))
            if len(coords) != 2 * length:
                raise ValueError('bad dragon body in replay map')
            dragons[len(dragons)] = {'team': team,
                                     'body': deque(zip(coords[::2], coords[1::2]))}
    if width <= 0 or height <= 0:
        raise ValueError('replay contains no valid map')
    events = list(root.pointer(3))
    max_round = max((event.pointer(0).i32(0) + 1 for event in events
                     if event.u16(0) == 0), default=0)
    selected = max_round if requested_round is None else requested_round
    if not 0 <= selected <= max_round:
        raise ValueError(f'round must be between 0 and {max_round}')
    current = 0
    for event in events:
        kind, payload = event.u16(0), event.pointer(0)
        if kind == 0:  # roundStart, zero-based in the engine wire format
            current = payload.i32(0) + 1
            if current > selected:
                break
        elif kind == 2:  # pearlCountdown
            countdowns[point(payload.pointer(0))] = payload.i32(0)
        elif kind == 3:  # tileChange
            cell = point(payload.pointer(0))
            if payload.bit(0):
                pearls.add(cell)
            else:
                pearls.discard(cell)
        elif kind == 9:  # dragonUpdate; same append/pop rules as shipped viewer
            dragon = dragons.get(payload.i32(0))
            if dragon is None:
                raise ValueError('update references an unknown dragon')
            body = dragon['body']
            body.appendleft(point(payload.pointer(0)))
            tail = point(payload.pointer(1))
            while len(body) > 1 and body[-1] != tail:
                body.pop()
            dragon['facing'] = ('N', 'E', 'S', 'W')[payload.u16(4)]
        elif kind == 10:  # dragonSplit, includes full parent/child bodies
            parent, child, team = payload.i32(0), payload.i32(4), payload.u16(8)
            dragons[parent] = {'team': team, 'body': deque(point(p) for p in payload.pointer(0))}
            dragons[child] = {'team': team, 'body': deque(point(p) for p in payload.pointer(1)),
                              'facing': ('N', 'E', 'S', 'W')[payload.u16(10)]}
        elif kind == 11:  # dragonDeath
            dragons.pop(payload.i32(0), None)
    result = root.pointer(4)
    standings = []
    for side in (0, 1):
        standing = result.pointer(side)
        standings.append({'dragons': standing.i32(0), 'longest': standing.i32(4),
                          'total': standing.i32(8), 'queen': standing.i32(12)})
    return dict(width=width, height=height, map_name=map_name, round=selected,
                max_round=max_round, dragons=dragons, edges=edges, pearls=pearls,
                countdowns=countdowns, standings=standings,
                winner=result.u16(6) if result.u16(4) == 1 else 'draw',
                end_reason=('elimination', 'round_limit')[result.u16(2)],
                terminated=result.bit(0))


def render(state):
    width, height = state['width'], state['height']
    board = [[' ' for _ in range(2 * width + 1)] for _ in range(2 * height + 1)]
    for y in range(height):
        for x in range(width):
            board[2*y+1][2*x+1] = '*' if (x, y) in state['pearls'] else '.'
    for edge_id, (kind, partner) in state['edges'].items():
        row, x = divmod(edge_id, width + 1)
        if row % 2 == 0:
            if x >= width:  # padded slot in the wire map, not a real edge
                continue
            y = row // 2
            if kind:
                board[2*y][2*x+1] = '#' if kind == 1 else '@'
        else:
            y = (row-1) // 2
            if kind:
                board[2*y+1][2*x] = '#' if kind == 1 else '@'
    for dragon in state['dragons'].values():
        for index, (x, y) in enumerate(dragon['body']):
            char = ('A' if index == 0 else 'a') if dragon['team'] == 0 else ('B' if index == 0 else 'b')
            board[2*y+1][2*x+1] = char
    print(f'map={state["map_name"]} size={width}x{height} round={state["round"]}/{state["max_round"]}')
    print('Legend: A/B heads (side 0/1), a/b bodies, * pearl, . empty, # kelp edge, @ portal edge')
    print('Coordinates: x grows right, y grows down; map boundaries wrap.')
    for line in board:
        print(''.join(line))
    for dragon_id, dragon in sorted(state['dragons'].items()):
        print(f'dragon id={dragon_id} team={dragon["team"]} length={len(dragon["body"])} '
              f'position={dragon["body"][0]} body={list(dragon["body"])}')
    if not state['dragons']:
        print('(no live dragons)')
    if state['round'] == state['max_round']:
        print(f'final winner={state["winner"]} how={state["end_reason"]} '
              f'lengths={state["standings"][0]["total"]},{state["standings"][1]["total"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('--round', type=int)
    args = parser.parse_args()
    try:
        render(snapshot(args.replay, args.round))
    except (OSError, ValueError, IndexError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
