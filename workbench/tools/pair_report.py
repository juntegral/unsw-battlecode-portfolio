#!/usr/bin/env python3
"""Summarise a finished smoke.py pair test from the server's game files.
usage: python3 tools/pair_report.py <label> [--post [card name]]
Reads data/online/smoke/<label>.json. The new bot is compared with the pooled live baseline:
every earlier pair run whose live half used the same submission, or another copy of the same code
(same source hash), on the same opponent + map.
--post sends a short summary via meowbot.
"""
import glob, json, os, subprocess, sys
from member_names import member_state, display_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "data/online/smoke")
US = 1119


def state(label):
    with open(os.path.join(SMOKE, label + ".json")) as source:
        return member_state(json.load(source))


def load(label, st, half):
    """(opponent, map) -> one game row of this half; {} when the half was not played."""
    ids = st["halves"][half]["battle_ids"]
    if not ids:
        return {}
    per = len(st["halves"][half]["batches"][0]["maps"])
    battles = [str(ids[i]) for i in range(0, len(ids), per)]
    out = f"smoke/{label}-{half}"
    files = lambda: glob.glob(os.path.join(ROOT, "data/online", out, "game-*.json"))
    if len(files()) < len(ids):
        subprocess.run(["node", os.path.join(ROOT, "tools/online.js"), "download", ",".join(battles), "--out", out,
                        "--purpose", f"pair {label} {half}"], capture_output=True, cwd=ROOT, timeout=1200)
    rows = {}
    for f in files():
        g = json.load(open(f))
        us = "a" if g["teamAId"] == US else "b"
        opp = g["teamBName"] if us == "a" else g["teamAName"]
        mine, theirs = (g["scoresA"], g["scoresB"]) if us == "a" else (g["scoresB"], g["scoresA"])
        rows[(opp, g["mapName"])] = dict(win=int(g["winner"] == us), us=mine or 0, them=theirs or 0)
    return rows


def source_hashes():
    """Submission id -> source hash: the saved map, refreshed from the server when it answers."""
    path = os.path.join(ROOT, "data/online/source-hashes.json")
    try:
        with open(path) as f:
            known = {str(k): v for k, v in json.load(f).items() if isinstance(v, str) and v}
    except (OSError, ValueError, AttributeError):
        known = {}
    try:
        listed = subprocess.run(["node", os.path.join(ROOT, "tools/online.js"), "submissions", "--all", "--json"],
                                capture_output=True, text=True, cwd=ROOT, timeout=120)
        fresh = {str(s["id"]): s["sourceHash"] for s in json.loads(listed.stdout)
                 if isinstance(s.get("sourceHash"), str) and s["sourceHash"]}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        fresh = {}
    if any(known.get(k) != v for k, v in fresh.items()):
        known.update(fresh)
        try:
            with open(path + ".tmp", "w") as f:
                json.dump(known, f, indent=1, sort_keys=True)
            os.replace(path + ".tmp", path)
        except OSError:
            pass
    return known


def baseline(live_id, shared_keys, hashes=None):
    """Pooled live-bot games: (opponent, map) -> rows from every complete live half with this submission
    or with another copy of the same code (same source hash, where the hash is known)."""
    pool, runs = {}, []
    hashes = hashes or {}
    live_hash = hashes.get(str(live_id))
    for path in sorted(glob.glob(os.path.join(SMOKE, "*.json"))):
        try:
            with open(path) as f:
                st = member_state(json.load(f))
            half = st["halves"]["old"]
        except (ValueError, KeyError, TypeError):
            continue
        planned = sum(len(b["maps"]) for b in half.get("batches", []))
        played = half.get("submission") or {}
        same = played.get("id") == live_id or (live_hash is not None and live_hash == (
            played.get("source_hash") or hashes.get(str(played.get("id")))))
        if st.get("kind") != "pair" or not same or not planned or len(half["battle_ids"]) != planned:
            continue
        name = os.path.basename(path)[:-5]
        rows = load(name, st, "old")
        if len(rows) != planned:
            continue
        used = [row for key, row in rows.items() if key in shared_keys]
        if used:
            runs.append((name, sum(r["win"] for r in used), len(used)))
        for key, row in rows.items():
            pool.setdefault(key, []).append(row)
    return pool, runs


def version_names(st):
    halves = st.get('halves', {})
    new = (halves.get('new', {}).get('submission') or {}).get('version')
    live = (halves.get('old', {}).get('submission') or {}).get('version')
    return (f'v{new}' if new is not None else None, f'v{live}' if live is not None else None)


def discord_message(ref, lines, splits, opponent_count, games, new=None, live=None):
    known = new is not None and live is not None
    baseline_name = live if known else 'live'
    def cells(split):
        live = split['live']
        return [split['opponent'][:18], f"{split['wins']}/{split['n']}",
                '-' if live is None else f"{live:.1f}/{split['n']}",
                f"{split['our_from']} → {split['our_to']}",
                f"{split['their_from']} → {split['their_to']}"]

    rows = []
    if opponent_count > 1:
        matched = [s for s in splits if s['live'] is not None]
        n = sum(s['n'] for s in matched)
        # Use the existing aggregate text to preserve its exact rounding.
        import re
        scores = re.findall(r"[0-9]+\.[0-9]+", lines[1])
        rows.append(['all', f"{sum(s['wins'] for s in matched)}/{n}",
                     f"{sum(s['live'] for s in matched):.1f}/{n}",
                     f"{scores[0]} → {scores[1]}", f"{scores[2]} → {scores[3]}"])
    rows.extend(cells(s) for s in splits)
    thin = [s['opponent'][:18] for s in splits if s['games'] < 30]
    first = f"📊 {ref} online result, same teams + maps"
    if known:
        first = f"📊 {new} = {live} main + {ref}, online result, same teams + maps"
    note = f"{baseline_name} baseline {games} games" + (' (thin, under 45)' if games < 45 else '')
    if thin:
        note += ' · thin for ' + ', '.join(thin)
    closing = '. about ±4 wins in 30 games is luck'
    header = ['opponent', 'wins new', 'wins live', 'our score', 'their score']
    if known:
        header[1:3] = [f'wins {new}', f'wins {live}']
    dropped = False
    def render():
        entries = [header] + rows + ([['…', '', '', '', '']] if dropped else [])
        widths = [max(len(r[i]) for r in entries) for i in range(5)]
        block = '\n'.join('  '.join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in entries)
        return first + '\n```\n' + block + '\n```\n' + note + closing
    while rows and len(render()) >= 1900:
        rows.pop()
        dropped = True
    if len(render()) >= 1900:
        note = f"{baseline_name} baseline {games} games" + (' (thin, under 45)' if games < 45 else '')
        if thin:
            note += ' · thin for …'
        budget = 1899 - len(render()) + len(first)
        first = first[:max(0, budget - 1)] + '…'
    return render()


def live_only_report(st, old, pool):
    avg = lambda rows, field: sum(r[field] for r in rows) / max(1, len(rows))
    lines = [f"live bot {len(old)} games | wins: {sum(r['win'] for r in old.values())}/{len(old)}",
             f"our avg score {avg(list(old.values()), 'us'):.1f} | their avg score {avg(list(old.values()), 'them'):.1f}"]
    available = {k[0] for k in old}
    order = [o['name'] for o in st.get('opponents', []) if o['name'] in available]
    order = list(dict.fromkeys(order + sorted(available - set(order))))
    splits = []
    for opp in order:
        keys = [k for k in old if k[0] == opp]
        rows = [old[k] for k in keys]
        pooled = [r for k in keys for r in pool.get(k, [])]
        wins = sum(r['win'] for r in rows)
        live = 15 * avg(pooled, 'win') if pooled else None
        splits.append(dict(opponent=opp, wins=wins, n=len(rows), live=live, games=len(pooled)))
        lines.append(f"vs {opp}: wins live {wins}/{len(rows)}"
                     f" | our avg score {avg(rows, 'us'):.1f} | their avg score {avg(rows, 'them'):.1f}"
                     + (f" | pooled wins {live:.1f}/15" if live is not None else " | pooled wins -/15")
                     + f" | pooled games {len(pooled)}")
    return lines, splits


def live_only_message(ref, splits, live=None):
    header = ['opponent', 'wins this run', 'pooled wins /15', 'pooled games']
    rows = [[s['opponent'][:18], f"{s['wins']}/{s['n']}",
             '-' if s['live'] is None else f"{s['live']:.1f}/15", str(s['games'])] for s in splits]
    first = f"📊 {ref}: the live bot's games. no bot swap or upload"
    if live is not None:
        first = f"📊 {live} main ({ref}): its games. no bot swap or upload"
    dropped = False
    def render():
        entries = [header] + rows + ([['…', '', '', '']] if dropped else [])
        widths = [max(len(r[i]) for r in entries) for i in range(4)]
        block = '\n'.join('  '.join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in entries)
        return first + '\n```\n' + block + '\n```'
    while rows and len(render()) >= 1900:
        rows.pop()
        dropped = True
    if len(render()) >= 1900:
        first = first[:max(0, 1898 - len(render()) + len(first))] + '…'
    return render()


def finish_report(label, argv, text, msg):
    text, msg = display_text(text), display_text(msg)
    with open(os.path.join(SMOKE, label + "-result.txt"), "w") as f:
        f.write(text + "\n")
    print(text)
    if "--post" in argv:
        p = os.path.join(ROOT, "data/guide", f"res-{label}.txt")
        with open(p, "w") as f:
            f.write(msg + "\n")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/meowbot.py"), "--announce-file", p], cwd=ROOT)


def main(argv):
    label = argv[1]
    st = state(label)
    new_name, live_name = version_names(st)
    new, old = load(label, st, "new"), load(label, st, "old")
    hashes = source_hashes()
    if st["rollback"].get("source_hash"):
        hashes[str(st["rollback"]["id"])] = st["rollback"]["source_hash"]
    pool, runs = baseline(st["rollback"]["id"], old if st.get('old_only') else new, hashes)
    if st.get('old_only'):
        lines, splits = live_only_report(st, old, pool)
        i = argv.index('--post') if '--post' in argv else len(argv)
        ref = argv[i + 1] if len(argv) > i + 1 else label
        finish_report(label, argv, "\n".join(lines), live_only_message(ref, splits, live_name))
        return
    avg = lambda rows, f: sum(r[f] for r in rows) / max(1, len(rows))
    ks = sorted(k for k in new if k in pool)
    bare = sorted(k for k in new if k not in pool)
    base = lambda K, f: sum(avg(pool[k], f) for k in K)
    n, games = len(ks), sum(len(pool[k]) for k in ks)
    lines = [f"new bot {n} games | wins: new {sum(new[k]['win'] for k in ks)}/{n} vs live {base(ks, 'win'):.1f}/{n}"
             f" (live baseline pooled over {games} games: " + ", ".join(f"{w}/{g}" for _, w, g in runs) + ")",
             f"our avg score {base(ks, 'us') / max(1, n):.1f} -> {avg([new[k] for k in ks], 'us'):.1f}"
             f" | their avg score {base(ks, 'them') / max(1, n):.1f} -> {avg([new[k] for k in ks], 'them'):.1f}",
             f"games where we scored 0: {sum(sum(r['us'] == 0 for r in pool[k]) / len(pool[k]) for k in ks):.1f} -> {sum(1 for k in ks if new[k]['us'] == 0)}"]
    both = sorted(set(old) & set(new))
    if both:
        plus = sum(1 for k in both if new[k]["win"] and not old[k]["win"])
        minus = sum(1 for k in both if old[k]["win"] and not new[k]["win"])
        lines.append(f"this run only, {len(both)} pairs | wins: live {sum(old[k]['win'] for k in both)} -> new {sum(new[k]['win'] for k in both)} (new only +{plus}, live only -{minus})")
    for opp in sorted({k[0] for k in bare}):
        K = [k for k in bare if k[0] == opp]
        lines.append(f"no live baseline yet vs {opp}: new {sum(new[k]['win'] for k in K)}/{len(K)} wins, our avg score {avg([new[k] for k in K], 'us'):.1f}, theirs {avg([new[k] for k in K], 'them'):.1f}")
    available = {k[0] for k in new}
    order = [o["name"] for o in st.get("opponents", []) if o["name"] in available]
    order = list(dict.fromkeys(order + sorted(available - set(order))))
    splits = []
    for opp in order:
        K = [k for k in ks if k[0] == opp]
        if not K:
            K = [k for k in bare if k[0] == opp]
            splits.append(dict(opponent=opp, wins=sum(new[k]['win'] for k in K),
                               n=len(K), live=None, games=0, our_from='-', their_from='-',
                               our_to=f"{avg([new[k] for k in K], 'us'):.1f}",
                               their_to=f"{avg([new[k] for k in K], 'them'):.1f}"))
            continue
        count = len(K)
        wins, live = sum(new[k]["win"] for k in K), base(K, "win")
        splits.append(dict(opponent=opp, wins=wins, n=count, live=live,
                           games=sum(len(pool[k]) for k in K),
                           our_from=f"{base(K, 'us') / count:.1f}",
                           our_to=f"{avg([new[k] for k in K], 'us'):.1f}",
                           their_from=f"{base(K, 'them') / count:.1f}",
                           their_to=f"{avg([new[k] for k in K], 'them'):.1f}"))
        lines.append(f"vs {opp}: wins new {wins}/{count} vs live {live:.1f}/{count}"
                     f" | our avg score {base(K, 'us') / count:.1f} -> {avg([new[k] for k in K], 'us'):.1f}"
                     f" | their avg score {base(K, 'them') / count:.1f} -> {avg([new[k] for k in K], 'them'):.1f}")
    table = []
    for m in sorted({k[1] for k in ks}):
        K = [k for k in ks if k[1] == m]
        table.append(f"  {m:18s} wins {base(K, 'win'):4.1f}->{sum(new[k]['win'] for k in K)} | ours {base(K, 'us'):6.1f}->{sum(new[k]['us'] for k in K):4d} | theirs {base(K, 'them'):6.1f}->{sum(new[k]['them'] for k in K):4d}")
    i = argv.index('--post') if '--post' in argv else len(argv)
    ref = argv[i + 1] if len(argv) > i + 1 else st.get('ref') or label
    prefix = [f'{new_name} = {live_name} main + {ref}'] if new_name and live_name else []
    text = display_text("\n".join(prefix + lines + table))
    with open(os.path.join(SMOKE, label + "-result.txt"), "w") as f:
        f.write(text + "\n")
    print(text)
    if "--post" in argv:
        msg = display_text(discord_message(ref, lines, splits, len(available), games, new_name, live_name))
        p = os.path.join(ROOT, "data/guide", f"res-{label}.txt")
        with open(p, "w") as f:
            f.write(msg + "\n")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/meowbot.py"), "--announce-file", p], cwd=ROOT)


if __name__ == "__main__":
    main(sys.argv)
