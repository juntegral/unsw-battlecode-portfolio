#!/usr/bin/env python3
"""Final artifact audit; all frozen rows, no replay samples or new games.

Checks completeness, independent recount versus per-game CSV, exhaustive death
and territory strata, frozen deep-read selection, Markdown table shape and local
links. This is artifact QA; the independent raw replay calculation is recount.js.
Writes only .cache/elite-counterplay/validation.json, before SUMMARY.txt exists.
"""
from pathlib import Path
from collections import Counter, defaultdict
import ast
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / '.cache/elite-counterplay'
CODE = ROOT / 'exp/elite-counterplay'


def read(name):
    return json.loads((C / name).read_text())


def jrows(name):
    with (C / name).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def crows(name):
    with (C / name).open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    assert not (CODE / 'SUMMARY.txt').exists(), 'Marker must be written last.'
    a, m = read('aggregate.json'), read('manifest.json')
    tasks = {g['key']: g for g in m['tasks']}
    assert len(tasks) == 9192 and not m['W11AtStart'] and not m['missing'] and m['duplicates'] == 0
    online = {r['key']: r for r in crows('per-game.csv')}
    rec = {r['key']: r for r in jrows('recount.jsonl')}
    online_tasks = {k for k, t in tasks.items() if t['src'] == 'online'}
    assert len(online) == len(rec) == 910 and set(online) == set(rec) == online_tasks
    check_totals = defaultdict(Counter)
    for key, g in online.items():
        us = tasks[key]['us']; enemy = 'B' if us == 'A' else 'A'
        r = rec[key]; u, e = r[us], r[enemy]
        elim = int(g['elimRound']) if g['elimRound'] else None
        assert elim == u['elim']
        assert int(g['ourFinalLongest']) == u['longest'] and int(g['theirFinalLongest']) == e['longest']
        assert sum(int(g[f'ours_nat_p{p}']) for p in range(5)) == u['nat']
        assert int(g['enemyNatOur']) == e['on'+us]
        assert int(g['kingRams']) == u['kingRams'] and int(g['kingSprint']) == u['kingSprint']
        outcome = 'D' if r['winner'] is None else 'W' if r['winner'] == us else 'L'
        assert outcome == g['outcome']
        c = check_totals[g['era']]
        c.update({'N': 1, outcome: 1, 'eliminated': int(elim is not None), 'naturalUs': u['nat'],
                  'enemyOurTerritory': e['on'+us], 'kingRams': u['kingRams'], 'kingSprint': u['kingSprint']})
    assert check_totals['primary'] == Counter(N=420, W=41, L=378, D=1, eliminated=155, naturalUs=63547,
                                            enemyOurTerritory=69837, kingRams=133, kingSprint=86)
    death_counts, cause_counts = Counter(), Counter()
    death_keys = set()
    for d in crows('our-deaths.csv'):
        key = (d['key'], d['dragon'])
        assert key not in death_keys
        death_keys.add(key)
        assert d['key'] in online
        assert int(d['d3']) == int(d['a3'])-int(d['e3']) and int(d['d8']) == int(d['a8'])-int(d['e8'])
        death_counts[d['era']] += 1
        if d['era'] == 'primary': cause_counts[d['cause']] += 1
    assert death_counts['primary'] == 39500 and dict(cause_counts) == a['overall']['causes']
    for era in ['primary', 'contrast']:
        for tid in a['teams']:
            gs = [g for g in online.values() if g['era'] == era and g['opponent'] == tid]
            target = a['teams' if era == 'primary' else 'contrast'][tid]
            assert len(gs) == target['N']
            assert Counter(g['outcome'] for g in gs) == Counter({k: target[k] for k in ['W', 'L', 'D'] if target[k]})
            assert Counter(g['lossClass'] for g in gs) == Counter(target['classes'])
            assert sum(int(g['enemyNatOur']) for g in gs) == target['enemyOur']
            assert sum(sum(int(g[f'ours_nat_p{p}']) for p in range(5)) for g in gs) == sum(target['intakeUs'])
    death_strata = crows('death-strata.csv')
    for era in ['primary', 'contrast']:
        for level in ['all', 'map', 'family']:
            assert sum(int(g['deathN']) for g in death_strata if g['era'] == era and g['level'] == level) == death_counts[era]
    terr = crows('territory-phase.csv')
    for level in ['all', 'family', 'map']:
        us = [r for r in terr if r['era'] == 'primary' and r['level'] == level and r['eater'] == 'ours' and r['origin'] == 'nat']
        them = [r for r in terr if r['era'] == 'primary' and r['level'] == level and r['eater'] == 'theirs' and r['origin'] == 'nat']
        assert sum(int(r['own'])+int(r['neutral'])+int(r['enemy']) for r in us) == 63547
        assert sum(int(r['enemy']) for r in them) == 69837
    reference = list(jrows('reference-games.jsonl'))
    excluded = read('excluded-top.json')
    assert len(reference) == 9321 and len(excluded) == 69
    ref_keys = {g['key'] for g in reference}
    ex_keys = {g['key'] for g in excluded}
    assert len(ref_keys) == 8213 and len(ex_keys) == 69 and not ref_keys & ex_keys
    assert ref_keys | ex_keys == {k for k, t in tasks.items() if t['src'] == 'top'}
    for g in excluded:
        assert g['rounds'] >= 100 and any(g[t]['sonar'] == 0 and g[t]['splits'] <= 3 for t in ['A', 'B'])
    for tid in a['teams']:
        refs = [g for g in reference if str(g['oppId']) == tid]
        assert len(refs) == a['reference'][tid]['all']['N']
        for map_name, v in a['maps'][tid].items():
            assert v['N'] == 6
            gs = [g for g in online.values() if g['era'] == 'primary' and g['opponent'] == tid and g['map'] == map_name]
            assert len(gs) == 6
            assert sum(int(g['kingRams']) for g in gs) == v['kingRams']
            for p in range(5):
                assert sum(int(g[f'ours_nat_p{p}']) for g in gs) == v['intakeUs'][p]
                assert sum(int(g[f'theirs_nat_p{p}']) for g in gs) == v['intakeEnemy'][p]
    film_index = read('film-index.json')
    selection = read('selection.json')
    assert len(film_index) == 28
    films = {g['key']: g for g in film_index}
    for tid, s in selection['teams'].items():
        losses = sorted([g for g in online.values() if g['era'] == 'primary' and g['opponent'] == tid and g['lossClass'] == s['largestClass']], key=lambda g: int(tasks[g['key']]['gameId']))
        wins = sorted([g for g in online.values() if g['era'] == 'primary' and g['opponent'] == tid and g['outcome'] == 'W'], key=lambda g: int(tasks[g['key']]['gameId']))
        assert [g['key'] for g in losses[:2]] == s['losses'] and [g['key'] for g in wins[:1]] == s['win']
        for key in s['losses'] + s['win']: assert key in films
    for item in film_index:
        film = json.loads((ROOT / item['file']).read_text())
        assert not any(film['checks'].values()) and film['key'] == item['key']
        if item['kind'] == 'reference': assert item['key'] in ref_keys
    for code in CODE.glob('*.py'): ast.parse(code.read_text(), filename=str(code))
    report_path = ROOT / 'research/observations/elite-counterplay.md'
    report = report_path.read_text()
    assert report.count('#### [') == 28
    assert 'PRESSURE_RETREAT_ON' in report and 'PATCH_HOLD_ON' in report
    assert report.count('**trigger.**') == 2 and report.count('**가설 수준 지표.**') == 2
    assert not re.search(r'https?://', report)
    columns = None; table_n = 0
    for line in report.splitlines():
        if line.startswith('| '):
            n = line.count('|')-1
            if columns is None: columns = n; table_n += 1
            assert n == columns, f'Markdown column mismatch: {line}'
        else: columns = None
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', report)
    for target in links:
        assert (report_path.parent / target).exists(), f'Broken local link: {target}'
    verdict = dict(status='verified', primaryGames=420, contrastGames=490, referenceUniqueGames=8213,
                   excludedReferenceGames=69, referenceTeamGames=9321, rawRecounts=910,
                   primaryValues=a['keyNumbers']['primarySecond'], perGameDisagreements=0,
                   onlineDeaths=dict(death_counts), deepReadFilms=28, proposals=2, tables=table_n,
                   localLinks=len(links), reportSha256=hashlib.sha256(report.encode()).hexdigest(),
                   reportLines=len(report.splitlines()), markerNotYetWritten=True)
    (C / 'validation.json').write_text(json.dumps(verdict, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(verdict, ensure_ascii=False))


if __name__ == '__main__':
    main()
