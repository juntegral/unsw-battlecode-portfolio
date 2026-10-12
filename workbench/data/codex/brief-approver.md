# Brief: author labels on ideas + two-person approval in meowbot

Repo: unsw-swarm. File: tools/meowbot.py. Read data/codex/report-approve-merge-submit.md for the current approve = merge + submit flow.
Team repo: forrest-gan2005/battlecode. Labels already exist there: by:zhe, by:qwq, by:junsing, by:ai.
Members (MEMBERS dict): 준싱 → by:junsing, Zhe → by:zhe, QWQ → by:qwq.

## Rule (team decision)
- Every idea card carries who proposed it as a `by:*` label.
- A candidate built from human ideas needs TWO OKs: the idea's author plus one other member.
- A candidate built only from AI ideas (`by:ai`) needs ONE OK from any member. Promotion by the AI counts as the author's OK.

## Changes
1. `/hypo` (and anything else in meowbot that creates an [Idea] issue):
   - add the `by:<member>` label of the Discord user who submitted it;
   - if the text says the idea is someone else's (an optional "Idea by" field, if the modal has one), use that member instead;
   - `/board-edit` may change it.
   Add a small helper so loops can tag AI cards with `by:ai` (document it in the docstring; loops use `gh issue edit N --add-label by:ai`).
2. Candidate card (open PR with candidates/*.json, manifest field "issues"):
   - Read the by:* labels of the linked issues once when the card is posted and store them in state.
     Fallback when there is no label: parse a `**Idea by:** X` line in the card body. If that also fails, treat it as a human idea with an unknown author and require two different members.
   - Show "Idea by: … · needs: author + 1 other" (or "needs: 1 member" for AI-only), and list the current OKs.
   - Button [OK] for any member records a vote; pressing again does nothing.
   - Button [Hold] works as now.
   - When the rule is satisfied:
     - Human ideas: at least one OK from an author of any linked idea, plus at least one OK from a non-author.
       With several human authors, one author OK is enough.
     - Mixed human + AI candidates follow the human rule.
     The member whose vote completed it gets the existing ephemeral confirm. On Confirm, run the existing lock → SHA check → merge → sync_release(merge commit) → upload path.
     If they cancel, keep the votes; the next voter (or the same one, by pressing again) gets the confirm.
   - Update the card after each vote.
3. Keep the UPLOAD_ENABLED gate, lock, SHA check and merge-commit submit unchanged. A new head SHA resets the votes; say so on the new card.
4. Update the docstring and footer.

## Constraints
- Do not run, restart or kill the bot.
- No keys printed.
- No real merge, push, commit, submit or gh write calls while testing; use fake gh as before.
- py_compile must pass.
- Add offline checks covering:
  - an author OK then a non-author OK triggers the confirm;
  - two non-authors don't trigger it;
  - AI-only with one OK triggers it;
  - a double click is ignored;
  - an SHA change resets the votes;
  - the label fallbacks.

Leave the changes uncommitted. Write data/codex/report-approver.md, under 20 lines.
