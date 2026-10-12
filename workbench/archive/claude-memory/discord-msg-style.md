---
name: discord-msg-style
description: user rule 10-03 — every English Discord draft comes with a Korean translation; keep drafts short and abstract, not detailed
metadata:
  type: feedback
---

When drafting English messages for the team Discord, always give a Korean translation right below. Keep the message abstracted (direction and key point), not file-level detail.

**Why:** 10-03 the user asked for translations every time and said my drafts were too detailed.

**How to apply:** English draft (short, casual) → "번역:" Korean version. Details go in PRs/issues, not chat. Related: [[discord-first]], [[report-in-korean]].

Shortcut (10-03): when the user says "디코 번역", sync Discord and immediately give a Korean translation of the whole current message flow.

Format (user 10-03): never wrap Discord drafts in blockquotes (`>`) — the quote bar got pasted into Discord as "▎". Put the English draft inside a plain fenced code block (```), written in Discord markdown (**bold**, - bullets, `code`), so it copies verbatim; the Korean translation goes below as plain text, not quoted.

10-03 permanent: drafts must sound like the team talks in #meow: casual, short sentences, lowercase ok, "tbh/lmk/sounds good", light emoji at most. No office/report tone, no headers or bold labels, minimal bullets.

10-03 (permanent): write like a teammate talking, chosen from context each time: relaxed when the moment is relaxed, a bit of wit welcome. No lab-report jargon in casual talk. No fixed phrase list or mechanical translations; just write it naturally. Applies to Discord and to GitHub summaries.

10-04: Discord replies are a conversation, not a finished plan. Share one opinion and maybe one question, then let teammates respond. Don't lay out the whole design in one message (the user called that playing ping-pong with yourself).
10-04: don't open every reply with "agreed / yeah fair / you're right". Be cool about it and only say it now and then. Also double-check who said the message before addressing anyone.
10-04: don't end messages fishing for a specific answer ("worth it?", "ok with that?", "sound good?", "lmk"). It reads like an AI waiting for approval. State the plan or the thought plainly ("gonna merge it before the loop starts, shout if something's off" or just the statement). Ask a question only when we genuinely need their input, and make it open.

10-05 03:28 KST user: "답변에 콜론 좀 자제 부탁할게 ... 말투 교정좀 하자." Discord drafts had a colon in almost every line ("that explains portals: ...", "which one did you see: ..."). Write drafts as plain chat sentences: end the clause with a full stop or a comma and start a new sentence instead of using a colon. Keep colons only where unavoidable (a URL, a time, "r132"-style labels are fine). Same for the Korean translation under the draft.

10-05 20:17 KST user, about a meowbot post that gave replay counts as sentences ("against test4 … 3 of 15 … 12 of 15 …"): "이거 좀 가독성 별로라서 디코 표 형태로 진행하면 될것 같아. 전에 했던 그 야매 표 느낌". So numbers that compare things (builds, opponents, causes) go to Discord as a small monospace table inside a ``` code block with aligned columns, one plain sentence above for what it is and one below for what it means. Sentences are for the reading, not for carrying four numbers each. Applies to meowbot posts and to drafts for the user. Done the same day: the automatic online result post (`tools/pair_report.py --post`) was changed to this table form.

10-05 20:59 KST user: "앞으로는 봇 버전으로 같이 적었으면 좋겠어. 저거는 또 #번호니까 좀 헷갈리는 감이 있기는 하네". When a post or report talks about a bot that ran online, name it by its portal version first (v26, v22 main) and put the card number second ("v26 = v22 main + queen-hunt (#31)"). `node tools/subs.js list` in unsw-swarm prints version, submission id, name and description. Card numbers alone are for talk about the card, not about a bot.

10-07 03:3x KST user, about the two meowbot answers to Zhe (tower_defense feeding, queen deaths after r300): two faults. (1) "제발 멘션좀 해 답변자한테" — an answer must tag the person it answers (<@id>), a bare "Zhe, …" does not notify them. Zhe 900000000000000002, QWQ 900000000000000003, jun 900000000000000005. Exception that still stands: park_watch swap notices carry no tag (Zhe 02:24). (2) "가독성이 똥임 … 공지나 답변 앞에 구분선 용도로 임티라도 하나 넣어" — every notice or answer opens with one emoji as a visual divider, and walls of bullets are out. My reading of how to fix (2): 💬 for answers, 📢 for notices, one-line conclusion first, then at most one table and 3–4 short lines; detail goes to a follow-up only if asked.
