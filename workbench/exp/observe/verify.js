'use strict';
// Independent head-position sweep: no action simulation or mass-ledger hooks.
const fs=require('fs'),path=require('path'),z=require('zlib'),crypto=require('crypto'),cp=require('child_process'),readline=require('readline');
const raw=require('./raw'),L=require('./lib'),O=__dirname,P=JSON.parse(fs.readFileSync(path.join(O,'population.json')));
const tasks=new Map(P.tasks.map(t=>[t.key,t]));
const mismatches=[],counts={games:0,turns:0,unionCheckpoints:0,processCheckpoints:0,inheritanceCheckpoints:0,staticFirstTeam:0,staticFirstProcess:0,sourceSonarChecks:0,protocolPackets:0,protocolProcessCheckpoints:0},samples=[];
function guard(){const d=cp.execFileSync('df',['-k',L.ROOT],{encoding:'utf8'}).trim().split('\n').pop().split(/\s+/),m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'}));return +d[3]/1048576>=21&&m&&+m[1]>=10;}
function times(n){return new Int16Array(n).fill(32767);}
function stats(A,tt,born=0){
 const et=times(2*A.N);let n=0;for(let k=0;k<A.N;k++)if(tt[k]<32767){n++;for(let d=0;d<4;d++){const e=A.eid(k,d);et[e]=Math.min(et[e],tt[k]);}}
 const rejected=Array(3).fill(32767);for(let h=0;h<3;h++){
  for(let k=0;k<A.N;k++)if(A.spawn[k]!==A.spawn[A.syms[h](k)])rejected[h]=Math.min(rejected[h],Math.max(tt[k],tt[A.syms[h](k)]));
  for(let e=0;e<2*A.N;e++)if(A.kind[e]!==A.kind[A.edgeSym[h][e]])rejected[h]=Math.min(rejected[h],Math.max(et[e],et[A.edgeSym[h][e]]));
 }
 let mask=7;for(let h=0;h<3;h++)if(rejected[h]<32767)mask&=~(1<<h);const sorted=rejected.slice().sort((a,b)=>a-b),first=sorted[1]<32767?Math.max(born,sorted[1]):null;
 return {n,mask,first};
}
function check(key,what,a,b){if(JSON.stringify(a)!==JSON.stringify(b))mismatches.push({key,what,expected:a,actual:b});}
function run(t,row){
 const R=raw.load(t.file),A=L.atlas(R.match.map,L.gaps(row,R.match.map).a),head=new Map(),states=new Map(),union={A:times(A.N),B:times(A.N)},archived=[];let r=-1;
 const make=(id,team,k,parent=null)=>{head.set(id,k);const s={id,team,born:parent?r:0,own:times(A.N),inherited:parent?parent.inherited.slice():times(A.N),edgeTimes:times(2*A.N),ownMask:7,patch:times(A.N),patchList:[],sent:0,resend:0,block:times(A.N),bitmap:times(A.N),inbox:[],summary:7,summaryFirst:null,seq:0,sendSeq:-1,blockRx:new Map(),bitmapRx:new Map(),blockFrame:null,blockTurn:0,bitmapFrame:null,bitmapTurn:0};states.set(id,s);};
 for(const d of R.match.map.initialDragons)make(d.id,d.team,d.body[0].y*A.W+d.body[0].x);
 function checkpoint(round,censored=false){
  const c=row.cp[round];for(const tm of 'AB'){const st=stats(A,union[tm]);check(t.key,'union '+round+' '+tm,c.teams[tm].seen,st.n);check(t.key,'mask '+round+' '+tm,c.teams[tm].mask,st.mask);counts.unionCheckpoints++;}
  if(!censored){for(const p of c.processes){const s=states.get(p.id);if(!s){mismatches.push({key:t.key,what:'missing process '+p.id});continue;}const st=stats(A,s.own,s.born),inh=stats(A,s.inherited,s.born);check(t.key,'process '+round+' '+p.id,p.own.seen,st.n);check(t.key,'process mask '+round+' '+p.id,p.own.mask,st.mask);check(t.key,'inheritance '+round+' '+p.id,p.inherited.seen,inh.n);counts.processCheckpoints++;counts.inheritanceCheckpoints++;
   for(const mode of ['patch','block']){const q=stats(A,s[mode],s.born);check(t.key,mode+' coverage '+round+' '+p.id,p[mode].seen,q.n);check(t.key,mode+' mask '+round+' '+p.id,p[mode].mask,q.mask);}
   check(t.key,'bitmap '+round+' '+p.id,p.bitmap.seen,s.bitmap.reduce((n,q)=>n+(q<32767),0));check(t.key,'summary mask '+round+' '+p.id,p.summary.mask,s.summary);counts.protocolProcessCheckpoints++;
  }}
 }
 const auditFile=path.join(O,'raw',crypto.createHash('sha256').update(t.key).digest('hex').slice(0,20)+'.json.gz'),audit=JSON.parse(z.gunzipSync(fs.readFileSync(auditFile))),trace=audit.trace.turns,contacts=new Map();let q=0,sendCursor=0;
 for(const [r,s,id,tile,mask]of audit.trace.contacts){const k=r+':'+s;if(!contacts.has(k))contacts.set(k,[]);contacts.get(k).push({id,tile,mask});}
 const window=k=>{const out=[],x=k%A.W,y=k/A.W|0;for(let yy=y-3;yy<=y+3;yy++)for(let xx=x-3;xx<=x+3;xx++)out.push(((yy%A.H+A.H)%A.H)*A.W+(xx%A.W+A.W)%A.W);return out;};
 const addPatch=(s,k,r)=>{if(s.patch[k]===32767)s.patchList.push(k);s.patch[k]=Math.min(s.patch[k],r);};
 for(const e of R.events){
  if(e.type==='roundStart'){if(L.CPS.includes(r))checkpoint(r);r=e.round;}
  else if(e.type==='turnStart'){
   const s=states.get(e.id);if(!s)continue;const k=head.get(e.id);check(t.key,'pre-turn '+q,trace[q],[r,e.id,s.team,k]);q++;counts.turns++;s.seq++;s.lastHead=k;
   for(const p of s.inbox){if(p.tile!==null)addPatch(s,p.tile,r);s.summary&=p.mask;for(const [mode,frame,part,need]of [['block',p.frame,p.part,10],['bitmap',p.bitmap,p.bitmapPart,2]]){const rx=mode==='block'?s.blockRx:s.bitmapRx,old=rx.get(p.sender),v=old&&old.gen===frame.gen?old:{gen:frame.gen,mask:0};v.mask|=1<<part;rx.set(p.sender,v);if(v.mask===(1<<need)-1)for(const a of frame.tiles)s[mode][a]=Math.min(s[mode][a],r);}}s.inbox=[];
   // Independent coordinate loops, rather than the extractor's cached window lists.
   const x=k%A.W,y=k/A.W|0;for(let yy=y-3;yy<=y+3;yy++)for(let xx=x-3;xx<=x+3;xx++){const a=((yy%A.H+A.H)%A.H)*A.W+(xx%A.W+A.W)%A.W,fresh=s.own[a]===32767;s.own[a]=Math.min(s.own[a],r);s.inherited[a]=Math.min(s.inherited[a],r);union[s.team][a]=Math.min(union[s.team][a],r);addPatch(s,a,r);s.block[a]=Math.min(s.block[a],r);s.bitmap[a]=Math.min(s.bitmap[a],r);
    if(fresh){for(let d=0;d<4;d++)s.edgeTimes[A.eid(a,d)]=Math.min(s.edgeTimes[A.eid(a,d)],r);
    for(let h=0;h<3;h++)if(s.ownMask&(1<<h)){const m=A.syms[h](a);if(s.own[m]<32767&&A.spawn[a]!==A.spawn[m])s.ownMask&=~(1<<h);for(let d=0;d<4;d++){const ee=A.eid(a,d),me=A.edgeSym[h][ee];if(s.edgeTimes[me]<32767&&A.kind[ee]!==A.kind[me])s.ownMask&=~(1<<h);}}}
   }s.summary&=s.ownMask;if(s.summaryFirst===null&&L.one(s.summary))s.summaryFirst=r;
  }
  else if(e.type==='dragonUpdate'){head.set(e.id,e.head.y*A.W+e.head.x);}
  else if(e.type==='dragonSplit'){const p=states.get(e.parentId);head.set(e.parentId,e.parentBody[0].y*A.W+e.parentBody[0].x);make(e.childId,e.team,e.childBody[0].y*A.W+e.childBody[0].x,p);}
  else if(e.type==='dragonDeath'){const s=states.get(e.id);if(s)archived.push(s);states.delete(e.id);head.delete(e.id);}
  else if(e.type==='sonarPing'){
   const s=states.get(e.senderId);if(!s||s.sendSeq===s.seq)continue;s.sendSeq=s.seq;check(t.key,'send turn '+sendCursor,audit.trace.sonarTurns[sendCursor++],[r,s.id]);let tile=null;if(s.patchList.length)tile=s.sent<s.patchList.length?s.patchList[s.sent++]:s.patchList[s.resend++%s.patchList.length];
   if(!s.blockFrame||s.blockTurn===20){s.blockFrame={gen:r,tiles:window(s.lastHead)};s.blockTurn=0;}const part=s.blockTurn++%10;
   if(!s.bitmapFrame||s.bitmapTurn===4){s.bitmapFrame={gen:r,tiles:window(s.lastHead)};s.bitmapTurn=0;}const bitmapPart=s.bitmapTurn++%2;
   for(const p of contacts.get(r+':'+s.id)||[]){check(t.key,'causal tile packet '+r+' '+s.id,p.tile,tile);check(t.key,'causal symmetry packet '+r+' '+s.id,p.mask,s.summary);const rec=states.get(p.id);if(!rec)throw Error('missing receiver');rec.inbox.push({sender:s.id,tile,mask:s.summary,frame:s.blockFrame,part,bitmap:s.bitmapFrame,bitmapPart});counts.protocolPackets++;}
  }
 }
 if(L.CPS.includes(r))checkpoint(r);for(const c of L.CPS)if(c>r)checkpoint(c,true);
 archived.push(...states.values());const life=new Map(row.lifetimes.map(v=>[v.id,v]));for(const s of archived){const v=stats(A,s.own,s.born),p=life.get(s.id);check(t.key,'process first '+s.id,p.ownFirst,v.first);check(t.key,'patch first '+s.id,p.patchFirst,stats(A,s.patch,s.born).first);check(t.key,'block first '+s.id,p.blockFirst,stats(A,s.block,s.born).first);check(t.key,'summary first '+s.id,p.summaryFirst,s.summaryFirst);counts.staticFirstProcess++;}
 for(const tm of 'AB'){const v=stats(A,union[tm]);check(t.key,'union first '+tm,row.cp[200].teams[tm].first,v.first!==null&&v.first<=200?v.first:null);counts.staticFirstTeam++;}
 counts.games++;
 if(counts.games%100===0)console.log('verify',counts.games,'/'+P.tasks.length,'mismatches',mismatches.length);
}
(async()=>{
 for await(const line of readline.createInterface({input:fs.createReadStream(path.join(O,'games.jsonl.gz')).pipe(z.createGunzip()),crlfDelay:Infinity})){while(!guard()){console.log('RESOURCE PAUSE');await new Promise(r=>setTimeout(r,30000));}const row=JSON.parse(line);run(tasks.get(row.key),row);}
 // A stratified official-parser crosscheck also covers 64-bit sonar values and delivery fields.
 const official=require('../../tools/replay');const choose=P.tasks.filter(t=>t.src==='local').slice(0,4).concat(P.tasks.filter(t=>t.src==='online').filter((t,i)=>i%200===0),P.tasks.filter(t=>t.src==='top').filter((t,i)=>i%64===0));
 for(const t of choose){const a=raw.load(t.file).events.filter(e=>e.type==='sonarPing'),b=official.load(t.file).events.filter(e=>e.type==='sonarPing');check(t.key,'official sonar count',b.length,a.length);for(let i=0;i<a.length;i++){counts.sourceSonarChecks++;for(const f of ['senderId','hitId','direction','origin','end','hitKind'])check(t.key,'official sonar '+i+' '+f,b[i][f],a[i][f]);check(t.key,'official sonar value '+i,String(b[i].value64),String(a[i].value64));}samples.push(t.key);}
 fs.writeFileSync(path.join(O,'verification-heads.json'),JSON.stringify({method:'replay dragonUpdate/split head positions; independently constructed coordinate windows; static decision via earliest contradiction witnesses; no mass-ledger or action simulation',counts,mismatchN:mismatches.length,mismatches:mismatches.slice(0,100),officialParserSampleGames:samples.length,samples},null,1));console.log('DONE',counts,'mismatches',mismatches.length);
})().catch(e=>{console.error(e);process.exitCode=1;});
