#!/usr/bin/env python3
"""Check the port against ladder fingerprint rows and the matched local output."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import contextlib
import io
import json
from pathlib import Path
import scoreboard as s


def main():
    originals = [json.loads(line) for line in (s.DOS/'per-game.jsonl').read_text().splitlines()]
    original = next(r for r in originals if r['relation'] == 'us')
    path = s.ROOT/original['replay']
    native = s.load_replay(path)
    python = s.replay_format.load(path)
    assert native.segments == python.segments
    own = 'AB'.index(original['our_side'])
    ported = s.count_game(s.load_counter(), path, 'oracle', (original['layout_key'], 1, own))
    extra = json.loads((s.DOS/'work/fp_recount.json').read_text())['games']
    metrics = s.definitions(originals, extra)
    for metric in metrics:
        key = s.metric_key(metric['name'], metric['window'])
        assert ported['rates'][key] == list(metric['fn'](original)), key
    assert ported['pearls'] == original['game_counts']['pearls_eaten']
    assert ported['longest'] == original['final_reconstructed']['longest']
    assert ported['result'] == original['result']
    # Both own-side adapters must agree with the independently saved ladder rows.
    other = next(r for r in originals if r['game'] == original['game'] and r['relation'] == 'them')
    swapped = s.count_game(s.load_counter(), path, 'oracle-other', (original['layout_key'], 1, 1-own))
    for metric in metrics:
        key = s.metric_key(metric['name'], metric['window'])
        assert swapped['rates'][key] == list(metric['fn'](other)), key
    assert s.marker(8, 10, 0, 20) == '*'
    assert s.marker(12, 10, 0, 20) == '!'
    assert s.marker(10, 10, 0, 20) == ''
    assert s.marker(0, 0, 0, 0) == ''
    assert s.marker(None, 0, 1, 0) == ''
    assert s.marker(-12, 10, 0, 20) == '!'
    assert s.pool([{'rates': {'x': [1, 1]}}, {'rates': {'x': [3, 9]}}], 'x') == .4
    assert s.pool([{'rates': {'x': [0, 0]}}], 'x') is None
    first = (s.HERE/'scoreboard-first.txt').read_text()
    reference = json.loads((s.DOS/'target/scoreboard.json').read_text())
    source = (s.DOS/'work/fp_build.py').read_text()
    tree = ast.parse(source)
    start = next(n.lineno for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'METRICS' for t in n.targets))
    end = next(n.lineno for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'pool')
    code = '\n'.join(source.splitlines()[start-1:end-1])
    assert hashlib.sha256(code.encode()).hexdigest() == reference['metric_definition_sha256']
    table = [line.split(' | ') for line in first.splitlines() if line.startswith('| ')][1:]
    assert len(table) == len(reference['displayed'])
    assert [(line[0][2:].rsplit(' (', 1)[0], line[1]) for line in table] == [
        (r['name'], r['window']) for r in reference['displayed']]
    retained = {}
    for line in s.CACHE.read_text().splitlines():
        row = json.loads(line)
        retained[row['replay']] = row
    for arm in ('m2base', 'm2all4', 'm2lg'):
        assert any(r['arm'] == arm for r in retained.values()), arm
    # An identical invocation must do no replay decoding and must not rewrite the cache.
    stat = s.CACHE.stat()
    before = s.CACHE.read_bytes()
    with contextlib.redirect_stdout(io.StringIO()) as output:
        saved_argv = sys.argv
        saved_count = s.count_game
        try:
            sys.argv = ['scoreboard.py', 'm2base', 'm2all4']
            s.count_game = lambda *args: (_ for _ in ()).throw(AssertionError('cache miss'))
            s.main()
        finally:
            sys.argv = saved_argv
            s.count_game = saved_count
    assert '0 counted' in output.getvalue()
    assert before == s.CACHE.read_bytes() and stat.st_mtime_ns == s.CACHE.stat().st_mtime_ns
    # Map filters and a single arm preserve the accumulated cache too.
    for args in (['m2base', 'm2all4', '--maps', 'ladder_islands'], ['m2lg', '--maps', 'no_such_map']):
        with contextlib.redirect_stdout(io.StringIO()):
            old = sys.argv
            try:
                sys.argv = ['scoreboard.py', *args]
                s.main()
            finally:
                sys.argv = old
        assert before == s.CACHE.read_bytes()
    print(f'PASS: {len(metrics)} fingerprint definitions match on both ladder sides; '
          f'{len(table)} displayed rows in order; pooled rates, markers, persistent cache and map filters verified.')


if __name__ == '__main__':
    main()
