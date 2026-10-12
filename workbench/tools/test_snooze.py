"""Offline snooze checks: GitHub, Discord and model calls are mocked."""
from concurrent.futures import ThreadPoolExecutor
import contextlib
import datetime as dt
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

import decision_nudge as nudge
import meowbot as bot
import meow_chat as core
import snooze

NOW = dt.datetime(2026, 10, 5, 11, tzinfo=snooze.KST)
USER = 900000000000000003
CARD = {'number': 25, 'state': 'open', 'title': '[Idea] Unbox',
        'labels': [{'name': 'name:queen-unbox'}]}
ROW = (90, 25, 'queen-unbox', ('QWQ', USER, 11), 'decision on the results')
OTHER = (70, 26, 'other', ('jun', 900000000000000005, 9), 'replay check')


class IntentTests(unittest.TestCase):
    def test_snooze_languages_and_lengths(self):
        for text, hours in [
            ('25 im taking some time on my decision. ill call you later', 6),
            ('#25 need more time for 3h', 3),
            ('25 아직 생각 중이에요 3시간', 3),
            ('25 还在考虑，稍后再说，3小时', 3),
            ('25 再想想', 6), ('25 still deciding, 12 hours', 12),
            ('25 still thinking until tomorrow', 24), ('25 좀 더 생각할게요 내일', 24),
            ('25 snooze for 72h', 24), ('25 later, for 1.5h', 1.5),
        ]:
            with self.subTest(text=text):
                action = snooze.parse_intent(text)
                self.assertEqual((action['action'], action['card']), ('snooze', 25))
                self.assertEqual(snooze.duration(action['text']), hours)

    def test_resume_and_fallthrough(self):
        for word in ('back', 'done', 'cancel', 'resume', '끝', '취소'):
            self.assertEqual(snooze.parse_intent(f'25 {word}'), {'action': 'unsnooze', 'card': 25})
        for text in ('25 what did the test show?', 'what about 25 later', '25 backbone',
                     '25 done with the test, what next?', '25 do not snooze', '25 snooze?', '0 later'):
            self.assertIsNone(snooze.parse_intent(text))


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'new/snooze.json'

    def test_set_expire_clear(self):
        self.assertEqual(snooze.read_store(self.path), {})
        self.assertFalse(self.path.parent.exists())
        entry = snooze.set_snooze(25, 'QWQ', 'later for 3h', NOW, self.path)
        self.assertEqual(set(entry), {'until', 'by', 'note', 'set'})
        self.assertEqual(dt.datetime.fromisoformat(entry['until']), NOW + dt.timedelta(hours=3))
        self.assertEqual(snooze.read_store(self.path)['25'], entry)
        self.assertIn('25', snooze.active_snoozes(NOW, [25], self.path))
        self.assertEqual(snooze.active_snoozes(NOW + dt.timedelta(hours=3), [25], self.path), {})
        self.assertEqual(snooze.read_store(self.path), {})
        snooze.set_snooze(25, 'QWQ', 'later', NOW, self.path)
        snooze.clear_snooze(25, self.path)
        snooze.clear_snooze(25, self.path)
        self.assertEqual(snooze.read_store(self.path), {})

    def test_atomic_failure_preserves_old_store(self):
        snooze.set_snooze(25, 'QWQ', 'later', NOW, self.path)
        before = self.path.read_bytes()
        with patch.object(snooze.os, 'replace', side_effect=OSError('fake failure')):
            with self.assertRaises(OSError):
                snooze.set_snooze(26, 'QWQ', 'later', NOW, self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual({p.name for p in self.path.parent.iterdir()}, {'snooze.json', 'snooze.json.lock'})

    def test_concurrent_updates_and_no_longer_waiting(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda n: snooze.set_snooze(n, 'QWQ', 'later', NOW, self.path), range(1, 9)))
        self.assertEqual(len(snooze.read_store(self.path)), 8)
        self.assertEqual(set(snooze.active_snoozes(NOW, [1, 2], self.path)), {'1', '2'})
        self.assertEqual(set(snooze.read_store(self.path)), {'1', '2'})

    def test_nudge_filter_and_all_quiet(self):
        snooze.set_snooze(25, 'QWQ', 'later', NOW, self.path)
        rows, quiet = nudge.filter_snoozed(NOW, [ROW, OTHER], path=self.path)
        message = nudge.text(NOW, rows, quiet)
        self.assertEqual(rows, [OTHER])
        self.assertNotIn(f'<@{USER}>', message)
        self.assertIn('<@900000000000000005>', message)
        self.assertTrue(message.endswith('still deciding: #25 queen-unbox (QWQ, quiet until ~17:00 KST)'))
        rows, quiet = nudge.filter_snoozed(NOW, [ROW], path=self.path)
        self.assertIsNone(nudge.text(NOW, rows, quiet))

    def test_nudge_says_a_teammate_can_answer_except_the_candidate_ok(self):
        zhe = ('Zhe', 900000000000000002, 2)
        message = nudge.text(NOW, [(189, 43, 'idle-exit', zhe, nudge.WAITS['status:needs-info']),
                                   (70, 44, 'other', zhe, nudge.WAITS['status:candidate'])])
        self.assertIn("#43 idle-exit has waited 3h 9m for Zhe's answers to the loop's questions, or a teammate's. ", message)
        self.assertIn("#44 other has waited 1h 10m for Zhe's OK on the candidate. ", message)

    def test_dry_prune_and_recent_waiting_card(self):
        snooze.set_snooze(25, 'QWQ', 'later', NOW, self.path)
        nudge.filter_snoozed(NOW, [], waiting_cards={25}, path=self.path)
        self.assertIn('25', snooze.read_store(self.path))
        nudge.filter_snoozed(NOW, [], path=self.path, persist=False)
        self.assertIn('25', snooze.read_store(self.path))
        nudge.filter_snoozed(NOW, [], path=self.path)
        self.assertEqual(snooze.read_store(self.path), {})

    def test_waiting_keeps_recent_card_for_cleanup(self):
        issue = {**CARD, 'updatedAt': NOW.isoformat(),
                 'labels': CARD['labels'] + [{'name': 'by:qwq'}, {'name': 'status:tested'}]}
        pending = set()
        with patch.object(nudge.subprocess, 'run', return_value=SimpleNamespace(stdout=json.dumps([issue]))):
            self.assertEqual(nudge.waiting(NOW, pending), [])
        self.assertEqual(pending, {25})

    def test_mocked_dry_run_does_not_write_or_announce(self):
        snooze.set_snooze(25, 'QWQ', 'later', NOW, self.path)
        def waiting(now, pending):
            pending.update({25, 26})
            return [ROW, OTHER]
        with patch.object(snooze, 'STORE', self.path), patch.object(nudge, 'waiting', side_effect=waiting), \
             patch.object(nudge.datetime, 'datetime', wraps=dt.datetime) as clock, \
             patch.object(nudge.subprocess, 'run') as runner, patch.object(sys, 'argv', ['decision_nudge.py', '--once', '--dry-run']), \
             patch('builtins.open', wraps=open) as opened, contextlib.redirect_stdout(io.StringIO()) as output:
            clock.now.return_value = NOW
            nudge.main()
        self.assertIn('still deciding:', output.getvalue())
        runner.assert_not_called()
        self.assertFalse(any(len(c.args) > 1 and c.args[1] in ('w', 'a') for c in opened.call_args_list))

    def test_all_snoozed_main_skips_message(self):
        snooze.set_snooze(25, 'QWQ', 'later', NOW, self.path)
        def waiting(now, pending):
            pending.add(25)
            return [ROW]
        with patch.object(snooze, 'STORE', self.path), patch.object(nudge, 'waiting', side_effect=waiting), \
             patch.object(nudge.datetime, 'datetime', wraps=dt.datetime) as clock, \
             patch.object(nudge.subprocess, 'run') as runner, patch.object(sys, 'argv', ['decision_nudge.py', '--once', '--dry-run']), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            clock.now.return_value = NOW
            nudge.main()
        runner.assert_not_called()
        self.assertNotIn('decision check', output.getvalue())
        self.assertNotIn('still deciding:', output.getvalue())


class BotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'snooze.json'
        store = patch.object(snooze, 'STORE', self.path)
        store.start()
        self.addCleanup(store.stop)
        schema = patch.dict(core.SCHEMA)
        schema.start()
        self.addCleanup(schema.stop)
        discord = SimpleNamespace(AllowedMentions=SimpleNamespace(none=lambda: None))
        with patch.object(bot.SnoozeMeowUI, 'views'):
            self.ui = bot.SnoozeMeowUI(bot, discord, {}, {}, None, None)
        self.it = SimpleNamespace(user=SimpleNamespace(id=USER),
                                  response=SimpleNamespace(defer=AsyncMock(), send_message=AsyncMock()),
                                  followup=SimpleNamespace(send=AsyncMock()))

    async def test_fast_path_is_visible_read_only_and_skips_model(self):
        with patch.object(bot, 'gh', return_value=CARD) as gh, patch.object(core, 'session_call') as model:
            await self.ui.slash(self.it, '25 im taking some time on my decision. ill call you later')
        gh.assert_called_once_with(['api', f'repos/{bot.REPO}/issues/25'])
        model.assert_not_called()
        self.it.response.defer.assert_awaited_once_with(thinking=True)
        reply = self.it.followup.send.call_args.args[0]
        self.assertIn('⏸ #25 queen-unbox: QWQ', reply)
        self.assertNotIn('\n', reply)
        self.assertIn('25', snooze.read_store(self.path))
        with patch.object(bot, 'gh', return_value=CARD):
            await self.ui.slash(self.it, '25 back')
        self.assertEqual(self.it.followup.send.call_args.args[0],
                         '▶ #25 queen-unbox: QWQ resumed decision checks for this card.')
        self.assertEqual(snooze.read_store(self.path), {})

    async def test_fallthrough_is_unchanged(self):
        with patch.object(bot.MeowUI, 'slash', new_callable=AsyncMock) as old:
            await self.ui.slash(self.it, '25 what did the test show?')
        old.assert_awaited_once_with(self.it, '25 what did the test show?')
        self.assertFalse(self.path.exists())

    def test_exact_example_replies(self):
        with patch.object(bot, 'gh', return_value=CARD), \
             patch.object(snooze.dt, 'datetime', wraps=dt.datetime) as clock:
            clock.now.return_value = NOW
            self.assertEqual(bot.snooze_action(snooze.parse_intent('25 still deciding'), USER),
                             '⏸ #25 queen-unbox: QWQ is taking more time on the decision. '
                             'decision checks stay quiet for this card until ~17:00 KST / 10:00 CEST / 19:00 AEDT. "/meow 25 back" ends it early')
            self.assertEqual(bot.snooze_action(snooze.parse_intent('#25 need more time for 3h'), USER),
                             '⏸ #25 queen-unbox: QWQ is taking more time on the decision. '
                             'decision checks stay quiet for this card until ~14:00 KST / 07:00 CEST / 16:00 AEDT. "/meow 25 back" ends it early')
            self.assertEqual(bot.snooze_action(snooze.parse_intent('25 back'), USER),
                             '▶ #25 queen-unbox: QWQ resumed decision checks for this card.')

    async def test_nonmember_and_missing_closed_or_noncard(self):
        self.it.user.id = 999
        with patch.object(bot, 'gh') as gh:
            await self.ui.slash(self.it, '25 later')
        gh.assert_not_called()
        self.it.response.send_message.assert_awaited_once()
        self.it.user.id = USER
        for issue in (None, dict(CARD, state='closed'), dict(CARD, pull_request={}), dict(CARD, title='Other issue')):
            with patch.object(bot, 'gh', return_value=issue):
                await self.ui.slash(self.it, '25 later')
            self.assertIn('was not found', self.it.followup.send.call_args.args[0])
            self.assertFalse(self.path.exists())
        with patch.object(bot, 'gh', side_effect=RuntimeError('HTTP 404')):
            await self.ui.slash(self.it, '25 back')
        self.assertEqual(self.it.followup.send.call_args.args[0], 'Card #25 was not found.')

    async def test_model_actions_skip_confirmation_and_preserve_other_actions(self):
        thread = SimpleNamespace(send=AsyncMock())
        plan = {'actions': [{'action': 'snooze', 'card': 25, 'text': 'need more time for 3h'},
                            {'action': 'comment', 'card': 25, 'text': 'test'}]}
        with patch.object(bot, 'gh', return_value=CARD) as gh, \
             patch.object(bot.MeowUI, 'offer', new_callable=AsyncMock) as old:
            await self.ui.offer(thread, USER, plan)
            self.assertEqual([a['action'] for a in old.call_args.args[2]['actions']], ['comment'])
            old.reset_mock()
            await self.ui.offer(thread, USER, {'actions': [{'action': 'unsnooze', 'card': 25}]})
            old.assert_not_awaited()
        self.assertTrue(all(c.args[0] == ['api', f'repos/{bot.REPO}/issues/25'] for c in gh.call_args_list))
        self.assertEqual(snooze.read_store(self.path), {})


if __name__ == '__main__':
    unittest.main()
