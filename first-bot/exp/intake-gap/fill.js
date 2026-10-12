#!/usr/bin/env node
// Fills exp/intake-gap/doc.tmpl.md with .cache/intake-gap/numbers.json -> research/observations/intake-gap.md
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const R = JSON.parse(fs.readFileSync(path.join(ROOT, '.cache', 'intake-gap', 'numbers.json'), 'utf8'));
const G = R.groups;
const f0 = x => (x === undefined || x === null || isNaN(x)) ? '–' : Math.round(x).toLocaleString('en-US');
const f1 = x => (x === undefined || x === null || isNaN(x)) ? '–' : (Math.round(x * 10) / 10).toFixed(1);
const pc = x => (x === undefined || x === null || isNaN(x)) ? '–' : Math.round(x * 100) + '%';
const f2x = x => (x === undefined || x === null || isNaN(x)) ? '–' : (Math.round(x * 100) / 100).toFixed(2);
const sm = a => a.reduce((x, y) => x + y, 0);
// independent-recount coverage of top games
let rcN = 0, topRaw = 0;
for (const f of fs.readdirSync(path.join(ROOT, '.cache', 'intake-gap')).filter(f => /^top.*\.jsonl$/.test(f)))
  for (const l of fs.readFileSync(path.join(ROOT, '.cache', 'intake-gap', f), 'utf8').split('\n')) { if (!l.trim()) continue; topRaw++; if (/"chkR":\{/.test(l)) rcN++; }
const V = {};
V.TOPN = f0(R.N.top); V.TOPSTALL = f0(R.N.exStall); V.TOPDRAW = f0(R.N.exDraw); V.ALLN = f0(R.N.online + R.N.topRaw); V.RCN = f0(rcN);
const t58 = G['stack5-8|r500'].dec.tot, e58 = G['stack5-8|elim'].dec.tot;
V.H58 = f1(t58.dCapHeadsP); V.P58 = f1(t58.dCapPlaceP); V.H58P = pc(t58.dCapHeadsP / t58.gap); V.P58P = pc(t58.dCapPlaceP / t58.gap);
V.H58E = f1(e58.dCapHeadsP); V.P58E = f1(e58.dCapPlaceP);
const TL = G['topL|r500'], TE = G['topL|elim'], TW = G['topW|r500'];
const fillT = (pre, X) => { const t = X.dec.tot;
  V[pre + '_GAP'] = f1(t.gap); V[pre + '_RACE'] = f1(t.dRace); V[pre + '_CAP'] = f1(t.dCap); V[pre + '_H'] = f1(t.dCapHeadsP); V[pre + '_P'] = f1(t.dCapPlaceP);
  V[pre + '_OPEN'] = f1(t.dBlkMe + t.dBlkOp + t.dBlkNat + t.dBlkDrop); V[pre + '_NAT'] = f1(t.dBlkNat); V[pre + '_BODY'] = f1(t.dBlkMe + t.dBlkOp); V[pre + '_DROP'] = f1(t.dBlkDrop);
  V[pre + '_RES'] = f1(t.dResid); V[pre + '_STEAL'] = f1(t.dSteal); V[pre + '_UNEAT'] = f1(t.dUneat); V[pre + '_TIE'] = f1(t.dTies); };
fillT('TL', TL); fillT('TE', TE);
V.TOPL500N = f0(TL.n); V.TOPLELN = f0(TE.n); V.TL_VBH = f1(TL.vb.tot.heads);
V.TOPWLGAP = f1(TL.dec.tot.gap); V.TOPWK = f1(TL.A.kingAt[1][4]); V.TOPLK = f1(TL.A.kingAt[0][4]);
// phase rows
V.PHASEROWS58 = G['stack5-8|r500'].dec.byPh.map(r => `| ${r.ph} | ${f1(r.gap)} | ${f1(r.dRace)} | ${f1(r.dCap)} (${f1(r.dCapHeadsP)} · ${f1(r.dCapPlaceP)}) | ${f1(r.dBlkMe + r.dBlkOp + r.dBlkNat + r.dBlkDrop)} (${f1(r.dBlkNat)}) | ${f1(r.dResid)} | ${f1(r.dSteal)} | ${f1(r.dUneat)} | ${f1(r.dTies)} | ${f1(r.stolenFromUs)} / ${f1(r.stolenByUs)} | ${pc(r.oU)} / ${pc(r.oO)} |`).join('\n');
// map rows
const MAPS = ['Slithery Fight', 'Schooltime', 'Trauma', 'Portals', 'Autarky', 'Devil', 'Default', 'Queen Of Spades', 'Trophy', 'Prisoners Dilemma'];
V.MAPROWS = MAPS.map(m => { const x = G['stack5-8|map|' + m]; if (!x) return null; const t = x.dec.tot, S = x.A;
  return `| ${m} | ${f0(t.Iu)} | ${f0(t.Io)} | ${f0(t.gap)} | ${f0(t.dRace)} | ${f0(t.dCap)} (${f0(t.dCapHeadsP)} · ${f0(t.dCapPlaceP)}) | ${f0(t.dBlkMe + t.dBlkOp + t.dBlkNat + t.dBlkDrop)} (${f0(t.dBlkNat)}) | ${f0(t.dSteal)} | ${f0(x.vb.tot.heads)} · ${f0(x.vb.tot.rate)} | ${f1(S.unitsAt[0][1])} / ${f1(S.unitsAt[1][1])} |`; }).filter(Boolean).join('\n');
// layouts
const lay = []; for (const m of ['Devil', 'Queen Of Spades', 'Schooltime', 'Slithery Fight', 'Prisoners Dilemma']) { const ks = Object.keys(G).filter(k => k.startsWith('stack5-8|mapv|' + m + '/')).sort(); if (ks.length < 2) continue;
  lay.push(`${m} ` + ks.map(k => { const x = G[k], t = x.dec.tot; return `${k.split('/').pop()} ${x.n}판 ${f0(t.Iu)} 대 ${f0(t.Io)}(격차 ${f0(t.gap)})`; }).join(', ')); }
V.LAYOUTNOTE = lay.length ? '두 판본이 모두 있는 지도(1차 표본): ' + lay.join('; ') + '.' : '';
// section 6 and 11
const capShares = X => { const S = X.A; const cap = [0, 1, 2].map(t => [0, 1, 2].map(r => S.att.reduce((a, ph) => a + ph[t][r], 0))); const capF = [0, 1, 2].map(t => [0, 1, 2].map(r => S.attF.reduce((a, ph) => a + ph[t][r], 0)));
  return { all: S.attTot.map(v => v / sm(S.attTot)), ownOpp: cap[1][2] / sm(cap[1]), theirUs: cap[2][0] / sm(cap[2]), fount: capF[1][2] / Math.max(1e-9, sm(capF[1])), heads: S.headTerr[0], eat: S.rateTerr[0].map(q => q.e) }; };
const cl = capShares(TL), cw = capShares(TW);
V.TLCAP = cl.all.map(pc).join(' / '); V.TLOWNOPP = pc(cl.ownOpp); V.TWOWNOPP = pc(cw.ownOpp); V.TLTHEIRUS = pc(cl.theirUs); V.TWTHEIRUS = pc(cw.theirUs); V.TLFOUNT = pc(cl.fount);
V.TLHEADS = cl.heads.map(pc).join(' / '); V.TWHEADS = cw.heads.map(pc).join(' / '); V.TLEAT = cl.eat.map(f1).join(' / '); V.TWEAT = cw.eat.map(f1).join(' / ');
V.TLRAID = f1(cl.eat[2]);
V.TL_R2 = f2x(TL.A.rateLc[0][0].r) + ' 대 ' + f2x(TL.A.rateLc[1][0].r);
{ const hp = TL.A.hrP[0][0], ssum = sm(hp); V.TL_PNEAR = pc(hp[0] / ssum) + ', ' + pc(hp[3] / ssum); V.TL_P11 = pc(hp[3] / ssum); }
{ const S = TL.A; const blocked = sm(S.ob[0]) + sm(S.ob[1]) + sm(S.pbr) + sm(S.db); V.TL_CAPTOT = f0(sm(S.attTot)); V.TL_APP = f0(S.appeared); V.TL_PRED = f0(sm(S.attTot) - blocked);
  const r = TL.dec.byPh[2]; V.TL_OPEN100 = pc(r.oU) + ' / ' + pc(r.oO); }
V.TL_IU = f0(TL.A.Iu); V.TL_RATIO = pc(TL.A.Iu / TL.A.Io); V.TL_IO = f0(TL.A.Io); V.TL_DROPS = TL.A.drop.map(f0).join(' / '); V.TLK = f1(TL.A.kingAt[0][4]); V.TWK = f1(TL.A.kingAt[1][4]); V.TL_TOT = f1(TL.A.totalAt[0][4]) + ' / ' + f1(TL.A.totalAt[1][4]);
// pf targets: elite winners' r100 units per map (and per layout where two exist)
const tg = [];
for (const m of ['Slithery Fight', 'Schooltime', 'Trauma', 'Portals', 'Devil', 'Default', 'Queen Of Spades', 'Trophy']) {
  const x = G['topL|map|' + m]; if (!x) continue;
  const ks = Object.keys(G).filter(k => k.startsWith('topL|mapv|' + m + '/')).sort();
  const lays = ks.length >= 2 ? ' (' + ks.map(k => k.split('/').pop() + ' ' + f0(G[k].A.unitsAt[1][1])).join(', ') + ')' : '';
  tg.push(`${m} ${f0(x.A.unitsAt[1][1])}${lays}`);
}
V.PFTARGETS = tg.join(', ') + '. 값은 상위권 승자의 r100 평균 수(판본별은 괄호)이고, 켠 지도에서 목표 = 그 값(64 한도 안).';
let s = fs.readFileSync(path.join(__dirname, 'doc.tmpl.md'), 'utf8');
const missing = new Set();
s = s.replace(/\{\{([A-Z0-9_]+)\}\}/g, (m, k) => { if (V[k] === undefined) { missing.add(k); return m; } return V[k]; });
fs.writeFileSync(path.join(ROOT, 'research', 'observations', 'intake-gap.md'), s);
console.log('filled; missing:', [...missing].join(', ') || 'none', '| top raw', topRaw, 'recount subset', rcN);
