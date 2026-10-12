#!/usr/bin/env node
// cand-stack11 (research/experiments/cand-stack11.md): add the stack11 section (gh / ghd / kx / lwk records, the pre-registered gates and the
// endgame king study's hypothesis-level indicators) to a copy of tools/mech_check.js. Every edit is an exact-string replacement whose
// anchor must occur exactly once, so a changed base fails loudly and nothing is written.
// usage: node exp/cand-stack11/mc_apply.js <mech_check.js copy>
'use strict';
const fs = require('fs'), path = require('path');
const file = path.resolve(process.argv[2] || '');
if (!fs.existsSync(file)) { console.error('usage: mc_apply.js <mech_check.js copy>'); process.exit(2); }

const HEADER = `//   stack11 (research/experiments/cand-stack11.md; study research/observations/endgame-king.md sections 3-5 and 7):
//   gh        move label " gh": a gathering turn within GH_HOLD + 2 (5) of the goal (the leaf penalty stops at 3). One record per turn.
//             Situation: the team's longest at the turn start (ledger rule, ties to the lowest id), not this dragon, within Manhattan 6.
//   ghd       move label " ghd@<x>,<y>": a fresh death drop within Manhattan 2 of a longer ally's head left to that ally (one record per dragon
//             and named pearl: tile + origin, with the first label's view). Situation: the pearl is a death drop in the ledger at the label.
//             Effect: eaten by an own dragon that was longer than the labeller with its head within Manhattan 2 of the pearl at the first
//             label ("the longer ally beside it").
//   kx        move label " kx<d>" (+ " kxm" when the move ends farther): the king keeps >= 7 from enemy heads from r300 on Schooltime, Slithery
//             Fight, Trauma and Autarky. Situation: no own dragon longer (replay, the turn start) and an enemy head within Manhattan 7.
//   lwk       move label " lwk": the late window (r430+) fed only the king class where the old rule would have fed. Situation: r >= 430 and
//             a longer own dragon's head within Manhattan 5 at the turn start.
//   stack11 metrics (section shown with gh / ghd / kx / lwk tags or --endgame): the endgame king study's numbers for our team by its own code
//             (exp/endgame-king/extract.js analyse() on the same replay, run when pool A carries stack11 tags or with --endgame): interception
//             (r300+ labelled feeds aimed at the line whose pearls other own dragons ate), the line member's (L >= 8) exposure to enemy heads
//             (torus Manhattan <= 6) by bin and map, r430+ feed targets, the line's sacrifice / natural / enemy-death pearls and split loss,
//             growth, the longest lost to an enemy head from r340; enemy deaths into or trapped against our line member's body from r300.
`;

const CONSTS = `// stack11 (cand-stack11.md): kx's maps (the bot's kxMapOn) and the record kinds that switch the stack11 section on
const S11_KX_MAPS = new Set(['Schooltime', 'Slithery Fight', 'Trauma', 'Autarky']);
const S11_KINDS = new Set(['gh', 'ghd', 'kx', 'lwk']);
`;

const PARSE = `      else if (t === 'gh') f.gh = true;                                                // stack11 gh
      else if ((g = /^ghd@(\\d+),(\\d+)$/.exec(t))) f.ghd = { x: +g[1], y: +g[2] };      // stack11 ghd
      else if ((g = /^kx(\\d+)$/.exec(t))) f.kx = +g[1];                                // stack11 kx
      else if (t === 'kxm') f.kxm = true;                                              // stack11 kxm
      else if (t === 'lwk') f.lwk = true;                                              // stack11 lwk
`;

const STATE = `  // ---- stack11 (research/experiments/cand-stack11.md): the pre-move view of the pearl a ghd label names (its origin, the longer own dragons
  //   within Manhattan 2 of it), ghd episodes, and enemy deaths from r300 into our body (cause 4) or trapped with our body beside the head (cause 1)
  const S11 = { ghdPre: new Map(), ghdEps: new Map(), bodyKill: [], trapBy: [] };
`;

const IND = `      { // stack11 ghd: the named pearl as the board holds it before the move, and the own dragons longer than us with a head within 2 of it
        const m11 = /(?:^|\\s)ghd@(\\d+),(\\d+)(?:\\s|$)/.exec(e.text || '');
        if (m11) {
          const p11 = { x: +m11[1], y: +m11[2] }, k11 = c.key(p11.x, p11.y), beside = [];
          for (const o of c.drag.values()) if (o.team === us && o.id !== d.id && o.body.length > d.body.length && c.tdist(o.body[0], p11) <= 2) beside.push(o.id);
          S11.ghdPre.set(e.id, { r, k: k11, px: p11.x, py: p11.y, o: c.pearls.has(k11) ? c.pearls.get(k11) : null, beside });
        }
      }
`;

const ACT = `          if (t.gh || t.kx !== undefined || t.lwk) { // stack11: the view at this dragon's turn start (its head before the move; the others as they stand)
            const h11 = before[0], L11 = before.length;
            let eD11 = 99, longest11 = 1, lk11 = 1, longer5 = 0, kg11 = null;
            for (const o of c.drag.values()) {
              if (o.id === d.id) continue;
              const x11 = c.tdist(o.body[0], h11);
              if (o.team !== us) { if (x11 < eD11) eD11 = x11; continue; }
              if (o.body.length > L11) { longest11 = 0; if (x11 <= 5) longer5 = 1; }
              if (o.body.length > L11 || (o.body.length === L11 && o.id < d.id)) lk11 = 0;
              if (!kg11 || o.body.length > kg11.body.length || (o.body.length === kg11.body.length && o.id < kg11.id)) kg11 = o;
            }
            if (t.gh) made.push({ k: 'gh', ...base, kD: lk11 || !kg11 ? null : c.tdist(kg11.body[0], h11), selfKing: lk11 });
            if (t.kx !== undefined) {
              let eDp = 99; for (const o of c.drag.values()) if (o.team !== us) eDp = Math.min(eDp, c.tdist(o.body[0], d.body[0]));
              made.push({ k: 'kx', ...base, d11: t.kx, kxm: t.kxm ? 1 : 0, longest: longest11, lk: lk11, eD: eD11, eDp });
            }
            if (t.lwk) made.push({ k: 'lwk', ...base, longer5 });
          }
          if (t.ghd) { // stack11 ghd: one record per dragon and named pearl (tile + origin), with the first label's view
            const q11 = S11.ghdPre.get(d.id);
            if (q11 && q11.r === r) {
              const key11 = d.id + ':' + q11.k + ':' + q11.o; let ep11 = S11.ghdEps.get(key11);
              if (!ep11) { ep11 = { k: 'ghd', ...base, tile: q11.k, px: q11.px, py: q11.py, o: q11.o, beside: q11.beside, turns: 0 }; S11.ghdEps.set(key11, ep11); recs.push(ep11); }
              ep11.turns++;
            }
          }
          S11.ghdPre.delete(d.id);
`;

const DEATH = `      if (d.team !== us && r >= 300 && NB) { // stack11: an enemy dragon killed by our body: it moved into it (cause 4) or died trapped (cause 1)
        const ids11 = new Set(); if (other && other.team === us && (rec.cause === 4 || rec.cause === 1)) ids11.add(other.id);
        if (rec.cause === 1) { const hk11 = K(d.body[0]); for (let j = 0; j < 4; j++) { const u = NB[hk11 * 4 + j]; if (u < 0) continue; const oid = c.occ.get(u); if (oid === undefined) continue; const od = c.drag.get(oid); if (od && od.team === us) ids11.add(oid); } }
        if (ids11.size) (rec.cause === 4 ? S11.bodyKill : S11.trapBy).push([r, [...ids11], rec.len]);
      }
`;

const EFFECTS = `      case 'gh': { x.ex = 1; x.sit = !x.selfKing && x.kD !== null && x.kD <= 6 ? 1 : 0; x.ok = null; break; } // stack11 (cand-stack11.md)
      case 'kx': { // stack11: situation from the replay, the move's effect on the nearest enemy head, death by an enemy head within 10 rounds
        x.ex = 1; x.sit = x.longest && x.eD <= 7 ? 1 : 0; x.sitLk = x.lk && x.eD <= 7 ? 1 : 0; x.away = x.eDp > x.eD ? 1 : 0; x.onKx = S11_KX_MAPS.has(task.map) ? 1 : 0;
        const dz = life.get(x.id) && life.get(x.id).death; x.rammed10 = dz && (dz.cause === 2 || dz.cause === 3) && dz.r <= x.r + 10 ? 1 : 0; x.ok = null;
        // dead ends (body rule, user 17:16): the body = this dragon and its descendants born from this turn on (an escape split leaves the
        // id on the stub), lost within 20 rounds; and an escape split (no safe move) by this dragon within 20 rounds
        { const t20 = Math.min(x.r + 20, rounds - 1), st = [x.id]; let bodyOn = 0;
          while (st.length && !bodyOn) { const y = st.pop(); if (alive(y, t20)) bodyOn = 1; for (const c of kids.get(y) || []) { const Lc = life.get(c); if (Lc && Lc.born >= x.r && Lc.born <= t20) st.push(c); } }
          x.bodyLost20 = bodyOn ? 0 : 1; }
        x.esc20 = recs.some(q => q.k === 'escsplit' && q.id === x.id && q.r > x.r && q.r <= x.r + 20) ? 1 : 0;
        x.lineNow = c2.inLine(x.id, x.r) ? 1 : 0; x.onLine = c2.win.has(x.id) ? 1 : 0;   // the final king's line member at this turn / ever (coordinator 23:58)
        break;
      }
      case 'lwk': { x.ex = 1; x.sit = x.r >= 430 && x.longer5 ? 1 : 0; x.alive10 = body(x.id, x.r + 10); x.aliveEnd = body(x.id, rounds - 1); x.ok = null; break; } // stack11
      case 'ghd': { // stack11: who ate the named pearl (the first eater at or after the label)
        x.ex = 1; x.present = x.o !== null ? 1 : 0; x.drop = x.o !== null && x.o >= 0 ? 1 : 0;
        const e0 = x.present ? (eatenBy.get(x.tile + ':' + x.o) || []).filter(q => q.r >= x.r).sort((a, b) => a.r - b.r)[0] || null : null;
        x.side = !e0 ? 'none' : e0.team === us ? 'us' : 'them';
        x.eatBeside = e0 && e0.team === us && x.beside.includes(e0.id) ? 1 : 0;
        x.eatSelf = e0 && e0.id === x.id ? 1 : 0;
        x.eatLonger = e0 && e0.team === us && e0.id !== x.id && lenAt(e0.id, e0.r) > x.L ? 1 : 0;
        x.eatLine = e0 && e0.team === us && c2.inLine(e0.id, e0.r) ? 1 : 0;
        x.delay = e0 ? e0.r - x.r : null; x.nBeside = x.beside.length; delete x.beside;
        x.ok = x.drop ? x.eatBeside : null;
        break;
      }
`;

const S11BLOCK = `  // stack11 (cand-stack11.md): the endgame king study's per-game numbers for our team by its own code (exp/endgame-king/extract.js analyse()),
  // when asked (task.endgame): the line's flows per 50-round bin from r300 (dec: nat, own sac, own other, enemy, sprint, split off, split path),
  // the line member's turns (env: turns, eD <= 3, eD <= 6, eD sum, natural pearls <= 5, own territory, team longest, enemy heads <= 6, own heads
  // <= 6), the labelled feeds from r300 that died (k, r, drops, to the line, to other own, to the enemy, target on the line, by a gathering
  // dragon), our L >= 8 deaths from r300 (r, len, cause, was the longest), root gathering episodes and those whose family's last death was an
  // own head; enemy deaths from r300 against our line member's body (body kills: cause 4; traps: cause 1), our L >= 8 survivors off the line.
  let s11 = null;
  if (task.endgame) try {
    const EK = require(path.join(ROOT, 'exp', 'endgame-king', 'extract.js'));
    const X11 = EK.analyse(R, { key: task.key, map: task.map, us, set: task.set || null, src: task.src, opp: task.opp || null }, perGame), T11 = X11[us];
    let bkLine = 0, trLine = 0;
    for (const q of S11.bodyKill) if (q[1].some(id => c2.inLine(id, q[0]))) bkLine++;
    for (const q of S11.trapBy) if (q[1].some(id => c2.inLine(id, q[0]))) trLine++;
    let off8 = 0; for (const [id, Lf] of fin) if (id !== finKing && Lf >= 8) off8 += Lf;
    const gr11 = (T11.gath || []).filter(q => !q[40]);
    s11 = { kind: X11.kind, rounds: X11.rounds, full: X11.rounds === 500 && T11.kid >= 0 ? 1 : 0, L300: T11.Lt && T11.Lt[300] !== undefined ? T11.Lt[300] : null, king: T11.king,
      dec: [1, 2, 3, 4].map(b => T11.dec[b]), env: T11.env,
      conv: (T11.conv || []).filter(v => v[6] && v[1] >= 300).map(v => [v[0], v[1], v[7], v[8], v[10], v[11], v[12], v[13]]),
      kd: (T11.kd || []).map(q => [q[0], q[1], q[2], q[3]]), gathRoot: gr11.length, gathAllyHead: gr11.filter(q => !q[42] && !q[22] && !q[44] && q[43] === 5).length,
      gathFate: [0, 1, 2, 3, 4].map(k => gr11.filter(q => (q[42] ? 0 : q[22] ? 1 : q[44] ? 2 : q[43] === 0 ? 3 : 4) === k).length), // the study's T3 family end
      gathFedDelay: gr11.filter(q => q[15] === 1).map(q => q[16] - q[1]),                          // rounds from the first g tag to its labelled feed
      bkAll: S11.bodyKill.length, bkLine, trAll: S11.trapBy.length, trLine, off8,
      chkBad: Object.values(X11.chk || {}).some(v => v) || Object.values(X11.chk2 || {}).some(v => v) ? 1 : 0 };
  } catch (err) { s11 = { err: String(err).slice(0, 160) }; }                       // never drop the game for the extra indicators
`;

const SECTION = `// stack11 (research/experiments/cand-stack11.md; the endgame king study research/observations/endgame-king.md sections 3-5 and 7): gh / ghd /
// kx / lwk lines, the pre-registered gates, the study's hypothesis-level indicators (its own code on the same replays, see analyse) and the
// side effects. Shown when a pool carries gh / ghd / kx / lwk tags, or with --endgame (any set, for comparison).
function effectLine11(k, xs) {
  if (k === 'gh') { const nk = xs.filter(x => !x.selfKing);
    return \`턴 \${xs.length} · 설계 상황(팀 최장(기보, 이 드래곤 아님)이 맨해튼 6 안) \${pct(xs.filter(x => x.sit).length, xs.length)} (기준 ≥95%) · 이 드래곤이 팀 최장 \${pct(xs.filter(x => x.selfKing).length, xs.length)} · 팀 최장까지 맨해튼 평균 \${f1(avg(nk.map(x => x.kD)))}\`; }
  if (k === 'ghd') { const dr = xs.filter(x => x.drop), side = s => dr.filter(x => x.side === s).length;
    return \`진주 \${xs.length}개 (표식 턴 \${xs.reduce((s, x) => s + x.turns, 0)}) · 실제 사망 진주 \${pct(dr.length, xs.length)} (기준 ≥95%; 자연 \${xs.filter(x => x.present && !x.drop).length}, 이미 없음 \${xs.filter(x => !x.present).length}) · 곁의 더 긴 아군이 먹음 \${pct(dr.filter(x => x.eatBeside).length, dr.length)} (기준 ≥70%) · 우리 \${pct(side('us'), dr.length)} (표식한 드래곤 \${pct(dr.filter(x => x.eatSelf).length, dr.length)}, 더 긴 우리 드래곤 \${pct(dr.filter(x => x.eatLonger).length, dr.length)}, 최종 왕 계보 \${pct(dr.filter(x => x.eatLine).length, dr.length)}) · 상대 \${pct(side('them'), dr.length)} · 안 먹힘 \${pct(side('none'), dr.length)} · 곁의 더 긴 아군 수 평균 \${f1(avg(dr.map(x => x.nBeside)))}\`; }
  if (k === 'kx') { const dd = {}; for (const x of xs) dd[x.d11] = (dd[x.d11] || 0) + 1;
    return \`턴 \${xs.length} · 설계 상황(기보: 더 긴 우리 드래곤 없음, 적 머리 맨해튼 7 안) \${pct(xs.filter(x => x.sit).length, xs.length)} (기준 ≥90%; 질량 장부의 왕 기준 \${pct(xs.filter(x => x.sitLk).length, xs.length)}) · kxm \${pct(xs.filter(x => x.kxm).length, xs.length)} · 움직인 뒤 가장 가까운 적 머리가 멀어짐 \${pct(xs.filter(x => x.away).length, xs.length)} (kxm 턴 \${pct(xs.filter(x => x.kxm && x.away).length, xs.filter(x => x.kxm).length)}) · 표식 거리 \${Object.keys(dd).sort((a, b) => a - b).map(d => d + ':' + dd[d]).join(' ')} · 10라운드 안 적 머리에 죽음 \${pct(xs.filter(x => x.rammed10).length, xs.length)} · 20라운드 안 몸(이 턴부터 태어난 자손 포함) 잃음 \${pct(xs.filter(x => x.bodyLost20).length, xs.length)} · 20라운드 안 탈출 분열 \${pct(xs.filter(x => x.esc20).length, xs.length)} · KX 지도 밖 \${xs.filter(x => !x.onKx).length}턴\`; }
  return \`턴 \${xs.length} · 설계 상황(r430 뒤, 더 긴 우리 머리가 맨해튼 5 안) \${pct(xs.filter(x => x.sit).length, xs.length)} (기준 모두) · r430 뒤 \${pct(xs.filter(x => x.r >= 430).length, xs.length)} · 10라운드 뒤 몸 생존 \${pct(xs.filter(x => x.alive10).length, xs.length)} · 끝까지 몸 생존 \${pct(xs.filter(x => x.aliveEnd).length, xs.length)}\`;
}
function caseLine11(x, where) {
  return \`\${where}: 진주 (\${x.px},\${x.py}) \${x.drop ? '사망 진주' : x.present ? '자연 진주' : '이미 없음'}, 곁의 더 긴 아군 \${x.nBeside}마리 → \${x.side === 'us' ? (x.eatSelf ? '표식한 드래곤이 먹음' : x.eatBeside ? '곁의 더 긴 아군이 먹음' : x.eatLonger ? '다른 더 긴 우리 드래곤이 먹음' : '다른 우리 드래곤이 먹음') : x.side === 'them' ? '상대가 먹음' : '아무도 안 먹음'}\${x.delay !== null ? \` (\${x.delay}라운드 뒤)\` : ''}, 표식 \${x.turns}턴\`;
}
function stack11Section(A, B, opts) {
  const L = [];
  const has = S => [...S11_KINDS].some(k => (S.by[k] || []).length);
  if (!has(A) && !(B && has(B)) && !opts.endgame) return L;
  const P = [['이번', A]].concat(B ? [['비교', B]] : []);
  const G = S => (S.s11 || []).filter(g => !g.err);
  const r5 = S => G(S).filter(g => g.kind === 'r500');                                   // 500-round maps, all games
  const full = S => r5(S).filter(g => g.full);                                            // ... that reached r500 with a final king
  const kxf = S => full(S).filter(g => S11_KX_MAPS.has(g.map));                          // ... on kx's maps
  const sb = (g, i, bs = [0, 1, 2, 3]) => bs.reduce((a, b) => a + g.dec[b][i], 0);
  const mn = (gs, f) => gs.length ? f1(gs.reduce((a, g) => a + f(g), 0) / gs.length) : '–';
  const mn2 = (gs, f) => gs.length ? (gs.reduce((a, g) => a + f(g), 0) / gs.length).toFixed(2) : '–';
  const expo = (gs, bs) => { let n = 0, k = 0; for (const g of gs) for (const b of bs) { n += g.env[b][0]; k += g.env[b][2]; } return n ? \`\${pct(k, n)} (\${k}/\${n}턴, \${gs.length}판)\` : '–'; };
  const rec = (S, k) => S.by[k] || [];
  L.push('## stack11: 끝판 왕 — 모이기 물러서기(gh), 왕 떼기(kx), 끝판 창도 왕 부류에게(lwk)', '');
  L.push('- 기준값은 \`research/experiments/cand-stack11.md\`(23:04–23:06, 로컬 발동 수치를 보기 전)에서, 상위권·우리 값은 \`research/observations/endgame-king.md\`(1–5절, 7절)에서 왔다. gh 2, kx 2, lwk 2와 가설 수준 지표는 그 연구의 추출기(\`exp/endgame-king/extract.js\` analyse)를 같은 기보에 돌려 잰다. "500형 전부"는 500라운드형 모든 판, "500형 끝까지"는 500라운드까지 가고 최종 왕이 있는 판, "KX 지도"는 그 가운데 Schooltime·Slithery Fight·Trauma·Autarky다. 판당의 분모는 그 모집단의 우리 팀-경기다.', '');
  L.push('### 게이트 (기능 적용)', '');
  L.push(\`| 기능 | 지표 | 기준 | \${P.map(p => p[0]).join(' | ')} |\`, \`|---|---|---|\${P.map(() => '---|').join('')}\`);
  const row = (f, name, crit, fn) => L.push(\`| \${f} | \${name} | \${crit} | \${P.map(p => fn(p[1])).join(' | ')} |\`);
  row('gh', '발동: gh 턴(판당) · ghd 진주', '–', S => \`\${rec(S, 'gh').length} (\${f1(rec(S, 'gh').length / Math.max(1, S.games))}) · \${rec(S, 'ghd').length}\`);
  row('gh', '1. 설계 상황: gh 턴에 팀 최장(기보, 이 드래곤 아님)이 맨해튼 6 안', '≥95%', S => { const xs = rec(S, 'gh'); return \`\${pct(xs.filter(x => x.sit).length, xs.length)} (이 드래곤이 팀 최장 \${xs.filter(x => x.selfKing).length}턴)\`; });
  row('gh', '1. 설계 상황: ghd 진주가 실제 사망 진주(표식 때 기보)', '≥95%', S => { const xs = rec(S, 'ghd'); return \`\${pct(xs.filter(x => x.drop).length, xs.length)} (\${xs.length}개)\`; });
  row('gh', '2. 즉시 효과 A: 가로채기 몫(r300 뒤 대상이 그때 계보인 표식 먹이의 진주를 계보 밖 우리 드래곤이 먹음; 500형 전부)', '≤20% (stack5–8 26–35%, merge2 20%)', S => {
    let d = 0, o = 0, n = 0; for (const g of r5(S)) for (const v of g.conv) if (v[6]) { n++; d += v[2]; o += v[4]; } return \`\${pct(o, d)} (\${o}/\${d}개, 먹이 \${n}번)\`; });
  row('gh', '3. 즉시 효과 B: ghd 진주를 곁의 더 긴 아군이 먹음', '≥70%', S => { const dr = rec(S, 'ghd').filter(x => x.drop); return \`\${pct(dr.filter(x => x.eatBeside).length, dr.length)} (\${dr.length}개; 우리 팀 \${pct(dr.filter(x => x.side === 'us').length, dr.length)}, 상대 \${pct(dr.filter(x => x.side === 'them').length, dr.length)})\`; });
  row('kx', '발동: kx 턴(KX 지도 판당)', '–', S => { const xs = rec(S, 'kx'), ng = new Set(xs.map(x => x.game)).size; return \`\${xs.length} (\${f1(xs.filter(x => x.onKx).length / Math.max(1, G(S).filter(g => S11_KX_MAPS.has(g.map)).length || 1))}; 발동한 판 \${ng})\`; });
  row('kx', '1. 설계 상황: kx 턴이 그 순간 팀 최장(기보: 더 긴 우리 드래곤 없음)이고 적 머리 맨해튼 7 안', '≥90%', S => { const xs = rec(S, 'kx'); return \`\${pct(xs.filter(x => x.sit).length, xs.length)} (팀 최장 \${pct(xs.filter(x => x.longest).length, xs.length)} · 적 머리 7 안 \${pct(xs.filter(x => x.eD <= 7).length, xs.length)}; 질량 장부 왕 \${pct(xs.filter(x => x.sitLk).length, xs.length)})\`; });
  row('kx', '2. 즉시 효과: KX 지도 계보 드래곤(길이 ≥8) r300–399 턴의 적 머리 6칸 안 몫(500형 끝까지)', '≤35% (stack5–7 52%, 승자 32%)', S => expo(kxf(S), [0, 1]));
  row('kx', '2. 즉시 효과: 같은 값 r400–499', '≤22% (stack5–7 32%, 승자 21%)', S => expo(kxf(S), [2, 3]));
  row('lwk', '발동: lwk 턴(판당)', '–', S => \`\${rec(S, 'lwk').length} (\${f1(rec(S, 'lwk').length / Math.max(1, S.games))})\`);
  row('lwk', '1. 설계 상황: r430 뒤이고 더 긴 우리 머리가 맨해튼 5 안(기보)', '모두', S => { const xs = rec(S, 'lwk'); return \`\${pct(xs.filter(x => x.sit).length, xs.length)} (r430 뒤 \${pct(xs.filter(x => x.r >= 430).length, xs.length)})\`; });
  row('lwk', '2. 즉시 효과: r430 뒤 feed의 대상이 그때 계보 · 떨군 진주 → 계보(500형 전부)', '≥55% · ≥45% (stack5–7 37% · 34%)', S => {
    let n = 0, t = 0, d = 0, l = 0; for (const g of r5(S)) for (const v of g.conv) if (v[0] === 'feed' && v[1] >= 430) { n++; t += v[6]; d += v[2]; l += v[3]; } return \`\${pct(t, n)} (\${t}/\${n}) · \${pct(l, d)} (\${l}/\${d}개)\`; });
  L.push('');
  L.push('### kx 2의 지도별 값 (계보 드래곤 길이 ≥8의 턴 가운데 적 머리 맨해튼 6 안; 500형 끝까지)', '');
  L.push(\`| 지도 | 구간 | 상위권 승자 (연구 T5b, r300–499) | \${P.map(p => p[0]).join(' | ')} |\`, \`|---|---|---|\${P.map(() => '---|').join('')}\`);
  const T5B = { Schooltime: '19%', 'Slithery Fight': '17%', Trauma: '17%', Autarky: '22%', Portals: '49% (참고: 벽 너머)' };
  for (const m of ['Schooltime', 'Slithery Fight', 'Trauma', 'Autarky', 'Portals']) for (const [lab, bs] of [['r300–399', [0, 1]], ['r400–499', [2, 3]]])
    L.push(\`| \${m} | \${lab} | \${T5B[m]} | \${P.map(p => expo(full(p[1]).filter(g => g.map === m), bs)).join(' | ')} |\`);
  L.push('');
  L.push('### kx 턴: 진짜 왕(기보에서 더 긴 우리 드래곤 없음) 대 지역 왕(더 긴 우리 드래곤이 있음) (코디네이터 요청 23:58; 관찰)', '');
  L.push(\`| 풀 | 구분 | 턴 | 적 머리 맨해튼 6 안: 차례 시작 · 움직인 뒤 | 움직인 뒤 더 멂 | 10라운드 안 적 머리에 죽음 | 20라운드 안 몸 잃음 · 탈출 분열 | 그 턴에 최종 왕 계보 · 끝내 계보 |\`, '|---|---|---|---|---|---|---|---|');
  for (const [pn, S] of P) for (const [cn, f] of [['진짜 왕', x => x.longest], ['지역 왕', x => !x.longest]]) { const xs = rec(S, 'kx').filter(f), c = g => xs.filter(g).length;
    L.push(\`| \${pn} | \${cn} | \${xs.length} | \${pct(c(x => x.eD <= 6), xs.length)} · \${pct(c(x => x.eDp <= 6), xs.length)} | \${pct(c(x => x.away), xs.length)} | \${pct(c(x => x.rammed10), xs.length)} | \${pct(c(x => x.bodyLost20), xs.length)} · \${pct(c(x => x.esc20), xs.length)} | \${pct(c(x => x.lineNow), xs.length)} · \${pct(c(x => x.onLine), xs.length)} |\`); }
  L.push('');
  L.push('### 가설 수준 지표 (관찰; 연구 7절)', '');
  L.push(\`| 기능 | 지표 | 기준 | 상위권 승자 · stack5–7 (연구) | \${P.map(p => p[0]).join(' | ')} |\`, \`|---|---|---|---|\${P.map(() => '---|').join('')}\`);
  const hrow = (f, name, crit, ref, fn) => L.push(\`| \${f} | \${name} | \${crit} | \${ref} | \${P.map(p => fn(p[1])).join(' | ')} |\`);
  hrow('gh', '계보가 r300–499에 먹은 우리 희생 진주(판당; 500형 끝까지 / KX 지도)', '≥9.3', '25.8 · 8.3', S => \`\${mn(full(S), g => sb(g, 1))} / \${mn(kxf(S), g => sb(g, 1))}\`);
  hrow('gh', '모이기 창(r340–429) feed(판당; 500형 전부) · 발동 라운드 중앙', '≥2.0', '– · 2.4', S => { const gs = r5(S), rs = []; let n = 0; for (const g of gs) for (const v of g.conv) if (v[0] === 'feed' && v[1] >= 340 && v[1] < 430) { n++; rs.push(v[1]); } rs.sort((a, b) => a - b); return \`\${gs.length ? f1(n / gs.length) : '–'} · \${rs.length ? rs[Math.floor(rs.length / 2)] : '–'}\`; });
  hrow('gh', '길이 ≥8 우리 드래곤의 아군 머리 사망 r340–399(판당; r340까지 간 500형)', '늘지 않음', '– · 0.08 (r350–399)', S => { const gs = r5(S).filter(g => g.rounds > 340); let n = 0; for (const g of gs) for (const q of g.kd) if (q[0] >= 340 && q[0] < 400 && q[1] >= 8 && q[2] === 5) n++; return gs.length ? (n / gs.length).toFixed(2) : '–'; });
  hrow('gh', '(참고) 뿌리 모이기 에피소드 가운데 가족의 마지막 죽음이 아군 머리(500형 전부)', '–', '–', S => { let n = 0, a = 0; for (const g of r5(S)) { n += g.gathRoot; a += g.gathAllyHead; } return \`\${pct(a, n)} (\${a}/\${n})\`; });
  hrow('gh', '(부작용) 뿌리 모이기 에피소드 가족의 끝: 계보 / 계보 밖 삶 / 표식 먹이 / 다른 희생 / 다른 죽음(500형 전부) · 첫 g 표식에서 표식 먹이까지 라운드 중앙', '–', '– · 11% / 21% / 47% / 0% / 21%', S => { const f = [0, 0, 0, 0, 0], dl = []; let n = 0; for (const g of r5(S)) { for (let i = 0; i < 5; i++) f[i] += g.gathFate[i]; n += g.gathRoot; dl.push(...g.gathFedDelay); } dl.sort((a, b) => a - b); return \`\${f.map(v => pct(v, n)).join(' / ')} (\${n}) · \${dl.length ? dl[Math.floor(dl.length / 2)] : '–'}\`; });
  hrow('kx', 'r340 뒤 팀 최장(길이 ≥8)을 적 머리에 잃은 판(500형 끝까지 / KX 지도)', '≤7%', '5% · 13% (stack5–8)', S => [full(S), kxf(S)].map(gs => { const h = gs.filter(g => g.kd.some(q => q[0] >= 340 && q[3] && (q[2] === 2 || q[2] === 3))).length; return \`\${pct(h, gs.length)} (\${h}/\${gs.length})\`; }).join(' / '));
  hrow('kx', '계보의 우리 희생 진주 r300–499(판당; KX 지도)', '≥10', '25.8 · 8.3', S => mn(kxf(S), g => sb(g, 1)));
  hrow('kx', '표식 먹이(feed·conv, r300 뒤) 가운데 대상이 그때 계보인 몫(500형 전부 / KX 지도)', '유지', '– · 64% (feed r340–429)', S => [r5(S), r5(S).filter(g => S11_KX_MAPS.has(g.map))].map(gs => { let n = 0, t = 0; for (const g of gs) for (const v of g.conv) { n++; t += v[6]; } return \`\${pct(t, n)} (\${n})\`; }).join(' / '));
  hrow('kx', '왕 성장 r300→500(라운드당; 500형 끝까지 / KX 지도)', '≥0.12', '0.18 · 0.09', S => [full(S), kxf(S)].map(gs => { const U = gs.filter(g => g.L300 !== null); return U.length ? (U.reduce((a, g) => a + (g.king - g.L300) / 200, 0) / U.length).toFixed(2) : '–'; }).join(' / '));
  hrow('kx', '부작용: 계보의 자연 진주 r300–499(판당; KX 지도)', '≥11', '11.7 · 12.4', S => mn(kxf(S), g => sb(g, 0)));
  hrow('kx', '부작용: 계보의 분열 손실(떼어 냄 + 넘김) r300–499(판당; KX 지도)', '늘지 않음(≤5.9)', '6.6 · 5.9', S => mn(kxf(S), g => sb(g, 5) + sb(g, 6)));
  hrow('lwk', '계보의 r450–499 우리 희생 진주(판당; 500형 끝까지)', '≥2.6', '6.4 · 2.1', S => mn(full(S), g => g.dec[3][1]));
  hrow('lwk', '끝에 계보 밖에서 산 길이 ≥8 드래곤의 끝 길이 합(판당; 500형 끝까지)', '늘지 않음', '–', S => mn(full(S), g => g.off8));
  L.push('', \`- 판 수(500형 전부 / 500형 끝까지 / KX 지도): \${P.map(p => \`\${p[0]} \${r5(p[1]).length} / \${full(p[1]).length} / \${kxf(p[1]).length}\`).join(' · ')}. 추출기 재구성 점검이 0이 아닌 판: \${P.map(p => \`\${p[0]} \${G(p[1]).filter(g => g.chkBad).length}\`).join(' · ')}; 계산 오류: \${P.map(p => \`\${p[0]} \${(p[1].s11 || []).filter(g => g.err).length}\`).join(' · ')}.\`, '');
  L.push('### 부작용 (관찰; 판정에 쓰지 않음)', '');
  L.push(\`| 항목 | \${P.map(p => p[0]).join(' | ')} |\`, \`|---|\${P.map(() => '---|').join('')}\`);
  const srow = (name, fn) => L.push(\`| \${name} | \${P.map(p => fn(p[1])).join(' | ')} |\`);
  srow('kx 먹이 찾기: 계보 드래곤 턴당 5칸 안 자연 진주(r300–499; KX 지도) · 계보의 자연 진주(판당)', S => { let n = 0, p = 0; for (const g of kxf(S)) for (let b = 0; b < 4; b++) { n += g.env[b][0]; p += g.env[b][4]; } return \`\${n ? (p / n).toFixed(2) : '–'} · \${mn(kxf(S), g => sb(g, 0))}\`; });
  srow('kx 가두기: r300 뒤 적이 계보 드래곤의 몸에 막혀 죽은 수(판당; 몸에 박음 + 몸 곁에 갇힘; KX 지도 / 500형 전부) · 계보가 먹은 적 사망 진주 r300–499(판당; KX 지도)', S => {
    const f = gs => gs.length ? f1(gs.reduce((a, g) => a + g.bkLine + g.trLine, 0) / gs.length) : '–'; const kg = r5(S).filter(g => S11_KX_MAPS.has(g.map)); return \`\${f(kg)} / \${f(r5(S))} · \${mn(kxf(S), g => sb(g, 3))}\`; });
  srow('(참고) r300 뒤 적이 우리 몸에 막혀 죽은 수 전체(판당; 500형 전부): 박음 · 갇힘', S => { const gs = r5(S); return gs.length ? \`\${f1(gs.reduce((a, g) => a + g.bkAll, 0) / gs.length)} · \${f1(gs.reduce((a, g) => a + g.trAll, 0) / gs.length)}\` : '–'; });
  srow('kx 막다른 곳·포털: 팀 최장(길이 ≥8)의 죽음 r300 뒤(판당; 500형 전부 / KX 지도): 적 머리 · 갇힘 · 아군 머리 · 희생 · 그 밖', S => [r5(S), r5(S).filter(g => S11_KX_MAPS.has(g.map))].map(gs => { const c = [0, 0, 0, 0, 0]; for (const g of gs) for (const q of g.kd) if (q[0] >= 300 && q[1] >= 8 && q[3]) c[q[2] === 2 || q[2] === 3 ? 0 : q[2] === 1 ? 1 : q[2] === 5 ? 2 : q[2] === 0 ? 3 : 4]++; return gs.length ? c.map(v => (v / gs.length).toFixed(2)).join(' · ') : '–'; }).join(' / '));
  srow('kx 포털: 그 순간 팀 최장(길이 ≥8)의 r300 뒤 포털 통과(판당; KX 지도) · 몸 3라운드 생존 · 드래곤 자체 3라운드 생존 · 넘는 걸음에서 죽음', S => { const xs = (S.by.portal || []).filter(x => x.r >= 300 && x.cx && x.cx.king === 1 && x.L >= 8 && S11_KX_MAPS.has(x.map)), ng = Math.max(1, G(S).filter(g => S11_KX_MAPS.has(g.map)).length); return \`\${f1(xs.length / ng)} (\${xs.length}) · \${pct(xs.filter(x => x.alive3).length, xs.length)} · \${pct(xs.filter(x => x.self3).length, xs.length)} · \${xs.filter(x => x.stepDeath).length}\`; });
  srow('kx: 계보 드래곤 턴의 적 머리 3칸 안 몫 r300–499(KX 지도)', S => { let n = 0, k = 0; for (const g of kxf(S)) for (let b = 0; b < 4; b++) { n += g.env[b][0]; k += g.env[b][1]; } return n ? pct(k, n) : '–'; });
  srow('길이 ≥8 우리 드래곤의 죽음 r300–499(판당; 500형 전부): 적 머리 · 아군 머리 · 갇힘 · 희생', S => { const gs = r5(S).filter(g => g.rounds > 300); const c = [0, 0, 0, 0]; for (const g of gs) for (const q of g.kd) if (q[0] >= 300 && q[1] >= 8) { if (q[2] === 2 || q[2] === 3) c[0]++; else if (q[2] === 5) c[1]++; else if (q[2] === 1) c[2]++; else if (q[2] === 0) c[3]++; } return gs.length ? c.map(v => (v / gs.length).toFixed(2)).join(' · ') : '–'; });
  srow('표식 먹이 r300 뒤(판당; 500형 전부): conv · 모이기 창 feed · 끝판 창 feed', S => { const gs = r5(S), c = [0, 0, 0]; for (const g of gs) for (const v of g.conv) { if (v[0] === 'conv') c[0]++; else if (v[1] < 430) c[1]++; else c[2]++; } return gs.length ? c.map(v => f1(v / gs.length)).join(' · ') : '–'; });
  srow('grab 표적 진주(판당) · 그중 우리가 먹음', S => { const xs = rec(S, 'grab'), dr = xs.filter(x => x.drop); return \`\${f1(xs.length / Math.max(1, S.games))} · \${pct(dr.filter(x => x.side === 'us').length, dr.length)}\`; });
  L.push('');
  return L;
}
`;

// ---------------------------------------------------------------------------------------------------------------
const edits = [
  ['\n\'use strict\';\nconst fs = require(\'fs\'), path = require(\'path\'), cp = require(\'child_process\');\n', '\n' + HEADER + '\'use strict\';\nconst fs = require(\'fs\'), path = require(\'path\'), cp = require(\'child_process\');\n'],
  ['const S9_LSPLIT_END = 340;', CONSTS + 'const S9_LSPLIT_END = 340;'],
  ['      else f.extra.push(t);\n', PARSE + '      else f.extra.push(t);\n'],
  ['  const S10 = { opp: [], xch: [], oppNow: new Map(), xPend: new Map() };\n', '  const S10 = { opp: [], xch: [], oppNow: new Map(), xPend: new Map() };\n' + STATE],
  ['      if (NB) { // stack8: the named pearl of an Fp / cl / ce label', IND + '      if (NB) { // stack8: the named pearl of an Fp / cl / ce label'],
  ['          if (t.tg) made.push({ k: \'tg\', ...base, tgx: t.tg === \'tgx\' ? 1 : 0 });', ACT + '          if (t.tg) made.push({ k: \'tg\', ...base, tgx: t.tg === \'tgx\' ? 1 : 0 });'],
  ['    death(d, rec, idx, other, r, c) {\n      if (d.team !== us) return;\n', '    death(d, rec, idx, other, r, c) {\n' + DEATH + '      if (d.team !== us) return;\n'],
  ['      case \'trade\': {\n        x.ex = x.died && x.died.cause === 3 ? 1 : 0;', EFFECTS + '      case \'trade\': {\n        x.ex = x.died && x.died.cause === 3 ? 1 : 0;'],
  ['  return { s10: s10o, t5: t5o,', S11BLOCK + '  return { s10: s10o, t5: t5o,'],
  ['    s9 };', '    s9, s11 };'],                                                                  // stack11: the endgame indicators (task.endgame)
  ['  S.s9 = games.filter(g => g.s9)', '  S.s11 = games.filter(g => g.s11).map(g => ({ ...g.s11, map: g.map, set: g.set, game: g.game }));                               // stack11\n  S.s9 = games.filter(g => g.s9)'],
  ['ORDER.splice(0, 0, \'lsplit\', \'covw\');', 'ORDER.splice(0, 0, \'lsplit\', \'covw\');' + `
Object.assign(LABEL, { gh: '모이기 물러서기 (gh, stack11; 턴 단위)', ghd: '더 긴 아군 곁 새 사망 진주 양보 (ghd, stack11; 드래곤·진주 단위)', kx: '왕 떼기 (kx, stack11; 턴 단위)', lwk: '끝판 창 왕 부류에게만 (lwk, stack11; 턴 단위)' }); // stack11
ORDER.splice(0, 0, 'gh', 'ghd', 'kx', 'lwk');                                                        // stack11`],
  ['    case \'lnt\': case \'lntv\': case \'kint\': return effectLine10(k, xs);', '    case \'gh\': case \'ghd\': case \'kx\': case \'lwk\': return effectLine11(k, xs);                     // stack11\n    case \'lnt\': case \'lntv\': case \'kint\': return effectLine10(k, xs);'],
  ['    case \'lnt\': case \'lntv\': case \'kint\': return caseLine10(x, where, dd);', '    case \'ghd\': return caseLine11(x, where);                                                             // stack11\n    case \'lnt\': case \'lntv\': case \'kint\': return caseLine10(x, where, dd);'],
  ['  L.push(\'\');\n  L.push(\'## 요약\', \'\');', `  if ([...S11_KINDS].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length)))              // stack11
    L.push(\`- stack11의 "의도대로": 더 긴 아군 곁 새 사망 진주 양보(ghd)=그 진주를 곁의 더 긴 아군(첫 표식 때 표식한 드래곤보다 길고 머리가 진주에서 맨해튼 2 안)이 먹음. gh·kx·lwk는 턴 단위 기록이라 "의도대로"를 매기지 않는다(설계 상황은 효과 줄). 게이트(가로채기, 노출, 끝판 창 대상 적중), 가설 수준 지표(끝판 왕 연구의 정의), 부작용은 맨 뒤 stack11 절.\`);
  L.push('');
  L.push('## 요약', '');`],
  ['  L.push(...stack9Section(A, B, opts));', '  L.push(...stack9Section(A, B, opts));\n  L.push(...stack11Section(A, B, opts));                                                                 // stack11'],
  ['  let rA = await runAll(sup9 ? withSup(tA) : tA, jobs);\n', `  const eg11 = argv.includes('--endgame'), withEg = ts => ts.map(t => ({ ...t, endgame: true }));       // stack11: the endgame indicators
  const flag11 = (ts, s, e) => { const o = s ? withSup(ts) : ts; return e ? withEg(o) : o; };              // stack11
  let rA = await runAll(flag11(tA, sup9, eg11), jobs);
`],
  ['  if (has9) rA = await runAll(withSup(tA), jobs);\n  const rB = tB ? await runAll(sup9 || has9 ? withSup(tB) : tB, jobs) : null;\n',
   `  const has11 = !eg11 && rA.games.some(g => g.recs.some(x => S11_KINDS.has(x.k)));                        // stack11: pool A carries stack11 tags
  if (has9 || has11) rA = await runAll(flag11(tA, sup9 || has9, eg11 || has11), jobs);
  const rB = tB ? await runAll(flag11(tB, sup9 || has9, eg11 || has11), jobs) : null;
`],
  ['    stack9: argv.includes(\'--stack9\') });', '    stack9: argv.includes(\'--stack9\'), endgame: argv.includes(\'--endgame\') });'], // stack11 --endgame
  ['module.exports = { parseInd, analyse, summarise, report };', SECTION + 'module.exports = { parseInd, analyse, summarise, report };'],
];

let s = fs.readFileSync(file, 'utf8'), bad = 0;
for (const [a, b] of edits) {
  const n = s.split(a).length - 1;
  if (n !== 1) { console.error(`anchor found ${n} times: ${JSON.stringify(a.slice(0, 100))}`); bad++; continue; }
  s = s.replace(a, () => b);
}
if (bad) { console.error(`${bad} anchors failed; nothing written`); process.exit(1); }
fs.writeFileSync(file, s);
console.log(`applied ${edits.length} edits to ${path.relative(process.cwd(), file)}`);
