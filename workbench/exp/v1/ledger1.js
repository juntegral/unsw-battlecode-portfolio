// one replay through the mass ledger (tools/mass_ledger.js perGame): our team's units, longest, total per 50 rounds, natural intake, deaths
const ML = require('../../tools/mass_ledger.js');
const { makeLoader, viewerSource } = require('../../tools/top_features.js');
const load = makeLoader(viewerSource());
const [file, us, mapName] = process.argv.slice(2);
const R = load(file);
const g = ML.perGame(R, { map: mapName });
for (const side of ['A', 'B']) {
  const T = g[side]; const st = T.st;
  const pick = a => [0, 5, 10, 15, 20, 25, 30, 35, 38, 40, 45, 50].map(i => a[i]).join(' ');
  const nat = ['nat_own', 'nat_enemy', 'nat_neutral'].reduce((s, k) => s + T.fl[ML.FI[k]].reduce((a, b) => a + b, 0), 0);
  console.log(side === us ? 'US  ' : 'OPP ', side, 'units', pick(st.units), '| king', pick(st.king), '| total', pick(st.total), '| nat', nat);
}
