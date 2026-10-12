'use strict';
const DIRS=['N','E','S','W'],DX={N:0,E:1,S:0,W:-1},DY={N:-1,E:0,S:1,W:0};
function geometry(M){
 const W=M.width,H=M.height,N=W*H,wx=x=>(x%W+W)%W,wy=y=>(y%H+H)%H,key=p=>p.y*W+p.x,point=k=>({x:k%W,y:k/W|0});
 const canon=e=>e.side==='S'?{x:e.x,y:wy(e.y+1),side:'N'}:e.side==='E'?{x:wx(e.x+1),y:e.y,side:'W'}:e,portal=new Map();
 for(const pair of M.portals||[]){if(pair.length!==2)continue;const[a,b]=pair.map(canon);portal.set([a.x,a.y,a.side].join(','),b);portal.set([b.x,b.y,b.side].join(','),a);}
 const hk=(x,y)=>M.initialHEdges[wy(y)*W+x]===1||(wy(y)===0&&M.initialHEdges[H*W+x]===1),vk=(x,y)=>M.initialVEdges[y*(W+1)+wx(x)]===1||(wx(x)===0&&M.initialVEdges[y*(W+1)+W]===1);
 function across(k,d){const{x,y}=point(k);let ek,kelp;if(d==='N'){ek=[x,y,'N'];kelp=hk(x,y);}else if(d==='S'){ek=[x,wy(y+1),'N'];kelp=hk(x,y+1);}else if(d==='W'){ek=[x,y,'W'];kelp=vk(x,y);}else{ek=[wx(x+1),y,'W'];kelp=vk(x+1,y);}const p=portal.get(ek.join(','));if(p)return d==='N'?wy(p.y-1)*W+p.x:d==='S'?p.y*W+p.x:d==='W'?p.y*W+wx(p.x-1):p.y*W+p.x;if(kelp)return null;return wy(y+DY[d])*W+wx(x+DX[d]);}
 const edges=Array.from({length:N},(_,k)=>Object.fromEntries(DIRS.map(d=>[d,across(k,d)]))),nb=edges.map(e=>[...new Set(Object.values(e).filter(k=>k!==null))]),rev=Array.from({length:N},()=>[]);
 for(let k=0;k<N;k++)for(const n of nb[k])rev[n].push(k);
 const mutual=nb.map((a,k)=>a.filter(n=>nb[n].includes(k))),tin=new Int32Array(N).fill(-1),low=new Int32Array(N),bridges=new Set(),articulations=new Set();let clock=0;
 function dfs(k,p){tin[k]=low[k]=clock++;let children=0;for(const n of mutual[k]){if(n===p)continue;if(tin[n]>=0)low[k]=Math.min(low[k],tin[n]);else{children++;dfs(n,k);low[k]=Math.min(low[k],low[n]);if(p!==-1&&low[n]>=tin[k])articulations.add(k);if(low[n]>tin[k])bridges.add([Math.min(k,n),Math.max(k,n)].join(','));}}if(p===-1&&children>1)articulations.add(k);}
 for(let k=0;k<N;k++)if(tin[k]<0)dfs(k,-1);
 const comp=new Int32Array(N).fill(-1),parts=[];
 for(let k=0;k<N;k++)if(comp[k]<0){const cid=parts.length,q=[k];comp[k]=cid;for(let i=0;i<q.length;i++)for(const n of mutual[q[i]])if(comp[n]<0&&!bridges.has([Math.min(q[i],n),Math.max(q[i],n)].join(','))){comp[n]=cid;q.push(n);}parts.push(q);}
 const entries=parts.map(()=>[]);for(let k=0;k<N;k++)for(const n of nb[k])if(comp[k]!==comp[n])entries[comp[n]].push({outside:k,inside:n});
 function distance(target,blocked=new Set(),allowedStart=null){const a=new Int32Array(N).fill(-1),q=[target];a[target]=0;for(let i=0;i<q.length;i++)for(const n of rev[q[i]])if(a[n]<0&&(!blocked.has(n)||n===allowedStart)){a[n]=a[q[i]]+1;q.push(n);}return a;}
 const tor=(a,b)=>{const p=point(a),q=point(b),dx=Math.abs(p.x-q.x),dy=Math.abs(p.y-q.y);return Math.min(dx,W-dx)+Math.min(dy,H-dy);},cheb=(a,b)=>{const p=point(a),q=point(b),dx=Math.abs(p.x-q.x),dy=Math.abs(p.y-q.y);return Math.max(Math.min(dx,W-dx),Math.min(dy,H-dy));};
 return {W,H,N,key,point,edges,nb,rev,comp,parts,entries,distance,tor,cheb,portal,articulations};
}
function state(s,G){const drag=new Map(s.dragons.map(d=>[d.id,{...d,body:d.body.map(G.key)}])),occ=new Map();for(const d of drag.values())for(const k of d.body)occ.set(k,d.id);return {drag,occ,pearls:new Set(s.pearls)};}
function moveOne(body,n,pearls,paid=false){const out=[n,...body];if(!pearls.has(n))out.pop();if(paid)out.pop();return out;}
function neighbours(S,q,G,remove=null){return DIRS.map(dir=>{const tile=G.edges[q.body[0]][dir],id=tile===null?null:S.occ.get(tile),o=S.drag.get(id);return {dir,tile,point:tile===null?null:G.point(tile),id:id??null,kind:tile===null?'wall':id===undefined||remove&&remove(o)?'free':id===q.id?'self':o.team===q.team?'ally':'enemy',isHead:!!o&&o.body[0]===tile};});}
function cycle(S,q,G){
 const tail=q.body.at(-1),head=q.body[0],prev=new Int32Array(G.N).fill(-2),queue=[];prev[head]=-1;
 for(const n of G.nb[head])if(!S.occ.has(n)){prev[n]=head;queue.push(n);}
 let found=null;for(let i=0;i<queue.length&&found===null;i++)for(const n of G.nb[queue[i]]){if(n===tail){prev[tail]=queue[i];found=tail;break;}if(prev[n]===-2&&!S.occ.has(n)){prev[n]=queue[i];queue.push(n);}}
 if(found===null)return null;const path=[];for(let k=tail;k!==-1;k=prev[k])path.push(k);path.reverse();const c=[...path,...q.body.slice(1,-1).reverse()];
 if(c.length<=q.body.length||new Set(c).size!==c.length||c.some((k,i)=>!G.nb[k].includes(c[(i+1)%c.length])))return null;
 return {tiles:c,coordinates:c.map(G.point),C:c.length,Q:q.body.length,G:c.length-q.body.length,free:Math.ceil(q.body.length/4),gateSkipSteps:c.length-q.body.length+2,capacity:true,pearlTiles:c.filter(k=>S.pearls.has(k)),method:'shortest currently empty head-to-tail detour + reversed actual body; aligned simple cycle'};
}
function flood(S,q,G){const seen=new Set([q.body[0]]),queue=[q.body[0]];for(let i=0;i<queue.length;i++)for(const n of G.nb[queue[i]])if(!seen.has(n)&&!S.occ.has(n)){seen.add(n);queue.push(n);}return queue;}
function room(S,q,G){const c=cycle(S,q,G),cid=G.comp[q.body[0]],part=G.parts[cid],entry=G.entries[cid],gates=[...new Set(entry.map(e=>e.inside))],free=flood(S,q,G),ns=neighbours(S,q,G);let kind=c?'circulatable-cycle':part.length===1&&G.nb[q.body[0]].length<=2?'corridor':gates.length===1&&part.length<=100||free.length<=9?'pocket':'open-area';
 const v={chamberTiles:part.length,incomingEdges:entry.length,gateTiles:gates,allBodyInside:q.body.every(k=>G.comp[k]===cid),enemyInside:[...S.drag.values()].filter(d=>d.team!==q.team&&G.comp[d.body[0]]===cid).map(d=>d.id),singleEntryTile:gates.length===1,gateOnCycle:!!c&&gates.length===1&&c.tiles.includes(gates[0]),freeSufficient:!!c&&c.free>=c.gateSkipSteps,noCurrentPearlOnCycle:!!c&&c.pearlTiles.length===0,gateOccupiedByQueenBody:gates.length===1&&q.body.slice(1).includes(gates[0]),note:'bridge-free terrain component; directed incoming edges and portals included; candidate cycle witness only, no claim of long-term vault control'};
 v.fixedLengthVaultCandidate=!!c&&v.singleEntryTile&&v.allBodyInside&&v.enemyInside.length===0&&v.gateOnCycle&&v.freeSufficient&&v.noCurrentPearlOnCycle;
 return {kind,freeFirstSteps:ns.filter(n=>n.kind==='free').map(n=>n.dir),neighbours:ns,floodTiles:free.length,terrainComponent:cid,terrainComponentSize:part.length,cycle:c,vault:v};
}
function safeSteps(S,q,G){const enemies=[...S.drag.values()].filter(e=>e.team!==q.team&&e.id>q.id),steps=[];
 for(const n of neighbours(S,q,G).filter(n=>n.kind==='free')){
  const body=moveOne(q.body,n.tile,S.pearls),dist=G.distance(n.tile);const hunters=enemies.map(e=>{const d=dist[e.body[0]],f=Math.ceil(e.body.length/4),M=f+e.body.length-2;const blocked=new Set(S.occ.keys());for(const k of q.body)blocked.delete(k);for(const k of body)blocked.add(k);blocked.delete(n.tile);blocked.delete(e.body[0]);const db=G.distance(n.tile,blocked,e.body[0])[e.body[0]];return {id:e.id,L:e.body.length,free:f,M,terrainDistance:d<0?null:d,frozenBodiesDistance:db<0?null:db,Mdanger:d>=0&&d<=M,freeDanger:d>=0&&d<=f,frozenMdanger:db>=0&&db<=M};});
  steps.push({dir:n.dir,tile:n.tile,point:n.point,afterLength:body.length,body:body.map(G.point),hunters,safeM:hunters.every(h=>!h.Mdanger),safeFree:hunters.every(h=>!h.freeDanger),safeFrozenM:hunters.every(h=>!h.frozenMdanger)});
 }
 return {legal:steps.length,safeM:steps.filter(s=>s.safeM).map(s=>s.dir),safeFree:steps.filter(s=>s.safeFree).map(s=>s.dir),safeFrozenM:steps.filter(s=>s.safeFrozenM).map(s=>s.dir),steps,scope:'known living later-id enemy heads, no pearl extension/split children; M uses terrain shortest paths ignoring bodies; frozen bodies is a second diagnostic, not a guarantee'};
}
function killerSearch(S,hunter,target,G,maxNodes=40000){
 const f=Math.ceil(hunter.body.length/4),M=f+hunter.body.length-2,terrain=G.distance(target),blocked=new Set(S.occ.keys());for(const k of hunter.body)blocked.delete(k);blocked.delete(target);
 let nodes=0,answer=null,capped=false;const start=terrain[hunter.body[0]];if(start<0)return {path:null,complete:true,nodes:0};
 function dfs(body,pearls,steps,limit,path){if(++nodes>maxNodes){capped=true;return false;}const h=body[0],remaining=limit-steps;if(terrain[h]<0||terrain[h]>remaining)return false;if(steps>=limit||steps>=f&&body.length<=2)return false;
  const next=Object.entries(G.edges[h]).filter(([,n])=>n!==null).sort((a,b)=>(terrain[a[1]]<0?999:terrain[a[1]])-(terrain[b[1]]<0?999:terrain[b[1]]));
  for(const [dir,n]of next){if(body.includes(n)||blocked.has(n))continue;if(n===target){answer=path+dir;return true;}const nb=moveOne(body,n,pearls,steps>=f),np=new Set(pearls);np.delete(n);if(dfs(nb,np,steps+1,limit,path+dir))return true;if(capped)return false;}return false;
 }
 for(let lim=Math.max(1,start);lim<=M&&!capped;lim++)if(dfs(hunter.body,S.pearls,0,lim,''))break;
 return {path:answer,pathLength:answer?.length??null,complete:!capped,nodes,free:f,M,condition:'one hunter moves, all other bodies frozen, actual pearls on path; search depth bounded by no-pearl M (extensions beyond M not excluded)'};
}
module.exports={geometry,state,neighbours,moveOne,cycle,room,safeSteps,killerSearch,DIRS};
function smallViability(S,q,G){
 const blocked=new Set([...S.occ].filter(([,id])=>id!==q.id).map(([k])=>k)),allowed=new Set([q.body[0]]),todo=[q.body[0]];
 for(let i=0;i<todo.length&&todo.length<=9;i++)for(const n of G.nb[todo[i]])if(!blocked.has(n)&&!allowed.has(n)){allowed.add(n);todo.push(n);}
 if(todo.length>9||!q.body.every(k=>allowed.has(k)))return {tested:false,reason:'body-accessible region exceeds nine tiles or excludes a body tile'};
 const status=new Map(),stack=[],moves=[];let nodes=0,witness=null,capped=false;
 function dfs(body){const k=body.join(',');if(status.get(k)===1){const i=stack.findIndex(x=>x.key===k);witness={prefix:moves.slice(0,i).join(''),loop:moves.slice(i).join(''),repeatBody:body.map(G.point)};return true;}if(status.get(k)===2)return false;if(++nodes>20000){capped=true;return false;}status.set(k,1);stack.push({key:k});
  for(const[dir,n]of Object.entries(G.edges[body[0]]))if(n!==null&&allowed.has(n)&&!body.includes(n)){const next=[n,...body.slice(0,-1)];moves.push(dir);if(dfs(next))return true;moves.pop();if(capped)return false;}
  stack.pop();status.set(k,2);return false;
 }
 dfs(q.body);return {tested:true,tiles:[...allowed],area:allowed.size,L:q.body.length,viable:!!witness,witness,nodes,capped,scope:'fixed other bodies; no pearls/growth/splits; actual terrain edges and ordered queen body, same state graph criterion as safe-cycle catalogue'};
}
module.exports.smallViability=smallViability;
