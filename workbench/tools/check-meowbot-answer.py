#!/usr/bin/env python3
"""Offline answer checks; all Discord interactions and GitHub calls are fake."""
import types
import unittest
from unittest.mock import AsyncMock, patch

import meowbot


class AnswerTests(unittest.IsolatedAsyncioTestCase):
    def interaction(self, uid=900000000000000002):
        return types.SimpleNamespace(user=types.SimpleNamespace(id=uid),
                                     response=types.SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock()),
                                     followup=types.SimpleNamespace(send=AsyncMock()),
                                     channel=types.SimpleNamespace(send=AsyncMock()))

    async def test_members_titles_and_original_text(self):
        text = "그대로 보존해요 / 原文不翻译 / keep `code`\nsecond line $(literal)"
        url = "https://github.com/forrest-gan2005/battlecode/issues/42#issuecomment-123"
        for uid, name in meowbot.MEMBERS.items():
            for title in ("[Idea] Question", "[Task] Question", "[tAsK] Question"):
                with self.subTest(member=name, title=title):
                    it = self.interaction(uid)
                    with patch.object(meowbot, "gh", side_effect=[{"state": "open", "title": title},
                                                                 {"html_url": url}]) as gh, \
                            patch.object(meowbot, "translate", side_effect=AssertionError("translation")):
                        await meowbot.answer_card(it, 42, text)
                    self.assertEqual(gh.call_args_list[0].args[0],
                                     ["api", f"repos/{meowbot.REPO}/issues/42"])
                    self.assertEqual(gh.call_args_list[1].args[0],
                                     ["api", f"repos/{meowbot.REPO}/issues/42/comments", "--method", "POST",
                                      "-f", f"body=Answer from {name}: {text}"])
                    it.response.defer.assert_awaited_once_with(ephemeral=True, thinking=True)
                    it.channel.send.assert_awaited_once_with(f"💬 {name} answered #42 Question: {text}\n{url}")
                    it.followup.send.assert_awaited_once_with("posted, everyone can see it above", ephemeral=True)

    async def test_nonmember_never_calls_github(self):
        it = self.interaction(0)
        with patch.object(meowbot, "gh", side_effect=AssertionError("GitHub")) as gh:
            await meowbot.answer_card(it, 42, "answer")
        gh.assert_not_called()
        it.response.send_message.assert_awaited_once_with(
            "Only team members can use meowbot commands.", ephemeral=True)
        it.response.defer.assert_not_awaited()
        it.followup.send.assert_not_awaited()

    async def test_closed_noncard_and_pr_refused_without_comment(self):
        cases = [({"state": "closed", "title": "[Idea] Closed"}, "#42 Closed is not open."),
                 ({"state": "closed", "title": "[Task] Closed"}, "#42 Closed is not open."),
                 ({"state": "open", "title": "Other issue"}, "#42 Other issue is not an [Idea]/[Task] card."),
                 ({"state": "open", "title": "[Idea] PR", "pull_request": {}},
                  "#42 PR is not an [Idea]/[Task] card.")]
        for issue, message in cases:
            with self.subTest(issue=issue):
                it = self.interaction()
                with patch.object(meowbot, "gh", return_value=issue) as gh:
                    await meowbot.answer_card(it, 42, "answer")
                gh.assert_called_once_with(["api", f"repos/{meowbot.REPO}/issues/42"])
                it.followup.send.assert_awaited_once_with(message, ephemeral=True)

    async def test_lookup_and_post_failures_are_ephemeral(self):
        for responses in ([RuntimeError("fake failure")],
                          [{"state": "open", "title": "[Task] Question"}, RuntimeError("fake failure")]):
            with self.subTest(responses=responses):
                it = self.interaction()
                with patch.object(meowbot, "gh", side_effect=responses) as gh:
                    await meowbot.answer_card(it, 42, "answer")
                self.assertEqual(gh.call_count, len(responses))
                it.followup.send.assert_awaited_once_with("Could not post an answer to #42" + (" Question" if len(responses) == 2 else "") + ".", ephemeral=True)


if __name__ == "__main__":
    unittest.main()
