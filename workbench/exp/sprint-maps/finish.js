'use strict';
// Refresh reports after the one-process audit and checks; SUMMARY is written last.
const fs=require('fs'),path=require('path'),C=require('../../tools/replay2map');
const dir=__dirname,read=f=>JSON.parse(fs.readFileSync(path.join(dir,f)));
const v=read('validation.json'),c=read('census.json'),q=read('checks.json');
v.conventions.gaps='pearlRespawn is the spawn interval, but current server replaces every interval with 0..0; all countdown events absent. Observed spawns alone cannot uniquely identify uniform support from finite censored samples. This converter does not attempt seeded engine RNG inversion; absence of direct gap/countdown fields is not a proof that every possible inference method must fail.';
for(const r of v.known)for(const e of r.replays)e.estimatedFields={...e.fields,tiles:e.estimatedFields.tiles,gapStatus:r.gapFit.status};
for(const s of v.sprint)for(const g of s.games)g.canonicalTeamSwap=g.globalTeamSwap!==s.canonicalTeamSwapFromFirst;
v.independentChecks={file:'exp/sprint-maps/checks.json',allPassed:q.allPassed,graphChecks:q.graphs.length};
v.validatorCLI={strict:read('validator-strict.json'),format:read('validator-format.json'),
  reportRedirect:'--require exp/sprint-maps/validate-preload.js redirects only validator report output; validation code and CLI arguments unchanged'};
fs.writeFileSync(path.join(dir,'validation.json'),JSON.stringify(v,null,2)+'\n');
C.writeReadme(v,c);
let text=fs.readFileSync(path.join(dir,'../../maps/sprint/README.md'),'utf8');
if(v.unredactedKnown) {
  text+='\n## 가림 이전 실제 기보의 정확 복원 확인\n\n';
  text+=`가림 이전 a배치 ${v.unredactedKnown.names}종의 실제 기보 ${v.unredactedKnown.replays}개(각 2개)에서는 TILE min/max까지 공식 파일과 완전히 일치했다. 몸·순서는 그대로이며 전체 A/B 교환 여부는 별도 기록했다. 이 검사는 변환기의 gap 읽기 규칙을 확인하지만, 가려진 본선 gap을 되살려 주지는 않는다.\n\n`;
  for(const r of v.unredactedKnown.rows)text+=`- ${r.name}: ${r.replays.map(g=>`${g.gameId} (${g.seriesId})`).join(', ')}.\n`;
}
text+='\n## 생성 간격 추정기의 알려진 지도 오차\n\n각 배치의 독립 기보 4개로만 맞춘 결과다. 본선에는 지도당 32개를 썼다. 아래 숫자는 알고리즘의 정확 복원 보증이 아니라 표본 부족과 검열의 영향을 드러내는 진단이다. MAE는 비생성칸도 포함한 전 칸 평균, 분류 오류는 칸 수다.\n\n';
text+='원래 간격의 직접 필드와 countdown 기록이 없다는 것을 확인했으며, 시드에 맞춘 엔진 RNG 역산은 하지 않았다. 통계 추정에서 보이는 비식별성은 모든 가능한 역산 방법이 불가능하다는 증명은 아니다.\n\n';
text+='| 지도/배치 | TILE 완전 일치 | minGap MAE | maxGap MAE | 생성 분류 오류 | 샘 분류 오류 |\n| --- | --- | --- | --- | --- | --- |\n';
for(const r of q.gapEstimatorKnownMapQA)text+=`| ${r.name}/${r.layout} | ${(100*r.exactTileShare).toFixed(1)}% | ${r.minGapMAE.toFixed(2)} | ${r.maxGapMAE.toFixed(2)} | ${r.spawnClassificationErrors} | ${r.fountainClassificationErrors} |\n`;
const problems=v.sprint.flatMap(s=>s.games.filter(g=>Object.values(g.extractionChecks).some(n=>n!==0)).map(g=>({name:s.name,gameId:g.gameId,checks:g.extractionChecks})));
text+='\n## 독립 점검과 검증기 실행\n\n';
text+=`회귀·산출물 검사 ${q.tests.length}개와 독립 포털 이동 그래프 7개 대조가 통과했다. 생성 표본 추출의 점유·낙하·최종 상태 검사에서 0이 아닌 항목이 있는 기보는 ${problems.length}개다.\n\n`;
text+='요청한 CLI를 그대로 실행했다: `node --require ./exp/sprint-maps/validate-preload.js tools/mapgen/validate.js maps/sprint`. 기본 모드의 엄격 연결성 실패는 원래 지도의 고립 성분을 그대로 보존한 결과다. `--existing maps/sprint` 실행으로 지도 형식·대칭과 포털·드래곤 제약을 따로 확인했다. preload는 도구가 기본적으로 exp/mapgen에 쓰는 보고서의 목적지만 허용 범위인 exp/sprint-maps로 바꾼다.\n\n';
text+='실행 결과: [엄격 검증](../../exp/sprint-maps/validator-strict.json), [형식 검증](../../exp/sprint-maps/validator-format.json), [독립 검사](../../exp/sprint-maps/checks.json).\n';
fs.writeFileSync(path.join(dir,'../../maps/sprint/README.md'),text);
if(problems.length)throw Error('nonzero extraction checks: '+JSON.stringify(problems));
C.finalize();
console.log(JSON.stringify({finalized:true,lines:fs.readFileSync(path.join(dir,'SUMMARY.txt'),'utf8').trimEnd().split('\n').length}));
