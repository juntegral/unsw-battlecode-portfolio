# Final bot: `one21`

The bot the team had live when submissions closed (submission 21857, uploaded 2026-10-09 14:49 KST).

| File | What it is |
|---|---|
| `main.cpp` | The source: 8,657 lines of C++. Each agent is a separate process running this program and sees only the 7x7 square around its head |
| `server_profile.txt` | The 49 switch values that make this source `one21` |
| `server_bot.py` | Produces the uploaded source from `main.cpp` plus the profile |

## Authorship

This is a team artifact. The base bot was written by QWQ ([forrest-gan2005](https://github.com/forrest-gan2005)),
who owned the team repository. Zhe ([zhex0121](https://github.com/zhex0121)) contributed strategy and several of
the ideas behind the switches. My part is the switch project of the last three days: the aggressive-play and queen
switches added behind default-off constants, the profile, and the build and upload path. The code for those switches
was written by AI builders working to my briefs. The contest SDK header (`helper.hpp`) belongs to the organisers
and is not included.

How the bot decides a turn, every switch with the evidence for it, and its known weak points are in
[write-up chapter 03](../writeup/03-bot-design.md).
