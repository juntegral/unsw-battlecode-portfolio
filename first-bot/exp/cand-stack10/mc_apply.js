#!/usr/bin/env node
// cand-stack10: apply the stack10 section (lnt / lntv / kint / utab and the economy-principles E4 / E3 metrics) to a copy of
// tools/mech_check.js. The pieces are in exp/cand-stack10/mc/; every anchor must occur exactly once in the target, so a changed base
// fails loudly instead of silently misplacing code. Apply to a fresh copy of the current tools/mech_check.js, never to an old copy.
// usage: node exp/cand-stack10/mc_apply.js <mech_check copy>
'use strict';
const fs = require('fs'), path = require('path');
const file = path.resolve(process.argv[2] || '');
if (!fs.existsSync(file)) { console.error('usage: mc_apply.js <mech_check copy>'); process.exit(2); }
const P = n => fs.readFileSync(path.join(__dirname, 'mc', n), 'utf8');
// [mode, anchor, text]: before = text + anchor, after = anchor + text, replace = text
const EDITS = [
  ['before', "'use strict';\n", P('p01_header.txt')],
  ['after', "      else if ((g = /^c([le])@(\\d+),(\\d+)$/.exec(t))) f['c' + g[1]] = { x: +g[2], y: +g[3] }; // stack8 cl / ce\n", P('p02_parse_move.txt')],
  ['replace', "view: / v(?:\\s|$)/.test(s), king: / k(?:\\s|$)/.test(s) }; // stack5 csplit",
   "view: / v(?:\\s|$)/.test(s), king: / k(?:\\s|$)/.test(s), tab: / tab(?:\\s|$)/.test(s) }; // stack5 csplit; stack10 utab: tab"],
  ['after', "  const S8 = { pings: new Map(), pre: new Map(), eps: new Map(), pullPre: new Map(), fT: 0, fCand: 0, fAway: 0 };\n", P('p04_state.txt')],
  ['after', "      ctxOf.set(d.id, { eD, eL, eSD, aD, aL, king: k === d ? 1 : 0, kingL: k ? k.body.length : 0, free: d.free, b3, eC, eP });\n", P('p05_turn.txt')],
  ['after', "      const base = { r, id: d.id, L: before.length, act: d.act, steps: d.steps, ate: d.ateThisAct, cx };\n      const made = [];\n", P('p06_action.txt')],
  ['replace', "        case 'csplit': made.push({ k: 'csplit', ...base, units: t.units, target: t.target, view: t.view ? 1 : 0, kingTag: t.king ? 1 : 0 }); break; // stack5\n", P('p07_csplit_rec.txt')],
  ['before', "      const m = pending.get(d.id);\n      if (m) for (const x of m) if (x.r === r) x.died = dz;\n", P('p08_death.txt')],
  ['after', "  const g = perGame(R, info, hooks);\n", P('p09_after_pergame.txt')],
  ['before', "      case 'trade': {\n", P('p10_recs_cases.txt')],
  ['replace', "  return { t5: t5o, key: task.key,", P('p11_return.txt').replace(/\n$/, '')],
  ['after', "  S.s8 = { fT: 0, fCand: 0, fAway: 0 }; for (const g of games) if (g.s8) for (const k of Object.keys(S.s8)) S.s8[k] += g.s8[k] || 0; // stack8\n", P('p12_summarise.txt')],
  ['after', "ORDER.splice(0, 0, 'fp', 'cl', 'ce', 'px2');                                                          // stack8\n", P('p13_label.txt')],
  ['after', "    case 'px2': case 'fp': case 'cl': case 'ce': return effectLine8(k, xs);                              // stack8\n", P('p14_effectline.txt')],
  ['after', "    case 'px2': case 'fp': case 'cl': case 'ce': return caseLine8(x, where);                                // stack8\n", P('p15_caseline.txt')],
  ['before', "  L.push('');\n  L.push('## 요약', '');\n", P('p16_report_def.txt')],
  ['after', "  L.push(...stack8Section(A, B, opts));                                                                  // stack8\n", P('p17_report_section.txt')],
  ['before', "module.exports = { parseInd, analyse, summarise, report };\n", P('p18_funcs.txt')],
];
let src = fs.readFileSync(file, 'utf8');
if (src.includes('stack10Section')) { console.error(`${file}: already has the stack10 section`); process.exit(1); }
for (const [mode, anchor, text] of EDITS) {
  const n = src.split(anchor).length - 1;
  if (n !== 1) { console.error(`anchor found ${n} times (need 1): ${anchor.slice(0, 100).replace(/\n/g, '\\n')}`); process.exit(1); }
  src = src.replace(anchor, () => mode === 'before' ? text + anchor : mode === 'after' ? anchor + text : text);
}
fs.writeFileSync(file, src);
console.log(`applied ${EDITS.length} stack10 edits to ${path.relative(process.cwd(), file)}`);
