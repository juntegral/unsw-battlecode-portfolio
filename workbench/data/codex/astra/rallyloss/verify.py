import sys
sys.dont_write_bytecode=True
import csv,json,hashlib
from pathlib import Path
OUT=Path('data/codex/astra/rallyloss')
games=list(map(json.loads,(OUT/'games.jsonl').read_text().splitlines()))
assert len(games)==60 and len({g['gid'] for g in games})==60
assert {g['trace']['schema'] for g in games}=={4}
audit=json.loads((OUT/'audit.json').read_text());assert audit['official_final_checks']==audit['official_queen_checks']==120
for file in ['ledger.tsv','ledger400.tsv','audit.tsv']:
    rows=list(csv.DictReader((OUT/file).open(),delimiter='\t'));assert len(rows)==120
    assert all(int(r['residual'])==0 for r in rows)
for g in games:
    expected='21033' if g['label'].startswith('one6') else '20980'
    assert g['base']['bot']==expected,(g['gid'],g['base']['bot'])
    for c in g['trace']['records']:
        assert c['lost_tokens']+c['remaining_tokens']==c['length']
        assert 0<=c['end_transported']<=c['length']
        assert c['end_transported']<=c['end_top']
src=Path('data/online/smoke/one6-bot/main.cpp').read_text()
assert (OUT/'build-check/main.cpp').read_text()==src.replace('constexpr int RALLY_END_FRESH = 25;','constexpr int RALLY_END_FRESH = 5;')
assert (OUT/'build-check/bot').stat().st_size>0
assert (OUT/'build-check/compile.log').stat().st_size==0
report=(OUT/'report.md').read_text()
words=len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split());assert words<=450
values=dict(games=60,ledger350=120,ledger400=120,independent_initial_ledgers=120,residual_failures=0,token_observations=sum(len(g['trace']['records']) for g in games),report_words_excluding_tables=words,card='RALLY_END_FRESH 25 -> 5',native_build=True,source_sha256=hashlib.sha256(src.encode()).hexdigest(),binary_sha256=hashlib.sha256((OUT/'build-check/bot').read_bytes()).hexdigest())
(OUT/'verification.json').write_text(json.dumps(values,indent=2));print(json.dumps(values,indent=2))
