#!/usr/bin/env node
// Fill the observation doc: replaces every line "<!--T:<id>-->" of the template with the table block "### <id> ..." of
// exp/endgame-king/doc-tables.md (its caption in bold, then the table).
// usage: node exp/endgame-king/doc.js > exp/endgame-king/doc-tables.md && node exp/endgame-king/fill.js exp/endgame-king/doc.tmpl.md research/observations/endgame-king.md
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const [tmpl, outF] = process.argv.slice(2);
const tables = fs.readFileSync(path.join(__dirname, 'doc-tables.md'), 'utf8');
const blocks = {}; let cur = null;
for (const l of tables.split('\n')) {
  const m = /^### (T\w+) (.*)$/.exec(l);
  if (m) { cur = m[1]; blocks[cur] = ['**' + m[1] + '.** ' + m[2], '']; continue; }
  if (cur && l.trim()) blocks[cur].push(l);
}
const head = tables.split('\n').find(l => l.startsWith('생성 기록:') || l.startsWith('모집단:')) || '';
let missing = [];
const out = fs.readFileSync(path.resolve(ROOT, tmpl), 'utf8').split('\n').map(l => {
  const m = /^<!--T:(\w+)-->$/.exec(l.trim());
  if (m) { if (!blocks[m[1]]) { missing.push(m[1]); return l; } return blocks[m[1]].join('\n'); }
  if (l.trim() === '<!--POP-->') return head;
  return l;
});
fs.writeFileSync(path.resolve(ROOT, outF), out.join('\n'));
console.log('wrote', outF, 'missing', missing.join(',') || 'none');
