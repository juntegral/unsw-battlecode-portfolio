import ast, asyncio, copy, importlib.util, json, pathlib, types
from unittest.mock import AsyncMock, Mock, patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('meowbot_states', ROOT / 'tools/meowbot.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
checks = []


def ok(name):
    checks.append(name)
    print('PASS', name)


def forbidden(*args, **kwargs):
    raise AssertionError('Unexpected external operation')


def issue(number=7, author='by:zhe', title='[Idea] Fixture'):
    return {'number': number, 'title': title, 'html_url': f'https://example.invalid/issues/{number}',
            'labels': [{'name': author}] if author else []}


def event(eid, status, action='labeled', card=None):
    # GitHub's payload.label is unreliable; the card's own labels carry the state.
    card = dict(card or issue())
    card['labels'] = [l for l in card.get('labels', []) if not l['name'].startswith('status:')]
    if action == 'labeled':
        card['labels'] = card['labels'] + [{'name': 'status:' + status}]
    return {'id': str(eid), 'type': 'IssuesEvent',
            'payload': {'action': action, 'issue': card, 'label': {'name': 'name:whatever'}}}


def events(st, fixtures):
    with patch.object(m, 'gh', return_value=list(reversed(fixtures))):
        return m.new_events(st)


class Calls:
    def __init__(self): self.calls = []
    async def defer(self, **kw): self.calls.append(kw)
    async def send(self, **kw): self.calls.append(kw)


class Interaction:
    def __init__(self): self.response, self.followup = Calls(), Calls()


TREE = ast.parse((ROOT / 'tools/meowbot.py').read_text())
RUN = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == 'run_bot')
BOT = next(n for n in RUN.body if isinstance(n, ast.ClassDef) and n.name == 'Bot')
SETUP = next(n for n in BOT.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'setup_hook')


def command_env(ideas, loops=None, results=None):
    ns = dict(vars(m))
    async def member(it): return True
    ns.update(member=member, discord=types.SimpleNamespace(Interaction=Interaction,
              Embed=types.SimpleNamespace(from_dict=lambda x: x)),
              board_state=lambda: copy.deepcopy(ideas), loop_status=lambda: (copy.deepcopy(loops or {}), None),
              recent_results=lambda: copy.deepcopy(results or []))
    selected = copy.deepcopy([n for n in SETUP.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                              and n.name in {'cards', 'board', 'loop_cmd'}])
    for node in selected: node.decorator_list = []
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<offline slash commands>', 'exec'), ns)
    return ns


async def command_checks():
    statuses = ['untested', 'ready', 'needs-info', 'building', 'needs-look', 'testing', 'tested',
                'candidate', 'smoke', 'kept', 'rejected', 'inconclusive']
    ideas = [{'n': n, 'status': status, 'title': f'Fixture {n}', 'url': f'https://example.invalid/{n}',
              'wf': '2', 'area': 'queen', 'created': str(n), 'ready': False, 'running': False}
             for n, status in enumerate(statuses, 1)]
    loops = {'final': {'issue': 10, 'state': 'running', 'wf': 2},
             'active': {'issue': 4, 'state': 'running', 'wf': 2}}
    results = [{'n': n, 'head': '[test] Fixture', 'first': '', 'at': '2026-10-03T12:00:00Z',
                'url': f'https://example.invalid/result/{n}'} for n in [4, 10]]
    ns = command_env(ideas, loops, results)
    for command in ['board', 'loop_cmd']:
        it = Interaction()
        await ns[command](it)
        embeds = [e for call in it.followup.calls for e in call['embeds']]
        fields = [f for e in embeds for f in e.get('fields', []) if 'status:' in f['name']]
        expected = ideas if command == 'board' else ideas[:9]
        assert len(fields) == len(expected)
        for i in expected:
            assert any(f['name'].startswith(f"#{i['n']} ") and f"status:{i['status']}" in f['name'] for f in fields)
        assert all(call['ephemeral'] and len(call['embeds']) <= 10 for call in it.followup.calls)
        if command == 'loop_cmd':
            assert 'status:kept' not in json.dumps(embeds)
            assert not any(e['title'].endswith('final') for e in embeds)
            assert not any(f['name'].startswith('#10 ') for e in embeds for f in e.get('fields', []))
    ok('/board shows all open states; /loop hides final cards, active-loop references and results')
    ns = command_env([dict(ideas[0], n=n, title='x' * 150,
                           url=f'https://github.com/forrest-gan2005/battlecode/issues/{n}')
                      for n in range(1, 201)])
    for command in ['board', 'loop_cmd']:
        it = Interaction(); await ns[command](it)
        fields = [f for call in it.followup.calls for e in call['embeds'] for f in e.get('fields', [])
                  if 'status:' in f['name']]
        assert len(fields) == 200
        assert all(len(call['embeds']) <= 10 for call in it.followup.calls)
        for call in it.followup.calls:
            size = sum(sum(len(e.get(k, '')) for k in ['title', 'description'])
                       + len(e.get('footer', {}).get('text', ''))
                       + sum(len(f['name']) + len(f['value']) for f in e.get('fields', []))
                       for e in call['embeds'])
            assert size <= 6000
    ok('200 open cards paginate within Discord embed count/text limits without dropping states')
    ns = command_env([])
    for command in ['board', 'loop_cmd']:
        it = Interaction(); await ns[command](it)
        assert it.followup.calls
    ok('empty board and loop retain card layout')


async def poll_check():
    ns = dict(vars(m)); sent = []
    class Channel:
        name = 'offline-meow'
        async def send(self, *a, **kw): sent.append((a, kw))
    ch = Channel()
    async def post_candidates(c): assert c == []
    async def sleep(seconds): pass
    st = {'last_event_id': 0}
    async def chat_poll(client): pass
    async def state_send(channel, n, extra, discord): await channel.send(m.state_message(n, extra))
    ns.update(discord=types.SimpleNamespace(), send_state_message=state_send, chat=types.SimpleNamespace(CardForceView=lambda n: 'force-view', poll=chat_poll), st=st, state={'channel': ch}, channel_id=0, log=lambda *a: None,
              approval_lock=asyncio.Lock(), post_candidates=post_candidates,
              new_candidates=lambda st: [], save_state=lambda st: None)
    poll = copy.deepcopy(next(n for n in BOT.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'poll'))
    exec(compile(ast.Module(body=[poll], type_ignores=[]), '<offline poll>', 'exec'), ns)
    class FakeBot:
        user = 'offline'
        async def wait_until_ready(self): pass
        def is_closed(self):
            self.count = getattr(self, 'count', 0) + 1
            return self.count > 1
    fixtures = [event(1, 'needs-info'), event(2, 'needs-look'), event(3, 'tested')]
    with patch.object(m, 'gh', return_value=list(reversed(fixtures))), patch.object(m.asyncio, 'sleep', sleep):
        await ns['poll'](FakeBot())
    assert len(sent) == 3
    assert all('<@900000000000000002>' in a[0] for a, kw in sent)
    assert all('view' not in kw for a, kw in sent)
    ok('actual poll sends one short mentioned message for each human-action state (fake channel)')


async def force_persistence_check():
    import discord
    from meow_ui import MeowUI
    st = {'idea_states': {'31': 'tested', '7': 'candidate'}}
    chat = MeowUI(m, discord, st, {}, asyncio.Lock(), asyncio.Lock())
    ns = dict(vars(m), st=st, chat=chat, discord=discord)
    # Execute the actual setup prefix without registering commands or starting a bot.
    prefix = copy.deepcopy(SETUP.body[:2])
    client = types.SimpleNamespace(add_view=Mock())
    with patch.object(m, 'save_state'):
        exec(compile(ast.Module(body=prefix, type_ignores=[]), '<offline persistent views>', 'exec'),
             dict(ns, self=client))
    views = [call.args[0] for call in client.add_view.call_args_list]
    assert [v.children[0].custom_id for v in views] == ['meow-force-state:31', 'meow-force-state:7']
    assert all(v.is_persistent() for v in views)
    it = types.SimpleNamespace(user=types.SimpleNamespace(id=next(iter(m.MEMBERS))),
                              response=types.SimpleNamespace(send_message=AsyncMock()),
                              followup=types.SimpleNamespace(send=AsyncMock()), channel=object())
    views[0].children[0]._values = ['candidate']
    with patch.object(chat, 'force', new_callable=AsyncMock) as force:
        await views[0].children[0].callback(it)
        force.assert_awaited_once_with(it, {'action': 'set_state', 'card': 31, 'state': 'candidate'})
    # A deleted/closed old card fails during preparation and acknowledges the click.
    with patch.object(chat, 'thread', new_callable=AsyncMock, return_value=object()), \
         patch.object(chat, 'offer', new_callable=AsyncMock, side_effect=ValueError('Card no longer open')):
        await views[0].children[0].callback(it)
    assert 'no action executed' in it.followup.send.call_args.args[0]
    ok('legacy Force menus restore with the same persistent IDs; stale cards fail gracefully')
    candidate = copy.deepcopy(next(n for n in RUN.body if isinstance(n, ast.ClassDef) and n.name == 'CandidateView'))
    exec(compile(ast.Module(body=[candidate], type_ignores=[]), '<offline candidate Force>', 'exec'), ns)
    view = ns['CandidateView']('old-candidate')
    button = next(b for b in view.children if b.label == 'Force')
    assert view.is_persistent() and button.custom_id == 'force:old-candidate'
    with patch.object(chat, 'force', new_callable=AsyncMock) as force:
        await button.callback(it)
        force.assert_awaited_once_with(it, {'action': 'vote', 'candidate': 'old-candidate', 'vote': 'OK'})
    ok('candidate Force button still routes through the responsibility confirmation flow')


with patch.object(m.subprocess, 'run', side_effect=forbidden):
    st = {}
    assert events(st, [event(1, 'needs-info')]) == [] and st['last_event_id'] == 1
    ok('first poll establishes cursor without replaying historical pings')
    st = {'last_event_id': 0}
    fixtures = [event(1, 'needs-info'), event(2, 'needs-info'), event(3, 'building'),
                event(4, 'needs-look'), event(5, 'testing'), event(6, 'tested'), event(7, 'candidate')]
    out = events(st, fixtures)
    assert [(kind, extra['status']) for kind, n, extra in out] == [
        ('state', 'needs-info'), ('state', 'needs-look'), ('verdict', 'tested'), ('state', 'candidate')]
    assert events(json.loads(json.dumps(st)), fixtures) == []
    late = events(st, [event(8, 'candidate'), event(9, 'smoke'), event(10, 'kept')])
    assert [(kind, extra['status']) for kind, n, extra in late] == [('verdict', 'kept')]
    ok('only requested states ping; duplicate labels and persisted-cursor replays stay silent')
    st = {'last_event_id': 0}
    out = events(st, [event(1, 'needs-info'), event(2, 'needs-info', 'unlabeled'), event(3, 'needs-info')])
    assert len(out) == 2
    out = events(st, [event(4, 'building'), event(5, 'needs-info', 'unlabeled'), event(6, 'needs-info')])
    assert len(out) == 1
    ok('genuine re-entry pings again; removing an older state preserves newer state')
    m.outcome_line = lambda number: 'Yes, it worked.'
    for uid, name in m.MEMBERS.items():
        card = issue(author=m.AUTHOR_LABELS[name])
        assert m.idea_mention(card) == f'<@{uid}>'
        for status in ['needs-info', 'needs-look', 'tested']:
            msg = m.state_message(7, {'issue': card, 'status': status})
            assert msg.startswith(f'<@{uid}> ') and '#7' in msg and card['html_url'] in msg
    for label in ['by:ai', 'by:unknown', None]:
        for status in ['needs-info', 'needs-look', 'tested']:
            assert '<@' not in m.state_message(7, {'issue': issue(author=label), 'status': status})
    for status in ['needs-info', 'needs-look', 'tested']:
        msg = m.state_message(7, {'issue': issue(), 'status': status})
        hint = ('decide with /answer card:7 text:ship it / drop it / revise: …'
                if status == 'tested' else 'reply with /answer card:7 text:…')
        assert hint in msg
    ok('all three member labels map to IDs; AI, absent and unknown authors have no mention')
    for status, icon in [('tested', '✅'), ('rejected', '❌'), ('inconclusive', '➖'), ('kept', '🚀')]:
        msg = m.state_message(7, {'issue': issue(), 'status': status})
        assert f'{icon} **#7 Fixture**' in msg and 'Yes, it worked.' in msg and msg.endswith('https://example.invalid/issues/7')
        assert msg.startswith('<@900000000000000002> ') == (status == 'tested')
    assert events({'last_event_id': 0}, [event(1, 'needs-info', card=issue(title='Other card'))]) == []
    ok('existing verdict wording/final verdicts preserved; non-Idea issues ignored')
    raw = [dict(issue(), url='https://example.invalid/7', createdAt='2026-10-03',
                labels=[{'name': 'status:needs-look'}]),
           dict(issue(8, title='Other card'), url='https://example.invalid/8', createdAt='2026-10-03')]
    with patch.object(m, 'gh', return_value=raw):
        assert m.board_state()[0]['status'] == 'needs-look' and len(m.board_state()) == 1
    ok('fake GitHub board reads status labels and excludes other issues')
    asyncio.run(command_checks())
    asyncio.run(poll_check())
    asyncio.run(force_persistence_check())
print(f'{len(checks)} offline checks passed; no bot startup, network or real state writes.')
