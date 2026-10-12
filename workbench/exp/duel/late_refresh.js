// One final inventory snapshot; add unprocessed games without rerunning early aggregates.
'use strict';
const fs=require('fs'),path=require('path'),cp=require('child_process'),os=require('os');
const {OUT,census,guard}=require('./setup');
async function main(){
 if(os.getPriority(0)<10)throw Error('nice >=10 required');guard();while(fs.existsSync(path.join(OUT,'early-tactical.active'))&&fs.readFileSync(path.join(OUT,'early-tactical.active'),'utf8')==='active'){guard();await new Promise(resolve=>setTimeout(resolve,15000));}
 while(fs.existsSync(path.join(OUT,'calibration.active'))&&fs.readFileSync(path.join(OUT,'calibration.active'),'utf8')==='active'){guard();await new Promise(resolve=>setTimeout(resolve,15000));}const P=census(),todo=P.tasks.filter(t=>!fs.existsSync(path.join(OUT,'cache',t.key+'.json.gz')));
 console.log('FINAL SNAPSHOT',JSON.stringify({at:P.frozenAt,N:P.N,strict:P.strictN,ours:P.oursN,under:P.underN,custom:P.customN,newN:todo.length}));
 let i=0,n=0,busy=0,stop=false;if(!todo.length)return;
 await new Promise((resolve,reject)=>{const ws=[];function next(w){if(stop)return;if(i===todo.length){if(!busy){stop=true;ws.forEach(w=>w.kill());resolve();}return;}try{if(n%10===0)guard();}catch(e){stop=true;ws.forEach(w=>w.kill());reject(e);return;}busy++;w.send(todo[i++]);}
 for(let k=0;k<Math.min(2,todo.length);k++){const w=cp.fork(path.join(OUT,'run.js'),['worker'],{execArgv:['--max-old-space-size=1400'],stdio:['ignore','ignore','inherit','ipc']});ws.push(w);w.on('message',m=>{busy--;n++;if(m.error){stop=true;ws.forEach(w=>w.kill());reject(Error(m.error));return;}if(n%25===0)console.log('LATE',n+'/'+todo.length);next(w);});w.on('error',reject);w.on('exit',(code,signal)=>{if(!stop){stop=true;ws.forEach(w=>w.kill());reject(Error('unexpected exit '+code+' '+signal));}});next(w);}});
 console.log('LATE COMPLETE',n);
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;});
