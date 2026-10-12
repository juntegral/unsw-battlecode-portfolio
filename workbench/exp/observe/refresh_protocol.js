'use strict';
const fs=require('fs'),path=require('path'),z=require('zlib'),readline=require('readline'),crypto=require('crypto'),cp=require('child_process'),L=require('./lib'),raw=require('./raw');
const O=__dirname,P=new Map(JSON.parse(fs.readFileSync(path.join(O,'population.json'))).tasks.map(t=>[t.key,t])),input=path.join(O,'games.jsonl.gz'),output=path.join(O,'games-protocol.jsonl.gz');
function guard(){const d=cp.execFileSync('df',['-k',L.ROOT],{encoding:'utf8'}).trim().split('\n').pop().split(/\s+/),m=/System-wide memory free percentage:\s*(\d+)%/.exec(cp.execFileSync('memory_pressure',['-Q'],{encoding:'utf8'}));return +d[3]/1048576>=21&&m&&+m[1]>=10;}
function run(row,a,t){
 const A=L.atlas(a.M,a.gap),R=raw.load(t.file),states=new Map(),contacts=new Map(),sentTurns=[],newContacts=[],life=new Map();let r=-1,turnCursor=0;
 for(const[q,s,id]of a.trace.contacts){const k=q+':'+s;if(!contacts.has(k))contacts.set(k,[]);contacts.get(k).push(id);}
 const make=d=>{const s={id:d.id,own:L.knowledge(A),patch:L.knowledge(A),block:L.knowledge(A),bitmap:new Uint8Array(A.N),summary:7,summaryFirst:null,seq:0,sendSeq:-1,inbox:[],blockRx:new Map(),bitmapRx:new Map(),frame:null,frameTurn:0,bitmapFrame:null,bitmapTurn:0};states.set(s.id,s);return s;};
 for(const d of a.M.initialDragons)make(d);
 const model=(K,mask=K.mask)=>({seen:K.list.length,coverage:K.list.length/A.N,mirroredSeen:L.sum(L.expanded(A,K,mask)),mask,candidates:+(!!(mask&1))+(!!(mask&2))+(!!(mask&4))});
 const archive=s=>life.set(s.id,{patchFirst:s.patch.first,summaryFirst:s.summaryFirst,blockFirst:s.block.first});
 function snapshot(round){const c=row.cp[round];for(const p of c.processes){const s=states.get(p.id);if(!s)throw Error('missing process '+p.id);p.patch=model(s.patch);p.summary=model(s.own,s.summary);p.block=model(s.block);const spawnSeen=L.sum(Array.from(s.bitmap,(v,k)=>v*A.spawn[k]));p.bitmap={seen:L.sum(s.bitmap),coverage:L.sum(s.bitmap)/A.N,spawnSeen,spawnCoverage:L.sum(A.spawn)?spawnSeen/L.sum(A.spawn):null};}a.cp[round]=c;}
 for(const e of R.events){
  if(e.type==='roundStart'){if(L.CPS.includes(r))snapshot(r);r=e.round;}
  else if(e.type==='turnStart'){
   const s=states.get(e.id);if(!s)continue;const q=a.trace.turns[turnCursor++];if(q[0]!==r||q[1]!==s.id)throw Error('turn order');s.seq++;s.head=q[3];
   for(const p of s.inbox){if(p.tile!==null)L.add(A,s.patch,p.tile,r);s.summary&=p.mask;
    for(const [kind,frame,index,count]of [['block',p.frame,p.fragment,10],['bitmap',p.bitmapFrame,p.bitmapFragment,2]]){
     const rx=kind==='block'?s.blockRx:s.bitmapRx,key=p.sender,old=rx.get(key),v=old&&old.gen===frame.gen?old:{gen:frame.gen,mask:0};v.mask|=1<<index;rx.set(key,v);
     if(v.mask===(1<<count)-1){for(const k of frame.tiles)if(kind==='block')L.add(A,s.block,k,r);else s.bitmap[k]=1;}
    }
   }s.inbox=[];
   for(const k of A.win[s.head]){L.add(A,s.own,k,r);L.add(A,s.patch,k,r);L.add(A,s.block,k,r);s.bitmap[k]=1;}
   s.summary&=s.own.mask;if(s.summaryFirst===null&&L.one(s.summary))s.summaryFirst=r;
  }
  else if(e.type==='dragonSplit')make({id:e.childId});
  else if(e.type==='dragonDeath'){const s=states.get(e.id);if(s){archive(s);states.delete(e.id);}}
  else if(e.type==='sonarPing'){
   const s=states.get(e.senderId);if(!s||s.sendSeq===s.seq)continue;s.sendSeq=s.seq;sentTurns.push([r,s.id]);
   const K=s.patch;let tile=null;if(K.list.length){if(K.sentCursor<K.list.length)tile=K.list[K.sentCursor++];else tile=K.list[(K.resendCursor++)%K.list.length];}
   if(!s.frame||s.frameTurn===20){s.frame={gen:r,tiles:A.win[s.head].slice()};s.frameTurn=0;}const fragment=s.frameTurn++%10;
   if(!s.bitmapFrame||s.bitmapTurn===4){s.bitmapFrame={gen:r,tiles:A.win[s.head].slice()};s.bitmapTurn=0;}const bitmapFragment=s.bitmapTurn++%2;
   const packet={sender:s.id,tile,mask:s.summary,frame:s.frame,fragment,bitmapFrame:s.bitmapFrame,bitmapFragment};
   for(const id of contacts.get(r+':'+s.id)||[]){const rec=states.get(id);if(!rec)throw Error('recipient not alive');rec.inbox.push(packet);newContacts.push([r,s.id,id,tile,s.summary]);}
  }
 }
 if(L.CPS.includes(r))snapshot(r);for(const c of L.CPS)if(c>r)snapshot(c);
 for(const s of states.values())archive(s);for(const p of row.lifetimes)Object.assign(p,life.get(p.id));
 a.trace.contacts=newContacts;a.trace.sonarTurns=sentTurns;
 row.protocolModel={selection:'one packet per actual send turn, chosen before any landing is used; all directions carry that packet; no ACK/receiver novelty oracle',blockFragments:10,blockRepeats:2,bitmapFragments:2,bitmapRepeats:2,alliedAuthenticationAssumed:true,protocol3Assumed:true};return row;
}
(async()=>{
 const done=new Set();if(fs.existsSync(output))for(const l of z.gunzipSync(fs.readFileSync(output)).toString().trim().split('\n'))if(l)done.add(JSON.parse(l).key);let n=done.size;console.log('RESUME completed',n);
 for await(const line of readline.createInterface({input:fs.createReadStream(input).pipe(z.createGunzip()),crlfDelay:Infinity})){
  while(!guard()){console.log('RESOURCE PAUSE');await new Promise(r=>setTimeout(r,30000));}
  const row=JSON.parse(line);if(done.has(row.key))continue;const f=path.join(O,'raw',crypto.createHash('sha256').update(row.key).digest('hex').slice(0,20)+'.json.gz'),a=JSON.parse(z.gunzipSync(fs.readFileSync(f)));run(row,a,P.get(row.key));fs.writeFileSync(f,z.gzipSync(JSON.stringify(a),{level:6}));fs.appendFileSync(output,z.gzipSync(JSON.stringify(row)+'\n',{level:6}));if(++n%100===0)console.log('protocol',n);
 }
 fs.renameSync(output,input);console.log('DONE protocol',n);
})().catch(e=>{console.error(e);process.exitCode=1;});
