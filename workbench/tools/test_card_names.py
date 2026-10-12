"""Offline card naming and Discord format regressions."""
import datetime
import json
import subprocess
import unittest
from unittest.mock import patch
import meowbot as bot
import meow_chat as chat
from card_names import unique_slug, valid_slug


class CardNames(unittest.TestCase):
    def setUp(self):
        self.card = {'number': 27, 'title': '[Idea] Keep a safe passage for the queen',
                     'labels': [{'name': 'name:passage'}, {'name': 'by:ai'}],
                     'html_url': 'https://example.invalid/issues/27', 'url': 'https://example.invalid/issues/27',
                     'n': 27, 'wf': '3', 'area': 'terrain', 'status': 'ready'}

    def test_ref_label_fallback_and_lookup(self):
        self.assertEqual(bot.card_ref(self.card), '#27 passage')
        self.assertEqual(bot.card_ref(dict(self.card, labels=[])), '#27 Keep a safe passage')
        with patch.object(bot, 'gh', return_value=self.card) as gh:
            self.assertEqual(bot.card_ref(27), '#27 passage')
            self.assertEqual(gh.call_args.args[0][-1], 'number,title,labels')
        with patch.object(bot, 'gh', side_effect=RuntimeError('offline')):
            self.assertEqual(bot.card_ref(27), '#27')

    def test_slug_collision_limits_and_fallback(self):
        used = set()
        for _ in range(60):
            slug = unique_slug('A dangerouslylongword queen chase', used)
            self.assertTrue(valid_slug(slug), slug)
            self.assertNotIn(slug, used)
            used.add(slug)
        self.assertEqual(unique_slug('女王', {'idea'}), 'idea-a')
        self.assertEqual(unique_slug('anything', suggested='safer-stride'), 'safer-stride')
        for value in ('', 'Too-Long', 'a-b-c', 'x'*17, None):
            self.assertFalse(valid_slug(value))

    def test_label_generation_uses_sonnet_then_fallback(self):
        with patch.object(bot, 'gh', side_effect=[[self.card], [] ,None]) as gh, \
             patch.object(bot, 'claude_json', return_value={'slug': 'passage'}) as ai:
            self.assertEqual(bot.name_label('Safe passage'), 'name:passage-a')
            self.assertIn('claude-sonnet', ai.call_args.args[1])
            self.assertEqual(gh.call_args.args[0][:3], ['label', 'create', 'name:passage-a'])
        with patch.object(bot, 'gh', side_effect=[[], [{'name': 'name:safe-passage'}]]), \
             patch.object(bot, 'claude_json', side_effect=RuntimeError('offline')):
            self.assertEqual(bot.name_label('Safe passage'), 'name:safe-passage')
        with patch.object(bot, 'gh', side_effect=[[self.card], [{'name': 'name:passage'}]]):
            self.assertEqual(bot.name_label('New title', 'passage', exclude=27), 'name:passage')

    def test_new_issue_attaches_name(self):
        with patch.object(bot, 'name_label', return_value='name:passage'), \
             patch.object(bot.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'https://example.invalid/27\n', '')) as run:
            self.assertEqual(bot.create_issue('Safe passage', '**Idea by:** AI (via meowbot).', 'terrain', 3),
                             (27, 'https://example.invalid/27'))
            self.assertIn('name:passage', run.call_args.args[0])

    def test_every_state_and_event_carries_ref(self):
        with patch.object(bot, 'outcome_line', return_value='Observed the passage'):
            for state in ('needs-info', 'needs-look', 'tested', 'kept', 'rejected', 'inconclusive', 'candidate'):
                text = bot.state_message(27, {'issue': self.card, 'status': state})
                self.assertIn('#27 passage', text)
                self.assertNotIn('Keep a safe', text)
        event = {'card': 27, 'name': 'passage', 'title': '#27 passage', 'step': 'outcome',
                 'event': 'start', 'eta_minutes': 42, 'time': '2026-10-04T08:40:00+00:00'}
        self.assertTrue(bot.loop_event_line(event).startswith('⏱ #27 passage: local A/B started, about 42m'))
        self.assertTrue(bot.loop_event_line(dict(event, event='failed', note='offline')).startswith('⚠️ #27 passage:'))
        self.assertIn('#27 passage', bot.ideas_card('Board', [self.card], 0, '')['fields'][0]['name'])
        self.assertEqual(bot.loop_card('Loop', {'issue': 27}, {27: self.card})['fields'][0]['value'], '#27 passage')

    def test_ai_look_notice_is_informational(self):
        url = self.card['html_url']
        text = bot.state_message(27, {'issue': self.card, 'status': 'needs-look'})
        self.assertEqual(text, "#27 passage is built. this is an AI card, so nobody needs to answer; "
                               f"the loop moves on by itself. replays below if you're curious: {url}")
        self.assertNotIn('/answer', text)
        self.assertNotIn('<@', text)
        human = dict(self.card, labels=[{'name': 'name:passage'}, {'name': 'by:zhe'}])
        noon = datetime.datetime(2026, 10, 7, 10, tzinfo=datetime.timezone.utc)  # 12:00 CEST
        with patch.object(bot, 'clock', return_value=noon):
            text = bot.state_message(27, {'issue': human, 'status': 'needs-look'})
        self.assertTrue(text.startswith('<@'))
        self.assertTrue(text.endswith(f'#27 passage is built, can you check 2–3 replays? {url}\n'
                                      'reply to this message in your own words, or use /answer card:27 text:…'))
        asked = bot.state_message(27, {'issue': self.card, 'status': 'needs-info'})
        self.assertIn('reply to this message in your own words, or use /answer card:27 text:…', asked)

    def test_candidate_and_normal_pr_formats(self):
        pr = {'pr': 32, 'url': 'https://example.invalid/pull/32', 'head_sha': 'a'*40}
        with patch.object(bot, 'gh', return_value=self.card):
            candidate = bot.candidate_embed({'version': 'v62', 'issues': [27], 'workflow': 3}, pr)
        self.assertEqual(candidate['title'], '#27 passage')
        self.assertIn('[PR](https://example.invalid/pull/32)', json.dumps(candidate))
        self.assertNotIn('PR #32', json.dumps(candidate))
        self.assertEqual(bot.pr_display({'title': 'Candidate #27', 'body': 'Fixes #27'}, [self.card]), '#27 passage')
        self.assertEqual(bot.pr_display({'title': 'Cleanup #32', 'body': ''}, [self.card]), 'Cleanup #32')
        self.assertEqual(bot.idea_embed(27, self.card['title'], self.card['url'], '', self.card['labels'])['description'].splitlines()[0],
                         'Keep a safe passage for the queen')

    def test_open_merged_closed_prs_link_known_card(self):
        pr = {'number': 32, 'title': 'Candidate #27', 'body': 'Results for #27',
              'url': 'https://example.invalid/pull/32', 'author': {'login': 'teammate'},
              'mergedBy': {'login': 'reviewer'}, 'headRefName': 'candidate', 'baseRefName': 'main',
              'changedFiles': 1, 'additions': 2, 'deletions': 0}
        for action in ('opened', 'merged', 'closed'):
            with patch.object(bot, 'gh', side_effect=[pr, [self.card]]):
                embed = bot.pr_embed(32, action)
            self.assertIn('#27 passage', embed['title'])
            self.assertNotIn('#32', embed['title'])
            self.assertIn('[#27 passage](https://github.com/', embed['description'])
        self.assertIn('[#27 passage]', bot.pr_line(pr, [self.card]))
        self.assertIn('[PR](https://example.invalid/pull/32)', bot.pr_line(pr, [self.card]))

    def test_edit_name_validated_and_applied(self):
        uid = next(iter(bot.MEMBERS))
        with self.assertRaises(ValueError):
            chat.validate_plan({'actions': [{'action': 'board-edit', 'card': 27, 'fields': {'name': 'BAD'}}]}, uid, bot.MEMBERS)
        executor = chat.Actions(bot, {})
        action = {'action': 'board-edit', 'card': 27, 'fields': {'name': 'safer-stride'}}
        record = chat.new_confirmation({'actions': [action]}, uid, 9, bot.MEMBERS)
        record['stage'] = 'executing'
        with patch.object(executor, 'card', return_value={**self.card, 'body': ''}), \
             patch.object(bot, 'name_label', return_value='name:safer-stride'), \
             patch.object(bot, 'gh') as gh, patch.object(bot, 'gh_comment'), patch.object(bot, 'save_state'), \
             patch.object(bot, 'card_ref', return_value='#27 safer-stride'):
            executor.prepare(record)
            result = executor.execute(record['prepared'][0], record)
        edit = gh.call_args.args[0]
        self.assertIn('name:passage', edit)
        self.assertIn('name:safer-stride', edit)
        self.assertIn('#27 safer-stride', result)


if __name__ == '__main__':
    unittest.main()
