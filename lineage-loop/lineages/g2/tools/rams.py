import json,gzip,collections,sys,os
d=sys.argv[1]
idx=json.load(open(os.path.join(d,'index.json')))
MAPF={4:'default',7:'queen_of_spades',9:'schooltime',11:'trophy',13:'devil',15:'trauma',17:'prisoners_dilemma',19:'autarky',20:'portals',21:'slithery_fight'}
R="~/01. Project/개인 프로젝트/UNSW/maps/online-20260927/"
tot=collections.Counter()
for g in idx['games']:
    gid=g['gameId']
    f=gzip.open(os.path.join(d,f'events-{gid}.jsonl.gz'),'rt'); meta=json.loads(f.readline())['meta']; us=meta['ourSide']
    team={}; i=0
    for l in open(R+MAPF[g['map']]+'.map'):
        if l.startswith('DRAGON '): team[i]='A' if l.split()[1]=='0' else 'B'; i+=1
    lastAct=None; head={}; c=collections.Counter()
    for l in f:
        e=json.loads(l); t=e['type']
        if t=='dragonSplit': team[e['childId']]=e['team']
        elif t=='dragonAction': lastAct=(e['id'], (e.get('action') or {}).get('steps'))
        elif t=='dragonDeath' and e['reason']=='H':
            victim=e['id']
            if lastAct and lastAct[0]!=victim and team.get(victim)==us:
                mover=lastAct[0]; c['rammed_by_'+('enemy' if team.get(mover)!=us else 'ally')+('_sprint' if lastAct[1] and len(lastAct[1])>1 else '')]+=1
            elif lastAct and lastAct[0]==victim and team.get(victim)==us:
                c['we_moved_into_head']+=1
    tot.update(c)
    if c: print(gid, MAPF[g['map']], dict(c))
print('TOTAL', dict(tot))
