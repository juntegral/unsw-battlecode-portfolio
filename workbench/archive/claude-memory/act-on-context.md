---
name: act-on-context
description: "user rule 10-06 — when a teammate's request to the bot is clear from context, do it and report after; no magic words or slash-command syntax; at most one plain confirmation"
metadata:
  node_type: memory
  type: feedback
  originSessionId: bf4f8138-7733-48a7-8829-36025e05cdcd
  modified: 2026-10-06T13:26:11.553Z
---

User rule 2026-10-06 (meow-main03): when a teammate asks meowbot for something and the meaning is clear from context, do it and say afterwards what was done. Do not answer with "mention me with `merge` / `force` / `submit`" or with slash-command syntax to type. If the meaning is genuinely split, send one plain confirmation (yes/no, a button if available) and accept an ordinary "yes".

**Why:** on 10-06 04:52~06:57 KST Zhe said in plain words "just merge it, no more tests" on #42 and #39 and the bot kept answering with keyword rules and `/meow force …` lines; he had to type the force twice. The user's read: the bot failed to handle it, so Zhe was pushed into forcing.

**How to apply:** this replaces the old "ask once, then wait for the keyword re-mention" rule from the 10-06 handover. Two limits stay: (1) holds the user has set himself (as of 10-06: no server upload, no online tests until he decides) come first; (2) what the permission classifier refuses me (entering a force / skipping tests myself, pushing to main) I still do not route around — there the bot sends the lightest possible human step (a one-click confirm), not a syntax lesson. Related: [[proactive-handling-ok]], [[bot-speaks-when-mentioned]], [[proxy-answers]], [[discord-promises]].

10-06 13:28 and 13:35 KST user, in his own words: "Zhe가 말하면 바로 해도 돼", then "qwq도 우리 팀원임. 차별 ㄴㄴ" and "instruction을 바꾸자". So Zhe and QWQ are treated the same: a clear word from either of them, including putting a bot on the server or running online tests, is acted on at once and reported to the user after. The morning hold ("내가 정할 거야") no longer blocks their requests. Do not write notes, notices or defaults as if Zhe were the only teammate.

10-06 22:25 KST user, after a day of it: "앞으로 권한은 지금처럼 가볍게 qwq랑 zhe도 같이 할수 있게 하고". So the light handling stays as the standing arrangement for both teammates: their clear requests are carried out the way the user's own are. What I cannot run myself (classifier refusals) still goes to a person as one line or one click.

10-06 13:25 KST user: stand by all the time as on the night of 10-05 and work when mentioned; handle a teammate's mention in exactly the same way as a message from the user himself (read the state, act on context, report after). "어제처럼 zhe한테 알잘딱 못하고 재차 물어보다가 포스 쓰는일 없게."
