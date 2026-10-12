import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
import json
from datetime import datetime
OUT=Path('data/codex/astra/queenbox')
BOTS={'20850','20880','20910','20941','20980'}

def valid(g):return 'excluded' not in g and (not g.get('bot') or g['bot'] in BOTS)
def chosen(t):return next((c for c in t['choices'] if t['moves'] and c['cell']==t['moves'][0]),None)
def delta(t):
    c=chosen(t)
    return c and not t['gate'] and c['penalty']>0 and any(a['penalty']<c['penalty'] and a['s3'] for a in t['choices'])
def danger(t):
    c=chosen(t)
    return c and not c['s3'] and any(a['s3'] for a in t['choices'])
def neigh(t):
    out=[]
    for n in t['neighbors']:
        v=n['kind']
        if v in 'ACE':v+=str(n['id'])+('h' if n['head'] else 'b')
        if n['portal']:v='P>'+v+'('+','.join(map(str,n['cell']))+')'
        if n['pearl']:v+='*'
        out.append(v)
    return '/'.join(out)
def gfmt(g):return f"{g['game']} {g['build']} {'R' if g['ranked'] else 'U'}"

def main():
    raw=list(map(json.loads,(OUT/'games.jsonl').read_text().splitlines()))
    gs=[g for g in raw if valid(g)]
    excluded=[dict(game=g['game'],bot=g.get('bot'),reason=g.get('excluded','bot id outside one1–one5')) for g in raw if not valid(g)]
    (OUT/'excluded.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2))
    cases=[g for g in gs if g['death'] and g['death']['reason']!=3]
    actors={x['game']:x for x in json.loads((OUT/'closure-actors.json').read_text()) if x}
    assert set(g['game'] for g in cases)<=set(actors), 'run closures.py after analyze.py completes'
    facts=[]
    for g in cases:
        d=g['death'];cl=g['closures'][-1];a=actors[g['game']]['actor_turn']
        window=[t for t in g['turns'] if t['round']>=d['round']-12]
        ds=[t for t in window if delta(t)];es=[t for t in window if danger(t)]
        lm=next((t for t in reversed(g['turns']) if t['moves'] and t['event']<=cl['event']),None)
        mc=chosen(lm) if lm else None
        near=any(t['enemy6'] is not None and t['enemy6']<=6 for t in g['turns'][-3:]) or (cl['enemy6'] is not None and cl['enemy6']<=6)
        ally=bool(a and a['actor']!=g['queen'] and a['ally'])
        eligible=ally and a['queen_visible'] and a['all_queen_neighbors_visible'] and bool(a['queen_free'])
        alts=[c for c in a['choices'] if c['queen_exits'] and c['self_exits']>0] if a else []
        facts.append(dict(game=g['game'],near=near,ally=ally,eligible=eligible,child=ally and cl['own_child'],alt=alts,
                          delta_rounds=[t['round'] for t in ds],earlier_rounds=[t['round'] for t in es],last_move=lm['round'] if lm else None,
                          last_move_choice=mc,closure_round=cl['round'],closure_actor=cl['actor'],actor_pearls=a['pearls'] if a else None,
                          queen_gate=g['turns'][-1]['gate']))
    fm={f['game']:f for f in facts}
    all_delta=[(g,t) for g in gs for t in g['turns'] if delta(t)]
    candidate_games=[g for g in cases if fm[g['game']]['delta_rounds']]
    eligible=[f for f in facts if f['eligible']]
    nalt=sum(bool(f['alt']) for f in eligible)
    pearl_candidates=sum(chosen(t)['pearl'] for g,t in all_delta)
    pearl_alternatives=sum(chosen(t)['pearl'] and any(a['pearl'] and a['penalty']<chosen(t)['penalty'] and a['s3'] for a in t['choices']) for g,t in all_delta)
    small=sum(g['cells']<=600 for g in cases)
    existing=sum(f['queen_gate'] for f in facts)
    stats=dict(games=len(gs),excluded=len(excluded),boxed=len(cases),zero_exit=sum(g['death']['free']==0 for g in cases),small=small,
               existing=existing,near=sum(f['near'] for f in facts),ally=len(eligible),child=sum(f['child'] for f in eligible),ally_alternatives=nalt,
               delta_deaths=len(candidate_games),delta_turns=len(all_delta),delta_pearls=pearl_candidates,delta_pearl_alternatives=pearl_alternatives,
               ally_closure_pearls=sum(f['actor_pearls'] for f in eligible),queen_pearls=sum(t['eats'] for g in gs for t in g['turns']),
               queen_turns=sum(len(g['turns']) for g in gs),facts=facts)
    (OUT/'summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    lines=[
      f"[M] 확인: {len(gs)}판의 비머리충돌 여왕 사망 {len(cases)}건은 모두 출구 0이며, {small}건이 ≤600칸 판, {len(eligible)}건은 아군의 마지막 출구 차단이다.",
      f"[E] 카드: QUEEN_DEAD_ALL=true(추가 감점·대안 후보 {len(candidate_games)}건), 아군 마지막 출구 금지({len(eligible)}건 도달). 구조된 사망 수는 아직 미측정이다.",
      '[M/E] 확신: 사건·몸·분열·폐쇄 시각은 높음; 공간항 근사와 변경 후 선택·섭취·생존은 제한적.', '',
      f"[M] 작성 {datetime.now().astimezone().isoformat(timespec='seconds')}. 원본 제출 id로 구분하고 중복 제거; 다른 제출 {len(excluded)}판 제외(`excluded.json`). 상세 재현·제약은 [method.md](method.md), 코드 경로는 [code.md](code.md). R=ranked, U=unranked.", '',
      '| [M] 빌드 / 상대·종류 | 판 | 상자 사망 | ≤600칸 | 아군 폐쇄(직접 자식) | [E] DEAD_ALL 차등 후보 |',
      '|---|---:|---:|---:|---:|---:|']
    keys=sorted(set((g['build'],('ranked '+g['opponent']) if g['ranked'] else g['opponent']) for g in gs))
    for key in keys:
        group=[g for g in gs if (g['build'],('ranked '+g['opponent']) if g['ranked'] else g['opponent'])==key]
        dd=[g for g in group if g['game'] in fm]
        lines.append(f"| {' / '.join(key)} | {len(group)} | {len(dd)} | {sum(g['cells']<=600 for g in dd)} | {sum(fm[g['game']]['ally'] for g in dd)} ({sum(fm[g['game']]['child'] for g in dd)}) | {sum(bool(fm[g['game']]['delta_rounds']) for g in dd)} |")
    lines += ['',f"[M] 마지막 세 차례/폐쇄 시 적 머리 토러스 거리≤6: {stats['near']}/{len(cases)}. 이는 ‘밀림’의 대용 지표이며 인과 판정은 아니다. 기존 여왕 공간항이 적용되는 사망도 {existing}건 있다.", '',
      '| [C] one5 규칙 | 행 | 의미 |','|---|---|---|',
      '| DEAD_END / ROOM / DEAD_PENALTY | 124–126,188,5672–5687 | true / 8 / 6000; 알려진 방 부족은 추가 6000+400×부족. 감점이지 거부 아님. |',
      '| MIN_CELLS / DEAD_ALL / dead_queen | 151,185,3789–3795 | >600 또는 home_closed만 적용; ALL은 false. ALL=true는 harvestable도 금지(1277). |',
      '| WAIT | 775–782,4159–4188 | 실제 여왕 L≥4가 막히면 L2 자식으로 기다림. 머리는 제자리. |',
      '| HERD | 3430–3506,5817–5836 | ≥12마리, 지형 방≥48, 보이는 동료<2; boxed·꼬리 미도달·위험 방향의 양의 당김 억제. |',
      '| EAT_FIRST | 969–972,6003–6041 | 여왕도 적용; 안전한 진주 방향의 영토점수 손실 보상. |', '',
      '[E] HERD의 단독 인과는 미확인이다. 명시적 작은 지형 방에는 보호가 있지만, 이후 동료가 들어와 막는 사건까지 예방하지 않는다.', '',
      '| [E] 카드 | 구체 규칙·삽입점 | [M/E] 도달·비용·틀렸다는 증거 |','|---|---|---|',
      f'| 1. 기존 ALL 켬 | 151행 true. 실제 여왕은 판 크기와 무관하게 기존 dead_queen 공간항·수확 금지를 받는다(1277,5672–5687). | 사망 전 12r 내 추가 감점 방향과 더 낮은 감점·3걸음 대안이 공존한 {len(candidate_games)}건. 전체 {stats["queen_turns"]}차례 중 차등 후보 {len(all_delta)}차례; 그중 실제 첫걸음 진주 {pearl_candidates}개, 대안에도 진주 {pearl_alternatives}개. 이는 선택 변화/섭취 손실 확정치가 아님. 후보 선택이 안 바뀌거나 정상 섭취만 감소하면 기각. |',
      f'| 2. 아군이 여왕 마지막 출구를 막지 않음 | 실제 여왕과 이웃이 보이는 비여왕은 이동 뒤 여왕 출구가 0이면 그 이동을 금지. 가능한 대안 선택; 모두 금지면 무행동. 새 규칙 필요: 5990–6002 후보 검사와 638–876의 ram/escape/stride 포함 모든 이동 실행 전 동일 검사. 자식도 적용. | 실제 폐쇄 {len(eligible)}건(직접 자식 {stats["child"]}); {nalt}건은 자기도 다음 출구가 있는 대안, {len(eligible)-nalt}건은 그런 대안 없음. 막는 실제 차례의 아군 진주 {stats["ally_closure_pearls"]}개가 노출 비용; 여왕 당장 섭취를 금지하지 않지만 이후 비용 미측정. 원본 순간 검사에서 놓치거나, 멈춘 아군 때문에 여왕이 그대로 죽고 먹이만 줄면 기각. |', '',
      '[M] 장면: 1461133 r87은 진주 방과 열린 대안; 1462982 r77은 #102의 다른 길이 있는 차단; 1460566 r79는 방금 낳은 #74의 차단. 아래 전수표와 JSON에 좌표·이웃·선택지를 보존했다.', '',
      '[E] 미확인: 전체 C++ 점수·기억·우회 경로 재실행, 스위치별 인과, CPU, 변경 후 실제 진주·생존. 코드 변경·대전·네트워크는 수행하지 않았다. 포털/다중걸음과 표의 ?를 일반 보행 근사로 확정하지 않는다.', '',
      '[M/E] 전수표: 폐쇄는 실제 마지막 양수→0 사건. Q=여왕, C=직접 자식, A=다른 아군, E=적. 이전 대안은 사망 전 12r의 3걸음 정적 검사([method.md](method.md)); —는 그 검사로 확인 못함. Δr은 추가 감점·대안 후보이고 **veto 확정이 아니다**. =는 이미 게이트 켜짐. 마지막 이동항 D=방 감점, K=known_room 감점, 0=그 근사에서 없음, P/?=포털 등 미재현.', '',
        '| [M] 경기 / 빌드 / 종류 | 상대 / 지도 / 칸 | 사망 r / L | 근접 | 마지막 출구 폐쇄 r:주체 | [M/E] 마지막 이동가능 / 이전 대안 r | [E] DEAD_ALL / 기존 항 |',
      '|---|---|---|---|---|---|---|']
    for g in cases:
        f=fm[g['game']];d=g['death'];cl=g['closures'][-1];a=actors[g['game']]['actor_turn']
        who='Q' if cl['changed']==g['queen'] else 'C' if f['child'] else 'A' if f['ally'] else 'E'
        early=','.join(map(str,f['earlier_rounds'][-2:])) or '—'
        lastfree=next((t for t in reversed(g['turns']) if t['free']>0),None)
        early=(f"r{lastfree['round']}({lastfree['free']}칸) / " if lastfree else '없음 / ')+early
        da='Δr'+','.join(map(str,f['delta_rounds'])) if f['delta_rounds'] else '=' if f['queen_gate'] else '추가; 선택?'
        c=f['last_move_choice']
        term='P/?' if c is None else ('D' if c['dead'] or c['room']<next(t['length'] for t in g['turns'] if t['round']==f['last_move'])+8 else '')+('K' if c['known']<next(t['length'] for t in g['turns'] if t['round']==f['last_move'])+2 else '') or '0'
        if f['last_move'] is not None:
            lm=next(t for t in g['turns'] if t['round']==f['last_move'])
            if not lm['gate'] and term not in ('0','P/?'):term='꺼짐('+term+')'
        if who=='C':who+=f"(출생r{next(s['round'] for s in g['splits'] if s['child']==cl['changed'])})"
        if f['ally']:da+='; 아군행동X'
        lines.append(f"| {gfmt(g)} | {g['opponent']} / {g['map']} / {g['cells']} | {d['round']} / {d['length']} | {'≤6' if f['near'] else '>6/없음'} | {cl['round']}:{who}#{cl['changed']} | {early} | {da}; r{f['last_move']} {term} |")
    lines += ['', '[M] 마지막 세 여왕 차례 시작 판면. 각 칸은 `r (x,y) L: N/E/S/W; 적거리`다. W=벽, S=자기 몸, A/C/E+id+h/b=동료/직접자식/적의 머리/몸, .=빈칸, *=진주, P>=포털 도착칸. 폐쇄 순간 판면·actor 선택지는 `closure-actors.json`에 있다.', '',
              '| [M] 경기 | 끝에서 세 번째 | 끝에서 두 번째 | 마지막 |','|---|---|---|---|']
    for g in cases:
        cs=[]
        for t in g['turns'][-3:]:cs.append(f"r{t['round']} ({t['head'][0]},{t['head'][1]}) L{t['length']}: {neigh(t)}; {t['enemy6']}")
        lines.append('| '+str(g['game'])+' | '+' | '.join(cs)+' |')
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in stats.items() if k!='facts'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
