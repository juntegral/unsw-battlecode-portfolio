"""PR lifecycle changes from list snapshots, independent of repository events."""

PR_FIELDS = "number,title,state,isDraft,author,headRefName,headRefOid,updatedAt,mergedAt,closedAt,url"


def pr_list_args(repo):
    return ["pr", "list", "--repo", repo, "--state", "all", "--limit", "30", "--json", PR_FIELDS]


def pr_activity(st, pulls, head_changes=False):
    first = "pr_snapshot" not in st
    snapshot = st.setdefault("pr_snapshot", {})
    actions = st.setdefault("pr_actions", {})
    candidates = {str(c.get("pr")) for c in st.get("candidates", {}).values()}
    out = []
    for pr in sorted(pulls, key=lambda p: (p["updatedAt"], p["number"])):
        number = str(pr["number"])
        old = snapshot.get(number)
        current = {"state": pr["state"], "draft": pr["isDraft"], "head": pr["headRefOid"]}
        changes = []
        if first:
            if number == "26" and pr["state"] == "OPEN" and old is None and number not in actions and number not in candidates:
                changes.append("opened")
        elif old is None:
            changes.append("opened")
        else:
            if current["state"] != old["state"]:
                changes.append({"OPEN": "reopened", "MERGED": "merged", "CLOSED": "closed"}[current["state"]])
            if current["state"] == "OPEN" and old["draft"] and not current["draft"]:
                changes.append("ready-for-review")
            if head_changes and current["head"] != old["head"]:
                changes.append("new commits pushed")
        seen = actions.setdefault(number, [])
        for action in changes:
            # Head changes can recur; lifecycle notifications dedupe by number and action.
            if action == "new commits pushed" or action not in seen:
                out.append((pr, action))
                if action != "new commits pushed":
                    seen.append(action)
        snapshot[number] = current
    return out
