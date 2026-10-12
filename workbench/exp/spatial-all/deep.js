// Selected deep reads only after the population classes have been written.
'use strict';
const fs=require('fs'),path=require('path'),S=require('./lib'),O=path.join(__dirname,'cache');
const P=JSON.parse(fs.readFileSync(path.join(O,'population.json'),'utf8')),C=JSON.parse(fs.readFileSync(path.join(O,'classes.json'),'utf8')),out=[];
for(const pick of C.selected){const task=P.tasks.find(t=>t.key===pick.key);if(!task)throw Error('Missing task '+pick.key);const R=S.raw.load(task.file),row=S.analyse(R,task,true);out.push({pick,rounds:row.rounds,result:row.result,us:row.us,A:{cp:row.A.cp,nat:row.A.nat,hrMid:row.A.hrMid,sd:row.A.sd,targets:row.A.targets},B:{cp:row.B.cp,nat:row.B.nat,hrMid:row.B.hrMid,sd:row.B.sd,targets:row.B.targets},timeline:row.deepRows});}
fs.writeFileSync(path.join(O,'deep-reads.json'),JSON.stringify(out,null,2));console.log('deep reads',out.length);
