#!/usr/bin/env python3
"""Offline announcement checks; all credentials and REST calls are fake."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import meowbot


class AnnounceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "data/discord").mkdir(parents=True)
        (self.root / "data/discord/channel.txt").write_text("123456\n")
        (self.root / "docs").mkdir()
        (self.root / "docs/discord.txt").write_text("bOt fake-token\nignored-line\n")
        self.file = self.root / "announcement.txt"
        self.text = "공지 🐱\nsecond line\n"
        self.file.write_text(self.text, encoding="utf-8")
        root_patch = patch.object(meowbot, "ROOT", str(self.root))
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def test_request_shape(self):
        response = MagicMock()
        with patch.object(meowbot, "urlopen", return_value=response) as send:
            meowbot.announce_file(self.file)
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://discord.com/api/v10/channels/123456/messages")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bot fake-token")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"content": self.text})
        self.assertEqual(send.call_args.kwargs, {"timeout": 30})
        response.__enter__.return_value.read.assert_called_once_with()

    def test_cli_dry_run_never_reads_token_or_starts_bot(self):
        output = io.StringIO()
        with patch.object(meowbot, "bot_token", side_effect=AssertionError("token read")), \
                patch.object(meowbot, "urlopen", side_effect=AssertionError("network")), \
                patch.object(meowbot, "run_bot", side_effect=AssertionError("gateway")), \
                patch("sys.argv", ["meowbot.py", "--announce-file", str(self.file), "--dry-run"]), \
                contextlib.redirect_stdout(output):
            meowbot.main()
        self.assertEqual(output.getvalue(), "123456\n" + self.text)

    def test_length_and_empty_validation(self):
        with patch.object(meowbot, "urlopen", side_effect=AssertionError("network")):
            for text in ("x" * 2001, "", " \n"):
                self.file.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    meowbot.announce_file(self.file, dry_run=True)
            self.file.write_text("x" * 2000, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                meowbot.announce_file(self.file, dry_run=True)

    def test_cli_error_does_not_print_exception_secrets(self):
        output = io.StringIO()
        with patch.object(meowbot, "announce_file", side_effect=RuntimeError("fake-token")), \
                patch("sys.argv", ["meowbot.py", "--announce-file", str(self.file), "--dry-run"]), \
                contextlib.redirect_stderr(output):
            with self.assertRaises(SystemExit) as result:
                meowbot.main()
        self.assertEqual(result.exception.code, 1)
        self.assertNotIn("fake-token", output.getvalue())


if __name__ == "__main__":
    unittest.main()
