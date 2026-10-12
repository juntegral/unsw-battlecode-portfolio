"""Offline regression checks for Discord embed length limits."""
import copy
import unittest
from unittest.mock import patch

import meowbot as bot


def embed_size(embed):
    return (len(embed.get('title', '')) + len(embed.get('description', ''))
            + len(embed.get('footer', {}).get('text', ''))
            + len(embed.get('author', {}).get('name', ''))
            + sum(len(f['name']) + len(f['value']) for f in embed.get('fields', [])))


class EmbedLimitTests(unittest.TestCase):
    def assert_limits(self, embed):
        self.assertLessEqual(len(embed.get('title', '')), 256)
        self.assertLessEqual(len(embed.get('description', '')), 4096)
        self.assertLessEqual(len(embed.get('fields', [])), 25)
        self.assertLessEqual(embed_size(embed), 6000)
        for field in embed.get('fields', []):
            self.assertLessEqual(len(field['name']), 256)
            self.assertLessEqual(len(field['value']), 1024)

    def candidate(self, results=None, changes=None):
        return {'version': 'card-29-82407e034c', 'workflow': 2, 'pr': 35,
                'issues': [], 'changes': changes or ['A change'],
                'results': results or {'mechanism': 'm' * 1500}}

    def test_candidate_long_mechanism(self):
        with patch.object(bot, 'gh', side_effect=AssertionError('No network')):
            embed = bot.candidate_embed(self.candidate())
        self.assert_limits(embed)
        mechanism = next(f['value'] for f in embed['fields'] if f['name'] == 'Mechanism check')
        self.assertEqual(len(mechanism), 1024)
        self.assertTrue(mechanism.endswith('…\n[PR](https://github.com/' + bot.REPO + '/pull/35)'))
        self.assertEqual(bot.clamp_embed(embed), embed)

    def test_candidate_total_budget_and_card_pointer(self):
        candidate = self.candidate({k: 'x' * 1500 for k in ('held', 'main', 'mechanism', 'cpu')}, ['x' * 5000])
        candidate.update(issues=[29], pr=None)
        with patch.object(bot, 'card_ref', return_value='#29 Example'):
            embed = bot.candidate_embed(candidate)
        self.assert_limits(embed)
        for field in embed['fields']:
            if '…' in field['value']:
                self.assertTrue(field['value'].endswith('/issues/29)'))

    def test_short_texts_unchanged(self):
        original = {'title': 'Title', 'url': 'https://example.com', 'description': 'Description',
                    'color': 123, 'fields': [{'name': 'Name', 'value': 'Value', 'inline': True}],
                    'footer': {'text': 'Footer'}, 'author': {'name': 'Author'}}
        self.assertEqual(bot.clamp_embed(original), original)
        embed = bot.candidate_embed(self.candidate({'mechanism': 'Short text'}))
        self.assertEqual(next(f['value'] for f in embed['fields'] if f['name'] == 'Mechanism check'), 'Short text')

    def test_all_limits_and_no_input_mutation(self):
        original = {'title': 't' * 500, 'description': 'd' * 5000,
                    'fields': [{'name': 'n' * 300, 'value': 'v' * 1500, 'inline': True} for _ in range(30)],
                    'footer': {'text': 'f' * 3000}, 'author': {'name': 'a' * 300}}
        before = copy.deepcopy(original)
        embed = bot.clamp_embed(original)
        self.assert_limits(embed)
        self.assertEqual(len(embed['fields']), 25)
        self.assertEqual(original, before)
        self.assertTrue(embed['title'].endswith('…'))
        self.assertEqual(bot.clamp_embed(embed), embed)

    def test_exact_boundaries_and_total_only_truncation(self):
        original = {'title': 't' * 256, 'description': 'd' * 4096,
                    'fields': [{'name': 'n' * 256, 'value': 'v' * 1024}]}
        self.assertEqual(bot.clamp_embed(original), original)
        original['fields'].append({'name': 'second', 'value': 'v' * 1024})
        embed = bot.clamp_embed(original)
        self.assert_limits(embed)
        self.assertEqual(embed_size(embed), 6000)
        self.assertTrue(embed['description'].endswith('…'))

    def test_board_batches_are_clamped_and_within_message_budget(self):
        cards = [{'title': 't' * 300, 'description': 'd' * 9000} for _ in range(3)]
        for batch in bot.card_batches(cards):
            self.assertLessEqual(sum(embed_size(card) for card in batch), 6000)
            for card in batch:
                self.assert_limits(card)


if __name__ == '__main__':
    unittest.main()
