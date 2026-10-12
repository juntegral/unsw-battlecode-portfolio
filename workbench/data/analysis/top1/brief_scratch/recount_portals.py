import json
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[2]
games = json.loads((root / 'queen-portals/games.json').read_text())
rows = defaultdict(list)
by_map = defaultdict(list)
for game in games:
    if not game.get('portals') or 'queens' not in game:
        continue
    by_map[game['map']].append(game)
    for queen in game['queens'].values():
        rows[game['map'], queen['tag']].append((game, queen))

def rate(n, d):
    return f'{n}/{d} ({100*n/d:.1f}%)' if d else '— (0 queens)'

lines = ['| Map | Tag | Queens Q; games G | Any jump | Wins, jump | Wins, no jump | Elimination, unique games |',
         '|---|---|---|---|---|---|---|']
counts = []
for name in sorted(by_map):
    for tag in ['ours', 'top three', 'other']:
        entries = rows[name, tag]
        distinct = {g['game_id']: g for g, q in entries}
        jumped = [q for g, q in entries if q['jumps']]
        stayed = [q for g, q in entries if not q['jumps']]
        elim = sum(g['end'] == 'elimination' for g in distinct.values())
        vals = [name, tag, f'{len(entries)}; {len(distinct)}', rate(len(jumped), len(entries)),
                rate(sum(q['win'] for q in jumped), len(jumped)),
                rate(sum(q['win'] for q in stayed), len(stayed)), rate(elim, len(distinct))]
        lines.append('| ' + ' | '.join(vals) + ' |')
        counts.append(dict(map=name, tag=tag, queens=len(entries), games=len(distinct),
                           jumped=len(jumped), wins_jump=sum(q['win'] for q in jumped),
                           no_jump=len(stayed), wins_no_jump=sum(q['win'] for q in stayed), elimination=elim))
lines += ['', 'All tags together, each game counted once:', '', '| Map | Elimination / games |', '|---|---|']
for name, entries in sorted(by_map.items()):
    lines.append(f"| {name} | {rate(sum(g['end'] == 'elimination' for g in entries), len(entries))} |")
out = Path(__file__).parent
(out / 'portal_table.md').write_text('\n'.join(lines) + '\n')
(out / 'portal_counts.json').write_text(json.dumps(counts, indent=2) + '\n')
print('\n'.join(lines))
print(f'Portal games: {sum(map(len, by_map.values()))}; queen-games: {sum(map(len, rows.values()))}')
