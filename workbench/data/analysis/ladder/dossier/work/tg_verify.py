#!/usr/bin/env python3
"""Validate report selection, denominators, layout balancing and reconstruction."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

DOS=Path(__file__).resolve().parents[1]
OUT=DOS/'target'


def main():
    root=DOS.parents[3]
    sys.path.insert(0,str(root/'tools'))
    from ladder_replay import replay
    packed=bytearray()
    for tag in range(256):
        packed.append(tag)
        packed.extend((bit*31+tag)%256 for bit in range(8) if tag & (1<<bit))
        if tag in (0,255):
            packed.append(255)
            if tag==255: packed.extend(bytes(range(255))*8)
    native=subprocess.run([str(OUT/'tg_unpack')],input=packed,stdout=subprocess.PIPE,check=True).stdout
    assert native==replay.unpack_packed(packed)
    a=json.loads((OUT/'scoreboard.json').read_text())
    rows=[json.loads(s) for s in (OUT/'per-game-top1.jsonl').read_text().splitlines()]
    extra=json.loads((OUT/'recount.json').read_text())
    baseline=json.loads((DOS/'fingerprint.json').read_text())
    checks=json.loads((OUT/'validation.json').read_text())
    snapshot=json.loads((OUT/'input-snapshot.json').read_text())
    assert len(rows)==2*a['summary']['games']==2*checks['games']
    assert Counter(r['relation'] for r in rows)=={'us':checks['games'],'them':checks['games']}
    assert len({(r['game'],r['relation']) for r in rows})==len(rows)
    assert {r['game'] for r in rows}=={c['game'] for c in checks['checks']}=={m['id'] for m in checks['metadata']}
    assert all(c['final_matches_rows'] and c['winner_matches_rows'] for c in checks['checks'])
    for path,digest in a['inputs_sha256'].items():
        assert hashlib.sha256((DOS/path).read_bytes()).hexdigest()==digest,path
    for path,digest in snapshot['inputs_sha256'].items():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
    assert a['summary']['layouts']==dict(Counter(r['layout_key'] for r in rows if r['relation']=='us'))
    for r in rows:
        c=extra[str(r['game'])][r['relation']]
        assert c['game'].get('eaten',0)==r['game_counts']['pearls_eaten']
        assert 0<=c['game'].get('drop_eaten',0)<=c['game'].get('eaten',0)
        for w in ('0-100','101-300'):
            assert c[w].get('turns',0)==r['ranges'][w]['turns']
            assert c[w].get('eaten',0)==r['ranges'][w]['pearls_eaten']
            assert 0<=c[w].get('drop_eaten',0)<=c[w].get('eaten',0)
    assert len(a['rates'])==122 and sum(not r['context'] for r in a['rates'])==109
    for r,b in zip(a['rates'],baseline['rates']):
        assert r['pooled']['ours']==b['pooled']['us']
        assert r['pooled']['our_2100plus_opponents']==b['rating_bands']['2100+']['them']
        for pool in [*r['pooled'].values(),*[v for l in r['layouts'].values() for v in l.values() if v is not None]]:
            n,d=pool['numerator_scaled'],pool['denominator']
            assert d>=0 and pool['value']==(n/d if d else None)
        s=r['shared_equal_layouts'];valid=s['valid_layouts']
        assert s['valid_layout_count']==len(valid)
        assert s['layout_count']==len(a['summary']['shared_layouts'])
        for role in ('ours','rank1'):
            value=sum(r['layouts'][l][role]['value'] for l in valid)/len(valid) if valid else None
            assert value==s[role]
        signs=Counter((r['layouts'][l]['rank1']['value']>r['layouts'][l]['ours']['value'])-
                      (r['layouts'][l]['rank1']['value']<r['layouts'][l]['ours']['value']) for l in valid)
        assert (s['rank1_higher'],s['rank1_lower'],s['tied'])==(signs[1],signs[-1],signs[0])
        if valid:
            x,y=s['ours'],s['rank1']
            expected=(y-x)/max(abs(x),abs(y)) if max(abs(x),abs(y)) else 0
            assert r['gap']==expected
        else: assert r['gap'] is None
    assert a['displayed'][:30]==baseline['top30']
    listed={(r['name'],r['window']) for r in a['displayed']}
    for r in a['rates']:
        if not r['context'] and any(g is not None and abs(g)>=.25 for g in (r['gap'],r['pooled_gap'])):
            assert (r['name'],r['window']) in listed
    assert len(a['largest_consistent_gaps'])==12
    indexed={(r['name'],r['window']):r for r in a['rates']}
    assert all(indexed[r['name'],r['window']]['consistent'] for r in a['largest_consistent_gaps'])
    assert all(abs(indexed[r['name'],r['window']]['gap'])<.1 for r in a['matches'])
    lines=(OUT/'scoreboard.md').read_text().splitlines()
    assert len(lines)<=90
    assert sum(s.startswith('| ') for s in lines)==len(a['displayed'])+1
    # Independent examples cover turn rates, cohort ownership and pooled origin shares.
    tests=[('Split frequency','game',lambda r:(1000*r['game_counts']['splits'],extra[str(r['game'])][r['relation']]['game']['turns'])),
           ('Blind direction kept','0-100',lambda r:(100*r['ranges']['0-100']['keeps'],r['ranges']['0-100']['keeps_eligible'])),
           ('Natural birth-cohort harvest','101-300',lambda r:(100*r['ranges']['101-300']['natural_eaten'][r['relation']],r['ranges']['101-300']['natural_births'])),
           ('Dead-dropped share of eaten pearls','game',lambda r:(100*extra[str(r['game'])][r['relation']]['game'].get('drop_eaten',0),r['game_counts']['pearls_eaten']))]
    for name,window,fn in tests:
        for side,role in (('us','rank1'),('them','rank1_opponents')):
            pairs=[fn(r) for r in rows if r['relation']==side];pairs=[p for p in pairs if p[1]>0]
            out=indexed[name,window]['pooled'][role]
            assert out['numerator_scaled']==sum(p[0] for p in pairs)
            assert out['denominator']==sum(p[1] for p in pairs)
    result=dict(verified_at=__import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'),
                games=checks['games'],side_rows=len(rows),behaviour_rates=109,context_entries=13,
                markdown_lines=len(lines),displayed_rates=len(a['displayed']),all_checks='PASS')
    (OUT/'report-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',json.dumps(result),flush=True)


if __name__=='__main__': main()
