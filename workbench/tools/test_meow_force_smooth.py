"""Deferred Force contracts, using only local fixtures and fake APIs."""
import asyncio
import datetime as dt
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

import meow_chat as chat
from meow_ui import MeowUI


class DeferredForce(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.card = {'number': 31, 'title': '[Idea] queen-hunt', 'body': 'Approved plan',
                     'state': 'OPEN', 'labels': [{'name': 'status:building'}]}
        self.api = types.SimpleNamespace(
            LOOK_DIR=str(self.root), REPO='fake/repo', MEMBERS={1: 'jun'},
            gh=Mock(side_effect=lambda args: self.card), is_board_card=lambda title: True,
            card_ref=lambda card: '#31 queen-hunt', save_state=Mock(), gh_comment=Mock())
        self.st = {}
        self.actions = chat.Actions(self.api, self.st)
        self.meta(attempt=3)

    def meta(self, **data):
        path = self.root / 'card-31/card.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(data))

    def prepare(self, force=True, target='candidate'):
        rec = chat.new_confirmation({'actions': [dict(action='set_state', card=31,
                                                     state=target, force=force)]}, 1, 99, self.api.MEMBERS)
        return self.actions.prepare(rec)

    def confirm(self, rec):
        self.assertEqual(chat.advance(rec, 1, 'confirm'), 'reason')
        self.assertEqual(chat.advance(rec, 1, 'reason', 'local tests were already enough'), 'executing')

    def test_deferred_preview_with_honest_step_eta(self):
        future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=20)
        (self.root / 'status.json').write_text(json.dumps({'cards': {'31': {'eta_at': future.isoformat()}}}))
        rec = self.prepare()
        clock = future.astimezone(dt.timezone(dt.timedelta(hours=9))).strftime('%H:%M KST')
        self.assertEqual(self.actions.preview(rec),
                         'Force for #31 queen-hunt: skip the remaining tests and open the candidate. '
                         f'The loop is still rebuilding it on the new main (current step done about {clock}); '
                         'confirm now and it happens by itself when this rebuild and its replay check finish. '
                         "You don't need to come back.")

    def test_no_invented_eta(self):
        self.assertNotIn('done about', self.actions.preview(self.prepare()))
        (self.root / 'status.json').write_text(json.dumps({'cards': {'31': {'eta_at': '2020-01-01T00:00:00Z'}}}))
        self.assertNotIn('done about', self.actions.preview(self.prepare()))

    def test_confirmation_spool_and_reply(self):
        rec = self.prepare()
        action = rec['prepared'][0]
        with self.assertRaisesRegex(ValueError, 'confirmation'):
            self.actions.execute(action, rec)
        self.confirm(rec)
        text = self.actions.execute(action, rec)
        req = json.loads(next((self.root / 'meow-requests').glob('*.json')).read_text())
        self.assertIs(req['after_build'], True)
        self.assertEqual(req['attempt'], 3)
        self.assertEqual(req['_state'], 'building')
        self.assertEqual(req['thread_id'], '99')
        self.assertEqual(req['requester_id'], '1')
        self.assertIn('local tests were already enough', req['audit'])
        self.assertEqual(self.st['meow-queue'][0]['request_id'], req['id'])
        self.assertEqual(text, 'Force queued for #31 queen-hunt: skip the remaining tests and open the candidate '
                         'automatically when this rebuild and its replay check finish. '
                         "You don't need to come back. I'll post the result here.")

    def test_progress_during_confirmation_is_accepted(self):
        rec = self.prepare()
        self.card['labels'][0]['name'] = 'status:needs-look'
        self.confirm(rec)
        self.actions.execute(rec['prepared'][0], rec)
        self.assertEqual(len(list((self.root / 'meow-requests').glob('*.json'))), 1)

    def test_revision_failure_and_body_change_still_block(self):
        rec = self.prepare()
        for meta, message in [({'attempt': 4}, 'new build attempt'),
                              ({'attempt': 3, 'failed': True}, 'build failed')]:
            self.meta(**meta)
            with self.assertRaisesRegex(ValueError, message):
                self.actions.gate(rec['prepared'][0], rec)
        self.meta(attempt=3)
        self.card['body'] = 'A different plan'
        with self.assertRaisesRegex(ValueError, 'Card changed'):
            self.actions.gate(rec['prepared'][0], rec)

    def test_other_forces_and_ordinary_actions_unchanged(self):
        for force, target in [(False, 'candidate'), (True, 'testing')]:
            self.assertNotIn('_after_build', self.prepare(force, target)['prepared'][0])
        self.card['labels'][0]['name'] = 'status:tested'
        rec = self.prepare()
        self.assertNotIn('_after_build', rec['prepared'][0])
        self.confirm(rec)
        self.actions.execute(rec['prepared'][0], rec)
        req = json.loads(next((self.root / 'meow-requests').glob('*.json')).read_text())
        self.assertNotIn('after_build', req)
        self.assertNotIn('attempt', req)

    def test_model_cannot_supply_its_own_attempt(self):
        with self.assertRaisesRegex(ValueError, 'Invalid fields'):
            chat.validate_plan({'actions': [dict(action='set_state', card=31, state='candidate',
                                                 force=True, after_build=True, attempt=2)]}, 1, self.api.MEMBERS)

    def test_result_is_posted_once_in_request_thread(self):
        self.st['meow-queue'] = [dict(request_id='request-1', thread_id='99')]
        path = self.root / 'meow-results/request-1.json'
        path.parent.mkdir()
        path.write_text(json.dumps({'ok': True, 'message': 'Applied set_state to #31.\n\nAudit'}))
        ui = MeowUI.__new__(MeowUI)
        ui.api, ui.st, ui.state = self.api, self.st, {'channel': object()}
        ui.send = AsyncMock()
        channel = object()
        client = types.SimpleNamespace(get_channel=Mock(return_value=channel))
        asyncio.run(ui.poll(client))
        asyncio.run(ui.poll(client))
        ui.send.assert_awaited_once_with(channel, '✅ Applied set_state to #31.\n\nAudit')

    def test_prompt_says_queue_now_and_explain_timing(self):
        result = types.SimpleNamespace(returncode=0, stdout=json.dumps({
            'result': 'Ready', 'session_id': '12345678-abcd-1234-abcd-123456789012'}))
        with patch.object(chat, 'build_brain', return_value='fixture'), \
                patch.object(chat.subprocess, 'run', return_value=result) as run:
            chat.session_call(self.api, 'force #31')
        prompt = run.call_args.kwargs['input']
        self.assertIn('Do not ask them to ask again later', prompt)
        self.assertIn('say what will happen and when', prompt)


if __name__ == '__main__':
    unittest.main()
