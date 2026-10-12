import sys,json,ast
from pathlib import Path
from collections import Counter
from datetime import datetime
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
S=json.loads((P/'summary.json').read_text());checks=[]
for label,s in S.items():
    led=list(map(json.loads,(P/(label+'-ledger.jsonl')).read_text().splitlines()))
    scan=list(map(json.loads,(P/(label+'-scan-v2.jsonl')).read_text().splitlines()))
    enrich=json.loads((P/(label+'-enrich.json')).read_text())
    assert len(led)==len(scan)==len(enrich)==s['games']==s['extra_games']==15
    assert {g['gid'] for g in led}=={g['gid'] for g in scan}=={g['gid'] for g in enrich}
    d=s['natural_decomp_per_game']
    assert abs(d['heads']+d['efficiency']-(s['totals'][1]['eat_n']-s['totals'][0]['eat_n'])/15)<1e-9
    assert abs(sum(v for k,v in d.items() if k.startswith('class '))-d['efficiency'])<1e-9
    for side in (0,1):
        c=s['totals'][side]
        assert c['L300']-c['L100']==c['eat_n']+c['eat_own']+c['eat_foe']-c['deadlen']-c['paid']
        assert c['H300']-c['H100']==c['splits']-c['deaths']
        assert sum(s['deaths'][side].values())==sum(s['dead_length_bins'][side].values())==c['deaths']
    assert sum(len(g['d1']) for g in scan)==s['counts'][0]['D1:miss']
    assert sum(len(g['blind']) for g in scan)==s['counts'][0]['solo']
    entry=Counter()
    for g in enrich:entry.update(g['C'])
    assert entry['continuing']+sum(v for k,v in entry.items() if k.startswith('entry:'))==s['counts'][0]['solo']
    checks.append(dict(label=label,games=15,length_and_heads_residual=0,partition_residual=0))
for f in P.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
report=(P/'report.md').read_text()
words=len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split())
assert words<450
assert report.splitlines()[0].startswith('[M]') and '카드' in report.splitlines()[1] and '확신' in report.splitlines()[2]
v=dict(at=datetime.now().astimezone().isoformat(),checks=checks,report_words_excluding_tables=words,python_syntax='passed')
(P/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(v,ensure_ascii=False))
