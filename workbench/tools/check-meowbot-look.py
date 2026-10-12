#!/usr/bin/env python3
"""Offline look-ping checks; no bot, Discord connection or GitHub calls."""
import asyncio
import contextlib
import datetime
import gzip
import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

import meowbot


class FakeFile:
    def __init__(self, fp, filename):
        self.fp, self.filename, self.closed = fp, filename, False

    def close(self):
        self.closed = True


class FakeChannel:
    def __init__(self, fail=False, fail_files=()):
        self.fail, self.fail_files = fail, set(fail_files)
        self.calls, self.attachments, self.payloads = [], [], []

    async def send(self, content=None, **kwargs):
        assert "files" not in kwargs, "Each replay needs its own message"
        file = kwargs.get("file")
        self.calls.append((content, [file.filename] if file else []))
        if file:
            assert content is None
            assert isinstance(file.fp, io.BytesIO)
            assert not file.fp.closed
            self.attachments.append(file)
            self.payloads.append(file.fp.getvalue())
        if self.fail or (file and file.filename in self.fail_files):
            raise RuntimeError("fake send failure")


class LookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.patch = patch.object(meowbot, "LOOK_DIR", self.temp.name)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.card = Path(self.temp.name) / "card-42"
        self.card.mkdir()
        self.extra = {"status": "needs-look", "issue": {
            "title": "[Idea] Test", "html_url": "https://example.invalid/42",
            "labels": [{"name": "by:zhe"}]}}
        self.discord = types.SimpleNamespace(File=FakeFile)

    def manifest(self, value):
        (self.card / "look.json").write_text(json.dumps(value))

    def replay(self, name, size=1):
        path = self.card / name
        with path.open("wb") as source:
            source.truncate(size)
        return str(path)

    def send(self, channel=None):
        channel = channel or FakeChannel()
        asyncio.run(meowbot.send_state_message(channel, 42, self.extra, self.discord))
        return channel

    def test_missing_manifest_preserves_ping(self):
        self.assertEqual(self.send().calls, [(meowbot.state_message(42, self.extra), [])])

    def test_author_is_named_without_a_tag_at_night(self):
        self.manifest({"replays": [], "note": "x"})
        night = datetime.datetime(2026, 10, 6, 23, tzinfo=datetime.timezone.utc)  # 01:00 CEST
        with patch.object(meowbot, "clock", return_value=night):
            message = self.send().calls[0][0]
        self.assertNotIn("<@", message)
        self.assertTrue(message.startswith("Zhe (asleep there, no ping) "))

    def test_small_attachments_text_first_note_viewer_and_limit(self):
        paths = [self.replay(f"{i}.replay") for i in range(4)]
        Path(paths[0]).write_bytes(b"small replay data")
        self.manifest({"replays": paths, "note": "Check feeding\n at round 20"})
        noon = datetime.datetime(2026, 10, 7, 10, tzinfo=datetime.timezone.utc)  # 12:00 CEST
        with patch.object(meowbot, "clock", return_value=noon):
            channel = self.send()
        message, names = channel.calls[0]
        self.assertEqual(names, [])
        self.assertEqual(channel.calls[1:],
                         [(None, [f"{i}.replay"]) for i in range(3)])
        self.assertEqual(channel.payloads, [b"small replay data", b"\0", b"\0"])
        self.assertIn("<@900000000000000002>", message)
        self.assertEqual(message.splitlines()[1], "reply to this message in your own words, or use /answer card:42 text:…")
        self.assertEqual(message.splitlines()[2], "Check feeding at round 20")
        self.assertIn("https://game.battlecode.au/visualiser", message.splitlines()[3])
        self.assertNotIn("(.gz files:", message)

    def test_large_replay_is_gzipped_with_instructions(self):
        raw = b"x" * (meowbot.LOOK_INLINE_BYTES + 1)
        path = self.replay("big.replay")
        Path(path).write_bytes(raw)
        self.manifest({"replays": [path]})
        channel = self.send()
        self.assertEqual(channel.calls[0][1], [])
        self.assertEqual(channel.calls[1:], [(None, ["big.replay.gz"])])
        self.assertEqual(gzip.decompress(channel.payloads[0]), raw)
        self.assertLessEqual(len(channel.payloads[0]), meowbot.LOOK_INLINE_BYTES)
        self.assertEqual(channel.calls[0][0].splitlines()[-1],
                         "(.gz files: unzip first, then open the .replay)")

    def test_inline_limit_is_sent_without_compression(self):
        path = self.replay("exact.replay", meowbot.LOOK_INLINE_BYTES)
        self.manifest({"replays": [path]})
        channel = self.send()
        self.assertEqual(channel.calls[1:], [(None, ["exact.replay"])])
        self.assertEqual(channel.payloads, [b"\0" * meowbot.LOOK_INLINE_BYTES])
        self.assertNotIn("(.gz files:", channel.calls[0][0])

    def test_skips_oversized_missing_and_invalid_paths(self):
        raw = os.urandom(meowbot.LOOK_INLINE_BYTES + 1)
        self.assertGreater(len(gzip.compress(raw, 9)), meowbot.LOOK_INLINE_BYTES)
        big = self.replay("oversize.replay")
        Path(big).write_bytes(raw)
        paths = [big, "missing.replay", None, "", self.replay("ok.replay"),
                 self.replay("second.replay"), self.replay("third.replay")]
        self.manifest({"replays": paths})
        channel = self.send()
        self.assertEqual(channel.calls[0][1], [])
        self.assertEqual(channel.calls[1:],
                         [(None, [name]) for name in
                          ("ok.replay", "second.replay", "third.replay")])
        self.assertNotIn("(.gz files:", channel.calls[0][0])

    def test_relative_paths_empty_files_and_short_note(self):
        self.replay("relative.replay", 0)
        self.manifest({"replays": ["relative.replay"], "note": "x" * 500})
        channel = self.send()
        self.assertEqual(channel.calls[0][1], [])
        self.assertEqual(channel.calls[1:], [(None, ["relative.replay"])])
        self.assertEqual(channel.payloads, [b""])
        self.assertEqual(len(channel.calls[0][0].splitlines()[2]), 300)
        for replays in ([], None, "relative.replay"):
            self.manifest({"replays": replays})
            self.assertEqual(len(self.send().calls), 1)

    def test_bad_manifest_falls_back(self):
        for value in ("{broken", "[]"):
            (self.card / "look.json").write_text(value)
            self.assertEqual(self.send().calls[0], (meowbot.state_message(42, self.extra), []))

    def test_other_statuses_unchanged(self):
        self.manifest({"replays": [self.replay("ignored.replay")], "note": "ignored"})
        for status in ("needs-info", "tested", "rejected", "inconclusive", "candidate"):
            self.extra["status"] = status
            self.assertEqual(self.send().calls[0], (meowbot.state_message(42, self.extra), []))

    def test_task_state_messages_match_ideas(self):
        for status in ("needs-info", "needs-look", "tested", "rejected", "inconclusive", "candidate"):
            with self.subTest(status=status):
                self.extra["status"] = status
                self.extra["issue"]["title"] = "[Idea] Test"
                expected = self.send().calls
                self.extra["issue"]["title"] = "[tAsK] Test"
                self.assertEqual(self.send().calls, expected)
                if status == "candidate":
                    self.assertEqual(expected, [("#42 Test is a candidate, PR + OK buttons coming", [])])

    def event(self, event_id, title, status, action="labeled"):
        base = dict(self.extra["issue"], number=42, title=title)
        labels = [l for l in base.get("labels", []) if not l["name"].startswith("status:")]
        if action == "labeled":
            labels = labels + [{"name": f"status:{status}"}]
        # GitHub's payload.label is unreliable; the card's own labels carry the state.
        return {"id": str(event_id), "type": "IssuesEvent", "payload": {
            "action": action, "label": {"name": "name:whatever"}, "issue": dict(base, labels=labels)}}

    def test_card_state_events_and_deduplication(self):
        for title in ("[Idea] Test", "[Task] Test", "[tAsK] Test"):
            with self.subTest(title=title):
                statuses = ("needs-info", "needs-look", "tested", "rejected", "inconclusive", "candidate")
                events = [self.event(n, title, status) for n, status in enumerate(statuses, 1)]
                events.append(self.event(7, title, "candidate"))
                state = {"last_event_id": 0}
                with patch.object(meowbot, "gh", return_value=list(reversed(events))):
                    output = meowbot.new_events(state)
                    self.assertEqual([extra["status"] for _, _, extra in output], list(statuses))
                    self.assertEqual([kind for kind, _, _ in output],
                                     ["state", "state", "verdict", "verdict", "verdict", "state"])
                    self.assertTrue(all(n == 42 for _, n, _ in output))
                    self.assertEqual(meowbot.new_events(state), [])
                with patch.object(meowbot, "gh", return_value=[self.event(8, title, "candidate")]):
                    self.assertEqual(meowbot.new_events(state), [])
                events = [self.event(10, title, "candidate"), self.event(9, title, "candidate", "unlabeled")]
                with patch.object(meowbot, "gh", return_value=events):
                    self.assertEqual(len(meowbot.new_events(state)), 1)

    def test_noncard_and_initial_history_do_not_ping(self):
        events = [self.event(1, "Ordinary issue", "candidate"),
                  self.event(2, "[Task] Test", "candidate")]
        with patch.object(meowbot, "gh", return_value=events):
            state = {}
            self.assertEqual(meowbot.new_events(state), [])
            self.assertEqual(state["last_event_id"], 2)
        with patch.object(meowbot, "gh", return_value=events[:1]):
            self.assertEqual(meowbot.new_events({"last_event_id": 0}), [])

    def test_board_and_loop_shared_cards_include_tasks(self):
        issues = [{"number": n, "title": title, "labels": [{"name": f"status:{status}"}],
                   "url": f"https://example.invalid/{n}", "createdAt": "2026-10-04T00:00:00Z"}
                  for n, title, status in ((3, "[Task] Ready", "ready"),
                                           (2, "[Idea] Question", "untested"),
                                           (1, "[tAsK] Build", "in-progress"),
                                           (4, "[Task] Candidate", "candidate"),
                                           (5, "Ordinary issue", "ready"))]
        with patch.object(meowbot, "gh", return_value=issues):
            cards = meowbot.board_state()
            self.assertEqual([(i["n"], i["title"], i["status"]) for i in cards],
                             [(1, "Build", "in-progress"), (2, "Question", "untested"),
                              (3, "Ready", "ready"), (4, "Candidate", "candidate")])
            self.assertEqual([i[0] for i in meowbot.open_ideas()], [1, 2])

    def test_one_file_failure_is_logged_and_others_continue(self):
        paths = [self.replay(name) for name in
                 ("first.replay", "failure.replay", "last.replay")]
        self.manifest({"replays": paths})
        channel = FakeChannel(fail_files={"failure.replay"})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.send(channel)
        self.assertEqual(channel.calls[0][1], [])
        self.assertEqual(channel.calls[1:],
                         [(None, [Path(path).name]) for path in paths])
        self.assertEqual(channel.payloads, [b"\0"] * 3)
        self.assertIn("look replay not sent: failure.replay RuntimeError", output.getvalue())
        self.assertEqual(len(output.getvalue().splitlines()), 1)

    def test_text_send_failure_prevents_attachment_sends(self):
        self.manifest({"replays": [self.replay("failure.replay")]})
        channel = FakeChannel(fail=True)
        with self.assertRaisesRegex(RuntimeError, "fake send failure"):
            self.send(channel)
        self.assertEqual(len(channel.calls), 1)
        self.assertEqual(channel.calls[0][1], [])
        self.assertEqual(channel.attachments, [])


if __name__ == "__main__":
    unittest.main()
