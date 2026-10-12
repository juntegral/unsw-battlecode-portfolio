#!/usr/bin/env node
// classes.js — stage 2 of the territory study: sort events and games into classes over the whole population, report
// every class size, and select the replays for close reading by a fixed rule (stage 3, film.js).
// usage (repository root): node --max-old-space-size=12000 exp/territory-analysis/classes.js [--top top-all] [--out exp/territory-analysis/classes]
//
// Classes
//   Raid pattern (one deep raid episode = a dragon 3+ steps inside the other territory; extract.js), by outcome then yield:
//     caught   died by defender contact (rammed by it, rammed it, hit its body, or trapped against its body)
//     selfloss died otherwise inside (sacrifice, trapped by own/ally body or kelp, ally collision)
//     end      still inside when the game ended
//     return0  went back out having eaten no natural pearl inside
//     return+  went back out having eaten 1+ natural pearls inside
//   crossed with the raider's length at entry S (2-3) / M (4-7) / B (8+).
//   Defence response (the same episodes seen from the defending team):
//     unattended no defender head within 6 steps at the raid's start and no contact later
//     nearby     a defender within 6 at the start, never within 1
//     contact    a defender head came within 1, the raider did not die by contact
//     caught     the raider died by defender contact
//   Coverage state (one team at r100 / r200 / r300): own-territory Voronoi share (capacity-weighted) >= 99% saturated,
//     90-99% held, 50-90% contested, < 50% lost.
//   Game loss pattern (one team-game; the primary set is merge2): disconnected (>= 90% of own-territory spawns have no
//     enemy path), held (enemy ate < 20% of own-territory spawns), flooded (>= 50% and >= 5 enemy heads inside per
//     round on average), leaky (the rest).
// Selection rule for close reading (stage 3), per selected group and class:
//   representative = among a deterministic hash sample of up to 60 members, the one closest to the class medians of
//     (duration, natural pearls, entry length) [raids] or (lost share, enemy heads inside per round) [games];
//   extreme = the member with the most natural pearls eaten inside (ties: the longest) [raids] or the most own-territory
//     pearls lost [games].
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const S = require('./summarise.js');
const { EI, CI, contactKill, SETS } = S;
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const OUT = path.resolve(ROOT, opt('out', 'exp/territory-analysis/classes'));
const TOPNAME = opt('top', 'top-all');

const RAID = ['caught', 'selfloss', 'end', 'return0', 'return+'];
const RAIDK = { caught: '수비에 잡힘', selfloss: '스스로 죽음', end: '판 끝까지 체류', return0: '빈손 귀환', 'return+': '먹고 귀환' };
const SIZE = ['S', 'M', 'B'];
const DEF = ['unattended', 'nearby', 'contact', 'caught'];
const DEFK = { unattended: '무방비(6걸음 안 수비 없음)', nearby: '곁에 있음(접촉 없음)', contact: '접촉(못 잡음)', caught: '잡음' };
const COV = ['saturated', 'held', 'contested', 'lost'];
const COVK = { saturated: '≥99%', held: '90–99%', contested: '50–90%', lost: '<50%' };
const GAME = ['disconnected', 'held', 'leaky', 'flooded'];
const GAMEK = { disconnected: '이어지지 않음', held: '지킴(<20%)', leaky: '샘(20–50%, 또는 침입 적음)', flooded: '범람(≥50%, 침입 ≥5)' };
const raidClass = e => e[EI.exit] === 1 ? (contactKill(e) ? 0 : 1) : e[EI.exit] === 2 ? 2 : e[EI.nat] > 0 ? 4 : 3;
const sizeOf = L => L <= 3 ? 0 : L <= 7 ? 1 : 2;
const defClass = e => contactKill(e) ? 3 : e[EI.dDefMin] <= 1 ? 2 : e[EI.nDef6] > 0 ? 1 : 0;
const covClass = v => v >= 0.99 ? 0 : v >= 0.9 ? 1 : v >= 0.5 ? 2 : 3;
function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const zeros = n => new Array(n).fill(0);
const kindOf = m => S.ELIM.includes(m) ? 'elim' : S.R500.includes(m) ? 'r500' : 'other';
const hMed = S.hMed;

// groups that get replay selections: reference (top winners raiding / defending) and primary (the elite against merge2)
const SELECT_RAID = ['TW', 'X-merge2'];   // raider groups
const SELECT_DEF = ['TW', 'merge2'];      // defender groups
const SELECT_GAME = ['merge2'];

(async () => {
  const raid = {}, def = {}, cov = {}, game = {}, sample = {}, extreme = {}, hist = {};
  const bump = (o, k, n, vals) => { if (!o[k]) o[k] = zeros(n); for (let i = 0; i < n; i++) o[k][i] += vals[i] || 0; };
  const gameRows = [];
  const files = [[path.join(S.CACHE, TOPNAME + '.jsonl.gz'), 'top']];
  for (const s of Object.keys(SETS)) files.push([path.join(S.CACHE, 'online-' + s + '.jsonl.gz'), 'online']);
  const inactive = T => T.splits <= 3 && T.sonar === 0;
  const nGames = { top: 0, online: 0 };
  for (const [file, src] of files) {
    await S.forEachGame(file, g => {
      if (src === 'top') { if (inactive(g.A) || inactive(g.B) || g.A.faults >= 3 || g.B.faults >= 3 || !g.winner) return; nGames.top++; } else nGames.online++;
      const kind = kindOf(g.map);
      const mapKey = g.map === 'Prisoners Dilemma' ? (g.variant.tag === '10' ? 'PD10' : 'PD6') : (g.variant.tag === 'b' ? g.map + ' b' : g.map);
      const us = src === 'online' ? (g.us === 'A' ? 0 : 1) : -1, bot = src === 'online' ? SETS[g.set] : null;
      const grpOf = ti => src === 'top' ? ((ti === 0 ? 'A' : 'B') === g.winner ? 'TW' : 'TL') : (ti === us ? bot : 'X-' + bot);
      const nameOf = ti => ti === 0 ? g.teamA : g.teamB;
      const where = { key: g.key, src, set: g.set, gameId: g.gameId, battleId: g.battleId, map: mapKey, kind };
      // raid episodes
      for (const e of g.E) {
        if (e[EI.dmax] < 3) continue;
        const ti = e[EI.ti], rg = grpOf(ti), dg = grpOf(1 - ti);
        const rc = raidClass(e), sz = sizeOf(e[EI.L0]), dc = defClass(e), dur = e[EI.r1] - e[EI.r0] + 1;
        bump(raid, [rg, kind, RAID[rc], SIZE[sz]].join('|'), 5, [1, e[EI.nat], e[EI.fnt], dur, e[EI.born]]);
        bump(raid, [rg, kind, RAID[rc], '*'].join('|'), 5, [1, e[EI.nat], e[EI.fnt], dur, e[EI.born]]);
        bump(def, [dg, kind, DEF[dc]].join('|'), 4, [1, e[EI.nat], dur, e[EI.fnt]]);
        for (const [grp, cls, sel] of [[rg, 'raid:' + RAID[rc], SELECT_RAID.includes(rg)], [dg, 'def:' + DEF[dc], SELECT_DEF.includes(dg)]]) {
          if (!sel) continue;
          const hk = grp + '|' + kind + '|' + cls;
          const h = hist[hk] || (hist[hk] = { dur: zeros(62), nat: zeros(21), L0: zeros(22) });
          h.dur[Math.min(61, dur)]++; h.nat[Math.min(20, e[EI.nat])]++; h.L0[Math.min(21, e[EI.L0])]++;
          const cand = { ...where, raider: nameOf(ti), defender: nameOf(1 - ti), raiderTi: ti, grp, cls, id: e[EI.id], r0: e[EI.r0], r1: e[EI.r1], L0: e[EI.L0], Lmax: e[EI.Lmax], nat: e[EI.nat], fnt: e[EI.fnt], dur,
            cause: e[EI.cause], exit: e[EI.exit], born: e[EI.born], dDef0: e[EI.dDef0], dDefMin: e[EI.dDefMin], nDef6: e[EI.nDef6], dmax: e[EI.dmax], hash: hash32(g.key + ':' + e[EI.id] + ':' + e[EI.r0]) };
          const sp = sample[hk] || (sample[hk] = []);
          sp.push(cand); if (sp.length > 120) { sp.sort((a, b) => a.hash - b.hash); sp.length = 60; }
          const ex = extreme[hk];
          if (!ex || cand.nat > ex.nat || (cand.nat === ex.nat && cand.dur > ex.dur)) extreme[hk] = cand;
        }
      }
      // coverage states and game loss patterns
      for (const ti of [0, 1]) {
        const grp = grpOf(ti), s = S.teamSummary(g, ti), o = S.teamSummary(g, 1 - ti);
        for (const r of [100, 200, 300]) {
          const c = s.C.find(c => c[0] === r); if (!c || c[CI.units] === 0 || g.rounds <= r + 99) continue;
          const cc = covClass(c[CI.vorOwn] / s.capOwn);
          let sp = 0, en = 0; for (const i of [r / 50, r / 50 + 1]) { sp += s.win50[i][0]; en += s.win50[i][2]; }
          bump(cov, [grp, kind, r, COV[cc]].join('|'), 4, [1, sp, en, c[CI.units]]);
        }
        const lost = s.ownSp ? s.enEat / s.ownSp : 0, noEn = s.ownSp ? s.byD[7][0] / s.ownSp : 1;
        const raiders = o.LOC.en.reduce((a, b) => a + b, 0) / Math.max(1, o.LOC.rounds.reduce((a, b) => a + b, 0));
        const gc = noEn >= 0.9 ? 0 : lost < 0.2 ? 1 : (lost >= 0.5 && raiders >= 5) ? 3 : 2;
        const c100 = s.C.find(c => c[0] === 100);
        bump(game, [grp, kind, GAME[gc]].join('|'), 5, [1, s.enEat, s.ownSp, raiders, c100 ? c100[CI.vorOwn] / s.capOwn : 0]);
        if (SELECT_GAME.includes(grp)) gameRows.push({ ...where, grp, cls: GAME[gc], team: nameOf(ti), opp: nameOf(1 - ti), ti, lost, lostN: s.enEat, ownSp: s.ownSp, raiders, vor100: c100 ? c100[CI.vorOwn] / s.capOwn : NaN,
          units100: c100 ? c100[CI.units] : NaN, win: (ti === 0 ? 'A' : 'B') === g.winner, fLost: s.fSp ? s.fEn / s.fSp : NaN, hash: hash32(g.key) });
      }
    });
  }

  // ---------------------------------------------------------------------------------------------------------------
  const L = [], P = (...a) => L.push(a.join(''));
  const pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
  const f1 = x => Number.isFinite(x) ? x.toFixed(1) : '–';
  const table = (head, rows) => { P('| ' + head.join(' | ') + ' |'); P('|' + head.map((h, i) => i ? '---:' : '---').join('|') + '|'); for (const r of rows) P('| ' + r.join(' | ') + ' |'); P(''); };
  const GROUPS = ['TW', 'TL', ...S.BOTS, ...S.BOTS.map(b => 'X-' + b)];
  P('# 분류와 크기 (exp/territory-analysis/classes.js)', '');
  P(`- 모집단: 상위권 ${nGames.top}판(멈춘 팀·시간 초과 판 제외), 우리 온라인 ${nGames.online}판(12세트, 상위 6팀 + DEV 팀).`, '');
  P('## 1. 침입 유형 (깊은 침입 에피소드 수; 괄호 = 그 유형이 먹은 자연 진주의 몫)', '');
  for (const kind of ['r500', 'elim']) {
    P(`### ${kind === 'r500' ? '500라운드형' : '전멸형'}`, '');
    const rows = [];
    for (const grp of GROUPS) {
      const tot = RAID.reduce((a, c) => a + ((raid[[grp, kind, c, '*'].join('|')] || [0])[0]), 0); if (!tot) continue;
      const natT = RAID.reduce((a, c) => a + ((raid[[grp, kind, c, '*'].join('|')] || [0, 0])[1]), 0);
      const sizes = SIZE.map(sz => RAID.reduce((a, c) => a + ((raid[[grp, kind, c, sz].join('|')] || [0])[0]), 0));
      const bornT = RAID.reduce((a, c) => a + ((raid[[grp, kind, c, '*'].join('|')] || [0, 0, 0, 0, 0])[4]), 0);
      rows.push([grp, tot, ...RAID.map(c => { const v = raid[[grp, kind, c, '*'].join('|')] || [0, 0]; return `${v[0]} (${pc(v[0], tot)}; 진주 ${pc(v[1], natT)})`; }), sizes.map(v => pc(v, tot)).join(' / '), pc(bornT, tot)]);
    }
    table(['침입하는 집단', '에피소드', ...RAID.map(c => RAIDK[c]), '처음 길이 S/M/B', '안에서 태어남'], rows);
  }
  P('## 2. 수비 반응 (받은 깊은 침입 수; 괄호 = 비율, 그 반응 아래 침입자가 먹은 자연 진주의 몫)', '');
  for (const kind of ['r500', 'elim']) {
    P(`### ${kind === 'r500' ? '500라운드형' : '전멸형'}`, '');
    const rows = [];
    for (const grp of GROUPS) {
      const tot = DEF.reduce((a, c) => a + ((def[[grp, kind, c].join('|')] || [0])[0]), 0); if (!tot) continue;
      const natT = DEF.reduce((a, c) => a + ((def[[grp, kind, c].join('|')] || [0, 0])[1]), 0);
      rows.push([grp, tot, ...DEF.map(c => { const v = def[[grp, kind, c].join('|')] || [0, 0]; return `${v[0]} (${pc(v[0], tot)}; 진주 ${pc(v[1], natT)})`; })]);
    }
    table(['수비하는 집단', '받은 침입', ...DEF.map(c => DEFK[c])], rows);
  }
  P('## 3. 덮기 상태 (팀·경기; 괄호 = 다음 100라운드에 상대가 먹은 우리 영토 진주 몫, 평균 드래곤 수)', '');
  for (const kind of ['r500', 'elim']) for (const r of [100, 200, 300]) {
    P(`### ${kind === 'r500' ? '500라운드형' : '전멸형'} r${r}`, '');
    const rows = [];
    for (const grp of GROUPS) {
      const tot = COV.reduce((a, c) => a + ((cov[[grp, kind, r, c].join('|')] || [0])[0]), 0); if (!tot) continue;
      rows.push([grp, tot, ...COV.map(c => { const v = cov[[grp, kind, r, c].join('|')] || [0, 0, 0, 0]; return v[0] ? `${v[0]} (${pc(v[2], v[1])}, ${f1(v[3] / v[0])}u)` : '0'; })]);
    }
    table(['집단', 'N', ...COV.map(c => '보로노이 ' + COVK[c])], rows);
  }
  P('## 4. 경기 단위 영토 손실 유형 (팀·경기; 괄호 = 평균 잃은 진주/판, 평균 상대 침입 수/라운드, 평균 보로노이 r100)', '');
  for (const kind of ['r500', 'elim']) {
    P(`### ${kind === 'r500' ? '500라운드형' : '전멸형'}`, '');
    const rows = [];
    for (const grp of GROUPS) {
      const tot = GAME.reduce((a, c) => a + ((game[[grp, kind, c].join('|')] || [0])[0]), 0); if (!tot) continue;
      rows.push([grp, tot, ...GAME.map(c => { const v = game[[grp, kind, c].join('|')] || [0, 0, 0, 0, 0]; return v[0] ? `${v[0]} (${f1(v[1] / v[0])}, ${f1(v[3] / v[0])}, ${(100 * v[4] / v[0]).toFixed(0)}%)` : '0'; })]);
    }
    table(['집단', 'N', ...GAME.map(c => GAMEK[c])], rows);
  }
  // merge2 game classes by map and opponent
  {
    P('### merge2 경기 유형의 지도·상대 구성 (210판)', '');
    const byC = {}; for (const r of gameRows) (byC[r.cls] = byC[r.cls] || []).push(r);
    const rows = [];
    for (const c of GAME) {
      const rs = byC[c] || []; if (!rs.length) continue;
      const mc = {}, oc = {}; for (const r of rs) { mc[r.map] = (mc[r.map] || 0) + 1; oc[r.opp] = (oc[r.opp] || 0) + 1; }
      rows.push([GAMEK[c], rs.length, Object.entries(mc).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', '), Object.entries(oc).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + v).join(', '), rs.filter(r => r.win).length]);
    }
    table(['유형', '판', '지도', '상대', '우리 승'], rows);
  }

  // ---------------------------------------------------------------------------------------------------------------
  // selection for close reading
  const picks = [];
  const medOf = h => hMed(h);
  for (const [hk, sp] of Object.entries(sample)) {
    const h = hist[hk]; const md = { dur: medOf(h.dur), nat: medOf(h.nat), L0: medOf(h.L0) };
    const n = h.dur.reduce((a, b) => a + b, 0);
    sp.sort((a, b) => a.hash - b.hash); const pool = sp.slice(0, 60);
    const dist = c => Math.abs(c.dur - md.dur) / Math.max(1, md.dur) + Math.abs(c.nat - md.nat) + Math.abs(c.L0 - md.L0) / 2;
    const rep = pool.slice().sort((a, b) => dist(a) - dist(b) || a.hash - b.hash)[0];
    picks.push({ type: 'raid-rep', hk, n, med: md, ...rep });
    const ex = extreme[hk]; if (ex && ex !== rep) picks.push({ type: 'raid-ext', hk, n, med: md, ...ex });
  }
  {
    const byC = {}; for (const r of gameRows) (byC[r.cls] = byC[r.cls] || []).push(r);
    for (const [c, rs] of Object.entries(byC)) {
      const q = (a, p) => { const b = [...a].sort((x, y) => x - y); return b[Math.floor((b.length - 1) * p)]; };
      const md = { lost: q(rs.map(r => r.lost), 0.5), raiders: q(rs.map(r => r.raiders), 0.5) };
      const pool = rs.slice().sort((a, b) => a.hash - b.hash).slice(0, 60);
      const rep = pool.slice().sort((a, b) => (Math.abs(a.lost - md.lost) + Math.abs(a.raiders - md.raiders) / 10) - (Math.abs(b.lost - md.lost) + Math.abs(b.raiders - md.raiders) / 10) || a.hash - b.hash)[0];
      picks.push({ type: 'game-rep', hk: 'merge2|' + c, n: rs.length, med: md, ...rep });
      const ex = rs.slice().sort((a, b) => b.lostN - a.lostN)[0]; if (ex !== rep) picks.push({ type: 'game-ext', hk: 'merge2|' + c, n: rs.length, med: md, ...ex });
    }
  }
  picks.sort((a, b) => a.hk.localeCompare(b.hk) || a.type.localeCompare(b.type));
  P('## 5. 자세히 읽을 기보 (선택 규칙은 파일 머리 참고)', '');
  const ptr = p => p.src === 'top' ? `대전 ${p.battleId} / 경기 ${p.gameId}` : `${p.set} 경기 ${p.gameId}`;
  for (const p of picks) {
    if (p.type.startsWith('raid')) P(`- [${p.hk}, 크기 ${p.n}, 중앙 지속 ${p.med.dur}·진주 ${p.med.nat}·길이 ${p.med.L0}] ${p.type === 'raid-rep' ? '대표' : '극단'}: ${ptr(p)} · ${p.map} · ${p.raider} → ${p.defender} · 드래곤 #${p.id} r${p.r0}–${p.r1} · L${p.L0}→${p.Lmax} · 진주 ${p.nat}(샘 ${p.fnt}) · 깊이 ${p.dmax}`);
    else P(`- [${p.hk}, 크기 ${p.n}, 중앙 잃은 몫 ${(100 * p.med.lost).toFixed(0)}%·침입 ${p.med.raiders.toFixed(1)}] ${p.type === 'game-rep' ? '대표' : '극단'}: ${ptr(p)} · ${p.map} · merge2 vs ${p.opp} · 잃음 ${p.lostN}/${p.ownSp} (${(100 * p.lost).toFixed(0)}%) · 상대 침입 ${p.raiders.toFixed(1)}/라운드 · 보로노이 r100 ${(100 * p.vor100).toFixed(0)}%`);
  }
  fs.writeFileSync(OUT + '.md', L.join('\n') + '\n');
  fs.writeFileSync(OUT + '.json', JSON.stringify({ nGames, raid, def, cov, game, picks }, null, 1));
  console.log(`wrote ${path.relative(ROOT, OUT)}.md/.json; picks ${picks.length}; games top ${nGames.top} online ${nGames.online}`);
})().catch(e => { console.error(e); process.exit(1); });
