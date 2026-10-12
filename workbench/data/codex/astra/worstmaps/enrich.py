import analyze as a
import json
rs=json.loads((a.OUT/'rows.json').read_text())
for r in rs:
 p=a.Path(r['path']);m=json.loads(p.with_name(f'game-{r["gid"]}.json').read_text());root=a.lr.agg.sb.load_replay(p).root()
 r.update(a.extra(root,m));print(r['gid'],r['map'],flush=True)
(a.OUT/'rows.json').write_text(json.dumps(rs,separators=(',',':')))
