import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
O=Path(__file__).parent
rows=[json.loads(p.read_text()) for p in O.glob('g*.json') if p.stem[1:].isdigit()]
for x in sorted(rows,key=lambda x:(x['v'],x['gid'])):
 if not x['selected']:continue
 d=x['death']; print(f"{x['gid']} v{x['v']} {x['map']} r{d['r']} L{d['L']} cause{d['reason']} actor{d['actor']}")
 for t in x['turns'][-3:]:
  print(' Q',t['r'],t['body'],'act',t['dirs'], 'split',t['split'], 'exit',t['before'],'->',t['endexits'],'end',t['endbody'])
 print(' neighbors',d['snapshot']['neighbors'])
 for c in x['closures'][-3:]:
  print(' CLOSE',c['r'],c['id'],'L',c['L'],'vis',c['qvisible'],'dist',c['distance'],'body',c['body'],'dirs',c['dirs'],'end',c['endbody'],'exits',c['before'],'remove',c['remove_exits'])
print('counts',Counter((x['v'],x['selected']) for x in rows))
