"""Exercise wrapper functions in isolation; no online tools or notices are invoked."""
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which('zsh'), 'zsh unavailable')
class RunPairManualSwitch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'data/online/smoke').mkdir(parents=True)
        self.path = self.root / 'data/online/smoke/sample.json'
        self.state = dict(phase='failed', rollback_required=True, rollback={'id': 61},
                          halves={'new': {'submission': {'id': 62, 'name': 'test'}}})
        self.path.write_text(json.dumps(self.state))
        source = (Path(__file__).resolve().parents[1] / 'data/online/smoke/run-pair.sh').read_text()
        self.functions = source[source.index('start_ready() {'):source.index('network_retries=0')]

    def run_functions(self, body):
        script = ('cd ' + shlex.quote(str(self.root)) + '\n'
                  'LABEL=sample; BASEID=61; REF="card reference"; announced=0\n'
                  'say() { print -r -- "$1" >> notices.txt; }\n'
                  'bot_names() { print -r -- "new bot = live + card reference"; }\n'
                  + self.functions + body)
        return subprocess.run(['zsh', '-c', script], capture_output=True, text=True, timeout=5)

    def test_active_test_allows_rollback(self):
        result = self.run_functions('active="62 test (2026-10-06)"\ncheck_rollback\nprint rollback-allowed\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'rollback-allowed')
        self.assertEqual(json.loads(self.path.read_text()), self.state)
        self.assertFalse((self.root / 'notices.txt').exists())

    def test_active_base_keeps_existing_behavior(self):
        result = self.run_functions('active="61 live (2026-10-06)"\ncheck_rollback\nprint base-unchanged\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'base-unchanged')
        self.assertEqual(json.loads(self.path.read_text()), self.state)
        self.assertFalse((self.root / 'notices.txt').exists())

    def test_manual_switch_stops_once_and_persists(self):
        body = 'active="99 teammate choice (2026-10-06)"\ncheck_rollback\nprint must-not-rollback\n'
        result = self.run_functions(body)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn('must-not-rollback', result.stdout)
        state = json.loads(self.path.read_text())
        self.assertFalse(state['rollback_required'])
        self.assertTrue(state['rollback_skipped_manual_switch'])
        self.assertEqual(state['active_submission'], {'id': 99, 'name': 'teammate choice'})
        self.assertEqual(state['note'], 'active bot was changed by hand to 99 and the rollback was skipped')
        self.assertEqual((self.root / 'notices.txt').read_text().splitlines(), [
            '⚠️ card reference online test stopped: someone set the active bot to 99 teammate choice during the test. leaving it as it is, nothing was swapped back. the bot that was live before the test was 61'])
        for active in ('99 teammate choice', '62 test'):
            result = self.run_functions(body.replace('99 teammate choice', active))
            self.assertEqual(result.returncode, 1)
        self.assertEqual(len((self.root / 'notices.txt').read_text().splitlines()), 1)
        self.assertTrue((self.root / 'data/online/smoke/sample-finished').exists())

    def test_unreadable_active_never_allows_rollback(self):
        result = self.run_functions('active="fetch failed"\ncheck_rollback && print must-not-rollback\nprint retry-later\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('must-not-rollback', result.stdout)
        self.assertIn('retry-later', result.stdout)
        self.assertFalse((self.root / 'notices.txt').exists())
        self.assertEqual(json.loads(self.path.read_text()), self.state)

    def test_start_notice_after_retries_only_once(self):
        self.state.update(phase='uploading', halves={'new': {'submission': None}})
        self.path.write_text(json.dumps(self.state))
        result = self.run_functions('attempts=3; network_retries=2\nannounce_start\nannounce_start\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        notices = (self.root / 'notices.txt').read_text().splitlines()
        self.assertEqual(len(notices), 1)
        self.assertTrue(notices[0].startswith('🧪 testing online now:'))

    def test_start_notice_after_quick_completion(self):
        self.state['phase'] = 'rolled-back'
        self.path.write_text(json.dumps(self.state))
        result = self.run_functions('announce_start\nannounce_start\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len((self.root / 'notices.txt').read_text().splitlines()), 1)

    def test_no_start_notice_before_upload(self):
        for phase in ('prepared', 'old-games', 'failed'):
            with self.subTest(phase=phase):
                self.state.update(phase=phase, halves={'new': {'submission': None}})
                self.path.write_text(json.dumps(self.state))
                result = self.run_functions('attempts=2; network_retries=1\nannounce_start\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((self.root / 'notices.txt').exists())


if __name__ == '__main__':
    unittest.main()
