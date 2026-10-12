"""Offline fake GitHub/Discord/subprocess checks; never starts the bot."""
import ast, asyncio, copy, importlib.util, pathlib, types
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('meowbot', ROOT / 'tools/meowbot.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
# Reuse only the existing fake objects, without running the older flow's tests.
source = (ROOT / 'data/codex/check-approver.py').read_text()
ns0 = {'__file__': str(ROOT / 'data/codex/check-approver.py')}
exec(source[:source.index('async def scenarios():')], ns0)
Interaction, Channel = ns0['Interaction'], ns0['Channel']
P, R = ns0['P'], ns0['R']
def card_lookup(args):
    assert args[:2] == ['issue', 'view'], args
    return {'number': int(args[2]), 'title': '[Idea] Test', 'labels': [{'name': 'name:test'}]}
ns0['m'].gh = card_lookup
checks = []
def ok(name):
    checks.append(name); print('PASS', name)
def forbidden(*a, **kw):
    raise AssertionError('Unexpected external operation')

def env():
    ns = ns0['env']()
    tree = ast.parse((ROOT / 'tools/meowbot.py').read_text())
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_bot')
    nodes = [n for n in run.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
             and n.name in {'edit_submit', 'SubmitView', 'SubmitConfirm'}]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<offline submit views>', 'exec'), ns)
    ns.update(candidate_current=lambda r: True, candidate_patch_id=lambda r: 'patch',
              keep_cards=lambda issues, sha: None, submit_frozen=lambda: False,
              submission_list=lambda: [{'id': 61, 'name': 'v61', 'status': 'active'}])
    ns['st']['submits'] = {'s': {'status': 'pending', 'commit': 'd'*40, 'version': 'v62',
        'bot_dir': 'mybot2', 'cards': [], 'changes': [], 'baseline_known': True,
        'merged_commits': ['b'*40], 'previous_id': 61, 'message_id': 2, 'oks': [str(next(iter(m.MEMBERS)))]}}
    ns['upload'] = forbidden
    ns['sync_release'] = forbidden
    return ns

async def scenarios():
    ns = env()
    tree = ast.parse((ROOT / 'tools/meowbot.py').read_text())
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_bot')
    bot = next(n for n in run.body if isinstance(n, ast.ClassDef) and n.name == 'Bot')
    hook = next(n for n in bot.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'setup_hook')
    command = copy.deepcopy(next(n for n in hook.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'submit_cmd'))
    command.decorator_list = []
    ns['discord'].Interaction = Interaction
    async def member(it):
        if it.user.id in m.MEMBERS: return m.MEMBERS[it.user.id]
        await it.response.send_message('Only team members', ephemeral=True)
    ns['member'] = member
    plan = copy.deepcopy(ns['st']['submits']['s']); plan['oks'] = []
    seen_refs = []
    ns['submit_plan'] = lambda st, ref: seen_refs.append(ref) or copy.deepcopy(plan)
    exec(compile(ast.Module(body=[command], type_ignores=[]), '<offline slash command>', 'exec'), ns)
    await ns['submit_cmd'](Interaction(0))
    assert not seen_refs and not ns['state']['channel'].sent
    it = Interaction(); await ns['submit_cmd'](it, 'feature/card')
    created = [r for k,r in ns['st']['submits'].items() if k != 's'][0]
    assert seen_refs == ['feature/card'] and created['oks'] == [str(it.user.id)]
    assert created['requester_id'] == str(it.user.id) and m.submit_ready(created)
    assert isinstance(it.followup.calls[0][2]['view'], ns['SubmitConfirm'])
    assert it.followup.calls[0][2]['ephemeral'] and len(ns['state']['channel'].sent) == 1
    assert ns['state']['channel'].sent[0]['embed']['fields'][0]['value'] == 'd'*40
    ok('/submit rejects outsiders, previews ephemerally, posts public card and records requester OK with optional ref')

    ns = env(); kept=[]
    ns['keep_cards'] = lambda issues, sha: kept.append((issues, sha))
    conf = ns['CandidateConfirm'](ns['CandidateView']('candidate'), Interaction().user.id)
    await conf.confirm(Interaction())
    rec = ns['st']['candidates']['candidate']
    assert rec['status'] == 'approved' and kept == [([7], 'b'*40)]
    assert ns['st']['merged_candidates'][0]['commit'] == 'b'*40
    assert 'next /submit' in rec['result']
    await conf.confirm(Interaction())
    assert len(ns['st']['merged_candidates']) == 1
    ok('candidate merges once, keeps linked cards, records pending changes; never syncs or uploads')

    ns = env(); writes=[]
    ns['candidate_current'] = lambda r: False
    ns['merge_candidate'] = forbidden
    ns['request_rebase'] = types.FunctionType(m.request_rebase.__code__, dict(vars(m),
        gh=lambda args: writes.append(args), gh_comment=lambda *args: writes.append(args)))
    before = copy.deepcopy(ns['st']['candidates']['candidate']['oks'])
    await ns['CandidateConfirm'](ns['CandidateView']('candidate'), Interaction().user.id).confirm(Interaction())
    assert 'needs:rebase' in writes[0] and 'main moved' in writes[1][-1]
    assert ns['st']['candidates']['candidate']['oks'] == before
    ok('stale base refuses merge, labels and comments needs:rebase, retains OKs')

    users = list(m.MEMBERS)
    ns=env(); rec=ns['st']['submits']['s']; v=ns['SubmitView']('s')
    await v.approve(Interaction(0)); assert len(rec['oks']) == 1
    it=Interaction(users[0]); await v.approve(it)
    assert m.submit_ready(rec) and len(rec['oks']) == 1
    conf=it.response.calls[0][2]['view']
    await conf.confirm(Interaction(users[1]))
    assert rec['status'] == 'pending' and not conf.used
    other=Interaction(users[1]); await v.approve(other)
    assert 'view' not in other.response.calls[0][2] and len(rec['oks']) == 1
    await conf.cancel(Interaction(users[0]))
    assert rec['status'] == 'pending' and len(rec['oks']) == 1
    again=Interaction(users[0]); await v.approve(again)
    assert isinstance(again.response.calls[0][2]['view'], ns['SubmitConfirm'])
    assert not m.submit_ready({'oks': []}) and not m.submit_ready({'oks': ['0']})
    assert not m.submit_ready({'requester_id': str(users[0]), 'oks': [str(users[1])]})
    ok('submit needs only requester + confirmation; rejects outsiders/other members; cancel allows requester retry')

    ns['submit_frozen']=lambda: True
    await ns['SubmitConfirm']('s', users[0]).confirm(Interaction(users[0]))
    assert rec['status'] == 'pending'
    ok('freeze refuses submit confirmation before any sync/upload')

    ns=env(); rec=ns['st']['submits']['s']; order=[]
    ns['sync_release']=lambda sha: order.append(('sync',sha))
    ns['upload']=lambda c: order.append(('upload',c['commit'])) or {'ok':True,'id':62,'result':'Uploaded v62'}
    conf=ns['SubmitConfirm']('s',users[0])
    await asyncio.gather(conf.confirm(Interaction(users[0])), conf.confirm(Interaction(users[0])))
    assert order == [('sync','d'*40),('upload','d'*40)]
    assert ns['st']['active_submission']['id'] == 62 and rec['submission_id'] == 62
    assert all(b.disabled for b in ns['state']['channel'].edits[-1][1]['view'].children)
    ok('submit syncs exact approved commit once; records id/version and updates public card')

    for kind in ('active', 'version', 'pending', 'freeze-after-sync'):
        ns=env(); rec=ns['st']['submits']['s']
        if kind=='active': ns['submission_list']=lambda: [{'id':60,'status':'active','name':'v60'}]
        if kind=='version': ns['submission_list']=lambda: [{'id':61,'status':'active','name':'v61'}, {'id':62,'name':'v62'}]
        if kind=='pending':
            ns['sync_release']=lambda sha: None
            ns['upload']=lambda c: {'ok':False,'id':None,'result':'refusing: 2 of our battles are live or pending'}
        if kind=='freeze-after-sync':
            ns['sync_release']=lambda sha: ns.update(submit_frozen=lambda: True)
        await ns['SubmitConfirm']('s',users[0]).confirm(Interaction(users[0]))
        assert rec['status'] in ('stale','error') and 'active_submission' not in ns['st']
        if kind=='pending': assert 'live or pending' in rec['result']
    ok('active/version changes refuse submission; pending-battle message surfaced; freeze rechecked after sync')

with patch.object(m.subprocess, 'run', side_effect=forbidden), patch.object(m, 'gh', side_effect=forbidden):
    asyncio.run(scenarios())
    for same in (True,False):
        old=dict(copy.deepcopy(R), patch_id='patch')
        rec=dict(copy.deepcopy(R), head_sha='e'*40)
        with patch.object(m,'candidate_authors',return_value=['by:ai']), patch.object(m,'candidate_patch_id',return_value='patch' if same else 'other'):
            m.prepare_candidate(rec, {'old':old})
        assert rec['oks'] == (old['oks'] if same else [])
    ok('same patch-id carries OKs; different patch-id resets OKs')

    cases = [
        (0, [{'filename': 'mybot2/bot.cpp'}], True),
        (1, [{'filename': 'docs/guide.md'}, {'filename': 'work/task.md'}, {'filename': 'tools/helper.py'}], True),
        (1, [{'filename': 'mybot2/bot.cpp'}], False),
        (2, [{'filename': 'docs/guide.md'}, {'filename': 'mybot2/deleted.cpp', 'status': 'removed'}], False),
        (1, [{'filename': 'work/moved.cpp', 'previous_filename': 'mybot2/moved.cpp'}], False),
        (1, [{'filename': 'mybot20/helper.cpp'}], True),
    ]
    for behind, files, current in cases:
        responses = [{'sha': 'f'*40}, {'behind_by': behind, 'files': [{'filename': 'mybot2/candidate.cpp'}]}]
        if behind: responses.append({'files': files})
        with patch.object(m, 'gh', side_effect=responses) as api:
            assert m.candidate_current(R) == current
            assert api.call_args_list[1].args[0][1].endswith(f"/compare/{'f'*40}...{R['head_sha']}")
            if behind:
                assert api.call_args_list[2].args[0][1].endswith(f"/compare/{R['head_sha']}...{'f'*40}")
            assert api.call_count == (3 if behind else 2)
    ok('stale guard blocks only behind-main mybot2 changes; ignores candidate code and docs/work/tools-only main changes')

    def gh_plan(args):
        if '/commits/' in args[1]: return {'sha':'d'*40}
        if '/tags?' in args[1]: return [[{'name':'v60'}],[{'name':'v63'}]]
        if '/compare/' in args[1]: return {'behind_by':0}
        raise AssertionError(args)
    state={'merged_candidates':[{'pr':12,'commit':'b'*40,'issues':[7],'changes':['change']}],
           'active_submission':{'id':61,'merged_commits':[]}}
    with patch.object(m,'gh',side_effect=gh_plan), patch.object(m,'submission_list',return_value=[{'id':61,'name':'v61','status':'active'}]), patch.object(m,'submit_frozen',return_value=False):
        plan=m.submit_plan(state)
        assert plan['version']=='v64' and plan['commit']=='d'*40 and plan['cards'][0]['issues']==[7]
    with patch.object(m,'submit_frozen',return_value=True):
        try: m.submit_plan(state)
        except RuntimeError as e: assert 'Freeze' in str(e)
        else: raise AssertionError('frozen plan allowed')
    assert not m.submit_frozen(m.datetime.datetime(2026,10,8,19,59,tzinfo=m.KST))
    assert m.submit_frozen(m.datetime.datetime(2026,10,8,20,tzinfo=m.KST))
    ok('version uses highest existing vNN across server/tags; preview lists cards; freeze boundary enforced')

    calls=[]
    def fake_gh(args):
        calls.append(args)
        return {'labels':[{'name':'status:candidate'},{'name':'by:ai'}]} if args[:2]==['issue','view'] else None
    with patch.object(m,'gh',side_effect=fake_gh), patch.object(m,'gh_comment') as comment:
        m.keep_cards([7,7],'b'*40)
        assert len(calls)==2 and 'status:kept' in calls[-1] and 'status:candidate' in calls[-1]
        assert 'next /submit' in comment.call_args.args[-1]
    ok('linked cards replace status label with kept and get exact merge comment')

for returncode, output in [(0,'active: 62 v62; server zip matches mybot2'),(3,'refusing: 2 of our battles are live or pending')]:
    commands=[]
    def fake_run(cmd,**kw):
        commands.append(cmd)
        return types.SimpleNamespace(returncode=returncode,stdout=output,stderr='')
    with patch.object(m.subprocess,'run',side_effect=fake_run):
        result=m.upload({'version':'v62','bot_dir':'mybot2','changes':[]})
    assert result['ok'] == (returncode==0) and result['id']==(62 if returncode==0 else None)
    assert '--confirm' in commands[0] and '--force' not in commands[0]
assert m.UPLOAD_ENABLED is True
ok('real submit gate enabled; existing submit.js upload retains pending guard and parses submission id (fake subprocess)')

with patch.object(m.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0,stdout='https://github.com/example/issue/7\n',stderr='')):
    assert m.gh(['issue','edit','7']) == 'https://github.com/example/issue/7'
ok('gh label writes accept plain URL output without JSON parsing failures')
print(f'{len(checks)} offline checks passed; no bot startup or real remote writes/uploads.')
