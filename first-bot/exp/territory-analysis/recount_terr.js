// recount_terr.js — compares territory tile counts (neutral / A / B) of recount.js against extract.js for every game.
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), readline = require('readline');
const C = path.join(__dirname, 'cache');
async function each(f, fn) { const rl = readline.createInterface({ input: fs.createReadStream(f).pipe(zlib.createGunzip()), crlfDelay: Infinity }); for await (const l of rl) { if (!l.trim()) continue; fn(l); } }
(async () => {
  const main = new Map();
  for (const f of fs.readdirSync(C).filter(f => /^(top-all|online-.*)\.jsonl\.gz$/.test(f))) await each(path.join(C, f), l => { const k = /^\{"key":"([^"]+)"/.exec(l)[1]; const t = /"terrTiles":\[(\d+),(\d+),(\d+)\]/.exec(l); main.set(k, t ? [+t[1], +t[2], +t[3]] : null); });
  let n = 0, eq = 0, miss = 0; const bad = [];
  for (const f of fs.readdirSync(C).filter(f => /^recount-.*\.jsonl\.gz$/.test(f))) await each(path.join(C, f), l => { const r = JSON.parse(l); const m = main.get(r.key); n++; if (!m) { miss++; return; } if (m.join() === r.owner.join()) eq++; else if (bad.length < 5) bad.push([r.key, m, r.owner]); });
  console.log(JSON.stringify({ games: n, equal: eq, missing: miss, firstDiffs: bad }));
})();
