import ast, asyncio, base64, contextlib, copy, importlib.util, io, json, pathlib, sys, types
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('meowbot', ROOT / 'tools/meowbot.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
C = {'version': 'v-preview', 'bot_dir': 'mybot2', 'workflow': 2, 'changes': ['Offline fixture'], 'results': {}, 'issues': [7], 'pr': 999}
P = {'number': 12, 'url': 'https://github.com/forrest-gan2005/battlecode/pull/12', 'state': 'OPEN', 'baseRefName': 'main', 'headRefOid': 'a' * 40, 'mergeable': 'MERGEABLE', 'isDraft': False, 'mergeCommit': None}
R = {'status': 'pending', 'manifest': C, 'pr': 12, 'url': P['url'], 'head_sha': P['headRefOid'], 'path': 'candidates/demo.json', 'message_id': 1, 'author_labels': ['by:ai'], 'oks': [str(next(iter(m.MEMBERS)))]}
checks = []
def ok(name):
    checks.append(name)
    print('PASS', name)

def forbidden(*a, **kw):
    raise AssertionError('Unexpected external operation')

class View:
    def __init__(self, **kw): self.children = []; self.stopped = False
    def add_item(self, item): self.children.append(item)
    def stop(self): self.stopped = True
class Button:
    def __init__(self, **kw): self.__dict__.update(kw); self.disabled = False
class HTTPException(Exception): pass
class Calls:
    def __init__(self): self.calls = []
    async def send_message(self, *a, **kw): self.calls.append(('send', a, kw))
    async def edit_message(self, *a, **kw): self.calls.append(('edit', a, kw))
    async def defer(self, *a, **kw): self.calls.append(('defer', a, kw))
    async def send(self, *a, **kw): self.calls.append(('send', a, kw))
class Interaction:
    def __init__(self, uid=None):
        self.user = types.SimpleNamespace(id=uid if uid is not None else next(iter(m.MEMBERS)))
        self.response, self.followup = Calls(), Calls()
class Channel:
    def __init__(self): self.sent = []; self.edits = []
    async def send(self, *args, **kw):
        self.sent.append(kw)
        return types.SimpleNamespace(id=len(self.sent) + 10)
    def get_partial_message(self, mid):
        async def edit(**kw): self.edits.append((mid, kw))
        return types.SimpleNamespace(edit=edit)

def env():
    ns = dict(vars(m))
    ns.update(st={'candidates': {'candidate': copy.deepcopy(R)}}, state={'channel': Channel()},
              approval_lock=asyncio.Lock(), release_lock=asyncio.Lock(),
              discord=types.SimpleNamespace(ui=types.SimpleNamespace(View=View, Button=Button),
                    ButtonStyle=types.SimpleNamespace(success=1, secondary=2),
                    Embed=types.SimpleNamespace(from_dict=lambda x: x), HTTPException=HTTPException),
              save_state=lambda st: None, log=lambda *a: None)
    tree = ast.parse((ROOT / 'tools/meowbot.py').read_text())
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run_bot')
    selected = [n for n in run.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and n.name in {'edit_candidate', 'post_candidates', 'CandidateConfirm', 'CandidateView'}]
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<offline candidate views>', 'exec'), ns)
    ns['candidate_pr'] = lambda n: copy.deepcopy(P)
    ns['merge_candidate'] = lambda rec: 'b' * 40
    ns['sync_release'] = lambda ref: None
    ns['candidate_authors'] = lambda c: ['by:ai']
    ns['prepare_candidate'] = types.FunctionType(m.prepare_candidate.__code__, ns)
    ns['upload'] = lambda c: m.upload(c)
    return ns

async def scenarios():
    """Legacy combined merge/upload scenarios retired; shared fakes remain for regressions."""


if __name__ == '__main__':
    import runpy
    runpy.run_path(str(ROOT / 'data/codex/check-merge-submit-split.py'), run_name='__main__')
