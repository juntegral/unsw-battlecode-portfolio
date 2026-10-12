#!/usr/bin/env python3
"""Offline target counting; original counters with only input/team adapters."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import importlib.util
import json
import gzip
import subprocess
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
DOS = ROOT / 'data/analysis/ladder/dossier'
OUT = DOS / 'target'
sys.path.insert(0, str(ROOT / 'tools'))
import ladder_replay as lr
from ladder_rows import signature


def fast_load(path):
    packed=Path(path).read_bytes()
    if packed[:2]==b'\x1f\x8b': packed=gzip.decompress(packed)
    raw=subprocess.run([str(OUT/'tg_unpack')],input=packed,stdout=subprocess.PIPE,check=True).stdout
    return lr.replay.Message(raw)


def prepare_decoder():
    source=DOS/'work/tg_unpack.c'
    binary=OUT/'tg_unpack'
    subprocess.run(['cc','-O2','-Wall','-Wextra',str(source),'-o',str(binary)],check=True)
    samples=sorted((ROOT/'data/online/top1').glob('*/M*.replay'))[:3]
    for path in samples:
        packed=path.read_bytes()
        if packed[:2]==b'\x1f\x8b': packed=gzip.decompress(packed)
        native=subprocess.run([str(binary)],input=packed,stdout=subprocess.PIPE,check=True).stdout
        assert native==lr.replay.unpack_packed(packed),path
    lr.replay.load=fast_load
    print('Native packed decoder matches original bytes on 3 replays',flush=True)


def load_counter():
    source = DOS / 'count_dossier.py'
    spec = importlib.util.spec_from_file_location('tg_dossier', source)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tree = ast.parse(source.read_text())
    scan = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'scan')
    replacements = {
        "path = ROOT / 'data/online/ladder' / str(row['battle']) / ('M%d.replay' % row['game'])":
            "path = ROOT / row['replay']",
        "assert metadata['team' + ours + 'Id'] == 1119":
            "assert metadata['team' + ours + 'Id'] == 306",
        "team='meow' if s == 'us' else row['opponent']":
            "team='Vibing++' if s == 'us' else row['opponent']",
    }
    code = ast.get_source_segment(source.read_text(), scan)
    for old, new in replacements.items():
        assert code.count(old) == 1, old
        code = code.replace(old, new)
    exec(compile(code, str(source), 'exec'), mod.__dict__)
    tree = ast.parse(Path(lr.__file__).read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'scan')
    class TeamAdapter(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant(306), node) if node.value == 1119 else node
    fn = TeamAdapter().visit(fn)
    ns = dict(lr.__dict__)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), lr.__file__, 'exec'), ns)
    return mod, ns['scan']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task(args):
    items, adapters_hash = args
    lr.replay.load=fast_load
    mod, scan = load_counter()
    geo = None
    summaries = []
    for item in items:
        path, meta, key, sig = item
        gid = meta['id']
        cache = OUT / 'cache' / f'{gid}.json'
        hashes = dict(replay=sha(path), metadata=sha(path.with_name(f'game-{gid}.json')), counters=adapters_hash)
        if cache.exists() and json.loads(cache.read_text())['hashes'] == hashes:
            summaries.append(str(cache.relative_to(ROOT)))
            continue
        g = scan(path, meta, str(path.parent), set())
        side = g['ours']
        other = 'B' if side == 'A' else 'A'
        row = dict(game=gid, battle=path.parent.name, replay=str(path.relative_to(ROOT)),
                   map_key=key, map=meta['mapName'], map_version=key.rsplit('#', 1)[-1],
                   opponent_rating=meta.get('team'+other+'Elo'), opponent=meta.get('team'+other+'Name'),
                   our_side=side, result='draw' if g['winner'] is None else 'win' if g['winner']==side else 'loss',
                   last_round=g['last_round'], ended_by=str(g['end_reason']),
                   final={s:{k:g['final'][s][k] for k in ('alive','longest','total','queen_length')} for s in mod.SIDES},
                   curves={str(n):g['snapshots'].get(n) for n in (50,100,200,300)},
                   queen={s:dict(death_round=next((d['round'] for d in g['deaths'] if d['id']==g['queens'][s]),None),
                                 alive_end=g['final'][s]['queen_alive']) for s in mod.SIDES})
        row['curves']['end'] = g['final']
        rows, check, geo = mod.scan(row, geo)
        extra = {s:{w:Counter() for w in ('0-100','101-300','game')} for s in mod.SIDES}
        root = lr.replay.load(path).root()
        teams = {}
        for line in root.text(0).splitlines():
            q = line.split()
            if q and q[0]=='DRAGON': teams[len(teams)]='AB'[int(q[1])]
        rnd = 0
        for ev in root.pointer(3):
            kind = ev.u16(0)
            if kind not in (0,1,10): continue
            p = ev.pointer(0)
            if kind==0: rnd=p.i32(0)
            elif kind==10: teams[p.i32(4)]='AB'[p.u16(8)]
            else:
                s='us' if teams[p.i32(0)]==side else 'them'
                extra[s]['game']['turns']+=1
                if rnd<=300: extra[s]['0-100' if rnd<=100 else '101-300']['turns']+=1
        for rnd,s in g['eaten_rounds']:
            extra[s]['game']['eaten']+=1
            if rnd<=300: extra[s]['0-100' if rnd<=100 else '101-300']['eaten']+=1
        for pearl in g['pearls']:
            if pearl['eater']=='nobody': continue
            s,rnd=pearl['eater'],pearl['eat_round']
            extra[s]['game']['drop_eaten']+=1
            if rnd<=300: extra[s]['0-100' if rnd<=100 else '101-300']['drop_eaten']+=1
        for r in rows:
            s=r['relation']
            assert extra[s]['game']['eaten']==r['game_counts']['pearls_eaten']
            for w in ('0-100','101-300'):
                assert extra[s][w]['turns']==r['ranges'][w]['turns']
                assert extra[s][w]['eaten']==r['ranges'][w]['pearls_eaten']
        payload=dict(hashes=hashes, metadata=meta, layout_signature=sig, rows=rows, validation=check, extra=extra)
        cache.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n')
        summaries.append(str(cache.relative_to(ROOT)))
        print(f'Counted {gid} {key}', flush=True)
    return summaries


def main():
    OUT.mkdir(exist_ok=True)
    (OUT/'cache').mkdir(exist_ok=True)
    prepare_decoder()
    sources=[DOS/'count_dossier.py', DOS/'losses/counts/count_replays.py', ROOT/'tools/ladder_replay.py',
             ROOT/'tools/ladder_rows.py', Path(__file__), DOS/'work/tg_unpack.c']
    sources[1]=DOS.parent/'losses/counts/count_replays.py'
    adapters_hash=hashlib.sha256(''.join(sha(p) for p in sources).encode()).hexdigest()
    originals=[json.loads(s) for s in (DOS/'per-game.jsonl').read_text().splitlines()]
    known={}
    for r in originals:
        if r['relation']=='us' and r['layout_key'] not in known.values():
            sig=signature(lr.replay.load(ROOT/r['replay']).root().text(0))
            assert (r['map_name'],sig) not in known
            known[r['map_name'],sig]=r['layout_key']
    candidates=[]; excluded=[]; missing=[]
    for path in sorted((ROOT/'data/online/top1').glob('*/M*.replay')):
        gid=int(path.stem[1:]); mp=path.with_name(f'game-{gid}.json')
        if not mp.exists(): missing.append(str(path.relative_to(ROOT))); continue
        meta=json.loads(mp.read_text())
        if 306 not in (meta['teamAId'],meta['teamBId']): excluded.append(gid); continue
        assert (meta['teamAId']==306)+(meta['teamBId']==306)==1
        sig=signature(lr.replay.load(path).root().text(0))
        key=known.get((meta['mapName'],sig),f"{meta['mapName']} #target-{sig}")
        candidates.append((path,meta,key,sig))
    assert len({m['id'] for p,m,k,s in candidates})==len(candidates)
    groups={}
    for item in candidates: groups.setdefault(item[2],[]).append(item)
    snapshot=dict(target_team_id=306, target_team='Vibing++', replay_files=len(candidates)+len(excluded)+len(missing),
                  selected_games=len(candidates), excluded_non_target=excluded, missing_metadata=missing,
                  inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},
                  layouts={k:len(v) for k,v in groups.items()}, signature_definition='tools/ladder_rows.py signature: size, edges, starting dragons; team-colour swap invariant')
    (OUT/'input-snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    files=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(task,(items,adapters_hash)) for items in groups.values()]
        for future in as_completed(futures): files.extend(future.result())
    rows=[]; extra={}; checks=[]; metadata=[]
    for file in sorted(files):
        saved=json.loads((ROOT/file).read_text())
        rows.extend(saved['rows']); checks.append(saved['validation']); metadata.append(saved['metadata'])
        extra[str(saved['metadata']['id'])]=saved['extra']
    rows.sort(key=lambda r:(r['game'],r['relation']))
    assert len(rows)==2*len(candidates)
    (OUT/'per-game-top1.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows))
    (OUT/'recount.json').write_text(json.dumps(extra)+'\n')
    (OUT/'validation.json').write_text(json.dumps(dict(games=len(checks),checks=checks,metadata=metadata),indent=2)+'\n')
    assert snapshot['inputs_sha256']=={str(p.relative_to(ROOT)):sha(p) for p in sources}
    print(f'Validated {len(checks)} target games / {len(rows)} sides',flush=True)


if __name__=='__main__': main()
