"""Offline regression checks; temporary fixtures stay in the output directory."""
import sys
sys.dont_write_bytecode = True
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import label_report as lr


class PartialInputs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='label-test-', dir=lr.HERE)
        self.folder = Path(self.temp.name)
        self.mock = patch.object(lr, 'SMOKE', self.folder)
        self.mock.start()

    def tearDown(self):
        self.mock.stop()
        self.temp.cleanup()

    def write(self, name, value):
        (self.folder/name).write_text(json.dumps(value))

    def test_inventory_reports_missing_duplicate_and_partial_inputs(self):
        self.write('partial.json', dict(halves=dict(new=dict(battle_ids=[1, 1, 2, 3, None],
                                                            batches=[dict(maps=[4, 7, 9, 11])]))))
        dest = self.folder/'partial-new'
        dest.mkdir()
        (dest/'M1.replay').write_bytes(b'fixture')
        self.write('partial-new/game-1.json', dict(id=1, teamAId=1119, teamBId=87, teamAName='us',
                                                  teamBName='op', winner='a', scoresA=3, scoresB=0,
                                                  mapId=4, mapName='Map'))
        (dest/'M2.replay').write_bytes(b'fixture')
        (dest/'game-2.json').write_text('{')
        (dest/'game-4.json').write_text('{"id":4}')
        inv = lr.inventory('partial', 'new')
        self.assertEqual([m['id'] for _, m in inv['jobs']], [1])
        self.assertEqual(inv['duplicate_ids'], [1])
        self.assertEqual(inv['planned'], 4)
        notes = ';'.join(inv['notes'])
        for expected in ('미완성/비정수', 'JSONDecodeError', 'M3.replay', 'game-3.json', 'M4.replay', '미요청 1판'):
            self.assertIn(expected, notes)

    def test_downloaded_folders_glob_duplicates_missing_and_metadata_side(self):
        for name in ('batch1', 'batch2'):
            dest = self.folder/name
            dest.mkdir()
            (dest/'index.json').write_text(json.dumps(dict(games=[dict(gameId=1), dict(gameId=2)])))
            (dest/'M1.replay').write_bytes(b'fixture')
            (dest/'game-1.json').write_text(json.dumps(dict(id=1, teamAId=87, teamBId=1119,
                teamAName='op', teamBName='us', winner='b', scoresA=0, scoresB=3, mapId=4, mapName='Map')))
        inv = lr.directory_inventory('ranked', str(self.folder/'batch*')+','+str(self.folder/'batch1'))
        self.assertEqual(len(inv['jobs']), 1)
        self.assertEqual(inv['jobs'][0][1]['teamBId'], 1119)
        self.assertEqual(inv['duplicate_ids'], [1])
        self.assertIn('M2.replay', ';'.join(inv['notes']))
        checks = lr.validate_log(inv, [dict(opponent='op', result='win')])
        self.assertEqual(checks[0]['actual'], [1, 1])
        self.assertEqual(checks[0]['status'], 'not countable')

    def test_absent_and_truncated_state_still_report_disk_inventory(self):
        self.assertEqual(lr.inventory('absent', 'new')['jobs'], [])
        (self.folder/'partial.json').write_text('{"halves":')
        inv = lr.inventory('partial', 'new')
        self.assertEqual(inv['jobs'], [])
        self.assertIn('JSONDecodeError', ';'.join(inv['notes']))
        self.write('null.json', dict(halves=None))
        self.assertEqual(lr.inventory('null', 'new')['jobs'], [])

    def test_log_partial_and_mismatch_are_distinct(self):
        inv = dict(label='x', half='new', state={}, part={})
        rows = [dict(opponent='one', result='win')]
        (self.folder/'x-report.log').write_text('vs one: wins new 1/2\nvs two: wins new 1/1')
        checks = lr.validate_log(inv, rows)
        self.assertEqual(checks[0]['status'], 'pending')
        self.assertEqual(len(checks), 2)
        (self.folder/'x-report.log').write_text('vs one: wins new 0/1\n')
        self.assertEqual(lr.validate_log(inv, rows)[0]['status'], 'mismatch')
        (self.folder/'x-report.log').write_text('vs one: wins new 1/1\n')
        self.assertEqual(lr.validate_log(inv, rows)[0]['status'], 'passed')

    def test_reference_log_does_not_reintroduce_other_opponents(self):
        inv = dict(label='x', half='new', state={}, part={}, excluded_games=1)
        rows = [dict(opponent='one', result='win')]
        (self.folder/'x-report.log').write_text('vs one: wins new 1/1\nvs other: wins new 0/1\n')
        checks = lr.validate_log(inv, rows)
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['status'], 'passed')

    def test_old_log_uses_current_run_instead_of_pooled_baseline(self):
        inv = dict(label='x', half='old', state={}, part=dict(opponents=[dict(name='one')]))
        rows = [dict(opponent='one', result='win')]
        (self.folder/'x-report.log').write_text('vs one: wins new 0/1 vs live 0.5/1\nthis run only, 1 pairs | wins: live 1 -> new 0\n')
        self.assertEqual(lr.validate_log(inv, rows)[0]['status'], 'passed')
        (self.folder/'x-report.log').write_text('vs one: wins live 1/1 | pooled wins 0.5/1\n')
        self.assertEqual(lr.validate_log(inv, rows)[0]['status'], 'passed')
        (self.folder/'x-report.log').write_text('vs one: wins new 0/1 vs live 0.5/1\n')
        inv['part']['opponents'].append(dict(name='other'))
        self.assertEqual(lr.validate_log(inv, rows)[0]['status'], 'not countable')

    def test_empty_reference_report(self):
        inv = dict(label='empty', half='new', planned=0, notes=['누락'])
        text = lr.report('empty', [('empty:new', []), ('ref:new', [])], [inv, inv],
                         [[dict(status='pending')], [dict(status='pending')]], lr.Counter())
        self.assertIn('승리: 0/0.', text)
        self.assertIn('비교 가능한 참조 없음', text)
        self.assertIn('NA (0판)', text)


class ExistingQueenAnalysis(unittest.TestCase):
    def test_complete_report_unique_games_early_end_and_log_checks(self):
        output = json.loads((lr.HERE/'label-agg8-q1.json').read_text())
        games = [r for c in output['columns'] for r in c['games']]
        self.assertEqual(len(games), 75)
        self.assertEqual(len({r['game'] for r in games}), 75)
        for checks in output['checks']:
            self.assertTrue(all(c['status'] == 'passed' for c in checks))
        for row in games:
            end = row['details']['checkpoints']['end']
            for p in lr.CHECKPOINTS:
                if p >= row['details']['last_round']:
                    self.assertEqual(row['details']['checkpoints'][str(p)], end)
        reference = output['columns'][1]['games']
        self.assertEqual((len(reference), sum(r['result'] == 'win' for r in reference)), (15, 4))
        self.assertEqual({r['opponent_id'] for r in reference}, {87})

    def test_rammed_attacker_matches_imported_death_details(self):
        output = json.loads((lr.HERE/'label-agg8-q1.json').read_text())
        checked = 0
        for column in output['columns']:
            for row in column['games']:
                ram = row['details']['queen_ram']
                if row['details']['queen_cause'] != 'rammed':
                    self.assertIsNone(ram)
                    continue
                other = row['extra']['queen_death']['other']
                self.assertEqual((ram['id'], ram['length']), (other['id'], other['length']))
                self.assertIn(ram['side'], ('A', 'B'))
                self.assertEqual(ram['relation'], '우리' if other['side'] == 0 else '상대')
                self.assertEqual(ram['round'], row['details']['queen_turns'][-1]['round'])
                self.assertTrue(ram['distance'] is None or ram['distance'] >= 0)
                checked += 1
        self.assertGreater(checked, 0)

    def test_all_queen_turns_snapshots_and_chases_match_existing_tq2_data(self):
        output = json.loads((lr.HERE/'label-agg8-q1.json').read_text())
        by_name = {c['name']: c['games'] for c in output['columns']}
        for name, tag in [('agg8-q1:new', 'q1'), ('agg7-m2:new', 'm2')]:
            scans = {r['game']: r for r in map(json.loads, (lr.DOS/f'work/tq2_scan-{tag}.jsonl').read_text().splitlines())}
            defs = {r['game']: r for r in map(json.loads, (lr.DOS/f'work/tq2_def-{tag}.jsonl').read_text().splitlines())}
            rows = by_name[name]
            self.assertEqual((len(rows), sum(r['result'] == 'win' for r in rows)), (30, 14 if tag == 'q1' else 7))
            for row in rows:
                old = scans[row['game']]
                turns = row['details']['queen_turns']
                self.assertEqual(len(turns), len(old['recs'][0]))
                for t, o in zip(turns, old['recs'][0]):
                    self.assertEqual([t['round'], t['head'], t['length'], t['mates5'], t['enemy3'], t['pearls']],
                                     [o[0], o[1], o[2], o[5], int(o[8] > 0), o[22]])
                for point, states in old['snaps'].items():
                    if point in row['details']['checkpoints']:
                        for s in (0, 1):
                            st = row['details']['checkpoints'][point][s]
                            self.assertEqual([st[k] for k in ('queen_length', 'alive', 'longest', 'total')], states[s])
                episodes = []
                for t in defs[row['game']]['qturns'][0]:
                    if episodes and t[0] == episodes[-1][-1][0]+1:
                        episodes[-1].append(t)
                    else:
                        episodes.append([t])
                self.assertEqual([(c['start'], c['end'], c['turns'], c['no_mate5']) for c in row['details']['chases']],
                                 [(e[0][1], e[-1][1], len(e), e[0][4] == 0) for e in episodes])


if __name__ == '__main__':
    unittest.main()
