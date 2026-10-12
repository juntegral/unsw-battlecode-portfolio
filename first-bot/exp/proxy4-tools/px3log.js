#!/usr/bin/env node
'use strict';
// px3log.js — copies bots/proxy3_{swarm,king,elim} to <out>/px3log_<style> with one change: each dragon process writes a
// LOG line in the recog.js format when v3's map recognition settles ("px4 map <name> r<round>") or finds no table map
// ("px4 map none r<round>"). Behaviour is unchanged (LOG lines do not affect the game). Used to measure what v3
// believes on the b layouts (exp/proxy4-check-p3).
// usage (repository root): node exp/proxy4-tools/px3log.js <out dir>
//   then: node exp/proxy4-tools/recog.js run --label proxy4-check-p3 --pairs <out>/px3log_swarm:<out>/px3log_king --maps maps/variants --seeds 1 --jobs 1
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const out = process.argv[2]; if (!out) { console.error('usage: px3log.js <out dir>'); process.exit(2); }
const edits = [
  ['        ingest(rb);\n        Plan p = decide();', '        ingest(rb);\n        if (!dbgLog.empty()) { w.log(dbgLog); dbgLog.clear(); }\n        Plan p = decide();'],
  ['    int sdbCand[16]; int nSdb = 0; int sdbIdx = -1; int sdbChecks = 0;', '    int sdbCand[16]; int nSdb = 0; int sdbIdx = -1; int sdbChecks = 0; std::string dbgLog; bool dbgNone = false;'],
  ['        if (nSdb == 1 && sdbChecks >= 49) {\n            sdbIdx = sdbCand[0];', '        if (nSdb == 0 && !dbgNone) { dbgNone = true; dbgLog = "px4 map none r" + std::to_string(round); }\n        if (nSdb == 1 && sdbChecks >= 49) {\n            sdbIdx = sdbCand[0];\n            { std::string nm0 = spawndb::MAPS[sdbIdx].name; for (char& c : nm0) if (c == \' \') c = \'_\'; dbgLog = "px4 map " + nm0 + " r" + std::to_string(round); }'],
];
for (const s of ['swarm', 'king', 'elim']) {
  const src = path.join(ROOT, 'bots', 'proxy3_' + s), dst = path.resolve(out, 'px3log_' + s);
  fs.rmSync(dst, { recursive: true, force: true }); fs.mkdirSync(dst, { recursive: true });
  for (const f of fs.readdirSync(src)) fs.copyFileSync(path.join(src, f), path.join(dst, f));
  let c = fs.readFileSync(path.join(dst, 'pxcore.cpp'), 'utf8');
  for (const [a, b] of edits) { if (!c.includes(a)) throw new Error('pxcore.cpp changed: ' + a.slice(0, 50)); c = c.replace(a, b); }
  fs.writeFileSync(path.join(dst, 'pxcore.cpp'), c);
  console.log('wrote', dst);
}
