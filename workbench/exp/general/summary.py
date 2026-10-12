"""Write the requested fifteen-line summary LAST, after every deliverable/audit."""
import json,pathlib,datetime
O=pathlib.Path(__file__).resolve().parent;T=json.load(open(O/'tables.json'));Q=json.load(open(O/'qa.json'));assert T['status']=='complete' and not Q['issues'];p=T['population'];c=p['counts'];F=T['verification']['fit'];I=T['sprintCheck']
lines=[
'미지 지도 일반화 연구 완료 — '+datetime.datetime.now(datetime.timezone.utc).isoformat(),
'산출물: exp/general/tables.json; research/observations/general-principles.md; 이 SUMMARY.txt (마지막 작성).',
f"고유 기보 N={p['processed']:,}: top {c['top']:,}, 우리 {c['online']:,}, 추가 elite {c['elite']:,}; 누락 N={len(p['missing'])}.",
f"top 멈춤 제외 N={c['topStalled']}; 유지 N={c['top']-c['topStalled']}; 미확정 판본 N={c.get('topUnknownLayout',0)} 별도 보존.",
'일반화 단위 N=15판본·10지도명·5고정 기하군; 21행동 목표, nested 단조/작은 tree/상수 검증.',
'방법: 전수 재구성 → 배타적 부류 N 및 행동 → 대표 정독 N='+str(T['deepReads']['N'])+'팀-판, ID·라운드 저장.',
'관측: r0 크기/wrap 정확; r30 아군 합집합 시야는 공유 상한; 실제 countdown reset 오차 검증 N=0.',
'전이 후보: 중앙 공급 몫→middle100, 지도/기하군 제외 MAE '+f"{T['fits']['middle100']['leaveFamilyOut']['score']['MAE']:.4f}/{T['fits']['middle100']['leaveGeometryFamilyOut']['score']['MAE']:.4f}.",
'전이 후보: 포켓 공급 몫→포켓 자연 섭취 몫, MAE '+f"{T['fits']['pocketIntakeShare']['leaveFamilyOut']['score']['MAE']:.4f}/{T['fits']['pocketIntakeShare']['leaveGeometryFamilyOut']['score']['MAE']:.4f}; oracle 입력 조건.",
'초반 head 공식은 미확증: heads100 r30 MAE '+f"{T['fits']['heads100']['runtimeEarly']['30']['leaveFamilyOut']['score']['MAE']:.3f} > 상수 {T['fits']['heads100']['leaveFamilyOut']['baseline']['MAE']:.3f}; 7/13/23/38은 조건부 행동 기준.",
'요새 gate: area≤1100, 씨앗왕≥8, 인증 cycle≥L+4, 보호 생산/guard; 신규 정책 효과 N=0.',
'전환: r250/350/400 점검·TTL4·first drop1–3·큰 packet r460 이전은 실험 후보, 신규 실행 N=0.',
f"독립 대조: 행동 {p['processed']:,}판, 기하 15판본, 예측 {F['checks']['predictionN']}개/점수 {F['checks']['scoreN']}개; 불일치 N=0.",
f"elite 최종 로컬 확인 N={I['uniqueN']}; 미지 지도 N={I['unknownN']}; sprint 이전 종료, 사전 동결 out-of-sample 부록 포함.",
'QA 통과; 최대 2 worker·메모리/디스크 gate·gzip 캐시; 허용 범위만 작성, 네트워크/업로드/게임/commit N=0.'
]
assert len(lines)==15
(O/'SUMMARY.txt').write_text('\n'.join(lines)+'\n')
print('SUMMARY LAST',len(lines),'lines')
