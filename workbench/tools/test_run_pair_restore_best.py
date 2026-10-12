"""The wrapper and the chosen restore copy; online tools and notices are stubbed, nothing reaches the server."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'data/online/smoke/run-pair.sh'
SWITCH_WARNING = ('⚠️ card reference online test stopped: someone set the active bot to {} during the test. '
                  'leaving it as it is, nothing was swapped back. the bot that was live before the test was 61')


def state(restore_id=63, rating=1913, version=47):
    return dict(kind='pair', label='sample', phase='rolled-back', rollback_required=False, active_verified=True,
                rollback={'id': 61, 'name': 'main-bob1', 'version': 44},
                restore={'id': restore_id, 'name': 'card-39', 'version': version, 'rating': rating,
                         'original_rating': 1907, 'rule': 'best-rated', 'reason': 'higher-rated copy of the same code',
                         'candidates': [{'id': 61, 'rating': 1907}, {'id': restore_id, 'rating': rating}]},
                halves={'old': {'submission': {'id': 61, 'version': 44}},
                        'new': {'submission': {'id': 62, 'name': 'test', 'version': 48}, 'phase': 'finished'}})


@unittest.skipUnless(shutil.which('zsh'), 'zsh unavailable')
class RunPairRestoreFunctions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'data/online/smoke').mkdir(parents=True)
        self.path = self.root / 'data/online/smoke/sample.json'
        self.state = state()
        self.path.write_text(json.dumps(self.state))
        source = SOURCE.read_text()
        self.functions = (source[source.index('bot_names() {'):source.index('# Only a verified, unplayed upload failure')]
                          + source[source.index('start_ready() {'):source.index('network_retries=0')])

    def run_functions(self, body, baseid='61', switch=None):
        script = ('cd ' + shlex.quote(str(self.root)) + '\n'
                  f'LABEL=sample; BASEID={baseid}; REF="card reference"; NAMES="test4 + dev1"; announced=0\n'
                  'say() { print -r -- "$1" >> notices.txt; }\n'
                  + self.functions + body)
        env = {k: v for k, v in os.environ.items() if k != 'SMOKE_RESTORE_BEST'}
        if switch is not None:
            env['SMOKE_RESTORE_BEST'] = switch
        return subprocess.run(['zsh', '-c', script], capture_output=True, text=True, timeout=10, env=env)

    def probe(self, active, **kwargs):
        body = (f'active="{active}"\nrestored && print restored\ncheck_rollback && print guard-ok\n')
        result = self.run_functions(body, **kwargs)
        notices = self.root / 'notices.txt'
        return result.returncode, result.stdout.split(), notices.read_text().splitlines() if notices.exists() else []

    def test_chosen_copy_and_original_count_as_restored(self):
        for active in ('63 card-39 (2026-10-06)', '61 main-bob1 (2026-10-06)'):
            with self.subTest(active=active):
                self.assertEqual(self.probe(active), (0, ['restored', 'guard-ok'], []))
                self.assertEqual(json.loads(self.path.read_text()), self.state)

    def test_test_bot_is_not_restored_and_may_be_swapped_back(self):
        self.assertEqual(self.probe('62 test (2026-10-06)'), (0, ['guard-ok'], []))
        self.assertEqual(json.loads(self.path.read_text()), self.state)

    def test_any_other_id_is_still_a_manual_switch(self):
        code, out, notices = self.probe('99 teammate choice (2026-10-06)')
        self.assertEqual((code, out), (1, []))
        self.assertEqual(notices, [SWITCH_WARNING.format('99 teammate choice')])
        saved = json.loads(self.path.read_text())
        self.assertTrue(saved['rollback_skipped_manual_switch'])
        self.assertEqual(saved['active_submission'], {'id': 99, 'name': 'teammate choice'})
        self.assertEqual((saved['rollback']['id'], saved['restore']['id']), (61, 63))

    def test_switch_off_accepts_only_the_original(self):
        for value in ('0', 'off'):
            with self.subTest(value=value):
                (self.root / 'notices.txt').unlink(missing_ok=True)
                self.path.write_text(json.dumps(self.state))
                self.assertEqual(self.probe('61 main-bob1 (2026-10-06)', switch=value), (0, ['restored', 'guard-ok'], []))
                code, out, notices = self.probe('63 card-39 (2026-10-06)', switch=value)
                self.assertEqual((code, out), (1, []))
                self.assertEqual(notices[-1], SWITCH_WARNING.format('63 card-39'))
        self.path.write_text(json.dumps(self.state))
        (self.root / 'notices.txt').unlink()
        self.assertEqual(self.probe('63 card-39 (2026-10-06)', switch='1'), (0, ['restored', 'guard-ok'], []))

    def test_copy_chosen_for_another_live_bot_is_ignored(self):
        self.state['rollback']['id'] = 60
        self.path.write_text(json.dumps(self.state))
        code, out, notices = self.probe('63 card-39 (2026-10-06)')
        self.assertEqual((code, out, len(notices)), (1, [], 1))

    def test_unusable_restore_records_are_ignored(self):
        for restore in (None, {}, {'id': '63'}, {'id': True}, 'junk'):
            with self.subTest(restore=restore):
                (self.root / 'notices.txt').unlink(missing_ok=True)
                self.state['restore'] = restore
                self.path.write_text(json.dumps(self.state))
                self.assertEqual(self.probe('61 main-bob1 (2026-10-06)')[:2], (0, ['restored', 'guard-ok']))
                self.assertEqual(self.probe('63 card-39 (2026-10-06)')[:2], (1, []))

    def test_unreadable_active_is_never_restored(self):
        for baseid in ('61', 'fetch', '""'):
            with self.subTest(baseid=baseid):
                result = self.run_functions('active="fetch failed"\nrestored && print restored\n'
                                            'check_rollback && print guard-ok\nprint retry-later\n', baseid=baseid)
                self.assertEqual(result.stdout.split(), ['retry-later'])
                self.assertFalse((self.root / 'notices.txt').exists())

    def notice(self, *args):
        result = self.run_functions('bot_names ' + ' '.join(args) + '\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_done_notice_when_the_original_is_live(self):
        original = '✅ done, swapped back: v44 main is active again. v48 (card reference) finished, result coming'
        self.assertEqual(self.notice('done', '61'), original)
        self.assertEqual(self.notice('done'), original)
        self.state['restore'] = dict(self.state['restore'], id=61, version=44, rating=1907)
        self.path.write_text(json.dumps(self.state))
        self.assertEqual(self.notice('done', '61'), original)
        del self.state['restore']
        self.path.write_text(json.dumps(self.state))
        self.assertEqual(self.notice('done', '61'), original)

    def test_done_notice_when_a_higher_rated_copy_is_live(self):
        self.assertEqual(self.notice('done', '63'),
                         '✅ done, swapped back. v47 (1913) is live, the higher-rated copy of the same code; v44 was 1907. '
                         'v48 (card reference) finished, result coming')
        self.assertEqual(self.notice('start'), 'new bot = v44 main + card reference, 15 maps vs each of test4 + dev1')

    def test_done_notice_when_the_test_bot_is_the_chosen_copy(self):
        self.state['restore'] = dict(self.state['restore'], id=62, version=48, rating=1950)
        self.path.write_text(json.dumps(self.state))
        self.assertEqual(self.notice('done', '62'),
                         '✅ done, swapped back. v48 (1950) stays live, the higher-rated copy of the same code; v44 was 1907. '
                         'v48 (card reference) finished, result coming')

    def test_done_notice_survives_an_unusable_restore_record(self):
        for restore in ('junk', ['x'], {'id': '63'}):
            with self.subTest(restore=restore):
                self.state['restore'] = restore
                self.path.write_text(json.dumps(self.state))
                self.assertEqual(self.notice('done', '61'),
                                 '✅ done, swapped back: v44 main is active again. v48 (card reference) finished, result coming')

    def test_done_notice_with_missing_numbers(self):
        self.state['restore'].update(rating=None, version=None)
        self.state['halves']['new']['submission'].pop('version')
        self.path.write_text(json.dumps(self.state))
        self.assertEqual(self.notice('done', '63'),
                         '✅ done, swapped back. submission 63 is live, a copy of the same code as v44. '
                         'card reference comparison finished, results coming on the card')


STUB = '''import json, os, pathlib, sys, time
root = pathlib.Path(os.environ['STUB_ROOT'])
args = sys.argv[1:]
name = pathlib.Path(sys.argv[0]).name
calls = root / 'calls.jsonl'
earlier = calls.read_text().splitlines() if calls.exists() else []
with calls.open('a') as f:
    f.write(json.dumps([name, args]) + '\\n')
state = root / 'data/online/smoke/sample.json'
if name == 'sleep':
    deadline = time.monotonic() + 2
    while not state.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    time.sleep(0.05)
    sys.exit(0)
if name == 'node':
    if args[1:2] != ['active']:
        print('UNEXPECTED NODE')
        sys.exit(1)
    live = root / 'active.txt'
    print(live.read_text() if live.exists() else '61 main-bob1 (2026-10-05)')
    sys.exit(0)
if args[:2] == ['tools/smoke.py', 'pair']:
    state.write_text(os.environ['STUB_STATE'])
    (root / 'active.txt').write_text(os.environ['STUB_ACTIVE_AFTER'])
    deadline = time.monotonic() + 2
    while not (root / 'notices.txt').exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    sys.exit(int(os.environ.get('STUB_PAIR_EXIT', '0')))
if args[:2] == ['tools/smoke.py', 'rollback'] and os.environ.get('STUB_ROLLBACK_STATE'):
    state.write_text(os.environ['STUB_ROLLBACK_STATE'])
    (root / 'active.txt').write_text(os.environ['STUB_ROLLBACK_ACTIVE'])
    sys.exit(0)
if args and args[0] == 'tools/meowbot.py':
    with (root / 'notices.txt').open('a') as f:
        f.write(pathlib.Path(args[-1]).read_text())
    sys.exit(0)
if args and args[0] in ('-', '-c'):
    os.execv(os.environ['REAL_PYTHON'], [os.environ['REAL_PYTHON']] + args)
sys.exit('Unexpected tool: ' + repr(args))
'''
START = ('🧪 testing online now: new bot = v44 main + card reference, 15 maps vs each of test4 + dev1. '
         'the active bot swaps for ~20 min, please don\'t upload or swap until "done, swapped back"')


@unittest.skipUnless(shutil.which('zsh'), 'zsh unavailable')
class RunPairRestoreWrapper(unittest.TestCase):
    def run_wrapper(self, active_after, saved, switch=None, rollbacks=0, **stub):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data/online/smoke').mkdir(parents=True)
            (root / 'data/guide').mkdir(parents=True)
            bindir = root / 'bin'
            bindir.mkdir()
            wrapper = root / 'run-pair.sh'
            lines = ['cd ' + shlex.quote(tmp) if line.startswith('cd ') else line for line in SOURCE.read_text().splitlines()]
            wrapper.write_text('\n'.join(lines) + '\n')
            for name in ('python3', 'node', 'sleep'):
                path = bindir / name
                path.write_text('#!' + sys.executable + '\n' + STUB)
                path.chmod(0o755)
            env = {k: v for k, v in os.environ.items() if k not in ('SMOKE_RESTORE_BEST', 'LIVE_ONLY', 'BASELINE')}
            env.update(PATH=str(bindir) + os.pathsep + os.environ['PATH'], STUB_ROOT=tmp, REAL_PYTHON=sys.executable,
                       STUB_ACTIVE_AFTER=active_after, STUB_STATE=json.dumps(saved))
            env.update(stub)
            if switch is not None:
                env['SMOKE_RESTORE_BEST'] = switch
            result = subprocess.run(['zsh', str(wrapper), 'sample', '-', 'card reference', '19,545'],
                                    cwd=tmp, env=env, capture_output=True, text=True, timeout=20)
            calls = [json.loads(line) for line in (root / 'calls.jsonl').read_text().splitlines()]
            self.assertEqual(sum(args[:2] == ['tools/smoke.py', 'rollback'] for _, args in calls), rollbacks, calls)
            self.assertFalse(any(name == 'node' and args[1:2] != ['active'] for name, args in calls), calls)
            self.assertTrue((root / 'data/online/smoke/sample-finished').exists())
            return result.returncode, (root / 'notices.txt').read_text().splitlines(), json.loads((root / 'data/online/smoke/sample.json').read_text())

    def test_higher_rated_copy_is_reported_as_swapped_back(self):
        code, notices, saved = self.run_wrapper('63 card-39 (2026-10-06)', state())
        self.assertEqual(code, 0)
        self.assertEqual(notices, [START, '✅ done, swapped back. v47 (1913) is live, the higher-rated copy of the same code; '
                                          'v44 was 1907. v48 (card reference) finished, result coming'])
        self.assertEqual(saved, state())

    def test_original_keeps_the_usual_notice(self):
        code, notices, _ = self.run_wrapper('61 main-bob1 (2026-10-06)', state(restore_id=61, rating=1907, version=44))
        self.assertEqual(code, 0)
        self.assertEqual(notices, [START, '✅ done, swapped back: v44 main is active again. v48 (card reference) finished, result coming'])

    def test_late_swap_back_to_the_chosen_copy(self):
        failed = state()
        failed.update(phase='failed', rollback_required=True, error='Our battles are live or pending; refusing to swap or start')
        del failed['restore']
        code, notices, saved = self.run_wrapper('62 test (2026-10-06)', failed, rollbacks=1, STUB_PAIR_EXIT='1',
                                                STUB_ROLLBACK_STATE=json.dumps(state()),
                                                STUB_ROLLBACK_ACTIVE='63 card-39 (2026-10-06)')
        self.assertEqual(notices, [START, '✅ done, swapped back. v47 (1913) is live, the higher-rated copy of the same code; '
                                          'v44 was 1907. v48 (card reference) finished, result coming'])
        self.assertEqual(saved, state())

    def test_late_swap_back_to_the_original(self):
        failed = state()
        failed.update(phase='failed', rollback_required=True, error='Our battles are live or pending; refusing to swap or start')
        del failed['restore']
        code, notices, _ = self.run_wrapper('62 test (2026-10-06)', failed, rollbacks=1, STUB_PAIR_EXIT='1',
                                            STUB_ROLLBACK_STATE=json.dumps(state(restore_id=61, rating=1907, version=44)),
                                            STUB_ROLLBACK_ACTIVE='61 main-bob1 (2026-10-06)')
        self.assertEqual(notices, [START, '✅ done, swapped back: v44 main is active again. v48 (card reference) finished, result coming'])

    def test_stopped_early_with_the_chosen_copy_live(self):
        stopped = state()
        stopped['phase'] = 'failed'
        stopped['halves']['new']['phase'] = None
        stopped['error'] = 'Active submission identity not verified'
        code, notices, _ = self.run_wrapper('63 card-39 (2026-10-06)', stopped, STUB_PAIR_EXIT='1')
        self.assertEqual(notices, [START, '⚠️ card reference online test stopped early: Active submission identity not verified. '
                                          'the live bot is active, nothing is broken. checking what happened'])

    def test_foreign_id_is_left_alone_and_reported(self):
        code, notices, saved = self.run_wrapper('99 teammate choice (2026-10-06)', state())
        self.assertEqual(code, 1)
        self.assertEqual(notices, [START, SWITCH_WARNING.format('99 teammate choice')])
        self.assertTrue(saved['rollback_skipped_manual_switch'])

    def test_switch_off_does_not_accept_the_copy(self):
        code, notices, saved = self.run_wrapper('63 card-39 (2026-10-06)', state(), switch='0')
        self.assertEqual(code, 1)
        self.assertEqual(notices, [START, SWITCH_WARNING.format('63 card-39')])
        self.assertTrue(saved['rollback_skipped_manual_switch'])


if __name__ == '__main__':
    unittest.main()
