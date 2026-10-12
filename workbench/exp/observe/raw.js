// Fast replay loader for exp/intake-gap: decodes the event list straight from the Cap'n Proto bytes (DataView), and uses the
// official viewer parser (tools/top_features.js internals Df/Of) only for the root (map text, teams, result).
// The per-event conversion of the official parser (bf) is the cost (80% of a game's analysis); this decoder gives the same
// objects for the event kinds the analyses read: roundStart, turnStart, pearlCountdown, tileChange, dragonAction (action,
// instructions, tle), dragonIndicator, dragonUpdate, dragonSplit, dragonDeath. sonarPing is counted per sender and dropped;
// engineLog, dragonLog and debugDraw are dropped. Layouts (from the viewer's generated schema classes):
//   Replay (8 B data, 5 ptr): events = ptr 3, a composite list of Event (8 B, 1 ptr): which = u16 @0, payload = ptr 0.
//   RoundStart/TurnStart (8,0): i32 @0. TileChange (8,1): hasPearl = bit 0, tile = ptr 0 -> Point (8,0): x i32 @0, y i32 @4.
//   DragonAction (8,2): id i32 @0, tle = bit 32, action = ptr 0 -> PlayerAction (8,1): which u16 @0 (0 move: ptr 0 List<u16>,
//     1 split: i32 @4, 2 suicide), instructions = ptr 1 -> (16,0): count u64 @0, exceeded = bit 64.
//   DragonIndicator (8,1): id i32 @0, text ptr 0. DragonUpdate (8,2): id i32 @0, facing u16 @4, head ptr 0, tail ptr 1.
//   DragonSplit (16,2): parentId i32 @0, childId i32 @4, team u16 @8, childFacing u16 @10, parentBody ptr 0, childBody ptr 1
//     (lists of Point). DragonDeath (8,0): id i32 @0, reason u16 @4. SonarPing: senderId i32 @0.
// validate(file) compares every decoded event with the official conversion (exp/intake-gap/validate_raw.js).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..', '..');
const DIR = ['N', 'E', 'S', 'W'], TEAM = ['A', 'B'], REASON = ['W', 'S', 'O', 'H', 'A'];
const TD = new TextDecoder();

// Cap'n Proto packed encoding (the viewer opens replays with new Message(buf, packed = true)): per 8-byte word a tag byte whose bits
// mark the non-zero bytes that follow; tag 0x00 is followed by a count of extra zero words, tag 0xFF by 8 raw bytes and a count of
// raw words copied verbatim. Two passes: size, then fill.
function unpack(src) {
  const n = src.length; let i = 0, size = 0;
  while (i < n) {
    const tag = src[i++];
    if (tag === 0x00) { size += 8 * (1 + src[i++]); continue; }
    let c = 0; for (let b = tag; b; b &= b - 1) c++;
    i += c; size += 8;
    if (tag === 0xff) { const w = src[i++]; i += w * 8; size += w * 8; }
  }
  const out = new Uint8Array(size); i = 0; let o = 0;
  while (i < n) {
    const tag = src[i++];
    if (tag === 0x00) { o += 8 * (1 + src[i++]); continue; }
    for (let b = 0; b < 8; b++) { if (tag & (1 << b)) out[o] = src[i++]; o++; }
    if (tag === 0xff) { const w = src[i++] * 8; out.set(src.subarray(i, i + w), o); i += w; o += w; }
  }
  return out;
}
function decodeEvents(packed, opts = {}) {
  const u8 = unpack(packed instanceof Uint8Array ? packed : new Uint8Array(packed));
  const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  const nseg = dv.getUint32(0, true) + 1;
  let off = 4 + nseg * 4; if (off % 8) off += 4;
  const segStart = new Array(nseg); let p = off;
  for (let i = 0; i < nseg; i++) { segStart[i] = p; p += dv.getUint32(4 + i * 4, true) * 8; }
  // resolve the pointer at byte address a (in segment s): returns [kind, contentAddr, hi] with far pointers followed
  const R = { kind: 0, addr: 0, hi: 0, lo: 0 };
  function resolve(a) {
    let lo = dv.getUint32(a, true), hi = dv.getUint32(a + 4, true);
    if (lo === 0 && hi === 0) { R.kind = -1; return R; }
    let kind = lo & 3;
    if (kind === 2) {
      const dbl = (lo >>> 2) & 1, pad = segStart[hi] + (lo >>> 3) * 8;
      if (!dbl) { a = pad; lo = dv.getUint32(a, true); hi = dv.getUint32(a + 4, true); kind = lo & 3; }
      else {
        const flo = dv.getUint32(pad, true), fhi = dv.getUint32(pad + 4, true);
        const content = segStart[fhi] + (flo >>> 3) * 8;
        const tlo = dv.getUint32(pad + 8, true), thi = dv.getUint32(pad + 12, true);
        R.kind = tlo & 3; R.addr = content; R.hi = thi; R.lo = tlo; return R;
      }
    }
    R.kind = kind; R.addr = a + 8 + ((lo | 0) >> 2) * 8; R.hi = hi; R.lo = lo; return R;
  }
  const structAt = a => { const r = resolve(a); if (r.kind !== 0) return null; return { addr: r.addr, dw: r.hi & 0xffff, pc: r.hi >>> 16 }; };
  const ptrAddr = (s, i) => i < s.pc ? s.addr + s.dw * 8 + i * 8 : -1;
  const i32 = (s, o) => o + 4 <= s.dw * 8 ? dv.getInt32(s.addr + o, true) : 0;
  const u16 = (s, o) => o + 2 <= s.dw * 8 ? dv.getUint16(s.addr + o, true) : 0;
  const bit = (s, b) => (b >> 3) < s.dw * 8 ? (u8[s.addr + (b >> 3)] >> (b & 7)) & 1 : 0;
  const point = (s, i) => { const a = ptrAddr(s, i); if (a < 0) return null; const q = structAt(a); if (!q) return null; return { x: i32(q, 0), y: i32(q, 4) }; };
  const pointList = (s, i) => {
    const a = ptrAddr(s, i); if (a < 0) return [];
    const r = resolve(a); if (r.kind !== 1) return [];
    const es = r.hi & 7, out = [];
    if (es === 7) {
      const tag = r.addr, n = (dv.getUint32(tag, true) | 0) >> 2, thi = dv.getUint32(tag + 4, true), dw = thi & 0xffff, pc = thi >>> 16, sz = (dw + pc) * 8;
      for (let k = 0; k < n; k++) { const b = tag + 8 + k * sz; out.push({ x: dw >= 1 ? dv.getInt32(b, true) : 0, y: dw >= 1 ? dv.getInt32(b + 4, true) : 0 }); }
    } else throw Error('unexpected Point list encoding ' + es);
    return out;
  };
  const text = (s, i) => {
    const a = ptrAddr(s, i); if (a < 0) return '';
    const r = resolve(a); if (r.kind !== 1) return '';
    const n = r.hi >>> 3; return n > 0 ? TD.decode(u8.subarray(r.addr, r.addr + n - 1)) : '';
  };
  const root = structAt(segStart[0]);
  const evPtr = ptrAddr(root, 3);
  const L = resolve(evPtr);
  if (L.kind !== 1 || (L.hi & 7) !== 7) throw Error('events list not found');
  const tag = L.addr, n = (dv.getUint32(tag, true) | 0) >> 2, thi = dv.getUint32(tag + 4, true), edw = thi & 0xffff, epc = thi >>> 16, esz = (edw + epc) * 8;
  const events = [], sonar = new Map();
  for (let k = 0; k < n; k++) {
    const e = { addr: tag + 8 + k * esz, dw: edw, pc: epc };
    const w = u16(e, 0);
    if (w === 5 || w === 6 || w === 8) continue;                          // engineLog, dragonLog, debugDraw
    const s = structAt(ptrAddr(e, 0));
    if (!s) throw Error('event payload missing at ' + k);
    switch (w) {
      case 0: events.push({ type: 'roundStart', round: i32(s, 0) }); break;
      case 1: events.push({ type: 'turnStart', id: i32(s, 0) }); break;
      case 2: events.push({ type: 'pearlCountdown', tile: point(s, 0), countdown: i32(s, 0) }); break;
      case 3: events.push({ type: 'tileChange', tile: point(s, 0), hasPearl: !!bit(s, 0) }); break;
      case 4: {
        const o = { type: 'dragonAction', id: i32(s, 0), action: null };
        const aa = ptrAddr(s, 0), as = aa >= 0 ? structAt(aa) : null;
        if (as) {
          const which = u16(as, 0);
          if (which === 0) {
            const la = ptrAddr(as, 0), lr = la >= 0 ? resolve(la) : null, steps = [];
            if (lr && lr.kind === 1) { const cnt = lr.hi >>> 3, base = lr.addr; for (let q = 0; q < cnt; q++) steps.push(DIR[dv.getUint16(base + q * 2, true)]); }
            o.action = { kind: 'move', steps };
          } else if (which === 1) o.action = { kind: 'split', childSegmentCount: i32(as, 4) };
          else if (which === 2) o.action = { kind: 'suicide' };
          else throw Error('unknown action kind ' + which);
        }
        const ia = ptrAddr(s, 1), is = ia >= 0 ? structAt(ia) : null;
        if (is) o.instructions = { count: Number(is.dw >= 1 ? dv.getBigUint64(is.addr, true) : 0n), exceeded: !!bit(is, 64) };
        if (bit(s, 32)) o.tle = true;
        events.push(o); break;
      }
      case 7: events.push({ type: 'dragonIndicator', id: i32(s, 0), text: text(s, 0) }); break;
      case 9: events.push({ type: 'dragonUpdate', id: i32(s, 0), facing: DIR[u16(s, 4)], head: point(s, 0), tail: point(s, 1) }); break;
      case 10: events.push({ type: 'dragonSplit', parentId: i32(s, 0), childId: i32(s, 4), team: TEAM[u16(s, 8)], childFacing: DIR[u16(s, 10)], parentBody: pointList(s, 0), childBody: pointList(s, 1) }); break;
      case 11: events.push({ type: 'dragonDeath', id: i32(s, 0), reason: REASON[u16(s, 4)] }); break;
      case 12: { const id=i32(s,0); sonar.set(id,(sonar.get(id)||0)+1); const o={type:'sonarPing',senderId:id,direction:DIR[u16(s,4)],origin:point(s,0),end:point(s,1),value64:s.dw>=4?dv.getBigUint64(s.addr+16,true):BigInt(dv.getUint32(s.addr+8,true)),hitKind:s.dw>=4?[null,'empty','kelp','ally','allyHead','enemy','enemyHead'][u16(s,24)]:null}; if(u16(s,6)===1)o.hitId=i32(s,12); events.push(o); break; }
      default: throw Error('unknown event kind ' + w);
    }
  }
  return { events, sonar };
}

let VIEW = null;
function viewer() {
  if (!VIEW) {
    const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
    const src = tf.viewerSource(), cut = src.indexOf('var Af=B(');
    const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') + 'globalThis.__tf={Df:Df,bf:bf,Of:Of,cu:$,of:of};})();';
    const ctx = { TextEncoder, TextDecoder }; vm.runInNewContext(code, ctx, { timeout: 5000 });
    VIEW = ctx.__tf;
  }
  return VIEW;
}
// load(file) -> R like tools/replay.js (match, events, result, teams) with R.sonarBySender; sonar events are not in R.events
function load(file) {
  const raw = fs.readFileSync(file), buf = file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw;
  const { Df, Of } = viewer();
  const root = Df(buf);
  const { events, sonar } = decodeEvents(buf);
  const R = Of(root, events);
  R.sonarBySender = sonar;
  return R;
}
// validate(file): every non-sonar/log event of the official conversion equals the decoded one (JSON), sonar counts equal
function validate(file) {
  const raw = fs.readFileSync(file), buf = file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw;
  const { Df, bf } = viewer();
  const root = Df(buf), list = root.events, off = [], sonar = new Map();
  for (let i = 0; i < list.length; i++) {
    const o = bf(list.get(i));
    if (o.type === 'sonarPing') { sonar.set(o.senderId,(sonar.get(o.senderId)||0)+1); continue; }
    if (o.type === 'engineLog' || o.type === 'dragonLog' || o.type === 'debugDraw') continue;
    off.push(o);
  }
  const mine = decodeEvents(buf); mine.events=mine.events.filter(e=>e.type!=='sonarPing');
  let bad = 0; const n = Math.max(off.length, mine.events.length);
  for (let i = 0; i < n; i++) if (JSON.stringify(off[i]) !== JSON.stringify(mine.events[i])) { if (bad < 3) console.error('diff', i, JSON.stringify(off[i]), JSON.stringify(mine.events[i])); bad++; }
  for (const [k, v] of sonar) if (mine.sonar.get(k) !== v) bad++;
  if (sonar.size !== mine.sonar.size) bad++;
  return { events: off.length, bad };
}
module.exports = { decodeEvents, load, validate, unpack };
