'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process'), assert = require('assert');
const TASK = __dirname, ROOT = path.resolve(TASK, '../..'), CENSUS = path.join(ROOT, 'exp/queen-rammed');
const {geometry, state, neighbours} = require(path.join(CENSUS, 'geometry.js'));
const tables = JSON.parse(fs.readFileSync(path.join(CENSUS, 'tables.json')));
const fixtures = [], cases = tables.mainDeaths.filter(d => d.cause === 'sac' && d.reason === 'S');
assert.equal(cases.length, 10);
for (const d of cases) {
  const raw = JSON.parse(fs.readFileSync(path.join(CENSUS, d.raw))), G = geometry(raw.map);
  const S = state(raw.game.death.lastQueenTurn, G), q = S.drag.get(d.queenId), tiles = [];
  let t = q.body[0]; for (const dir of d.queenAction.action.steps) { t = G.edges[t][dir]; tiles.push(t === null ? -1 : t); }
  const f = {id: d.id, L: q.body.length, N: G.N, body: q.body, tiles,
    eats: tiles.map(t => +S.pearls.has(t)), blocked: [...S.occ].filter(([, id]) => id !== q.id).map(([t]) => t), target: -1,
    actual: d.queenAction.endBody.map(G.key), old: d.mechanismChecks.rules110SameInput.body, map: d.map, side: d.side, round: d.round};
  fixtures.push(f);
  for (const n of neighbours(S, q, G).filter(n => n.kind === 'free'))
    fixtures.push({...f, id: d.id + '-' + n.dir, tiles: [n.tile], eats: [+S.pearls.has(n.tile)], actual: null, old: null});
}
const censusCount = fixtures.length;
for (let L = 2; L <= 64; L++) for (let steps = 1; steps <= 20; steps++) for (let pattern = 0; pattern < 3; pattern++) {
  const tiles = Array.from({length: steps}, (_, i) => i);
  fixtures.push({id: `straight-${L}-${steps}-${pattern}`, L, N: 2048,
    body: Array.from({length: L}, (_, i) => 1000 + i), tiles,
    eats: tiles.map((_, i) => +(pattern === 1 && i === 0 || pattern === 2 && i % 2 === 0)), blocked: [], target: -1});
}
for (let L = 2; L <= 16; L++) for (let cycle = 3; cycle <= 8; cycle++) for (let food = 0; food <= 1; food++) {
  const tiles = Array.from({length: 20}, (_, i) => i % cycle);
  fixtures.push({id: `cycle-${L}-${cycle}-${food}`, L, N: 2048,
    body: Array.from({length: L}, (_, i) => 1000 + i), tiles,
    eats: tiles.map(t => +(food && t === 0)), blocked: [], target: -1});
}
fixtures.push({id:'tail-blocked-before-advance',L:4,N:20,body:[3,2,1,0],tiles:[0],eats:[0],blocked:[],target:-1});
fixtures.push({id:'external-body',L:6,N:20,body:[6,5,4,3,2,1],tiles:[7,8],eats:[0,0],blocked:[8],target:-1});
fixtures.push({id:'terminal-trade',L:6,N:20,body:[6,5,4,3,2,1],tiles:[7,8],eats:[0,0],blocked:[8],target:8});
function request(f) { return [f.L, f.tiles.length, f.N, ...f.body, ...f.tiles, ...f.eats, f.blocked.length, ...f.blocked, f.target].join(' '); }
function oracle(f, on) {
  let body = [...f.body], removed = 0, pearls = 0, reason = '-', failed = -1, legal = true;
  const gratis = on ? Math.ceil(f.L / 4) : 1, states = [], consumed = new Set();
  for (let i = 0; i < f.tiles.length; i++) {
    const t = f.tiles[i];
    if (i >= gratis && body.length <= 2) reason = 'A';
    else if (t < 0) reason = 'W';
    else if (body.includes(t)) reason = 'S';
    if (reason !== '-') { failed = i; legal = false; break; }
    if (f.blocked.includes(t) && !(t === f.target && i + 1 === f.tiles.length)) legal = false;
    const eat = !!f.eats[i] && !consumed.has(t); consumed.add(t);
    body.unshift(t); if (eat) pearls++; else { body.pop(); removed++; }
    if (i >= gratis) { body.pop(); removed++; }
    states.push([...body]);
  }
  return {body, removed, pearls, reason, failed, states, legal};
}
const results = {};
for (const variant of ['on', 'off']) {
  const r = cp.spawnSync(path.join(TASK, 'fixtures-' + variant), [], {input: fixtures.map(request).join('\n')+'\n', encoding:'utf8', maxBuffer: 128 * 1024 ** 2});
  assert.equal(r.status, 0, r.stderr);
  const lines = r.stdout.trim().split('\n').map(JSON.parse); assert.equal(lines.length, fixtures.length);
  for (let i = 0; i < fixtures.length; i++) {
    const f = fixtures[i], got = lines[i], want = oracle(f, variant === 'on');
    for (const k of ['body', 'removed', 'pearls', 'reason', 'failed', 'states']) assert.deepStrictEqual(got[k], want[k], `${variant} ${f.id} ${k}`);
    assert(Math.abs(got.cost - (f.tiles.length - 1) * 1.6) < 1e-8, `${variant} price ${f.id}`);
    if (variant === 'on') assert.equal(got.legal, want.legal, f.id);
    if (f.actual) {
      assert.equal(got.legal, variant === 'off', f.id);
      if (variant === 'on') { assert.equal(got.failed, 2); assert.equal(got.reason, 'S'); assert.deepStrictEqual(got.body, f.actual); }
      else { assert.equal(got.reason, '-'); assert.deepStrictEqual(got.body, f.old); }
    }
  }
  results[variant] = lines;
}
const census = cases.map(d => {
  const i = fixtures.findIndex(f => f.id === d.id), alternatives = fixtures.slice(0, censusCount).map((f,i) => ({f,i})).filter(x => x.f.id.startsWith(d.id+'-') && results.on[x.i].legal);
  assert(alternatives.length, d.id + ' needs a safe first step');
  return {id: d.id, map:d.map, side:d.side, round:d.round, command:d.queenAction.action.steps.join(''), on:results.on[i], off:results.off[i], safeSingles:alternatives.map(x=>x.f.id.slice(d.id.length+1))};
});
fs.writeFileSync(path.join(TASK, 'census-fixtures.json'), JSON.stringify(fixtures.slice(0,censusCount),null,2)+'\n');
const report = {cases:fixtures.length, censusCommands:cases.length, rejectedOn:census.length, acceptedOff:census.length,
  drift:0, priceChanges:0, scope:'actual Planner bodyXCandidate/tileEnterable/paidSteps and transition; full-state fixtures, no games or choose replay', census};
fs.writeFileSync(path.join(TASK, 'fixture-check.json'), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,census:undefined}));
