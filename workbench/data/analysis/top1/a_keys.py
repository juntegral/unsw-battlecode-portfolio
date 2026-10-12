import json, sys
g = sys.argv[1]
for d in ("q", "q2", "q3"):
    try:
        j = json.load(open(f"{d}/{g}.json"))
    except Exception as e:
        print(d, "ERR", e); continue
    print("==", d, type(j).__name__)
    if isinstance(j, dict):
        for k, v in j.items():
            s = json.dumps(v)
            print("  ", k, ":", s[:400])
