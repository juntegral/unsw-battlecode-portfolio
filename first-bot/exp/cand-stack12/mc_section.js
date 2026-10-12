// ---------------------------------------------------------------------------------------------------------------
// stack12 (research/experiments/cand-stack12.md; the intake-gap study research/observations/intake-gap.md section 13): pf's gates, the study's
// hypothesis-level indicators, protection, pf children and side effects. Shown when a pool carries pf tags, or with --pf (any set, for comparison).
function effectLine12(xs) {
  const ex = xs.filter(x => x.ex), td = {};
  for (const x of ex) if (x.childDeath) td[CAUSE_KO[x.childDeath.cause]] = (td[CAUSE_KO[x.childDeath.cause]] || 0) + 1;
  return `분열 ${pct(ex.length, xs.length)} · 설계 상황(r1–99, pf 지도, 기보의 우리 수 < 표식 목표) ${pct(xs.filter(x => x.sit).length, xs.length)} · 새끼 몸 30라운드 생존 ${pct(ex.filter(x => x.body30).length, ex.length)} (기준 ≥60%; 새끼 자체 ${pct(ex.filter(x => x.childAlive30).length, ex.length)}, 10라운드 몸 ${pct(ex.filter(x => x.body10).length, ex.length)}) · 30라운드 안 자연 진주 ≥1 ${pct(ex.filter(x => x.nat30 >= 1).length, ex.length)} (기준 ≥38%) · 30라운드 안 새끼 죽음: ${Object.entries(td).map(([k, v]) => `${k} ${v}`).join(', ') || '없음'} · 부모 10라운드 생존 ${pct(ex.filter(x => x.parentAlive10).length, ex.length)}`;
}
function caseLine12(x, where, dd) {
  return `${where}: pf 새끼 L${x.childLen || '?'} (수 ${x.uR}/${x.target}${x.fam ? ', 가족 목표' : ''}${x.view ? ', 적 머리 시야 안' : ''}${x.kingTag ? ', 스스로 최장' : ''}${x.startDragon ? ', 시작 드래곤' : ''}) → ${x.childDeath ? `새끼 죽음 ${dd(x.childDeath)}` : '새끼 30라운드 생존'}${x.ex && !x.body30 ? ' (자손도 없음)' : ''}, 30라운드 안 자연 진주 ${x.nat30 ?? 0}${x.sit ? '' : ' (설계 밖)'}`;
}
function stack12Section(A, B, opts) {
  const L = [];
  const has = S => (S.by.pf || []).length > 0;
  if (!has(A) && !(B && has(B)) && !opts.pf) return L;
  const PS12 = require(path.join(ROOT, 'exp', 'cand-stack12', 'pfstats.js'));
  const P = [['이번', A]].concat(B ? [['비교', B]] : []);
  const G = S => (S.s12 || []).filter(g => !g.err);
  const pool = (S, f) => PS12.pool(G(S).filter(f));
  const T = S => S.s12t || [];
  const rec = S => S.by.pf || [];
  const ex = S => rec(S).filter(x => x.ex);
  const f3 = v => v === null || v === undefined ? '–' : v.toFixed(3);
  const OFF = new Set(['Autarky', 'Portals', 'Prisoners Dilemma', 'Prisoners Dilemma (10)']);
  const on = g => S12_MAPS.has(g.map), on5 = g => S12_500.has(g.map), onE = g => S12_ELIM.has(g.map);
  const nOn = S => T(S).filter(g => S12_MAPS.has(g.gmap)).length;
  L.push('## stack12: 조각 먼저 여는 판(pf)', '');
  L.push('- 기준값은 `research/experiments/cand-stack12.md`(2026-10-01 00:03–00:08, 로컬 발동 수치를 보기 전)에서, 상위권·우리 값은 `research/observations/intake-gap.md`(3·13절)와 이전 웨이브(`exp/cand-stack12/baseline.js`)에서 왔다. 수·분열 속도·섭취·관점 B·경주 몫·영토 몫은 그 연구의 추출기(`exp/intake-gap/extract.js` analyse, `aggregate.js` teamView)를 `exp/cand-stack12/pfstats.js`로 같은 기보에 돌려 잰다(연구의 발표값을 다시 냄).');
  L.push('- pf 지도 = Slithery Fight·Schooltime·Trauma(500형)와 Default·Devil·Queen Of Spades·Trophy(전멸형). 끄는 지도 = Autarky, Portals, Prisoners Dilemma(두 판본). 수는 라운드 10·50·100의 첫 턴 전 우리 드래곤 수(판 평균, 전멸 0)다. 생존은 몸(새끼와 그 자손)으로 센다.', '');
  L.push('### 게이트 (기능 적용)', '');
  L.push(`| 지표 | 기준 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|${P.map(() => '---|').join('')}`);
  const row = (name, crit, fn) => L.push(`| ${name} | ${crit} | ${P.map(p => fn(p[1])).join(' | ')} |`);
  row('발동: pf 분열(pf 지도 판당) · 발동한 판', '–', S => { const xs = rec(S); return `${xs.length} (${f1(xs.filter(x => S12_MAPS.has(x.map)).length / Math.max(1, nOn(S)))}) · ${new Set(xs.map(x => x.game)).size}판 / pf 지도 ${nOn(S)}판`; });
  row('1. 설계 상황: r1–99 · pf 지도(정답) · 기보의 우리 수 < 표식 목표', '≥95%', S => { const xs = rec(S); return xs.length ? `${pct(xs.filter(x => x.sit).length, xs.length)} (창 ${pct(xs.filter(x => x.sitR).length, xs.length)} · 지도 ${pct(xs.filter(x => x.sitM).length, xs.length)} · 수 ${pct(xs.filter(x => x.sitU).length, xs.length)}; 표식 수 = 기보 수 ${pct(xs.filter(x => x.tagOk).length, xs.length)} · 정답 판본 목표 미만 ${pct(xs.filter(x => x.sitT).length, xs.length)})` : '–'; });
  row('2. 즉시 효과: 새끼 30라운드 생존(몸: 새끼나 자손; 판이 먼저 끝나면 생존)', '≥60% (csplit 67–72%)', S => { const e = ex(S); return e.length ? `${pct(e.filter(x => x.body30).length, e.length)} (${e.length}마리; 새끼 자체 ${pct(e.filter(x => x.childAlive30).length, e.length)})` : '–'; });
  row('2. 즉시 효과: 새끼가 30라운드 안에 자연 진주 1개 이상', '≥38% (csplit 38–42%)', S => { const e = ex(S); return e.length ? pct(e.filter(x => x.nat30 >= 1).length, e.length) : '–'; });
  row('3. 분열 속도: pf 지도 r0–99, 탈출 분열 뺀 우리 새 머리 ÷ 길이 ≥4 머리-라운드 (500형 · 전멸형; 상대)', '≥0.25 (W5–W11 0.118–0.128)', S => { const a = pool(S, on), b = pool(S, on5), c = pool(S, onE); return a.n ? `${f3(a.speed99)} (${f3(b.speed99)} · ${f3(c.speed99)}; 상대 ${f3(a.speed99O)}; ${a.n}판, 판당 새 머리 ${f1(a.births99)} · 길이 ≥4 머리-라운드 ${f1(a.l4hr99)})` : '–'; });
  row('4. 수: pf 500형 3지도 r50 · r100', '≥14 · ≥22 (W5–W9 8.6 · 12.6)', S => { const a = pool(S, on5); return a.n ? `${f1(a.units[1])} · ${f1(a.units[2])} (상대 ${f1(a.unitsO[1])} · ${f1(a.unitsO[2])}; ${a.n}판)` : '–'; });
  row('4. 수: Slithery Fight r10', '≥15 (W5–W9 8.4)', S => { const a = pool(S, g => g.map === 'Slithery Fight'); return a.n ? `${f1(a.units[0])} (상대 ${f1(a.unitsO[0])}; ${a.n}판)` : '–'; });
  L.push('');
  L.push('### 가설 수준 지표 (관찰; 판단값)', '');
  L.push(`| 지표 | 기준 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|${P.map(() => '---|').join('')}`);
  row('pf 500형 r0–99 자연 진주 섭취(판당; 상대)', '≥67 (W5–W9 41.8, 상대 165.1)', S => { const a = pool(S, on5); return a.n ? `${f1(a.nat99)} (상대 ${f1(a.nat99O)})` : '–'; });
  row('pf 500형 관점 B 머리 항 r0–249', '≤195 (W5–W9 277.4)', S => { const a = pool(S, on5); return a.n ? f1(a.heads249) : '–'; });
  row('pf 500형 경주 몫 r0–249(나타난 국면, N_O − N_U)', '≤275 (W5–W9 393.4)', S => { const a = pool(S, on5); return a.n ? f1(a.race249) : '–'; });
  row('pf 전멸형 관점 B 머리 항 r0–249', '≤85 (W5–W9 118.3)', S => { const a = pool(S, onE); return a.n ? f1(a.heads249) : '–'; });
  row('(참고) Slithery Fight: r0–99 섭취 우리 · 상대 · 수 r10 / r50 / r100', '– (W5–W9 83.5 · 326.0 · 8.4 / 13.1 / 19.8)', S => { const a = pool(S, g => g.map === 'Slithery Fight'); return a.n ? `${f1(a.nat99)} · ${f1(a.nat99O)} · ${a.units.slice(0, 3).map(f1).join(' / ')}` : '–'; });
  row('(참고) 자연 섭취 우리 / 상대(판당): pf 500형 r0–99 · r100–249 · r250+ · 전체', '–', S => { const a = pool(S, on5); if (!a.n) return '–'; const ph = (arr, i, j) => arr.slice(i, j).reduce((s, v) => s + (v || 0), 0); return `${f1(ph(a.natPh, 0, 2))}/${f1(ph(a.natPhO, 0, 2))} · ${f1(a.natPh[2])}/${f1(a.natPhO[2])} · ${f1(ph(a.natPh, 3, 6))}/${f1(ph(a.natPhO, 3, 6))} · ${f1(a.nat)}/${f1(a.natO)}`; });
  row('(참고) 자연 섭취 우리 / 상대(판당): pf 전멸형 r0–99 · 전체', '–', S => { const a = pool(S, onE); return a.n ? `${f1(a.nat99)}/${f1(a.nat99O)} · ${f1(a.nat)}/${f1(a.natO)}` : '–'; });
  row('(대조) 끄는 지도: 수 r50 · r100 · 분열 속도 r0–99 · 자연 섭취 우리/상대', '–', S => { const a = pool(S, g => !S12_MAPS.has(g.map)); return a.n ? `${f1(a.units[1])} · ${f1(a.units[2])} · ${f3(a.speed99)} · ${f1(a.nat)}/${f1(a.natO)} (${a.n}판)` : '–'; });
  L.push('');
  L.push('### 보호', '');
  L.push(`| 지표 | 기준 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|${P.map(() => '---|').join('')}`);
  row('500형 끝 최장(판 평균, 전멸 0; 5지도) · pf 500형', '≥23.2 (stack9; W11 22.8)', S => { const a = pool(S, g => g.kind === 'r500'), b = pool(S, on5); return a.n ? `${f1(a.kingEnd)} · ${f1(b.kingEnd)} (상대 ${f1(a.kingEndO)})` : '–'; });
  row('전멸률 500형 · 전멸형', '오르지 않음 (W10 3% · 63%, W11 6% · 63%)', S => { const a = pool(S, g => g.kind === 'r500'), b = pool(S, g => g.kind === 'elim'); return a.n || b.n ? `${a.n ? pct(Math.round(a.elim * a.n), a.n) : '–'} · ${b.n ? pct(Math.round(b.elim * b.n), b.n) : '–'}` : '–'; });
  row('500형 우리 영토 용량 중 상대 머리가 더 가까운 몫(모든 라운드; 5지도)', '≤34% (W5–W9 35%, W10 41%, W11 42%)', S => { const a = pool(S, g => g.kind === 'r500'); return a.n ? pct(Math.round(1000 * a.terrNear), 1000) : '–'; });
  row('건강: 시간 초과 사망 · 표식 누락 · 한 턴 최대 명령 수(로컬 기보에는 없음: –)', '0 · 0 · <80M', S => `${S.health.fault || 0} · ${(S.health.turns || 0) - (S.health.labelled || 0)} · ${S.health.maxInstr ? (S.health.maxInstr / 1e6).toFixed(1) + 'M' : '–'}`);
  L.push('');
  L.push('### pf 새끼·부모와 부작용 (관찰; 판정에 쓰지 않음)', '');
  L.push(`| 항목 | ${P.map(p => p[0]).join(' | ')} |`, `|---|${P.map(() => '---|').join('')}`);
  const srow = (name, fn) => L.push(`| ${name} | ${P.map(p => fn(p[1])).join(' | ')} |`);
  const causeMix = (xs, pick) => { const c = [0, 0, 0, 0, 0, 0, 0, 0]; let n = 0; for (const x of xs) { const z = pick(x); if (z) { c[z.cause] = (c[z.cause] || 0) + 1; n++; } } return { c, n }; };
  srow('pf 새끼 30라운드 안 죽음(마리 · 몫): 갇힘 · 박힘(상대 돌진) · 우리가 박음 · 아군 머리 · 희생 · 그 밖', S => { const e = ex(S); if (!e.length) return '–'; const m = causeMix(e, x => x.childDeath); const o = m.n - m.c[1] - m.c[2] - m.c[3] - m.c[5] - m.c[0]; return `${m.n} · ${pct(m.n, e.length)}: ${m.c[1]} · ${m.c[2]} · ${m.c[3]} · ${m.c[5]} · ${m.c[0]} · ${o}`; });
  srow('pf 새끼 가운데 갇혀 죽은 몫: 30라운드 안 · 끝까지(태어난 새끼 전체 대비 / 죽은 새끼 대비)', S => { const e = ex(S); if (!e.length) return '–'; const t30 = e.filter(x => x.childDeath && x.childDeath.cause === 1).length, dead = e.filter(x => x.childEnd), tAll = dead.filter(x => x.childEnd.cause === 1).length; return `${pct(t30, e.length)} · ${pct(tAll, e.length)} / ${pct(tAll, dead.length)} (죽은 ${dead.length}마리)`; });
  srow('pf 새끼 끝: 끝까지 삶 · 표식 희생(conv·feed) · 갇힘 · 박힘 · 우리가 박음 · 아군 머리 · 그 밖(마리)', S => { const e = ex(S); if (!e.length) return '–'; const al = e.filter(x => !x.childEnd).length, fed = e.filter(x => x.childEnd && x.childEnd.fed).length, k = c => e.filter(x => x.childEnd && !x.childEnd.fed && x.childEnd.cause === c).length; const rest = e.length - al - fed - k(1) - k(2) - k(3) - k(5); return `${al} · ${fed} · ${k(1)} · ${k(2)} · ${k(3)} · ${k(5)} · ${rest}`; });
  srow('부모 10라운드 생존(자체 · 몸) · 10라운드 안 부모 죽음 원인', S => { const e = ex(S); if (!e.length) return '–'; const m = causeMix(e, x => x.parentDeath10); return `${pct(e.filter(x => x.parentAlive10).length, e.length)} · ${pct(e.filter(x => x.parentBody10).length, e.length)} · ${m.c.map((v, i) => v ? `${CAUSE_KO[i]} ${v}` : '').filter(Boolean).join(', ') || '없음'}`; });
  srow('pf 표식: 가족 목표(f) · 시야에 적 머리(v) · 스스로 최장(k) · 시작 드래곤이 나눔 · 새끼가 우리 영토에서 태어남', S => { const xs = rec(S), e = ex(S); return xs.length ? `${pct(xs.filter(x => x.fam).length, xs.length)} · ${pct(xs.filter(x => x.view).length, xs.length)} · ${pct(xs.filter(x => x.kingTag).length, xs.length)} · ${xs.filter(x => x.startDragon).length}회 · ${pct(e.filter(x => x.bornOwn).length, e.length)}` : '–'; });
  srow('pf 차례인데 못 나눔(r1–99, pf 지도 판당): 이동 관문(pfx) · 새끼 자리(pfc)', S => { const gs = T(S).filter(g => S12_MAPS.has(g.gmap)); return gs.length ? `${f1(gs.reduce((a, g) => a + (g.pfx99 || 0), 0) / gs.length)} · ${f1(gs.reduce((a, g) => a + (g.pfc99 || 0), 0) / gs.length)}` : '–'; });
  srow('수 한도(pf 지도): 판 평균 최대 수 · 수 ≥56인 라운드가 있는 판', S => { const gs = T(S).filter(g => S12_MAPS.has(g.gmap)); return gs.length ? `${f1(gs.reduce((a, g) => a + (g.maxU || 0), 0) / gs.length)} · ${gs.filter(g => g.at56 > 0).length}/${gs.length}` : '–'; });
  srow('우리 최장 r100 · r250(판 평균; pf 500형 / Slithery Fight / pf 전멸형)', S => { const f = gs => gs.length ? `${f1(gs.reduce((a, g) => a + (g.k100 || 0), 0) / gs.length)} · ${f1(gs.reduce((a, g) => a + (g.k250 || 0), 0) / gs.length)}` : '–'; return `${f(T(S).filter(g => S12_500.has(g.gmap)))} / ${f(T(S).filter(g => g.gmap === 'Slithery Fight'))} / ${f(T(S).filter(g => S12_ELIM.has(g.gmap)))}`; });
  srow('우리 드래곤 죽음(판당; pf 지도, 모든 라운드 / r250 전): 갇힘 · 박힘 · 아군 머리', S => { const gs = G(S).filter(on).map(g => g.t5 || {}); if (!gs.length) return '–'; const m = f => f1(gs.reduce((a, t) => a + (t[f] || 0), 0) / gs.length); return `${m('dTrap')} · ${m('dRam')} · ${m('dAlly')} / ${m('dTrap250')} · ${m('dRam250')} · ${m('dAlly250')}`; });
  srow('r1–99 pf 지도 우리 조각(길이 ≤4)의 교환(판당): 수 · d3 ≤−1 / 0 / ≥+1(건) · d3 ≤−1 가운데 TRADE 표식 / kint / 표식 없는 이동(떠밀림) · 두 몸 진주 net20 합(판당) · 거부(lntv) 턴(판당)', S => { const gs = G(S).filter(on); if (!gs.length) return '–'; let n = 0, lo = 0, z = 0, hi = 0, net = 0, loT = 0, loK = 0, loM = 0; for (const g of gs) for (const q of g.xch || []) { if (q[0] >= 100 || q[14] > 4) continue; n++; if (q[3] <= -1) { lo++; if (q[8]) loK++; else if (q[15] === 'trade') loT++; else loM++; } else if (q[3] === 0) z++; else hi++; if (q[13]) net += q[12]; } const lv = T(S).filter(g => S12_MAPS.has(g.gmap)).reduce((a, g) => a + (g.lntv99 || 0), 0); return `${f1(n / gs.length)} · ${lo} / ${z} / ${hi} · ${loT} / ${loK} / ${loM} · ${f1(net / gs.length)} · ${f1(lv / gs.length)}`; });
  srow('늦은 사슬(판당, pf 500형): conv · feed · 모이기 드래곤 · lsplit · frag · csplit', S => { const gs = T(S).filter(g => S12_500.has(g.gmap)).length; if (!gs) return '–'; const c = k => (S.by[k] || []).filter(x => S12_500.has(x.map)).length / gs; return ['conv', 'feed', 'gather', 'lsplit', 'frag', 'csplit'].map(k => f1(c(k))).join(' · '); });
  L.push('');
  L.push('### 지도 가르기 (pf; 판 단위)', '');
  L.push(`| 지도 | ${P.map(p => `${p[0]}: 판 · pf 발동 · 켜는 가족이 아닌 표식에서 발동`).join(' | ')} |`, `|---|${P.map(() => '---|').join('')}`);
  const maps = [...new Set(P.flatMap(p => T(p[1]).map(g => g.gmap)))].sort();
  const fam = t => t ? t.split('/')[0].replace(/_/g, ' ') : null;
  for (const m of maps) L.push(`| ${m}${OFF.has(m) ? ' (끔)' : ''} | ${P.map(p => { const xs = rec(p[1]).filter(x => x.map === m); return `${T(p[1]).filter(g => g.gmap === m).length} · ${xs.length} · ${xs.filter(x => !S12_MAPS.has(fam(x.mt))).length}`; }).join(' | ')} |`);
  L.push('', `- 추출기 재구성 점검이 0이 아닌 판: ${P.map(p => `${p[0]} ${G(p[1]).filter(g => g.chkBad).length}`).join(' · ')}; 추출 오류: ${P.map(p => `${p[0]} ${(p[1].s12 || []).filter(g => g.err).length}`).join(' · ')}.`, '');
  return L;
}
