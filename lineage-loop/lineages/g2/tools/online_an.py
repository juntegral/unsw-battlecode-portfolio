import json,gzip,collections,sys,glob,os
d=sys.argv[1]
idx=json.load(open(os.path.join(d,'index.json')))
req=json.load(open(os.path.join(d,'requests.json')))
names={s['teamId']:s['name'] for s in req['sent']}
mp={4:'default',7:'queen',9:'school',11:'trophy',13:'devil',15:'trauma',17:'prisoners',19:'autarky',20:'portals',21:'slithery'}
MAPF={4:'default',7:'queen_of_spades',9:'schooltime',11:'trophy',13:'devil',15:'trauma',17:'prisoners_dilemma',19:'autarky',20:'portals',21:'slithery_fight'}
R="~/01. Project/개인 프로젝트/UNSW/maps/online-20260927/"
for g in idx['games']:
    gid=g['gameId']
    f=gzip.open(os.path.join(d,f'events-{gid}.jsonl.gz'),'rt'); meta=json.loads(f.readline())['meta']
    us=meta['ourSide']; res=meta['result']
    # initial teams from map file order
    team={}
    i=0
    for l in open(R+MAPF[g['map']]+'.map'):
        if l.startswith('DRAGON '): team[i]='A' if l.split()[1]=='0' else 'B'; i+=1
    deaths=collections.Counter(); ourdeath=[]; sprints=collections.Counter(); splits=collections.Counter(); sonar=collections.Counter()
    for l in f:
        e=json.loads(l); t=e['type']
        if t=='dragonSplit': team[e['childId']]=e['team']; splits[e['team']]+=1
        elif t=='dragonDeath':
            tm=team.get(e['id'],'?'); deaths[(tm,e['reason'])]+=1
            if tm==us: ourdeath.append((e['round'],e['reason']))
        elif t=='dragonAction':
            a=e.get('action') or {}
            if a.get('kind')=='move' and len(a.get('steps',[]))>1: sprints[team.get(e['id'],'?')]+=1
        elif t=='sonarPing': sonar[team.get(e['senderId'],'?')]+=1
    them='B' if us=='A' else 'A'
    w=res.get('winner'); r='W' if w==us else ('D' if w is None else 'L')
    print(f"{gid} {names.get(g['opponentTeam'],'?')[:18]:18s} {mp[g['map']]:9s} {r} {res['endReason'][:9]:9s} long {res['team'+us]['longestDragon']}-{res['team'+them]['longestDragon']} "
          f"ourD {sum(v for k,v in deaths.items() if k[0]==us)} {dict((k[1],v) for k,v in deaths.items() if k[0]==us)} theirD {sum(v for k,v in deaths.items() if k[0]==them)} "
          f"spr {sprints[us]}/{sprints[them]} spl {splits[us]}/{splits[them]} sonarThem {sonar[them]} first5deaths {ourdeath[:5]}")
