import sys
sys.dont_write_bytecode=True
import json,re,hashlib,subprocess,datetime
from pathlib import Path
O=Path(__file__).resolve().parent
games=[json.loads(p.read_text()) for p in sorted(O.glob('game-*.json'))]
assert len(games)==len({g['gid'] for g in games})==60
assert all(len(g['rows'])==64 for g in games)
assert all(set(g['snaps'])=={str(r) for r in range(0,151,10)} for g in games)
assert all(set(map(tuple,g['natural_bearing']))<=set(map(tuple,g['bearing'])) for g in games)
known={}
for label in ('one5-w1','one5-c1'):
    for line in (O.parent/'midgame'/(label+'-ledger.jsonl')).read_text().splitlines():
        g=json.loads(line);known[g['gid']]=g
checkpoints=0
for g in games:
    if g['gid'] not in known:continue
    old=known[g['gid']]
    for r in (0,50,100,150):
        for s in (0,1):
            new=g['snaps'][str(r)];ref=old['snaps'].get(str(r),old['ends'])[s]
            assert len(new['heads'][s])==ref[0]
            assert sum(h[3] for h in new['heads'][s])==ref[1]
            natural=sum(e[0]<=min(r,old['last']) and e[1]==s and e[3]=='n' for e in old['eats'])
            assert new['nat'][s]==natural,(g['gid'],r,s,new['nat'][s],natural)
            checkpoints+=1
src=Path('data/online/smoke/one7-bot/main.cpp');text=src.read_text();build=[]
for line in (O/'variants.txt').read_text().splitlines():
    name,changes=line.split('=');const,value=changes.split(':')
    pattern=r'(constexpr\s+(?:bool|int|double)\s+'+re.escape(const)+r'\s*=\s*)([^;]+);'
    assert len(re.findall(pattern,text))==1
    old=re.search(pattern,text).group(2)
    patched=re.sub(pattern,lambda m:m[1]+value+';',text)
    path=O/'build-probe.cpp';path.write_text(patched)
    result=subprocess.run(['c++','-std=c++20','-O2','-fsyntax-only','-I',str(src.parent),str(path)],capture_output=True,text=True)
    build.append(dict(name=name,constant=const,old=old,new=value,status=result.returncode,stderr=result.stderr))
    assert result.returncode==0,(name,result.stderr)
    print(name,'syntax OK',flush=True)
result=dict(time=datetime.datetime.now().astimezone().isoformat(),games=len(games),rows=sum(len(g['rows']) for g in games),
            independent_one5_checkpoint_sides=checkpoints,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
            source_lines=len(text.splitlines()),builds=build,check='native syntax only, no game or CPU validation')
(O/'verification.json').write_text(json.dumps(result,indent=2))
