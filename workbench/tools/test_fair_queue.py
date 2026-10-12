"""Offline queue presentation policy checks."""
import tempfile
import unittest
from pathlib import Path
import fair_queue as fair


class FairQueueTests(unittest.TestCase):
    def test_display_order_and_history_unchanged(self):
        cards = [{'n': n, 'created': str(n), 'labels': ['by:' + by]} for n, by in
                 [(1, 'zhe'), (2, 'qwq'), (3, 'junsing'), (4, 'zhe'), (5, 'ai')]]
        history = {'by:zhe': '2026-10-05T00:00:00+00:00', fair.COUNTER: 2}
        self.assertEqual([c['n'] for c in fair.order_cards(cards, history)], [2, 5, 3, 1, 4])
        self.assertEqual(history[fair.COUNTER], 2)

    def test_ai_turn_is_one_slot_and_spent_by_an_ai_lock(self):
        cards = [{'n': n, 'created': str(n), 'labels': ['by:' + by]} for n, by in
                 [(31, 'zhe'), (34, 'junsing'), (23, 'ai'), (30, 'ai')]]
        due = {'by:zhe': '2026-10-05T01:00:00+00:00', 'by:junsing': '2026-10-05T02:00:00+00:00', fair.COUNTER: 3}
        self.assertEqual([c['n'] for c in fair.order_cards(cards, due)], [23, 31, 34, 30])
        spent = fair.lock_taken(due, cards[2])
        self.assertEqual(spent[fair.COUNTER], 0)
        self.assertEqual(due[fair.COUNTER], 3)
        self.assertEqual([c['n'] for c in fair.order_cards(cards, spent)], [31, 34, 23, 30])
        self.assertEqual(fair.lock_taken(due, cards[0]), due)
        self.assertEqual(fair.lock_taken(due, {'n': 8, 'labels': ['by:ai', 'type:task']}), due)

    def test_missing_and_invalid_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fair.json'
            self.assertEqual(fair.read_fair(path), {})
            path.write_text('invalid')
            self.assertEqual(fair.read_fair(path), {})


if __name__ == '__main__':
    unittest.main()
