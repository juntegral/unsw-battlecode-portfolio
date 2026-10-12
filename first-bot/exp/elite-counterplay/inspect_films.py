#!/usr/bin/env python3
"""Readable traces of every preselected replay; no extra game selection.

Usage: guard.py python3 exp/elite-counterplay/inspect_films.py TEAM_ID
Pointer rounds are zero-based roundStart values. The JSON films preserve the
complete tracked action histories; this view prints state transitions and the
last three victims, final-line feeding, invading heads and relevant move windows.
"""
from pathlib import Path
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / '.cache/elite-counterplay'
manifest = json.loads((C / 'manifest.json').read_text())
tasks = {t['key']: t for t in manifest['tasks']}
team = int(sys.argv[1])

def action(a):
    h, e = a['head'], a['end']
    return (f"r{a['r']} #{a['id']} {a['team']} L{a['L']} ({h['x']},{h['y']})->({e['x']},{e['y']}) "
            f"{a['kind']} {a['steps']} a3/e3={a['a3']}/{a['e3']} a8/e8={a['a8']}/{a['e8']} "
            f"{a['tag'].split('|')[0].strip()}")

for row in json.loads((C / 'film-index.json').read_text()):
    if row['team'] != team:
        continue
    g = json.loads((ROOT / row['file']).read_text())
    task = tasks[g['key']]
    t = task['us'] or ('A' if task['teamA'] == manifest['names'][str(team)] else 'B')
    e = 'B' if t == 'A' else 'A'
    print('\nGAME', g['key'], g['map'], row['kind'], 'subject', t, 'rounds', g['rounds'], 'result', g['result'])
    for s in g['snaps']:
        if s['r'] in [0, 30, 50, 100, 250, 340, 350, 400, 450, 499]:
            a,b=s[t],s[e]
            print(f"STATE r{s['r']} {t}:u{a['u']} M{a['total']} K#{a['kingId']} L{a['kingLen']} | {e}:u{b['u']} M{b['total']} K#{b['kingId']} L{b['kingLen']}")
    for side in [t, e]:
        print('FINAL LINE', side, 'generations', max(0, len(g['line'][side]) - 1), g['line'][side][-4:])
    kills = [d for d in g['deaths'] if d['team'] == t and d['king'] and d['L'] >= 8 and d['cause'] == 'rammed']
    victims = [d for d in g['deaths'] if d['team'] == t]
    important = {d['id']: d for d in kills + victims[-3:]}
    for d in important.values():
        print('DEATH', {k: d[k] for k in ['r', 'id', 'L', 'head', 'cause', 'king', 'killer', 'killerLen', 'killerSteps', 'tag']})
        for id in [d['id'], d['killer']]:
            for a in g['actions'].get(str(id), []):
                if d['r'] - 2 <= a['r'] <= d['r']:
                    print('TRACE', action(a))
    for side in [t, e]:
        line_ids = {d['id'] for d in g['line'][side]}
        for id in line_ids:
            acts = g['actions'].get(str(id), [])
            for a in acts:
                if a['r'] in [100, 250, 340, 350, 450, 497, 498, 499]:
                    print('LINE TRACE', action(a))
        ee = [x for x in g['eats'] if x['team'] == side]
        print('EAT', side, 'natural', sum(x['origin'] < 0 for x in ee), 'drops', sum(x['origin'] >= 0 for x in ee))
        late_line = [x for x in ee if x['origin'] >= 0 and x['id'] in line_ids and x['r'] >= 350]
        for x in late_line[-5:]:
            d = g['deaths'][x['origin']]
            print('LINE DROP', f"r{x['r']} #{x['id']} ate ({x['x']},{x['y']}) from r{d['r']} #{d['id']} {d['team']} L{d['L']} {d['cause']}")
    for id, count in g['invaders']:
        et = g['dragons'][str(id)]['team']
        print('INVADER', id, et, 'natural eaten on other starting territory', count)
        for a in g['actions'].get(str(id), []):
            if a['r'] in [30, 50, 100, 250, 340, 350, 400, 450]:
                print('INVADER TRACE', action(a))
    print('SPLITS per phase', {side: [sum(s['team'] == side and lo <= s['r'] < hi for s in g['splits'])
                                      for lo, hi in [(0, 100), (100, 250), (250, 350), (350, 450), (450, 500)]]
                                for side in ['A', 'B']})
