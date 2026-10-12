// Independently recount >=10-round stays within path 4 of one pocket mouth.
// Heads come directly from replay updates. Nearest-mouth labels use separate bounded BFSs.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..'),O=path.join(__dirname,'cache'),raw=require(path.join(ROOT,'legacy/exp/intake-gap/rawload.js')),{geo}=require('./recount');
const P=JSON.parse(fs.readFileSync(path.join(O,'population.json'),'utf8')),ind=new Map(fs.readFileSync(path.join(O,'recount.jsonl'),'utf8').split('\n').filter(Boolean).map(JSON.parse).map(r=>[r.key,r])),tasks=P.tasks.filter(t=>ind.has(t.key)),labelsCache=new Map(),file=path.join(O,'park-recount.jsonl'),done=new Set(fs.existsSync(file)?fs.readFileSync(file,'utf8').split('\n').filter(Boolean).map(l=>JSON.parse(l).key):[]);
const matrix=()=>Array.from({length:4},()=>Array(6).fill(0)),ph=r=>r<100?0:r<250?1:r<375?2:3;
function labels(g){const key=JSON.stringify(g.directions);if(labelsCache.has(key))return labelsCache.get(key);const n=g.N,und=Array.from({length:n},()=>new Set()),reverse=Array.from({length:n},()=>[]);for(let k=0;k<n;k++)for(const v of g.adj[k]){und[k].add(v);und[v].add(k);reverse[v].push(k);}const used=new Set(),pockets=[];
 for(let k=0;k<n;k++)if(g.pocket[k]&&!used.has(k)){const ts=[k],mouth=new Set();used.add(k);for(let i=0;i<ts.length;i++)for(const v of und[ts[i]])if(!g.pocket[v])mouth.add(v);else if(!used.has(v)){used.add(v);ts.push(v);}pockets.push([...mouth]);}
 const ds=Array(n).fill(Infinity),label=Array(n).fill(-1);for(let i=0;i<pockets.length;i++){const q=pockets[i].map(k=>[k,0]),seen=new Set(pockets[i]);for(let z=0;z<q.length;z++){const[k,d]=q[z];if(d<ds[k]||d===ds[k]&&(label[k]<0||i<label[k])){ds[k]=d;label[k]=i;}if(d===4)continue;for(const v of reverse[k])if(!seen.has(v)){seen.add(v);q.push([v,d+1]);}}}labelsCache.set(key,label);return label;
}
let n=0,start=Date.now();for(const task of tasks){if(done.has(task.key))continue;if(n%100===0){const m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'})),d=cp.execFileSync('df',['-g',ROOT],{encoding:'utf8'}).trim().split('\n').pop().trim().split(/\s+/);if(!m||+m[1]<10||+d[3]<20){console.log('PAUSED');process.exit(75);}}
 const R=raw.load(task.file),g=geo(R.match.map,task.map,ind.get(task.key).layout),L=labels(g),heads=new Map(),team=new Map(),streak=new Map(),T={A:matrix(),B:matrix()},near={A:matrix(),B:matrix()};for(const d of R.match.map.initialDragons){heads.set(d.id,d.body[0].y*g.W+d.body[0].x);team.set(d.id,d.team);}let round=-1;
 for(const e of R.events){if(e.type==='roundStart'){round=e.round;for(const[id,k]of heads){const t=team.get(id),bin=g.bin[t][k],pocket=L[k];if(pocket<0){streak.delete(id);continue;}near[t][ph(round)][bin]++;let s=streak.get(id);if(!s||s.r!==round-1||s.pocket!==pocket)s={r:round,pocket,n:0,history:[]};s.r=round;s.n++;if(s.n<=10)s.history.push([ph(round),bin]);if(s.n===10)for(const[p,b]of s.history)T[t][p][b]++;else if(s.n>10)T[t][ph(round)][bin]++;streak.set(id,s);}}
  else if(e.type==='dragonUpdate'){if(round>=0)heads.set(e.id,e.head.y*g.W+e.head.x);}
  else if(e.type==='dragonSplit'){heads.set(e.parentId,e.parentBody[0].y*g.W+e.parentBody[0].x);heads.set(e.childId,e.childBody[0].y*g.W+e.childBody[0].x);team.set(e.childId,e.team);}
  else if(e.type==='dragonDeath')heads.delete(e.id);
 }
 fs.appendFileSync(file,JSON.stringify({key:task.key,A:T.A,B:T.B,nearA:near.A,nearB:near.B})+'\n');n++;if(n%100===0)console.log('progress',n+'/'+(tasks.length-done.size),'sec',Math.round((Date.now()-start)/1000));
}console.log('DONE',n,'seconds',(Date.now()-start)/1000);
