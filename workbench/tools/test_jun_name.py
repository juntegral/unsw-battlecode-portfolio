"""Offline display-name and legacy member-input compatibility checks."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import meowbot as bot
import meow_chat as chat
import decision_nudge as nudge
import pair_report
import smoke
import snooze
import tasks

ALIASES = ('jun', 'Jun', 'junsing', 'juntegral', '준싱')
UID = 900000000000000005
NOW = dt.datetime(2026, 10, 5, 21, 27, tzinfo=bot.KST)


class JunNameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for target in ('subprocess.run', 'subprocess.Popen', 'urllib.request.urlopen'):
            p = patch(target, side_effect=AssertionError('Unexpected external call'))
            p.start()
            self.addCleanup(p.stop)

    def test_aliases_and_github_label(self):
        self.assertEqual(bot.MEMBERS[UID], 'jun')
        self.assertEqual(bot.AUTHOR_LABELS['jun'], 'by:junsing')
        self.assertEqual(bot.author_name('by:junsing'), 'jun')
        self.assertEqual(nudge.PEOPLE['by:junsing'][0], 'jun')
        for alias in ALIASES:
            with self.subTest(alias=alias):
                self.assertEqual(bot.author_label(alias), 'by:junsing')
                self.assertEqual(bot.body_author(f'**Idea by:** {alias} (via meowbot).'), 'by:junsing')
                self.assertTrue(bot.card_body(alias, {}).startswith('**Idea by:** jun '))

    def test_idea_by_plan_normalizes_without_mutating_input(self):
        for alias in ALIASES:
            fields = {'title': 'Fixture', 'idea_by': alias}
            plan = {'actions': [{'action': 'hypo', 'fields': fields}]}
            clean = chat.validate_plan(plan, UID, bot.MEMBERS)
            self.assertEqual(clean['actions'][0]['fields']['idea_by'], 'jun')
            self.assertEqual(fields['idea_by'], alias)
        with self.assertRaises(ValueError):
            chat.validate_plan({'actions': [{'action': 'hypo', 'fields':
                                            {'title': 'Fixture', 'idea_by': 'stranger'}}]}, UID, bot.MEMBERS)

    def test_task_aliases_and_legacy_caller(self):
        data = {'people': {n: {'todo': [], 'yours': [], 'parked': []} for n in tasks.NAMES},
                'anyone': [], 'now': NOW.isoformat()}
        for alias in ALIASES:
            self.assertIn('**jun** · 0 waiting\nnothing waiting', tasks.render(data, who=alias))
            self.assertIn('**jun** · 0 waiting', tasks.render(data, who='me', caller=alias))
        with patch('sys.argv', ['meowbot.py', '--preview-tasks', '--who', '준싱']), \
                patch.object(tasks, 'collect', return_value=data), patch('builtins.print') as printed:
            bot.main()
        self.assertIn('**jun**', printed.call_args.args[0])

    def test_old_state_read_and_canonical_write_preserve_paths_and_labels(self):
        path = self.root / 'state.json'
        old = {'candidates': {'fixture': {'by': '준싱', 'author_labels': ['by:junsing']}},
               'meow': {'plan': {'fields': {'idea_by': 'juntegral'}}}, 'file': '준싱.md'}
        path.write_text(json.dumps(old))
        with patch.object(bot, 'STATE', str(path)):
            state = bot.load_state()
            self.assertEqual(state['candidates']['fixture']['by'], 'jun')
            self.assertEqual(state['meow']['plan']['fields']['idea_by'], 'jun')
            bot.save_state(old)
        saved = json.loads(path.read_text())
        self.assertEqual(saved['candidates']['fixture']['by'], 'jun')
        self.assertEqual(saved['candidates']['fixture']['author_labels'], ['by:junsing'])
        self.assertEqual(saved['file'], '준싱.md')

    def test_old_snooze_read_and_new_write(self):
        path = self.root / 'snooze.json'
        path.write_text(json.dumps({'25': {'by': '준싱', 'until': (NOW + dt.timedelta(hours=2)).isoformat()}}))
        self.assertEqual(snooze.active_snoozes(NOW, [25], path=path, persist=False)['25']['by'], 'jun')
        for alias in ALIASES:
            self.assertEqual(snooze.set_snooze(26, alias, 'later', NOW, path)['by'], 'jun')
            saved = json.loads(path.read_text())
            self.assertEqual(saved['25']['by'], 'jun')
            self.assertEqual(saved['26']['by'], 'jun')

    def test_decision_fixture_with_old_names(self):
        row = (90, 25, 'queen-unbox', ('준싱', UID, 9), 'decision on the results')
        quiet = ((row, {'by': '준싱', 'until': (NOW + dt.timedelta(hours=2)).isoformat()}),)
        text = nudge.text(NOW, [row], quiet)
        self.assertIn("jun's decision", text)
        self.assertIn('(jun, quiet until', text)
        self.assertNotIn('준싱', text)

    def test_pair_state_compatibility(self):
        state = {'label': 'fixture', 'kind': 'pair', 'by': '준싱', 'file': '준싱.md'}
        with patch.object(smoke, 'STATE', self.root):
            smoke.save(state)
            self.assertEqual(smoke.load('fixture')['by'], 'jun')
            path = self.root / 'fixture.json'
            self.assertEqual(json.loads(path.read_text())['by'], 'jun')
            path.write_text(json.dumps(state))
            self.assertEqual(smoke.load('fixture')['by'], 'jun')
        with patch.object(pair_report, 'SMOKE', str(self.root)):
            self.assertEqual(pair_report.state('fixture')['by'], 'jun')

    def test_brain_canonicalizes_excerpts_without_editing_sources(self):
        docs = self.root / 'docs'
        docs.mkdir()
        source = docs / 'PROMISES.md'
        source.write_text('준싱 will review the fixture.')
        with patch.object(chat, 'bot_versions', return_value='## Bot versions on the server\nFixture'), \
                patch.object(chat, 'read_text', side_effect=lambda path, budget: source.read_text() if path == source else '[unavailable]'), \
                patch.object(bot, 'board_state', return_value=[]), patch.object(bot, 'gh', return_value=[]):
            brain = chat.build_brain(bot, root=self.root, team=self.root, memory=self.root, look=self.root)
        self.assertIn('jun will review the fixture.', brain)
        self.assertNotIn('준싱', brain)
        self.assertEqual(source.read_text(), '준싱 will review the fixture.')
