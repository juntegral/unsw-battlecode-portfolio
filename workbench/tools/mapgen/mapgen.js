#!/usr/bin/env node
'use strict';
const L=require('./lib'),V=require('./validate'),{fs,path,ROOT,blank,read,mirrorTile,mirrorEdge,endpoints,edgeBetween,graph,components,bfs,coreOf,metrics,serialize,hash,mod}=L;
const RNG=seed=>{let s=seed>>>0;return()=>{s+=0x6D2B79F5;let t=Math.imul(s^s>>>15,1|s);t^=t+Math.imul(t^t>>>7,61|t);return((t^t>>>14)>>>0)/4294967296;};};
function shuffle(a,r){for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
const tileReps=m=>m.tiles.map((_,k)=>k).filter(k=>k<=mirrorTile(m,k));
const edgeReps=m=>m.edges.map((_,k)=>k).filter(k=>k<=mirrorEdge(m,k));
function setEdge(m,e,value){m.edges[e]=value.slice();m.edges[mirrorEdge(m,e)]=value.slice();}
function setTile(m,k,value){m.tiles[k]=value.slice();m.tiles[mirrorTile(m,k)]=value.slice();}
function starts(m,count,length,crowded=false) {
 const used=new Set(),cx=m.symmetry==='x'?Math.floor(m.W/2):Math.floor(m.W/4),cy=m.symmetry==='x'?Math.floor(m.H/4):Math.floor(m.H/2);
 const candidates=[];for(let y=0;y<m.H;y++)for(let x=length;x<m.W-length;x++)candidates.push([x,y]);
 candidates.sort((a,b)=>{const score=p=>Math.abs(p[0]-cx)+Math.abs(p[1]-cy)*(crowded?1:0.3);return score(a)-score(b)||a[1]-b[1]||a[0]-b[0];});
 for(const[x,y]of candidates){const body=Array.from({length},(_,i)=>y*m.W+x-i),other=body.map(k=>mirrorTile(m,k)),all=[...body,...other];if(new Set(all).size!==all.length||all.some(k=>used.has(k)))continue;if(!crowded&&m.dragons.some(d=>Math.abs(Math.floor(d.body[0]/m.W)-y)<3))continue;all.forEach(k=>used.add(k));m.dragons.push({team:0,body},{team:1,body:other});if(m.dragons.length===2*count)break;}
 if(m.dragons.length!==2*count)throw Error('could not place starts');
}
function connect(m,locked,r) {
 const N=m.W*m.H,p=Array.from({length:N},(_,i)=>i),find=a=>{while(p[a]!==a){p[a]=p[p[a]];a=p[a];}return a;},join=(a,b)=>{a=find(a);b=find(b);if(a!==b)p[a]=b;};
 graph(m).forEach((a,k)=>a.forEach(v=>join(k,v)));let repairs=0;
 for(const e of shuffle(edgeReps(m),r)) {if(locked.has(e)||locked.has(mirrorEdge(m,e))||m.edges[e][0]!==1)continue;const[a,b]=endpoints(m,e);if(find(a)===find(b))continue;setEdge(m,e,[0,-1]);for(const z of new Set([e,mirrorEdge(m,e)])){const[u,v]=endpoints(m,z);join(u,v);}repairs++;}
 return repairs;
}
function portals(m,count,locked,r) {
 const available=shuffle(edgeReps(m).filter(e=>e!==mirrorEdge(m,e)&&!locked.has(e)&&!locked.has(mirrorEdge(m,e))&&m.edges[e][0]===0),r);
 let id=0;for(const e of available){if(id>=count)break;if(m.edges[e][0]!==0)continue;setEdge(m,e,[2,id++]);}
 if(id!==count)throw Error('not enough portal edges');
}
function pockets(m){for(let y=4;y<m.H-4;y+=7){const x=4,len=5;for(let j=0;j<len;j++){const k=y*m.W+x+j;setEdge(m,k,[1,-1]);setEdge(m,mod(y+1,m.H)*m.W+x+j,[1,-1]);}setEdge(m,m.W*m.H+y*m.W+x+len,[1,-1]);}}
function protectedRegion(base,radius=6) {
 const mask=base.tiles.map((_,k)=>base.dragons.some(d=>{const a=d.body[0],dx=Math.abs(k%base.W-a%base.W),dy=Math.abs(Math.floor(k/base.W)-Math.floor(a/base.W));return Math.min(dx,base.W-dx)+Math.min(dy,base.H-dy)<=radius;}));
 const edges=new Set();base.edges.forEach(([t],e)=>{if(t===2||endpoints(base,e).every(k=>mask[k]))edges.add(e);});
 // Preserve all segments and the edge supporting each segment, even outside the radius.
 for(const d of base.dragons)for(let i=1;i<d.body.length;i++){const e=edgeBetween(base,d.body[i-1],d.body[i]);edges.add(e);edges.add(mirrorEdge(base,e));}
 return {mask,edges,radius};
}
const plans=[
 ['S',12,12,'xy','open',1,3],['S',14,14,'y','light',2,4],['S',16,18,'x','maze',1,4],['S',18,18,'xy','centre',2,4],['S',20,16,'y','edge',2,4],['S',10,10,'xy','crowded',3,2],
 ['M',28,28,'xy','rooms',3,4],['M',30,26,'y','pockets',2,4],['M',32,30,'x','portals2',3,4],['M',36,28,'xy','portals4',3,4],['M',34,34,'y','centre',3,4],['M',40,24,'x','edge',3,4],['M',38,26,'xy','thin',2,4],['M',24,40,'y','pockets',3,4],
 ['L',48,48,'xy','sparse',3,6],['L',50,54,'y','maze',3,4],['L',64,64,'xy','far',2,6],['L',56,48,'x','many',8,4],['L',60,50,'xy','portals4',4,4],['L',62,58,'y','rooms',4,6],
 ['R',64,12,'xy','thin',2,4],['R',14,56,'x','edge',2,4]
].map(([family,W,H,symmetry,style,count,length])=>({family,W,H,symmetry,style,count,length}));
function make(plan,seed) {
 const r=RNG(seed),base=plan.source?read(plan.source):null,m=blank(plan.W,plan.H,plan.symmetry,plan.name),N=m.W*m.H;
 let region=null,locked=new Set();if(base&&!plan.differentStarts){m.dragons=structuredClone(base.dragons);region=protectedRegion(base);locked=region.edges;}else starts(m,plan.count,plan.length,plan.style==='crowded');
 for(const e of edgeReps(m)) {
  let probability=0;
  if(['light','centre','edge','crowded','portals2','portals4'].includes(plan.style))probability=.08;
  if(plan.style==='maze'||plan.style==='thin')probability=.91;
  if(plan.style==='rooms'){const[a,b]=endpoints(m,e),x=b%m.W,y=Math.floor(b/m.W);probability=(e<N?y%8===0&&x%8!==3:x%8===0&&y%8!==3)?1:.015;}
  if(plan.style==='pockets')probability=.025;
  if(plan.style==='trap')probability=.72;
  setEdge(m,e,r()<probability?[1,-1]:[0,-1]);
 }
 if(plan.style==='pockets')pockets(m);
 // Start bodies must be contiguous through ordinary open edges in newly designed maps.
 if(!region)for(const d of m.dragons)for(let i=1;i<d.body.length;i++)setEdge(m,edgeBetween(m,d.body[i-1],d.body[i]),[0,-1]);
 if(region)for(const e of locked)m.edges[e]=base.edges[e].slice();
 let repairs=connect(m,locked,r);
 const portalCount=plan.style==='portals2'?2:plan.style==='portals4'?4:0;
 if(portalCount){portals(m,portalCount,locked,r);repairs+=connect(m,locked,r);}
 const nb=graph(m),core=coreOf(nb),da=bfs(nb,m.dragons.filter(d=>d.team===0).flatMap(d=>d.body)),db=bfs(nb,m.dragons.filter(d=>d.team===1).flatMap(d=>d.body));
 for(const k of tileReps(m)) {
  if(region&&region.mask[k]){setTile(m,k,base.tiles[k]);continue;}
  const x=k%m.W,y=Math.floor(k/m.W),middle=da[k]>=0&&db[k]>=0&&da[k]+db[k]>0&&da[k]/(da[k]+db[k])>=.4&&da[k]/(da[k]+db[k])<.6;
  let value=[0,0],z=r();
  if(plan.style==='trap')value=base.tiles[k][1]>0?[0,0]:[60,180];
  else if(['sparse','far'].includes(plan.style))value=z<.09?[80,400]:[0,0];
  else if(plan.style==='centre')value=middle?(z<.12?[4,12]:[40,160]):z<.15?[120,400]:[0,0];
  else if(plan.style==='edge')value=Math.min(x,m.W-1-x,y,m.H-1-y)<3?(z<.07?[4,12]:[60,180]):z<.1?[150,350]:[0,0];
  else if(plan.style==='pockets')value=!core[k]?(z<.65?[4,12]:[20,80]):z<.15?[100,300]:[0,0];
  else value=z<.5?[60,220]:z<.505?[4,12]:[0,0];
  setTile(m,k,value);
 }
 // Force at least a pair of fountain tiles for ordinary non-sparse families.
 if(!region&&!['sparse','far','maze','thin'].includes(plan.style)){const candidates=tileReps(m).filter(k=>plan.style!=='centre'||da[k]>=0&&db[k]>=0&&Math.abs(da[k]-db[k])<=2);if(candidates.length)setTile(m,candidates[0],[4,12]);}
 let trap=null;if(region){const mutableTiles=region.mask.filter(x=>!x).length,mutableEdges=m.edges.length-locked.size,edgeChanged=m.edges.filter((e,k)=>JSON.stringify(e)!==JSON.stringify(base.edges[k])).length,tileChanged=m.tiles.filter((g,k)=>JSON.stringify(g)!==JSON.stringify(base.tiles[k])).length,spawnChanged=m.tiles.filter((g,k)=>Boolean(g[1])!==Boolean(base.tiles[k][1])).length;
  trap={source:plan.source,radius:region.radius,distance:'toroidal Manhattan from every start head',preservedTileCount:N-mutableTiles,preservedEdgeCount:locked.size,mutableTiles,mutableEdges,changedEdges:edgeChanged,changedTiles:tileChanged,changedSpawnSupport:spawnChanged,edgeChangeShare:edgeChanged/m.edges.length,tileChangeShare:tileChanged/N,spawnSupportChangeShare:spawnChanged/N,mutableEdgeChangeShare:mutableEdges?edgeChanged/mutableEdges:0,mutableSpawnChangeShare:mutableTiles?spawnChanged/mutableTiles:0,localPreserved:m.tiles.every((g,k)=>!region.mask[k]||JSON.stringify(g)===JSON.stringify(base.tiles[k]))&&[...locked].every(e=>JSON.stringify(m.edges[e])===JSON.stringify(base.edges[e])),sameStarts:JSON.stringify(m.dragons)===JSON.stringify(base.dragons)};
 }
 return {m,repairs,trap};
}
function generate(seed=20261001) {
 const census=JSON.parse(fs.readFileSync(path.join(ROOT,'exp/mapgen/census.json'),'utf8')),p=[...plans];
 for(const source of L.mapFiles(['maps/online-20260927'])){const b=read(source);p.push({family:'X',W:b.W,H:b.H,symmetry:b.symmetry,style:'trap',source,count:0,length:0});}
 for(const source of ['maps/online-20260927/devil.map','maps/online-20260927/trauma.map','maps/online-20260927/trophy.map']){const b=read(source);p.push({family:'X',W:b.W,H:b.H,symmetry:b.symmetry,style:'light',source,differentStarts:true,count:1,length:5});}
 const ord={},rows=[],out=path.join(ROOT,'maps/generated');fs.mkdirSync(out,{recursive:true});
 for(let i=0;i<p.length;i++) {const plan=p[i];plan.name=`gen_${plan.family}_${String(ord[plan.family]=(ord[plan.family]||0)+1).padStart(2,'0')}`;
  let made,usedSeed,validation;for(let attempt=0;attempt<80;attempt++){usedSeed=(seed+Math.imul(i+1,1009)+attempt)>>>0;made=make(plan,usedSeed);validation=V.validate(made.m,{connected:true});if(made.trap&&made.trap.mutableEdgeChangeShare<.4)continue;if(validation.valid||plan.source&&!plan.differentStarts&&validation.errors.every(x=>x.startsWith('generated map disconnected')))break;}
  if(made.trap&&made.trap.mutableEdgeChangeShare<.4)throw Error(plan.name+': mutable edge change below 40%');
  // An immutable source neighbourhood can contain sealed components. Record rather than alter it.
  const exception=validation.errors.length>0&&made.trap&&validation.errors.every(x=>x.startsWith('generated map disconnected'));
  if(!validation.valid&&!exception)throw Error(plan.name+': '+validation.errors.join('; '));
  const file=`maps/generated/${plan.name}.map`;fs.writeFileSync(path.join(ROOT,file),serialize(made.m));const met=metrics(made.m),outside=Object.entries(census.envelope).flatMap(([k,e])=>met[k]!==null&&(met[k]<e.min||met[k]>e.max)?[`${k}=${met[k]} outside [${e.min}, ${e.max}]`]:[]);
  const exercises=['W3 실행 중 지도 모형'];if(plan.family==='S')exercises.push('W7 작은 지도 생존');if(met.pocketTiles)exercises.push('주머니·수확');if(met.portalPairCount)exercises.push('포털');if(['L','R'].includes(plan.family))exercises.push('v1.6h 넓은 지도 전환');if(plan.family==='X')exercises.push('W2 인식 함정');
  rows.push({name:plan.name,file,seed:usedSeed,family:plan.family,style:plan.style,source:plan.source||null,differentStarts:!!plan.differentStarts,sha256:hash(made.m),metrics:met,envelope:outside.length?'stress':'inside',outsideEnvelope:outside,exercises,connectivityRepairOrbits:made.repairs,trap:made.trap,staticValid:validation.valid,connectivityException:exception?'원본의 보존 영역에 분리된 구역이 있어 전 칸 연결 불가':null});
 }
 const manifest={createdAt:new Date().toISOString(),seed,mapCount:rows.length,census:'exp/mapgen/census.json',purpose:'기제 점검: 발동·판면·깨짐 확인. 승패 판정 금지.',trapChangeDenominator:'보존 영역 밖 40%; 전체 변경률 별도. 사용자 확인 대기 뒤 기본값 적용.',maps:rows};fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');return manifest;
}
if(require.main===module){const a=process.argv.slice(2),i=a.indexOf('--seed'),s=i>=0?Number(a[i+1]):20261001;if(!Number.isInteger(s)||s<0||s>0xffffffff)throw Error('seed must be uint32');const m=generate(s);console.log(JSON.stringify({maps:m.mapCount,strictValid:m.maps.filter(x=>x.staticValid).length,exceptions:m.maps.filter(x=>x.connectivityException).map(x=>({name:x.name,components:x.metrics.componentSizes})),stress:m.maps.filter(x=>x.envelope==='stress').length}));}
module.exports={RNG,plans,make,generate,protectedRegion};
