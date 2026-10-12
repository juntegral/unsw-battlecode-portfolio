"""Server version context, using only temporary files and stubbed processes."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import meow_chat


SUBMISSIONS = [
    dict(version=22, id=17594, name='card-25-ff0327008d', status='active',
         description='Current main', uploadedAt='2026-10-05T09:00:00Z'),
    dict(version=26, id=17648, name='qh31d-test', status='idle',
         description='Queen hunt test', uploadedAt='2026-10-05T10:49:00Z'),
]
PAIR = dict(kind='pair', ref='#31 queen-hunt (on new main)',
            opponents=[dict(name='test4'), dict(name='WeHaveQuizzes')],
            halves={'new': {'submission': {'id': 17648}}})


class BotVersionsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.smoke = self.root / 'data/online/smoke'
        self.smoke.mkdir(parents=True)
        self.state = self.smoke / 'qh31d-test.json'
        self.state.write_text(json.dumps(PAIR))
        self.result = self.smoke / 'qh31d-test-result.txt'
        self.result.write_text('Fixture result: mechanism observed\nNever include second line\n')
        self.runner = patch.object(meow_chat.subprocess, 'run',
                                   return_value=SimpleNamespace(stdout=json.dumps(SUBMISSIONS)))
        self.run = self.runner.start()
        self.addCleanup(self.runner.stop)

    def section(self):
        return meow_chat.bot_versions(self.root)

    def test_matching_label_and_first_result_line(self):
        section = self.section()
        self.assertIn('v26 · 17648 · qh31d-test · idle · Queen hunt test', section)
        self.assertIn('tested: #31 queen-hunt (on new main) · vs test4 + WeHaveQuizzes', section)
        self.assertIn('Fixture result: mechanism observed', section)
        self.assertNotIn('Never include second line', section)
        self.assertLess(section.index('v26 ·'), section.index('v22 ·'))
        self.run.assert_called_once_with(
            ['node', 'tools/subs.js', 'list', '--json', '--last', '15'], cwd=self.root,
            capture_output=True, text=True, timeout=10, check=True)

    def test_no_label_and_live_control(self):
        line = next(line for line in self.section().splitlines() if line.startswith('v22 ·'))
        self.assertEqual(line, 'v22 · 17594 · card-25-ff0327008d · active · LIVE · Current main')
        self.assertIn('Control: v22 (active submission 17594); card tests are v22 main + <card>.', self.section())

    def test_missing_ref_and_result(self):
        self.state.write_text(json.dumps({k: v for k, v in PAIR.items() if k != 'ref'}))
        self.result.unlink()
        self.assertIn('tested: qh31d-test · vs test4 + WeHaveQuizzes', self.section())

    def test_wrong_submission_and_non_pair_do_not_match(self):
        for state in (dict(PAIR, halves={'new': {'submission': {'id': 1}}}), dict(PAIR, kind='baseline')):
            with self.subTest(state=state):
                self.state.write_text(json.dumps(state))
                self.assertNotIn('tested:', self.section())

    def test_failure_keeps_section_and_replaces_timestamp(self):
        path = self.root / 'data/meow/brain.md'
        path.parent.mkdir()
        original = self.section()
        path.write_text('# Brain\n' + original + '\n(could not refresh at 01:02)\n\n## Next\nOther context')
        instant = dt.datetime(2026, 10, 5, 21, 34)
        for error in (subprocess.CalledProcessError(1, ['node']),
                      subprocess.TimeoutExpired(['node'], 10), OSError('No node')):
            with self.subTest(error=error), patch.object(meow_chat.dt, 'datetime') as clock:
                clock.now.return_value = instant
                self.run.side_effect = error
                self.assertEqual(self.section(), original + '\n(could not refresh at 21:34)')

    def test_failure_without_previous_and_bad_json(self):
        self.run.return_value.stdout = 'invalid json'
        self.assertIn('Server versions unavailable.\n(could not refresh at ', self.section())

    def test_size_cap_cuts_oldest_and_retains_control(self):
        rows = [dict(version=n, id=n, name=f'bot-{n}', status='active' if n == 1 else 'idle',
                     description='긴 설명 ' * 100, uploadedAt=f'2026-10-{n:02d}T00:00:00Z')
                for n in range(1, 16)]
        self.run.return_value.stdout = json.dumps(rows)
        section = self.section()
        self.assertLess(len(section), 2500)
        self.assertIn('v15 ·', section)
        self.assertNotIn('v1 ·', section)
        self.assertIn('Control: v1 (active submission 1)', section)
        self.assertTrue(section.splitlines()[-2].endswith('긴 설명'))

    def test_full_brain_refresh_and_failure_fallback(self):
        api = SimpleNamespace(LOOK_DIR=self.root, REPO='fixture', gh=lambda _: [])
        brain = meow_chat.build_brain(api, root=self.root, team=self.root, memory=self.root)
        self.assertIn(self.section(), brain)
        self.run.side_effect = subprocess.TimeoutExpired(['node'], 10)
        brain = meow_chat.build_brain(api, root=self.root, team=self.root, memory=self.root)
        self.assertIn('v26 · 17648', brain)
        self.assertIn('(could not refresh at ', brain)
        self.assertEqual(brain, (self.root / 'data/meow/brain.md').read_text())


if __name__ == '__main__':
    unittest.main()
