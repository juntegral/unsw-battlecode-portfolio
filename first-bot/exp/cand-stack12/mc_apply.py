#!/usr/bin/env python3
# cand-stack12: add the pf (stack12) records, the intake-gap per-game numbers and the stack12 section to a copy of tools/mech_check.js.
# Every edit is an exact-string replacement whose anchor must occur exactly once (a changed base fails loudly).
# usage: python3 exp/cand-stack12/mc_apply.py <base mech_check.js> <out file>
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
edits = []
def E(a, b): edits.append((a, b))

# 1. header
E("""//             growth, the longest lost to an enemy head from r340; enemy deaths into or trapped against our line member's body from r300.
'use strict';""",
"""//             growth, the longest lost to an enemy head from r340; enemy deaths into or trapped against our line member's body from r300.
//   stack12 (research/experiments/cand-stack12.md; study research/observations/intake-gap.md section 13):
//   pf        "pf<n> u<units> L<len> t<target>[ f][ v][ k]": piece-first opening. In r1-99 on the pf maps (Slithery Fight, Schooltime, Trauma,
//             Default, Devil, Queen Of Spades, Trophy; off on Autarky, Prisoners Dilemma, Portals) while the team has fewer units than the layout's
//             target (top winners' r100 mean, <= 56), a dragon of length >= 4 splits off a 2-child, once in 2 rounds, king rule and E1 block off
//             (f = the target was the family's, v = an enemy head in view, k = the parent believed it was our longest). Situation: r1-99, a pf map
//             (truth), our units at the action (replay count) below the tag's target. Effect ("의도대로"): the child's body (the child or a
//             descendant) alive 30 rounds on (or at the end); gate 2 also counts the child's natural pearls within 30 rounds (>= 1).
//             Move tags " pfx" (pf chose to split, the move gate kept the dragon moving) and " pfc" (pf's turn, the child's spot failed): counts.
//   stack12 metrics (section shown with pf tags or --pf): the intake-gap study's numbers for our team by its own code (exp/intake-gap/extract.js
//             analyse() and aggregate.js teamView through exp/cand-stack12/pfstats.js, run when pool A carries pf tags or with --pf): units at r10 /
//             r50 / r100 / r250 (both teams), non-escape births per length >= 4 head-round in r0-99 (both teams), natural intake by phase (both
//             teams), view B heads term and race share r0-249, our territory's spawn capacity where the enemy head is nearer (all rounds), the end
//             king; tag-independent: our longest at r100 / r250, max units, rounds at >= 56 units; pf children's fates, trades of our pieces in r1-99.
'use strict';""")

# 2. constants
E("""const S9_LSPLIT_END = 340; // lsplit window end (bot LSPLIT_END): r250-339 from W10 (coordinator 22:0x; the study and the first build: 430)
""",
"""const S9_LSPLIT_END = 340; // lsplit window end (bot LSPLIT_END): r250-339 from W10 (coordinator 22:0x; the study and the first build: 430)
// stack12 (cand-stack12.md): pf's maps (the bot's pfMapOn), its 500-round and elimination groups, and its target table (plan.cpp PF_TAB: top winners'
// mean r100 count per layout, the family's before the layout is decided; capped at 64 - PF_HEADROOM = 56)
const S12_MAPS = new Set(['Slithery Fight', 'Schooltime', 'Trauma', 'Default', 'Devil', 'Queen Of Spades', 'Trophy']);
const S12_500 = new Set(['Slithery Fight', 'Schooltime', 'Trauma']);
const S12_ELIM = new Set(['Default', 'Devil', 'Queen Of Spades', 'Trophy']);
const S12_TAB = { 'Slithery Fight': [57, 60, 54], 'Schooltime': [30, 44, 16], 'Trauma': [18, 18, 18], 'Default': [19, 19, 19], 'Devil': [26, 29, 23],
  'Queen Of Spades': [13, 13, 12], 'Trophy': [31, 31, 31] };
const S12_TARGET = (map, lay) => { const t = S12_TAB[map]; if (!t) return null; return Math.min(56, lay === 'a' ? t[1] : lay === 'b' ? t[2] : t[0]); };
""")

# 3. non-escape split kinds (stack7's episode counts)
E("""const S7_SPLITS = new Set(['split', 'frag', 'bsplit', 'csplit', 'kcap', 'floor', 'lsplit']); // stack9: lsplit is a non-escape split""",
  """const S7_SPLITS = new Set(['split', 'frag', 'bsplit', 'csplit', 'kcap', 'floor', 'lsplit', 'pf']); // stack9: lsplit is a non-escape split; stack12: pf""")

# 4. parseInd: the pf split label and the move tags
E("""  if (s.startsWith('last-trade')) return { kind: 'lasttrade' };""",
  """  if ((m = /^pf(\\d+) u(\\d+) L(\\d+) t(\\d+)/.exec(s))) return { kind: 'pf', size: +m[1], units: +m[2], target: +m[4], fam: / f(?:\\s|$)/.test(s), view: / v(?:\\s|$)/.test(s), king: / k(?:\\s|$)/.test(s) }; // stack12 pf
  if (s.startsWith('last-trade')) return { kind: 'lasttrade' };""")
E("""      else if (t === 'lwk') f.lwk = true;                                              // stack11 lwk
""",
  """      else if (t === 'lwk') f.lwk = true;                                              // stack11 lwk
      else if (t === 'pfx') f.pfx = true; else if (t === 'pfc') f.pfc = true;         // stack12 pf: the move gate / the child's spot stopped a pf split
""")

# 5. per-game state
E("""  const covWin = new Map();    // stack9: our dragon id -> its open cov window record (30 rounds)
""",
  """  const covWin = new Map();    // stack9: our dragon id -> its open cov window record (30 rounds)
  const S12 = { pfx: 0, pfc: 0, pfx99: 0, pfc99: 0 };          // stack12: pf's move tags (all / r1-99)
""")

# 6. the action hook: pf records, move-tag counts
E("""        case 'bsplit': made.push({ k: 'bsplit', ...base, units: t.units }); break; // cand-mapid bsplit
""",
  """        case 'bsplit': made.push({ k: 'bsplit', ...base, units: t.units }); break; // cand-mapid bsplit
        case 'pf': { let u12 = 0; for (const o of c.drag.values()) if (o.team === us) u12++; const mt12 = mapTags.get(d.id); // stack12: our units now (replay), the last map tag
          made.push({ k: 'pf', ...base, units: t.units, target: t.target, fam: t.fam ? 1 : 0, view: t.view ? 1 : 0, kingTag: t.king ? 1 : 0, uR: u12,
            mt: mt12 && mt12.length ? mt12[mt12.length - 1].tag : null }); break; }
""")
E("""          if (t.ks2) counts.ks2++;
""",
  """          if (t.ks2) counts.ks2++;
          if (t.pfx) { S12.pfx++; if (r < 100) S12.pfx99++; } if (t.pfc) { S12.pfc++; if (r < 100) S12.pfc99++; } // stack12 pf
""")

# 7. effects of the pf records
E("""      case 'csplit': { // stack5: the study's two gates on the child (pass2.js: born, alive 30 rounds on or at the end, natural eats)
""",
  """      case 'pf': { // stack12 (cand-stack12.md): the situation from the replay; the child's body 10 / 30 rounds on, its natural pearls, its end; the parent 10 rounds on
        x.ex = x.child !== undefined ? 1 : 0;
        x.tT = S12_TARGET(task.map, truthLay());                                                  // the true layout's target (null off the pf maps)
        x.sitR = x.r >= 1 && x.r < 100 ? 1 : 0; x.sitM = S12_MAPS.has(task.map) ? 1 : 0; x.sitU = x.uR < x.target ? 1 : 0;
        x.sit = x.sitR && x.sitM && x.sitU ? 1 : 0;
        x.sitT = x.tT !== null && x.uR < x.tT ? 1 : 0;                                            // (reference) below the true layout's target
        x.tagOk = x.units === x.uR ? 1 : 0;                                                       // the tag's unit count is the replay's
        const PL = life.get(x.id); x.startDragon = PL && PL.parent !== undefined && PL.parent !== null && PL.parent >= 0 ? 0 : 1;
        if (x.ex) {
          const CL = life.get(x.child); x.childId = x.child;
          x.childAlive10 = alive(x.child, x.r + 10) ? 1 : 0; x.childAlive30 = alive(x.child, x.r + 30) ? 1 : 0;
          x.body10 = body(x.child, x.r + 10); x.body30 = body(x.child, x.r + 30);
          x.nat30 = CL.nat.filter(q => q >= x.r && q <= x.r + 30).length;
          x.parentAlive10 = alive(x.id, x.r + 10) ? 1 : 0; x.parentBody10 = body(x.id, x.r + 10);
          x.childDeath = CL.death && CL.death.r <= x.r + 30 ? { r: CL.death.r, cause: CL.death.cause, otherLen: CL.death.otherLen } : null;
          x.childEnd = CL.death ? { r: CL.death.r, cause: CL.death.cause, age: CL.death.r - x.r, fed: fedBy.has(x.child) ? fedBy.get(x.child).k : null } : null;
          x.parentDeath10 = PL && PL.death && PL.death.r <= x.r + 10 ? { r: PL.death.r, cause: PL.death.cause, otherLen: PL.death.otherLen } : null;
          const bt = T5.cb.get(x.child); x.bornOwn = bt !== undefined && T5.terr && T5.terr[bt] === ourTerr ? 1 : 0;
        }
        x.ok = x.ex ? x.body30 : 0;
        break;
      }
      case 'csplit': { // stack5: the study's two gates on the child (pass2.js: born, alive 30 rounds on or at the end, natural eats)
""")

# 8. per-game stack12 numbers
E("""  } catch (err) { s11 = { err: String(err).slice(0, 160) }; }                       // never drop the game for the extra indicators
""",
  """  } catch (err) { s11 = { err: String(err).slice(0, 160) }; }                       // never drop the game for the extra indicators
  // stack12 (cand-stack12.md): the intake-gap study's per-game numbers for our team by its own code (exp/intake-gap/extract.js analyse() and aggregate.js
  // teamView, through exp/cand-stack12/pfstats.js gameStats), when asked (task.intake). Tag-independent here (always): our longest at r100 / r250 (the
  // final state after the end, 0 once eliminated), our max units and the rounds at >= 56 units, pf's move tags.
  let s12 = null;
  if (task.intake) try {
    const IG = require(path.join(ROOT, 'exp', 'intake-gap', 'extract.js')), PS12 = require(path.join(ROOT, 'exp', 'cand-stack12', 'pfstats.js'));
    const G12 = IG.analyse(R, { map: task.map, us, gameId: task.gameId || null, src: task.src === 'online' ? 'online' : 'local', key: task.key });
    G12.map = task.map; G12.kind = S9_R500.has(task.map) ? 'r500' : 'elim';
    s12 = PS12.gameStats(G12, us === 'B' ? 1 : 0);
    s12.chkBad = [G12.chk, G12.chkX, G12.chkR].some(o => o && Object.entries(o).some(([k, v]) => k !== 'liveLeft' && v)) ? 1 : 0;
  } catch (err) { s12 = { err: String(err).slice(0, 160) }; }                       // never drop the game for the extra indicators
  const s12t = (() => {
    const kE = fin.size ? Math.max(...fin.values()) : 0, at12 = (arr, r, v) => r >= rounds || arr[r] === undefined ? v : arr[r];
    const us12 = S7.u.filter(v => v !== undefined);
    return { k100: at12(S7.k, 100, kE), k250: at12(S7.k, 250, kE), maxU: us12.length ? Math.max(...us12) : 0, at56: us12.filter(v => v >= 56).length,
      pfx: S12.pfx, pfc: S12.pfc, pfx99: S12.pfx99, pfc99: S12.pfc99, lntv99: recs.filter(x => x.k === 'lntv' && x.r < 100).length };
  })();
""")
E("""    s9, s11 };                                                                           // stack9 supply-chain indicators (task.supply)""",
  """    s9, s11, s12, s12t };                                                                // stack9 supply-chain indicators (task.supply); stack12""")

# 9. summarise
E("""  S.s9 = games.filter(g => g.s9).map(g => ({ ...g.s9, map: g.map, set: g.set, rounds: g.rounds }));                                 // stack9
""",
  """  S.s9 = games.filter(g => g.s9).map(g => ({ ...g.s9, map: g.map, set: g.set, rounds: g.rounds }));                                 // stack9
  S.s12 = games.filter(g => g.s12).map(g => ({ ...g.s12, gmap: g.map, set: g.set, game: g.game, t12: g.s12t, xch: g.s10 ? g.s10.xch : [], t5: g.t5 })); // stack12
  S.s12t = games.map(g => ({ ...(g.s12t || {}), gmap: g.map, rounds: g.rounds }));                                                  // stack12 (tag-independent)
""")

# 10. labels and order
E("""ORDER.splice(0, 0, 'gh', 'ghd', 'kx', 'lwk');""",
  """Object.assign(LABEL, { pf: '조각 먼저 여는 판 (pf, stack12)' });                                   // stack12
ORDER.splice(0, 0, 'pf');                                                                               // stack12
ORDER.splice(0, 0, 'gh', 'ghd', 'kx', 'lwk');""")

# 11. effect / case lines
E("""    case 'lnt': case 'lntv': case 'kint': return effectLine10(k, xs);                                    // stack10
""",
  """    case 'lnt': case 'lntv': case 'kint': return effectLine10(k, xs);                                    // stack10
    case 'pf': return effectLine12(xs);                                                                   // stack12
""")
E("""    case 'lsplit': case 'covw': return caseLine9(x, where);                                                 // stack9
""",
  """    case 'lsplit': case 'covw': return caseLine9(x, where);                                                 // stack9
    case 'pf': return caseLine12(x, where, dd);                                                            // stack12
""")

# 12. report: the "의도대로" line and the section
E("""  L.push('');
  L.push('## 요약', '');""",
  """  if ((A.by.pf || []).length || (B && (B.by.pf || []).length))                                         // stack12
    L.push(`- stack12의 "의도대로": 조각 먼저 여는 판(pf)=새끼의 몸(새끼와 그 자손)이 30라운드 뒤 살아 있음(판이 먼저 끝나면 생존). 새끼의 자연 진주, 분열 속도, 수, 섭취(섭취 격차 연구의 정의), 부작용은 맨 뒤 stack12 절.`);
  L.push('');
  L.push('## 요약', '');""")
E("""  L.push(...stack11Section(A, B, opts));""",
  """  L.push(...stack11Section(A, B, opts));
  L.push(...stack12Section(A, B, opts));                                                                 // stack12""")

# 13. main: the intake indicators when pool A carries pf tags or with --pf
E("""  let rA = await runAll(flag11(tA, sup9, eg11), jobs);""",
  """  const pf12 = argv.includes('--pf'), withIn = ts => ts.map(t => ({ ...t, intake: true }));              // stack12: the intake-gap indicators
  const flag12 = (ts, s, e, i) => { const o = flag11(ts, s, e); return i ? withIn(o) : o; };                 // stack12
  let rA = await runAll(flag12(tA, sup9, eg11, pf12), jobs);""")
E("""  if (has9 || has11) rA = await runAll(flag11(tA, sup9 || has9, eg11 || has11), jobs);
  const rB = tB ? await runAll(flag11(tB, sup9 || has9, eg11 || has11), jobs) : null;""",
  """  const has12 = !pf12 && rA.games.some(g => g.recs.some(x => x.k === 'pf'));                               // stack12: pool A carries pf tags
  if (has9 || has11 || has12) rA = await runAll(flag12(tA, sup9 || has9, eg11 || has11, pf12 || has12), jobs);
  const rB = tB ? await runAll(flag12(tB, sup9 || has9, eg11 || has11, pf12 || has12), jobs) : null;""")
E("""    stack9: argv.includes('--stack9'), endgame: argv.includes('--endgame') });""",
  """    stack9: argv.includes('--stack9'), endgame: argv.includes('--endgame'), pf: argv.includes('--pf') }); // stack12 --pf""")

# 14. the stack12 section
E("""module.exports = { parseInd, analyse, summarise, report };""",
  open(sys.path[0] + '/mc_section.js', encoding='utf-8').read() + """
module.exports = { parseInd, analyse, summarise, report };""")

bad = 0
for a, b in edits:
    n = s.count(a)
    if n != 1:
        print(f'anchor found {n} times: {a[:100]!r}', file=sys.stderr); bad += 1; continue
    s = s.replace(a, b)
if bad:
    print(f'{bad} anchors failed; nothing written', file=sys.stderr); sys.exit(1)
open(out, 'w', encoding='utf-8').write(s)
print(f'applied {len(edits)} edits -> {out}')
