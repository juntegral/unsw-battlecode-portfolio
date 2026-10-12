import sys,json,csv,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime
O=Path('data/codex/astra/longest')
C=json.loads((O/'census.json').read_text());G=[json.loads(l) for l in (O/'games.jsonl').read_text().splitlines()];L=[json.loads(l) for l in (O/'local.jsonl').read_text().splitlines()];V=json.loads((O/'verification.json').read_text());I=json.loads((O/'inventory.json').read_text());B={b['gid']:b for b in map(json.loads,(O/'base.jsonl').read_text().splitlines())}
assert len(C)==len({r['gid'] for r in C})==181
assert {g['gid'] for g in G}=={c['gid'] for c in C if c['how']=='longest'}
assert len(L)==16 and V['checked']==85 and V['terminal_mismatches']==0
assert len(I['sets'])==10 and all(s['available']==s['planned']==15 for s in I['sets'])
for g in G:
 assert set(map(int,g['snapshots']))==set(range(200,500,25))|{499}
for v in V['inputs']:
 if isinstance(v['gid'],int):assert v['queen_lengths']==[B[v['gid']]['ends'][s][3] for s in (0,1)]
with (O/'checkpoints.tsv').open() as f:
 rows=list(csv.DictReader(f,delimiter='\t'))
assert len(rows)==69*13*2
assert all(int(r['feed_proxy_pearls'])>0 for r in rows if r['role']=='fed')
src=Path('data/online/smoke/one5-bot/main.cpp').read_text();candidate=(O/'build-check/main.cpp').read_text()
assert candidate==src.replace('constexpr int RALLY_END_FRESH = 0;', 'constexpr int RALLY_END_FRESH = 25;')
assert (O/'build-check/bot').stat().st_size>0
s=(O/'report.md').read_text();words=len('\n'.join(l for l in s.splitlines() if not l.startswith('|')).split());assert words<450
out=dict(time=datetime.now().astimezone().isoformat(),inventory=181,longest=69,local=16,checkpoint_rows=len(rows),queen_field_mismatches=0,queen_both_dead=sum(v['queen_lengths']==[0,0] for v in V['inputs'] if isinstance(v['gid'],int)),report_words_excluding_tables=words,source_sha256=hashlib.sha256(src.encode()).hexdigest(),candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),native_compile='passed; no execution or game')
(O/'completion.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
