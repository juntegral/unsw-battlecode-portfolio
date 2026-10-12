'use strict';
const fs=require('fs'),path=require('path'),OUT=__dirname;
const read=name=>JSON.parse(fs.readFileSync(path.join(OUT,name+'.json')));
const T=read('tables'),V=read('verification'),F=read('fountain-verification'),B=read('blocking-verification');
if(!V.complete||V.mismatches||F.mismatches||B.mismatches)throw Error('Unresolved audit');
T.verification={all:{file:'verification.json',N:V.N,expected:V.expected,mismatches:V.mismatches,checks:V.checks},fountainComponents:{file:'fountain-verification.json',N:F.N,mismatches:F.mismatches},ownFountainBodyOccupation:{file:'blocking-verification.json',N:B.N,expected:B.expected,mismatches:B.mismatches},independence:'Same raw decoder and frozen layout assignment; separate body movement/drop simulation and independently reconstructed 2-core. Family labels and intent are not independently inferred.'};
T.supplementary={bodyOccupation:read('blocking'),deepSelection:read('deep-selection'),boards:'boards.json',recount:'recount.jsonl'};
fs.writeFileSync(path.join(OUT,'tables.json'),JSON.stringify(T,null,2));
console.log('Attached completed audits and supplemental measures');
