"""Late notifications and all status surfaces, with no external calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import meowbot as bot
import meow_chat


class LateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.event = {'event': 'late', 'card': 31, 'name': 'queen-hunt', 'title': 'Queen hunt',
                      'step': 'build', 'elapsed_minutes': 45, 'planned_minutes': 27,
                      'reason': 'still editing and re-checking that it plays the same when off',
                      'new_eta_at': '2026-10-04T14:10:00+00:00', 'eta_known': True, 'level': 1}
        p = patch('meow_chat.bot_versions', return_value='## Bot versions on the server\nOffline fixture.')
        p.start()
        self.addCleanup(p.stop)
        for target in ('subprocess.run', 'subprocess.Popen', 'urllib.request.urlopen'):
            p = patch(target, side_effect=AssertionError('Unexpected external call'))
            p.start()
            self.addCleanup(p.stop)

    def test_running_message(self):
        message = bot.loop_event_line(self.event)
        self.assertEqual(message, "⏳ #31 queen-hunt: building is running late: 45m so far, planned 27m. "
                         "it's still working: still editing and re-checking that it plays the same when off. "
                         "should be done ~23:10 KST / 16:10 CEST / 01:10 AEDT.")
        self.assertNotIn('@', message)

    def test_waiting_start_time_and_unknown(self):
        event = dict(self.event, waiting=True, queue='batch lock', elapsed_minutes=18,
                     new_start_at='2026-10-04T14:17:00+00:00')
        message = bot.loop_event_line(event)
        self.assertIn('waiting 18m for the game slot', message)
        self.assertIn('should start ~23:17 KST / 16:17 CEST / 01:17 AEDT', message)
        self.assertIn("no estimate yet, i'll post again in 15 min", bot.loop_event_line(dict(event, eta_known=False)))
        message = bot.loop_event_line(dict(event, reason='@everyone <@123> ' + 'x' * 600))
        self.assertNotIn('@everyone', message)
        self.assertNotIn('<@123>', message)
        self.assertLess(len(message), 550)

    def test_ladder_with_two_waiters_and_batch(self):
        event = dict(self.event, card=0, title='Ladder review', step='ladder', name='',
                     elapsed_minutes=22, planned_minutes=17,
                     reason='Comparing how exposed our queen is vs theirs…',
                     waiters=[{'card': 27, 'name': 'passage'}, {'card': 30, 'name': 'big-map-trades'}])
        message = bot.loop_event_line(event)
        self.assertIn('the ladder review (AI reading our new ladder games) is running late: 22m', message)
        self.assertIn('comparing how exposed our queen is vs theirs.', message)
        self.assertTrue(message.endswith('waiting behind it: #27 passage, #30 big-map-trades'))
        self.assertNotIn('#0', message)
        self.assertNotIn('…', message)
        batch = bot.loop_event_line(dict(self.event, step='outcome', reason='games are taking longer than planned'))
        self.assertIn('games are taking longer than planned', batch)

    def test_unknown_once_and_legacy_tool_counts(self):
        event = dict(self.event, eta_known=False, reason='game progress unavailable; unknown, checking again in 15 min')
        message = bot.loop_event_line(event)
        self.assertEqual(message.count("no estimate yet, i'll post again in 15 min"), 1)
        self.assertNotIn('unknown', message)
        legacy = bot.loop_event_line(dict(self.event, reason="still working: 59 tool calls (28 reads); last: 'Compare queen exposure…'"))
        self.assertNotIn('tool calls', legacy)
        self.assertIn('compare queen exposure.', legacy)
        self.assertIsNone(bot.loop_event_line(dict(self.event, covered_by=['holder'])))

    def test_group_waiters_before_holder_and_from_status(self):
        holder = dict(self.event, job='ladder-job', card=0, step='ladder', name='')
        waiter = dict(self.event, card=27, name='passage', waiting=True,
                      holders=[{'job': 'ladder-job'}], queue='ai lock')
        path = self.root / 'events.jsonl'
        path.write_text(''.join(json.dumps(e) + '\n' for e in (waiter, holder)))
        (self.root / 'status.json').write_text(json.dumps({'cards': {'30': {
            'name': 'big-map-trades', 'queue': 'batch lock', 'holders': [{'job': 'ladder-job'}]}}}))
        with patch.object(bot, 'LOOK_DIR', str(self.root)):
            rows = bot.tail_loop_events({'loop_events_offset': 0}, path)
        self.assertIsNone(rows[0][1])
        self.assertEqual(sum(bool(m) for _, m in rows), 1)
        self.assertIn('#27 passage', rows[1][1])
        self.assertIn('#30 big-map-trades', rows[1][1])

    def test_waiter_covered_by_previously_reported_holder(self):
        path = self.root / 'events.jsonl'
        event = dict(self.event, waiting=True, queue='ai lock', holders=[{'job': 'ladder-job'}])
        path.write_text(json.dumps(event) + '\n')
        (self.root / 'status.json').write_text(json.dumps({'cards': {'0': {
            'late': True, 'queue': None, 'job': 'ladder-job'}}}))
        with patch.object(bot, 'LOOK_DIR', str(self.root)):
            rows = bot.tail_loop_events({'loop_events_offset': 0}, path)
        self.assertEqual(rows, [(path.stat().st_size, None)])

    def test_lone_waiter_and_latest_notice_per_cause(self):
        waiter = dict(self.event, waiting=True, queue='ai lock', elapsed_minutes=18,
                      reason='waiting for #9 pool-check', new_start_at='2026-10-04T14:17:00+00:00')
        message = bot.loop_event_line(waiter)
        self.assertEqual(message, '⏳ #31 queen-hunt: waiting 18m for the AI slot. '
                         'waiting for #9 pool-check. should start ~23:17 KST / 16:17 CEST / 01:17 AEDT.')
        path = self.root / 'events.jsonl'
        path.write_text(''.join(json.dumps(e) + '\n' for e in (self.event, dict(self.event, level=2))))
        with patch.object(bot, 'LOOK_DIR', str(self.root)):
            rows = bot.tail_loop_events({'loop_events_offset': 0}, path)
        self.assertIsNone(rows[0][1])
        self.assertEqual(sum(bool(m) for _, m in rows), 1)

    def test_one_event_one_message(self):
        path = self.root / 'events.jsonl'
        path.write_text(json.dumps(self.event) + '\n')
        state = {'loop_events_offset': 0}
        rows = bot.tail_loop_events(state, path)
        self.assertEqual(len([m for _, m in rows if m]), 1)
        state['loop_events_offset'] = rows[-1][0]
        self.assertEqual(bot.tail_loop_events(state, path), [])

    def test_post_false_is_skipped_and_legacy_is_unchanged(self):
        self.assertIsNone(bot.loop_event_line(dict(self.event, post=False)))
        self.assertEqual(bot.loop_event_line(dict(self.event, post=True)),
                         bot.loop_event_line(self.event))
        for minute in (30, 60, 119):
            self.assertIsNone(bot.loop_event_line(dict(self.event, waiting=True,
                                                       elapsed_minutes=minute, post=False)))
        for minute in (120, 240):
            self.assertIn('waiting', bot.loop_event_line(dict(self.event, waiting=True,
                              elapsed_minutes=minute, post=True, covered_by=['holder'])))

    def test_suppressed_update_does_not_hide_due_notice(self):
        path = self.root / 'events.jsonl'
        holder = dict(self.event, post=True, job='holder')
        hidden = dict(holder, post=False, level=2)
        waiter = dict(self.event, waiting=True, post=False, card=30, name='passage',
                      holders=[{'job': 'holder'}])
        path.write_text(''.join(json.dumps(e) + '\n' for e in (holder, hidden, waiter)))
        with patch.object(bot, 'LOOK_DIR', str(self.root)):
            rows = bot.tail_loop_events({'loop_events_offset': 0}, path)
        self.assertIn('waiting behind it: #30 passage', rows[0][1])
        self.assertEqual([message for _, message in rows[1:]], [None, None])

    def test_loop_status_and_brain(self):
        info = {**self.event, 'late': True, 'step': 'build running', 'step_kind': 'build',
                'step_started': '2026-10-04T13:00:00+00:00', 'eta_at': self.event['new_eta_at']}
        (self.root / 'status.json').write_text(json.dumps({'cards': {'31': info}}))
        with patch.object(bot, 'LOOK_DIR', str(self.root)), patch.object(bot, 'gh', return_value=[]):
            loops, _ = bot.loop_status()
            loop = next(iter(loops.values()))
            text = bot.loop_eta(loop)
            embed = bot.loop_card('card loop', loop, {})
            brain = meow_chat.build_brain(bot, root=self.root, team=self.root, memory=self.root, look=self.root)
            for rendered in (text, embed['fields'][1]['value'], brain):
                self.assertIn('⏳ late', rendered)
                self.assertIn(self.event['reason'], rendered)
                self.assertIn('should be done ~23:10 KST / 16:10 CEST / 01:10 AEDT', rendered)


if __name__ == '__main__':
    unittest.main()
