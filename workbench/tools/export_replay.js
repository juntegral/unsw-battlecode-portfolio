#!/usr/bin/env node
// Neutral online game exporter for lineage logs: raw replay events as JSONL, no interpretation.
// usage: node tools/export_replay.js <game-<id>.json> <M<id>.replay> <out.jsonl> [ourTeamId=583]
// line 1 = {"meta":...}; then one JSON object per replay event, in order, with the current round attached.
const fs=require('fs'),path=require('path');
const {load}=require(path.join(__dirname,'viewer.js'));
const [gameFile,replayFile,outFile,own='583']=process.argv.slice(2);
if(!gameFile||!replayFile||!outFile){console.error('usage: export_replay.js <game.json> <replay> <out.jsonl> [ourTeamId]');process.exit(2);}
const g=JSON.parse(fs.readFileSync(gameFile,'utf8'));
const tmp=fs.mkdtempSync(path.join(path.dirname(outFile),'.rp-'));fs.copyFileSync(replayFile,path.join(tmp,'x.replay'));
const R=load(tmp);fs.rmSync(tmp,{recursive:true});
const us=g.teamAId===+own?'A':'B';
const meta={gameId:g.id,map:g.mapId,ourSide:us,teamAId:g.teamAId,teamBId:g.teamBId,submissionAId:g.submissionAId,submissionBId:g.submissionBId,ranked:g.ranked,completedAt:g.completedAt,result:R.result,note:'events are raw replay-viewer events; roundStart marks each round'};
const out=[JSON.stringify({meta})];let round=-1;
for(const e of R.events){if(e.type==='roundStart')round=e.round;out.push(JSON.stringify({round,...e}));}
fs.writeFileSync(outFile,out.join('\n')+'\n');console.log(outFile,out.length-1,'events');
