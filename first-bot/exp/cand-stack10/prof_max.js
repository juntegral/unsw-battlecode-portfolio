#!/usr/bin/env node
// Max decide() points per turn from a PROFILE build's labels (" | enemy .. field .. cand .. dfs .. rest .. total <T>M nodes <n>").
// usage: node exp/cand-stack10/prof_max.js <dir with <map>/game.replay> [...]
'use strict';
const fs = require('fs'), path = require('path');
const { load } = require(path.resolve(__dirname, '..', '..', 'tools', 'replay.js'));
for (const dir of process.argv.slice(2)) for (const m of fs.readdirSync(dir).sort()) {
  const f = path.join(dir, m, 'game.replay'); if (!fs.existsSync(f)) continue;
  const R = load(f); let mx = 0, mxField = 0, mxCand = 0, n = 0, over80 = 0;
  for (const e of R.events) {
    if (e.type !== 'dragonIndicator' || !e.text) continue;
    const g = / total ([\d.]+)M/.exec(e.text); if (!g) continue;
    const t = +g[1]; n++; if (t > mx) mx = t; if (t > 80) over80++;
    const fd = / field ([\d.]+)M/.exec(e.text), cd = / cand ([\d.]+)M/.exec(e.text);
    if (fd && +fd[1] > mxField) mxField = +fd[1]; if (cd && +cd[1] > mxCand) mxCand = +cd[1];
  }
  console.log(`${path.basename(dir)} ${m}: max total ${mx.toFixed(1)}M (field ${mxField.toFixed(1)}M, cand ${mxCand.toFixed(1)}M) over ${n} labelled turns, >80M ${over80}`);
}
