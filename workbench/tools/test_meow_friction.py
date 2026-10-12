"""One-click offers, single-confirm Force, typed commands and proxy moves; Discord, GitHub and Claude are fakes."""
import asyncio
import contextlib
import copy
import datetime as dt
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

import decision_nudge
import meow_chat as chat
import meow_offer
import meowbot as api
import tasks

JUN, ZHE, QWQ = list(api.MEMBERS)
FORCE_39 = {'actions': [{'action': 'set_state', 'card': 39, 'state': 'candidate', 'force': True}]}
WORDS = 'merge #39 directly (tests are done)'


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
    return types.SimpleNamespace(
        ui=types.SimpleNamespace(View=FakeView, Modal=FakeView, Button=FakeItem, TextInput=FakeItem, Select=FakeItem),
        TextStyle=types.SimpleNamespace(short=1), ButtonStyle=types.SimpleNamespace(success=1, secondary=2),
        SelectOption=FakeItem, Object=lambda id: id,
        AllowedMentions=type('AllowedMentions', (), {'__init__': lambda self, **kw: self.__dict__.update(kw),
                                                     'none': staticmethod(lambda: None)}))


def interaction(uid, channel):
    return types.SimpleNamespace(user=types.SimpleNamespace(id=uid), channel=channel,
        response=types.SimpleNamespace(send_message=AsyncMock(), send_modal=AsyncMock(), edit_message=AsyncMock()),
        followup=types.SimpleNamespace(send=AsyncMock()))


def said(uid, channel, content, bot=False):
    return types.SimpleNamespace(author=types.SimpleNamespace(id=uid, bot=bot), channel=channel, content=content,
                                 reply=AsyncMock(), create_thread=AsyncMock(return_value=Channel(555)))


class Friction(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.addCleanup(patch.stopall)
        for name, value in (('LOOK_DIR', str(self.root / 'look')), ('OFFER_DIR', str(self.root / 'offers'))):
            patch.object(api, name, value).start()
        patch.object(api, 'save_state').start()
        self.comment = patch.object(api, 'gh_comment').start()
        patch.object(api, 'gh', side_effect=AssertionError('GitHub')).start()
        patch('subprocess.run', side_effect=AssertionError('External call')).start()
        self.model = patch.object(chat, 'session_call', side_effect=AssertionError('model')).start()
        self.channel = Channel()
        self.st = {'meow_threads': {}}
        self.ui = api.SnoozeMeowUI(api, discord_fake(), self.st, {'channel': self.channel}, asyncio.Lock(), asyncio.Lock())
        self.card = {'number': 39, 'title': '[Idea] Queen safety', 'body': 'Approved plan', 'state': 'OPEN',
                     'labels': [{'name': 'status:tested'}, {'name': 'by:zhe'}, {'name': 'name:queen-safety'}]}
        self.ui.actions.card = lambda number: copy.deepcopy(self.card)
        self.ui.actions.transition = Mock()
        self.client = types.SimpleNamespace(get_channel=lambda n: self.channel)

    def status(self, value):
        self.card['labels'][0]['name'] = 'status:' + value

    def spooled(self):
        return [json.loads(p.read_text()) for p in (self.root / 'look/meow-requests').glob('*.json')]

    async def drop(self, good_reason=WORDS, **over):
        data, _ = meow_offer.build('Zhe', 'ok, this is yours to confirm', FORCE_39, good_reason)
        data.update(over)
        meow_offer.write(data, api.OFFER_DIR)
        await self.ui.outside_offers(self.client)
        result = json.loads((self.root / 'offers/handled' / (data['id'] + '.result.json')).read_text())
        rec = self.st.get('meow_confirmations', {}).get(result.get('confirmation'))
        return result, rec

    def last_view(self):
        return self.channel.messages[-1][1]['view']

    # 1. an outside offer is confirmable only by its named member
    async def test_offer_waits_for_the_named_member_only(self):
        result, rec = await self.drop()
        self.assertEqual(result['status'], 'posted')
        self.assertEqual((rec['requester_id'], rec['stage']), (str(ZHE), 'final'))
        self.assertEqual(self.spooled(), [])
        await self.ui.poll(self.client)
        await self.ui.outside_offers(self.client)
        self.assertEqual(self.spooled(), [], 'polling must never apply an offer')
        view = self.last_view()
        for other in (JUN, QWQ, 0):
            it = interaction(other, self.channel)
            await view.confirm(it)
            self.assertRegex(it.response.send_message.call_args.args[0], 'Only the requester|another member')
            self.assertEqual(rec['stage'], 'final')
            await view.cancel(interaction(other, self.channel))
            self.assertEqual(rec['stage'], 'final')
        self.assertEqual(self.spooled(), [])
        await view.confirm(interaction(ZHE, self.channel))
        request, = self.spooled()
        self.assertEqual((request['requester_id'], request['state'], request['force']), (str(ZHE), 'candidate', True))
        self.assertEqual(rec['stage'], 'done')

    # 2. a forced offer shows one confirm button and records the given reason
    async def test_forced_offer_is_one_click_with_the_given_reason(self):
        _, rec = await self.drop()
        text, kw = self.channel.messages[-1]
        self.assertEqual([item.label for item in kw['view'].children], ['Confirm', 'Cancel'])
        self.assertEqual(kw['allowed_mentions'].users, [ZHE])
        self.assertTrue(text.startswith(f'<@{ZHE}> ok, this is yours to confirm\n'))
        self.assertIn('Force for #39 queen-safety: skip the remaining tests and open the candidate.', text)
        self.assertIn(f'Recorded reason: "{WORDS}"', text)
        self.assertIn('Only Zhe can confirm, until <t:', text)
        it = interaction(ZHE, self.channel)
        await kw['view'].confirm(it)
        it.response.send_modal.assert_not_called()
        self.assertEqual((rec['stage'], rec['reason']), ('done', WORDS))
        self.assertIn(f'⚠️ forced by Zhe: {WORDS}', self.spooled()[0]['audit'])
        notices = [t for t, _ in self.channel.messages if f'⚠️ forced by Zhe: {WORDS}' in t and 'Result: done' in t]
        self.assertEqual(len(notices), 1)
        self.assertFalse(any('view' in kw for _, kw in self.channel.messages[1:]), 'no second confirmation')
        await kw['view'].confirm(interaction(ZHE, self.channel))
        self.assertEqual(len(self.spooled()), 1)

    async def test_forced_offer_without_reason_asks_the_member_for_it(self):
        _, rec = await self.drop(good_reason=None)
        self.assertEqual(rec['stage'], 'review')
        it = interaction(ZHE, self.channel)
        await self.last_view().confirm(it)
        self.assertEqual(self.spooled(), [])
        self.assertTrue(it.response.send_modal.called)

    # 3. an expired or stale offer is refused
    async def test_expired_offer_is_refused_before_and_after_posting(self):
        old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=12, minutes=1)).isoformat()
        result, rec = await self.drop(created=old)
        self.assertEqual((result['status'], rec), ('refused', None))
        self.assertIn('expired', result['error'])
        self.assertEqual(self.channel.messages, [])
        _, rec = await self.drop()
        self.assertEqual(rec['ttl'], 12 * 3600)
        rec['created'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=11, minutes=59)).isoformat()
        self.assertEqual(chat.advance(copy.deepcopy(rec), ZHE, 'confirm'), 'executing')
        rec['created'] = old
        it = interaction(ZHE, self.channel)
        await self.last_view().confirm(it)
        self.assertIn('expired', it.response.send_message.call_args.args[0])
        self.assertEqual(self.spooled(), [])

    async def test_card_change_after_the_offer_is_refused_at_click(self):
        for change in ('body', 'state'):
            with self.subTest(change=change):
                self.card.update(body='Approved plan')
                self.status('tested')
                _, rec = await self.drop()
                if change == 'body':
                    self.card['body'] = 'A different plan'
                else:
                    self.status('rejected')
                await self.last_view().confirm(interaction(ZHE, self.channel))
                self.assertEqual(rec['stage'], 'uncertain')
                self.assertIn('Card changed after preview', self.channel.messages[-2][0])
                self.assertEqual(self.spooled(), [])

    async def test_build_checks_still_run_for_an_offer_made_during_a_build(self):
        meta = self.root / 'look/card-39/card.json'
        meta.parent.mkdir(parents=True)
        for later, message in (({'attempt': 4}, 'new build attempt'), ({'attempt': 3, 'failed': True}, 'build failed')):
            with self.subTest(message=message):
                self.status('building')
                meta.write_text(json.dumps({'attempt': 3}))
                _, rec = await self.drop()
                self.assertIn('happens by itself when this rebuild', self.channel.messages[-1][0])
                meta.write_text(json.dumps(later))
                self.status('needs-look')
                await self.last_view().confirm(interaction(ZHE, self.channel))
                self.assertEqual(rec['stage'], 'uncertain')
                self.assertIn(message, self.channel.messages[-2][0])
                self.assertEqual(self.spooled(), [])

    async def test_a_file_cannot_stand_in_for_the_click(self):
        ahead = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=3)).isoformat()
        _, rec = await self.drop(created=ahead)
        self.assertLessEqual(chat.expires(rec), dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=12, seconds=5))
        for extra in ({'stage': 'executing'}, {'ttl': 10 ** 9}, {'requester_id': str(ZHE)}, {'prepared': []},
                      {'member': 'meowbot'}, {'member': 'everyone'}, {'id': 'x' * 32},
                      {'plan': {'actions': [dict(FORCE_39['actions'][0], requester_id=str(JUN))]}},
                      {'plan': {'actions': [{'action': 'shell', 'command': 'true'}]}},
                      {'plan': {'actions': []}}, {'thread': '123456789'}, {'reason': 'two\nlines'}):
            with self.subTest(extra=extra):
                before = len(self.channel.messages)
                result, rec = await self.drop(**extra)
                self.assertEqual((result['status'], rec, len(self.channel.messages)), ('refused', None, before))
        self.assertEqual(self.spooled(), [])
        self.assertTrue(all(r['stage'] in {'final', 'review', 'cancelled'} for r in self.st['meow_confirmations'].values()))

    async def test_an_offer_is_posted_once_and_merge_offers_keep_the_short_window(self):
        data, _ = meow_offer.build('Zhe', 'yours', FORCE_39, WORDS)
        for _ in range(2):
            meow_offer.write(data, api.OFFER_DIR)
            await self.ui.outside_offers(self.client)
        self.assertEqual(len(self.channel.messages), 1)
        for plan in ({'actions': [{'action': 'vote', 'candidate': '#46', 'vote': 'OK', 'force': True}]},
                     {'actions': [{'action': 'submit', 'ref': 'main'}]}):
            self.assertEqual(chat.check_offer(meow_offer.build('QWQ', 'yours', plan)[0], api.MEMBERS)['ttl'], 2 * 3600)

    async def test_failed_runner_result_for_a_channel_offer_is_posted_once(self):
        _, rec = await self.drop()
        await self.last_view().confirm(interaction(ZHE, self.channel))
        request, = self.spooled()
        path = self.root / 'look/meow-results' / (request['id'] + '.json')
        path.parent.mkdir()
        path.write_text(json.dumps({'ok': False, 'message': 'Card moved after confirmation; request a fresh preview.'}))
        posted = len(self.channel.messages)
        await self.ui.poll(self.client)
        await self.ui.poll(self.client)
        self.assertEqual([t for t, _ in self.channel.messages[posted:]],
                         ['⚠️ Card moved after confirmation; request a fresh preview.'])

    # 4. /meow force typed by a person: one confirm, the message is the reason
    async def test_meow_force_needs_one_confirm_and_records_the_message(self):
        message = 'force set_state 39 candidate'
        await self.ui.conversation(self.channel, QWQ, message)
        text, kw = self.channel.messages[-1]
        rec, = self.st['meow_confirmations'].values()
        self.assertEqual((rec['stage'], rec['reason'], rec['ttl']), ('final', message, 2 * 3600))
        self.assertIn(f'Recorded reason: "{message}"', text)
        self.assertEqual([item.label for item in kw['view'].children], ['Confirm', 'Cancel'])
        await kw['view'].confirm(interaction(ZHE, self.channel))
        self.assertEqual(self.spooled(), [])
        it = interaction(QWQ, self.channel)
        await kw['view'].confirm(it)
        it.response.send_modal.assert_not_called()
        self.assertEqual(rec['stage'], 'done')
        self.assertIn(f'⚠️ forced by QWQ: {message}', self.spooled()[0]['audit'])
        self.assertTrue(any(f'⚠️ forced by QWQ: {message}' in t and 'Result: done' in t for t, _ in self.channel.messages))

    async def test_meow_force_reason_is_trimmed_and_the_window_is_two_hours(self):
        long = 'just merge #39,\nno more tests ' + 'x' * 400
        self.model.side_effect = None
        self.model.return_value = ('On it.\n```json\n' + json.dumps(FORCE_39) + '\n```', '12345678-abcd-1234-abcd-123456789012')
        self.st['meow_threads']['99'] = {'session': None}
        await self.ui.conversation(self.channel, ZHE, long)
        rec, = self.st['meow_confirmations'].values()
        self.assertEqual(rec['reason'], ' '.join(long.split())[:300])
        self.assertEqual(len(rec['reason']), 300)
        rec['created'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=119)).isoformat()
        self.assertEqual(chat.advance(copy.deepcopy(rec), ZHE, 'confirm'), 'executing')
        rec['created'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=121)).isoformat()
        with self.assertRaisesRegex(ValueError, 'expired'):
            chat.advance(rec, ZHE, 'confirm')

    async def test_force_button_reason_form_is_the_last_step(self):
        it = interaction(JUN, self.channel)
        await self.ui.force(it, {'action': 'set_state', 'card': 39, 'state': 'candidate'})
        rec, = self.st['meow_confirmations'].values()
        view = self.last_view()
        first = interaction(JUN, self.channel)
        await view.confirm(first)
        self.assertEqual((rec['stage'], self.spooled()), ('reason', []))
        again = interaction(JUN, self.channel)
        await view.confirm(again)
        self.assertTrue(again.response.send_modal.called, 'a closed form can be reopened')
        modal = again.response.send_modal.call_args.args[0]
        stranger = interaction(ZHE, self.channel)
        modal.reason.value = 'not mine'
        await modal.on_submit(stranger)
        self.assertEqual((rec['stage'], self.spooled()), ('reason', []))
        modal.reason.value = 'local tests were enough'
        posted = len(self.channel.messages)
        await asyncio.gather(modal.on_submit(interaction(JUN, self.channel)), modal.on_submit(interaction(JUN, self.channel)))
        self.assertEqual((rec['stage'], rec['reason']), ('done', 'local tests were enough'))
        self.assertEqual(len(self.spooled()), 1)
        self.assertFalse(any('view' in kw for _, kw in self.channel.messages[posted:]), 'no Final confirm')

    # 5. a non-author member's ordinary move is accepted
    async def test_non_author_ordinary_move_is_accepted(self):
        for state, target in (('tested', 'candidate'), ('tested', 'rejected'), ('needs-info', 'building'),
                              ('needs-look', 'testing')):
            for member in (JUN, QWQ):
                with self.subTest(state=state, member=member):
                    self.status(state)
                    self.ui.actions.transition.reset_mock()
                    rec = chat.new_confirmation({'actions': [{'action': 'set_state', 'card': 39, 'state': target}]},
                                                member, 99, api.MEMBERS)
                    self.ui.actions.prepare(rec)
                    chat.advance(rec, member, 'confirm')
                    self.ui.actions.execute(rec['prepared'][0], rec)
                    self.ui.actions.transition.assert_called_once_with(39, target)
        self.status('tested')
        rec = chat.new_confirmation({'actions': [{'action': 'set_state', 'card': 39, 'state': 'kept'}]}, JUN, 99, api.MEMBERS)
        self.ui.actions.prepare(rec)
        with self.assertRaisesRegex(ValueError, 'skips a workflow gate'):
            self.ui.actions.gate(rec['prepared'][0], rec)

    # 6. commands typed as ordinary messages
    async def test_plain_message_answer_is_posted_as_the_author(self):
        url = 'https://github.com/forrest-gan2005/battlecode/issues/39#issuecomment-1'
        for content, text in (('/answer card:39 text:looks right', 'looks right'), ('/answer 39 ship it', 'ship it'),
                              ('/Answer #39: revise: keep two tiles', 'revise: keep two tiles')):
            with self.subTest(content=content):
                message = said(ZHE, self.channel, content)
                with patch.object(api, 'gh', side_effect=[{'state': 'open', 'title': '[Idea] Queen safety'},
                                                          {'html_url': url}]) as gh:
                    self.assertTrue(await api.typed_answer(message, self.channel))
                self.assertEqual(gh.call_args_list[1].args[0][-1], f'body=Answer from Zhe: {text}')
                self.assertEqual(self.channel.messages[-1][0], f'💬 Zhe answered #39 Queen safety: {text}\n{url}')
                message.reply.assert_not_called()
        for content in ('/answer looks right', '/answer 390', '/answer'):
            message = said(ZHE, self.channel, content)
            self.assertTrue(await api.typed_answer(message, self.channel))
            self.assertIn('Which card?', message.reply.call_args.args[0])
        for message in (said(0, self.channel, '/answer 39 yes'), said(ZHE, Channel(7), '/answer 39 yes'),
                        said(ZHE, self.channel, '/answer 39 yes', bot=True), said(ZHE, self.channel, 'answer 39 yes'),
                        said(ZHE, self.channel, '/answers 39 yes')):
            self.assertFalse(await api.typed_answer(message, self.channel))

    async def test_plain_message_meow_runs_as_the_author(self):
        message = said(QWQ, self.channel, '/meow force set_state 39 candidate')
        await self.ui.followup(message)
        thread = message.create_thread.return_value
        self.assertIn('555', self.st['meow_threads'])
        rec, = self.st['meow_confirmations'].values()
        self.assertEqual((rec['requester_id'], rec['thread_id'], rec['stage']), (str(QWQ), '555', 'final'))
        self.assertEqual(rec['reason'], 'force set_state 39 candidate')
        self.assertEqual(self.spooled(), [], 'typing the command still needs the Confirm click')
        await thread.messages[-1][1]['view'].confirm(interaction(QWQ, thread))
        self.assertEqual(len(self.spooled()), 1)

    async def test_plain_message_meow_snooze_queue_and_ordinary_chat(self):
        with patch.object(api, 'snooze_action', return_value='⏸ quiet') as snooze:
            await self.ui.followup(said(ZHE, self.channel, '/meow 39 still deciding'))
        self.assertEqual(snooze.call_args.args[1], ZHE)
        self.assertEqual(self.channel.messages[-1][0], '⏸ quiet')
        await self.ui.followup(said(ZHE, self.channel, '/meow queue'))
        self.assertEqual(self.channel.messages[-1][0], 'No pending /meow requests.')
        posted = len(self.channel.messages)
        for message in (said(ZHE, self.channel, 'just merge it'), said(0, self.channel, '/meow pause runner'),
                        said(ZHE, Channel(7), '/meow pause runner'), said(ZHE, self.channel, '/meow pause runner', bot=True),
                        said(ZHE, self.channel, '/meow')):
            await self.ui.followup(message)
            message.create_thread.assert_not_called()
        self.assertEqual(len(self.channel.messages), posted)
        self.assertEqual(self.st.get('meow_confirmations', {}), {})


class Wording(unittest.TestCase):
    def test_syntax_is_offered_not_demanded(self):
        issue = {'number': 39, 'title': '[Idea] Queen safety', 'html_url': 'https://example.invalid/39',
                 'labels': [{'name': 'by:zhe'}, {'name': 'name:queen-safety'}]}
        with patch.object(api, 'outcome_line', return_value=''):
            texts = [api.state_message(39, {'issue': issue, 'status': status})
                     for status in ('needs-info', 'needs-look', 'tested')]
        now = dt.datetime(2026, 10, 6, 3, tzinfo=dt.timezone.utc)
        texts.append(decision_nudge.text(now, [(90, 39, 'queen-safety', ('Zhe', ZHE, 2), 'replay check')]))
        texts.append(tasks.FOOTER)
        for text in texts:
            self.assertIn('in your own words, or use /answer card:', text)
            self.assertNotIn('reply with /answer', text)
            self.assertNotIn('decide with /answer', text)
        self.assertIn('ship it, drop it, or say what to revise', texts[2])


class OfferCli(unittest.TestCase):
    def test_build_runs_the_meow_plan_validation(self):
        data, offer = meow_offer.build('zhe', 'yours', FORCE_39, WORDS)
        self.assertEqual((offer['member'], offer['reason'], offer['ttl']), (ZHE, WORDS, 12 * 3600))
        self.assertEqual(offer['plan']['actions'][0]['requester_id'], str(ZHE))
        self.assertEqual(meow_offer.build('junsing', 'yours', FORCE_39)[1]['member'], JUN)
        bad = [('Nobody', 'yours', FORCE_39, None), ('Zhe', ' ', FORCE_39, None), ('Zhe', 'x' * 1501, FORCE_39, None),
               ('Zhe', 'yours', {'actions': [{'action': 'delete_issue', 'card': 39}]}, None),
               ('Zhe', 'yours', {'actions': [{'action': 'set_state', 'card': 39, 'state': 'candidate', 'force': 'yes'}]}, None),
               ('Zhe', 'yours', {'actions': [{'action': 'set_state', 'card': 39, 'state': 'candidate'}]}, 'not forced'),
               ('Zhe', 'yours', {'actions': [], 'queue': {'question': 'q', 'human': True}}, None),
               ('Zhe', 'yours', FORCE_39, 'x' * 301), ('Zhe', 'yours', [FORCE_39], None)]
        for case in bad:
            with self.subTest(case=str(case)[:80]), self.assertRaises(ValueError):
                meow_offer.build(*case)

    def test_refused_offer_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            text = Path(directory) / 'text.txt'
            text.write_text('yours')
            argv = ['meow_offer.py', '--to', 'Zhe', '--text-file', str(text)]
            with patch.object(api, 'OFFER_DIR', directory + '/offers'):
                with patch.object(sys, 'argv', argv + ['--plan', '{"actions":[{"action":"shell"}]}']), \
                        contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as stop:
                    meow_offer.main()
                self.assertEqual(stop.exception.code, 1)
                self.assertIn('Offer refused', err.getvalue())
                self.assertFalse(Path(directory, 'offers').exists())
                with patch.object(sys, 'argv', argv + ['--plan', json.dumps(FORCE_39), '--reason', WORDS]), \
                        contextlib.redirect_stdout(io.StringIO()) as out:
                    meow_offer.main()
                self.assertIn('for Zhe: one Confirm, valid 12 h', out.getvalue())
                written, = Path(directory, 'offers').glob('*.json')
                self.assertEqual(json.loads(written.read_text())['reason'], WORDS)


if __name__ == '__main__':
    unittest.main()
