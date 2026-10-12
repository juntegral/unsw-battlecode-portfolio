// LAST WRITE of the study. Run only after artifact-check.json reports no issues.
'use strict';
const fs=require('fs'),path=require('path'),J=JSON.parse(fs.readFileSync(path.join(__dirname,'tables.json'),'utf8')),A=JSON.parse(fs.readFileSync(path.join(__dirname,'cache/artifact-check.json'),'utf8'));
if(J.status!=='complete-verified'||A.issues.length)throw Error('Cannot summarize an incomplete or failed study');
const sum=a=>a.reduce((s,v)=>s+v,0),pct=v=>(100*v).toFixed(1),m=k=>J.maps[k],w=k=>m(k).classes['elite-winners'],v=k=>m(k).classes['local:v1'];
const pocket=k=>{const ps=m(k).pocketFountains.map(p=>p.counts.top);return {app:sum(ps.map(p=>p.app)),eaten:sum(ps.map(p=>p.eatenWinner+p.eatenLoser))};};
const sf=pocket('Slithery Fight/a'),pd6=pocket('Prisoners Dilemma/6'),pd10=pocket('Prisoners Dilemma/10');
const lines=[
 `동결 2026-10-01 03:41 KST: 상위 ${J.population.expected.top}판, 멈춤 ${J.population.topStalled} 제외, ${J.population.topKept} 유지; 요청 판본 확정 8664판/미확정 6판.`,
 '우리 온라인 1680판(W0–W12 1050+이전 630), 로컬 332판; 질문 지도 온라인 840/로컬 174판.',
 `공간 독립 재계산 ${J.verification.comparedGames}판, 입구 체류 ${J.parkingVerification.comparedGames}판; 불일치 0, ledger checks 전부 0.`,
 '지정 Slithery a 로컬 N=1: 자연 섭취 191:1663, 본진 x-band 머리86%/출현3%, sd 포켓4779/12295=38.9%.',
 `Slithery a 중앙 머리: 승자 ${pct(w('Slithery Fight/a').headShare50_374[2])}% (N=881) / v1 ${pct(v('Slithery Fight/a').headShare50_374[2])}% (N=6), r50–374.`,
 `Slithery b 중앙 머리: 승자 ${pct(w('Slithery Fight/b').headShare50_374[2])}% (N=938) / v1 ${pct(v('Slithery Fight/b').headShare50_374[2])}% (N=6), r50–374.`,
 `Slithery a 포켓 샘: 상위 ${sf.eaten}/${sf.app} 자연 진주 먹힘=${pct(sf.eaten/sf.app)}% (N=881); 로컬98% 존재를 전체에 일반화하지 않음.`,
 `Devil a/b 중앙 머리: 승자 ${pct(w('Devil/a').headShare50_374[2])}/${pct(w('Devil/b').headShare50_374[2])}% (N=792/779), v1 ${pct(v('Devil/a').headShare50_374[2])}/${pct(v('Devil/b').headShare50_374[2])}% (N=6/6).`,
 `Queen Of Spades a/b 샘0; 안전 느린 생성 무리 ${m('Queen Of Spades/a').safeSpawnCandidateGroups.length}/${m('Queen Of Spades/b').safeSpawnCandidateGroups.length}개; 생산 띠 f=.2–.4,.6–.8 우선 (N=844/842).`,
 `Schooltime a 중앙 머리 승자 ${pct(w('Schooltime/a').headShare50_374[2])}% (N=1005)/v1 ${pct(v('Schooltime/a').headShare50_374[2])}% (N=6); 지정 승리35:26, 자연828:732 (N=1).`,
 `Schooltime b 샘0, 안전 느린 생성 무리 ${m('Schooltime/b').safeSpawnCandidateGroups.length}개; 중앙 머리 승자 ${pct(w('Schooltime/b').headShare50_374[2])}% (N=978)/v1 ${pct(v('Schooltime/b').headShare50_374[2])}% (N=6).`,
 `PD6 샘12개 모두 포켓; 상위 먹힘 ${pd6.eaten}/${pd6.app}=${pct(pd6.eaten/pd6.app)}% (N=810); 기존 F 수확 유지.`,
 `PD10 샘8개 모두 포켓; 상위 먹힘 ${pd10.eaten}/${pd10.app}=${pct(pd10.eaten/pd10.app)}% (N=795); 6판본과 분리.`,
 `훅 집합 차분은 재생성 사이 섭취를 누락하는 ${J.previousTurnHookDifferences.length}판 발견; 직접 먹기 이벤트 귀속은 ${J.verification.comparedGames}판 전부 ledger와 일치.`,
 '분산 규칙: 안전한 실제 재생성/(1+배정 머리)/(1+ETA), 겹친 무리 임대 중복 제거; r50/100/250 f 배치 및 지도별 예외를 tables.json/보고서 끝 표에 제공.'
];if(lines.length!==15)throw Error('Summary must have exactly 15 lines');fs.writeFileSync(path.join(__dirname,'SUMMARY.txt'),lines.join('\n')+'\n');console.log('SUMMARY.txt written last: 15 lines');
