import json,re
from pathlib import Path
P=Path('data/codex/astra/topqueen2');S=json.loads((P/'summary.json').read_text());C=json.loads((P/'convergence-summary.json').read_text())
lines=[];inside=False
for line in (P/'tables.md').read_text().splitlines():
 if line.startswith('|공격 팀'):inside=True
 if inside and line.startswith('|'):
  a=line.strip('|').split('|')
  if a[0]=='공격 팀 [M]':v='3r 접근 머리 중앙값 / 2+건'
  elif a[0]=='---':v='---'
  else:
   m=re.search(r'\((\d+)\)$',a[0]);key=m[1] if m else 'one10-1119' if a[0].startswith('one10') else 'one9-1119';c=C[key];v=f"{c['approach_median']}/{c['approach2plus']}"
  a.insert(7,v);line='|'+'|'.join(a)+'|'
 elif inside:inside=False
 lines.append(line)
extra=['|보조: WHQ·Cache [M]|N|우리/상대 여왕 생존|생존 여왕 평균L 우리/상대|','|---|---|---|---|']
for v in [5,6,7,8]:
 for o,name in [(87,'WHQ'),(952,'Cache')]:
  a=S[f'one{v}-opp{o}'];b=S[f'opp{o}-one{v}'];extra.append(f"|one{v} 대 {name}|{a['n']}|{a['alive']}/{b['alive']}|{a['endL']}/{b['endL']}|")
extra += ['|one9 대 WHQ·Cache|0|미측정|미측정|','|one10 대 WHQ·Cache|0|미측정|미측정|']
body=(P/'report-body.md').read_text();assert len(body.split())<600
(P/'report.md').write_text(body+'\n'+'\n'.join(lines)+'\n\n'+'\n'.join(extra)+'\n')
print('report non-table words',len(body.split()))
