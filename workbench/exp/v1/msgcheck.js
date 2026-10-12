// decode our team's sonar messages in a replay (format 1 = stack11, format 2 = v1 belief fix) and check them against the truth:
// sender id exact, round, and (format 2) the reported head = the sender's head after its action (the ray's origin), length within 1
const { makeLoader, viewerSource } = require('../../tools/top_features.js');
const load = makeLoader(viewerSource());
const [file, us] = process.argv.slice(2);
const R = load(file);
const W = R.match.map.width;
const WH = 0x9E3779B97F4A7C15n;
const team = new Map(); for (const d of R.match.map.initialDragons) team.set(d.id, d.team);
const len = new Map(); for (const d of R.match.map.initialDragons) len.set(d.id, d.body.length);
let round = -1;
const st = { n: 0, f1: 0, f2: 0, f2relay: 0, idOk: 0, idBad: 0, rndOk: 0, posOk: 0, posN: 0, relayIdOk: 0 };
for (const e of R.events) {
  if (e.type === 'roundStart') round = e.round;
  else if (e.type === 'dragonSplit') team.set(e.childId, e.team);
  else if (e.type === 'sonarPing' && team.get(e.senderId) === us) {
    st.n++;
    const v = BigInt(e.value64) ^ WH;
    const magic = Number(v >> 58n);
    if (magic === 0x33 || magic === 0x0D) {
      const relay = magic === 0x0D;
      const id = Number((v >> 47n) & 2047n), rnd = Number((v >> 40n) & 127n), x = Number((v >> 34n) & 63n), y = Number((v >> 28n) & 63n);
      if (relay) { st.f2relay++; if (team.get(id) === us) st.relayIdOk++; continue; }
      st.f2++;
      if (id === (e.senderId & 2047)) st.idOk++; else st.idBad++;
      if (rnd === (round & 127)) st.rndOk++;
      st.posN++; if (e.origin && e.origin.x === x && e.origin.y === y) st.posOk++;
    } else if (magic === 0x2D || magic === 0x1B) {
      st.f1++;
      if (magic === 0x2D) { const id = Number((v >> 50n) & 255n); if (id === e.senderId) st.idOk++; else st.idBad++; }
    }
  }
}
console.log(JSON.stringify(st));
