exec(open('data/codex/astra/sweep/0559/loss2/detail.py').read().split('for gid in (')[0])
gid=1494959;d=json.loads((OUT/f'{gid}-detail.json').read_text());b=json.loads((OUT/f'{gid}-base.json').read_text());w,h=d['w'],d['h'];t=next(t for t in d['queen'] if t['round']==419);g=cr.Geometry(w,h,[tuple(map(int,x.split()[1:4])) for x in b['text'].splitlines() if x.startswith('EDGE ')])
res=[]
for dest in (60+31*w,60+33*w):
 qb=[dest]+t['start'];qb=qb if dest in t['pearls'] else qb[:-1]
 eb=t['bodies']['840'];fixed=set(qb[1:])|{c for i,bb in t['bodies'].items() if int(i) not in (1,840) for c in bb};pe=set(t['pearls'])-{dest};queue=deque([(eb,[],frozenset())]);found=None
 while queue:
  body,path,eaten=queue.popleft();paid=len(path)>=2
  if len(path)>=5 or paid and len(body)<=2:continue
  for di,(kind,cell) in enumerate(g.moves[body[0]]):
   if kind==1 or cell in body or cell in fixed:continue
   if cell==dest:found=path+[di];break
   eat=cell in pe and cell not in eaten;nb=[cell]+body
   if not eat:nb.pop()
   if paid:nb.pop()
   queue.append((nb,path+[di],eaten|{cell} if eat else eaten))
  if found:break
 res.append(dict(queen_destination=[dest%w,dest//w],attacker=840,initial_length=len(eb),max_steps=5,ram_path=found,ram_directions=''.join('NESW'[x] for x in found) if found else None))
print(json.dumps(res));(OUT/'dynamic-check.json').write_text(json.dumps(res,indent=2))
blocked={c for bb in t['bodies'].values() for c in bb}-{t['start'][-1]}
dist={t['bodies']['840'][0]:0};queue=deque(dist)
while queue:
 c=queue.popleft()
 for kind,n in g.moves[c]:
  if kind!=1 and n not in dist and n not in blocked:dist[n]=dist[c]+1;queue.append(n)
static={str([n%w,n//w]):dist.get(n) for n in (60+31*w,60+33*w)}
assert list(static.values())==[4,4]
(OUT/'static-check.json').write_text(json.dumps(static,indent=2))
print('Static model, our tail passable:',static)
