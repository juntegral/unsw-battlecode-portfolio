#!/usr/bin/env python3
"""Freeze every requested local game, before classification or deep replay reading.

No network. Writes only new elite-counterplay paths. Existing input files are read-only.
Selection fixed now: each opponent's largest mutually exclusive primary loss class
(tie: class priority), lowest two game IDs, plus lowest-ID primary win. If no win,
record its absence. Top examples: lowest-ID nonstalled victory displaying the same
signature measured by aggregate.py. No sample is used for population statistics.
"""
from pathlib import Path
from datetime import datetime
import json
import hashlib

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.cache/elite-counterplay'
NAMES = {306: 'Cutlery', 70: 'cheji bt', 20: 'calc', 801: '中国必须人能飞😡',
         264: 'forgot to mention', 46: 'Sabotage-d', 545: 'dev test 1 :P'}
PRIMARY = ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2',
           'cand-stack7-online', 'cand-stack8-online', 'cand-stack9-online']
CONTRAST = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3',
            *[f'cand-stack{i}-online' for i in range(1, 5)]]
R500 = ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']

def main():
    target = OUT / 'manifest.json'
    if target.exists():
        raise SystemExit('Frozen manifest already exists; never replace it.')
    OUT.mkdir(parents=True, exist_ok=True)
    # W11 did not exist during the initial inventory at 23:14 KST on 2026-09-30.
    # Keep that start-of-study boundary even if a new wave arrives while we work.
    tasks, missing, inputs = [], [], []
    for era, sets in [('primary', PRIMARY), ('contrast', CONTRAST)]:
        for s in sets:
            f = ROOT / 'data/online' / s / 'index.json'
            raw = f.read_bytes()
            inputs.append({'path': str(f.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
            for g in json.loads(raw)['games']:
                if g['opponentTeam'] not in NAMES:
                    raise ValueError(f'Unexpected team {g}')
                file = f.parent / f"M{g['gameId']}.replay"
                row = {'key': f"{s}:{g['gameId']}", 'file': str(file.relative_to(ROOT)),
                       'era': era, 'src': 'online', 'set': s, 'map': g['mapName'],
                       'kind': 'r500' if g['mapName'] in R500 else 'elim', 'gameId': g['gameId'],
                       'oppId': g['opponentTeam'], 'us': g['ourSide'].upper(),
                       'teamA': '583' if g['ourSide'].upper() == 'A' else NAMES[g['opponentTeam']],
                       'teamB': '583' if g['ourSide'].upper() == 'B' else NAMES[g['opponentTeam']],
                       'winnerIdx': (g.get('winner') or '').upper() or None,
                       'sub': g.get('ourSubmission'), 'at': g.get('completedAt')}
                (tasks if file.exists() else missing).append(row)
    f = ROOT / 'data/top/index.jsonl'
    raw = f.read_bytes()
    inputs.append({'path': str(f.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
    seen, duplicate = set(), 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        g = json.loads(line)
        if not any(g[s] in NAMES.values() for s in ['teamA', 'teamB']):
            continue
        key = f"{g['battleId']}:{g['gameId']}"
        if key in seen:
            duplicate += 1
            continue
        seen.add(key)
        file = ROOT / 'data/top' / str(g['battleId']) / f"{g['gameId']}.replay.gz"
        row = {'key': key, 'file': str(file.relative_to(ROOT)), 'era': 'reference', 'src': 'top',
               'map': g['map'], 'kind': 'r500' if g['map'] in R500 else 'elim',
               **{k: g[k] for k in ['gameId', 'battleId', 'teamA', 'teamB', 'eloA', 'eloB', 'at']},
               'us': None, 'winnerIdx': (g.get('winner') or '').upper() or None}
        (tasks if file.exists() else missing).append(row)
    obj = {'startedAt': '2026-09-30T23:14:06+09:00', 'frozenAt': datetime.now().astimezone().isoformat(),
           'names': NAMES, 'primarySets': PRIMARY, 'contrastSets': CONTRAST,
           'W11AtStart': False, 'duplicates': duplicate, 'missing': missing, 'inputs': inputs,
           'selectionRule': 'largest primary loss class, priority tie break, two lowest game IDs; lowest-ID primary win; report absent wins',
           'tasks': tasks}
    target.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'tasks': len(tasks), 'eras': {e: sum(t['era'] == e for t in tasks) for e in ['primary', 'contrast', 'reference']},
                      'missing': len(missing), 'duplicates': duplicate}, ensure_ascii=False))

if __name__ == '__main__':
    main()
