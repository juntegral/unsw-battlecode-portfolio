import json
import gzip
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import ladder_collect as c
import ladder_guard as guard
import ladder_hourly as runner
import ladder_rows as rows

class CollectorTests(unittest.TestCase):
    def battle(self,i=1):return dict(id=i,ranked=True,outcome='win',results=['win','loss'],wins=1,losses=1,at='2026-10-07T00:05:00+00:00')
    def polls(self):return [dict(time='2026-10-07T00:00:00+00:00',submissions=[dict(id=10,wins=2,losses=3,draws=0),dict(id=11,wins=0,losses=0)]),dict(time='2026-10-07T00:10:00+00:00',submissions=[dict(id=10,wins=3,losses=4,draws=0),dict(id=11,wins=0,losses=0)])]
    def test_attribution(self):self.assertEqual(c.submission_for(self.battle(),self.polls()),10)
    def test_before_first(self):
        b=self.battle();b['at']='2026-10-06T00:00:00+00:00';self.assertIsNone(c.submission_for(b,self.polls()))
    def test_ambiguous(self):
        p=self.polls();p[1]['submissions'][1]['wins']=1;self.assertIsNone(c.submission_for(self.battle(),p))
    def test_new_submission_not_guessed(self):
        p=self.polls();p[1]['submissions'].append(dict(id=12,wins=10,losses=0));p[1]['submissions'][0]['wins']=2;p[1]['submissions'][0]['losses']=3
        self.assertIsNone(c.submission_for(self.battle(),p))
    def test_finished(self):
        self.assertTrue(c.finished(self.battle()))
        for k,v in [('ranked',False),('outcome','live'),('results',['win','pending'])]:
            b=self.battle();b[k]=v;self.assertFalse(c.finished(b))
    def test_retry_and_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out';raw=Path(tmp)/'raw';calls=[];complete=False
            def fetch(*args):
                if args[0]=='battles':return json.dumps([self.battle()])
                calls.append(args);folder=raw/'1';folder.mkdir(parents=True,exist_ok=True)
                c.atomic(folder/'index.json',dict(games=[dict(gameId=i) for i in (1,2)]))
                for i in (1,2):
                    c.atomic(folder/f'game-{i}.json',dict(id=i,status='completed',mapName='test'))
                    if i==1 or complete:(folder/f'M{i}.replay').write_bytes(gzip.compress(b'replay'))
                return ''
            first=c.collect(fetch,out,raw,lambda _:None,self.polls());self.assertEqual(first['incomplete'],1);self.assertEqual(first['downloaded_games'],1)
            complete=True
            second=c.collect(fetch,out,raw,lambda _:None,self.polls());self.assertEqual(second['added'],1);self.assertEqual(second['downloaded_games'],1)
            third=c.collect(fetch,out,raw,lambda _:None,self.polls());self.assertEqual(third['added'],0);self.assertEqual(len(calls),2);self.assertEqual(len(c.read_lines(out/'battles.jsonl')),1)
    def test_truncated_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'M1.replay';p.write_bytes(gzip.compress(b'payload')[:-2])
            self.assertFalse(c.replay_valid(p,{}))
            p.write_bytes(gzip.compress(b'payload'));self.assertTrue(c.replay_valid(p,{}))
            self.assertFalse(c.replay_valid(p,dict(replay=dict(bytes=999))))
    def test_poll(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fetch(*a):return json.dumps([dict(id=9,status='active',name='v9',wins=1,losses=2,sourceHash='hash',rating=1900)])
            r=c.poll(fetch,'2026-10-07T00:00:00+00:00',Path(tmp));self.assertEqual(r[0]['active']['id'],9);self.assertEqual(r[0]['submissions'][0]['losses'],2)
    def test_sequential_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            count=[];pauses=[]
            def fetch(*a):
                if a[0]=='battles':return json.dumps([self.battle(i) for i in range(151)])
                count.append(a);return ''
            r=c.collect(fetch,Path(tmp)/'out',Path(tmp)/'raw',pauses.append,[])
            self.assertEqual(r['attempts'],150);self.assertEqual(len(pauses),149);self.assertEqual(set(pauses),{1})

class AuditTests(unittest.TestCase):
    """Definitions fixed in the 10-07 audit."""
    VAULT='\n'.join(['MAP 4 3']+[f'TILE {x} {y} 0 0' for y in range(3) for x in range(4)]+[f'EDGE {e} 1 -1' for e in (0,1,20,21,5,15,7,17)]+['DRAGON 0 4 1 1 1 0 0 0 0 1','DRAGON 1 2 3 1 3 2','END'])
    def table(self):return {'7':dict(version=3,name='card-x',description='MAIN, live',sourceHash=next(h for h,v in rows.CODE.items() if v=='main'),uploadedAt='t'),
                            '8':dict(version=4,name='x-test',description='TEST. x',sourceHash='abc',uploadedAt='t'),'9':dict(version=5,name='y-test',description='TEST. same code',sourceHash=next(h for h,v in rows.CODE.items() if v=='main'),uploadedAt='t')}
    def game(self,end_reason,us,them,winner):
        side=lambda q,longest,total,alive:dict(alive=alive,total=total,longest=longest,pearls=0,queen_alive=q>0,queen_length=q)
        final=dict(us=side(*us),them=side(*them))
        return dict(ours='A',bots=dict(A='7',B=''),winner=winner,last_round=499 if end_reason else 80,final=final,end_reason=end_reason,snapshots={},queens=dict(us=0,them=1),
                    deaths=[],collisions=[],pearls=[],q_eats={},q_splits={},eaten_rounds=[],text='',natural=[],intervals={})
    def row(self,*a):
        with patch.object(rows,'scan',lambda *x:self.game(*a)):return rows.make_row(Path('x/M1.replay'),dict(id=1,mapName='m',teamAId=1119,teamBId=2),table=self.table())[0]
    def test_plain_replay_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'M1.replay';p.write_bytes(b'p}\x96\x1bplain')
            self.assertTrue(c.replay_valid(p,dict(replay=dict(bytes=9))));self.assertFalse(c.replay_valid(p,dict(replay=dict(bytes=8))));self.assertFalse(c.replay_valid(p,{}))
    def test_recheck(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out';raw=Path(tmp)/'raw';folder=raw/'5';folder.mkdir(parents=True)
            c.atomic(folder/'index.json',dict(games=[dict(gameId=5),dict(gameId=6)]))
            for i in (5,6):
                (folder/f'M{i}.replay').write_bytes(b'plain');c.atomic(folder/f'game-{i}.json',dict(id=i,status='completed',mapName='m',replay=dict(bytes=5)))
            c.atomic(out/'battles.jsonl',[dict(id=5,results=['win','loss'],games=[],complete=False)],True)
            self.assertEqual(c.recheck(out,raw),dict(battles=1,changed=1,incomplete=0));b=c.read_lines(out/'battles.jsonl')[0]
            self.assertTrue(b['complete']);self.assertEqual([g['id'] for g in b['games']],[5,6]);self.assertEqual(c.recheck(out,raw)['changed'],0)
    def test_border_edges(self):
        self.assertEqual(rows.edge_id(4,3,3,1,1),rows.edge_id(4,3,0,1,3));self.assertEqual(rows.edge_id(4,3,2,2,2),rows.edge_id(4,3,2,0,0))
        self.assertEqual(rows.canonical_edges(4,3,[(30,1,-1),(19,2,7),(4,1,-1)]),{0:(1,-1),15:(2,7)})
    def test_vault_geometry(self):
        _,g=rows.geometry(self.VAULT)
        self.assertEqual((g['open_tiles'],g['queen_spawn_distance'],g['queen_spawn_room'],g['queen_spawn_region'],g['queen_spawn_dead_end'],g['queen_spawn_length'],g['dragons_at_spawn']),(12,2,0,4,True,2,1))
        self.assertAlmostEqual(g['wall_share'],1/3);self.assertAlmostEqual(g['corridor_share'],0.5)
        _,free=rows.geometry(self.VAULT.replace('DRAGON 0 4 1 1 1 0 0 0 0 1','DRAGON 0 2 2 0 2 1'));self.assertFalse(free['queen_spawn_dead_end'])
    def test_our_code(self):
        t=self.table();bot,code,note=rows.our_bot('7',t);self.assertEqual((code,bot['test'],bot['same_code_as'],note),('main',False,[3,5],None))
        self.assertEqual(rows.our_bot('9',t)[1],'main');self.assertTrue(rows.our_bot('9',t)[0]['test']);self.assertEqual(rows.our_bot('8',t)[1],'v4 x-test')
        self.assertEqual(rows.our_bot('',t)[:2],(None,'unknown'));bot,code,note=rows.our_bot('77',t);self.assertEqual((bot['id'],code),(77,'unknown'));self.assertIsNotNone(note)
    def test_ended_by(self):
        for args,ended,queens,result in [((0,(0,3,9,4),(0,0,0,0),'A'),'elimination','both dead','win'),((1,(0,9,30,5),(4,4,4,1),'B'),'queen rule','only theirs','loss'),
                ((1,(5,5,5,1),(4,9,30,5),'A'),'queen rule','both alive','win'),((1,(0,7,30,5),(0,9,20,5),'B'),'longest dragon','both dead','loss'),
                ((1,(3,7,30,5),(3,7,20,5),'A'),'total length','both alive','win'),((1,(3,7,20,5),(3,7,20,5),None),'draw','both alive','draw')]:
            r=self.row(*args);self.assertEqual((r['ended_by'],r['queens_at_end'],r['result']),(ended,queens,result));self.assertNotIn('result',r['notes']);self.assertEqual(r['our_code'],'main')
        self.assertIn('result',self.row(1,(0,9,30,5),(4,4,4,1),'A')['notes'])
    def test_map_versions(self):
        swapped=self.VAULT.replace('DRAGON 0 4','DRAGON x 4').replace('DRAGON 1 2','DRAGON 0 2').replace('DRAGON x 4','DRAGON 1 4');other=self.VAULT.replace('EDGE 17 1 -1','EDGE 17 0 -1')
        self.assertEqual(rows.signature(self.VAULT),rows.signature(swapped));self.assertNotEqual(rows.signature(self.VAULT),rows.signature(other))
        obs={'3':dict(map='m',time='t3',text=other,natural={},intervals={}),'1':dict(map='m',time='t1',text=self.VAULT,natural={},intervals={}),'2':dict(map='m',time='t2',text=swapped,natural={},intervals={})}
        self.assertEqual(rows.map_keys(obs),{'1':(1,'m #1'),'2':(1,'m #1'),'3':(2,'m #2')})
        with patch.object(rows,'local_ranges',lambda *a:(None,None)):maps=rows.build_maps(obs)
        self.assertEqual({k:(v['versions_of_name'],v['games_observed']) for k,v in maps.items()},{'m #1':(2,2),'m #2':(2,1)})
    def test_local_gaps_must_match_births(self):
        births={'2,2':6,'3,0':4};obs={'1':dict(map='m',time='t',text=self.VAULT,natural=births,intervals={'2,2':[1,1,1,1,1]})}
        good={(x,y):((1,1) if (x,y)==(2,2) else (1,100) if (x,y)==(3,0) else (0,0)) for y in range(3) for x in range(4)}
        with patch.object(rows,'local_ranges',lambda *a:(good,'local.map')):m=rows.build_maps(obs)['m #1']
        self.assertEqual((m['supply_method'],m['pearl_tiles'],m['fast_tiles'],m['fast_supply_share']),('local gaps',2,1,0.6));self.assertAlmostEqual(m['fast_rate_share'],1/(1+2/101))
        bad=dict(good);bad[3,0]=(0,0)
        with patch.object(rows,'local_ranges',lambda *a:(bad,'local.map')):m=rows.build_maps(obs)['m #1']
        self.assertEqual((m['supply_method'],m['fast_rate_share'],m['fast_supply_share']),('observed intervals',None,0.6));self.assertIn('4 of 10',m['notes']['source'])

class GuardTests(unittest.TestCase):
    def check(self,cmd,role='analyst'):
        with patch.dict(os.environ,LADDER_ROLE=role):return guard.check(dict(tool_name='Bash',cwd=str(c.ROOT),tool_input=dict(command=cmd)))
    def test_blocked_classes(self):
        for cmd in ['cat docs/api.txt','cat docs/discord.txt','node tools/online.js battles --confirm','node tools/submit.js','node tools/online.js request 2','node tools/online.js activate 3','cat meowbot','ls meow_release','echo discord','python3 board.py','gh issue create','git push','git commit','git config --list','git remote -v','curl https://a','wget https://a','nohup ls','ls &','python -c "print(1)"','python3 -c "print(1)"','echo bad > tools/oops','rm versions/bot','cp x tools/a','cat x | tee tools/a']:
            with self.subTest(cmd=cmd):self.assertIsNotNone(self.check(cmd))
    def test_allowed(self):
        for cmd in ['ls data/online/ladder','rg queen tools/ladder_replay.py','node tools/online.js battles --limit 200 --json','node tools/online.js submissions --all --json','node tools/online.js battle 12 --json','node tools/online.js maps','git status --short','gh pr view 3','echo ok > data/analysis/ladder/work/test.txt',"python3 - <<'EOF'\nfrom pathlib import Path\nPath('data/analysis/ladder/work/a.json').write_text('[]')\nEOF"]:
            with self.subTest(cmd=cmd):self.assertIsNone(self.check(cmd))
    def test_heredoc_bad(self):
        for cmd in ["python3 - <<'EOF'\nfrom pathlib import Path\nPath('tools/a').write_text('bad')\nEOF", "python3 - <<'EOF'\nimport subprocess\nsubprocess.run(['curl','x'])\nEOF", "python3 - <<EOF\nprint(1)\nEOF"]:self.assertIsNotNone(self.check(cmd))
    def test_write_roles(self):
        for role,good,bad in [('analyst','data/analysis/ladder/findings.md','tools/x'),('verifier','data/analysis/ladder/verify/F1.md','data/analysis/ladder/findings.md')]:
            with patch.dict(os.environ,LADDER_ROLE=role):
                self.assertIsNone(guard.check(dict(tool_name='Write',tool_input=dict(file_path=good))))
                self.assertIsNotNone(guard.check(dict(tool_name='Write',tool_input=dict(file_path=bad))))
        self.assertIsNone(self.check('echo [] > data/analysis/ladder/verify-results.json','verifier'))
        self.assertIsNotNone(self.check('echo [] > data/analysis/ladder/state.json','verifier'))
    def test_traversal_symlink(self):
        self.assertIsNotNone(self.check('echo bad > data/analysis/ladder/../../../tools/a'))
        with tempfile.TemporaryDirectory(dir=c.OUT) as tmp:
            p=Path(tmp)/'escape';p.symlink_to(c.ROOT/'tools',target_is_directory=True)
            self.assertIsNotNone(self.check(f'echo bad > "{p}/a"'))
    def test_readonly_python_outside_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'read.py';p.write_text('print(1)\n')
            self.assertIsNone(self.check(f'python3 "{p}"'))
    def test_unknown_tool(self):self.assertIsNotNone(guard.check(dict(tool_name='WebFetch',tool_input={})))
    def test_file_python(self):
        with tempfile.TemporaryDirectory(dir=c.OUT) as tmp:
            p=Path(tmp)/'test.py';p.write_text("from pathlib import Path\nPath('data/analysis/ladder/work/output').write_text('[]')\n")
            self.assertIsNone(self.check(f'python3 "{p}"'))
            self.assertIsNotNone(self.check(f'python3 "{p}"','verifier'))

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.out=Path(self.tmp.name)
        self.p=patch.object(runner,'OUT',self.out);self.p.start();self.addCleanup(self.p.stop)
    def test_effort(self):
        self.assertEqual(runner.effort(),'high');(self.out/'findings.md').write_text('x');self.assertEqual(runner.effort(),'high');self.assertEqual(runner.effort(True),'high')
    def test_queue_success(self):
        q=self.out/'verify-queue.json';q.write_text('[{"id":"F1"}]');calls=[]
        self.assertTrue(runner.verify('stamp',lambda *a:calls.append(a)));self.assertEqual(json.loads(q.read_text()),[]);self.assertEqual(json.loads((self.out/'verified/stamp-queue.json').read_text()),[{'id':'F1'}]);self.assertEqual(calls,[('verifier','stamp')])
    def test_queue_failure_kept(self):
        q=self.out/'verify-queue.json';q.write_text('[1]')
        def fail(*a):raise RuntimeError('failure')
        with self.assertRaises(RuntimeError):runner.verify('stamp',fail)
        self.assertEqual(json.loads(q.read_text()),[1]);self.assertFalse((self.out/'verified').exists())
    def test_empty_queue(self):
        (self.out/'verify-queue.json').write_text('[]');self.assertFalse(runner.verify('stamp',lambda *a:self.fail('called')))
    def test_cycle_no_ai_failure_continues(self):
        calls=[]
        def fake(argv,**kw):
            calls.append(argv)
            if 'collect' in str(argv):raise RuntimeError('offline')
        with patch.object(runner,'run',fake),patch.object(runner,'ai',side_effect=AssertionError):runner.cycle(no_ai=True)
        self.assertEqual(len(calls),2);text=(self.out/'runner.log').read_text();self.assertIn('collect failed',text);self.assertIn('rows ok',text)
    def test_ai_argv_timeouts(self):
        for role,first,expected,timeout in [('analyst',True,'high',3000),('analyst',False,'high',3000),('verifier',False,'high',2400)]:
            (self.out/f'{role}-prompt.md').write_text('prompt');(self.out/'findings.md').write_text('x');calls=[]
            def fake(argv,**kw):calls.append((argv,kw));kw['output'].write_text('{"type":"result","is_error":false}\n')
            with patch.object(runner,'run',fake):runner.ai(role,role,first)
            argv,kw=calls[0];self.assertEqual(argv[argv.index('--effort')+1],expected);self.assertEqual(kw['timeout'],timeout);self.assertEqual(kw['env']['LADDER_ROLE'],role);self.assertIn("This run's hour file:",kw['stdin'])

if __name__=='__main__':unittest.main()
