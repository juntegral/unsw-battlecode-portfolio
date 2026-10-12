'use strict';
process.env.UNSW_RULES='123';
const fs=require('fs'),path=require('path'),{load}=require('../../tools/replay');
const out={verifiedKeys:0,verifiedFateCheckpoints:0,expectedKeys:{},sets:{},errors:[]};
function scan(file,side){
 const R=load(file),teams=new Map(R.match.map.initialDragons.map(d=>[d.id,d.team])),queen=Math.min(...R.match.map.initialDragons.filter(d=>d.team===side).map(d=>d.id));
 const own=[],all=[],deaths=new Map();let round=-1,currentMover=null;
 for(const e of R.events){if(e.type==='roundStart')round=e.round;if(e.type==='turnStart')currentMover=e.id;if(e.type==='dragonSplit')teams.set(e.childId,e.team);
  if(e.type==='dragonAction'){const a={round,id:e.id,action:e.action??null,tle:!!e.tle};all.push(a);if(teams.get(e.id)===side)own.push(a);}
  if(e.type==='dragonDeath')deaths.set(e.id,{round,reason:e.reason,mover:currentMover});}
 return {own,all,deaths,rounds:round+1,queen};
}
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function independentClass(on,off,id,r,k){
 const state=(arm)=>{const d=arm.deaths.get(id);return d&&d.round<r+k?'dead':r+k>arm.rounds?'censored':'alive';};
 const a=state(on),b=state(off);return a==='censored'||b==='censored'?'censored':a==='dead'?(b==='dead'?'both':'harm'):(b==='dead'?'help':'neither');
}
for(const name of ['bodymem','bodyx','freecost','qsight']){
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,name+'.json'))),report={keys:0,firstDivergences:0,firstAllActionEqual:0,noDivergence:0,checkpointChecks:0,tables:{changed:{},queen:{}}};
 const spec=require('../'+name+'/spec.json'),expected=new Set();for(const s of spec.filter(s=>s.out==='exp/'+name+'/on'))for(const m of s.only||fs.readdirSync(path.resolve(__dirname,'../..',s.maps)).filter(f=>f.endsWith('.map')).map(f=>f.slice(0,-4)))for(const o of s.opps)for(const side of s.sides||['A','B'])for(const seed of s.seeds)expected.add([path.basename(o),m,side,seed].join(':'));
 out.expectedKeys[name]=expected.size;if(data.rows.length!==expected.size)out.errors.push({name,error:'expected key count'});
 for(const subject of ['changed','queen'])for(const k of subject==='changed'?[1,3,10]:[10,50])report.tables[subject][k]={harm:0,help:0,both:0,neither:0,censored:0};
 for(const row of data.rows){try{
  if(!expected.has(row.key))throw Error('unexpected key');
  const side=row.key.split(':').at(-2),on=scan(row.files.on,side),off=scan(row.files.off,side);report.keys++;out.verifiedKeys++;
  let i=0;while(i<on.own.length&&i<off.own.length&&eq(on.own[i],off.own[i]))i++;
  if(row.status==='no_divergence'){if(i!==on.own.length||i!==off.own.length)throw Error('no divergence wrong');report.noDivergence++;continue;}
  const a=on.own[i],b=off.own[i];if(row.R!==(a||b).round||row.id!==(a||b).id)throw Error('first divergence differs');report.firstDivergences++;
  let j=0;while(j<on.all.length&&j<off.all.length&&eq(on.all[j],off.all[j]))j++;
  const z=on.all[j]||off.all[j];if(z.round===row.R&&z.id===row.id)report.firstAllActionEqual++;else throw Error('earlier other-team action difference');
  for(const c of row.changed)for(const arm of ['on','off'])for(const k of [1,3,10,50]){
   const raw=arm==='on'?on:off,d=raw.deaths.get(c.id),target=row.R+k,expectedState=d&&d.round<target?'dead':target>raw.rounds?'censored':'alive',f=c.fates[arm].states[k];
   if(f.state!==expectedState)throw Error('dragon fate differs');if(expectedState==='dead'&&(f.death.round!==d.round||f.death.reason!==d.reason||f.death.mover!==d.mover))throw Error('death reason differs');report.checkpointChecks++;out.verifiedFateCheckpoints++;
  }
  for(const arm of ['on','off'])for(const k of [1,3,10,50]){const raw=arm==='on'?on:off,d=raw.deaths.get(raw.queen),target=row.R+k,expectedState=d&&d.round<target?'dead':target>raw.rounds?'censored':'alive';if(row.queen.fates[arm].states[k].state!==expectedState)throw Error('queen fate differs');report.checkpointChecks++;out.verifiedFateCheckpoints++;}
  if(row.status==='matched'){
   for(const k of [1,3,10]){const c=independentClass(on,off,row.id,row.R,k);if(c!==row.classification[k])throw Error('classification differs');report.tables.changed[k][c]++;}
   for(const k of [10,50]){const c=independentClass(on,off,on.queen,row.R,k);if(c!==row.queen.classification[k])throw Error('queen classification differs');report.tables.queen[k][c]++;}
  }
 }catch(e){out.errors.push({name,key:row.key,error:String(e)});} }
 if(!eq(report.tables,data.summary.tables))out.errors.push({name,error:'aggregate differs'});
 out.sets[name]=report;fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(out,null,2)+'\n');console.log(name,report.keys,'verified',report.checkpointChecks,'fates');
}
fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(out,null,2)+'\n');
if(out.errors.length){console.error(out.errors);process.exitCode=1;}
