'use strict';
const fs=require('fs'),path=require('path'),Module=require('module');
const out=__dirname,root=path.resolve(out,'../../..'),source=path.join(root,'tools/online.js');
process.env.UNSW_KEY_FILE=path.join(root,'docs/api.txt');
// Run the existing client's GET and replay routines without its CLI or outside logging.
const client=new Module(source,module);client.filename=source;client.paths=Module._nodeModulePaths(path.dirname(source));
client._compile(fs.readFileSync(source,'utf8')+'\nmodule.exports={get,fetchReplay,redact};',source);
const {get,fetchReplay,redact}=client.exports;
const pause=()=>new Promise(r=>setTimeout(r,750));
const save=(name,x)=>fs.writeFileSync(path.join(out,name),JSON.stringify(x,null,2)+'\n');
async function read(p){await pause();let x=await get(p);fs.appendFileSync(path.join(out,'remote.jsonl'),JSON.stringify({at:new Date().toISOString(),method:'GET',path:p})+'\n');return x;}
(async()=>{
 const board=await read('leaderboard');save('leaderboard-full.json',board);
 const exact=board.find(t=>t.name.toLowerCase()==='naah'); const target=exact?.id||454;
 const found=new Map();
 const prof=JSON.parse(fs.readFileSync(path.join(out,'team454.json')));
 for(const b of prof.recent||[]) if(target===454)found.set(b.id,b);
 for(const t of board.filter(t=>t.elo>=2000&&t.hasBot).sort((a,b)=>a.rank-b.rank).slice(0,35)){
  const p=await read('teams/'+t.id);if(p.team)delete p.team.code;save('profile-'+t.id+'.json',p);
  for(const b of p.recent||[])if(t.id===target||b.opponentId===target)found.set(b.id,{...b,opponentElo:t.id===target?b.opponentElo:t.elo});
 }
 const candidates=[...found.values()].filter(b=>b.opponentElo>=2000&&b.at>='2026-10-04T03:00:00Z').sort((a,b)=>b.at.localeCompare(a.at));
 save('battle-candidates.json',candidates);let games=[];
 for(const b of candidates){
  if(games.length>=120)break;
  const d=await read('battles/'+b.id);save('battle-'+b.id+'.json',d);
  for(const g of d.games||[]){
   if(games.length>=120)break;
   if(!['completed','draw'].includes(g.status))continue;
   const file='M'+g.id+'.replay';
   try{
    const gd=g.id===d.match.id?d:await read('battles/'+g.id); const m=gd.match;
    if(![m.teamAId,m.teamBId].includes(target))throw Error('wrong target');
    save('game-'+g.id+'.json',gd);
    if(!fs.existsSync(path.join(out,file))){await pause();const buf=await fetchReplay(g.id);fs.writeFileSync(path.join(out,file),buf);fs.appendFileSync(path.join(out,'remote.jsonl'),JSON.stringify({at:new Date().toISOString(),method:'GET',path:'battles/'+g.id+'/replay',bytes:buf.length})+'\n');}
    games.push({game:g.id,battle:b.id,target,replay:path.join('data/local/queen454',file),metadata:'game-'+g.id+'.json'});
    save('downloaded.json',games);
    console.log('saved',g.id,'total',games.length);
   }catch(e){fs.appendFileSync(path.join(out,'download-errors.txt'),redact(e.message)+'\n');console.log('failed',g.id,redact(e.message));}
  }
 }
 console.log('done',games.length,'target',target);
})().catch(e=>{console.error(redact(e.message));process.exitCode=1;});
