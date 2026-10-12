#!/usr/bin/env node
// Stage 2 (classes with sizes) and stage 3 selection for close reading, from the extract.js cache (no replays read).
// usage (repository root): node exp/supply-chain/cases.js [--top top-all] [--per 2] [--out exp/supply-chain/cases.md]
// Selection rule (fixed before reading any replay): inside each class, the cases with the smallest FNV-1a hash of
// "<game key>#<dragon id>" (or of the game key for game classes), --per of them (default 2) per map kind (r500 / elim).
// Classes (pieces = children born with length <= 3; fields as in extract.js):
//   A1 stack5/stack6 csplit child, born r0-249, no natural pearl within 30 rounds, nearest own head at birth <= 2, no spawn claimed
//   A2 stack5/stack6 csplit child, born r0-249, no natural pearl within 30 rounds, nearest own head at birth >= 3, no spawn claimed
//   A3 stack5/stack6 csplit child, born r0-249, no natural pearl within 30 rounds, >= 1 spawn claimed within 30 rounds
//   A4 TW piece born r0-249 with nearest own head at birth <= 2 that ate a natural pearl within 30 rounds (the elite contrast)
//   B1 TW piece that ended by sacrifice with its drops >= half eaten by own dragons >= 8, that had been >= 9 from every own
//      head >= 8 (or had none) and was within 3 of one at its last turn (forage and return)
//   B2 stack5/stack6 piece ended by sacrifice (conv) — same fields, any trajectory
//   C1 TW piece trapped (end trap) with its drops >= half eaten by own pieces (<= 4): the recycling link
//   L1 TW piece born r250-449 from a length-4 parent (2+2) that ended by sacrifice with >= half its drops eaten by own >= 8 (late pool)
//   A5 stack5/stack6 bsp child (Schooltime b early split), any outcome
//   D1 stack5 team-games on 500-round maps: the one with the median cs episodes r250-449 (game film for both sides)
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'supply-chain');
const { SETGROUP, R500 } = require('./aggregate.js');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const PER = +opt('per', 2);
function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const CLASSES = ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'C1', 'L1'];
const size = {}, pick = {};
const keep = (cls, kind, h, rec) => {
  const k = cls + '|' + kind; size[k] = (size[k] || 0) + 1;
  const a = pick[k] || (pick[k] = []);
  if (a.length < PER || h < a[a.length - 1].h) { a.push({ h, rec }); a.sort((x, y) => x.h - y.h); if (a.length > PER) a.pop(); }
};
const d1 = [];
function onGame(g) {
  const top = g.src === 'top', kind = R500.has(g.map) ? 'r500' : 'elim';
  let sideGroup = {};
  if (top) {
    const inactive = s => g[s].splits <= 3 && g[s].sonar === 0;
    if (inactive('A') || inactive('B') || g.A.faults >= 3 || g.B.faults >= 3 || !g.winner) return;
    sideGroup[g.winner] = 'TW';
  } else {
    const bot = SETGROUP[g.set]; if (!bot) return;
    sideGroup[g.us] = bot; sideGroup[g.us === 'A' ? 'B' : 'A'] = 'X';
  }
  for (const p of g.P) {
    const side = p[0] === 0 ? 'A' : 'B', grp = sideGroup[side]; if (!grp) continue;
    const [ti, born, bl, pl, cls, pk, bt, bv, bdBig, bnnd, bn5, life, end, Lf, maxL, steps, nat, natOwn, natEnemy, dOwn, dEnemy, spr, splitsN, C,
      turns, tOwn, tEnemy, n30, alive30, drops, eOwn, eOwnBig, eEnemy, dBigLast, dBigMax, dBig10, claim30, claimEat30, csT, fsT, eOwnP, eLonger, id] = p;
    const rec = { key: g.key, map: g.map, side, grp, id, born, bl, pl, bt, bv, bdBig, bnnd, bn5, life, end, Lf, nat, n30, claim30, claimEat30, drops, eOwn, eOwnBig, eOwnP, eEnemy, dBigMax, dBig10, dBigLast, steps, tOwn, tEnemy, turns };
    const h = hash32(g.key + '#' + id);
    if ((grp === 'stack5' || grp === 'stack6') && cls === 1 && born < 250 && n30 === 0) {
      if (claim30 === 0 && bnnd <= 2) keep('A1', kind, h, rec);
      else if (claim30 === 0 && bnnd >= 3) keep('A2', kind, h, rec);
      else if (claim30 >= 1) keep('A3', kind, h, rec);
    }
    if (grp === 'TW' && born < 250 && bnnd <= 2 && n30 >= 1) keep('A4', kind, h, rec);
    if (grp === 'TW' && end === 1 && eOwnBig * 2 >= drops && (dBigMax >= 9) && dBigLast <= 3) keep('B1', kind, h, rec);
    if ((grp === 'stack5' || grp === 'stack6') && end === 1) keep('B2', kind, h, rec);
    if (grp === 'TW' && end === 2 && eOwnP * 2 >= drops && drops > 0) keep('C1', kind, h, rec);
    if (grp === 'TW' && born >= 250 && born < 450 && pl === 4 && end === 1 && eOwnBig * 2 >= drops) keep('L1', kind, h, rec);
    if ((grp === 'stack5' || grp === 'stack6') && cls === 3) keep('A5', kind, h, rec);
  }
  if (!top && SETGROUP[g.set] === 'stack5' && kind === 'r500') {
    const T = g[g.us], e = T.ep.cs; let eps = 0; if (e) for (const ph of [2, 3]) eps += e[ph * 9];
    const O = g[g.us === 'A' ? 'B' : 'A'].ep.cs; let oeps = 0; if (O) for (const ph of [2, 3]) oeps += O[ph * 9];
    if (g.rounds >= 450) d1.push({ key: g.key, map: g.map, eps, oeps });
  }
}
async function main() {
  const files = fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl.gz') && (!f.startsWith('top-') || f === opt('top', 'top-all') + '.jsonl.gz'));
  for (const f of files) {
    const rl = readline.createInterface({ input: fs.createReadStream(path.join(CACHE, f)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    for await (const l of rl) if (l.trim()) onGame(JSON.parse(l));
  }
  const L = ['# 선별 기보 (exp/supply-chain/cases.js)', '', `선별 규칙: 부류마다, 지도 유형(500라운드형/전멸형)마다 "<판 키>#<드래곤 id>"의 FNV-1a 해시가 가장 작은 ${PER}건.`, ''];
  for (const c of CLASSES) for (const kind of ['r500', 'elim']) {
    const k = c + '|' + kind; L.push(`## ${c} ${kind}: 부류 크기 ${size[k] || 0}`);
    for (const x of pick[k] || []) L.push('- ' + JSON.stringify(x.rec));
    L.push('');
  }
  d1.sort((a, b) => a.eps - b.eps);
  const med = d1[Math.floor(d1.length / 2)];
  L.push(`## D1 stack5 500라운드형 (r450까지 간 ${d1.length}판): cs 에피소드 r250–449 중앙값 판`, '- ' + JSON.stringify(med), '');
  const outF = path.resolve(ROOT, opt('out', 'exp/supply-chain/cases.md'));
  fs.writeFileSync(outF, L.join('\n') + '\n');
  console.log(L.join('\n'));
}
main().catch(e => { console.error(e); process.exit(1); });
