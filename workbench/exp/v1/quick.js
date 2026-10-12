// quick look at one local replay: our team (the side whose indicators carry " E="), units over time, tag counts, result
const { makeLoader, viewerSource } = require('../../tools/top_features.js');
const load = makeLoader(viewerSource());
const R = load(process.argv[2]);
const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
let us = process.argv[3] || null;
const alive = { A: new Set(), B: new Set() };
for (const d of R.match.map.initialDragons) alive[d.team].add(d.id);
const units = { A: {}, B: {} }; let round = -1;
const tags = {}; const labs = [];
for (const e of R.events) {
  if (e.type === 'roundStart') { round = e.round; if (round % 50 === 0) for (const t of ['A', 'B']) units[t][round] = alive[t].size; }
  else if (e.type === 'dragonSplit') { team.set(e.childId, e.team); alive[e.team].add(e.childId); }
  else if (e.type === 'dragonDeath') { const t = team.get(e.id); if (t) alive[t].delete(e.id); }
  else if (e.type === 'dragonIndicator') {
    const t = team.get(e.id); const s = e.text || '';
    if (!us && / E=[FS]$/.test(s)) us = t;
    if (t !== us) continue;
    for (const k of ['sx', 'sr', 'sxx', 'sxc', 'srx', 'src', 'srn', 'sq', 'sc', 'scx', 'sk', 'conv', 'feed', 'grab', 'cl', 'tg', 'tgx', 'lntv', 'E=S', 'E=F', 'escape-split', 'no-exit', 'pocket-eat', 'csplit', 'lsplit', 'frag', 'kcap', 'floor', 'bsp']) {
      const re = new RegExp('(^|\\s)' + k.replace('-', '\\-') + '(\\d|\\s|$)');
      if (re.test(s)) tags[k] = (tags[k] || 0) + 1;
    }
    if (/ sd\d+@/.test(s)) tags.sd = (tags.sd || 0) + 1;
    if (/ sd\d+@\S+o/.test(s)) tags.sdo = (tags.sdo || 0) + 1;
    if (/sf#/.test(s)) tags.sf = (tags.sf || 0) + 1;
    if (process.argv[4] && new RegExp(process.argv[4]).test(s) && labs.length < 12) labs.push(round + ' #' + e.id + ' ' + s);
  }
}
console.log('us', us, 'result', JSON.stringify(R.result));
console.log('units A', JSON.stringify(units.A)); console.log('units B', JSON.stringify(units.B));
console.log('tags', JSON.stringify(tags));
for (const l of labs) console.log(l);
