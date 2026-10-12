#!/usr/bin/env python3
"""Make final new script versions; allow newly arrived W12 without source-cache writes."""
from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'prepare.js').read_text()
s=s.replace("const key=d.set+':'+g.gameId, m=mm.get(key), e=em.get(key);", "const key=d.set+':'+g.gameId, e=em.get(key); let m=mm.get(key);")
s=s.replace("if(!m)throw Error('Missing mass ledger '+key);", """if(!m){
      resourceCheck();
      const R=require('../../tools/replay.js').load(dir+'/M'+g.gameId+'.replay');
      const variant=g.mapName==='Prisoners Dilemma'?(R.match.map.initialDragons.length===10?'PD10':'PD6'):null;
      m={...ML.perGame(R,{map:g.mapName,variant}),variant};
      console.log('fresh mass reconstruction '+key);
    }""")
with open(p/'prepare-v2.js','x') as f:f.write(s)
s=(p/'render-v2.py').read_text().replace('14회 실행','15회 실행')
s=s.replace("z=[q for q in lines[tm] if q['born']<=t]", "z=[q for q in lines[tm] if q['born']<t or (t==0 and q['born']==0)]")
with open(p/'render-v3.py','x') as f:f.write(s)
print('created prepare-v2.js and render-v3.py')
