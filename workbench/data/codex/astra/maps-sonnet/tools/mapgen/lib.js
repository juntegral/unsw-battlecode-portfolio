'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '../..');
const EXISTING = ['maps/online-20260927', 'maps/bundled', 'maps/server-b', 'maps/variants'];
const mod = (x, n) => (x % n + n) % n;
const sum = a => a.reduce((s, x) => s + x, 0);
const hist = a => Object.fromEntries([...new Set(a)].sort((a,b)=>a-b).map(x=>[x,a.filter(y=>x===y).length]));
function mapFiles(dirs) { return dirs.flatMap(d => fs.statSync(path.resolve(ROOT,d)).isDirectory() ? fs.readdirSync(path.resolve(ROOT,d)).filter(f=>f.endsWith('.map')).sort().map(f=>path.join(d,f)) : [d]); }
function blank(W,H,symmetry,name) { return {W,H,symmetry,name,tiles:Array.from({length:W*H},()=>[0,0]),edges:Array.from({length:2*W*H},()=>[0,-1]),dragons:[]}; }
// Canonical toroidal edges: first N north edges, next N west edges.
function decodeEdge(m, i) {
  const row=Math.floor(i/(m.W+1)), x=i%(m.W+1);
  if(row%2===0) { if(x===m.W) return null; return mod(row/2,m.H)*m.W+x; }
  return m.W*m.H+Math.floor(row/2)*m.W+mod(x,m.W);
}
function encodeEdge(m,k) { const N=m.W*m.H, z=k%N, x=z%m.W, y=Math.floor(z/m.W); return (2*y+(k>=N?1:0))*(m.W+1)+x; }
// Names describe the mirror AXIS: y is left/right, x is top/bottom.
function mirrorTile(m,k) { let x=k%m.W,y=Math.floor(k/m.W); if(m.symmetry.includes('y'))x=m.W-1-x; if(m.symmetry.includes('x'))y=m.H-1-y; return y*m.W+x; }
function mirrorEdge(m,k) {
  const N=m.W*m.H,z=k%N,hor=k<N; let x=z%m.W,y=Math.floor(z/m.W);
  if(m.symmetry.includes('y')) x=mod(m.W-(hor?1:0)-x,m.W);
  if(m.symmetry.includes('x')) y=mod(m.H-(hor?0:1)-y,m.H);
  return (hor?0:N)+y*m.W+x;
}
function parse(text, file='<text>') {
  const lines=text.split(/\r?\n/).map(l=>l.trim()).filter(l=>l&&!l.startsWith('#'));
  const fail=s=>{throw Error(file+': '+s);};
  if(!/^MAP \d+ \d+$/.test(lines[0]||''))fail('MAP must be first');
  const [W,H]=lines[0].split(/\s+/).slice(1).map(Number); if(W<10||W>64||H<10||H>64)fail('dimensions 10..64');
  const m=blank(W,H,'',''), seen=new Set(), counts={}, actual={TILE:0,EDGE:0,DRAGON:0}, tileSeen=new Set(), rawEdges=new Map();let ended=false;
  for(const line of lines.slice(1)) {
    if(ended)fail('directives after END');
    const a=line.split(/\s+/),kind=a.shift(), v=a.map(Number);
    const ints=n=>{if(v.length!==n||v.some(x=>!Number.isSafeInteger(x)))fail('invalid '+line);};
    if(['MAP_NAME','SYMMETRY','TILE_COUNT','EDGE_COUNT','DRAGON_COUNT'].includes(kind)) {if(seen.has(kind))fail('duplicate '+kind);seen.add(kind);}
    if(kind==='MAP_NAME') { if(!a.length)fail('empty name');m.name=a.join(' '); }
    else if(kind==='SYMMETRY') {if(a.length!==1||!['x','y','xy'].includes(a[0]))fail('invalid symmetry');m.symmetry=a[0];}
    else if(kind.endsWith('_COUNT')&&['TILE','EDGE','DRAGON'].includes(kind.slice(0,-6))) {ints(1);if(v[0]<0)fail('negative count');counts[kind.slice(0,-6)]=v[0];}
    else if(kind==='TILE') {ints(4);const[x,y,lo,hi]=v,k=y*W+x;if(x<0||x>=W||y<0||y>=H||lo<0||hi<lo||hi>0&&lo<1)fail('tile bounds/gap');if(tileSeen.has(k))fail('duplicate tile');tileSeen.add(k);m.tiles[k]=[lo,hi];actual.TILE++;}
    else if(kind==='EDGE') {ints(3);const[i,t,id]=v;if(i<0||i>=(2*H+1)*(W+1)||![0,1,2].includes(t)||t===2&&id<0||t!==2&&id!==-1)fail('edge bounds/type/id');if(rawEdges.has(i))fail('duplicate edge index');const k=decodeEdge(m,i);if(k===null&&t!==0)fail('horizontal padding edge');rawEdges.set(i,[t,id]);if(k!==null&&t!==0){if(m.edges[k][0]!==0&&JSON.stringify(m.edges[k])!==JSON.stringify([t,id]))fail('conflicting wrap aliases');m.edges[k]=[t,id];}actual.EDGE++;}
    else if(kind==='DRAGON') {if(v.some(x=>!Number.isSafeInteger(x))||v.length<2)fail('dragon integers');const[team,n,...xy]=v;if(![0,1].includes(team)||n<2||xy.length!==2*n)fail('dragon team/length');const body=[];for(let j=0;j<xy.length;j+=2){const[x,y]=xy.slice(j,j+2);if(x<0||x>=W||y<0||y>=H)fail('dragon bounds');body.push(y*W+x);}m.dragons.push({team,body});actual.DRAGON++;}
    else if(kind==='END'&&a.length===0) { ended=true; }
    else fail('unknown directive '+kind);
  }
  for(const kind of Object.keys(actual))if(counts[kind]!==actual[kind])fail(kind+'_COUNT mismatch/missing');
  m.file=file; return m;
}
const read = file => parse(fs.readFileSync(path.resolve(ROOT,file),'utf8'),file);
function endpoints(m,e) {const N=m.W*m.H,k=e%N,x=k%m.W,y=Math.floor(k/m.W);return e<N?[mod(y-1,m.H)*m.W+x,k]:[y*m.W+mod(x-1,m.W),k];}
function edgeBetween(m,a,b) {const x=a%m.W,y=Math.floor(a/m.W),bx=b%m.W,by=Math.floor(b/m.W),N=m.W*m.H;if(x===bx){if(mod(y+1,m.H)===by)return b;if(mod(y-1,m.H)===by)return a;}if(y===by){if(mod(x+1,m.W)===bx)return N+b;if(mod(x-1,m.W)===bx)return N+a;}return -1;}
function graph(m, portals=true) {
  const N=m.W*m.H,partners=new Map(),pairs=new Map();m.edges.forEach(([t,id],e)=>{if(t===2){if(!pairs.has(id))pairs.set(id,[]);pairs.get(id).push(e);}});
  for(const es of pairs.values())if(es.length===2){partners.set(es[0],es[1]);partners.set(es[1],es[0]);}
  const nb=Array.from({length:N},()=>[]);
  for(let e=0;e<2*N;e++) {const [t]=m.edges[e],[a,b]=endpoints(m,e);if(t===1||t===2&&!portals)continue;if(t===2){const p=partners.get(e);if(p===undefined)continue;const[c,d]=endpoints(m,p);nb[a].push(d);nb[b].push(c);}else{nb[a].push(b);nb[b].push(a);}}
  return nb.map(a=>[...new Set(a)]);
}
function bfs(nb,seeds) {const d=Array(nb.length).fill(-1),q=[];for(const k of seeds)if(d[k]<0){d[k]=0;q.push(k);}for(let i=0;i<q.length;i++)for(const v of nb[q[i]])if(d[v]<0){d[v]=d[q[i]]+1;q.push(v);}return d;}
function components(nb) {const c=Array(nb.length).fill(-1),sizes=[];for(let k=0;k<nb.length;k++)if(c[k]<0){const id=sizes.length,q=[k];c[k]=id;for(let i=0;i<q.length;i++)for(const v of nb[q[i]])if(c[v]<0){c[v]=id;q.push(v);}sizes.push(q.length);}return {c,sizes};}
function coreOf(nb) {const core=Array(nb.length).fill(true),d=nb.map(a=>a.length),q=[];for(let k=0;k<d.length;k++)if(d[k]<=1)q.push(k);for(let i=0;i<q.length;i++){const k=q[i];if(!core[k])continue;core[k]=false;for(const v of nb[k])if(core[v]&&--d[v]<=1)q.push(v);}return core;}
// Width proxy: minimum of the straight horizontal and vertical open runs through a tile;
// portals terminate a run. This is geometric width, not the degree-2 share.
function corridorWidths(m) {const out=[],N=m.W*m.H;for(let k=0;k<N;k++){const x=k%m.W,y=Math.floor(k/m.W);const run=(axis)=>{const visited=new Set([k]);for(const sign of [-1,1]){let a=k;for(let j=0;j<(axis===0?m.W:m.H)-1;j++){const b=axis===0?y*m.W+mod(a%m.W+sign,m.W):mod(Math.floor(a/m.W)+sign,m.H)*m.W+x;const e=edgeBetween(m,a,b);if(m.edges[e][0]!==0||visited.has(b))break;visited.add(b);a=b;}}return visited.size;};out.push(Math.min(run(0),run(1)));}return hist(out);}
function metrics(m) {
  const N=m.W*m.H,nb=graph(m),comp=components(nb),core=coreOf(nb),heads=t=>m.dragons.filter(d=>d.team===t).map(d=>d.body[0]);
  const dA=bfs(nb,m.dragons.filter(d=>d.team===0).flatMap(d=>d.body)),dB=bfs(nb,m.dragons.filter(d=>d.team===1).flatMap(d=>d.body));
  const middle=k=>dA[k]>=0&&dB[k]>=0&&(dA[k]+dB[k]===0||dA[k]/(dA[k]+dB[k])>=.4&&dA[k]/(dA[k]+dB[k])<.6);
  const spawn=m.tiles.flatMap((g,k)=>g[1]>0?[k]:[]),capacity=k=>m.tiles[k][1]>0?2/sum(m.tiles[k]):0,total=sum(spawn.map(capacity));
  const pockets=core.map((v,k)=>!v?k:-1).filter(k=>k>=0),pc=new Set(pockets),pocketComps=[];while(pc.size){const q=[pc.values().next().value];pc.delete(q[0]);for(let i=0;i<q.length;i++)for(const v of nb[q[i]])if(pc.delete(v))q.push(v);pocketComps.push(q.length);}
  const pairs=[...new Set(m.edges.filter(e=>e[0]===2).map(e=>e[1]))].map(id=>({id,edges:m.edges.flatMap(([t,p],e)=>t===2&&p===id?[encodeEdge(m,e)]:[])}));
  const headD=bfs(nb,heads(0)),startDistances=heads(1).map(k=>headD[k]).filter(d=>d>=0),gapHistogram={};for(const k of spawn){const s=m.tiles[k].join('..');gapHistogram[s]=(gapHistogram[s]||0)+1;}
  const f=spawn.filter(k=>sum(m.tiles[k])/2<=12);
  return {width:m.W,height:m.H,area:N,aspect:m.W/m.H,extremeAspect:Math.max(m.W/m.H,m.H/m.W),symmetry:m.symmetry,kelpEdges:m.edges.filter(e=>e[0]===1).length,kelpDensity:m.edges.filter(e=>e[0]===1).length/(2*N),corridorWidthDistribution:corridorWidths(m),degreeDistribution:hist(nb.map(a=>a.length)),corridorDegree2Share:nb.filter(a=>a.length===2).length/N,deadEnds:nb.filter(a=>a.length===1).length,isolatedTiles:nb.filter(a=>!a.length).length,core2Tiles:core.filter(Boolean).length,pocketTiles:pockets.length,pocketComponentSizes:pocketComps.sort((a,b)=>a-b),portalPairs:pairs,portalPairCount:pairs.length,spawnTiles:spawn.length,spawnShare:spawn.length/N,gapDistribution:gapHistogram,meanGap:spawn.length?sum(spawn.map(k=>sum(m.tiles[k])/2))/spawn.length:null,fountainTiles:f.length,fountainShare:spawn.length?f.length/spawn.length:0,fountainPositions:f.map(k=>[k%m.W,Math.floor(k/m.W)]),supply:total,centreSupplyShare:total?sum(spawn.filter(middle).map(capacity))/total:null,pocketSupplyShare:total?sum(spawn.filter(k=>!core[k]).map(capacity))/total:null,middleTiles:dA.filter((_,k)=>middle(k)).length,startDragons:[0,1].map(t=>m.dragons.filter(d=>d.team===t).length),startLengths:[0,1].map(t=>m.dragons.filter(d=>d.team===t).map(d=>d.body.length)),startDistance:startDistances.length?Math.min(...startDistances):null,componentSizes:comp.sizes.sort((a,b)=>b-a),mobileConnected:comp.sizes.filter(x=>x>1).length===1,allTilesConnected:comp.sizes.length===1,teamsReachEachOther:heads(1).some(k=>headD[k]>=0)};
}
function hash(m) {return crypto.createHash('sha256').update(JSON.stringify([m.W,m.H,m.symmetry,m.tiles,m.edges,m.dragons])).digest('hex');}
function serialize(m) {const a=[`MAP ${m.W} ${m.H}`,`MAP_NAME ${m.name}`,`SYMMETRY ${m.symmetry}`,`TILE_COUNT ${m.tiles.length}`];m.tiles.forEach((g,k)=>a.push(`TILE ${k%m.W} ${Math.floor(k/m.W)} ${g.join(' ')}`));const es=m.edges.flatMap((v,e)=>v[0]?[`EDGE ${encodeEdge(m,e)} ${v.join(' ')}`]:[]);a.push(`EDGE_COUNT ${es.length}`,...es,`DRAGON_COUNT ${m.dragons.length}`);for(const d of m.dragons)a.push(`DRAGON ${d.team} ${d.body.length} ${d.body.flatMap(k=>[k%m.W,Math.floor(k/m.W)]).join(' ')}`);return a.join('\n')+'\n';}
module.exports={fs,path,crypto,ROOT,EXISTING,mod,sum,hist,blank,read,parse,mapFiles,mirrorTile,mirrorEdge,decodeEdge,encodeEdge,endpoints,edgeBetween,graph,bfs,components,coreOf,corridorWidths,metrics,hash,serialize};
