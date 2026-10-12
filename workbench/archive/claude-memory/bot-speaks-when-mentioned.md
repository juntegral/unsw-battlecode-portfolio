---
name: bot-speaks-when-mentioned
description: "user rule 10-06: never join a conversation between Zhe and QWQ; in #meow the bot answers a teammate only when it is mentioned (or a card is answered with /answer)"
metadata:
  type: feedback
---

In Discord #meow, stay out of what Zhe and QWQ say to each other. Answer a teammate's message only when it mentions the bot (`@meowbot`, user id 900000000000000001); card answers given with `/answer` are handled as before. Infra notices that nobody asked for (test results, a new live bot, a broken tool) are still fine.

**Why:** said 2026-10-06 00:07 KST, right after Claude had replied to a question Zhe had addressed to QWQ: "예정대로 zhe나 qwq의 대화에는 절대 끼지 마. 가능하면 멘션을 했을때만 대답하게 하는걸로." Claude deleted that reply within a minute and posted a correction to its earlier "just talk to me in the channel" note.

**How to apply:** a reply to one of the bot's own posts is not a mention if it addresses someone else. When a teammate's question to another teammate is something the tools could answer (a trace, a count), prepare it quietly and hold it until someone asks or mentions the bot; do not post it uninvited. The session watcher wakes only on bot mentions and `/answer` relays. Related: [[team-dynamics]], [[teammates-see-jun]], [[proactive-handling-ok]].

10-06 00:14 KST user, before signing off, on what a mention may ask for: everything jun himself could do must be doable when Zhe or QWQ ask with a mention ("내가 할수있는 모든 작업은 쟤네가 말을 걸어도 실제로 할 수 있게만 하면 돼"), including analysis of all battle data so far. Two conditions. (1) On every mention, first read the current state exactly (Discord, loop, the card, the server bot) before answering. (2) For actions that really need a confirmation (skipping tests, merging to main, uploading or rolling back the server bot), ask the requester once and act only after they mention the bot again with the trigger word given: `force`, `merge`, `submit` or `rollback`; record on the card who confirmed. Announced to the team at 00:14 (data/guide/px-howto.txt). Answers to teammates use the same style as reports to the user: conclusion first, numbers in a small table, short.

10-06 01:40 KST correction after a miss: the watcher had only matched an explicit `<@bot>` mention written by Zhe or QWQ, so a plain Discord reply to the bot's own message (Zhe, 01:30) and a mention by jun himself (01:35) both went unanswered for 10 minutes and the user had to prod ("너 왜 대답안해 감시 제대로 안해?"). Rule as it stands now: wake and answer on (a) a mention of the bot by anyone, jun included, (b) a reply to one of the bot's messages that does not address another teammate by mention, (c) an `/answer` relay. A reply to the bot that mentions another teammate is still theirs to answer.

10-06 01:45 KST user: "뭔가 고민이 필요한 경우에는 중간에 질문 답하기 전에 (thinking) 띄우고, 답 오면 그때 삭제후 답 올려. 고장난건지 우리입장에서는 모르니까." So when a teammate's question takes more than a moment, a "(thinking)" message goes up first and is deleted when the answer is posted. Implemented: `unsw-swarm/tools/meow_think.py start|done`; the session watcher calls `start` the moment it sees a mention or a reply to the bot, and every answer is posted as `meowbot.py --announce-file … && meow_think.py done`. Never leave a "(thinking)" note standing: if no answer can be given, delete it and say why.

10-06 12:20 KST user: the "ask once, then wait for a keyword re-mention (`force`, `merge`, `submit`, `rollback`, `ranked`)" condition above is withdrawn. A clear request is acted on and reported after; see [[act-on-context]].
