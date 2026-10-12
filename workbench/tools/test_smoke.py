"""Offline tests: no Node process, network, upload, request or activation is run."""
import contextlib
import copy
import importlib.util
import io
import itertools
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('smoke', Path(__file__).with_name('smoke.py'))
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class SmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bot = self.root / 'bot'
        self.bot.mkdir()
        (self.bot / 'bot.toml').write_text('')
        self.calls = []
        self.current = {'id': 61, 'name': 'v61'}
        self.maps = [{'id': i, 'name': f'map{i}', 'active': True, 'private': False} for i in range(1, 11)]
        self.next_id = 100
        self.matches = {}
        self.fail = None
        self.pending = False
        self.dev = True
        self.duplicate = False
        self.remaining = 60
        self.bad_download = False
        self.normal_remaining = 60
        self.live = False
        self.download_side = 'A'
        self.fail_new_request = False
        self.fail_after_upload = False
        self.submissions = [self.sub(61, 42, 'v61', 1907, 'aaaa', 'idle'), self.sub(62, 43, 'test', 1990, 'bbbb', 'active')]
        self.patches = [patch.object(smoke, 'ROOT', self.root), patch.object(smoke, 'DATA', self.root / 'data/online'),
                        patch.object(smoke, 'STATE', self.root / 'data/online/smoke'), patch.object(smoke, 'run', self.fake),
                        patch.dict(os.environ)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        os.environ.pop(smoke.RESTORE_SWITCH, None)

    @staticmethod
    def sub(sid, version, name, rating, code, status='idle'):
        return {'id': sid, 'version': version, 'name': name, 'status': status, 'rating': rating,
                'sourceHash': code, 'wins': 3, 'losses': 2}

    def fake(self, tool, *args, json_output=False):
        self.calls.append((tool, args))
        command = args[0]
        if self.fail == command:
            raise RuntimeError('fake failure bc_secret')
        if command == 'list':
            return [{'id': 61, 'version': 42, 'status': 'active', 'sourceHash': 'aaaa'},
                    {'id': 62, 'version': 43, 'sourceHash': 'bbbb'}]
        if command == 'submissions':
            if self.submissions is None:
                raise RuntimeError('online.js submissions failed (exit 1): fetch failed')
            return copy.deepcopy(self.submissions)
        if command == 'active':
            return f"{self.current['id']} {self.current['name']} (2026-10-03)"
        if tool == 'subs.js' and command == 'list':
            return [dict(self.current, version=self.current['id'])]
        if command == 'leaderboard':
            rows = [{'id': 7, 'name': 'dev_test_1', 'elo': 1800}, {'id': 8, 'name': 'top8', 'elo': 1900}, {'id': 9, 'name': 'low', 'elo': 1500}] if '--eligible' in args else [{'id': 7, 'name': 'dev_test_1'}]
            return {'rows': rows * (2 if self.duplicate else 1)}
        if command == 'team':
            return {'team': {'id': int(args[1]), 'name': 'dev_test_1' if int(args[1]) == 7 else 'top' + str(args[1]), 'dev': self.dev, 'hasBot': True}} if len(args) > 1 else {'team': {'id': 1119, 'elo': 1700}}
        if command == 'maps':
            return self.maps
        if command == 'tickets':
            return {'dev': {'remaining': self.remaining}, 'normal': {'remaining': self.normal_remaining}}
        if command == 'upload':
            self.current = {'id': 62, 'name': args[args.index('--name') + 1]}
            if self.fail_after_upload:
                raise RuntimeError('zip verification failed after activation')
            return 'uploaded'
        if command == 'activate':
            self.current = {'id': int(args[1]), 'name': 'v61'}
            return 'activated'
        if command == 'battles':
            return [{'id': 99, 'outcome': 'live', 'results': ['pending']}] if self.live else []
        if command == 'request':
            if self.fail_new_request and self.current['id'] == 62:
                raise RuntimeError('new request failed')
            ids = []
            for mid in args[args.index('--maps') + 1].split(','):
                self.next_id += 1
                gid = self.next_id
                ids.append(gid)
                game = {'id': gid, 'status': 'completed', 'mapName': f'map{mid}', 'mapId': int(mid), 'winner': 'a'}
                self.matches[gid] = {'match': {'id': gid, 'status': 'completed'}, 'games': [game], 'submission': self.current['id'], 'opponent': int(args[1])}
            return '신청됨  7 dev_test_1: 201 ids ' + ','.join(map(str, ids))
        if command == 'battle':
            detail = copy.deepcopy(self.matches[int(args[1])])
            if self.pending:
                detail['games'][0]['status'] = 'pending'
            return detail
        if command == 'download':
            directory = smoke.DATA / args[args.index('--out') + 1]
            directory.mkdir(parents=True, exist_ok=True)
            games = []
            for gid in map(int, args[1].split(',')):
                detail = self.matches[gid]
                game = {'gameId': gid, 'mapName': detail['games'][0]['mapName'], 'ourSide': self.download_side, 'winner': 'a',
                        'map': detail['games'][0]['mapId'], 'ourSubmission': detail['submission'], 'opponentTeam': detail['opponent'], 'replay': not self.bad_download}
                games.append(game)
                (directory / f'M{gid}.replay').write_bytes(b'fake')
                (directory / f'game-{gid}.json').write_text(json.dumps({'replay': {'result': {'reason': 'round-limit', 'teamA': {'longestDragon': 50}, 'teamB': {'longestDragon': 40}}}}))
            (directory / 'index.json').write_text(json.dumps({'games': games}))
            return 'saved'
        raise AssertionError((tool, args))

    def args(self, command='start', name='test', games=60):
        return SimpleNamespace(command=command, name=name, botdir=str(self.bot), opp='dev_test_1', maps='all', games=games, baseline='v61', wait_seconds=1)

    def execute(self, args):
        state = smoke.prepare(args)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            smoke.execute(args, state)
        return state

    def test_plan_and_no_confirm(self):
        for command in ('plan', 'start', 'baseline'):
            argv = [command] + ([] if command == 'baseline' else [str(self.bot)]) + ['--name', 'smoketest', '--opp', 'dev_test_1', '--maps', 'all']
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(smoke.main(argv), 0)
            self.assertIn('60 games in 6 sequential requests', output.getvalue())
            self.assertIn('DEV verified', output.getvalue())
            self.assertFalse(smoke.STATE.exists())
        self.assertFalse(any(args[0] in ('upload', 'request', 'activate') for _, args in self.calls))
        plan_args = self.args('plan', 'smoketest')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            smoke.plan(plan_args, smoke.prepare(plan_args))
        self.plan_output = output.getvalue()

    def test_baseline_candidate_report(self):
        base = self.execute(self.args('baseline', 'v61'))
        self.assertEqual(len(base['battle_ids']), 60)
        state = self.execute(self.args())
        self.assertEqual(len(state['battle_ids']), 60)
        self.assertTrue(smoke.compatible(state, base))
        pick = '| Game | Map | Result | Queen | Death | Alive | Portals | Splits | Suicides | Longest |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| 101 | map1 | win | 0 | survived | 500 | 2 | 3 | 4 | 50 |\n'
        with patch.object(smoke, 'picks', return_value=pick) as picker, contextlib.redirect_stdout(io.StringIO()):
            smoke.report(state)
        self.assertEqual(picker.call_count, 2)
        report = (smoke.STATE / 'test-report.md').read_text()
        for value in ('noise at 60 games (±8)', 'area owner decides', 'Selected rank', 'round-limit', 'Previous submission'):
            self.assertIn(value, report)
        requests = [args for _, args in self.calls if args[0] == 'request']
        self.assertTrue(all('--expect-active' in args and '--ranked' not in args for args in requests))

    def test_upload_failure_keeps_rollback(self):
        self.fail = 'upload'
        args = self.args()
        state = smoke.prepare(args)
        with contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(RuntimeError):
            smoke.execute(args, state)
        self.assertIn('activate 61 --confirm', output.getvalue())
        saved = smoke.load('test')
        self.assertEqual(saved['phase'], 'failed')
        self.assertNotIn('bc_secret', saved['error'])
        self.assertFalse(any(a[0] == 'request' for _, a in self.calls))

    def test_pending_and_incomplete_download(self):
        state = self.execute(self.args(games=2))
        self.pending = True
        with self.assertRaisesRegex(RuntimeError, 'not all complete'):
            smoke.download(state)
        self.pending = False
        self.bad_download = True
        with self.assertRaisesRegex(RuntimeError, 'incomplete'):
            smoke.download(state)

    def test_request_failure_and_duplicate_state(self):
        self.fail = 'request'
        args = self.args(games=2)
        state = smoke.prepare(args)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(RuntimeError):
            smoke.execute(args, state)
        self.assertEqual(smoke.load('test')['requests'][0]['status'], 'in-flight')
        self.fail = None
        with self.assertRaisesRegex(RuntimeError, 'already exists'):
            smoke.execute(args, state)

    def test_zero_exit_request_rejection_is_uncertain(self):
        args = self.args(games=2)
        state = smoke.prepare(args)
        def refusal(tool, *values, **kwargs):
            return '거절 7 dev_test_1: 409 pending' if values[0] == 'request' else self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=refusal), contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'acceptance/count'):
            smoke.execute(args, state)
        self.assertEqual(smoke.load('test')['requests'][0]['status'], 'uncertain')
        self.assertEqual(smoke.load('test')['battle_ids'], [])

    def test_timeout_stops_next_batch(self):
        self.pending = True
        args = self.args()
        state = smoke.prepare(args)
        with patch.object(smoke.time, 'monotonic', side_effect=[0, 2]), contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'Timed out'):
            smoke.execute(args, state)
        self.assertEqual(len(state['battle_ids']), 10)
        self.assertEqual(len(state['requests']), 1)

    def test_non_dev_ambiguous_budget_and_mismatch(self):
        self.dev = False
        with self.assertRaisesRegex(RuntimeError, 'not marked DEV'):
            smoke.prepare(self.args())
        self.dev = True
        self.duplicate = True
        with self.assertRaisesRegex(RuntimeError, '2 matches'):
            smoke.prepare(self.args())
        self.duplicate = False
        state = smoke.prepare(self.args())
        self.remaining = 59
        with self.assertRaisesRegex(RuntimeError, 'Insufficient DEV'):
            smoke.execute(self.args(), state)
        self.assertFalse(smoke.STATE.exists())
        self.remaining = 60
        base = self.execute(self.args('baseline', 'v61'))
        state['batches'] = [[1]]
        self.assertFalse(smoke.compatible(state, base))

    def test_rollback_without_confirm(self):
        self.execute(self.args(games=1))
        before = len(self.calls)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(smoke.main(['rollback', 'test']), 0)
        self.assertIn('activate 61 --confirm', output.getvalue())
        self.assertEqual(len(self.calls), before)

    def test_fake_rollback_verification(self):
        state = self.execute(self.args(games=1))
        with contextlib.redirect_stdout(io.StringIO()):
            smoke.perform_rollback(state)
        self.assertEqual(self.current['id'], 61)
        self.assertEqual(smoke.load('test')['phase'], 'rolled-back')
        self.current['id'] = 62
        with patch.object(smoke, 'active', return_value={'id': 99, 'name': 'other'}), contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'verification failed'):
            smoke.perform_rollback(state)

    def test_picker_uses_recorded_team_and_warns(self):
        tool = self.root / 'tools/smoke_pick.py'
        tool.parent.mkdir()
        tool.write_text('')
        result = SimpleNamespace(returncode=1, stdout='No readable replays', stderr='bc_secret')
        with patch.object(smoke.subprocess, 'run', return_value=result) as fake:
            text = smoke.picks(self.root, 1119)
        self.assertIn('--us', fake.call_args.args[0])
        self.assertIn('1119', fake.call_args.args[0])
        self.assertIn('coverage unavailable', text)
        self.assertNotIn('bc_secret', text)

    def test_report_refuses_partial(self):
        state = self.execute(self.args(games=1))
        state['requests'][0]['status'] = 'uncertain'
        with self.assertRaisesRegex(RuntimeError, 'partial or uncertain'):
            smoke.report(state)

    def pair_args(self, games=60):
        args = self.args('pair', games=games)
        args.opp = '7,8'
        args.top = None
        return args

    def execute_pair(self, args=None):
        args = args or self.pair_args()
        state = smoke.pair_prepare(args)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            smoke.pair_execute(args, state)
        return state

    def test_default_description_ref_label_and_single_upload(self):
        args = self.pair_args(games=4)
        state = self.execute_pair(args)
        self.assertEqual(state['description'], 'TEST. v42 main + test. vs dev_test_1, top8')
        self.assertEqual(sum(t == 'subs.js' for t, _ in self.calls), 2)
        upload = next(a for _, a in self.calls if a[0] == 'upload')
        self.assertNotIn('--allow-pending', upload)
        self.assertEqual(upload[upload.index('--desc') + 1], state['description'])
        args = self.args(name='single', games=1)
        args.ref = 'card A'
        state = self.execute(args)
        self.assertEqual(state['description'], 'TEST. v42 main + card A. vs dev_test_1')
        upload = [a for _, a in self.calls if a[0] == 'upload'][-1]
        self.assertNotIn('--allow-pending', upload)
        self.assertEqual(upload[upload.index('--desc') + 1], state['description'])

    def test_description_ref_lookup_failure_and_cut(self):
        args = self.pair_args(games=4)
        args.ref = 'card B'
        state = smoke.pair_prepare(args)
        self.assertEqual(state['description'], 'TEST. v42 main + card B. vs dev_test_1, top8')
        self.fail = 'list'
        state = smoke.pair_prepare(args)
        self.assertEqual(state['description'], 'TEST. live 61 main + card B. vs dev_test_1, top8')
        args.ref = 'x' * 300
        self.assertEqual(smoke.pair_prepare(args)['description'], ('TEST. live 61 main + ' + args.ref + '. vs dev_test_1, top8')[:190])
        args.desc = 'explicit ' * 40
        before = len(self.calls)
        self.assertEqual(smoke.pair_prepare(args)['description'], args.desc[:190])
        self.assertFalse(any(t == 'subs.js' for t, _ in self.calls[before:]))

    def test_old_only_no_swap_state_and_cost(self):
        args = self.pair_args(games=30)
        args.old_only = True
        args.botdir = '-'
        self.live = True
        state = self.execute_pair(args)
        self.assertEqual(state['phase'], 'rolled-back')
        self.assertFalse(state['rollback_required'])
        self.assertEqual(state['planned_total'], 30)
        self.assertEqual(smoke.pair_cost(state), (0, 30))
        self.assertEqual(state['halves']['old']['submission']['id'], 61)
        self.assertEqual(state['halves']['old']['phase'], 'finished')
        self.assertEqual(len(state['halves']['old']['battle_ids']), 30)
        self.assertEqual(state['halves']['new']['battle_ids'], [])
        self.assertEqual(state['halves']['new']['requests'], [])
        self.assertIsNone(state['halves']['new']['submission'])
        with contextlib.redirect_stdout(io.StringIO()):
            smoke.perform_rollback(state)
        self.assertFalse(any(a[0] in ('upload', 'activate') for t, a in self.calls))
        self.assertEqual(state['halves']['old']['submission']['version'], 42)

    def test_old_only_normal_budget_and_plan(self):
        args = self.pair_args(games=30)
        args.old_only = True
        self.dev = False
        self.normal_remaining = 30
        state = smoke.pair_prepare(args)
        self.assertEqual(smoke.pair_cost(state), (30, 0))
        smoke.pair_budget(state)
        self.normal_remaining = 29
        with self.assertRaisesRegex(RuntimeError, 'Insufficient normal'):
            smoke.pair_budget(state)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            smoke.pair_plan(args, state)
        self.assertIn('no upload, swap or rollback', output.getvalue())
        self.assertNotIn('Upload:', output.getvalue())

    def test_old_only_failure_does_not_require_rollback_after_external_upload(self):
        args = self.pair_args(games=4)
        args.old_only = True
        state = smoke.pair_prepare(args)
        self.current = {'id': 99, 'name': 'external'}
        with contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(RuntimeError):
            smoke.pair_execute(args, state)
        self.assertEqual(state['phase'], 'failed')
        self.assertFalse(state['rollback_required'])
        self.assertNotIn('ROLLBACK REQUIRED', output.getvalue())
        self.assertFalse(any(a[0] in ('upload', 'activate') for _, a in self.calls))

    def test_old_only_exclusive_with_new_only(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            smoke.main(['pair', '-', '--name', 'exclusive', '--opp', '7', '--old-only', '--new-only'])
        self.assertEqual(error.exception.code, 2)
        self.assertEqual(self.calls, [])

    def test_pair_order_and_same_schedule(self):
        state = self.execute_pair()
        self.assertEqual(state['phase'], 'rolled-back')
        self.assertEqual(self.current['id'], 61)
        self.assertFalse(state['rollback_required'])
        uploads = [i for i, (_, a) in enumerate(self.calls) if a[0] == 'upload']
        activations = [i for i, (_, a) in enumerate(self.calls) if a[0] == 'activate']
        requests = [(i, a) for i, (_, a) in enumerate(self.calls) if a[0] == 'request']
        old = [a for i, a in requests if i < uploads[0]]
        new = [a for i, a in requests if i > uploads[0]]
        self.assertEqual([(a[1], a[a.index('--maps') + 1]) for a in old],
                         [(a[1], a[a.index('--maps') + 1]) for a in new])
        self.assertTrue(all(a[-1] == 61 for a in old))
        self.assertTrue(all(a[-1] == 62 for a in new))
        for key, boundary in (('old', uploads[0]), ('new', activations[0])):
            self.assertEqual(len(state['halves'][key]['battle_ids']), 30)
            polled = {a[1] for _, a in self.calls[:boundary] if a[0] == 'battle'}
            self.assertTrue(set(state['halves'][key]['battle_ids']) <= polled)
        counts = [sum(len(b['maps']) for b in state['schedule'] if b['opponent']['id'] == tid) for tid in (7, 8)]
        self.assertEqual(counts, [15, 15])

    def test_pair_versions_saved_after_upload_in_one_lookup(self):
        self.execute_pair(self.pair_args(games=4))
        saved = smoke.load('test')
        self.assertEqual(saved['halves']['new']['submission']['version'], 43)
        self.assertEqual(saved['halves']['old']['submission']['version'], 42)
        self.assertEqual(saved['rollback']['version'], 42)
        upload = next(i for i, (_, a) in enumerate(self.calls) if a[0] == 'upload')
        lookups = [a for t, a in self.calls[upload:] if t == 'subs.js']
        self.assertEqual(lookups, [('list', '--last', '40')])

    def test_pair_version_lookup_failure_keeps_running(self):
        self.fail = 'list'
        saved = self.execute_pair(self.pair_args(games=4))
        self.assertEqual(saved['phase'], 'rolled-back')
        self.assertNotIn('version', saved['rollback'])
        self.assertNotIn('version', saved['halves']['new']['submission'])

    def test_pair_missing_version_keeps_running(self):
        def missing(tool, *args, **kwargs):
            if tool == 'subs.js':
                return [{'id': 61}, {'id': 62, 'version': None}]
            return self.fake(tool, *args, **kwargs)
        with patch.object(smoke, 'run', side_effect=missing):
            saved = self.execute_pair(self.pair_args(games=4))
        self.assertEqual(saved['phase'], 'rolled-back')
        self.assertNotIn('version', saved['rollback'])
        self.assertNotIn('version', saved['halves']['new']['submission'])

    def test_pair_upload_retries_live_refusals(self):
        attempts = []
        def refusal(tool, *values, **kwargs):
            if values[0] == 'upload':
                attempts.append(values)
                if len(attempts) <= 2:
                    raise RuntimeError('Our battles are live or pending')
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=refusal), patch.object(smoke.time, 'sleep') as nap:
            state = self.execute_pair(self.pair_args(games=4))
        self.assertEqual(state['phase'], 'rolled-back')
        self.assertEqual(len(attempts), 3)
        self.assertEqual(nap.call_args_list, [unittest.mock.call(15)] * 2)

    def test_pair_rollback_retries_live_refusal(self):
        attempts = []
        def refusal(tool, *values, **kwargs):
            if values[0] == 'activate':
                attempts.append(values)
                if len(attempts) == 1:
                    raise RuntimeError('Our battles are live or pending')
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=refusal), patch.object(smoke.time, 'sleep') as nap:
            state = self.execute_pair(self.pair_args(games=4))
        self.assertEqual(state['phase'], 'rolled-back')
        self.assertEqual(self.current['id'], 61)
        self.assertEqual(len(attempts), 2)
        nap.assert_called_once_with(15)

    def test_pair_swap_refusal_deadline(self):
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        error = RuntimeError('Our battles are live or pending')
        attempts = []
        def refusal(tool, *values, **kwargs):
            if values[0] == 'activate':
                attempts.append(values)
                raise error
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=refusal), \
             patch.object(smoke.time, 'monotonic', return_value=0) as clock, \
             patch.object(smoke.time, 'sleep', side_effect=lambda _: setattr(clock, 'return_value', 900)) as nap, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as output, \
             self.assertRaisesRegex(RuntimeError, 'stopped safely') as raised:
            smoke.pair_execute(args, state)
        self.assertIs(raised.exception.__cause__, error)
        self.assertEqual(len(attempts), 1)
        nap.assert_called_once_with(15)
        saved = smoke.load(args.name)
        self.assertEqual(saved['phase'], 'failed')
        self.assertEqual(saved['active_submission']['id'], 62)
        self.assertIn('ROLLBACK REQUIRED', output.getvalue())
        self.assertIn('activate 61 --confirm', output.getvalue())

    def test_swap_other_error_is_not_retried(self):
        error = RuntimeError('zip verification failed')
        with patch.object(smoke, 'run', side_effect=error) as runner, \
             patch.object(smoke.time, 'sleep') as nap, self.assertRaises(RuntimeError) as raised:
            smoke.swap('upload', str(self.bot), '--confirm')
        self.assertIs(raised.exception, error)
        runner.assert_called_once_with('submit.js', 'upload', str(self.bot), '--confirm')
        nap.assert_not_called()

    def test_pair_upload_retry_checks_guards(self):
        for guard, message in (('check_freeze', 'Frozen'), ('pair_time_left', 'Pair hour expired')):
            with self.subTest(guard=guard):
                args = self.pair_args(games=4)
                args.name = guard
                state = smoke.pair_prepare(args)
                attempts = []
                def refusal(tool, *values, **kwargs):
                    if values[0] == 'upload':
                        attempts.append(values)
                        raise RuntimeError('Our battles are live or pending')
                    return self.fake(tool, *values, **kwargs)
                with patch.object(smoke, guard, wraps=getattr(smoke, guard)) as guarded, \
                     patch.object(smoke, 'run', side_effect=refusal), \
                     patch.object(smoke.time, 'sleep', side_effect=lambda _: setattr(guarded, 'side_effect', RuntimeError(message))) as nap, \
                     contextlib.redirect_stderr(io.StringIO()), self.assertRaises(RuntimeError):
                    smoke.pair_execute(args, state)
                self.assertEqual(len(attempts), 1)
                nap.assert_called_once_with(15)
                self.assertEqual(smoke.load(args.name)['error'], message)

    def test_perform_rollback_retries_live_refusal(self):
        state = self.execute_pair(self.pair_args(games=4))
        self.current = {'id': 62, 'name': 'test'}
        attempts = []
        def refusal(tool, *values, **kwargs):
            if values[0] == 'activate':
                attempts.append(values)
                if len(attempts) == 1:
                    raise RuntimeError('Our battles are live or pending')
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=refusal), patch.object(smoke.time, 'sleep') as nap, \
             contextlib.redirect_stdout(io.StringIO()):
            smoke.perform_rollback(state)
        self.assertEqual(smoke.load('test')['phase'], 'rolled-back')
        self.assertEqual(self.current['id'], 61)
        self.assertEqual(len(attempts), 2)
        nap.assert_called_once_with(15)

    def test_pair_no_confirm_and_plan(self):
        for prefix in (['pair'], ['plan', '--pair']):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(smoke.main(prefix + [str(self.bot), '--name', 'test', '--opp', '7,8']), 0)
            self.assertIn('30 per bot', output.getvalue())
            self.assertIn('maps 1,2,3,4,5,6,7,8,9,10,1,2,3,4,5', output.getvalue())
        self.assertFalse(smoke.STATE.exists())
        self.assertFalse(any(a[0] in ('upload', 'request', 'activate') for _, a in self.calls))

    def test_pair_failure_midway_and_after_upload(self):
        for after_upload in (False, True):
            args = self.pair_args(games=4)
            args.name = 'after-upload' if after_upload else 'midway'
            state = smoke.pair_prepare(args)
            self.fail_after_upload = after_upload
            self.fail_new_request = not after_upload
            with contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(RuntimeError):
                smoke.pair_execute(args, state)
            saved = smoke.load(args.name)
            self.assertEqual(saved['phase'], 'failed')
            self.assertEqual(saved['active_submission']['id'], 62)
            self.assertTrue(saved['active_verified'])
            self.assertTrue(saved['rollback_required'])
            self.assertIn('activate 61 --confirm', output.getvalue())
            self.assertEqual(saved['rollback_command'], 'node tools/submit.js activate 61 --confirm')
            self.current = {'id': 61, 'name': 'v61'}
        self.assertFalse(any(a[0] == 'activate' for _, a in self.calls))

    def test_pair_pending_prevents_swap(self):
        self.pending = True
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        with patch.object(smoke.time, 'monotonic', side_effect=[0, 2]), contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'stopped safely'):
            smoke.pair_execute(args, state)
        self.assertFalse(any(a[0] in ('upload', 'activate') for _, a in self.calls))
        self.assertEqual(self.current['id'], 61)

    def test_pair_external_pending_refusal(self):
        self.live = True
        state = smoke.pair_prepare(self.pair_args())
        with self.assertRaisesRegex(RuntimeError, 'live or pending'):
            smoke.pair_execute(self.pair_args(), state)
        self.assertFalse(any(a[0] in ('upload', 'request', 'activate') for _, a in self.calls))

    def test_pair_new_only_skips_the_live_half(self):
        args = self.pair_args(games=30)
        args.new_only = True
        state = self.execute_pair(args)
        self.assertEqual(state['phase'], 'rolled-back')
        self.assertEqual(self.current['id'], 61)
        self.assertEqual((state['planned_total'], state['halves']['old']['phase']), (30, 'skipped'))
        self.assertEqual((len(state['halves']['old']['battle_ids']), len(state['halves']['new']['battle_ids'])), (0, 30))
        requests = [a for _, a in self.calls if a[0] == 'request']
        self.assertTrue(all(a[-1] == 62 for a in requests))
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(smoke.main(['plan', '--pair', '--new-only', str(self.bot), '--name', 'plan-new', '--opp', '7,8', '--games', '30']), 0)
        self.assertIn('new bot only', output.getvalue())
        self.assertIn('New bot vs 7', output.getvalue())

    def test_pair_dev_games_use_the_dev_allowance(self):
        args = self.pair_args(games=30)
        args.new_only = True
        state = smoke.pair_prepare(args)
        self.assertEqual(smoke.pair_cost(state), (0, 30))
        self.normal_remaining = 0
        smoke.pair_budget(state)
        self.remaining = 29
        with self.assertRaisesRegex(RuntimeError, 'Insufficient DEV'):
            smoke.pair_budget(state)
        self.dev = False
        self.assertEqual(smoke.pair_cost(smoke.pair_prepare(args)), (30, 0))
        args.new_only = False
        self.assertEqual(smoke.pair_cost(smoke.pair_prepare(self.pair_args())), (60, 0))

    def test_swap_waits_for_other_teams_battles(self):
        live = iter([True, True, False])
        def battles(tool, *values, **kwargs):
            if values[0] == 'battles':
                return [{'id': 99, 'outcome': 'live', 'results': ['pending']}] if next(live) else []
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=battles), patch.object(smoke.time, 'sleep') as nap:
            smoke.wait_no_pending()
        self.assertEqual(nap.call_count, 2)
        self.live = True
        with patch.object(smoke.time, 'sleep'), patch.object(smoke.time, 'monotonic', side_effect=[0, 901]), \
             self.assertRaisesRegex(RuntimeError, 'live or pending'):
            smoke.wait_no_pending()

    def test_pair_budget_and_freeze(self):
        self.dev = False
        args = self.pair_args()
        state = smoke.pair_prepare(args)
        self.normal_remaining = 59
        with self.assertRaisesRegex(RuntimeError, 'Insufficient normal'):
            smoke.pair_execute(args, state)
        self.assertFalse(smoke.STATE.exists())
        with patch.object(smoke, 'datetime') as clock:
            clock.now.return_value = smoke.FREEZE
            with self.assertRaisesRegex(RuntimeError, 'Frozen'):
                smoke.pair_prepare(args)
            with self.assertRaisesRegex(RuntimeError, 'Frozen'):
                smoke.pair_execute(args, state)
        self.assertFalse(any(a[0] in ('upload', 'request', 'activate') for _, a in self.calls))

    def test_pair_top_and_dev545(self):
        args = self.pair_args(games=4)
        args.opp, args.top = None, 2
        self.assertEqual([o['id'] for o in smoke.pair_prepare(args)['opponents']], [8, 7])
        self.assertTrue(any('--eligible' in a for _, a in self.calls))
        args.top = 3
        with self.assertRaisesRegex(RuntimeError, 'Not enough'):
            smoke.pair_prepare(args)
        args.top, args.opp = None, '545'
        self.assertEqual(smoke.pair_prepare(args)['opponents'][0]['id'], 545)
        self.dev = False
        self.assertFalse(smoke.pair_prepare(args)['opponents'][0]['dev'])

    def test_new_pending_prevents_rollback(self):
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        def pending_new(tool, *values, **kwargs):
            result = self.fake(tool, *values, **kwargs)
            if values[0] == 'request' and self.current['id'] == 62:
                self.pending = True
            return result
        with patch.object(smoke, 'run', side_effect=pending_new), patch.object(smoke.time, 'monotonic', side_effect=itertools.count(0, 2)), contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(RuntimeError):
            smoke.pair_execute(args, state)
        self.assertFalse(any(a[0] == 'activate' for _, a in self.calls))
        self.assertIn('ROLLBACK REQUIRED', output.getvalue())
        self.assertEqual(smoke.load('test')['active_submission']['id'], 62)

    def test_freeze_before_swap_and_hour_expiry(self):
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        def frozen_swap(tool, *values, **kwargs):
            result = self.fake(tool, *values, **kwargs)
            if values[0] == 'battle':
                smoke.FREEZE = smoke.datetime.now(smoke.timezone.utc)
            return result
        with patch.object(smoke, 'FREEZE', smoke.FREEZE), patch.object(smoke, 'run', side_effect=frozen_swap), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(RuntimeError):
            smoke.pair_execute(args, state)
        self.assertFalse(any(a[0] in ('upload', 'activate') for _, a in self.calls))
        with self.assertRaisesRegex(RuntimeError, 'hour expired'):
            smoke.pair_time_left({'expires_at': '2026-01-01T00:00:00+00:00'})

    def test_failure_probe_unavailable_records_last_observation(self):
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        def lost_connection(tool, *values, **kwargs):
            if values[0] == 'upload':
                self.fake(tool, *values, **kwargs)
                self.fail = 'active'
                raise RuntimeError('connection lost after upload')
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=lost_connection), contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(RuntimeError):
            smoke.pair_execute(args, state)
        saved = smoke.load('test')
        self.assertFalse(saved['active_verified'])
        self.assertEqual(saved['active_submission']['id'], 61)
        self.assertIn('active_probe_error', saved)
        self.assertTrue(saved['rollback_required'])
        self.assertIn('verification unavailable', output.getvalue())
        self.assertNotIn('bc_secret', json.dumps(saved))

    def test_pair_report_side_b(self):
        state = self.execute_pair(self.pair_args(games=4))
        self.download_side = 'B'
        with patch.object(smoke, 'picks', return_value='ids'), contextlib.redirect_stdout(io.StringIO()):
            smoke.report(state)
        text = (smoke.STATE / 'test-report.md').read_text()
        self.assertIn('40.0 / 50.0', text)
        self.assertIn('old 0/2; new 0/2', text)


    def test_pair_report(self):
        state = self.execute_pair(self.pair_args(games=4))
        with patch.object(smoke, 'picks', return_value='replay ids for Zhe') as picker, contextlib.redirect_stdout(io.StringIO()):
            smoke.report(state)
        self.assertEqual(picker.call_count, 2)
        text = (smoke.STATE / 'test-report.md').read_text()
        self.assertTrue(text.startswith('Pair test:'))
        self.assertEqual(text.splitlines()[3], '')
        self.assertIn('small sample', text)
        self.assertIn('50.0 / 40.0', text)
        self.assertIn('round-limit', text)
        self.assertIn('| 7 dev_test_1 | 1 | 1 | 1 | 1 |', text)
        self.assertTrue(text.rstrip().endswith('keep vs roll back: author + one OK'))


    def activations(self):
        return [a for _, a in self.calls if a[0] == 'activate']

    def test_restore_picks_the_higher_rated_copy_of_the_same_code(self):
        self.submissions += [self.sub(55, 40, 'main-copy', 1913, 'aaaa'), self.sub(54, 39, 'older-copy', 1890, 'aaaa')]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            args = self.pair_args(games=4)
            smoke.pair_execute(args, smoke.pair_prepare(args))
        self.assertEqual(self.activations(), [('activate', 55, '--confirm')])
        self.assertEqual(self.current['id'], 55)
        self.assertIn('rollback verified: 55 (higher-rated copy of the same code; live before the test: 61)', output.getvalue())
        saved = smoke.load('test')
        self.assertEqual((saved['phase'], saved['rollback_required'], saved['active_verified']), ('rolled-back', False, True))
        self.assertEqual(saved['active_submission']['id'], 55)
        self.assertEqual((saved['rollback']['id'], saved['rollback']['name'], saved['rollback']['version']), (61, 'v61', 42))
        self.assertEqual(saved['rollback_command'], 'node tools/submit.js activate 61 --confirm')
        restore = saved['restore']
        self.assertEqual({k: restore[k] for k in ('id', 'name', 'version', 'rating')},
                         {'id': 55, 'name': 'main-copy', 'version': 40, 'rating': 1913})
        self.assertEqual((restore['rule'], restore['reason'], restore['source_hash'], restore['original_rating']),
                         ('best-rated', 'higher-rated copy of the same code', 'aaaa', 1907))
        self.assertEqual(sorted((c['id'], c['version'], c['rating'], c['status']) for c in restore['candidates']),
                         [(54, 39, 1890, 'idle'), (55, 40, 1913, 'idle'), (61, 42, 1907, 'idle')])
        self.assertIn('chosen_at', restore)

    def test_restore_keeps_the_original_on_a_tie_or_when_it_is_best(self):
        for rating, reason in ((1907, 'tie with 55; original kept'), (1906, 'original is the best-rated copy')):
            with self.subTest(rating=rating):
                self.calls.clear()
                self.submissions = [self.sub(61, 42, 'v61', 1907, 'aaaa'), self.sub(62, 43, 'test', 1990, 'bbbb', 'active'),
                                    self.sub(55, 40, 'main-copy', rating, 'aaaa')]
                args = self.pair_args(games=4)
                args.name = f'keep{rating}'
                self.execute_pair(args)
                self.assertEqual(self.activations(), [('activate', 61, '--confirm')])
                restore = smoke.load(args.name)['restore']
                self.assertEqual({k: restore[k] for k in ('id', 'name', 'version', 'rating')},
                                 {'id': 61, 'name': 'v61', 'version': 42, 'rating': 1907})
                self.assertEqual(restore['reason'], reason)
                self.assertEqual(len(restore['candidates']), 2)

    def test_restore_ignores_a_higher_rated_submission_with_other_code(self):
        self.submissions += [self.sub(56, 41, 'other-code', 2500, 'cccc'), self.sub(57, 44, 'no-hash', 2600, None)]
        self.execute_pair(self.pair_args(games=4))
        self.assertEqual(self.activations(), [('activate', 61, '--confirm')])
        restore = smoke.load('test')['restore']
        self.assertEqual(restore['id'], 61)
        self.assertEqual(restore['reason'], 'no other usable copy of the same code; original kept')
        self.assertEqual([c['id'] for c in restore['candidates']], [61])

    def test_restore_takes_the_best_of_several_copies(self):
        self.submissions += [self.sub(55, 40, 'copy-a', 1913, 'aaaa'), self.sub(57, 44, 'copy-b', 1920, 'aaaa'),
                             self.sub(58, 45, 'copy-c', 1920, 'aaaa')]
        self.execute_pair(self.pair_args(games=4))
        self.assertEqual(self.activations(), [('activate', 57, '--confirm')])

    def test_restore_falls_back_to_the_original_when_unverifiable(self):
        copy_ = self.sub(55, 40, 'main-copy', 1913, 'aaaa')
        test = self.sub(62, 43, 'test', 1990, 'bbbb', 'active')
        cases = {
            'unreadable': (None, 'submissions list unreadable; original kept'),
            'not-a-list': ({'rows': []}, 'submissions list malformed; original kept'),
            'bad-row': ([self.sub(61, 42, 'v61', 1907, 'aaaa'), 'junk', copy_], 'submissions list malformed; original kept'),
            'duplicate-id': ([self.sub(61, 42, 'v61', 1907, 'aaaa'), copy_, copy_], 'submissions list malformed; original kept'),
            'original-missing': ([test, copy_], 'original is not in the submissions list; original kept'),
            'no-hash': ([self.sub(61, 42, 'v61', 1907, None), test, self.sub(55, 40, 'main-copy', 1913, None)],
                        'original has no source hash; original kept'),
            'empty-hash': ([self.sub(61, 42, 'v61', 1907, ''), test, self.sub(55, 40, 'main-copy', 1913, '')],
                           'original has no source hash; original kept'),
            'no-original-rating': ([self.sub(61, 42, 'v61', None, 'aaaa'), test, copy_],
                                   'original has no readable rating; original kept'),
            'copy-rating-missing': ([self.sub(61, 42, 'v61', 1907, 'aaaa'), test, self.sub(55, 40, 'main-copy', None, 'aaaa')],
                                    'no other usable copy of the same code; original kept'),
            'copy-rating-text': ([self.sub(61, 42, 'v61', 1907, 'aaaa'), test, self.sub(55, 40, 'main-copy', '2000', 'aaaa')],
                                 'no other usable copy of the same code; original kept'),
            'copy-rating-bool': ([self.sub(61, 42, 'v61', 1907, 'aaaa'), test, self.sub(55, 40, 'main-copy', True, 'aaaa')],
                                 'no other usable copy of the same code; original kept'),
            'copy-not-built': ([self.sub(61, 42, 'v61', 1907, 'aaaa'), test, self.sub(55, 40, 'main-copy', 1913, 'aaaa', 'failed')],
                               'no other usable copy of the same code; original kept'),
        }
        for name, (rows, reason) in cases.items():
            with self.subTest(case=name):
                self.calls.clear()
                self.submissions = rows
                args = self.pair_args(games=4)
                args.name = name
                state = self.execute_pair(args)
                self.assertEqual(self.activations(), [('activate', 61, '--confirm')])
                self.assertEqual((self.current['id'], state['phase'], state['rollback_required']), (61, 'rolled-back', False))
                restore = smoke.load(name)['restore']
                self.assertEqual((restore['id'], restore['name'], restore['reason']), (61, 'v61', reason))

    def test_restore_choice_error_keeps_the_original(self):
        self.submissions += [self.sub(55, 40, 'main-copy', 1913, 'aaaa')]
        with patch.object(smoke, 'rating_of', side_effect=ZeroDivisionError('boom')):
            self.execute_pair(self.pair_args(games=4))
        self.assertEqual(self.activations(), [('activate', 61, '--confirm')])
        restore = smoke.load('test')['restore']
        self.assertEqual((restore['id'], restore['reason']), (61, 'restore choice failed (ZeroDivisionError); original kept'))

    def test_restore_switch_off_restores_exactly_the_original(self):
        self.submissions += [self.sub(55, 40, 'main-copy', 1913, 'aaaa')]
        for value in ('0', 'off', 'False', ' no '):
            with self.subTest(value=value):
                self.calls.clear()
                os.environ[smoke.RESTORE_SWITCH] = value
                args = self.pair_args(games=4)
                args.name = 'off-' + value.strip().lower()
                self.execute_pair(args)
                self.assertEqual(self.activations(), [('activate', 61, '--confirm')])
                self.assertFalse(any(a[0] == 'submissions' for _, a in self.calls))
                restore = smoke.load(args.name)['restore']
                self.assertEqual((restore['id'], restore['rule'], restore['candidates']), (61, 'exact', []))
                self.assertEqual(restore['reason'], 'SMOKE_RESTORE_BEST is off; exact restore')
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    smoke.pair_plan(args, smoke.pair_prepare(args))
                self.assertIn('Restore rule: exactly the live bot (SMOKE_RESTORE_BEST is off)', output.getvalue())
        os.environ[smoke.RESTORE_SWITCH] = '1'
        self.calls.clear()
        args = self.pair_args(games=4)
        args.name = 'on'
        self.execute_pair(args)
        self.assertEqual(self.activations(), [('activate', 55, '--confirm')])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            smoke.pair_plan(args, smoke.pair_prepare(args))
        self.assertIn('Restore rule: the best-rated copy of the same code as the live bot', output.getvalue())

    def test_restore_test_bot_only_when_it_is_the_same_code(self):
        self.submissions = [self.sub(61, 42, 'v61', 1907, 'aaaa'), self.sub(62, 43, 'test', 1950, 'aaaa', 'active')]
        state = self.execute_pair(self.pair_args(games=4))
        self.assertEqual(self.activations(), [])
        self.assertEqual((self.current['id'], state['phase'], state['rollback_required']), (62, 'rolled-back', False))
        saved = smoke.load('test')
        self.assertEqual((saved['restore']['id'], saved['rollback']['id'], saved['active_submission']['id']), (62, 61, 62))
        self.calls.clear()
        self.current = {'id': 61, 'name': 'v61'}
        self.submissions = [self.sub(61, 42, 'v61', 1907, 'aaaa'), self.sub(62, 43, 'test', 1950, 'bbbb', 'active')]
        args = self.pair_args(games=4)
        args.name = 'other-code'
        self.execute_pair(args)
        self.assertEqual(self.activations(), [('activate', 61, '--confirm')])

    def test_swap_back_verifies_the_chosen_copy(self):
        self.submissions += [self.sub(55, 40, 'main-copy', 1913, 'aaaa')]
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        def wrong(tool, *values, **kwargs):
            if values[0] == 'activate':
                self.calls.append((tool, values))
                self.current = {'id': 61, 'name': 'v61'}
                return 'activated'
            return self.fake(tool, *values, **kwargs)
        with patch.object(smoke, 'run', side_effect=wrong), contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaisesRegex(RuntimeError, 'stopped safely'):
            smoke.pair_execute(args, state)
        self.assertEqual(self.activations(), [('activate', 55, '--confirm')])
        saved = smoke.load('test')
        self.assertEqual((saved['phase'], saved['error']), ('failed', 'Active submission identity not verified'))
        self.assertFalse(saved['rollback_required'])
        self.assertNotIn('ROLLBACK REQUIRED', output.getvalue())

    def test_failed_swap_to_the_chosen_copy_still_requires_rollback(self):
        self.submissions += [self.sub(55, 40, 'main-copy', 1913, 'aaaa')]
        for switched in (False, True):
            with self.subTest(switched=switched):
                self.calls.clear()
                self.current = {'id': 61, 'name': 'v61'}
                args = self.pair_args(games=4)
                args.name = f'swap-{switched}'
                state = smoke.pair_prepare(args)
                def broken(tool, *values, **kwargs):
                    if values[0] == 'activate':
                        if switched:
                            self.current = {'id': int(values[1]), 'name': 'main-copy'}
                        raise RuntimeError('socket hang up')
                    return self.fake(tool, *values, **kwargs)
                with patch.object(smoke, 'run', side_effect=broken), contextlib.redirect_stdout(io.StringIO()), \
                     contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(RuntimeError):
                    smoke.pair_execute(args, state)
                saved = smoke.load(args.name)
                self.assertEqual((saved['phase'], saved['restore']['id']), ('failed', 55))
                self.assertEqual(saved['active_submission']['id'], 55 if switched else 62)
                self.assertEqual(saved['rollback_required'], not switched)
                self.assertEqual('activate 61 --confirm' in output.getvalue(), not switched)

    def test_perform_rollback_uses_the_same_rule(self):
        args = self.pair_args(games=4)
        state = smoke.pair_prepare(args)
        self.fail_new_request = True
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(RuntimeError):
            smoke.pair_execute(args, state)
        self.assertEqual((self.current['id'], smoke.load('test')['rollback_required']), (62, True))
        self.assertNotIn('restore', smoke.load('test'))
        self.submissions += [self.sub(55, 40, 'main-copy', 1913, 'aaaa')]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            smoke.perform_rollback(state)
        self.assertEqual(self.activations(), [('activate', 55, '--confirm')])
        self.assertIn('Verified active: 55', output.getvalue())
        saved = smoke.load('test')
        self.assertEqual((saved['phase'], saved['rollback_required'], saved['restore']['id'], saved['rollback']['id']),
                         ('rolled-back', False, 55, 61))
        self.calls.clear()
        with contextlib.redirect_stdout(io.StringIO()) as output:
            smoke.perform_rollback(state)
        self.assertEqual(self.activations(), [])
        self.assertIn('No swap: 55 is live', output.getvalue())
        self.calls.clear()
        self.submissions = None
        with contextlib.redirect_stdout(io.StringIO()):
            smoke.perform_rollback(state)
        self.assertEqual(self.activations(), [('activate', 61, '--confirm')])
        self.assertEqual(smoke.load('test')['restore']['reason'], 'submissions list unreadable; original kept')
        self.submissions = [self.sub(61, 42, 'v61', 1907, 'aaaa'), self.sub(55, 40, 'main-copy', 1913, 'aaaa')]
        with patch.object(smoke, 'active', return_value={'id': 61, 'name': 'v61'}), contextlib.redirect_stdout(io.StringIO()), \
             self.assertRaisesRegex(RuntimeError, 'verification failed'):
            smoke.perform_rollback(state)

    def test_source_hash_saved_with_the_versions(self):
        self.execute_pair(self.pair_args(games=4))
        saved = smoke.load('test')
        self.assertEqual(saved['rollback']['source_hash'], 'aaaa')
        self.assertEqual(saved['halves']['old']['submission']['source_hash'], 'aaaa')
        self.assertEqual(saved['halves']['new']['submission']['source_hash'], 'bbbb')

    def test_safe_and_label(self):
        self.assertNotIn('secret', smoke.safe('bc_secret Bearer secret'))
        with self.assertRaises(Exception):
            smoke.label('../escape')


if __name__ == '__main__':
    unittest.main()
