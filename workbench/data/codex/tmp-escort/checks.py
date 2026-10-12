import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
import report
import dn_tab

here = Path(__file__).resolve().parent
old = report.rows(report.run_check_command('esc_tab.py'))
new = report.rows(report.run_check_command('dn_tab.py'))
assert all(new.get(k) == v for k,v in old.items())
expected_headons = ('19 / 2', '61 / 18')
expected_chases = ('24; 3.5; 9', '31; 2.3; 7')
assert new['head-ons mate v enemy within 5 tiles of her: mate moved / enemy moved'] == expected_headons
assert new['close chases; turns each; lasting 4+'] == expected_chases
checkarms = ['m3b7qk_vh', 'm5es_vh']
data = {a:report.read('dn',a) for a in checkarms}
common = sorted(set.intersection(*(set(d) for d in data.values())))
for a in checkarms:
    c,_ = dn_tab.measure([data[a][k] for k in common])
    total = sum(c[f'dn_L{L}_{t}'] for L in (2,3,4,5) for t in ('pursuer','radius'))
    assert total == c['near_mate_moved']
    print(a, 'sum', total, 'mate moved', c['near_mate_moved'])
print('PASS: all',len(old),'shared table rows; specified head-ons and chases; new length-by-target sums')
for a in ('m3b7qk_vh','m4qd_vh','m5es_vh'):
    data = report.read('dn',a)
    for g in data.values():
        for d in g['deaths']:
            if d['reason'] != 3:
                continue
            assert isinstance(d['L0'],int) and d['L0'] >= 1
            assert isinstance(d['moved'],int) and d['moved'] >= 0
            if d['s'] == 1:
                assert d['qsteps'] in range(9) or d['qsteps'] == 99
                if d['qhead0'] is None:
                    assert d['qsteps'] == d['qtiles'] == 99
                else:
                    q,e,w,h = d['qhead0'],d['starthead'],g['w'],g['h']
                    dx,dy = abs(q%w-e%w),abs(q//w-e//w)
                    assert d['qtiles'] == min(dx,w-dx)+min(dy,h-dy)
    print(a, len(data), 'records; added death fields validated')
