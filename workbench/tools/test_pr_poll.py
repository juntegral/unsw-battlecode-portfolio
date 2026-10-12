"""Offline PR polling tests; all GitHub calls are fake and state is temporary."""
import copy
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import meowbot
import team_watch
from pr_poll import pr_activity


def pull(n=19, **changes):
    p = dict(number=n, title=f'Test {n}', state='OPEN', isDraft=False,
             author={'login': 'teammate'}, headRefName='topic', headRefOid='aaa',
             updatedAt='2026-10-04T07:02:00Z', mergedAt=None, closedAt=None,
             url=f'https://example.invalid/pull/{n}')
    p.update(changes)
    return p


def event(n, action='opened', eid=1):
    return dict(id=str(eid), type='PullRequestEvent', actor={'login': 'teammate'},
                created_at='2026-10-04T07:02:00Z', payload=dict(action=action,
                pull_request=dict(number=n, title=f'Test {n}', merged=False)))


class PollTests(unittest.TestCase):
    def test_watch_displays_own_github_login_as_jun(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, 'last.txt')
            pulls = [pull()]
            def fake_run(args, **kwargs):
                return subprocess.CompletedProcess(args, 0, json.dumps(pulls if args[1] == 'pr' else []), '')
            with patch.object(team_watch.subprocess, 'run', side_effect=fake_run):
                team_watch.github(state)
                pulls.append(pull(26, author={'login': 'juntegral'}))
                self.assertEqual(team_watch.github(state), ['- 10-04 07:02Z jun: PR #26 opened: Test 26'])

    def test_seed_and_lifecycle(self):
        st = {}
        self.assertEqual(pr_activity(st, [pull(), pull(20, state='MERGED')]), [])
        self.assertEqual(st['pr_snapshot']['19'], dict(state='OPEN', draft=False, head='aaa'))
        got = pr_activity(st, [pull(), pull(20, state='MERGED'), pull(21)])
        self.assertEqual([(p['number'], a) for p, a in got], [(21, 'opened')])
        self.assertEqual(pr_activity(st, [pull(21)]), [])
        self.assertEqual(pr_activity(st, [pull(21, state='MERGED')])[0][1], 'merged')
        self.assertEqual(pr_activity(st, [pull(state='CLOSED')])[0][1], 'closed')
        self.assertEqual(pr_activity(st, [pull()])[0][1], 'reopened')

    def test_ready_and_head(self):
        st = {}
        pr_activity(st, [pull(isDraft=True)])
        got = pr_activity(st, [pull(headRefOid='bbb')], head_changes=True)
        self.assertEqual([a for _, a in got], ['ready-for-review', 'new commits pushed'])
        self.assertEqual(pr_activity(st, [pull(headRefOid='bbb')], head_changes=True), [])
        self.assertEqual([a for _, a in pr_activity(st, [pull(headRefOid='ccc')], head_changes=True)], ['new commits pushed'])
        self.assertEqual(pr_activity(st, [pull(headRefOid='ddd')]), [])

    def test_catchup_once_and_existing_record(self):
        st = {}
        self.assertEqual([a for _, a in pr_activity(st, [pull(26)])], ['opened'])
        st = json.loads(json.dumps(st))
        self.assertEqual(pr_activity(st, [pull(26)]), [])
        for prior in ({'pr_actions': {'26': ['opened']}},
                      {'candidates': {'old': {'pr': 26}}},
                      {'pr_snapshot': {'26': dict(state='OPEN', draft=False, head='aaa')}}):
            self.assertEqual(pr_activity(prior, [pull(26)]), [])
        self.assertEqual(pr_activity({}, [pull(26, state='CLOSED')]), [])
        self.assertEqual(pr_activity({}, [pull(26, state='MERGED')]), [])

    def test_meowbot_dedupe_and_candidate_reset_source(self):
        st, pulls, events = {}, [pull()], []
        def fake_gh(args):
            self.assertIn(args[0], ('pr', 'api'))
            return copy.deepcopy(pulls if args[0] == 'pr' else events)
        with patch.object(meowbot, 'gh', side_effect=fake_gh):
            self.assertEqual(meowbot.new_events(st), [])
            pulls.append(pull(26))
            events.append(event(26))
            self.assertEqual(meowbot.new_events(st), [('pr', 26, 'opened')])
            events.append(event(26, eid=2))
            self.assertEqual(meowbot.new_events(st), [])
            pulls[-1]['headRefOid'] = 'bbb'
            self.assertEqual(meowbot.new_events(st), [])
            pulls[-1]['state'] = 'MERGED'
            events.append(event(26, 'closed', 3))
            self.assertEqual(meowbot.new_events(st), [('pr', 26, 'merged')])

    def test_meowbot_first_run_catchup(self):
        with patch.object(meowbot, 'gh', side_effect=lambda args: [pull(19), pull(26)] if args[0] == 'pr' else []):
            st = {}
            self.assertEqual(meowbot.new_events(st), [('pr', 26, 'opened')])
            self.assertEqual(meowbot.new_events(st), [])

    def test_candidate_detection_still_uses_current_head(self):
        st = {'candidates': {'old-card': {'pr': 26, 'head_sha': 'aaa'}}}
        pages = [[dict(number=26, html_url='https://example.invalid/26', head={'sha': 'bbb'})]]
        with patch.object(meowbot, 'gh', return_value=pages), patch.object(meowbot, 'pr_candidates', return_value=[]) as detect:
            self.assertEqual(meowbot.new_candidates(st), [])
            detect.assert_called_once_with(dict(number=26, state='OPEN', url='https://example.invalid/26', headRefOid='bbb'), {'old-card'})

    def test_watch_both_modes_migration_dedupe_and_head(self):
        for prs in (False, True):
            with self.subTest(prs=prs), tempfile.TemporaryDirectory() as tmp:
                state = os.path.join(tmp, 'last.txt')
                with open(state, 'w') as f:
                    f.write('10\n')
                pulls, events = [pull(), pull(26)], [event(26, eid=11)]
                def fake_run(args, **kwargs):
                    self.assertEqual(args[0], 'gh')
                    return subprocess.CompletedProcess(args, 0, json.dumps(pulls if args[1] == 'pr' else events), '')
                with patch.object(team_watch.subprocess, 'run', side_effect=fake_run):
                    self.assertEqual(team_watch.github(state, prs), ['- 10-04 07:02Z teammate: PR #26 opened: Test 26'])
                    events.append(event(26, eid=12))
                    self.assertEqual(team_watch.github(state, prs), [])
                    pulls[-1]['headRefOid'] = 'bbb'
                    self.assertIn('PR #26 new commits pushed:', team_watch.github(state, prs)[0])
                    pulls[-1]['state'] = 'CLOSED'
                    self.assertIn('PR #26 closed:', team_watch.github(state, prs)[0])
                    pulls[-1]['state'] = 'OPEN'
                    self.assertIn('PR #26 reopened:', team_watch.github(state, prs)[0])
                    pulls[-1]['state'] = 'MERGED'
                    self.assertIn('PR #26 merged:', team_watch.github(state, prs)[0])
                    self.assertEqual(team_watch.github(state, prs), [])


if __name__ == '__main__':
    unittest.main()
