"""Run the wrapper in a temporary directory with all online tools stubbed."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest


class RunPairLiveOnly(unittest.TestCase):
    @unittest.skipUnless(shutil.which('zsh'), 'zsh unavailable')
    def test_wrapper_modes_and_no_live_only_rollback(self):
        source = Path(__file__).resolve().parents[1] / 'data/online/smoke/run-pair.sh'
        for mode in ('live', 'live-failed', 'live-unknown', 'new', 'new-unknown', 'baseline'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'data/online/smoke').mkdir(parents=True)
                (root / 'data/guide').mkdir(parents=True)
                bindir = root / 'bin'
                bindir.mkdir()
                wrapper = root / 'run-pair.sh'
                lines = source.read_text().splitlines()
                lines = ['cd ' + shlex.quote(tmp) if line.startswith('cd ') else line for line in lines]
                wrapper.write_text('\n'.join(lines) + '\n')
                stub = '#!' + sys.executable + '\n' + '''import json, os, pathlib, sys
root = pathlib.Path(os.environ['STUB_ROOT'])
args = sys.argv[1:]
name = pathlib.Path(sys.argv[0]).name
with (root / 'calls.jsonl').open('a') as f:
    f.write(json.dumps([name, args]) + '\\n')
if name == 'sleep':
    import time
    deadline = time.monotonic() + 2
    while not (root / 'data/online/smoke/sample.json').exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    time.sleep(0.05)
    sys.exit(0)
if name == 'node':
    print('61 live (2026-10-05)' if len(args) > 1 and args[1] == 'active' else 'UNEXPECTED NODE')
    sys.exit(0 if len(args) > 1 and args[1] == 'active' else 1)
if args[:2] == ['tools/smoke.py', 'pair']:
    failed = os.environ['STUB_MODE'] == 'live-failed'
    (root / 'data/online/smoke/sample.json').write_text(json.dumps(dict(
        phase='failed' if failed else 'rolled-back', error='Active submission identity not verified',
        kind='pair', label='sample', old_only='--old-only' in args,
        active_verified=True, rollback_required=False, active_submission={'id': 99}, rollback={'id': 61, 'version': 42},
        halves={'old': {'submission': {'id': 61, 'version': 42}, 'battle_ids': [1]},
                'new': {'submission': None if '--old-only' in args else {'id': 62, 'version': 43}}})))
    if os.environ['STUB_MODE'].endswith('unknown'):
        path = root / 'data/online/smoke/sample.json'
        state = json.loads(path.read_text())
        state['rollback'].pop('version')
        for half in state['halves'].values():
            if half['submission']:
                half['submission'].pop('version')
        path.write_text(json.dumps(state))
    if '--old-only' not in args:
        import time
        deadline = time.monotonic() + 2
        while not (root / 'notices.txt').exists() and time.monotonic() < deadline:
            time.sleep(0.01)
    sys.exit(1 if failed else 0)
if args and args[0] == 'tools/meowbot.py':
    with (root / 'notices.txt').open('a') as f:
        f.write(pathlib.Path(args[-1]).read_text())
    sys.exit(0)
if args and args[0] == 'tools/pair_report.py':
    sys.exit(0)
if args and args[0] in ('-', '-c'):
    os.execv(os.environ['REAL_PYTHON'], [os.environ['REAL_PYTHON']] + args)
sys.exit('Unexpected tool: ' + repr(args))
'''
                for name in ('python3', 'node', 'sleep'):
                    path = bindir / name
                    path.write_text(stub)
                    path.chmod(0o755)
                env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ['PATH'],
                           STUB_ROOT=tmp, STUB_MODE=mode, REAL_PYTHON=sys.executable,
                           LIVE_ONLY='1' if mode.startswith('live') else '0', BASELINE='1' if mode == 'baseline' else '0')
                result = subprocess.run(['zsh', str(wrapper), 'sample', '-', 'card reference', '19,87,545'],
                                        cwd=tmp, env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1 if mode == 'live-failed' else 0, result.stderr)
                calls = [json.loads(line) for line in (root / 'calls.jsonl').read_text().splitlines()]
                pair = next(args for name, args in calls if args[:2] == ['tools/smoke.py', 'pair'])
                self.assertEqual(pair[pair.index('--ref') + 1], 'card reference')
                self.assertIn('--old-only' if mode.startswith('live') else '--new-only' if mode.startswith('new') else '--games', pair)
                self.assertEqual(pair[pair.index('--games') + 1], '90' if mode == 'baseline' else '45')
                notices = (root / 'notices.txt').read_text()
                if mode.startswith('live'):
                    main = 'live bot' if mode.endswith('unknown') else 'v42 main'
                    self.assertIn(f'🧪 more {main} games for the baseline: 15 maps vs each of test4 + WeHaveQuizzes + dev1. no bot swap, uploads are fine meanwhile', notices)
                    self.assertNotIn("please don't upload", notices)
                    self.assertNotIn('swapped back', notices)
                    self.assertEqual(sum(name == 'node' for name, _ in calls), 1)
                    self.assertFalse(any(args[:2] == ['tools/smoke.py', 'rollback'] for _, args in calls))
                    reports = [args for _, args in calls if args and args[0] == 'tools/pair_report.py']
                    self.assertEqual(reports, [] if mode == 'live-failed' else [['tools/pair_report.py', 'sample', '--post', 'card reference']])
                else:
                    main = 'live bot' if mode.endswith('unknown') else 'v42 main'
                    done = ('✅ done, swapped back: the live bot is active again. card reference comparison finished, results coming on the card'
                            if mode.endswith('unknown') else '✅ done, swapped back: v42 main is active again. v43 (card reference) finished, result coming')
                    self.assertEqual(notices.splitlines(), [
                        f'🧪 testing online now: new bot = {main} + card reference, 15 maps vs each of test4 + WeHaveQuizzes + dev1. the active bot swaps for ~20 min, please don\'t upload or swap until "done, swapped back"', done])
                    self.assertEqual(sum(name == 'node' for name, _ in calls), 2)
