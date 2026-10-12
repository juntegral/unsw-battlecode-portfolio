'use strict';
const fs=require('fs'),path=require('path'),OUT=__dirname,read=n=>JSON.parse(fs.readFileSync(path.join(OUT,n+'.json'))),T=read('tables'),C=read('checks'),A=read('archive');
if(T.status!=='complete'||C.status!=='PASS'||!A.verified)throw Error('Final checks/archive incomplete');
const lines=[
 '완료: 동결 2026-10-01 05:11:57 KST; 원자료 N=10,149/10,149; 상위 요청 9,422 + W0–W12 525 + 로컬 202.',
 '집계 유지 N=10,004; stalled 상위 145 제외; 판본 미확정 7은 별도; 물리 에피소드 1,372,405, 수확 가족 1,027,866.',
 '전체 독립 이동·드롭·2-core 검산 N=10,149: 모든 차이 0; 최초 질주 비용 귀속 오류 790판 수정 이력 보존.',
 '샘 포켓 부분집합 독립 검산 N=5,929 차이 0; PD 샘 몸 점유 독립 검산 N=1,829 차이 0.',
 'Slithery a 승자 샘 포켓 +16.74/판(N=914), 전체 포켓 −11.93; W12 −7.60(N=5), 아군 드롭 회수 27.96%.',
 'Slithery b 승자 샘 포켓 +30.87/판(N=966), 전체 +10.82; W12 −7.50(N=2).',
 'PD6 승자 +32.08/판(N=849), 자연/사망 1.667; W12 −4.40(N=5), 자연/사망 1.012, 회수 98.97%.',
 'PD10 온라인 N=48: 자연 정확히169인 판 40, 순질량+2인 판 42; v0t/v1 로컬 각각6/6은169·+2.',
 'PD10 승자 −0.09/판(N=835), 500도달 −5.74(N=69); 길이10–11 고리는 대체재료를 먹어 길이를 유지.',
 'Trauma 샘 포켓 승자 +115.85/판(N=1,869), W12 +40.71(N=7); 효율보다 서비스량·내부 후손 사슬이 차이.',
 'Schooltime a/b·QoS a/b 포켓 샘0: 반복 농사 제외; 승자 모든 포켓 −17.0/−8.9/−9.7/−7.9(N=1,056/1,022/883/876).',
 '권고 가설: 비왕 L2–3, 자연≥2, 자식 출구·분열 슬롯 예약, SPLIT L−2, 반출→입구 비움→드롭→다음 조각.',
 '주차 원인 근거: F/sd 포켓 배정 + HOLD2 + 공간 벌점; 최종 v1 a 포켓sd 0/2,739(N=2); PD birthLen 유지가 성장 제한.',
 `정독 경제 사례 7판 + 목표 실패 4판, 클래스/후보 N·게임ID·라운드 명시; 실제 보드 그림3; QA ${C.checks.toLocaleString('en-US')}개 통과.`,
 'episodes.jsonl.gz·tables.json·한국어 보고서 완료; 수익은 관측 기준(신규 봇 효과 미검증); 지정 범위만 작성, 네트워크·업로드·커밋 없음.'
];if(lines.length!==15)throw Error('Summary must have 15 lines');fs.writeFileSync(path.join(OUT,'SUMMARY.txt'),lines.join('\n')+'\n');console.log('Wrote SUMMARY.txt LAST (15 lines)');
