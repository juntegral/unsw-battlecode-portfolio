'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process');
const ROOT=path.resolve(__dirname,'../..');
const env={...process.env,UNSW_RULES:'123'};
for(const v of ['v18','q18','q18b2']){
  const dirs=['king','hunter','gen'].map(s=>'exp/v16/q1/'+v+'-'+s);
  cp.execFileSync(process.execPath,['exp/v16/q1/qmech.js',...dirs,'--out','exp/q-analysis/verify-qmech-'+v+'.md'],{cwd:ROOT,env,maxBuffer:2**22});
  console.log('qmech',v,'done');
}
const sets=['cand4-king','cand6-king','cand4-hunter2','cand6-hunter2','cand4-hunter','cand6-hunter'].map(s=>'exp/q2/'+s);
for(const tool of ['queenstat','queendeath']){
  const text=cp.execFileSync(process.execPath,['exp/q2/'+tool+'.js',...sets,'--nopocket'],{cwd:ROOT,env,maxBuffer:2**22});
  fs.writeFileSync(path.join(__dirname,'verify-'+tool+'.txt'),text);console.log(tool,'done');
}
