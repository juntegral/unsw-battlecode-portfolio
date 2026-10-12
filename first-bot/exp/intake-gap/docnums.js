#!/usr/bin/env node
// Prints every number research/observations/intake-gap.md cites, from .cache/intake-gap/numbers.json.
// usage: node exp/intake-gap/docnums.js > exp/intake-gap/docnums.txt
'use strict';
const R = require('../../.cache/intake-gap/numbers.json');
const f0 = x => (x === undefined || x === null || isNaN(x)) ? '–' : Math.round(x).toLocaleString('en-US');
const f1 = x => (x === undefined || x === null || isNaN(x)) ? '–' : (Math.round(x * 10) / 10).toFixed(1);
const f2 = x => (x === undefined || x === null || isNaN(x)) ? '–' : (Math.round(x * 100) / 100).toFixed(2);
const pc = x => (x === undefined || x === null || isNaN(x)) ? '–' : Math.round(x * 100) + '%';
const G = R.groups;
console.log('N', JSON.stringify(R.N), 'checks', JSON.stringify(R.chkSum));
for (const fam of ['r500', 'elim']) {
  console.log(`\n=== ${fam}: main identity (per team-game)`);
  for (const gr of ['merge2', 'stack1-4', 'stack5-8', 'stack9', 'g4r4', 'swarm8', 'px', 'topL']) {
    const x = G[gr + '|' + fam]; if (!x) continue; const t = x.dec.tot, S = x.A;
    const body = t.dBlkMe + t.dBlkOp, open = body + t.dBlkNat + t.dBlkDrop;
    console.log(`${gr.padEnd(9)} n ${x.n} rounds ${f0(S.rounds)} elim ${pc(S.elim)} win ${pc(S.win)} | Iu ${f1(t.Iu)} Io ${f1(t.Io)} gap ${f1(t.gap)} | race ${f1(t.dRace)} = cap ${f1(t.dCap)} [heads ${f1(t.dCapHeadsP)} place ${f1(t.dCapPlaceP)}] + open ${f1(open)} [bodies ${f1(body)} (ours ${f1(t.dBlkMe)}, theirs ${f1(t.dBlkOp)}), nat ${f1(t.dBlkNat)}, drops ${f1(t.dBlkDrop)}] + resid ${f1(t.dResid)} | steals2 ${f1(t.dSteal)} (from us ${f1(t.stolenFromUs)}, by us ${f1(t.stolenByUs)}) | uneaten ${f1(t.dUneat)} (ours ${f1(t.uneatU)}, theirs ${f1(t.uneatO)}) | ties ${f1(t.dTies)} | check ${f1(t.dCheck)} | NU ${f1(t.NU)} NO ${f1(t.NO)} NT ${f1(t.NT)}`);
    console.log(`          shapley: cov ${f1(t.cov)} contest ${f1(t.contest)} uneaten ${f1(t.uneaten)} ties ${f1(t.ties)} | viewB heads ${f1(x.vb.tot.heads)} rate ${f1(x.vb.tot.rate)} (mix ${f1(x.vb.tot.mix)} within ${f1(x.vb.tot.within)})`);
  }
  for (const gr of ['stack5-8', 'merge2', 'stack9', 'topL']) {
    const x = G[gr + '|' + fam]; if (!x) continue;
    console.log(`--- ${fam} ${gr} by phase: gap / race [cap: heads place] open resid / steals2 / uneaten / ties || Iu Io || H us/opp, rate us/opp /10r || NU NO, lost from us, stolen by us, o_U o_O`);
    x.dec.byPh.forEach((r, i) => { const v = x.vb.rows[i]; const open = r.dBlkMe + r.dBlkOp + r.dBlkNat + r.dBlkDrop;
      console.log(`${r.ph.padEnd(9)} ${f1(r.gap)} / ${f1(r.dRace)} [${f1(r.dCap)}: ${f1(r.dCapHeadsP)} ${f1(r.dCapPlaceP)}] ${f1(open)} (nat ${f1(r.dBlkNat)}) ${f1(r.dResid)} / ${f1(r.dSteal)} / ${f1(r.dUneat)} / ${f1(r.dTies)} || ${f1(r.Iu)} ${f1(r.Io)} || ${f0(v.HU)}/${f0(v.HO)} ${f2(v.rU)}/${f2(v.rO)} heads ${f1(v.heads)} rate ${f1(v.rate)} || ${f1(r.NU)} ${f1(r.NO)} ${f1(r.stolenFromUs)} ${f1(r.stolenByUs)} ${pc(r.oU)} ${pc(r.oO)}`); });
  }
  for (const gr of ['stack5-8', 'merge2', 'stack9', 'topL', 'topW', 'px']) {
    const x = G[gr + '|' + fam]; if (!x) continue; const S = x.A;
    console.log(`*** ${fam} ${gr}: units r50,100,250,350,450,end us ${S.unitsAt[0].map(f1).join(' ')} | opp ${S.unitsAt[1].map(f1).join(' ')}`);
    console.log(`    units r0,10,20,30,40,50,100,150,200,250 us ${S.unitsEarly[0].map(f1).join(' ')} | opp ${S.unitsEarly[1].map(f1).join(' ')}`);
    console.log(`    total r0..: us ${S.totalEarly[0].map(f1).join(' ')} | opp ${S.totalEarly[1].map(f1).join(' ')}; king r100,250,350,450,end us ${S.kingAt[0].map(f1).join(' ')} opp ${S.kingAt[1].map(f1).join(' ')}; total r100.. us ${S.totalAt[0].map(f1).join(' ')} opp ${S.totalAt[1].map(f1).join(' ')}`);
    console.log(`    births by phase us ${S.birthPh[0].map(f1).join(' ')} | opp ${S.birthPh[1].map(f1).join(' ')}; deaths us ${S.deathPh[0].map(f1).join(' ')} | opp ${S.deathPh[1].map(f1).join(' ')}`);
    console.log(`    rate by length class /10r (head-rounds): us ${S.rateLc[0].map((q, i) => ['2', '3', '4', '5-7', '8-14', '15+'][i] + ':' + f2(q.r) + '(' + f0(q.h) + ')').join(' ')} | opp ${S.rateLc[1].map((q, i) => ['2', '3', '4', '5-7', '8-14', '15+'][i] + ':' + f2(q.r) + '(' + f0(q.h) + ')').join(' ')}`);
    console.log(`    nat eaten by pearl territory own/neu/enemy us ${S.rateTerr[0].map(q => f1(q.e)).join('/')} opp ${S.rateTerr[1].map(q => f1(q.e)).join('/')}; heads own/neu/enemy us ${S.headTerr[0].map(pc).join('/')} opp ${S.headTerr[1].map(pc).join('/')}; drops eaten ${S.drop.map(f1).join('/')}`);
    const cap = [0, 1, 2].map(t => [0, 1, 2].map(r => S.att.reduce((a, ph) => a + ph[t][r], 0))), capF = [0, 1, 2].map(t => [0, 1, 2].map(r => S.attF.reduce((a, ph) => a + ph[t][r], 0)));
    const sm = a => a.reduce((x, y) => x + y, 0);
    console.log(`    capacity/game total ${f0(sm(S.attTot))}: us-near ${pc(S.attTot[0] / sm(S.attTot))} tie ${pc(S.attTot[1] / sm(S.attTot))} opp-near ${pc(S.attTot[2] / sm(S.attTot))}; our territory opp-near ${pc(cap[1][2] / sm(cap[1]))}; their territory us-near ${pc(cap[2][0] / sm(cap[2]))}; our fountains opp-near ${pc(capF[1][2] / Math.max(1e-9, sm(capF[1])))}; appeared ${f1(S.appeared)} spawned ${f1(S.spawned)}`);
    console.log(`    appeared by territory [neutral, mine, theirs]: ${[0, 1, 2].map(t => { const rr = S.raceT[t]; const tot = rr.flat().reduce((a, b) => a + b, 0); return f1(tot) + ' (we ' + f1(rr[0][0] + rr[1][0] + rr[2][0]) + ', they ' + f1(rr[0][1] + rr[1][1] + rr[2][1]) + ')'; }).join(' | ')}`);
    console.log(`    blocked/game: bodies [ours, theirs] x terr [n, mine, theirs] ${JSON.stringify(S.ob.map(a => a.map(v => +v.toFixed(0))))}; nat pearls by terr (per round) ${JSON.stringify(S.pbr.map(v => +v.toFixed(0)))}; nat pearls terr x fate(spawn attribution) ${JSON.stringify(S.pb.map(a => a.map(v => +v.toFixed(0))))}; drops by terr ${JSON.stringify(S.db.map(v => +v.toFixed(0)))}; mirror observed ${JSON.stringify(S.sbm.map(a => a.map(v => +v.toFixed(1))))}`);
    console.log(`    by race (us-near, tie, opp-near): capacity ${S.attTot.map(f0).join('/')}; bodies ours ${S.obR[0].map(f0).join('/')} theirs ${S.obR[1].map(f0).join('/')}; nat pearls ${S.pbrR.map(f0).join('/')}; drops ${S.dbR.map(f0).join('/')}`);
    console.log(`    movement: turns ${S.turns.map(f0).join('/')} steps ${S.steps.map(f0).join('/')} steps/pearl ${S.stepsPerPearl.map(f1).join('/')} sprint cost ${S.spr.map(f1).join('/')} sprints ${S.sprN.map(f1).join('/')}`);
    const hp = S.hrP; for (const t of [0, 1]) console.log(`    ${t ? 'opp' : 'us '} head-rounds nearest natural pearl d0-3/4-6/7-10/11+ by length <=4 | 5-7 | >=8: ${[0, 1, 2].map(l => { const a = hp[t][l]; const s = sm(a); return a.map(v => pc(v / s)).join('/'); }).join(' | ')}`);
    if (S.act) { console.log(`    labels: ${S.act.filter(a => a.turns > 0.5).map(a => a.k + ' ' + f0(a.turns) + 't/' + f1(a.eat) + 'p (' + f2(a.rate) + ')').join(', ')}`); console.log(`    origins: ${S.org.filter(a => a.births > 0.05).map(a => a.k + ' b' + f1(a.births) + ' eat' + f1(a.eat) + ' hr' + f0(a.hr) + ' r' + f2(a.rate)).join(', ')}`); }
  }
}
console.log('\n=== per map (r500 and elim): group, n, Iu, Io, gap, race, cap [heads place], open, resid, steals2, uneaten, ties | units r100 us/opp | rounds elim');
for (const m of ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma', 'Default', 'Devil', 'Prisoners Dilemma', 'Queen Of Spades', 'Trophy']) for (const gr of ['stack5-8', 'topL', 'merge2', 'stack9']) {
  const x = G[gr + '|map|' + m]; if (!x) continue; const t = x.dec.tot, S = x.A;
  console.log(`${m.padEnd(17)} ${gr.padEnd(8)} ${x.n} ${f0(t.Iu)} ${f0(t.Io)} ${f0(t.gap)} ${f0(t.dRace)} ${f0(t.dCap)} [${f0(t.dCapHeadsP)} ${f0(t.dCapPlaceP)}] ${f0(t.dBlkMe + t.dBlkOp + t.dBlkNat + t.dBlkDrop)} (nat ${f0(t.dBlkNat)}) ${f0(t.dResid)} ${f0(t.dSteal)} ${f0(t.dUneat)} ${f0(t.dTies)} | ${f1(S.unitsAt[0][1])}/${f1(S.unitsAt[1][1])} | ${f0(S.rounds)} ${pc(S.elim)} | VB heads ${f0(x.vb.tot.heads)} rate ${f0(x.vb.tot.rate)}`);
}
console.log('\n=== per map and layout (stack5-8): n, Iu, Io, gap');
for (const k of Object.keys(G).filter(k => k.startsWith('stack5-8|mapv|')).sort()) { const x = G[k], t = x.dec.tot; console.log(`${k.split('|')[2].padEnd(22)} ${x.n} ${f0(t.Iu)} ${f0(t.Io)} ${f0(t.gap)} race ${f0(t.dRace)} steals2 ${f0(t.dSteal)}`); }
console.log('\n=== topL per map and layout: n, Iu, Io, gap');
for (const k of Object.keys(G).filter(k => k.startsWith('topL|mapv|')).sort()) { const x = G[k], t = x.dec.tot; console.log(`${k.split('|')[2].padEnd(22)} ${x.n} ${f0(t.Iu)} ${f0(t.Io)} ${f0(t.gap)}`); }
console.log('\n=== per set: fam n Iu Io gap race steals2');
for (const k of Object.keys(G).filter(k => k.startsWith('set|')).sort()) { const x = G[k], t = x.dec.tot; const [, s, fam] = k.split('|'); console.log(`${s.padEnd(24)} ${fam} ${x.n} ${f0(t.Iu)} ${f0(t.Io)} ${f0(t.gap)} ${f0(t.dRace)} ${f0(t.dSteal)}`); }
