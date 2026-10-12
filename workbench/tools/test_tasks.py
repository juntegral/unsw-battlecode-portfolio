"""Task board checks with every GitHub call and data-file read stubbed."""
import contextlib
import datetime as dt
import io
import json
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, mock_open, patch

import meowbot as bot
import tasks

NOW = dt.datetime(2026, 10, 5, 21, 27, tzinfo=bot.KST)
UIDS = {name: str(uid) for uid, name in bot.MEMBERS.items()}


def card(n, name, owner, status, minutes=90, extra=()):
    return {'number': n, 'title': '[Idea] ' + name, 'url': f'https://github.com/{bot.REPO}/issues/{n}',
            'createdAt': (NOW - dt.timedelta(days=2)).isoformat(),
            'updatedAt': (NOW - dt.timedelta(minutes=minutes)).isoformat(),
            'labels': [{'name': label} for label in ('name:' + name, bot.AUTHOR_LABELS[owner], 'status:' + status, *extra)]}


def pr(n=45, days=2, candidate=True, head='head'):
    return {'number': n, 'title': 'Queen safety', 'url': f'https://github.com/{bot.REPO}/pull/{n}',
            'createdAt': (NOW - dt.timedelta(days=days)).isoformat(),
            'updatedAt': (NOW - dt.timedelta(minutes=75)).isoformat(), 'headRefOid': head,
            'files': [{'path': 'candidates/v27.json'}] if candidate else []}


def candidate(oks=(), authors=('by:zhe',), status='pending', head='head', issues=(39,)):
    return {'pr': 45, 'head_sha': head, 'status': status, 'author_labels': list(authors),
            'oks': [UIDS[name] for name in oks], 'manifest': {'issues': list(issues)}}


def today_cards():
    return [card(39, 'queen-safety', 'Zhe', 'needs-info', 30),
            card(31, 'queen-hunt', 'Zhe', 'needs-look', 120),
            card(36, 'queen-dead-end', 'Zhe', 'needs-look', 90),
            card(16, 'safezone-v2', 'Zhe', 'untested'),
            card(38, 'queen-loop', 'QWQ', 'in-progress'),
            card(33, 'blind-circling', 'QWQ', 'in-progress'),
            card(22, 'late-feed', 'QWQ', 'in-progress')]


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.cards, self.prs, self.state, self.snapshot, self.snoozes = [], [], {}, {}, {}
        self.reads = []
        def opened(path, mode='r', *args, **kwargs):
            self.assertEqual(mode, 'r')
            self.reads.append(str(path))
            self.assertNotIn(str(path), (bot.ROOT + '/docs/api.txt', bot.ROOT + '/docs/discord.txt'))
            data = self.state if str(path) == bot.STATE else (
                {'cards': self.snapshot} if str(path).endswith('/status.json') else self.snoozes)
            return mock_open(read_data=json.dumps(data))()
        def gh(args):
            if args[:2] == ['issue', 'list']:
                self.assertIn('updatedAt', args[-1])
                return self.cards
            if args[:2] == ['pr', 'list']:
                return self.prs
            self.fail('Unexpected GitHub call: ' + repr(args))
        for target, kwargs in (
            ('builtins.open', {'side_effect': opened}),
            ('subprocess.run', {'side_effect': AssertionError('Unexpected process/network call')}),
            ('subprocess.Popen', {'side_effect': AssertionError('Unexpected process call')}),
            ('urllib.request.urlopen', {'side_effect': AssertionError('Unexpected network call')}),
            ('meowbot.gh', {'side_effect': gh}),
            ('meowbot.pr_candidates', {'return_value': []}),
        ):
            p = patch(target, **kwargs)
            p.start()
            self.addCleanup(p.stop)

    def collect(self):
        return tasks.collect(NOW)

    def test_four_wait_states_and_all_human_owners(self):
        for owner in tasks.NAMES:
            for status, action in tasks.ACTIONS.items():
                with self.subTest(owner=owner, status=status):
                    self.cards = [card(39, 'queen-safety', owner, status, minutes=15)]
                    person = self.collect()['people'][owner]
                    if status == 'needs-look' and owner != 'Zhe':
                        self.assertEqual(person['todo'], [])
                        continue
                    row, = person['todo']
                    self.assertEqual((row['ref'], row['action']), ('#39 queen-safety', action))
                    self.assertEqual(row['reply'], 'press OK on the candidate post' if status == 'candidate'
                                     else 'tell @meowbot, or /answer card:39 text:…')
                    self.assertEqual(tasks.age(row['since'], NOW), '15m')
                    self.assertEqual(row['waited'], '15m')

    def test_look_step_only_waits_on_zhe(self):
        self.cards = [card(31, 'queen-hunt', 'Zhe', 'needs-look'),
                      card(32, 'auto-check', 'jun', 'needs-look'),
                      card(34, 'ai-check', 'AI', 'needs-look')]
        people = self.collect()['people']
        self.assertEqual(len(people['Zhe']['todo']), 1)
        self.assertEqual(people['jun']['todo'], [])
        self.assertIn('passes by itself', people['jun']['yours'][0]['step'])

    def test_snoozed_card_stays_visible_but_does_not_count(self):
        self.cards = [card(39, 'queen-safety', 'Zhe', 'needs-info')]
        self.snoozes = {'39': {'until': (NOW + dt.timedelta(hours=3)).isoformat(), 'by': 'Zhe'}}
        data = self.collect()
        text = tasks.render(data, who='Zhe', now=NOW)
        self.assertIn('0 waiting', text)
        self.assertIn('#39 queen-safety', text)
        self.assertIn('(still deciding, quiet until ~00:27)', text)
        self.assertEqual(data['people']['Zhe']['todo'][0]['quiet_until'], self.snoozes['39']['until'])

    def test_expired_and_unrelated_snoozes_ignored(self):
        self.cards = [card(39, 'queen-safety', 'Zhe', 'tested')]
        self.snoozes = {'39': {'until': (NOW - dt.timedelta(minutes=1)).isoformat()},
                        '999': {'until': (NOW + dt.timedelta(hours=1)).isoformat()}}
        self.assertIn('1 waiting', tasks.render(self.collect(), who='Zhe'))

    def test_candidate_missing_non_author_ok(self):
        self.cards = [card(39, 'queen-safety', 'Zhe', 'candidate')]
        self.prs = [pr()]
        self.state = {'candidates': {'a': candidate(oks=('Zhe',))}}
        data = self.collect()
        self.assertEqual(data['people']['Zhe']['todo'], [])
        for name in ('jun', 'QWQ'):
            row, = data['people'][name]['todo']
            self.assertIn('non-author OK', row['action'])
            self.assertIn('#39 queen-safety', row['ref'])
            self.assertEqual(row['reply'], 'press OK on the candidate post')
        shared, = data['anyone']
        self.assertIn('missing non-author OK from jun/QWQ', shared['text'])
        self.assertIn(pr()['url'], shared['text'])

    def test_candidate_missing_author_ok(self):
        self.cards = [card(39, 'queen-safety', 'Zhe', 'candidate')]
        self.prs = [pr()]
        self.state = {'candidates': {'a': candidate(oks=('QWQ',))}}
        data = self.collect()
        self.assertIn('author OK: Zhe', data['people']['Zhe']['todo'][0]['action'])
        self.assertEqual(data['people']['QWQ']['todo'], [])
        self.assertEqual(data['anyone'], [])

    def test_new_unposted_candidate_uses_pr_link_and_no_carried_votes(self):
        self.cards = [card(39, 'queen-safety', 'Zhe', 'candidate')]
        self.prs = [pr()]
        self.state = {'candidates': {'old': candidate(head='old', oks=('Zhe', 'QWQ'))}}
        fresh = candidate()
        fresh.pop('author_labels')
        with patch.object(bot, 'pr_candidates', return_value=[('fresh', fresh)]), \
             patch.object(bot, 'candidate_authors', return_value=['by:zhe']):
            data = self.collect()
        row, = data['people']['Zhe']['todo']
        self.assertIn('author OK: Zhe', row['action'])
        self.assertIn(pr()['url'], row['reply'])
        self.assertIn('wait for the candidate post', row['reply'])
        self.assertIn('non-author OK', data['anyone'][0]['text'])
        self.assertEqual(len(data['people']['QWQ']['todo']), 1)

    def test_missing_cached_author_labels_uses_same_reader_as_ok_button(self):
        self.prs = [pr()]
        rec = candidate(oks=('Zhe',))
        rec.pop('author_labels')
        self.state = {'candidates': {'a': rec}}
        with patch.object(bot, 'candidate_authors', return_value=['by:zhe']) as authors:
            data = self.collect()
        authors.assert_called_once_with(rec['manifest'])
        self.assertEqual(data['people']['Zhe']['todo'], [])
        self.assertIn('non-author OK from jun/QWQ', data['anyone'][0]['text'])

    def test_candidate_no_votes_and_ai_unknown_authors(self):
        self.prs = [pr()]
        for authors in (('by:zhe',), ('by:ai',), ('by:unknown',)):
            with self.subTest(authors=authors):
                self.state = {'candidates': {'a': candidate(authors=authors)}}
                data = self.collect()
                self.assertTrue(all(len(p['todo']) == 1 for p in data['people'].values()))
                self.assertEqual(len(data['anyone']), 1)
        self.state = {'candidates': {'a': candidate(authors=('by:unknown',), oks=('QWQ',))}}
        data = self.collect()
        self.assertEqual(data['people']['QWQ']['todo'], [])
        self.assertIn('1 distinct member OK', data['anyone'][0]['text'])

    def test_multi_author_gate_matches_bot(self):
        self.prs = [pr()]
        for oks in ((), ('Zhe',), ('QWQ',), ('jun',), ('Zhe', 'jun')):
            rec = candidate(authors=('by:zhe', 'by:qwq'), oks=oks)
            self.state = {'candidates': {'a': rec}}
            data = self.collect()
            if bot.approval_ready(rec):
                self.assertEqual(data['anyone'], [])
                self.assertIn('confirm merge', data['people']['Zhe']['todo'][0]['action'])
            else:
                self.assertTrue(any(p['todo'] for p in data['people'].values()))

    def test_ready_candidate_needs_confirmation_not_extra_votes(self):
        self.prs = [pr()]
        self.state = {'candidates': {'a': candidate(oks=('Zhe', 'QWQ'))}}
        data = self.collect()
        self.assertEqual(data['anyone'], [])
        self.assertEqual(data['people']['jun']['todo'], [])
        self.assertIn('then Confirm', data['people']['QWQ']['todo'][0]['reply'])

    def test_stale_closed_handled_and_legacy_candidates_ignored(self):
        self.prs = [pr()]
        self.state = {'candidates': {'old': candidate(head='old'), 'stale': candidate(status='stale'),
                                     'merged': candidate(status='approved'), 'closed': dict(candidate(), pr=99),
                                     'legacy': {'status': 'pending', 'manifest': {}}}}
        data = self.collect()
        self.assertTrue(all(not person['todo'] for person in data['people'].values()))
        self.assertEqual(data['anyone'], [])

    def test_hold_candidate_can_still_be_approved(self):
        self.prs = [pr()]
        self.state = {'candidates': {'a': candidate(status='hold', oks=('Zhe',))}}
        self.assertIn('non-author OK', self.collect()['anyone'][0]['text'])

    def test_in_progress_parked_queue_building_testing_and_eta(self):
        self.cards = [card(38, 'queen-loop', 'QWQ', 'in-progress'),
                      card(16, 'safezone-v2', 'Zhe', 'untested'),
                      card(41, 'queued', 'Zhe', 'ready'), card(42, 'build', 'Zhe', 'building'),
                      card(43, 'test', 'Zhe', 'testing'),
                      card(44, 'queued-label', 'Zhe', 'untested', extra=('loop:ready',))]
        self.snapshot = {'42': {'step': 'build running', 'eta_at': (NOW + dt.timedelta(hours=1)).isoformat()}}
        data = self.collect()
        self.assertEqual(len(data['people']['Zhe']['yours']), 4)
        self.assertEqual(data['people']['Zhe']['parked'], [{'ref': '#16 safezone-v2'}])
        self.assertEqual(data['people']['QWQ']['yours'][0]['step'], 'in progress by hand')
        text = tasks.render(data)
        self.assertIn('build running · done ~22:27 KST', text)
        self.assertIn('queue it with status:ready or close it', text)
        self.assertIn('yours, nothing to do now', text)

    def test_late_eta_uses_revised_finish(self):
        self.cards = [card(42, 'build', 'Zhe', 'building')]
        self.snapshot = {'42': {'step': 'build running', 'late': True, 'eta_at': NOW.isoformat(),
                                'new_eta_at': (NOW + dt.timedelta(hours=2)).isoformat()}}
        self.assertIn('done ~23:27 KST', tasks.render(self.collect()))

    def test_final_states_are_not_parked(self):
        self.cards = [card(i, status, 'Zhe', status) for i, status in enumerate(bot.FINAL_STATES, 1)]
        self.assertEqual(self.collect()['people']['Zhe'], {'todo': [], 'yours': [], 'parked': []})

    def test_old_non_candidate_prs_only(self):
        self.prs = [pr(45), pr(46, candidate=False), pr(47, days=1, candidate=False), pr(48, days=0, candidate=False)]
        shared, = self.collect()['anyone']
        self.assertIn('PR #46', shared['text'])
        self.assertIn('review Queen safety (open 2d)', shared['text'])

    def test_live_ahead_line_requires_known_baseline_and_pending_merge(self):
        self.state = {'merged_candidates': [{'commit': 'new'}]}
        self.assertEqual(self.collect()['anyone'], [])
        self.state['active_submission'] = {'commit': 'live', 'merged_commits': []}
        self.assertIn('/submit uploads main', self.collect()['anyone'][0]['text'])
        self.state['active_submission']['merged_commits'] = ['new']
        self.assertEqual(self.collect()['anyone'], [])

    def test_oldest_first_and_unknown_dates(self):
        self.cards = [card(39, 'new', 'Zhe', 'needs-info', 10), card(31, 'old', 'Zhe', 'tested', 200)]
        rows = self.collect()['people']['Zhe']['todo']
        self.assertEqual([r['ref'] for r in rows], ['#31 old', '#39 new'])
        self.assertEqual(tasks.age(None, NOW), '?')
        self.assertEqual(tasks.age((NOW + dt.timedelta(hours=1)).isoformat(), NOW), '0m')

    def test_filter_caller_first_me_and_local_times(self):
        self.cards = today_cards()
        data = self.collect()
        all_text = tasks.render(data, caller='QWQ')
        self.assertLess(all_text.index('**QWQ**'), all_text.index('**jun**'))
        self.assertLess(all_text.index('**jun**'), all_text.index('**Zhe**'))
        self.assertIn('**Zhe** (14:27 there) · 3 waiting', all_text)
        self.assertIn('**QWQ** (23:27 there) · 0 waiting', all_text)
        self.assertTrue(all_text.startswith('📋 tasks · 21:27 KST'))
        for who in ('Zhe', 'me'):
            text = tasks.render(data, who=who, caller='Zhe')
            self.assertIn('**Zhe**', text)
            self.assertNotIn('**QWQ**', text)
            self.assertNotIn('**jun**', text)

    def test_nothing_waiting_and_footer(self):
        text = tasks.render(self.collect(), who='jun')
        self.assertIn('**jun** · 0 waiting\nnothing waiting', text)
        self.assertTrue(text.endswith(tasks.FOOTER))

    def test_character_cap_preserves_sections_counts_fences_footer(self):
        self.cards = [card(i, 'long-name' * 10, owner, 'tested', i)
                      for i in range(1, 55) for owner in tasks.NAMES]
        self.cards += [card(100 + i, 'parked' * 50, 'Zhe', 'untested') for i in range(40)]
        self.cards += [card(200 + i, 'building' * 30, 'QWQ', 'building') for i in range(40)]
        self.prs = [pr(300 + i, candidate=False) for i in range(40)]
        text = tasks.render(self.collect(), caller='Zhe')
        self.assertLess(len(text), 1900)
        self.assertIn('… and ', text)
        self.assertEqual(text.count('```') % 2, 0)
        self.assertTrue(text.endswith(tasks.FOOTER))
        self.assertTrue(text.splitlines()[1].startswith('**Zhe**'))
        self.assertIn('54 waiting', text)
        for name in tasks.NAMES:
            self.assertIn('**' + name + '**', text)
        self.assertIn('**anyone**', text)

    def test_code_fence_in_card_text_is_safe(self):
        self.cards = [card(39, '```\n@everyone', 'Zhe', 'needs-info')]
        text = tasks.render(self.collect())
        self.assertEqual(text.count('```'), 2)

    def test_preview_cli_exits_without_discord_bot(self):
        self.cards = today_cards()
        with patch.object(sys, 'argv', ['meowbot.py', '--preview-tasks', '--who', 'Zhe']), \
             patch.object(bot, 'run_bot') as run, contextlib.redirect_stdout(io.StringIO()) as output:
            bot.main()
        run.assert_not_called()
        self.assertIn('**Zhe**', output.getvalue())
        self.assertNotIn('**QWQ**', output.getvalue())

    def test_explicit_live_state_skips_state_file(self):
        tasks.collect(NOW, state={})
        self.assertNotIn(bot.STATE, self.reads)


class SlashTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.it = SimpleNamespace(user=SimpleNamespace(id=int(UIDS['Zhe'])),
                                  response=SimpleNamespace(defer=AsyncMock(), send_message=AsyncMock()),
                                  followup=SimpleNamespace(send=AsyncMock()))
        self.mentions = object()
        discord = SimpleNamespace(AllowedMentions=SimpleNamespace(none=lambda: self.mentions))
        p = patch.dict(sys.modules, {'discord': discord})
        p.start()
        self.addCleanup(p.stop)
        for target in ('builtins.open', 'subprocess.run', 'subprocess.Popen', 'urllib.request.urlopen', 'meowbot.gh'):
            p = patch(target, side_effect=AssertionError('Unexpected file/process/network call'))
            p.start()
            self.addCleanup(p.stop)

    async def test_private_default_and_shared_mentions_disabled(self):
        for share in (False, True):
            with patch.object(tasks, 'collect', return_value={}) as collect, \
                 patch.object(tasks, 'render', return_value='fixture') as render:
                await bot.reply_tasks(self.it, {'fixture': True}, share=share)
            self.assertEqual(collect.call_args.kwargs['state'], {'fixture': True})
            self.assertEqual(render.call_args.kwargs['caller'], 'Zhe')
            self.it.response.defer.assert_awaited_with(ephemeral=not share, thinking=True)
            self.it.followup.send.assert_awaited_with('fixture', ephemeral=not share, allowed_mentions=self.mentions)

    async def test_nonmember_does_not_collect_or_share(self):
        self.it.user.id = 999
        with patch.object(tasks, 'collect') as collect:
            await bot.reply_tasks(self.it, {}, share=True)
        collect.assert_not_called()
        self.it.followup.send.assert_not_awaited()
        self.it.response.send_message.assert_awaited_once_with('Only team members can use meowbot commands.', ephemeral=True)

    async def test_failure_sends_short_safe_error(self):
        with patch.object(tasks, 'collect', side_effect=RuntimeError('private detail')):
            await bot.reply_tasks(self.it, {})
        self.assertNotIn('private detail', self.it.followup.send.call_args.args[0])
        self.assertIn('Try /task again', self.it.followup.send.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
