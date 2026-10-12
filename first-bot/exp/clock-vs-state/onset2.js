// Within games that reach r500 where both sides sacrifice >= 10 length after r200: does the winner start earlier or later?
// And: per-bin sacrifice rate curve (winners vs losers) to see whether the rise is a step (clock) or gradual.
const fs = require('fs'), path = require('path'), readline = require('readline');
const H = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { FL } = require(path.join(H, 'tools/mass_ledger.js'));
const SAC = FL.indexOf('dl_sac');
(async () => {
  const diffs = [], byMap = {}; const curveW = new Array(50).fill(0), curveL = new Array(50).fill(0); let nW = 0, nL = 0;
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(H, '.cache/mass-ledger/top-sample.jsonl')) });
  for await (const line of rl) {
    const g = JSON.parse(line);
    if (g.rounds < 500 || !g.winner) continue;
    const on = {};
    for (const side of ['A', 'B']) {
      const sac = g[side].fl[SAC], S = sac.slice(20, 50).reduce((s, v) => s + v, 0);
      const w = g.winner === side; for (let b = 0; b < 50; b++) (w ? curveW : curveL)[b] += sac[b]; if (w) nW++; else nL++;
      if (S < 10) continue; let cum = 0; for (let b = 20; b < 50; b++) { cum += sac[b]; if (cum >= 0.5 * S) { on[side] = b * 10; break; } }
    }
    if (on.A === undefined || on.B === undefined) continue;
    const w = g.winner, l = w === 'A' ? 'B' : 'A'; const d = on[w] - on[l]; diffs.push(d); (byMap[g.map] = byMap[g.map] || []).push(d);
  }
  const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
  console.log(`games with both sides sacrificing: ${diffs.length}; winner onset50 - loser onset50: mean ${mean(diffs).toFixed(1)} rounds; winner earlier ${(100 * diffs.filter(d => d < 0).length / diffs.length).toFixed(0)}%, same ${(100 * diffs.filter(d => d === 0).length / diffs.length).toFixed(0)}%, later ${(100 * diffs.filter(d => d > 0).length / diffs.length).toFixed(0)}%`);
  for (const [m, a] of Object.entries(byMap).sort()) if (a.length >= 30) console.log(`  ${m.padEnd(18)} n ${String(a.length).padStart(4)} mean ${mean(a).toFixed(1)}  earlier ${(100 * a.filter(d => d < 0).length / a.length).toFixed(0)}%`);
  console.log('\nsacrificed length per team-game per 10-round bin (r200..r490): winners | losers');
  for (let b = 20; b < 50; b++) console.log(`  r${b * 10}  ${(curveW[b] / nW).toFixed(1).padStart(5)} | ${(curveL[b] / nL).toFixed(1).padStart(5)}`);
})();
