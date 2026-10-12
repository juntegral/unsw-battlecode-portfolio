'use strict';
process.env.UNSW_RULES = '123';
const fs = require('fs');
const {load} = require('../../tools/replay');
const {perGame} = require('../../tools/mass_ledger');
const first = JSON.parse(fs.readFileSync('exp/freecost2/firstdiv.json'));
const output = [];
const onlyKey = process.argv[2];
for (const row of first.rows.filter(r => r.status === 'matched' && (!onlyKey || r.key===onlyKey))) {
  for (const arm of ['on', 'off']) {
    const replay = load(row.files[arm]), selected = new Set(row.changed.map(c => `${row.R}:${c.id}`));
    if (row.key === 'bot-hunter:Colosseum:A:1') for (let r = 43; r <= 45; r++) for (const id of [0, 6]) selected.add(`${r}:${id}`);
    if (onlyKey && row.key === 'bot-hunter:Colosseum:A:1') selected.add(`${arm==='on'?17:18}:2`);
    const snapshots = new Map(), indicators = new Map();
    perGame(replay, {rules:'123'}, {
      indicator(e) {indicators.set(e.id, e.text);},
      turn(d, round, c) {
        if (!selected.has(`${round}:${d.id}`)) return;
        const graph = Array.from({length:c.W*c.H}, (_, t) => [...'NESW'].map(dir => {const p=c.across(t%c.W,Math.floor(t/c.W),dir);return p ? c.key(p.x,p.y) : -1;}));
        const s = {key:row.key, arm, round, id:d.id, W:c.W, H:c.H, body:d.body.map(p=>c.key(p.x,p.y)), pearls:[...c.pearls.keys()], occupancy:[...c.occ], graph};
        snapshots.set(d.id,s);
      },
      action(d,e,round,c) {
        const s=snapshots.get(d.id);
        if (!s || s.round!==round) return;
        s.action=e.action; s.indicator=indicators.get(d.id); s.fate=d.fate; s.after=d.body.map(p=>c.key(p.x,p.y));
        s.free=Math.ceil(s.body.length/4);
        const simulate = choice => {
          let body=[...s.body];const pearls=new Set(s.pearls),occ=new Map(s.occupancy),steps=[];
          for (let i=0;i<choice.length;i++) {
            const dir=choice[i], head=body[0], next=s.graph[head]['NESW'.indexOf(dir)], paid=i>=s.free;
            let fate=paid&&body.length<=2?'A':next<0?'W':body.includes(next)?'S':occ.has(next)&&occ.get(next)!==s.id?'O/H':null;
            if (fate) return {survived:false,steps,fate,step:i,next,hit:occ.get(next)};
            const before=[...body],pearl=pearls.has(next),normalRemoved=pearl?[]:[body[body.length-1]];
            body.unshift(next);if(!pearl)body.pop();pearls.delete(next);
            const paidRemoved=paid?[body.pop()]:[];
            steps.push({dir,headBefore:head,headAfter:next,pearl,paid,normalRemoved,paidRemoved,before,after:[...body]});
          }
          return {survived:true,steps,body};
        };
        if (s.action?.kind==='move') {
          s.oracle=simulate(s.action.steps.join(''));
          s.oracleMatchesActual=JSON.stringify(s.oracle.body||s.oracle.steps.at(-1)?.after||s.body)===JSON.stringify(s.after)&&s.oracle.survived===!s.fate;
        }
        if (round===row.R && d.id===row.id) {
          const changed=row.changed[0];s.newOracle=simulate(changed.on.text);s.oldOracle=simulate(changed.off.text);
        }
        if(row.key==='bot-hunter:Colosseum:A:1'&&arm==='on'&&round===44&&d.id===0) s.alternativeS=simulate('S');
        delete s.graph;delete s.occupancy;
        output.push(s);
      }
    });
  }
}
fs.writeFileSync(`exp/freecost2/${onlyKey?'supplemental-details':'decision-details'}.json`,JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({decisions:output.length,oracleMismatch:output.filter(s=>s.oracleMatchesActual===false),instantNewOnlyDeath:output.filter(s=>s.newOracle&&!s.newOracle.survived&&s.oldOracle.survived)},null,2));
