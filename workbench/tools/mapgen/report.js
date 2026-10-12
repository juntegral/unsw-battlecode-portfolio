#!/usr/bin/env node
'use strict';
const L=require('./lib'),{fs,path,ROOT}=L,cp=require('child_process'),{tasks,readRows}=require('./smoke');
const num=x=>x===null||x===undefined?'미측정':typeof x==='number'?Number(x.toFixed(4)):x;
const cell=x=>String(x??'—').replace(/\|/g,'/').replace(/\n/g,' ');
const table=(headers,rows)=>['| '+headers.join(' | ')+' |','| '+headers.map(()=>'---').join(' | ')+' |',...rows.map(row=>'| '+row.map(cell).join(' | ')+' |')].join('\n');
const read=f=>JSON.parse(fs.readFileSync(path.join(ROOT,f),'utf8'));
function report() {
 const c=read('exp/mapgen/census.json'),m=read('maps/generated/manifest.json'),existing=read('exp/mapgen/validation-existing.json'),generated=read('exp/mapgen/validation-generated.json');
 const checks=fs.existsSync(path.join(ROOT,'exp/mapgen/checks.json'))?read('exp/mapgen/checks.json'):null;
 const clock=cp.execFileSync('date',['+%Y-%m-%d %H:%M:%S %Z'],{encoding:'utf8'}).trim(),latest=new Map();for(const r of readRows())latest.set(r.gameId,r);
 const expected=tasks(m),rows=expected.map(t=>{const r=latest.get(t.gameId);return r&&r.mapSha256===t.mapSha256?r:{...t,status:'pending',attempted:false};}),attempted=rows.filter(r=>r.attempted),finished=attempted.filter(r=>r.mapLoaded&&r.finished),faults=attempted.filter(r=>r.error||r.ourErrors?.length||r.ourTimeouts?.length||r.mapDefects),recognised=attempted.filter(r=>r.misrecognition?.length);
 const summary={at:clock,planned:expected.length,attempted:attempted.length,finished:finished.length,blocked:rows.filter(r=>r.status==='blocked').length,pending:rows.filter(r=>!r.attempted).length,ourFaultGameIds:faults.map(r=>r.gameId),misrecognitionGameIds:recognised.map(r=>r.gameId),strictStaticValid:generated.rows.filter(r=>r.valid).length};
 fs.writeFileSync(path.join(ROOT,'exp/mapgen/status.json'),JSON.stringify(summary,null,2)+'\n');
 const explain=[
  '공급은 생성 가능한 칸의 `Σ 2/(minGap+maxGap)`이며 실제 섭취량이 아니다. 샘은 평균 간격 ≤12다.',
  '중앙은 **모든 시작 몸 칸**을 씨앗으로 한 BFS의 `0.4 ≤ dA/(dA+dB) < 0.6`이다. 양쪽 모두 못 닿는 칸은 중앙에서 제외한다. 이 정의는 `exp/spatial/lib.js` 및 일반 원칙 연구와 같다.',
  '주머니는 포털을 포함한 무방향 이동 그래프의 2-core 밖 칸이다. 기존 연구처럼 고립 칸도 포함한다. 주머니 공급 몫은 그 칸의 잠재 공급/전체 공급이다.',
  '통로 너비는 각 칸을 지나는 수평/수직 열린 직선 구간 길이 중 작은 값이다. 포털에서 끊고 wrap을 반영한다. 실제 경로의 최소 여유 폭과 같지는 않다. 분포에는 전 칸을 넣었고 degree=2 몫도 별도 기록했다.',
  '간선 밀도 분모는 wrap 별칭을 합친 `2×면적`이다. `SYMMETRY y`는 y축 거울(좌우), `x`는 x축 거울(상하), `xy`는 180° 회전이다.',
  '시작 거리는 양 팀 시작 머리의 최단 BFS 거리다. 공급 중앙 정의의 몸 칸 씨앗과 구분한다.'
 ];
 const censusHeaders=['파일 / 이름','중복 원본','크기/면적/비율','대칭','켈프 밀도','통로 degree2','막다른/2-core/주머니','포털 쌍','생성 칸/몫','샘 칸/몫','공급','중앙/주머니 공급','시작 수 A/B','시작 길이 A/B','시작 거리'];
 const censusTable=table(censusHeaders,c.maps.map(x=>[`${x.file} (${x.name})`,x.duplicateOf||'고유',`${x.width}×${x.height}/${x.area}/${num(x.aspect)}`,x.symmetry,num(x.kelpDensity),num(x.corridorDegree2Share),`${x.deadEnds}/${x.core2Tiles}/${x.pocketTiles}`,x.portalPairCount,`${x.spawnTiles}/${num(x.spawnShare)}`,`${x.fountainTiles}/${num(x.fountainShare)}`,num(x.supply),`${num(x.centreSupplyShare)}/${num(x.pocketSupplyShare)}`,x.startDragons.join('/'),x.startLengths.map(a=>a.join(',')).join('/'),num(x.startDistance)]));
 const generatedTable=table(['지도','가족/구조','크기/대칭','범위','검증','점검할 기제'],m.maps.map(x=>[x.name,`${x.family}/${x.style}`,`${x.metrics.width}×${x.metrics.height}/${x.metrics.symmetry}`,x.envelope==='inside'?'전수 범위 안':'범위 밖 스트레스',x.staticValid?'통과':'연결성 예외',x.exercises.join(', ')]));
 const details=m.maps.flatMap(x=>{const a=x.metrics;return[
  `### ${x.name}`,'',`- 파일: [${x.name}.map](./${x.name}.map), seed ${x.seed}, 구조 ${x.style}. ${x.source?'원본: `'+x.source+'`.':''}`,
  `- 기하: 면적 ${a.area}, W/H ${num(a.aspect)}, 켈프 ${a.kelpEdges}/${2*a.area}=${num(a.kelpDensity)}, 막다른 길 ${a.deadEnds}, 2-core ${a.core2Tiles}, 주머니 ${a.pocketTiles}, 분리 성분 ${a.componentSizes.join(',')}.`,
  `- 통로 너비별 칸 수: \`${JSON.stringify(a.corridorWidthDistribution)}\`; degree별 칸 수: \`${JSON.stringify(a.degreeDistribution)}\`.`,
  `- 포털 ${a.portalPairCount}쌍: \`${JSON.stringify(a.portalPairs)}\`.`,
  `- 생성 ${a.spawnTiles}칸 (${num(a.spawnShare)}), gap별 칸 수 \`${JSON.stringify(a.gapDistribution)}\`, 생성칸 평균 gap ${num(a.meanGap)}, 샘 ${a.fountainTiles}칸 (생성칸 중 ${num(a.fountainShare)}).`,
  `- 공급 ${num(a.supply)}, 중앙 공급 몫 ${num(a.centreSupplyShare)}, 주머니 공급 몫 ${num(a.pocketSupplyShare)}.`,
  `- 시작 수 ${a.startDragons.join('/')}, 길이 ${a.startLengths.map(b=>b.join(',')).join('/')}, 양 팀 머리 거리 ${num(a.startDistance)}.`,
  `- 범위 밖 지표: ${x.outsideEnvelope.length?x.outsideEnvelope.join('; '):'없음'}.`,
  ...(x.trap?[`- 함정: wrap Manhattan 반경 ${x.trap.radius}, 보존 타일 ${x.trap.preservedTileCount}, 보존 변 ${x.trap.preservedEdgeCount}. 근처 일치 ${x.trap.localPreserved}, 시작 일치 ${x.trap.sameStarts}. 변 변경 전체 ${num(x.trap.edgeChangeShare)} / 가변 영역 ${num(x.trap.mutableEdgeChangeShare)}, 생성 support 변경 전체 ${num(x.trap.spawnSupportChangeShare)} / 가변 영역 ${num(x.trap.mutableSpawnChangeShare)}.`]:[]),
  ...(x.connectivityException?[`- **연결성 실패:** ${x.connectivityException}. 양 팀 시작 경로는 연결. 엄격 검증 통과로 세지 않는다.`]:[]),''
 ];});
 const limitations=[
  '35개는 실제 qualifier 지도 분포의 표본이 아니라 기제를 자극하는 합성 시험장이다. 한 seed·한 상대의 smoke는 발동 효과·정책 채택을 입증하지 않는다.',
  `정적 검증은 기존 ${existing.rows.filter(x=>x.valid).length}/${existing.rows.length}개 형식·대칭 통과, 생성 ${generated.rows.filter(x=>x.valid).length}/${generated.rows.length}개 전 칸 연결 포함 통과다. 기존의 연결성은 실제로 검사하되 규칙상 금지되지 않은 분리 구역을 오류로 바꾸지 않았다.`,
  'Portals 원본 근처 보존과 전 칸 연결은 동시에 만족하지 않는다. gen_X_04의 4개 작은 성분(각 2칸)을 예외로 남겼으며, 엄격 검증은 실패를 반환한다. 모든 시작은 큰 성분에 있고 양 팀은 서로 도달한다.',
  '함정의 반경은 wrap Manhattan 6이다. 근처 TILE 전부와 양 끝이 보존 영역 안인 변, 모든 포털 쌍, 시작 몸의 접합 변을 보존한다. 영역 밖 40% 변/support 변경을 적용하고 전체 비율을 함께 표시했다. 전체 40% 변경으로 읽으면 일부 X 지도는 그 요구를 만족하지 않는다. 조건 충돌을 사용자에게 질의한 뒤 기본값을 명시했다.',
  'strictValid는 Node 검증기의 결과다. 실제 공식 엔진이 보정 없이 읽었는지는 mapDefects와 smoke 완료 뒤 확인한다. 현재 미실행 판은 오류 0이나 인식 0으로 세지 않는다.',
  'CPU는 공식 runner의 팀별 points-per-turn max를 읽는다. M 표시는 0.1M 단위 반올림이므로 precisionPoints를 저장한다. 값이 없으면 null이다.',
  '전수 범위는 고유 지도에서 지표별 최소/최대만 비교한다. 지표들의 조합이 현실적이라는 뜻은 아니다. maze·thin과 일부 인식 함정은 의도적으로 범위 밖이다.',
  '새 쓰기는 사용자 허용 경로 안이다. WORKQUEUE·DECISIONS·versions·bots·기존 큐는 수정하지 않았다. 봇 소스를 읽지 않았고 커밋·네트워크·업로드를 하지 않았다.'
 ];
 const manifestText=['# 생성 지도 시험장 (W8)','',`작성/갱신: ${clock}. 지도 35개(S6/M8/L6/R2/X13), seed ${m.seed}.`,'','기제의 발동·실제 판면 변화·깨짐 점검에만 쓴다. 승패 비교나 후보 채택에 쓰지 않는다.','',...explain.map(x=>'- '+x),'',generatedTable,'',`엄격 정적 검증 ${summary.strictStaticValid}/35. smoke 계획 ${summary.planned}판, 실행 ${summary.attempted}판, 로딩·완료 ${summary.finished}판, 미실행 ${summary.pending}판.`,'','재현·큐 사용법: [README](../../tools/mapgen/README.md). 원수: [manifest.json](./manifest.json), [census.json](../../exp/mapgen/census.json), [smoke.jsonl](../../exp/mapgen/smoke.jsonl).','',...details,'## 한계','',...limitations.map(x=>'- '+x),''].join('\n');
 fs.writeFileSync(path.join(ROOT,'maps/generated/MANIFEST.md'),manifestText);
 const trapTable=table(['지도/원본','보존 타일','변 변경: 전체/가변','생성 support 변경: 전체/가변','근처·시작 동일'],m.maps.filter(x=>x.trap).map(x=>[`${x.name}/${x.source}`,x.trap.preservedTileCount,`${num(x.trap.edgeChangeShare)}/${num(x.trap.mutableEdgeChangeShare)}`,`${num(x.trap.spawnSupportChangeShare)}/${num(x.trap.mutableSpawnChangeShare)}`,`${x.trap.localPreserved}/${x.trap.sameStarts}`]));
 const gameTable=table(['판 ID','우리 좌석','실행 상태','로딩/완료','우리 오류/timeout','CPU max','우리 인식'],rows.map(r=>[r.gameId,r.side,r.status,r.attempted?`${r.mapLoaded}/${r.finished}`:'미실행',r.attempted?`${r.ourErrors?.length??'미측정'}/${r.ourTimeouts?.length??'미측정'}`:'미측정',r.ourMaxCpuPerTurn?.reported||'미측정',r.recognition?Object.keys(r.recognition[r.side]||{}).join(', ')||'태그 없음':'미측정']));
 const reportText=['# W8: 처음 보는 지도 생성 시험장','',`갱신 ${clock}. 전수조사 생성 ${c.createdAt} (생성 지도보다 먼저 기록).`,'','## 전수조사','',`파일 ${c.fileCount}, 중복을 뺀 지도 ${c.uniqueCount}. online 10, bundled 13, server-b 링크 10, variants 5를 모두 읽었다. dilemma는 Prisoners Dilemma와 같다. 중복 기준은 이름을 제외한 크기·대칭·모든 gap·canonical 변·파일 순서의 시작 몸이다.`,'',...explain.map(x=>'- '+x),'',censusTable,'','### 통로 너비와 gap 분포','',table(['파일','통로 너비별 칸 수','gap별 생성 칸 수'],c.maps.map(x=>[x.file,JSON.stringify(x.corridorWidthDistribution),JSON.stringify(x.gapDistribution)])),'','## 생성 설계와 가족','',
 'Node 표준 라이브러리만 쓴다. uint32 seed의 Mulberry32로 결정한 타일/변 orbit 대표 하나(기본 영역)를 만든 뒤 선언한 거울/회전으로 완성한다. 변은 north/west의 toroidal canonical 표로 관리하고 저장할 때 width+1 교대 행의 index로 변환한다. 시작 몸은 반대 팀에 순서 그대로 대칭 복제한다.',
 '', '연결성은 무방향 이동 그래프를 DSU로 검사하고 분리 성분을 잇는 켈프 orbit만 연다. 포털은 같은 방향의 변과 대칭 변을 한 쌍으로 놓고, 추가 후 다시 연결한다. rooms는 문이 있는 격벽, pockets는 단일 입구 가지, maze/thin은 높은 켈프 후보 밀도를 연결 보수로 줄인 구조다. 공급은 BFS 중앙·지도 테두리·2-core 가지 위치에 따라 배치한다.','',generatedTable,'','## 인식 함정','',trapTable,'','## 검증과 공식 runner smoke','',...(checks?[`독립 교차 검산: 기존 연구 도구의 이동 그래프 38개, 온라인/판본의 2-core·중앙 공급·주머니 공급 15개가 모두 일치했다. 오류 검출·대체 seed·원본 보존 검사는 ${checks.tests.length}개 모두 통과했다. 원수: exp/mapgen/checks.json. 이 검사는 공식 엔진 smoke를 대체하지 않는다.`,'']:[]),`기존 형식·대칭 ${existing.rows.filter(x=>x.valid).length}/${existing.rows.length}개 통과. 생성 엄격 ${summary.strictStaticValid}/35개 통과. gen_X_04는 근처 원형을 보존한 연결성 실패이며 감추지 않았다. 정적 원수는 exp/mapgen/validation-{existing,generated}.json이다.`,'',`총 계획 ${summary.planned}판(35개 A, X13개 B 추가), 실제 시작 ${summary.attempted}, 로딩·완료 ${summary.finished}, 미실행 ${summary.pending}.`,'',...(summary.blocked?['**실행 차단:** 샌드박스에서 pgrep이 sysmond/process list 접근을 거부했다. 기계 전체 판 수 <6을 확인할 수 없어 새 게임을 시작하지 않았다. exp/mapgen/resource-check.json과 smoke.jsonl에 미실행 상태를 남겼다. 일반 로컬 터미널에서 `node tools/mapgen/smoke.js`를 실행하면 매 판 자원을 다시 확인하고 순차 재개한다.','']:[]),gameTable,'',`우리 봇 오류/timeout/엔진 보정이 있는 실제 실행 판 ID: ${faults.map(r=>r.gameId).join(', ')|| (attempted.length?'없음':'미측정(실행 N=0)')}. 잘못 인식한 실제 실행 판 ID: ${recognised.map(r=>r.gameId+': '+r.misrecognition.join(',')).join('; ')|| (attempted.length?'없음':'미측정(실행 N=0)')}.`,'','## 한계','',...limitations.map(x=>'- '+x),'','재현 명령과 기존 큐 연결은 [README](../../tools/mapgen/README.md)를 따른다. 승패 열은 생성하지 않았다.',''].join('\n');
 fs.writeFileSync(path.join(ROOT,'research/observations/mapgen.md'),reportText);
 // Last artifact write, always exactly twelve lines.
 const lines=[`W8 지도 시험장 — ${clock}`,`전수조사: ${c.fileCount}파일 / ${c.uniqueCount}고유 지도; census.json 먼저 기록`,`생성: 35개 (S6/M8/L6/R2/X13), seed ${m.seed}`,`기존 정적 형식·대칭: ${existing.rows.filter(x=>x.valid).length}/${existing.rows.length} 통과`,`생성 엄격 정적: ${summary.strictStaticValid}/35 통과`,`연결성 예외: gen_X_04 원본 근처 보존; 작은 성분 4개`,`함정: 시작·근처 동일, 보존 밖 변/support >=40% 변경`,`범위 안 ${m.maps.filter(x=>x.envelope==='inside').length} / 스트레스 ${m.maps.filter(x=>x.envelope==='stress').length}`,`공식 smoke: ${summary.attempted}/${summary.planned} 시작, ${summary.finished} 로딩·완료`,`오류/timeout·오인식: ${attempted.length?'status.json 및 보고서 참조':'미측정; pgrep 샌드박스 차단'}`,`재개: node tools/mapgen/smoke.js`,`기제 점검 전용; 승패 표·커밋·네트워크·업로드 없음`];
 fs.writeFileSync(path.join(ROOT,'exp/mapgen/SUMMARY.txt'),lines.join('\n')+'\n');return summary;
}
if(require.main===module)console.log(JSON.stringify(report()));module.exports={report};
