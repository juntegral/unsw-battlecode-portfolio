#!/usr/bin/env python3
"""Fingerprint scoreboard for matched local games; no games or network are started."""
import sys
sys.dont_write_bytecode = True
import argparse
import ast
import gzip
import hashlib
import importlib.util
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import replay_format

HERE = Path(__file__).resolve().parent
DOS = HERE.parent
ROOT = DOS.parents[3]
RUNS = Path('~/meow-redteam/solo/runs')
CACHE = HERE / 'scoreboard-rows.jsonl'
WINDOWS = {'0-100': (0, 100), '101-300': (101, 300)}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def replace_once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def load_counter():
    mod = module('local_scoreboard_dossier', DOS / 'count_dossier.py')
    source = (DOS / 'count_dossier.py').read_text()
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'scan')
    code = ast.get_source_segment(source, fn)
    replacements = {
        "path = ROOT / 'data/online/ladder' / str(row['battle']) / ('M%d.replay' % row['game'])":
            "path = Path(row['replay'])",
        "meta_path = path.parent / ('game-%d.json' % row['game'])": "meta_path = path.with_name('result.json')",
        "metadata = json.loads(meta_path.read_text())": "metadata = {'team' + row['our_side'] + 'Id': 1119}",
        "assert all_eats[s] == row['curves']['end'][s]['pearls']":
            "assert all_eats[s] == row['_extra'][s]['game'].get('eaten', 0)",
        "assert (queen_death[s] or {}).get('round') == row['queen'][s]['death_round']":
            "assert (queen_death[s] or {}).get('round') == row['_queen_deaths'].get(s)",
        "assert (queens[s] in bodies) == row['queen'][s]['alive_end']":
            "assert (queens[s] in bodies) == (final[s]['queen_length'] > 0)",
        "sha(meta_path)": "None",
    }
    for old, new in replacements.items():
        code = replace_once(code, old, new)
    code = code.replace('str(path.relative_to(ROOT))', 'str(path)')
    exec(compile(code, str(DOS / 'count_dossier.py'), 'exec'), mod.__dict__)
    mod.replay = replay_format
    return mod


def definitions(rows, extra):
    # This is the same extraction used by tg_score.py, with no metric edits.
    source = (DOS / 'work/fp_build.py').read_text()
    tree = ast.parse(source)
    start = next(n.lineno for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'METRICS' for t in n.targets))
    end = next(n.lineno for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'pool')
    env = dict(ROWS=rows, EXTRA=extra, WINDOWS=WINDOWS)
    exec(compile('\n'.join(source.splitlines()[start-1:end-1]),
                 str(DOS / 'work/fp_build.py'), 'exec'), env)
    return env['METRICS']


def metric_key(name, window):
    return name + ' | ' + window


def load_replay(path):
    binary = DOS / 'target/tg_unpack'
    if binary.is_file():
        blob = path.read_bytes()
        if blob[:2] == b'\x1f\x8b':
            blob = gzip.decompress(blob)
        raw = subprocess.run([str(binary)], input=blob, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, check=True).stdout
        return replay_format.Message(raw)
    return replay_format.load(path)


def count_game(mod, path, arm, key):
    slug, seed, own = key
    own_letter = 'AB'[own]
    root = load_replay(path).root()
    result = root.pointer(4)
    if result is None or not result.bit(0):
        raise ValueError('unfinished replay')
    teams = {}
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            teams[len(teams)] = 'AB'[int(q[1])]
    side = lambda i: 'us' if teams[i] == own_letter else 'them'
    queens = {s: min(i for i in teams if side(i) == s) for s in ('us', 'them')}
    extra = {s: {w: Counter() for w in (*WINDOWS, 'game')} for s in ('us', 'them')}
    present, queen_deaths = {}, {}
    rnd, actor = 0, None
    for ev in root.pointer(3):
        kind = ev.u16(0)
        if kind not in (0, 1, 3, 10, 11):
            continue
        p = ev.pointer(0)
        if kind == 0:
            rnd, actor = p.i32(0), None
        elif kind == 10:
            teams[p.i32(4)] = 'AB'[p.u16(8)]
        elif kind == 11:
            i = p.i32(0)
            if i == queens[side(i)]:
                queen_deaths[side(i)] = rnd
        elif kind == 1:
            actor = p.i32(0)
            s = side(actor)
            for w in ['game'] + [w for w, (lo, hi) in WINDOWS.items() if lo <= rnd <= hi]:
                extra[s][w]['turns'] += 1
        else:
            tile = replay_format.point(p.pointer(0))
            if p.u32(0):
                assert tile not in present
                present[tile] = actor is not None
            else:
                dropped = present.pop(tile)
                s = side(actor)
                for w in ['game'] + [w for w, (lo, hi) in WINDOWS.items() if lo <= rnd <= hi]:
                    extra[s][w]['eaten'] += 1
                    extra[s][w]['drop_eaten'] += int(dropped)
    final = {}
    for z in (0, 1):
        st = result.pointer(z)
        final['us' if z == own else 'them'] = dict(zip(
            ('alive', 'longest', 'total', 'queen_length'), (st.i32(o) for o in (0, 4, 8, 12))))
    winner = result.u16(6) if result.u16(4) == 1 else None
    outcome = 'draw' if winner is None else 'win' if winner == own else 'loss'
    row = dict(game=str(path), battle=path.parent.name, replay=str(path), map_key=slug,
               map=slug, map_version='local', opponent_rating=None, opponent='local opponent',
               our_side=own_letter, result=outcome, last_round=rnd, ended_by=result.u16(2),
               final=final, curves={}, _extra=extra, _queen_deaths=queen_deaths)
    # Decode once; scan() still consumes the original counter's event sequence.
    mod.replay = type('Reader', (), {'load': staticmethod(lambda _: type('Loaded', (), {'root': lambda _: root})()),
                                   'point': staticmethod(replay_format.point)})
    rows, _, _ = mod.scan(row)
    ours = next(r for r in rows if r['relation'] == 'us')
    metrics = definitions(rows, {str(path): extra})
    pairs = {metric_key(m['name'], m['window']): list(m['fn'](ours)) for m in metrics}
    for w in WINDOWS:
        assert ours['ranges'][w]['turns'] == extra['us'][w]['turns']
        assert ours['ranges'][w]['pearls_eaten'] == extra['us'][w]['eaten']
    alive = {}
    for checkpoint, window in ((100, '0-100'), (300, '101-300')):
        snap = ours['ranges'][window]['end_state']
        alive[str(checkpoint)] = snap['alive'] if snap else final['us']['alive'] if rnd < checkpoint else None
        assert alive[str(checkpoint)] is not None
    return dict(replay=str(path), arm=arm, map=slug, seed=seed, side=own, result=outcome,
                last_round=rnd, rates=pairs, pearls=ours['game_counts']['pearls_eaten'],
                alive=alive, longest=final['us']['longest'])


def pool(rows, key):
    pairs = [r['rates'][key] for r in rows if r['rates'][key][1] > 0]
    denominator = sum(d for _, d in pairs)
    return sum(n for n, _ in pairs) / denominator if denominator else None


def marker(value, base, target, ladder):
    if any(v is None for v in (value, base, target, ladder)):
        return ''
    gap = abs(target - ladder)
    if gap == 0:
        return ''
    progress = abs(base - target) - abs(value - target)
    if progress >= .1 * gap:
        return '*'
    if progress <= -.1 * gap:
        return '!'
    return ''


def fmt(value, signed=False):
    return 'NA' if value is None else format(value, '+.3f' if signed else '.3f')


def inventory(arm, substring):
    if Path(arm).name != arm or arm in ('.', '..'):
        raise ValueError('arm must be a directory name under runs')
    folder = RUNS / arm
    if not folder.is_dir():
        raise ValueError(f'unknown arm: {arm}')
    games = {}
    for path in sorted(folder.glob('*/game.replay')):
        match = re.fullmatch(r'(.+)-seed(\d+)-side([01])', path.parent.name)
        if match and (substring is None or substring in match[1]):
            games[(match[1], int(match[2]), int(match[3]))] = path.resolve()
    return games


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arms', nargs='+')
    parser.add_argument('--maps', help='substring of the local layout name')
    args = parser.parse_args()
    if len(set(args.arms)) != len(args.arms):
        parser.error('name each arm only once')
    inventories = {a: inventory(a, args.maps) for a in args.arms}
    common = sorted(set.intersection(*(set(g) for g in inventories.values())))
    scoreboard = json.loads((DOS / 'target/scoreboard.json').read_text())
    reference = {(r['name'], r['window']): r for r in scoreboard['rates']}
    sources = [Path(__file__), HERE/'replay_format.py', DOS/'count_dossier.py',
               DOS.parent/'losses/counts/count_replays.py', ROOT/'tools/ladder_replay.py',
               DOS/'work/fp_build.py', DOS/'target/tg_unpack']
    version = hashlib.sha256(b''.join(p.read_bytes() for p in sources if p.exists())).hexdigest()
    cache = {}
    if CACHE.exists():
        for number, line in enumerate(CACHE.read_text().splitlines(), 1):
            try:
                r = json.loads(line)
                cache[r['replay']] = r
            except (ValueError, KeyError) as error:
                raise ValueError(f'invalid cache line {number}: {error}') from error
    mod = None
    selected = {a: [] for a in args.arms}
    hits = counted = 0
    for arm in args.arms:
        for key in common:
            path = inventories[arm][key]
            st = path.stat()
            signature = [version, st.st_size, st.st_mtime_ns]
            cached = cache.get(str(path))
            if cached and cached.get('_signature') == signature:
                row = cached
                hits += 1
            else:
                if mod is None:
                    mod = load_counter()
                row = count_game(mod, path, arm, key)
                after = path.stat()
                assert (after.st_size, after.st_mtime_ns) == (st.st_size, st.st_mtime_ns), 'replay changed; rerun'
                row['_signature'] = signature
                # Append immediately: interrupted counts and newly added arms retain old rows.
                with CACHE.open('a') as handle:
                    handle.write(json.dumps(row, separators=(',', ':')) + '\n')
                cache[str(path)] = row
                counted += 1
                if counted % 10 == 0:
                    print(f'Counted {counted}/{len(common)*len(args.arms)} selected games', file=sys.stderr, flush=True)
            meta_path = path.with_name('result.json')
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                if meta.get('crash') or meta.get('error') or meta.get('bot_errors'):
                    raise ValueError(f'{meta_path}: crash or bot errors')
                winner = None if row['result'] == 'draw' else key[2] if row['result'] == 'win' else 1-key[2]
                assert meta.get('winner', winner) == winner, f'{meta_path}: winner mismatch'
                assert meta.get('rounds', row['last_round']+1) == row['last_round']+1, f'{meta_path}: rounds mismatch'
            selected[arm].append(row)
    print(f'Matched games per arm: {len(common)}; layouts: {len({k[0] for k in common})}; maps: {args.maps or "all"}')
    print('R/O = shared-layout rank-1/our ladder means; arms = pooled scaled numerator / denominator.')
    print(f'Changes = arm minus {args.arms[0]}; * closer to R, ! farther from R by >=10% of |O-R|, compared with the first arm.')
    print('Inclusive raw rounds; birth cohorts followed to game end; only full 20-round blocks. NA = no denominator.')
    print(f'Cache: {hits} reused, {counted} counted; {len(cache)} replay paths retained.')
    headers = ['Rate (unit)', 'Window', 'R', 'O', *args.arms,
               *(f'Δ {a}-{args.arms[0]}' for a in args.arms[1:])]
    print('\n| ' + ' | '.join(headers) + ' |')
    print('|' + '---|'*len(headers))
    unported = []
    for display in scoreboard['displayed']:
        r = reference[display['name'], display['window']]
        key = metric_key(r['name'], r['window'])
        target, ladder = (r['shared_equal_layouts'][s] for s in ('rank1', 'ours'))
        if any(key not in row['rates'] for rows in selected.values() for row in rows):
            unported.append(key)
            values = [None]*len(args.arms)
        else:
            values = [pool(selected[a], key) for a in args.arms]
        base = values[0]
        cells = [f"{r['name']} ({r['unit']})", r['window'], fmt(target), fmt(ladder)]
        cells += [fmt(v)+marker(v, base, target, ladder) for v in values]
        cells += [fmt(v-base if v is not None and base is not None else None, True)
                  + marker(v, base, target, ladder) for v in values[1:]]
        print('| ' + ' | '.join(cells) + ' |')
    print()
    for arm in args.arms:
        rows = selected[arm]
        mean = lambda values: sum(values)/len(values) if values else None
        print(f'{arm}: games={len(rows)}, wins={sum(r["result"] == "win" for r in rows)}')
        print(f'{arm}: pearls eaten/game={fmt(mean([r["pearls"] for r in rows]))}, dragons alive r100/r300='
              f'{fmt(mean([r["alive"]["100"] for r in rows]))}/{fmt(mean([r["alive"]["300"] for r in rows]))}')
        print(f'{arm}: longest at end={fmt(mean([r["longest"] for r in rows]))}')
    print('Context checkpoints carry terminal standings forward for games ending early.')
    print('Unported rates: ' + ('; '.join(unported) if unported else 'none (all displayed fingerprint definitions ported).'))


if __name__ == '__main__':
    main()
