#!/usr/bin/env node
'use strict';
// Offline replay -> canonical map. No network, workers, or games.
// node tools/replay2map.js replay[.gz] output.map [more-replays...]
// node tools/replay2map.js --audit
// Gaps hidden by the server are ESTIMATES, never evidence of exact recovery.
const fs = require('fs'), path = require('path'), zlib = require('zlib'), vm = require('vm');
const L = require('./mapgen/lib'), P = require('./pearl_layout'), V = require('./mapgen/validate');
const ROOT = L.ROOT, OUT = path.join(ROOT, 'exp/sprint-maps');
const eq = (a,b) => JSON.stringify(a) === JSON.stringify(b);
let decoder;
function loadReplay(file, {events=true}={}) {
  if (!decoder) {
    const src = require('./top_features').viewerSource(), cut = src.indexOf('var Af=B(');
    if (cut < 0) throw Error('unsupported official viewer build');
    const ctx = {TextEncoder,TextDecoder};
    vm.runInNewContext(src.slice(0,cut).replace('if(n.formatVersion>1)','if(n.formatVersion>2)') +
      'globalThis.decoder={Df,bf,Of,of};})();',ctx,{timeout:5000});
    decoder = ctx.decoder;
  }
  const raw = fs.readFileSync(file), root = decoder.Df(file.endsWith('.gz')?zlib.gunzipSync(raw):raw);
  // These are exactly the events needed by the existing occupancy/censoring extractor.
  const wanted = new Set(['ROUND_START','TURN_START','PEARL_COUNTDOWN','TILE_CHANGE','DRAGON_UPDATE','DRAGON_SPLIT','DRAGON_DEATH'].map(k=>decoder.of[k]));
  const es=[];
  if (events) for(let i=0;i<root.events.length;i++) {
    const e=root.events.get(i); if(wanted.has(e.which()))es.push(decoder.bf(e));
  }
  return decoder.Of(root,es);
}
function fromMap(M, mapText) {
  const W=M.width,H=M.height,N=W*H,m=L.blank(W,H,M.symmetry||'',M.mapName||'Replay');
  if(M.initialHEdges.length!==(H+1)*W||M.initialVEdges.length!==H*(W+1))throw Error('edge array dimensions');
  for(let k=0;k<N;k++) {
    const p=M.pearlRespawn[k]; m.tiles[k]=[p.minRounds,p.maxRounds];
    const x=k%W,y=Math.floor(k/W);
    // Opposite boundary aliases represent the same toroidal edge.
    if(M.initialHEdges[k]===1 || y===0&&M.initialHEdges[H*W+x]===1)m.edges[k]=[1,-1];
    if(M.initialVEdges[y*(W+1)+x]===1 || x===0&&M.initialVEdges[y*(W+1)+W]===1)m.edges[N+k]=[1,-1];
  }
  const original=mapText?L.parse(mapText):null;
  for(const [i,pair]of (M.portals||[]).entries()) {
    const es=pair.map(p=>p.side==='N'?p.y*W+p.x:p.side==='S'?L.mod(p.y+1,H)*W+p.x:
      p.side==='W'?N+p.y*W+p.x:p.side==='E'?N+p.y*W+L.mod(p.x+1,W):NaN);
    if(es.length!==2||es.some(e=>!Number.isInteger(e)))throw Error('invalid portal pair');
    // Viewer sorts pairs by original id but labels them 0..n-1. Use embedded text
    // to retain ids including holes; pair-list-only input has recoverable pairing only.
    const id=original?original.edges[es[0]][1]:i;
    if(original&&es.some(e=>original.edges[e][0]!==2||original.edges[e][1]!==id))throw Error('portal text/list mismatch');
    for(const e of es)m.edges[e]=[2,id];
  }
  const ds=[...M.initialDragons].sort((a,b)=>a.id-b.id);
  ds.forEach((d,i)=>{if(d.id!==i)throw Error('nonconsecutive initial dragon ids');
    if(!['A','B'].includes(d.team))throw Error('invalid team');
    m.dragons.push({team:d.team==='A'?0:1,body:d.body.map(b=>b.y*W+b.x)});
  });
  if(original&&(!eq(m.edges,original.edges)||!eq(m.dragons,original.dragons)||!eq(m.tiles,original.tiles)))throw Error('decoded map differs from embedded text');
  return m;
}
function fromReplay(file,options) {const replay=loadReplay(file,options);return {m:fromMap(replay.match.map,replay.map),replay};}
function structure(m,flip=false) {return [m.W,m.H,m.symmetry,m.edges,m.dragons.map(d=>({...d,team:flip?1-d.team:d.team}))];}
function estimate(m,rows) {
  const N=m.W*m.H,mir=k=>L.mirrorTile(m,k),groups=Array.from({length:N},(_,k)=>k).filter(k=>k<=mir(k));
  const c={mir,relevant:groups},games=rows.map(r=>P.gameFromRow(c,r)),fits=[],tiles=m.tiles.map(g=>g.slice());
  const truth=rows.filter(r=>r.truth);
  if(truth.length) {
    const t=Array.from({length:N},()=>[0,0]);for(let i=0;i<truth[0].truth.length;i+=3){const[k,a,b]=truth[0].truth.slice(i,i+3);t[k]=[a,b];}
    for(const r of truth.slice(1)){const u=Array.from({length:N},()=>[0,0]);for(let i=0;i<r.truth.length;i+=3){const[k,a,b]=r.truth.slice(i,i+3);u[k]=[a,b];}if(!eq(t,u))throw Error('conflicting unredacted gaps');}
    return {tiles:t,status:'exact-unredacted',groups:[],games:rows.length};
  }
  for(const k of groups) {
    const segs=games.flatMap(g=>P.segmentsOf(g.ep.get(k),g.blk.get(k),g.rounds));
    const f=P.fitGroup(segs),gap=f.never?[0,0]:[f.m,Number.isFinite(f.M)?f.M:10000000];
    tiles[k]=gap;tiles[mir(k)]=gap.slice();
    const {h,...summary}=f;
    fits.push({tile:k,mirror:mir(k),gap,...summary,status:f.never?'unobserved-not-proven-disabled':'estimated'});
  }
  return {tiles,status:'estimated-redacted',games:rows.length,groups:fits,
    method:'tools/pearl_layout.js: natural pre-turn tileChange spawns; mirrored occupancy; death drops excluded; blocked rounds and game ends censored; fitGroup two-step censored uniform. Unobserved groups written 0..0 only as a conservative test-bed assumption, not proof of no spawning.'};
}
function compare(a,b) {
  const diff=(x,y)=>Array.from({length:Math.max(x.length,y.length)},(_,k)=>k).filter(k=>!eq(x[k],y[k]));
  const tile=diff(a.tiles,b.tiles),edge=diff(a.edges,b.edges),dragon=diff(a.dragons,b.dragons);
  const flipped=a.dragons.map(d=>({...d,team:1-d.team})),swap=eq(flipped,b.dragons);
  const field=(indices,x,y)=>({equal:indices.length===0,mismatches:indices.length,differences:indices.map(index=>({index,reconstructed:x[index],reference:y[index]}))});
  return {dimensions:{equal:a.W===b.W&&a.H===b.H,reconstructed:[a.W,a.H],reference:[b.W,b.H]},
    name:{equal:a.name===b.name,reconstructed:a.name,reference:b.name},symmetry:{equal:a.symmetry===b.symmetry,reconstructed:a.symmetry,reference:b.symmetry},
    tiles:field(tile,a.tiles,b.tiles),edges:field(edge,a.edges,b.edges),
    edgeKinds:field(diff(a.edges.map(e=>e[0]),b.edges.map(e=>e[0])),a.edges.map(e=>e[0]),b.edges.map(e=>e[0])),
    portals:field(diff(a.edges.map(e=>e[0]===2?e[1]:null),b.edges.map(e=>e[0]===2?e[1]:null)),a.edges.map(e=>e[0]===2?e[1]:null),b.edges.map(e=>e[0]===2?e[1]:null)),
    dragons:field(dragon,a.dragons,b.dragons),dragonOrderAndBodies:{equal:eq(a.dragons.map(d=>d.body),b.dragons.map(d=>d.body))},
    teams:{equal:dragon.length===0,globalTeamSwap:swap},geometryExact:a.W===b.W&&a.H===b.H&&a.symmetry===b.symmetry&&edge.length===0&&(dragon.length===0||swap)};
}
function deadChains(m) {
  const nb=L.graph(m),core=L.coreOf(nb),seen=new Set(),chains=[];
  // Maximal leaf -> degree-2 stem -> junction paths outside the 2-core.
  // Length counts off-core tiles and excludes the junction. An isolated path is
  // counted once; isolated tiles are reported separately by lib.metrics.
  for(let k=0;k<nb.length;k++)if(!core[k]&&nb[k].length===1&&!seen.has(k)) {
    let prev=-1,u=k;const tiles=[];
    while(!core[u]&&nb[u].length<=2&&!seen.has(u)) {
      seen.add(u);tiles.push(u);const next=nb[u].find(v=>v!==prev);
      if(next===undefined)break;prev=u;u=next;
    }
    chains.push({terminus:k,tiles,length:tiles.length,attachment:tiles.includes(u)?null:u});
  }
  return {deadEndChainCount:chains.length,deadEndChainLengthDistribution:L.hist(chains.map(c=>c.length)),
    deadEndChainMaxLength:Math.max(0,...chains.map(c=>c.length)),deadEndChainTiles:chains.reduce((s,c)=>s+c.length,0),deadEndChains:chains};
}
function censusRow(file,group,gapStatus='exact-file') {
  const m=L.read(file),met=L.metrics(m);return {file,name:m.name,group,gapStatus,sha256:L.hash(m),...met,
    offCoreShare:met.pocketTiles/met.area,width1Share:(met.corridorWidthDistribution[1]||0)/met.area,
    fountainAreaShare:met.fountainTiles/met.area,dragons:m.dragons,...deadChains(m)};
}
const write=(file,value)=>fs.writeFileSync(path.join(ROOT,file),JSON.stringify(value,null,2)+'\n');
function audit() {
  fs.mkdirSync(OUT,{recursive:true});fs.mkdirSync(path.join(ROOT,'maps/sprint'),{recursive:true});
  const at=new Date().toISOString(),variants=JSON.parse(fs.readFileSync(path.join(ROOT,'data/pearl_layout/variants.json')));
  const index=fs.readFileSync(path.join(ROOT,'data/top/index.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
  const refs=L.mapFiles(['maps/online-20260927','maps/server-b']).filter((f,i,a)=>a.findIndex(g=>fs.realpathSync(path.join(ROOT,g))===fs.realpathSync(path.join(ROOT,f)))===i);
  const known=[];
  for(const file of refs) {
    const ref=L.read(file),tag=file.includes('_10.map')?'10':file.includes('_b.map')?'b':'a',cat=variants.cats[ref.name+'/'+ref.dragons.length];
    const candidates=index.filter(r=>r.map===ref.name&&cat?.assign['g'+r.gameId]===tag&&fs.existsSync(path.join(ROOT,`data/top/${r.battleId}/${r.gameId}.replay.gz`)));
    const selected=candidates.filter((r,i,a)=>a.findIndex(s=>s.gameId===r.gameId)===i).slice(0,4),rows=[],entries=[];
    if(selected.length<2)throw Error('not enough replays for '+file);
    for(const r of selected) {
      const replayFile=`data/top/${r.battleId}/${r.gameId}.replay.gz`,{m,replay}=fromReplay(path.join(ROOT,replayFile));
      const fields=compare(m,ref);if(!fields.geometryExact)throw Error('known geometry mismatch '+replayFile+' vs '+file);
      rows.push(P.extract(replay));entries.push({battleId:r.battleId,gameId:r.gameId,replayFile,reference:file,layout:tag,
        layoutAssignmentSource:'data/pearl_layout/variants.json (prior spawn-likelihood classification; gaps are not imported)',
        gapFieldsRedacted:m.tiles.every(g=>g[1]===0),countdownEvents:replay.events.filter(e=>e.type==='pearlCountdown').length,fields});
    }
    const fit=estimate(ref,rows),est={...ref,tiles:fit.tiles};
    const estimatedTiles=compare(est,ref).tiles;
    for(const e of entries)e.estimatedFields={...e.fields,tiles:estimatedTiles,gapStatus:fit.status};
    known.push({file,name:ref.name,layout:tag,replays:entries,gapFit:fit});
    console.log('known',ref.name,tag,selected.length,'geometry exact; gaps',fit.status);
  }
  const sprintDir=path.join(ROOT,'data/online/sprint-bracket'),sets=new Map();
  for(const file of fs.readdirSync(sprintDir).filter(f=>/^game-\d+\.json$/.test(f)).sort()) {
    const meta=JSON.parse(fs.readFileSync(path.join(sprintDir,file))),replayFile=`data/online/sprint-bracket/M${meta.id}.replay`;
    if(!fs.existsSync(path.join(ROOT,replayFile)))throw Error('missing sprint replay '+meta.id);
    const {m,replay}=fromReplay(path.join(ROOT,replayFile)),row=P.extract(replay);
    if(m.name!==meta.mapName)throw Error('metadata map mismatch');
    if(!sets.has(m.name))sets.set(m.name,{m,rows:[],games:[]});
    const s=sets.get(m.name),same=eq(structure(m),structure(s.m)),swap=eq(structure(m,true),structure(s.m));
    if(!same&&!swap)throw Error('sprint structural disagreement '+meta.id);
    s.rows.push(row);s.games.push({gameId:meta.id,battleId:meta.battleId??null,seriesId:meta.seriesId,mapId:meta.mapId,replayFile,
      globalTeamSwap:!same&&swap,rawMapSha256:L.crypto.createHash('sha256').update(replay.map).digest('hex'),
      redactedGaps:m.tiles.every(g=>g[1]===0),countdownEvents:replay.events.filter(e=>e.type==='pearlCountdown').length,extractionChecks:row.chk});
    if(s.games.length%8===0)console.log('sprint',m.name,s.games.length);
  }
  if(sets.size!==7)throw Error('expected seven sprint maps');
  const sprint=[];
  for(const [name,s]of sets) {
    const fit=estimate(s.m,s.rows),slug=name.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,''),file=`maps/sprint/${slug}.map`;
    // Stable canonical team orientation: the first dragon belongs to A. File order
    // and every body remain untouched. Server global swaps are listed per game.
    const flip=s.m.dragons[0].team===1,m={...s.m,tiles:fit.tiles,dragons:s.m.dragons.map(d=>({...d,team:flip?1-d.team:d.team}))};
    // No '#' lines: unswbc 1.2.3 rejects them ("unknown map line"). Provenance lives in maps/sprint/README.md.
    const text=L.serialize(m)+'END\n';
    fs.writeFileSync(path.join(ROOT,file),text);
    const row=censusRow(file,'sprint',fit.status);
    sprint.push({file,name,mapId:s.games[0].mapId,games:s.games.map(g=>({...g,canonicalTeamSwap:g.globalTeamSwap!==flip})),canonicalTeamSwapFromFirst:flip,
      allGamesSameStructureUpToGlobalTeamSwap:true,gapsExactlyRecoverable:fit.status==='exact-unredacted',gapFit:fit,
      staticValidation:V.validate(L.read(file),{connected:false}),strictConnectivityValidation:V.validate(L.read(file),{connected:true}),census:row});
    console.log('write',file,'games',s.games.length,'core',row.core2Tiles,'offcore',row.offCoreShare);
  }
  const unique=new Set(),existing=[];
  for(const f of L.mapFiles(L.EXISTING)){const m=L.read(f),h=L.hash(m);if(!unique.has(h)){unique.add(h);existing.push(censusRow(f,'existing'));}}
  const generated=L.mapFiles(['maps/generated']).map(f=>censusRow(f,'generated-'+path.basename(f).split('_')[1]));
  const familyNames=['S','M','L','R','X'],keys=['area','kelpDensity','offCoreShare','width1Share','deadEndChainCount','deadEndChainMaxLength','portalPairCount','spawnShare','fountainShare'];
  const families=familyNames.map(name=>{const rows=generated.filter(r=>r.group==='generated-'+name);return {name,maps:rows.length,ranges:Object.fromEntries(keys.map(k=>[k,{min:Math.min(...rows.map(r=>r[k])),max:Math.max(...rows.map(r=>r[k]))}]))};});
  const validation={at,conventions:{horizontal:'(H+1)*W; north edge y*W+x; y=H aliases y=0',vertical:'H*(W+1); west edge y*(W+1)+x; x=W aliases x=0',
    dragonOrder:'initial id ascending = map file order; server may globally swap A/B without changing ids or bodies',
    portalIds:'original EDGE portalId from embedded replay map text; match.map pair order alone loses nonconsecutive ids',
    gaps:'pearlRespawn is the spawn interval, but current server replaces every interval with 0..0; all countdown events absent. Observed spawns alone cannot uniquely identify uniform support from finite censored samples. This converter uses statistical fitting and does not attempt seeded engine RNG inversion.'},
    known,sprint,counts:{knownNames:new Set(known.map(r=>r.name)).size,knownLayouts:known.length,knownReplays:known.reduce((n,r)=>n+r.replays.length,0),sprintGames:sprint.reduce((n,r)=>n+r.games.length,0)}};
  write('exp/sprint-maps/validation.json',validation);
  const census={at,definitions:{...JSON.parse(fs.readFileSync(path.join(ROOT,'exp/mapgen/census.json'))).definitions,
    deadEndChain:'maximal off-core leaf and degree-2 stem until first degree>=3 junction/core; length counts tiles excluding junction; detached linear component counted once',
    offCoreShare:'pocketTiles / area; includes isolated cells; not all off-core cells are chains',
    gapUncertainty:'Sprint supply/spawn/fountain fields use estimated intervals; unobserved groups assumed disabled. Do not treat these as exact source-map fields.'},
    counts:{sprint:sprint.length,existingUnique:existing.length,generated:generated.length},sprint:sprint.map(s=>s.census),existing,generated,families};
  write('exp/sprint-maps/census.json',census);
  writeReadme(validation,census);
  // SUMMARY.txt is deliberately produced by --finalize after independent checks.
  return validation;
}
function writeReadme(v,c) {
  const pct=x=>(100*x).toFixed(1)+'%',row=r=>`| ${r.name}${/_b\.map$/.test(r.file)?' (b)':/_10\.map$/.test(r.file)?' (10)':''} | ${r.width}×${r.height}/${r.symmetry} | ${pct(r.kelpDensity)} | ${r.core2Tiles} | ${pct(r.offCoreShare)} | ${r.deadEndChainCount}/${r.deadEndChainMaxLength} | ${pct(r.width1Share)} | ${r.portalPairCount} | ${pct(r.spawnShare)} | ${pct(r.fountainShare)} | ${r.startDragons.join('/')} |`;
  let text=`# 스프린트 본선 지도 복원 (W5 / W8)\n\n작성: ${new Date().toLocaleString('sv-SE',{timeZone:'Asia/Seoul'})} KST. 오프라인 분석, 커밋·업로드·경기 실행 없음.\n\n`;
  text+='**구조는 복원했지만 진주 생성 간격은 추정이다.** 서버가 기보 안 지도 TILE을 모두 0..0으로 바꿨고 pearlCountdown도 남기지 않았다. 이 때문에 원본과 완전히 같은 지도라고 부를 수 없다. 생성 관련 점검에는 이 불확실성을 고려해야 한다.\n\n';
  text+=`알려진 지도 ${v.counts.knownNames}종/${v.counts.knownLayouts}배치, ${v.counts.knownReplays}기보에서 크기·대칭·켈프·포털 id/짝·드래곤 몸/순서가 공식 파일과 일치했다. 팀은 기보마다 전체 A/B 교환을 허용하며 직접 비교와 교환 여부를 validation.json에 따로 적었다. b 파일은 기존 연구에서 통계로 추정한 판본으로, 공식 원본이라는 독립 보증은 없다. 비교할 배치는 기존 variants.json 분류를 썼으며 그 간격을 복사하지 않았다.\n\n`;
  text+=`본선 ${v.counts.sprintGames}기보 모두에서 지도별 구조가 전체 팀 교환을 제외하고 같았다. 파일은 첫 드래곤을 A로 정규화하고 원래 순서를 보존한다. MAP_NAME은 원래 이름이다. 초기 진주·무작위 시드·봇은 지도 정의가 아니므로 복제하지 않는다.\n\n`;
  text+='간격 추정은 기존 tools/pearl_layout.js의 검증된 점유 재구성과 censored-uniform fitGroup을 사용한다. 턴 전 자연 생성만 표본으로 삼고 사망 낙하는 제외한다. 대칭 칸을 묶고 전부 점유된 구간과 경기 종료를 검열한다. minGap은 깨끗한 표본 최소, maxGap은 우도 추정이다. 관측 안 된 묶음의 0..0은 시험용 가정이며 비생성의 증명이 아니다. 묶음별 표본 수·구간·비생성 한계는 validation.json에 남겼다.\n\n';
  text+='2-core/통로 폭/샘/공급은 lib.metrics 정의를 따른다. off-core는 고립 칸도 포함한다. 사슬은 off-core 끝칸부터 degree=2 줄기를 따라 분기점 직전까지의 칸 수다. 독립 선형 성분은 한 번 센다. 통로 폭 1 비율은 수평·수직 열린 직선 길이 중 작은 값이 1인 칸의 비율이며 degree=2와 다르다. 샘 비율 분모는 생성칸이다. 생성·샘 비율과 공급은 **추정값**이다.\n\n';
  text+='| 지도 | 크기/대칭 | 켈프 | 2-core | off-core | 끝사슬 수/최장 칸 | 폭1 | 포털쌍 | 생성* | 샘* | 시작 A/B |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n';
  text+=c.sprint.map(row).join('\n')+'\n\n## 기존 20지도와 나란히 비교\n\n'+
    '| 지도 | 크기/대칭 | 켈프 | 2-core | off-core | 끝사슬 수/최장 칸 | 폭1 | 포털쌍 | 생성* | 샘* | 시작 A/B |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'+c.existing.map(row).join('\n')+'\n\n';
  text+='## 생성 가족과 비교\n\n35개 개별 행과 폭·사슬 길이 분포는 [census.json](../../exp/sprint-maps/census.json)에 있다. 가족의 목적은 [MANIFEST.md](../generated/MANIFEST.md)를 따른다.\n\n';
  text+='가족 표의 비율은 0–1 단위의 최솟값–최댓값이다.\n\n';
  text+='| 가족 | 수 | 면적 | 켈프 | off-core | 폭1 | 끝사슬 수 | 최장 사슬 | 포털쌍 | 생성 | 샘 |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n';
  for(const f of c.families){const range=k=>`${f.ranges[k].min.toFixed(k.endsWith('Share')||k==='kelpDensity'?3:0)}–${f.ranges[k].max.toFixed(k.endsWith('Share')||k==='kelpDensity'?3:0)}`;text+=`| ${f.name} | ${f.maps} | ${['area','kelpDensity','offCoreShare','width1Share','deadEndChainCount','deadEndChainMaxLength','portalPairCount','spawnShare','fountainShare'].map(range).join(' | ')} |\n`;}
  text+='\n## 출처와 지도별 세부 통계\n\n본선 메타데이터에는 숫자 battleId가 없고 seriesId가 대전 묶음 식별자다. 이를 숫자 id로 꾸며 쓰지 않았다. 각 game의 입력 경로와 실제 필드는 validation.json에 전부 보존했다.\n\n';
  for(const s of v.sprint){const r=s.census;text+=`### ${s.name}\n\n- 파일: [${path.basename(s.file)}](./${path.basename(s.file)}), map id ${s.mapId}.\n- series/battle 묶음: ${[...new Set(s.games.map(g=>g.seriesId))].join(', ')}. 숫자 battleId: ${s.games.some(g=>g.battleId!==null)?[...new Set(s.games.map(g=>g.battleId))].join(', '):'메타데이터에 없음'}.\n- game ids (${s.games.length}): ${s.games.map(g=>g.gameId).join(', ')}.\n- census 행: ${row(r)}\n- 폭별 칸 수: \`${JSON.stringify(r.corridorWidthDistribution)}\`. 끝사슬 길이별 수: \`${JSON.stringify(r.deadEndChainLengthDistribution)}\`.\n- 시작 길이 A/B: ${r.startLengths.map(a=>a.join(',')).join(' / ')}.\n- 형식·대칭 검증: ${s.staticValidation.valid?'통과':s.staticValidation.errors.join('; ')}. 엄격 연결성: ${s.strictConnectivityValidation.valid?'통과':s.strictConnectivityValidation.errors.join('; ')}. 성분 크기: ${r.componentSizes.join(', ')}.\n- 생성 추정: 관측 안 된 묶음 ${s.gapFit.groups.filter(g=>g.never).length}/${s.gapFit.groups.length}.\n\n`;}
  text+='재현: `nice -n 10 node tools/replay2map.js --audit`. 단일 복원: `node tools/replay2map.js <기보> <출력.map> [같은 지도의 추가 기보...]`. 기보 지도 문자열을 통한 변 id 보존과 match.map 배열 변환을 서로 대조한다. 통계 및 검증 원수는 [validation.json](../../exp/sprint-maps/validation.json), [census.json](../../exp/sprint-maps/census.json)에 있다.\n';
  fs.writeFileSync(path.join(ROOT,'maps/sprint/README.md'),text);
}
function finalize() {
  const v=JSON.parse(fs.readFileSync(path.join(OUT,'validation.json'))),c=JSON.parse(fs.readFileSync(path.join(OUT,'census.json')));
  const lines=[`완료 시각: ${new Date().toLocaleString('sv-SE',{timeZone:'Asia/Seoul'})} KST`,
    `알려진 지도: ${v.counts.knownNames}종, ${v.counts.knownLayouts}배치, 가림 ${v.counts.knownReplays} + 비가림 ${v.counts.unredactedKnownReplays||0}기보`,
    '구조 검증: 크기·대칭·변 종류·포털 id/짝·시작 몸과 순서 일치 (전체 A/B 교환 기록)',
    '생성 간격: 서버 TILE 0..0 가림, countdown 없음; 직접 정보 없음, 검열 균등분포 추정',
    `본선 검증: ${v.counts.sprintGames}기보, ${v.sprint.length}지도; 전체 팀 교환 외 구조 동일`,
    `정적 형식/대칭 검증: ${v.sprint.filter(s=>s.staticValidation.valid).length}/7; 엄격 연결성 ${v.sprint.filter(s=>s.strictConnectivityValidation.valid).length}/7`,
    `통계 비교: 본선 7 + 기존 고유 ${c.counts.existingUnique} + 생성 ${c.counts.generated} (S/M/L/R/X)`,
    '사슬: off-core leaf→degree2 줄기→분기점; 칸 수 길이, 고립 선형 성분 1회',
    '산출: tools/replay2map.js, maps/sprint/*.map, maps/sprint/README.md',
    '원수: exp/sprint-maps/validation.json, census.json (비교 필드·추정 불확실성 포함)',
    '제약: 추정 생성·샘·공급, 미관측=비생성 가정; 원본 완전 동일 주장 불가',
    '네트워크·업로드·경기 실행·커밋 없음; 코디네이터 smoke 대기'];
  fs.writeFileSync(path.join(OUT,'SUMMARY.txt'),lines.join('\n')+'\n');
}
if(require.main===module) {
  try {
    const args=process.argv.slice(2);
    if(args[0]==='--audit')audit();
    else if(args[0]==='--finalize')finalize();
    else {
      const [file,out,...rest]=args;if(!file||!out)throw Error('usage: replay2map.js input.replay output.map [more.replays...] | --audit | --finalize');
      const {m,replay}=fromReplay(file),rows=[P.extract(replay)];
      for(const f of rest){const q=fromReplay(f);if(!eq(structure(m),structure(q.m))&&!eq(structure(m),structure(q.m,true)))throw Error('different map '+f);rows.push(P.extract(q.replay));}
      const fit=estimate(m,rows);m.tiles=fit.tiles;fs.writeFileSync(out,'# Gap status: '+fit.status+'; see tools/replay2map.js\n'+L.serialize(m)+'END\n');
      console.error(JSON.stringify({output:out,name:m.name,gaps:fit.status,games:rows.length,unobserved:fit.groups.filter(g=>g.never).length}));
    }
  }catch(e){console.error(e.stack);process.exitCode=1;}
}
module.exports={loadReplay,fromMap,fromReplay,estimate,compare,deadChains,censusRow,audit,writeReadme,finalize};
