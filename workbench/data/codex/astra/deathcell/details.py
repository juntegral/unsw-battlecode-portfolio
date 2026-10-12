"""Ten repeated cells: true geometry, personal knowledge, and an explicit room-kernel estimate."""
import sys
sys.dont_write_bytecode=True
import json
from collections import deque
from pathlib import Path
import scan
SELECT=[(1471966,(6,2)),(1473235,(22,10)),(1470230,(27,5)),(1462993,(5,2)),
        (1472016,(18,1)),(1472765,(4,6)),(1461132,(17,10)),(1461131,(31,15)),
        (1471964,(14,5)),(1472754,(15,8))]
CAUSES={
1471966:'[E] 출구를 탐색하지 않았다는 설명은 맞지 않는다. 알려진 포털은 score_step(exit)을 호출한다(5902). 완전한 몸 기억이면 last_room=1, last_dead_end=true, pocket=1이며 긴축+주머니 비용 23,800, EAT_BONUS=0이어야 한다. 진주 300이 이 비용을 이겼다는 설명도 맞지 않는다. [C] 포털의 closed는 채우지 않고(5959–5978 대 5998–6000), 여왕의 portal_dead도 저장하지 않는다(5966). 따라서 위험 고리에서 막힌 주머니를 열린 안전 대안으로 취급할 수 있다(6073–6085, QS_HIT_PENALTY=300M:144). 작은 지도 여왕의 dead_queen/is_queen 관문도 별도다(151,185,3790–3795). [E] r218 남쪽의 적 도달과 이 분기 조합은 원인 후보이며, 실측 선택 점수가 없어 최종 순위의 직접 원인으로 확정하지 않는다.',
1473235:'[M] r67 출구가 현재 시야 밖이고 출구의 모든 변을 본 적도 없다. [C] 미지 포털은 score_step을 부르지 않고(5898–5902), 길이 짧은 정찰은 blind 후보를 best_base+정찰 보상으로 바꾼다(5975–5978,6131–6132). [E] 여기서는 ROOM/DEAD_END가 출구를 검증하지 못한다. 커널의 가상 room=334, tail=true는 미지 변을 열림으로 취급한 결과이지 탈출 경로 증거가 아니다. known_room=1 검사가 실측 활성 상태에 적용됐다는 증거는 없다.',
1470230:'[M] r72에는 먼 출구가 시야 밖이지만 그 변들은 이미 기억한다. [E] 여기서는 미지 지형 설명보다 알려진 포털 후보의 soft 비용과 closed 누락을 점검해야 한다. 완전한 몸 기억이면 room=1/tail=false여서 DEAD_END·ROOM·pocket 비용이 모두 걸려야 한다. [C] 활성 여왕의 portal_exit_safe는 현재 시야를 요구하지만(4552–4554), 작은 지도 is_queen 관문 및 any_enterable=false의 강제 포털 경로(790–810)가 그 보호와 다르다. 어느 경로로 선택됐는지 로그 없이 확정하지 않는다.',
1462993:'[M] r31 출구의 벽이 미관측이다. [C] 미지 포털 blind 보상 경로가 출구의 dead-end/room 계산을 생략한다(5898,5977,6131). [E] 미지 변을 열어 계산한 room=341.5/tail=true는 실제 한 칸 방의 공간이 아니다. HARVEST_PORTAL로 여왕이 허용됐다는 설명은 틀리다: real_queen 제외가 명시돼 있다(5966).',
1472016:'[M] r126의 출구 칸은 보이지만 몸의 실제 꼬리는 포털 반대편이라 시야 밖이다. [E] 완전한 몸을 가정한 커널은 room=2/tail=false. 실제 tail_index가 -1이면 일반 last_dead_end와 no-tail 비용의 관문이 열리지 않는다(1654,5664,5672); 기억된 꼬리가 남았는지는 미확인이다. [C] pocket은 몸을 보지 않으며 루프 포털 때문에 48로 반환할 수 있다(3569–3615). 따라서 EAT_BONUS는 pocket에서 막히지 않는다(5739).',
1472765:'[M] r138 L7 여왕이 진주를 먹고 r139 L5로 벽에 죽는다. [E] 커널은 오래 뒤 풀릴 꼬리까지 이어져 room=426/tail=true라 last_dead_end=false로 나온다. 실제 꼬리 기억 여부는 미확인이다. [C] survey_from은 방문 시각만 계산하고 각 이동 뒤의 새 몸을 배치하지 않는다(3089–3228); known_room도 옛 꼬리에 닿으면 충분한 공간으로 반환한다(3557–3558). known_room=1 보조 검사가 활성 여왕이면 추가 보호여야 한다(5680–5685). [E] 이는 단순 진주 보상보다는 시간/몸 전이와 여왕 관문의 진단 대상이다.',
1461132:'[M] r82 L3 여왕이 진주를 먹고 r83 분열 뒤 r84 앞부분 L2가 자기 몸에 죽는다. [E] 커널 room=1/tail=false, pocket=3, EAT_BONUS=0: 진주 보상이 주머니 비용보다 크다는 설명은 아니다. [C] 일반 이동의 closed는 채워진다(5999); 그러나 hard 금지는 아니다. [E] 비여왕의 탈출 분열과 같은 동작이어도 여왕 앞부분을 잃으면 정당한 수확이 아니다. 정확히 어느 여왕 관문이 꺼졌는지는 추가 계측 대상이다.',
1461131:'[M] r81 L3 여왕이 진주를 먹고 r82 분열, r83 앞부분 L2가 벽에 죽는다. [E] kernel room=1/tail=false라 DEAD_END 및 ROOM 관련 비용은 걸려야 한다. [C] 이들은 점수 감점(5656–5685)이지 행동 불허가 아니며, 이미 모든 다른 출구가 막힌 상태에서는 비용만 올려도 살 길이 생기지 않는다. [E] 도착 전 대안을 확인해야 하므로 최종 카드에 대안 관문을 둔다.',
1471964:'[M] r82 L3 여왕은 진주 없는 칸으로 걸어가 r83 벽에 죽는다. [E] kernel room=1/tail=false이고 pocket=48: pocket 자체가 못 잡는 한 칸 폭 끝이다. [C] 일반 last_dead_end(5672)와 긴축 비용은 켤 수 있지만 점수 감점이며, queen known_room 추가 비용은 dead_queen 관문 안에 있다(5680). [E] 진주 탐욕이라는 설명은 이 장면에는 해당하지 않는다.',
1472754:'[M] r95 여왕이 진주 없는 칸에 들어가 r96 벽에 죽는다. [E] kernel room=1256/tail=true는 현재 공간의 미래 꼬리 접근을 허용한 값이다. 영구 한 칸 방이 아니라 큰 열린 성분의 시간별 몸 봉쇄일 수 있어 좌표 전체를 영구 금지해서는 안 된다. [C] reaches_tail이면 last_dead_end는 false(5672), 알려진 꼬리에 닿은 known_room도 limit을 반환(3557–3558)한다. [E] 실제 도착 뒤 다른 드래곤이 출구를 닫았는지는 별도 시간 전이 계측 없이 이 값만으로 확정하지 않는다.'}

def kernel(geo,ctx,dest):
    edges=set(ctx['seen_edges']);seen=set(map(tuple,ctx['seen']));window=set(map(tuple,ctx['window']))
    body=list(map(tuple,ctx['body']));pearls=set(map(tuple,ctx['remembered_pearls']))
    portal_ban=ctx['id']<=1 and geo.w*geo.h>600
    free={c:len(body)-z+1 for z,c in enumerate(body)}
    for i,b in ctx['bodies'].items():
        if int(i)!=ctx['id']:
            for c in map(tuple,b):
                if c in window:free[c]=1<<28
    def step(c,z):
        e=scan.edge_id(geo.w,geo.h,*c,z)
        if e not in edges:
            dx,dy=scan.STEP[z];return ((c[0]+dx)%geo.w,(c[1]+dy)%geo.h)
        k=geo.kind(c,z)
        if k==1:return None
        if k==2 and portal_ban:return None
        if k==2 and not all(e in edges for e in geo.portals[geo.edges[e][1]]):return None
        return geo.dest(c,z)
    dist={dest:1};eaten={dest:int(dest in pearls)};q=deque([dest]);tail=body[-1]
    while q:
        c=q.popleft()
        for z in range(4):
            t=step(c,z)
            if t is None or t in dist or dist[c]+1-eaten[c]<free.get(t,0):continue
            dist[t]=dist[c]+1;eaten[t]=eaten[c]+int(t in pearls);q.append(t)
    room=sum(1 if c in seen else .5 for c in dist);reaches=tail in dist
    kd={dest:1};ke={dest:int(dest in pearls)};q=deque([dest]);need=len(body)+2;known_tail=False
    while q and len(kd)<need:
        c=q.popleft()
        for z in range(4):
            e=scan.edge_id(geo.w,geo.h,*c,z)
            if e not in edges or geo.kind(c,z)!=0:continue
            t=geo.dest(c,z)
            if t in kd or t not in seen or kd[c]+1-ke[c]<free.get(t,0):continue
            if t==tail:known_tail=True;break
            kd[t]=kd[c]+1;ke[t]=ke[c]+int(t in pearls);q.append(t)
        if known_tail:break
    ps={dest};q=deque([dest]);doors=[];pocket=48
    while q:
        c=q.popleft()
        if any(scan.edge_id(geo.w,geo.h,*c,z) not in edges for z in range(4)):break
        for z in range(4):
            k=geo.kind(c,z)
            if k==2:
                e=scan.edge_id(geo.w,geo.h,*c,z)
                t=geo.dest(c,z) if all(a in edges for a in geo.portals[geo.edges[e][1]]) else None
                dx,dy=scan.STEP[z];across=((c[0]+dx)%geo.w,(c[1]+dy)%geo.h)
                if t is not None:doors.append((across,t))
            if k==0:
                t=geo.dest(c,z)
                if t not in ps:ps.add(t);q.append(t)
        if len(ps)>=48:break
    else:pocket=48 if any(a in ps and b not in ps for a,b in doors) else len(ps)
    wanted=3*len(body)+8;dead=not reaches and room<wanted
    pocket_penalty=1000*max(0,len(body)+int(dest in pearls)-pocket//2) if pocket<48 else 0
    return dict(room=room,reaches_tail=reaches,dead_if_tail_known=dead,
                known_room=need if known_tail else min(len(kd),need),pocket=pocket,
                cramped=400*max(0,wanted-room)+5000*max(0,len(body)+2-room)+(0 if reaches else 600),
                pocket_penalty=pocket_penalty,eat_bonus=300 if dest in pearls and not pocket_penalty else 0,
                all_exit_edges_known=all(scan.edge_id(geo.w,geo.h,*dest,z) in edges for z in range(4)),
                destination_in_view=dest in window,tail_visible=tail in window)

def draw(geo,ctx,center,observed=False):
    seen=set(map(tuple,ctx['seen']));window=set(map(tuple,ctx['window']));edges=set(ctx['seen_edges']);pearl=set(map(tuple,ctx['pearls']))
    occ={tuple(c):(i,z) for i,b in ctx['bodies'].items() for z,c in enumerate(b)};out=[]
    def edge(c,d):
        if observed and scan.edge_id(geo.w,geo.h,*c,d) not in edges:return '?'
        return [' ','#','P'][geo.kind(c,d)]
    for yy in range(-3,4):
        y=(center[1]+yy)%geo.h;xs=[(center[0]+xx)%geo.w for xx in range(-3,4)]
        out.append(''.join('+'+edge((x,y),0) for x in xs)+'+');row=''
        for x in xs:
            c=(x,y);ch='*' if c in pearl else '.'
            if c in occ:
                i,z=occ[c];ch=('H' if z==0 else 'o') if int(i)==ctx['id'] else ('a' if ctx['teams'][i]==ctx['teams'][str(ctx['id'])] else 'e')
            if c==center:ch='D'
            if observed and c not in window:ch=':'
            if observed and c not in seen:ch='?'
            row+=edge(c,3)+ch
        out.append(row+edge((xs[-1],y),1))
    out.append(''.join('+'+edge((x,y),2) for x in xs)+'+');return out

def main():
    games={g['gid']:g for g in map(json.loads,(scan.OUT/'games.jsonl').read_text().splitlines())}
    selected=[];md=['# 열 개 반복 사망 칸 [M]\n',
        '[M] D 중심 7×7 타일. 경계 #=벽, P=포털, 공백=열림. H=진입 전 머리, o=자기 몸, a=아군, e=적, *=진주, ?=미관측, :=지형만 기억하고 현재 시야 밖. 왼쪽은 실제 상태, 오른쪽은 개인 관측이다. 포털 진입 전 관측 창은 입구 중심이므로 먼 출구를 중심으로 그린 오른쪽 그림 전체가 시야 밖일 수도 있다.\n',
        '[E] 커널은 one5 survey_from/known_room/pocket_size의 Python 재계산이다. 몸 전체를 안다고 가정한다. 큰 지도의 여왕은 survey 포털 금지를 적용한다. 작은 지도의 home_closed 이력, 영토·위협·목표·음파·생성 countdown·guard beyond 분기는 재현하지 않았으므로 실시간 로그 값이 아니다.\n']
    for gid,cell in SELECT:
        g=games[gid];ds=[d for d in g['deaths'] if d['side']==0 and tuple(d['cell'])==cell and d['cause'] in ('wall','own body','mate body')]
        d=next((d for d in ds if d['queen']),ds[0]);path=Path(g['path'])
        meta=json.loads(path.with_name(f'game-{gid}.json').read_text());root=scan.lr.agg.sb.load_replay(path).root()
        full=scan.census(path,meta,root,{d['id']});d=next(x for x in full['deaths'] if x['event']==d['event'])
        ent=d['entry'];ctx=ent.get('context') if ent else None
        if ctx is None:ctx=d['death_context']
        # JSON-loaded teams have string keys; the live capture has integer keys.
        ctx=json.loads(json.dumps(ctx));geo=scan.Geo(root.text(0));dest=tuple(ent['dest']) if ent else cell;k=kernel(geo,ctx,dest)
        selected.append(dict(gid=gid,map=g['map'],version=g['version'],cell=cell,deaths=ds,representative=d,kernel=k))
        md += [f"\n## {gid} {g['map']} {cell} ({g['version']}) [M]\n",
            f"[M] 같은 칸 사망 {len(ds)}건, 거리 조건 통과 {sum(x['no_enemy3'] for x in ds)}건. r/L/id/Q: "+', '.join(f"{x['r']}/{x['length']}/{x['id']}/{int(x['queen'])}" for x in ds)+'.\n',
            f"[M] 대표 #{d['id']}: r{ctx['r']} {ctx['head']} → {dest}, 포털 {ent['portal'] if ent else None}, 진주 섭취 {ent['pearl'] if ent else None}, 시작 L{len(ctx['body'])}; r{d['r']} {d['cause']} L{d['length']}. 열린 변 성분 {d['component_size']}칸.\n",
            '```text\n실제 지형/몸       관측 누적 (? 미지)\n'+'\n'.join(a+'    '+b for a,b in zip(draw(geo,ctx,cell),draw(geo,ctx,cell,True)))+'\n```\n',
            '[M] 중심 출구 N/E/S/W (종류 0열림/1벽/2포털, 실제 도착): '+str([(geo.kind(cell,z),geo.dest(cell,z)) for z in range(4)])+'.\n',
            '[E] 커널 재계산: `'+json.dumps(k,ensure_ascii=False)+'`.\n']
        md.append(CAUSES[gid]+'\n')
        print(gid,cell,'r',d['r'],k,flush=True)
    (scan.OUT/'ten-cells.json').write_text(json.dumps(selected,separators=(',',':')))
    (scan.OUT/'ten-cells.md').write_text('\n'.join(md))

if __name__=='__main__':main()
