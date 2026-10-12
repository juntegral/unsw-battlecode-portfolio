import sys
sys.path.insert(0,'mytools'); sys.path.insert(0,'tools')
import trace, re
for path in sys.argv[2:]:
    out = trace.run(path, 0, 10**9, int(sys.argv[1]))
    print(path)
    deaths={'A':0,'B':0}
    for l in out:
        if 'DEATH' in l:
            m=re.search(r'team=(\w)',l); deaths[m.group(1)]+=1
        if l.startswith('r'):
            a=re.findall(r'(\d+)AL(\d+)',l); b=re.findall(r'(\d+)BL(\d+)',l)
            qa=[int(L)-0 for i,L in a if int(i)<2]; qb=[int(L) for i,L in b if int(i)<2]
            print(' ',l.split(':')[0],'A n=%d tot=%d max=%d q=%s dead=%d | B n=%d tot=%d max=%d q=%s dead=%d'%(len(a),sum(int(L) for i,L in a),max([int(L) for i,L in a] or [0]),qa,deaths['A'],len(b),sum(int(L) for i,L in b),max([int(L) for i,L in b] or [0]),qb,deaths['B']))
    print(' ',out[-1])
