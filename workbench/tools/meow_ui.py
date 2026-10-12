"""Discord adapter for /meow; construction does not start a client or make network calls."""
import asyncio
import json
from pathlib import Path
import re

import meow_chat as core


class MeowUI:
    def __init__(self, api, discord, st, state, approval_lock, release_lock):
        self.api, self.d, self.st, self.state = api, discord, st, state
        self.approval_lock, self.release_lock = approval_lock, release_lock
        self.sessions_lock = asyncio.Lock()
        self.thread_locks = {}
        self.actions = core.Actions(api, st)
        self.views()

    def save(self):
        self.api.save_state(self.st)

    async def send(self, channel, text, **kw):
        for i in range(0, max(1, len(text)), 1800):
            await channel.send(text[i:i + 1800] or 'Done.', allowed_mentions=self.d.AllowedMentions.none(),
                               **(kw if i + 1800 >= len(text) else {}))

    async def thread(self, channel, requester):
        if str(channel.id) in self.st.get('meow_threads', {}):
            return channel
        message = await self.state['channel'].send(f"💬 /meow · {self.api.MEMBERS[requester]}")
        thread = await message.create_thread(name=f'meow · {self.api.MEMBERS[requester]}', auto_archive_duration=1440)
        self.st.setdefault('meow_threads', {})[str(thread.id)] = {'session': None, 'created': core.now()}
        self.save()
        return thread

    async def slash(self, it, message):
        if it.user.id not in self.api.MEMBERS:
            await it.response.send_message('Only team members can use /meow.', ephemeral=True)
            return
        await it.response.send_message('👀 on it…', ephemeral=True)
        if message.strip().lower() == 'queue':
            text = core.queue_text(self.st)
            for start in range(0, len(text), 1800):
                await it.followup.send(text[start:start + 1800], ephemeral=True, allowed_mentions=self.d.AllowedMentions.none())
            return
        thread = await self.thread(it.channel, it.user.id)
        await it.followup.send(f'Continue here: {thread.mention}', ephemeral=True)
        await self.send(thread, f"{self.api.MEMBERS[it.user.id]}: {message}")
        await self.conversation(thread, it.user.id, message)

    async def followup(self, message):
        if message.author.bot or message.author.id not in self.api.MEMBERS:
            return
        if str(message.channel.id) not in self.st.get('meow_threads', {}):
            await self.typed(message)
            return
        if not message.content.strip():
            return
        await self.send(message.channel, '👀 on it…')
        await self.conversation(message.channel, message.author.id, message.content)

    def typed_text(self, message):
        channel = self.state.get('channel')
        match = re.fullmatch(r'(?is)/meow\s+(.+)', message.content.strip())
        if (not match or channel is None or message.channel.id != channel.id
                or message.author.bot or message.author.id not in self.api.MEMBERS):
            return None
        return match[1].strip()

    async def typed(self, message):
        # "/meow …" sent as an ordinary message in #meow; the author is the requester.
        text = self.typed_text(message)
        if not text:
            return False
        if text.lower() == 'queue':
            await self.send(message.channel, core.queue_text(self.st))
            return True
        thread = await message.create_thread(name=f'meow · {self.api.MEMBERS[message.author.id]}',
                                             auto_archive_duration=1440)
        self.st.setdefault('meow_threads', {})[str(thread.id)] = {'session': None, 'created': core.now()}
        self.save()
        await self.send(thread, '👀 on it…')
        await self.conversation(thread, message.author.id, text)
        return True

    async def conversation(self, thread, requester, message):
        lock = self.thread_locks.setdefault(str(thread.id), asyncio.Lock())
        async with lock:
            if message.strip().lower() == 'queue':
                await self.send(thread, core.queue_text(self.st))
                return
            if m := re.fullmatch(r'(?i)queue done ([a-f0-9]{12})', message.strip()):
                row = next((r for r in self.st.get('meow-queue', []) if r['id'] == m[1]), None)
                if row and row['requester_id'] == str(requester) and not row.get('request_id'):
                    row.update(status='done', resolved_by=str(requester))
                    self.save()
                    await self.send(thread, 'Queue item resolved by its requester.')
                else:
                    await self.send(thread, 'Only its requester can resolve a judgment entry; runner requests report their own result.')
                return
            try:
                modal_command = re.fullmatch(r'/?(hypo|hypo-max)(?:\s+(queen|terrain|late-game|economy|infra|other))?', message.strip(), re.I)
                edit_command = re.fullmatch(r'/?board-edit\s+#?(\d+)', message.strip(), re.I)
                if modal_command or edit_command:
                    mode = modal_command[1].lower() if modal_command else 'board-edit'
                    card = int(edit_command[1]) if edit_command else None
                    current = await asyncio.to_thread(self.actions.card, card) if card else None
                    await self.send(thread, 'Open the usual card form; submitting it confirms your changes.',
                                    view=self.CardFormView(requester, mode, modal_command[2] or 'other' if modal_command else 'other', card, current))
                    return
                plan = core.direct_plan(message)
                if plan is None:
                    session = self.st['meow_threads'][str(thread.id)]
                    async with self.sessions_lock:
                        reply, sid = await asyncio.to_thread(core.session_call, self.api,
                            f"Requester: {self.api.MEMBERS[requester]} ({requester})\n{message}", session.get('session'))
                        session['session'] = sid
                        self.save()
                    answer, plan = core.parse_reply(reply, requester, self.api.MEMBERS)
                    if answer:
                        await self.send(thread, answer)
                plan = core.validate_plan(plan, requester, self.api.MEMBERS)
                queue = plan.pop('queue', None)
                if queue:
                    row = core.enqueue(self.st, requester, thread.id, queue['question'], queue['human'])
                    self.save()
                    await self.send(thread, f"Queued `{row['id']}`: {row['question']}")
                    if queue['human']:
                        plan['actions'].append({'action': 'escalate', 'question': queue['question']})
                if plan['actions']:
                    await self.offer(thread, requester, plan, core.message_reason(message))
            except Exception as exc:
                row = core.enqueue(self.st, requester, thread.id, message, error=type(exc).__name__)
                detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
                self.save()
                await self.send(thread, f"Could not complete this request ({detail}). Queued `{row['id']}`. "
                                       'No automatic retry of actions; review the card before retrying.')

    def offer_note(self, rec):
        if not rec['force']:
            return 'Confirm to execute as yourself.'
        if rec.get('reason'):
            return f"Confirm to force this as yourself. Recorded reason: \"{rec['reason']}\""
        return 'Force: confirm, then one line on why. That line is the last step.'

    async def offer(self, thread, requester, plan, reason=None):
        rec = core.new_confirmation(plan, requester, thread.id, self.api.MEMBERS, reason)
        await asyncio.to_thread(self.actions.prepare, rec)
        self.st.setdefault('meow_confirmations', {})[rec['id']] = rec
        self.save()
        await self.send(thread, self.actions.preview(rec) + '\n' + self.offer_note(rec),
                        view=self.ConfirmView(rec['id']))

    async def post_offer(self, client, key, path):
        if path.stat().st_size > 20000:
            raise ValueError('Offer file is too large.')
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or data.get('id') != key:
            raise ValueError('Offer id must match its file name.')
        offer = core.check_offer(data, self.api.MEMBERS)
        target = self.state['channel']
        if offer['thread'] and offer['thread'] != str(target.id):
            if offer['thread'] not in self.st.get('meow_threads', {}):
                raise ValueError('Offers go to #meow or to an existing /meow thread.')
            target = client.get_channel(int(offer['thread'])) or await client.fetch_channel(int(offer['thread']))
        rec = core.new_confirmation(offer['plan'], offer['member'], target.id, self.api.MEMBERS,
                                    offer['reason'], offer['ttl'])
        rec.update(created=offer['created'], offer=key)
        await asyncio.to_thread(self.actions.prepare, rec)
        text = (f"<@{offer['member']}> {offer['text']}\n{self.actions.preview(rec)}\n{self.offer_note(rec)}"
                f"\nOnly {self.api.MEMBERS[offer['member']]} can confirm, until <t:{int(core.expires(rec).timestamp())}:t>.")
        if len(text) > 1900:
            raise ValueError('Offer text and preview are too long for one message.')
        self.st.setdefault('meow_confirmations', {})[rec['id']] = rec
        self.save()
        try:
            await target.send(text, view=self.ConfirmView(rec['id']), allowed_mentions=self.d.AllowedMentions(
                users=[self.d.Object(id=offer['member'])], roles=False, everyone=False))
        except Exception:
            rec['stage'] = 'cancelled'
            raise
        return rec

    async def outside_offers(self, client):
        """Post offers left by tools/meow_offer.py. A file only proposes: its plan is validated again
        here and then waits for the named member's own click, like any /meow plan."""
        box = Path(self.api.OFFER_DIR)
        seen = self.st.setdefault('meow_offers', {})
        for path in sorted(box.glob('*.json')):
            key = path.stem
            if key not in seen:
                # Claimed before posting, so a crash can lose an offer but never post it twice.
                seen[key] = {'at': core.now(), 'status': 'refused', 'error': 'Interrupted before posting.'}
                self.save()
                try:
                    rec = await self.post_offer(client, key, path)
                    seen[key] = {'at': seen[key]['at'], 'status': 'posted', 'confirmation': rec['id']}
                except Exception as exc:
                    seen[key]['error'] = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
                self.save()
            done = box / 'handled'
            done.mkdir(parents=True, exist_ok=True)
            (done / (key + '.result.json')).write_text(json.dumps({'id': key, **seen[key]}, ensure_ascii=False, indent=2))
            path.replace(done / path.name)

    async def force(self, it, action):
        if it.user.id not in self.api.MEMBERS:
            await it.response.send_message('Only team members can force.', ephemeral=True)
            return
        await it.response.send_message('👀 on it…', ephemeral=True)
        try:
            thread = await self.thread(it.channel, it.user.id)
            await self.offer(thread, it.user.id, {'actions': [dict(action, force=True)]})
            await it.followup.send(f'Confirm here: {thread.mention}', ephemeral=True)
        except Exception as exc:
            await it.followup.send(f'Could not prepare Force ({type(exc).__name__}); no action executed.', ephemeral=True)

    async def execute(self, rec, thread):
        async with self.approval_lock, self.release_lock:
            rec['stage'] = 'executing'
            self.save()
            try:
                for i, action in enumerate(rec['prepared']):
                    rec['index'] = i
                    self.save()
                    result = await asyncio.to_thread(self.actions.execute, action, rec)
                    rec.setdefault('results', []).append(result)
                    self.save()
                    await self.send(thread, result + self.audit_tail(rec))
                    if action['action'] == 'escalate':
                        mentions = ' '.join(f'<@{uid}>' for uid in self.api.MEMBERS)
                        await self.state['channel'].send(mentions + '\n' + result + '\n' + core.audit_line(rec, self.api.MEMBERS),
                                                        allowed_mentions=self.d.AllowedMentions(users=[self.d.Object(id=uid) for uid in self.api.MEMBERS], roles=False, everyone=False))
                rec['stage'] = 'done'
            except Exception as exc:
                rec.update(stage='uncertain', error=type(exc).__name__)
                detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
                row = core.enqueue(self.st, int(rec['requester_id']), rec['thread_id'],
                                   f"Review action {rec.get('index', 0) + 1} in confirmation {rec['id']}: {type(exc).__name__}", True)
                await self.send(thread, f"Stopped; `{row['id']}` needs review ({detail}). "
                                       'Check the card/PR before retrying; earlier actions may have completed.'
                                       + self.audit_tail(rec))
            finally:
                self.save()
                if rec['force'] and not rec.get('force_notice'):
                    await self.send(self.state['channel'], self.force_notice(rec))
                    rec['force_notice'] = True
                    self.save()

    def public(self, rec):
        return str(rec['thread_id']) == str(self.state['channel'].id)

    def audit_tail(self, rec):
        # In #meow itself the force notice right below already carries the audit line.
        return '' if rec['force'] and self.public(rec) else '\n' + core.audit_line(rec, self.api.MEMBERS)

    def force_notice(self, rec):
        return (core.audit_line(rec, self.api.MEMBERS) + f"\nResult: {rec['stage']}"
                + ('' if self.public(rec) else f" · <#{rec['thread_id']}>"))

    async def poll(self, client):
        for rec in list(self.st.get('meow_confirmations', {}).values()):
            if rec.get('force') and rec['stage'] in {'done', 'uncertain'} and not rec.get('force_notice'):
                await self.send(self.state['channel'], self.force_notice(rec))
                rec['force_notice'] = True
                self.save()
            if rec.get('audit_pending'):
                await asyncio.to_thread(self.actions.flush_audit, rec)
        for row in self.st.get('meow-queue', []):
            if not row.get('request_id') or row.get('notified'):
                continue
            path = Path(self.api.LOOK_DIR) / 'meow-results' / (row['request_id'] + '.json')
            try:
                result = json.loads(path.read_text())
            except (OSError, ValueError):
                continue
            text = ('✅ ' if result['ok'] else '⚠️ ') + result['message']
            channel = client.get_channel(int(row['thread_id'])) or await client.fetch_channel(int(row['thread_id']))
            await self.send(channel, text)
            if not result['ok'] and not self.public(row):
                await self.send(self.state['channel'], text)
            row.update(status='done' if result['ok'] else 'needs-review', notified=True, result=result)
            self.save()

    def restore(self, client):
        for rec in list(self.st.get('meow_confirmations', {}).values()):
            if rec['stage'] in {'review', 'reason', 'final'}:
                client.add_view(self.ConfirmView(rec['id']))
            elif rec['stage'] == 'executing':
                rec['stage'] = 'uncertain'
                core.enqueue(self.st, int(rec['requester_id']), rec['thread_id'],
                             f"Interrupted action {rec['id']}; inspect card/PR before retrying", True)
        self.save()

    def views(self):
        ui, d = self, self.d

        class ReasonModal(d.ui.Modal):
            def __init__(self, key):
                super().__init__(title='I take responsibility', timeout=600)
                self.key = key
                self.reason = d.ui.TextInput(label='I take responsibility: …', style=d.TextStyle.short,
                                             required=True, max_length=300)
                self.add_item(self.reason)

            async def on_submit(self, it):
                rec = ui.st['meow_confirmations'][self.key]
                try:
                    core.advance(rec, it.user.id, 'reason', self.reason.value)
                    ui.save()
                except ValueError as exc:
                    await it.response.send_message(str(exc), ephemeral=True)
                    return
                await it.response.send_message('👀 on it…', ephemeral=True)
                await ui.execute(rec, it.channel)

        class ConfirmView(d.ui.View):
            def __init__(self, key):
                super().__init__(timeout=None)
                self.key = key
                rec = ui.st['meow_confirmations'][key]
                # A closed reason form is reopened from the same Confirm button.
                self.expected_stage = 'review' if rec['stage'] == 'reason' else rec['stage']
                yes = d.ui.Button(label='Confirm', style=d.ButtonStyle.success,
                                  custom_id=f'meow:{key}:{self.expected_stage}:yes')
                no = d.ui.Button(label='Cancel', style=d.ButtonStyle.secondary,
                                 custom_id=f'meow:{key}:{self.expected_stage}:no')
                yes.callback, no.callback = self.confirm, self.cancel
                self.add_item(yes)
                self.add_item(no)

            async def act(self, it, event):
                rec = ui.st['meow_confirmations'][self.key]
                try:
                    stages = {'review', 'reason'} if self.expected_stage == 'review' else {self.expected_stage}
                    if it.user.id not in ui.api.MEMBERS or rec['stage'] not in stages:
                        raise ValueError('This confirmation was already handled or belongs to another member.')
                    stage = core.advance(rec, it.user.id, event)
                    ui.save()
                except ValueError as exc:
                    await it.response.send_message(str(exc), ephemeral=True)
                    return
                if stage == 'reason':
                    await it.response.send_modal(ReasonModal(self.key))
                elif stage == 'cancelled':
                    await it.response.edit_message(content='Cancelled.', view=None)
                else:
                    await it.response.send_message('👀 on it…', ephemeral=True)
                    await ui.execute(rec, it.channel)

            async def confirm(self, it):
                await self.act(it, 'confirm')

            async def cancel(self, it):
                await self.act(it, 'cancel')

        class CardForceView(d.ui.View):
            def __init__(self, card):
                super().__init__(timeout=None)
                select = d.ui.Select(placeholder='Force a state (author wait / skip checks / override verdict)',
                                    custom_id=f'meow-force-state:{card}',
                                    options=[d.SelectOption(label='Force → ' + s, value=s) for s in sorted(core.STATES)])
                async def choose(it):
                    await ui.force(it, {'action': 'set_state', 'card': card, 'state': select.values[0]})
                select.callback = choose
                self.add_item(select)

        class CardModal(d.ui.Modal):
            def __init__(self, requester, mode, area, card=None, current=None):
                super().__init__(title=('Edit ' + ui.api.card_ref(current))[:45] if card else 'New hypothesis', timeout=900)
                self.requester, self.mode, self.area, self.card = requester, mode, area, card
                sec = ui.api.parse_card(current['body']) if current else {}
                defaults = {'title': (ui.api.board_card_title(current['title'])[:94] + (' | name:' + ui.api.card_name(current) if ui.api.card_name(current) else '')) if current else ''}
                defaults.update({k: sec.get(h, '') for k, h in ui.api.CARD})
                self.fields = {}
                for key, label in [('title', 'Title | name:short-name (optional)'), *ui.api.CARD]:
                    item = d.ui.TextInput(label=label, default=defaults.get(key, '')[:1500] or None,
                                          required=key in {'title', 'claim'}, max_length=120 if key == 'title' else 1500,
                                          style=d.TextStyle.short if key == 'title' else d.TextStyle.paragraph)
                    self.fields[key] = item
                    self.add_item(item)

            async def on_submit(self, it):
                if it.user.id != self.requester or it.user.id not in ui.api.MEMBERS:
                    await it.response.send_message('Only the requester can submit this form.', ephemeral=True)
                    return
                await it.response.send_message('👀 on it…', ephemeral=True)
                fields = {k: v.value.strip() for k, v in self.fields.items()}
                if ' | name:' in fields['title']:
                    fields['title'], fields['name'] = map(str.strip, fields['title'].rsplit(' | name:', 1))
                    if not ui.api.valid_slug(fields['name']):
                        await ui.send(it.channel, 'Name must be 1–2 lowercase words, hyphenated, at most 16 characters.')
                        return
                fields['area'] = self.area
                action = {'action': self.mode, 'fields': fields}
                if self.card:
                    action['card'] = self.card
                try:
                    rec = core.new_confirmation({'actions': [action]}, self.requester, it.channel.id, ui.api.MEMBERS)
                    await asyncio.to_thread(ui.actions.prepare, rec)
                    rec['stage'] = 'executing'
                    ui.st.setdefault('meow_confirmations', {})[rec['id']] = rec
                    ui.save()
                    await ui.execute(rec, it.channel)
                except Exception as exc:
                    await ui.send(it.channel, f'Could not apply this form ({type(exc).__name__}); review the card before retrying.')

        class CardFormView(d.ui.View):
            def __init__(self, requester, mode, area, card=None, current=None):
                super().__init__(timeout=900)
                button = d.ui.Button(label='Open card form', style=d.ButtonStyle.success)
                async def open_form(it):
                    if it.user.id != requester or it.user.id not in ui.api.MEMBERS:
                        await it.response.send_message('Only the requester can use this form.', ephemeral=True)
                        return
                    await it.response.send_modal(CardModal(requester, mode, area, card, current))
                button.callback = open_form
                self.add_item(button)

        self.CardFormView = CardFormView
        self.ConfirmView, self.ReasonModal, self.CardForceView = ConfirmView, ReasonModal, CardForceView
