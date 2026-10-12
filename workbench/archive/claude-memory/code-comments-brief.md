---
name: code-comments-brief
description: User rule (2026-10-01 23:3x) — when writing code, keep comments short and simple
metadata:
  type: feedback
---

User, 2026-10-01 ~23:33 KST: "앞으로는 코드 작성하는 경우에 가능하면 주석을 간단하게만 적어줘. 기존에도 그냥 간단하게만 적었으면 상관 없고."

**Why:** the bot code is shared with other people. The existing comments in unsw-swarm (params.hpp, plan.cpp) are long, essay-like rationale lines.
**How to apply:** new code gets one short line per non-obvious item, with no history or rationale essays in comments; rationale belongs in VERSION.md and DECISIONS.md. Tell agents and Codex the same in briefs (AGENTS.md has the rule). Don't rewrite old comments unless asked, but offer a cleanup pass for a shared copy.
