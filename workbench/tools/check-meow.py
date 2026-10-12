#!/usr/bin/env python3
"""Offline /meow regression suite: all Discord, GitHub and Claude calls are fakes."""
import asyncio
import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

import meowbot as api
import meow_chat as c
import meow_guard as guard
from meow_ui import MeowUI

UID, OTHER = list(api.MEMBERS)[:2]


class Offline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for target in ('subprocess.run', 'subprocess.Popen', 'urllib.request.urlopen'):
            patcher = patch(target, side_effect=AssertionError('Unexpected external call'))
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_router(self):
        for text in ['What is a toggle?', 'Explain the queue', 'How does sonar work?']:
            self.assertEqual(c.route(text), ('claude-sonnet-5-5', 'medium'))
        for text in ['Analyze card 7', 'why did this fail?', 'Submit main', 'force OK #12',
                     'What should we do?', '비교 분석해줘', '暂停 runner', 'hello']:
            self.assertEqual(c.route(text), ('opus', 'high'))

    def test_direct_commands(self):
        for message, name in [('/answer 7 원문', 'answer'), ('submit main', 'submit'),
                              ('force OK #12', 'vote'), ('pause runner', 'pause_runner'),
                              ('resume_runner', 'resume_runner'), ('set_state 7 ready', 'set_state')]:
            plan = c.direct_plan(message)
            self.assertEqual(plan['actions'][0]['action'], name)
            c.validate_plan(plan, UID, api.MEMBERS)
        self.assertTrue(c.direct_plan('강행 submit main')['actions'][0]['force'])
        self.assertIsNone(c.direct_plan('compare the two proposals'))

    def test_plan_whitelist_and_identity(self):
        for action in [{'action': 'answer', 'card': 7, 'text': 'unchanged'},
                       {'action': 'vote', 'candidate': '#12', 'vote': 'OK'}]:
            plan = c.validate_plan({'actions': [action]}, UID, api.MEMBERS)
            self.assertEqual(plan['actions'][0]['requester_id'], str(UID))
            for spoof in [{'user_id': str(OTHER)}, {'requester_id': str(OTHER)}, {'author': 'Zhe'}]:
                with self.assertRaises(ValueError):
                    c.validate_plan({'actions': [dict(action, **spoof)]}, UID, api.MEMBERS)
        bad = [{'action': 'shell', 'command': 'echo x'}, {'action': 'delete_issue', 'card': 7},
               {'action': 'queue_test', 'card': 7, 'kind': 'ranked'},
               {'action': 'set_state', 'card': True, 'state': 'ready'},
               {'action': 'submit', 'ref': '--upload-pack=x'},
               {'action': 'use_branch_as_impl', 'card': 7, 'branch_or_commit': 'a..b'},
               {'action': 'pause_runner', 'force': 'yes'}]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                c.validate_plan({'actions': [a]}, UID, api.MEMBERS)
        with self.assertRaises(ValueError):
            c.validate_plan({'actions': []}, 0, api.MEMBERS)

    def test_json_reply(self):
        answer, plan = c.parse_reply('Ready.\n```json\n{"actions":[{"action":"pause_runner"}]}\n```', UID, api.MEMBERS)
        self.assertEqual(answer, 'Ready.')
        self.assertEqual(plan['actions'][0]['requester_id'], str(UID))
        with self.assertRaises(ValueError):
            c.parse_reply('```json\n{"actions": broken}\n```', UID, api.MEMBERS)
        with self.assertRaises(ValueError):
            c.parse_reply('```json\n{"actions":[{"action":"delete_issue"}]}\n```', UID, api.MEMBERS)

    def test_force_requires_confirm_and_reason(self):
        r = c.new_confirmation({'actions': [{'action': 'pause_runner', 'force': True}]}, UID, 99, api.MEMBERS)
        for event in ['reason', 'execute']:
            with self.assertRaises(ValueError):
                c.advance(r, UID, event, 'because')
        with self.assertRaises(ValueError):
            c.advance(r, OTHER, 'confirm')
        self.assertEqual(c.advance(r, UID, 'confirm'), 'reason')
        self.assertEqual(c.advance(r, UID, 'confirm'), 'reason')
        for text in ['', 'a\nb', 'I take responsibility: ', 'x' * 301]:
            with self.assertRaises(ValueError):
                c.advance(r, UID, 'reason', text)
        with self.assertRaises(ValueError):
            c.advance(r, OTHER, 'reason', 'urgent fix')
        self.assertEqual(c.advance(r, UID, 'reason', 'I take responsibility: urgent fix'), 'executing')
        self.assertIn('⚠️ forced by jun: urgent fix', c.audit_line(r, api.MEMBERS))
        with self.assertRaises(ValueError):
            c.advance(r, UID, 'confirm')
        r = c.new_confirmation({'actions': [{'action': 'pause_runner', 'force': True}]}, UID, 99, api.MEMBERS, 'own words')
        self.assertEqual((r['stage'], r['reason']), ('final', 'own words'))
        with self.assertRaises(ValueError):
            c.advance(r, OTHER, 'confirm')
        self.assertEqual(c.advance(r, UID, 'confirm'), 'executing')
        r = c.new_confirmation({'actions': [{'action': 'pause_runner'}]}, UID, 99, api.MEMBERS, 'not forced')
        self.assertEqual((r['stage'], r.get('reason')), ('review', None))

    def test_cancel_and_expiry(self):
        r = c.new_confirmation({'actions': [{'action': 'resume_runner'}]}, UID, 9, api.MEMBERS)
        c.advance(r, UID, 'cancel')
        with self.assertRaises(ValueError):
            c.advance(r, UID, 'confirm')
        r = c.new_confirmation({'actions': []}, UID, 9, api.MEMBERS)
        r['created'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).isoformat()
        with self.assertRaisesRegex(ValueError, 'expired'):
            c.advance(r, UID, 'confirm')

    def test_queue_survives_reload(self):
        st = {}
        row = c.enqueue(st, UID, 9, 'Who decides?', True)
        st = json.loads(json.dumps(st))
        self.assertIn(row['id'], c.queue_text(st))
        st['meow-queue'][0]['status'] = 'done'
        self.assertEqual(c.queue_text(st), 'No pending /meow requests.')

    def test_brain_all_sources_and_bound(self):
        for name, text in {'team/docs/LOOP.md': 'Loop rule\n' * 5000,
                           'docs/PROMISES.md': 'promise\n' * 1000,
                           'out/status.json': '{"paused":false}',
                           'data/analysis/new.md': 'analysis\n' * 3000,
                           'memory/MEMORY.md': 'memory index\n' * 500,
                           'memory/note.md': 'memory details\n' * 500,
                           'data/discord/history.md': ''.join(f'- 10-04 01:{i:02} **Zhe**: message{i}\n  extra\n' for i in range(60))}.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        gh = Mock(return_value=[{'number': 7, 'title': '[Idea] Feeding', 'labels': [], 'body': 'body',
                                 'comments': [{'body': 'What we tried: Last result\n[check]'}]}])
        fake = types.SimpleNamespace(gh=gh, REPO=api.REPO, is_board_card=api.is_board_card, card_ref=api.card_ref)
        with patch.object(guard, 'safe_path', return_value=True), \
                patch.object(c, 'bot_versions', return_value='## Bot versions on the server\nFixture versions'):
            text = c.build_brain(fake, self.root, self.root / 'team', self.root / 'memory', self.root / 'out')
            messages = c.recent_discord(self.root / 'data/discord')
        self.assertLessEqual(len(text.encode()), 15000)
        self.assertEqual(len(messages), 40)
        self.assertIn('message20', messages[0])
        self.assertIn('message59', messages[-1])
        for word in ['Loop rule', 'promise', 'paused', 'Last result', 'message59', 'analysis', 'memory index', 'memory details']:
            self.assertIn(word, text)
        self.assertEqual((self.root / 'data/meow/brain.md').read_text(), text)

    def test_session_resume_and_settings(self):
        sid = '12345678-abcd-1234-abcd-123456789012'
        response = types.SimpleNamespace(returncode=0, stdout=json.dumps({'result': 'hello', 'session_id': sid}))
        with patch.object(c, 'build_brain', return_value='brain'), patch.object(c.subprocess, 'run', return_value=response) as call:
            self.assertEqual(c.session_call(api, 'What is sonar?', sid), ('hello', sid))
        argv = call.call_args.args[0]
        self.assertEqual(argv[argv.index('--resume') + 1], sid)
        self.assertIn('--strict-mcp-config', argv)
        self.assertNotIn('--no-session-persistence', argv)
        self.assertEqual(argv[argv.index('--tools') + 1], 'Read,Glob,Grep,Bash')
        self.assertTrue(call.call_args.kwargs['env']['MEOW_GUARD'].endswith('meow_guard.py'))
        settings = json.loads((c.ROOT / 'tools/meow-settings.json').read_text())
        self.assertIn('$MEOW_GUARD', settings['hooks']['PreToolUse'][0]['hooks'][0]['command'])

    def test_guard_keys_aliases_and_tools(self):
        for name in ['docs/api.txt', 'docs/discord.txt', '~/Downloads/api.txt', 'docs/../docs/api.txt',
                     '.git/config', '.env', '../battlecode/docs/api.txt']:
            self.assertIsNotNone(guard.check({'cwd': str(c.ROOT), 'tool_name': 'Read', 'tool_input': {'file_path': name}}))
        link = self.root / 'innocent.md'
        link.symlink_to(c.ROOT / 'docs/api.txt')
        with patch.object(guard, 'roots', return_value=[self.root, c.ROOT]):
            self.assertFalse(guard.safe_path(str(link)))
        for tool in ['Write', 'Edit', 'Task', 'Agent', 'mcp__gh__create_issue']:
            self.assertIsNotNone(guard.check({'tool_name': tool, 'tool_input': {}}))
        self.assertIsNotNone(guard.check({'tool_name': 'Grep', 'tool_input': {'path': str(c.ROOT), 'pattern': '.'}}))
        self.assertIsNone(guard.check({'tool_name': 'Read', 'tool_input': {'file_path': str(c.ROOT / 'docs/PROMISES.md')}}))

    def test_guard_shell_allowlist(self):
        allowed = [f'gh issue view 7 --repo {api.REPO} --comments',
                   f'gh pr list --repo {api.REPO} --json number,title',
                   f'git -C "{c.TEAM}" log --oneline --max-count=10',
                   f'git -C "{c.TEAM}" show HEAD:mybot2/main.cpp']
        allowed += [f'node "{c.ROOT}/tools/online.js" {name} --json' for name in ['leaderboard', 'team', 'battles', 'submissions']]
        allowed += [f'node "{c.ROOT}/tools/online.js" download 123 --out meow/test']
        denied = ['cat docs/api.txt', 'python3 -c "print(1)"', 'echo $(cat docs/api.txt)', 'git push',
                  f'gh pr merge 7 --repo {api.REPO}', f'gh issue view 7 --repo {api.REPO} --web',
                  f'git -C "{c.TEAM}" show HEAD:docs/api.txt', 'gh api user',
                  f'node "{c.ROOT}/tools/online.js" request 1 --ranked',
                  f'node "{c.ROOT}/tools/online.js" download 1 --out ../../escape',
                  f'node "{c.ROOT}/tools/online.js" team --json; echo hello']
        for command in allowed:
            self.assertIsNone(guard.check({'tool_name': 'Bash', 'tool_input': {'command': command}}), command)
        for command in denied:
            self.assertIsNotNone(guard.check({'tool_name': 'Bash', 'tool_input': {'command': command}}), command)

    def test_protected_merge_paths(self):
        for path in ['docs/LOOP.md', 'docs/LOOP.zh.md', 'rules/rule.txt', 'AGENTS.md', '.claude/x',
                     'docs/PROMISES.md', 'memory/MEMORY.md', 'docs/api.txt']:
            self.assertTrue(c.protected_change(path), path)
        self.assertFalse(c.protected_change('mybot2/main.cpp'))
        with patch.object(api, 'gh', return_value=[[{'filename': 'new.md', 'previous_filename': 'docs/LOOP.md'}]]):
            with self.assertRaises(ValueError):
                c.check_pr_files(api, 7)

    def test_answer_attribution_and_audit(self):
        st = {}
        executor = c.Actions(api, st)
        card = {'title': '[Idea] test', 'body': 'old', 'state': 'OPEN', 'labels': [{'name': 'status:needs-info'}]}
        rec = c.new_confirmation({'actions': [{'action': 'answer', 'card': 7, 'text': '원문'}]}, UID, 9, api.MEMBERS)
        rec['stage'] = 'executing'
        with patch.object(executor, 'card', return_value=card), patch.object(api, 'gh_comment') as comment, patch.object(api, 'save_state'):
            executor.prepare(rec)
            executor.execute(rec['prepared'][0], rec)
        self.assertEqual(comment.call_args.args, ('issue', 7, 'Answer from jun: 원문\n\nvia /meow by jun'))

    def test_any_member_moves_a_card_but_workflow_gate_needs_force(self):
        executor = c.Actions(api, {})
        card = {'title': '[Idea] test', 'body': 'old', 'state': 'OPEN',
                'labels': [{'name': 'status:tested'}, {'name': 'by:zhe'}]}
        rec = c.new_confirmation({'actions': [{'action': 'set_state', 'card': 7, 'state': 'candidate'}]}, UID, 9, api.MEMBERS)
        with patch.object(executor, 'card', return_value=card):
            executor.prepare(rec)
            executor.gate(rec['prepared'][0], rec)
            rec['prepared'][0]['state'] = 'kept'
            with self.assertRaisesRegex(ValueError, 'skips a workflow gate'):
                executor.gate(rec['prepared'][0], rec)
            rec['prepared'][0]['force'] = True
            executor.gate(rec['prepared'][0], rec)

    def test_force_merge_pinned_and_identity_queue(self):
        st = {'candidates': {'key': {'pr': 12, 'head_sha': 'a' * 40, 'status': 'hold', 'oks': [],
                                   'author_labels': ['by:zhe'], 'manifest': {'issues': [7], 'changes': ['fix']}}}}
        executor = c.Actions(api, st)
        rec = c.new_confirmation({'actions': [{'action': 'vote', 'candidate': '#12', 'vote': 'OK', 'force': True}]}, UID, 9, api.MEMBERS)
        rec.update(reason='needed', stage='executing', index=0)
        def gh(args):
            if args[:2] == ['issue', 'view']: return {'number': 7, 'title': '[Idea] test', 'labels': [{'name': 'name:test'}]}
            if '/files?' in args[1]: return [[{'filename': 'mybot2/main.cpp'}]]
            if args[1].endswith('commits/main'): return {'sha': 'b' * 40}
            if '/commits/' in args[1]: return {'parents': [{'sha': 'b' * 40}]}
            raise AssertionError(args)
        with patch.object(api, 'gh', side_effect=gh), patch.object(api, 'LOOK_DIR', str(self.root)), \
             patch.object(api, 'save_state'), patch.object(api, 'keep_cards'), patch.object(api, 'gh_comment') as comment, \
             patch.object(api, 'candidate_current', side_effect=AssertionError('Force must skip stale gate')), \
             patch.object(api, 'candidate_pr', return_value={'headRefOid': 'a' * 40, 'state': 'OPEN', 'baseRefName': 'main', 'isDraft': False}), \
             patch.object(api, 'merge_candidate', return_value='c' * 40) as merge:
            executor.prepare(rec)
            executor.execute(rec['prepared'][0], rec)
        merge.assert_called_once()
        self.assertEqual(st['candidates']['key']['status'], 'approved')
        self.assertEqual(st['candidates']['key']['oks'], [str(UID)])
        queued = json.loads(next((self.root / 'meow-requests').glob('*.json')).read_text())
        self.assertEqual(queued['action'], 'identity_notice')
        self.assertEqual(queued['base'], 'b' * 40)
        self.assertIn('⚠️ forced by jun: needed', comment.call_args.args[-1])
        self.assertEqual(len(st['meow-queue']), 1)

    def test_executor_refuses_unconfirmed_even_with_force(self):
        executor = c.Actions(api, {})
        rec = c.new_confirmation({'actions': [{'action': 'pause_runner', 'force': True}]}, UID, 9, api.MEMBERS)
        with self.assertRaisesRegex(ValueError, 'confirmation'):
            executor.execute(rec['plan']['actions'][0], rec)
        rec['stage'] = 'executing'
        with self.assertRaisesRegex(ValueError, 'confirmation'):
            executor.execute(rec['plan']['actions'][0], rec)

    def test_changed_head_still_blocks_force(self):
        st = {'candidates': {'key': {'pr': 12, 'head_sha': 'a' * 40, 'status': 'pending', 'oks': [],
                                   'manifest': {'issues': [7]}}}}
        executor = c.Actions(api, st)
        rec = c.new_confirmation({'actions': [{'action': 'vote', 'candidate': 'key', 'vote': 'OK', 'force': True}]}, UID, 9, api.MEMBERS)
        rec.update(stage='executing', reason='urgent')
        with patch.object(c, 'check_pr_files', return_value=[]), patch.object(api, 'save_state'), patch.object(api, 'gh_comment'), \
             patch.object(api, 'candidate_pr', return_value={'headRefOid': 'b' * 40}), \
             patch.object(api, 'merge_candidate', side_effect=AssertionError('must not merge')):
            executor.prepare(rec)
            with self.assertRaisesRegex(ValueError, 'revision changed'):
                executor.execute(rec['prepared'][0], rec)

    def test_force_uses_admin_but_never_branch_deletion(self):
        pr = {'state': 'MERGED', 'baseRefName': 'main', 'headRefOid': 'a' * 40, 'mergeCommit': {'oid': 'b' * 40}}
        with patch.object(api.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0)) as call, \
             patch.object(api, 'candidate_pr', return_value=pr):
            api.merge_candidate({'pr': 12, 'head_sha': 'a' * 40}, force=True)
        self.assertIn('--admin', call.call_args.args[0])
        self.assertIn('--match-head-commit', call.call_args.args[0])
        self.assertNotIn('--delete-branch', call.call_args.args[0])

    def test_force_upload_passes_existing_tool_override_only(self):
        output = types.SimpleNamespace(returncode=0, stdout='active: 62 v62; server zip matches mybot2', stderr='')
        with patch.object(api.subprocess, 'run', return_value=output) as call, patch.object(api, 'UPLOAD_ENABLED', False):
            result = api.upload({'version': 'v62', 'bot_dir': 'mybot2', 'changes': []}, force=True)
        self.assertTrue(result['ok'])
        self.assertIn('--confirm', call.call_args.args[0])
        self.assertIn('--force', call.call_args.args[0])
        self.assertNotIn('--ranked', call.call_args.args[0])

    def test_normal_meow_submit_rechecks_freeze_after_sync(self):
        executor = c.Actions(api, {})
        rec = c.new_confirmation({'actions': [{'action': 'submit', 'ref': 'main'}]}, UID, 9, api.MEMBERS)
        rec['stage'] = 'executing'
        a = {'action': 'submit', 'ref': 'main', '_submit': {'commit': 'a' * 40, 'version': 'v62', 'previous_id': 61}}
        with patch.object(executor, 'audit_intent'), patch.object(api, 'submit_frozen', side_effect=[False, True]), \
             patch.object(api, 'submission_list', return_value=[{'id': 61, 'name': 'v61', 'status': 'active'}]), \
             patch.object(api, 'sync_release') as sync, patch.object(api, 'upload', side_effect=AssertionError('frozen')):
            with self.assertRaisesRegex(ValueError, 'Freeze reached'):
                executor.execute(a, rec)
        sync.assert_called_once_with('a' * 40)


class FakeView:
    def __init__(self, **kw): self.children = []
    def add_item(self, item): self.children.append(item)


class FakeItem:
    def __init__(self, **kw): self.__dict__.update(kw); self.value = ''


class Channel:
    def __init__(self, id=99): self.id = id; self.mention = f'<#{id}>'; self.messages = []
    async def send(self, text, **kw):
        self.messages.append((text, kw))
        return types.SimpleNamespace(create_thread=AsyncMock(return_value=self))


def discord_fake():
    return types.SimpleNamespace(ui=types.SimpleNamespace(View=FakeView, Modal=FakeView, Button=FakeItem,
                                                         TextInput=FakeItem, Select=FakeItem),
        TextStyle=types.SimpleNamespace(short=1), ButtonStyle=types.SimpleNamespace(success=1, secondary=2),
        SelectOption=FakeItem, AllowedMentions=types.SimpleNamespace(none=lambda: None, __call__=lambda **kw: None))


def interaction(uid=UID, channel=None):
    return types.SimpleNamespace(user=types.SimpleNamespace(id=uid), channel=channel or Channel(),
        response=types.SimpleNamespace(send_message=AsyncMock(), send_modal=AsyncMock(), edit_message=AsyncMock()),
        followup=types.SimpleNamespace(send=AsyncMock()))


class UITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.channel = Channel()
        self.st = {'meow_threads': {'99': {'session': None}}}
        self.saver = patch.object(api, 'save_state').start()
        self.addCleanup(patch.stopall)
        patch('subprocess.run', side_effect=AssertionError('External call')).start()
        self.ui = MeowUI(api, discord_fake(), self.st, {'channel': self.channel}, asyncio.Lock(), asyncio.Lock())

    async def test_force_ui_double_click_and_public_notice(self):
        rec = c.new_confirmation({'actions': [{'action': 'pause_runner', 'force': True}]}, UID, 99, api.MEMBERS)
        self.st['meow_confirmations'] = {rec['id']: rec}
        rec['prepared'] = rec['plan']['actions']
        view = self.ui.ConfirmView(rec['id'])
        it = interaction(channel=self.channel)
        self.ui.actions.execute = Mock(return_value='Paused.')
        await view.confirm(it)
        self.assertEqual(rec['stage'], 'reason')
        self.ui.actions.execute.assert_not_called()
        modal = it.response.send_modal.call_args.args[0]
        modal.reason.value = 'Urgent diagnosis'
        await asyncio.gather(modal.on_submit(interaction(channel=self.channel)), modal.on_submit(interaction(channel=self.channel)))
        self.ui.actions.execute.assert_called_once()
        self.assertEqual(rec['stage'], 'done')
        await view.confirm(interaction(channel=self.channel))
        self.ui.actions.execute.assert_called_once()
        self.assertTrue(rec['force_notice'])
        self.assertTrue(any('⚠️ forced by jun: Urgent diagnosis' in text and 'Result:' in text for text, kw in self.channel.messages))

    async def test_meow_force_card_request(self):
        reply = '```json\n{"actions":[{"action":"set_state","card":31,"state":"candidate","force":true}]}\n```'
        with patch.object(c, 'session_call', return_value=(reply, 'session')) as model, \
             patch.object(self.ui, 'offer', new_callable=AsyncMock) as offer:
            await self.ui.slash(interaction(channel=self.channel), 'force #31 candidate')
        self.assertIn('force #31 candidate', model.call_args.args[1])
        self.assertEqual(offer.call_args.args[2]['actions'][0],
                         {'action': 'set_state', 'card': 31, 'state': 'candidate', 'force': True,
                          'requester_id': str(UID)})

    async def test_nonmember_and_other_member(self):
        it = interaction(0)
        await self.ui.slash(it, 'do something')
        self.assertIn('Only team members', it.response.send_message.call_args.args[0])
        r = c.new_confirmation({'actions': [{'action': 'pause_runner'}]}, UID, 99, api.MEMBERS)
        self.st['meow_confirmations'] = {r['id']: r}
        view = self.ui.ConfirmView(r['id'])
        await view.confirm(interaction(OTHER))
        self.assertEqual(r['stage'], 'review')

    async def test_ack_precedes_slow_work_and_thread_resume(self):
        it = interaction(channel=self.channel)
        sid = '12345678-abcd-1234-abcd-123456789012'
        def session(api, message, previous):
            self.assertTrue(it.response.send_message.called)
            return 'All good.', sid
        with patch.object(c, 'session_call', side_effect=session) as model:
            await self.ui.slash(it, 'What is sonar?')
            message = types.SimpleNamespace(author=types.SimpleNamespace(id=UID, bot=False),
                                            channel=self.channel, content='And split?')
            await self.ui.followup(message)
        self.assertEqual(model.call_args_list[0].args[2], None)
        self.assertEqual(model.call_args_list[1].args[2], sid)
        self.assertEqual(self.st['meow_threads']['99']['session'], sid)

    async def test_restart_never_reexecutes_uncertain_action(self):
        r = c.new_confirmation({'actions': [{'action': 'pause_runner'}]}, UID, 99, api.MEMBERS)
        r['stage'] = 'executing'
        self.st['meow_confirmations'] = {r['id']: r}
        self.ui.restore(types.SimpleNamespace(add_view=Mock()))
        self.assertEqual(r['stage'], 'uncertain')
        self.assertEqual(len(self.st['meow-queue']), 1)

    async def test_identity_failure_posts_thread_and_public_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            row = c.enqueue(self.st, UID, 7, 'identity', request_id='abc')
            path = Path(directory) / 'meow-results/abc.json'
            path.parent.mkdir()
            path.write_text(json.dumps({'ok': False, 'message': 'Identity failed; notification only.'}))
            thread = Channel(7)
            client = types.SimpleNamespace(get_channel=lambda n: thread)
            with patch.object(api, 'LOOK_DIR', directory):
                await self.ui.poll(client)
                await self.ui.poll(client)
        self.assertEqual((len(thread.messages), len(self.channel.messages)), (1, 1))
        self.assertTrue(all('⚠️' in message for message, kw in thread.messages + self.channel.messages))
        self.assertEqual(row['status'], 'needs-review')

    async def test_real_discord_views_construct_offline(self):
        import discord
        ui = MeowUI(api, discord, self.st, {'channel': self.channel}, asyncio.Lock(), asyncio.Lock())
        rec = c.new_confirmation({'actions': [{'action': 'pause_runner', 'force': True}]}, UID, 99, api.MEMBERS)
        self.st['meow_confirmations'] = {rec['id']: rec}
        for view in [ui.ConfirmView(rec['id']), ui.CardForceView(7), ui.CardFormView(UID, 'hypo', 'queen')]:
            self.assertTrue(view.children)
        form = ui.CardFormView(UID, 'hypo', 'queen')
        it = interaction(channel=self.channel)
        await form.children[0].callback(it)
        self.assertEqual(len(it.response.send_modal.call_args.args[0].children), 5)

    async def test_direct_form_skips_model(self):
        with patch.object(c, 'session_call', side_effect=AssertionError('unneeded model')):
            await self.ui.conversation(self.channel, UID, '/hypo queen')
        self.assertIn('usual card form', self.channel.messages[-1][0])
        self.assertTrue(self.channel.messages[-1][1]['view'].children)


if __name__ == '__main__':
    unittest.main()
