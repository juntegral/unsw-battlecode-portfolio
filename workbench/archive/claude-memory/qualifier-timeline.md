---
name: qualifier-timeline
description: Qualifier submissions close 2026-10-09 17:00 AEDT (15:00 KST); best-of-7 single elimination on UNSEEN maps; per-map tables won't apply. The earlier "until 1/10 = Jan 10" reading was wrong.
metadata:
  type: project
---

On 2026-10-01 at about 10:45 KST the user pasted the official qualifier format:
- Every eligible team enters a seeded single-elimination bracket for 10 Grand Final places. Each match is best of 7 **on unseen maps**.
- **Submissions close at 17:00 AEDT on 9 October 2026, which is 15:00 KST on Oct 9.** Autoscrims then run until the stream and set the seeds.
- The 8 quarterfinalists qualify. The 8 Round-of-16 losers play a second-chance bracket, reseeded by their original seed, and its two finalists take the last two places.
- The event streams from 17:30 AEDT on 10 October, which is 15:30 KST.

**Correction:** at 08:30 KST the user said "퀄리파이어는 1월 10일까지임 천천히 가자", and I recorded "until 2026-01-10". The site says the qualifier deadline is Oct 9–10, about 8 days later. The "1/10" in the notes was day/month.

**Why it matters:**
- The bracket plays unseen maps. On an unknown map our bot falls back to the FORTRESS engine (policy.hpp DEFAULT_POLICY), so none of the per-map tables apply: engine rows, mapdb, terrdb, frontdb, opdb, ptmap, pocket tables.
- The online top-6 waves on the 10 known maps measure the known-map ladder (seeding autoscrims), not the bracket.

**How to apply:**
- The qualifier target is generalisation: rules computed at runtime from the geometry the bot observes, plus a sound engine choice on unknown maps.
- Use held-out maps for evaluation: the bundled maps that are not in the online pool (arena, big_empty, Colosseum, default_small, dilemma, stronghold), or known maps with recognition switched off.
- The deadline is 2026-10-09 15:00 KST. Check `rules/CHANGES-*.md` for any later announcements. See [[sprint-deadline-freeze]].
- **Qualifier build runs with map recognition OFF (user-confirmed 2026-10-01 15:21 KST: "ㅇㅇ 퀄리파이어는 인식 끄는 걸로 가자").** On unseen maps recognition can only misfire (stronghold = edited Trauma; same-start edits pass the W2 start anchor). Candidate line: unsw-swarm `versions/v1.7/` with `QUAL_NO_MAPID` on. Per-map differences must come from runtime observation (W3 map model, W9 engine gate, W7 area/density rules), not tables; the old per-map choices serve as check targets with recognition off.
- **Sprint bracket maps were fully custom (user watched the live stream, 2026-10-01 ~16:50 KST): "완전 다른 맵임. 완전 커스텀이네. 맵에 따라서 최적화를 하는거는 맞지 않아."** Sprint autoscrims (08:18–11:13 KST) had used the 10 known maps. Option A (recognition fully off) confirmed; option B (keep recognition for known-map seeding autoscrims) dropped. No per-map optimisation from now on.
