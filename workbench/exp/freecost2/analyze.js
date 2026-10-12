#!/usr/bin/env node
'use strict';
process.env.UNSW_RULES = '123';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '../..');
const {makeLoader, viewerSource} = require('../../tools/top_features');
const {perGame} = require('../../tools/mass_ledger');
const load = makeLoader(viewerSource());
const causes = ['sac','trap','rammed','ram','enemyBody','allyHead','fault','sprintDeath'];
const equal = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const band = l => l <= 4 ? 'L2-4' : l <= 8 ? 'L5-8' : l <= 12 ? 'L9-12' : 'L13+';
function hashReplay(R) {
  const hash = crypto.createHash('sha256'), skip = new Set(['dragonIndicator','dragonLog','debugDraw','engineLog']);
  for (const e of R.events) {
    if (skip.has(e.type)) continue;
    const o = {}; for (const [k,v] of Object.entries(e)) if (k !== 'instructions') o[k] = typeof v === 'bigint' ? String(v) : v;
    hash.update(JSON.stringify(o));
  }
  return hash.digest('hex');
}
function bodyHash(body) { let h = 2166136261; for (const t of body) h = Math.imul(h ^ t,16777619) >>> 0; return h; }
function audit(R, row) {
  const queen = Math.min(...R.match.map.initialDragons.filter(d => d.team === row.side).map(d => d.id));
  if (!Number.isFinite(queen)) throw Error('missing queen');
  const out = {queen, hash:hashReplay(R), turns:0, turnsL5:0, freeMulti:0, completedFreeMulti:0, multi:0, completedMulti:0,
    bands:{}, raw:{}, causes:{}, deaths:[], queenDeath:null, oversprint:0, tle:0, missingAction:0, actions:0,
    bodyxTags:0, missingBodyxTags:0, startHashDrift:[], endHashDrift:[], unknownInput:0, unseenPath:0, depth:{}, samples:[]};
  const indicators = new Map(), actions = new Map();
  const ledger = perGame(R,{map:row.map, rules:'123'},{
    indicator(e) { indicators.set(e.id,e.text || ''); },
    turn(d) {
      if (d.team !== row.side) return;
      indicators.delete(d.id);
      out.turns++; if (d.body.length >= 5) out.turnsL5++;
      const b = band(d.body.length); out.bands[b] ||= {turns:0, freeMulti:0, completedFreeMulti:0}; out.bands[b].turns++;
    },
    action(d,e,round,c,before) {
      if (d.team !== row.side) return;
      out.actions++; if (e.tle) out.tle++; if (!e.action) out.missingAction++;
      const length = before.length, steps = e.action?.kind === 'move' ? e.action.steps.length : 0;
      const free = Math.ceil(length/4), paid = Math.max(0,steps-free), ind = indicators.get(d.id) || '';
      const rec = {round,id:d.id,length,steps,free,paid,action:e.action,indicator:ind,fate:d.fate || null}; actions.set(d.id,rec);
      const dep = /\bd(\d+)\b/.exec(ind); if (dep) out.depth[`${round}:${d.id}`] = +dep[1];
      if (steps <= 1) return;
      out.multi++; if (!d.fate) out.completedMulti++;
      if (steps <= free) {
        out.freeMulti++; out.bands[band(length)].freeMulti++;
        if (!d.fate) {out.completedFreeMulti++; out.bands[band(length)].completedFreeMulti++;}
        if (out.samples.length < 12) out.samples.push(rec);
      }
      if (d.fate?.why === 'sprint') out.oversprint++;
      const tag = /\bbodyx(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)/.exec(ind);
      if (!tag) {out.missingBodyxTags++; return;}
      out.bodyxTags++; const v = tag.slice(1).map(Number);
      if (v[3]) out.unknownInput++; if (v[6]) out.unseenPath++;
      if (v[4] !== bodyHash(before.map(t=>c.key(t.x,t.y)))) out.startHashDrift.push({round,id:d.id,reported:v[4],completed:!d.fate});
      if (!d.fate && (v[0]!==free || v[1]!==paid || v[2]!==d.body.length || v[5]!==bodyHash(d.body.map(t=>c.key(t.x,t.y)))))
        out.endHashDrift.push({round,id:d.id,reported:v,actualLength:d.body.length,actualHash:bodyHash(d.body.map(t=>c.key(t.x,t.y)))});
    },
    death(d,rec,idx,other,round) {
      if (d.team !== row.side) return;
      const a = actions.get(d.id), death = {round,id:d.id,cause:causes[rec.cause],fate:d.fate || null,
        length:d.body.length,head:d.body[0],action:a?.round === round ? a.action : null,indicator:indicators.get(d.id) || ''};
      out.deaths.push(death); if (d.id === queen) out.queenDeath = death;
    }
  });
  const raw = new Map(R.events.filter(e=>e.type==='dragonDeath').map(e=>[e.id,e.reason]));
  for (const d of out.deaths) {d.reason=raw.get(d.id); out.raw[d.reason]=(out.raw[d.reason] || 0)+1; out.causes[d.cause]=(out.causes[d.cause] || 0)+1;}
  out.checks = ledger.chk; out.turnActionGap = out.turns-out.actions;
  out.lastRound = R.events.reduce((m,e)=>e.type==='roundStart' ? Math.max(m,e.round) : m,-1);
  out.queenLifetime = out.queenDeath ? out.queenDeath.round : out.lastRound+1;
  out.queenCensored = !out.queenDeath;
  out.rate = out.turnsL5 ? out.freeMulti/out.turnsL5 : null;
  const line = (row.cpu || []).find(l=>l.startsWith('team '+row.side+' points per turn:'));
  const max = line && /max\s+([\d.]+)M/.exec(line); out.cpuMaxM = max ? +max[1] : null;
  return out;
}
function main() {
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname,'spec.json')));
  const report = {expectedGames:0,sets:{},missing:[],historyErrors:[],duplicates:[],unexpected:[],errors:[],pairs:[],identity:[]};
  for (const dir of new Set(spec.map(s=>s.out))) {
    const name = path.basename(dir), rows = new Map(), expected = new Map(); report.sets[name] = {};
    const file = path.join(ROOT,dir,'rows.jsonl');
    if (fs.existsSync(file)) for (const [i,l] of fs.readFileSync(file,'utf8').split('\n').entries()) {
      if (!l.trim()) continue; let r;
      try {r=JSON.parse(l);} catch(e) {report.historyErrors.push({set:name,line:i+1,error:String(e)}); continue;}
      if (r.G !== undefined && r.exit === 0 && !r.error && !r.botProblem) {
        if (rows.has(r.key)) report.duplicates.push({set:name,key:r.key}); rows.set(r.key,r);
      } else report.historyErrors.push({set:name,line:i+1,row:r});
    }
    for (const s of spec.filter(s=>s.out===dir)) for (const opp of s.opps) for (const map of s.only) for (const side of s.sides) for (const seed of s.seeds)
      expected.set([path.basename(opp),map,side,seed].join(':'),{opp:path.basename(opp),map,side,seed});
    report.expectedGames += expected.size;
    for (const key of rows.keys()) if (!expected.has(key)) report.unexpected.push({set:name,key});
    for (const [key,meta] of expected) {
      const row = rows.get(key), stem = path.join(ROOT,dir,'games',key.replace(/:/g,'_'),'game.replay');
      const replay = fs.existsSync(stem) ? stem : stem+'.gz';
      if (!row || !fs.existsSync(replay)) {report.missing.push({set:name,key}); continue;}
      try {
        if (!equal(meta,{opp:row.opp,map:row.map,side:row.side,seed:row.seed})) throw Error('metadata mismatch');
        report.sets[name][key]=audit(load(replay),row);
      } catch(e) {report.errors.push({set:name,key,error:String(e.stack || e)});}
    }
  }
  for (const key of new Set([...Object.keys(report.sets.on),...Object.keys(report.sets.off)])) {
    const a=report.sets.on[key],b=report.sets.off[key]; if (!a || !b) continue;
    const delta=a.queenLifetime-b.queenLifetime;
    report.pairs.push({key,rateOn:a.rate,rateOff:b.rate,freeMultiDelta:a.freeMulti-b.freeMulti,
      queenLifetimeOn:a.queenLifetime,queenLifetimeOff:b.queenLifetime,queenCensoredOn:a.queenCensored,queenCensoredOff:b.queenCensored,
      queenDirection:delta>0?'longer':delta<0?'shorter':'same',queenDelta:delta,rawOn:a.raw,rawOff:b.raw,causesOn:a.causes,causesOff:b.causes});
  }
  for (const key of Object.keys(report.sets['id-off'])) {
    const a=report.sets['id-off'][key],b=report.sets['id-base'][key];
    report.identity.push({key,same:!!b && a.hash === b.hash});
  }
  fs.writeFileSync(path.join(__dirname,'analysis.json'),JSON.stringify(report,null,2)+'\n');
  const header=['key','freeMultiOn','turnsL5On','rateOn','freeMultiOff','turnsL5Off','rateOff','queenLifetimeOn','queenLifetimeOff','queenDirection','queenDelta','queenCensoredOn','queenCensoredOff','S_on','S_off','W_on','W_off','O_on','O_off','H_on','H_off','A_on','A_off'];
  const lines=report.pairs.map(p=>[p.key,report.sets.on[p.key].freeMulti,report.sets.on[p.key].turnsL5,p.rateOn,report.sets.off[p.key].freeMulti,report.sets.off[p.key].turnsL5,p.rateOff,
    p.queenLifetimeOn,p.queenLifetimeOff,p.queenDirection,p.queenDelta,p.queenCensoredOn,p.queenCensoredOff,...['S','W','O','H','A'].flatMap(r=>[p.rawOn[r]||0,p.rawOff[r]||0])].join('\t'));
  fs.writeFileSync(path.join(__dirname,'keywise.tsv'),header.join('\t')+'\n'+lines.join('\n')+'\n');
  console.log(JSON.stringify({expectedGames:report.expectedGames,pairs:report.pairs.length,identity:report.identity.length,missing:report.missing.length,historyErrors:report.historyErrors.length,errors:report.errors.length},null,2));
  if (report.missing.length || report.errors.length || report.unexpected.length) process.exitCode=1;
}
if (require.main === module) main();
module.exports = {audit,hashReplay};
