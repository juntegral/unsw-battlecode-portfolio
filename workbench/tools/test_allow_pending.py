"""Release pending policy checks using mocked uploads and offline Node helpers."""
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import meowbot


class AllowPendingTests(unittest.TestCase):
    def test_release_upload_allows_pending_with_and_without_force(self):
        candidate = dict(bot_dir='versions/test/bot', version='release-test', changes=['test'])
        for force in (False, True):
            with self.subTest(force=force), patch.object(meowbot, 'UPLOAD_ENABLED', True), patch.object(
                meowbot.subprocess, 'run', return_value=SimpleNamespace(
                    returncode=0, stdout='active: 123 release-test; server zip matches\n', stderr='')) as run:
                self.assertTrue(meowbot.upload(candidate, force=force)['ok'])
                command = run.call_args.args[0]
                self.assertEqual(command.count('--allow-pending'), 1)
                self.assertEqual('--force' in command, force)

    def test_offline_pending_policy(self):
        submit = Path(__file__).with_name('submit.js').resolve()
        script = '''
const { uploadPendingMessage: message } = require(process.argv[1]);
const live = [{id: 12}, {id: 34}];
console.log(JSON.stringify([
  message(live, false, false), message(live, true, false),
  message(live, false, true), message(live, true, true),
  message([], false, false), message([], true, false)
]));
'''
        result = subprocess.run(['node', '-e', script, str(submit)],
                                capture_output=True, text=True, check=True)
        refusal, note, forced, both, empty, empty_allowed = json.loads(result.stdout)
        self.assertEqual(refusal, {'refusal': 'refusing: 2 of our battles are live or pending (12,34); retry later or --force'})
        self.assertEqual(note, {'note': 'note: 2 of our battles are live or pending (12,34); uploading anyway, running matches keep their version'})
        self.assertEqual(both, note)
        self.assertIsNone(forced)
        self.assertIsNone(empty)
        self.assertIsNone(empty_allowed)
