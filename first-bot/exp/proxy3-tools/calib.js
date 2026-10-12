#!/usr/bin/env node
'use strict';
// calib.js — per-map calibration table: our bot against local proxies next to our bot against the real top teams online.
// Reads side records written by tools/proxy_check.js (`online` for server sets, `measure` for tools/eval.js labels).
// No games, no network.
//
// usage (repository root):
//   node exp/proxy3-tools/calib.js --g "<name>=<src>[+<src>...]" [--g ...] [--ref <name>] [--metrics win,elim,...] [--json <file>]
//     <src> = online:<set>                 exp/proxy3-online/<set>/sides.jsonl (our team = side named "bot")
//           | local:<label>[@opp1,opp2]    exp/<label>/sides.jsonl, optionally only these opponents
//     --ref <name>: the group the others are compared with (default: the first group). The error line is the mean over maps
//       of |group - ref| for each metric (maps where both have games), and the count of maps within the tolerance.
//
// Per game (our side = record named "bot", their side = the other record of the same game key):
//   map        map key; Prisoners Dilemma split by starting dragons per team: pd6 (3) / pd10 (5)
//   win        our win share (draw 0.5)
//   elim       we were eliminated (our dragon count 0 at the end)
//   elimR      median end round of the games in which we were eliminated
//   reach      alive at r340 with >= 4 units (research/experiments/online-analysis-px8.md: the late conversion can start)
//   G          our longest at the end, 0 if eliminated (mean)
//   oU100      their units at r100 (median over games still running at r100)
//   oM300      their total length at r300 (median over games still running at r300)
//   oK500      their longest at r500 (median over games that reached r500)
//   uM300      our total length at r300 (median over games still running at r300)
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const PC = require(path.join(ROOT, 'tools', 'proxy_check.js'));

const MAPS = ['autarky', 'portals', 'schooltime', 'slithery_fight', 'trauma', 'default', 'devil', 'pd6', 'pd10', 'queen_of_spades', 'trophy'];
const R500 = new Set(['autarky', 'portals', 'schooltime', 'slithery_fight', 'trauma']);
const MAP_SHORT = { autarky: 'Autarky', portals: 'Portals', schooltime: 'Schooltime', slithery_fight: 'Slithery', trauma: 'Trauma', default: 'Default', devil: 'Devil', pd6: 'PD6', pd10: 'PD10', queen_of_spades: 'QoS', trophy: 'Trophy' };

const sum = a => a.reduce((x, y) => x + y, 0);
const mean = a => a.length ? sum(a) / a.length : null;
function med(a) { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y), m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; }
const inProg = (x, r) => x.rounds > r || (r === 500 && x.rounds === 500);

function games(spec) {
  const out = [];
  for (const src of spec.split('+')) {
    const [kind, rest] = src.split(/:(.*)/s);
    let file, opps = null;
    if (kind === 'online') file = path.join(ROOT, 'exp', 'proxy3-online', rest, 'sides.jsonl');
    else if (kind === 'local') { const [label, o] = rest.split('@'); file = path.join(ROOT, 'exp', label, 'sides.jsonl'); if (o) opps = new Set(o.split(',')); }
    else throw new Error('bad source ' + src);
    if (!fs.existsSync(file)) throw new Error('missing ' + file);
    const S = PC.readJsonl(file), byKey = new Map();
    for (const x of S) { if (!byKey.has(x.key)) byKey.set(x.key, []); byKey.get(x.key).push(x); }
    for (const [k, rs] of byKey) {
      const us = rs.find(x => x.name === 'bot'), them = rs.find(x => x.opp === 'bot');
      if (!us || !them) continue;
      if (opps && !opps.has(us.opp)) continue;
      let m = PC.mapKey(us.map);
      if (m.startsWith('prisoners_dilemma')) m = us.tl[0][0] >= 5 ? 'pd10' : 'pd6';
      out.push({ key: src + '|' + k, map: m, opp: us.opp, us, them });
    }
  }
  return out;
}

function stats(G) {
  const o = { n: G.length };
  if (!G.length) return o;
  o.win = mean(G.map(g => g.us.win));
  const el = G.filter(g => g.us.final[0] === 0);
  o.elim = el.length / G.length;
  o.elimR = med(el.map(g => g.us.rounds));
  o.reach = mean(G.map(g => (g.us.rounds > 340 && g.us.tl[34][0] >= 4) ? 1 : 0));
  o.G = mean(G.map(g => g.us.final[0] > 0 ? g.us.final[1] : 0));
  const at = (r, side, i) => { const y = G.filter(g => inProg(g[side], r)); return y.length ? med(y.map(g => g[side].tl[r / 10][i])) : null; };
  o.oU100 = at(100, 'them', 0); o.oM300 = at(300, 'them', 1); o.oK500 = at(500, 'them', 2); o.uM300 = at(300, 'us', 1);
  o.oK400 = at(400, 'them', 2); o.oK300 = at(300, 'them', 2); o.oU300 = at(300, 'them', 0); o.oU400 = at(400, 'them', 0);
  return o;
}

const FMT = {
  n: v => String(v), win: v => (100 * v).toFixed(0) + '%', elim: v => (100 * v).toFixed(0) + '%', elimR: v => v.toFixed(0), reach: v => (100 * v).toFixed(0) + '%',
  G: v => v.toFixed(1), oU100: v => v.toFixed(0), oK300: v => v.toFixed(0), oU300: v => v.toFixed(0), oU400: v => v.toFixed(0), oM300: v => v.toFixed(0), oK400: v => v.toFixed(0), oK500: v => v.toFixed(0), uM300: v => v.toFixed(0),
};
const TOL = { oK300: 3, oU300: 8, oU400: 6, win: 0.15, elim: 0.15, elimR: 40, reach: 0.15, G: 5, oU100: 8, oM300: 25, oK400: 6, oK500: 6, uM300: 20 };
const fmt = (k, v) => v === null || v === undefined || Number.isNaN(v) ? '–' : FMT[k](v);

function main() {
  const argv = process.argv.slice(2), groups = [];
  let ref = null, metrics = ['n', 'win', 'elim', 'elimR', 'reach', 'G', 'oU100', 'oM300', 'oK500'], json = null;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--g') { const s = argv[++i], j = s.indexOf('='); groups.push({ name: s.slice(0, j), spec: s.slice(j + 1) }); }
    else if (argv[i] === '--ref') ref = argv[++i];
    else if (argv[i] === '--metrics') metrics = argv[++i].split(',');
    else if (argv[i] === '--json') json = argv[++i];
  }
  if (!groups.length) { console.error('see the header for usage'); process.exit(2); }
  for (const g of groups) g.G = games(g.spec);
  const refG = groups.find(g => g.name === ref) || groups[0];
  const res = {};
  for (const g of groups) {
    res[g.name] = {};
    for (const m of MAPS) res[g.name][m] = stats(g.G.filter(x => x.map === m));
    res[g.name]['500-round'] = stats(g.G.filter(x => R500.has(x.map)));
    res[g.name].elimination = stats(g.G.filter(x => !R500.has(x.map)));
    res[g.name].all = stats(g.G);
  }
  const cols = [...MAPS, '500-round', 'elimination', 'all'];
  for (const k of metrics) {
    console.log(`\n### ${k}\n`);
    console.log('| group | ' + cols.map(c => MAP_SHORT[c] || c).join(' | ') + ' | mean abs diff vs ' + refG.name + ' | maps within ' + (TOL[k] !== undefined ? (k === 'win' || k === 'elim' || k === 'reach' ? (100 * TOL[k]) + '%p' : TOL[k]) : '-') + ' |');
    console.log('|---|' + cols.map(() => '---:').join('|') + '|---:|---:|');
    for (const g of groups) {
      const cells = cols.map(c => fmt(k, res[g.name][c][k]));
      let err = '', within = '';
      if (g !== refG && k !== 'n') {
        const d = []; let w = 0, n = 0;
        for (const m of MAPS) {
          const a = res[g.name][m][k], b = res[refG.name][m][k];
          if (a === null || a === undefined || b === null || b === undefined) continue;
          d.push(Math.abs(a - b)); n++; if (TOL[k] !== undefined && Math.abs(a - b) <= TOL[k]) w++;
        }
        const e = mean(d);
        err = e === null ? '–' : (k === 'win' || k === 'elim' || k === 'reach') ? (100 * e).toFixed(1) + '%p' : e.toFixed(1);
        within = `${w}/${n}`;
      }
      console.log(`| ${g.name} | ${cells.join(' | ')} | ${err} | ${within} |`);
    }
  }
  if (json) fs.writeFileSync(path.resolve(json), JSON.stringify(res, null, 1));
}
if (require.main === module) main();
module.exports = { games, stats, MAPS, R500 };
