#!/usr/bin/env python3
"""c_gamestab.py: write c_p_games.md, the table of games read in sub-session A3 (ids are listed in this file).

For our own games the table also gives the run (battle id in games.csv) and what is known about the bot build of that
run: "-old" smoke runs and the ladder downloads are the live bot of that hour; tc30-test-new is the candidate with
TRADE_CONTACT (source kept in data/online/smoke/tc30-bot), which differs from the live bot only on maps over 1,200
cells; qh31-test-new is the candidate with QH_SCOUT (queen hunt, source in qh31-bot); passage2-test-new is a candidate
whose source was not kept.
"""
import csv

GAMES = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
NAMES = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow", 19: "test4", 87: "WeHaveQuizzes"}
# (game id, team read (id), how it was read)
READ = [
    ("1058144", 1119, "tables, board r40, pocket tiles"), ("1067904", 1119, "tables"), ("1068050", 1119, "tables, ledger to r349"),
    ("1021860", 1119, "tables"), ("1046985", 264, "tables"), ("1046528", 91, "tables"), ("1069883", 264, "tables"), ("1054789", 306, "tables"),
    ("1063012", 1119, "tables"),
    ("1067905", 1119, "tables, ledger to r349"), ("1068051", 1119, "tables, events r8-24 and r19-24, fountain tiles, length classes r100-349, dragon list r140-220"),
    ("1063671", 1119, "tables"), ("1062235", 264, "tables"), ("1051826", 91, "tables"), ("1046989", 264, "tables"),
    ("1063016", 1119, "tables"),
    ("1068055", 1119, "tables"), ("1067909", 1119, "tables, fountain tiles, boards r22 and r28, events r22-30"), ("1063675", 1119, "tables"),
    ("1064304", 91, "tables"), ("1062237", 264, "tables"),
    ("1063252", 1119, "tables"),
    ("1067917", 1119, "tables, death cells, splits"), ("1068063", 1119, "tables, ledger"), ("1063024", 1119, "tables"),
    ("1051824", 91, "tables, death cells, fountain tiles"), ("1046988", 264, "tables, splits"), ("1054792", 306, "tables"),
    ("1067915", 1119, "tables"), ("1068061", 1119, "tables"), ("1063774", 1119, "tables"), ("1046991", 264, "tables"), ("1054786", 91, "tables"),
    ("1067906", 1119, "tables"), ("1068052", 1119, "tables, fountain tiles"), ("1063672", 1119, "tables"), ("1046984", 264, "tables"),
    ("1046526", 91, "tables"), ("1069373", 91, "tables"),
    ("1067908", 1119, "tables"), ("1068054", 1119, "tables"), ("1046992", 264, "tables"), ("1051827", 91, "tables"), ("1070191", 264, "tables"),
    ("1067907", 1119, "tables, events r0-34, board r18"), ("1068053", 1119, "tables"), ("1059076", 1119, "tables"), ("1046977", 264, "tables"),
    ("1062236", 264, "tables"),
    ("1063682", 1119, "tables, fountain tiles, board r60"), ("1063251", 1119, "tables"), ("1067916", 1119, "tables"), ("1046982", 264, "tables"), ("1062234", 264, "tables"),
    ("1064306", 91, "tables"),
]


def build(g):
    bid = g["battle_id"]
    big = int(g["cells"]) > 1200
    if bid.startswith("dl-"):
        return "ladder: live bot"
    if bid.endswith("-old"):
        return f"`{bid}`: live bot"
    if bid.startswith("tc30"):
        return f"`{bid}`: test build, trade on contact" + ("" if big else " (same as live on this map)")
    if bid.startswith("qh31"):
        return f"`{bid}`: test build, queen hunt"
    return f"`{bid}`: test build"


n_ours = sum(1 for _, t, _ in READ if t == 1119)
sizes = {"large": 0, "medium": 0, "small": 0}
for gid, _, _ in READ:
    ms = GAMES[gid]["map_size"]
    sizes["small" if ms.startswith("small") else "medium" if ms.startswith("medium") else "large"] += 1
big_ours = [(gid, GAMES[gid]["battle_id"]) for gid, t, _ in READ if t == 1119 and int(GAMES[gid]["cells"]) > 1200]
n_big = len(big_ours)
n_tc = sum(1 for _, b in big_ours if b.startswith("tc30"))
out = ["## Games read", "",
       f"{len(READ)} games: {sizes['large']} on large maps, {sizes['medium']} on medium, {sizes['small']} on small; {n_ours} of ours and {len(READ) - n_ours} of the top three with the same opponents. \"Tables\" = the per-10-round tables of",
       "`c_econ.py` for rounds 0-150 (both sides), kept as `c_out/ec_<id>.txt`; the large-map games also for rounds 150-350 (`c_out/ecm_<id>.txt`).",
       "Every game was read for both sides, so the opponent in each of our games (test4, WeHaveQuizzes) is read as well.",
       "The column \"end\": `wipe-out rN` = one team had no dragon left at round N. Otherwise the game runs 500 rounds and the team with",
       "the longer queen wins, a dead queen counting as 0 (`queen rule`); if that is a tie (both dead, as a rule), the team with the",
       "longest living dragon (`longest`).",
       "The column \"run and build\" is for our own games: the run the game came from (`c_batches.py`) and what bot played it; see",
       f"\"Which bot played\" above. On large maps {n_tc} of the {n_big} games of ours read are from the trade-on-contact test build.", "",
       "| # | game id | map | size | team read | side | opponent (elo) | result | end | final units / total / longest, own vs opponent | run and build (our games) | read with |",
       "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i, (gid, team, how) in enumerate(READ, 1):
    g = GAMES[gid]
    s = "A" if int(g["teamAId"]) == team else "B"
    o = "B" if s == "A" else "A"
    size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
    opp = NAMES.get(int(g[f"team{o}Id"]), g[f"team{o}Name"][:18])
    res = "win" if g["winner"] == s else "loss"
    end = g["end_type"] + (f" r{g['rounds']}" if g["rounds"] != "500" else "")
    fin = (f"{g[f'final_units_{s}']} / {g[f'final_total_length_{s}']} / {g[f'final_longest_length_{s}']} vs "
           f"{g[f'final_units_{o}']} / {g[f'final_total_length_{o}']} / {g[f'final_longest_length_{o}']}")
    run = build(g) if team == 1119 else "-"
    out.append(f"| {i} | {gid} | {g['map']} | {size} | {NAMES[team]} | {s} | {opp} ({float(g[f'team{o}Elo']):.0f}) | {res} | {end} | {fin} | {run} | {how} |")
open("c_p_games.md", "w").write("\n".join(out) + "\n")
print("c_p_games.md written,", len(READ), "games;", n_ours, "of ours; large-map games of ours:", n_big,
      "of which trade-on-contact build:", n_tc)
