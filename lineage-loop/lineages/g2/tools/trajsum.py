import sys,collections
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
team=sys.argv[2] if len(sys.argv)>2 else 'A'
pos=collections.defaultdict(dict); deaths=[]
for r in rows:
    if r[0]=='D': deaths.append(r[1:]); continue
    rnd,i,t,x,y,ln=int(r[0]),int(r[1]),r[2],int(r[3]),int(r[4]),int(r[5])
    pos[rnd][(t,i)]=(ln,x,y)
for rnd in (0,20,40,60,80,100,150,200,250,300,350,400,450,499):
    A=sorted([(v,k[1]) for k,v in pos[rnd].items() if k[0]=='A'],reverse=True)[:4]
    B=sorted([(v,k[1]) for k,v in pos[rnd].items() if k[0]=='B'],reverse=True)[:4]
    print(rnd,'A',A,' B',B)
print('A deaths', [d for d in deaths if d[2]=='A'][:25])
