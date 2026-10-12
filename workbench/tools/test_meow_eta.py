"""Offline checks for loop event notifications and ETA visibility."""
import datetime
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import meowbot as bot
import meow_chat


class MeowEtaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / 'events.jsonl'
        self.start = {'time': '2026-10-04T08:40:00+00:00', 'card': 17, 'title': 'Test',
                      'step': 'outcome', 'event': 'start', 'eta_minutes': 150, 'note': ''}

    def tearDown(self):
        self.temp.cleanup()

    def append(self, event):
        with self.path.open('a') as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + '\n')

    def test_first_poll_skips_history_then_consumes_byte_offsets(self):
        self.append(self.start)
        state = {}
        self.assertEqual(bot.tail_loop_events(state, self.path), [])
        first = state['loop_events_offset']
        self.append(dict(self.start, event='done'))
        self.append(dict(self.start, event='failed', note='fake error'))
        rows = bot.tail_loop_events(state, self.path)
        self.assertEqual(len(rows), 2)
        self.assertIsNone(rows[0][1])
        self.assertIn('failed: fake error', rows[1][1])
        self.assertGreater(rows[1][0], first)
        state['loop_events_offset'] = rows[-1][0]
        self.assertEqual(bot.tail_loop_events(state, self.path), [])
        self.assertEqual(state['loop_events_offset'], self.path.stat().st_size)

    def test_partial_invalid_and_rotated_file(self):
        state = {'loop_events_offset': 0}
        data = json.dumps(self.start, ensure_ascii=False).encode()
        self.path.write_bytes(b'invalid\n' + data[:20])
        rows = bot.tail_loop_events(state, self.path)
        self.assertEqual(rows, [(8, None)])
        state['loop_events_offset'] = 8
        with self.path.open('ab') as stream:
            stream.write(data[20:] + b'\n')
        rows = bot.tail_loop_events(state, self.path)
        self.assertIn('local A/B started', rows[0][1])
        state['loop_events_offset'] = rows[0][0]
        self.path.write_bytes(b'{}\n')
        self.assertEqual(bot.tail_loop_events(state, self.path), [(3, None)])

    def test_start_threshold_and_dual_timezones(self):
        self.assertEqual(bot.loop_event_line(self.start),
                         '⏱ #17 Test: local A/B started, about 2h 30m (done ~20:10 KST / 13:10 CEST / 22:10 AEDT)')
        self.assertIsNone(bot.loop_event_line(dict(self.start, eta_minutes=9)))
        self.assertIsNone(bot.loop_event_line(dict(self.start, event='done')))
        self.assertIn('about 10m', bot.loop_event_line(dict(self.start, eta_minutes=10, step='task')))
        self.assertIn('CET', bot.eta_clock('2026-12-04T08:40:00+00:00'))
        failure = bot.loop_event_line(dict(self.start, event='failed', note='long\nerror ' * 100))
        self.assertNotIn('\n', failure)
        self.assertLess(len(failure), 300)

    def test_running_status_and_brain(self):
        info = {'state': 'testing', 'step': 'outcome running', 'step_kind': 'outcome',
                'step_started': self.start['time'], 'eta_minutes': 150,
                'eta_at': '2026-10-04T11:10:00+00:00', 'queue': None, 'wait_minutes': 0}
        (self.root / 'status.json').write_text(json.dumps({'cards': {'17': info}}))
        now = datetime.datetime.fromisoformat('2026-10-04T08:55:00+00:00')
        self.assertIn('15m elapsed', bot.loop_eta(info, now))
        with patch.object(bot, 'LOOK_DIR', str(self.root)), patch.object(bot, 'gh', return_value=[]), \
                patch.object(meow_chat.subprocess, 'run', return_value=type('Result', (), {'stdout': '[]'})()):
            loops, url = bot.loop_status()
            self.assertEqual(loops['card #17']['issue'], 17)
            card = bot.loop_card('card #17', loops['card #17'], {})
            self.assertIn('ETA 20:10 KST / 13:10 CEST / 22:10 AEDT', card['fields'][1]['value'])
            brain = meow_chat.build_brain(bot, root=self.root, team=self.root, memory=self.root, look=self.root)
            for field in ('step_started', 'eta_minutes', 'eta_at', 'queue'):
                self.assertIn(field, brain)
            self.assertIn('ETA 20:10 KST / 13:10 CEST / 22:10 AEDT', brain)

    def test_missing_file_and_waiting_display(self):
        state = {}
        self.assertEqual(bot.tail_loop_events(state, self.path), [])
        self.append(self.start)
        self.assertEqual(len(bot.tail_loop_events(state, self.path)), 1)
        text = bot.loop_eta({'step_kind': 'build', 'step_started': None, 'queue': 'ai lock',
                             'wait_minutes': 12, 'eta_at': self.start['time']})
        self.assertIn('building · waiting on ai lock (~12m wait)', text)


if __name__ == '__main__':
    unittest.main()
