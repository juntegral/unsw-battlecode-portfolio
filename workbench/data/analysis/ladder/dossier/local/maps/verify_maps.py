"""Copy exact local originals and inspect engine initialization, without bot actions."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from wasmtime import Store, WasiConfig, Linker, FuncType, ValType
from unswbc.engine import EngineModule

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
PROJECTS = ROOT.parent
sys.path.insert(0, str(PROJECTS / 'battlecode'))
import replay
sys.path.insert(0, str(ROOT / 'tools'))
from ladder_replay import canonical_edges

TARGETS = [('Islands #1', 'islands_1'), ('Australia #1', 'australia_1'),
           ('Around UNSW #1', 'around_unsw_1'), ('Slithery Fight #1', 'slithery_fight_1'),
           ('Schooltime #1', 'schooltime_1'), ('Schooltime #2', 'schooltime_2')]


def state(text):
    w = h = None
    tiles, edges, dragons, extra = {}, [], [], []
    for line in text.splitlines():
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'TILE':
            x, y, lo, hi = map(int, q[1:5])
            tiles[x, y] = lo, hi
        elif q[0] == 'EDGE':
            edges.append(tuple(map(int, q[1:4])))
        elif q[0] == 'DRAGON':
            team, n = map(int, q[1:3])
            assert len(q) == 3 + 2*n
            dragons.append((team, tuple(zip(map(int, q[3::2]), map(int, q[4::2])))))
        elif q[0] not in ('MAP_NAME', 'TILE_COUNT', 'EDGE_COUNT', 'DRAGON_COUNT', 'END'):
            extra.append(line)
    assert len(tiles) == w*h
    edges = canonical_edges(w, h, edges)
    pairs = defaultdict(list)
    for edge, (kind, pid) in edges.items():
        if kind == 2:
            pairs[pid].append(edge)
    assert all(len(p) == 2 for p in pairs.values())
    return dict(size=(w, h), walls=sorted(e for e, kp in edges.items() if kp[0] == 1),
                portals=sorted(tuple(sorted(p)) for p in pairs.values()),
                edges=sorted(edges.items()), dragons=dragons, tiles=sorted(tiles.items()),
                metadata=sorted(extra))


def same_layout(a, b):
    if any(a[k] != b[k] for k in ('size', 'edges', 'tiles', 'metadata')):
        return False
    aa = sorted(a['dragons'])
    return aa == sorted(b['dragons']) or aa == sorted((1-t, body) for t, body in b['dragons'])


class InitializationComplete(Exception):
    pass


def engine_load(data, seed=0):
    engine = EngineModule()
    store = Store(engine._engine)
    wasi = WasiConfig()
    notices, spawns = [], []
    wasi.stderr_custom = lambda b: (notices.append(b.decode(errors='replace')) or len(b))
    store.set_wasi(wasi)
    linker = Linker(engine._engine)
    linker.define_wasi()
    i32 = ValType.i32()
    holder = {}
    calls = 0

    def before_action(*args):
        nonlocal calls
        calls += 1
        raise InitializationComplete()

    def spawned(dragon_id, ptr, length):
        spawns.append((dragon_id, bytes(holder['memory'].read(store, ptr, ptr + length)).decode()))

    linker.define_func('unswbc', 'bot_reply', FuncType([i32]*5, [i32]), before_action)
    linker.define_func('unswbc', 'log', FuncType([i32]*3, []), lambda *a: None)
    linker.define_func('unswbc', 'bot_spawn', FuncType([i32]*3, []), spawned)
    exports = linker.instantiate(store, engine._module).exports(store)
    exports['_initialize'](store)
    memory = holder['memory'] = exports['memory']
    ptr = exports['ubc_alloc'](store, len(data))
    memory.write(store, data, ptr)
    out = exports['ubc_alloc'](store, 48)
    try:
        code = exports['ubc_run'](store, ptr, len(data), 0, seed, out)
    except InitializationComplete:
        pass
    else:
        raise AssertionError(('loader did not reach initialization boundary', code,
                              engine._read_error(store, exports, memory)))
    assert calls == 1
    size = exports['ubc_replay'](store, 0, 0, 0, 0)
    assert size > 0
    base = exports['ubc_replay_ptr'](store)
    root = replay.Message(replay.unpack_packed(bytes(memory.read(store, base, base + size)))).root()
    events = list(root.pointer(3))
    names = Counter(replay.EVENT_NAMES[e.u16(0)] for e in events)
    assert not any(names[k] for k in ('dragonAction', 'dragonSplit', 'dragonDeath'))
    loaded = state(root.text(0))
    updates = [e.pointer(0) for e in events if replay.EVENT_NAMES[e.u16(0)] == 'dragonUpdate']
    assert len(updates) == len(loaded['dragons'])
    for update in updates:
        team, body = loaded['dragons'][update.i32(0)]
        assert replay.point(update.pointer(0)) == body[0]
        assert replay.point(update.pointer(1)) == body[-1]
    limits = sorted({int(line.split()[1]) for _, block in spawns
                     for line in block.splitlines() if line.startswith('UNIT_LIMIT ')})
    return state(root.text(0)), dict(unit_limits=limits, spawns=len(spawns),
                                     event_counts=dict(names), actions=0, notices=notices)


def main():
    rows = defaultdict(dict)
    for line in (OUT.parents[1] / 'per-game.jsonl').read_text().splitlines():
        r = json.loads(line)
        if r['layout_key'] in dict(TARGETS):
            rows[r['layout_key']][r['replay']] = r
    paths = subprocess.check_output(['rg', '--files', str(PROJECTS),
                                     '~/meow-redteam', '-g', '*.map'], text=True).splitlines()
    candidates = []
    for path in sorted(paths, key=lambda p: ('official127' not in p, 'variants_sq' in p, p)):
        p = Path(path)
        if p.is_relative_to(OUT):
            continue
        try:
            s = state(p.read_text())
        except (ValueError, AssertionError, UnicodeError, IndexError, TypeError):
            continue
        if s['size'][0]*s['size'][1] > 1200:
            candidates.append((p, s))
    results = []
    for key, slug in TARGETS:
        refs = list(rows[key])
        assert len(refs) >= 2
        first = state(replay.load(ROOT / refs[0]).root().text(0))
        matches = [(p, s) for p, s in candidates if same_layout(first, s)]
        target = OUT / ('ladder_' + slug + '.map')
        if matches:
            source, original = matches[0]
            data = source.read_bytes()
        else:
            source, original = ROOT / refs[0], first
            data = (replay.load(source).root().text(0).rstrip() + '\n').encode()
        target.write_bytes(data)
        loaded, diagnostics = engine_load(data)
        assert same_layout(original, loaded)
        checks = []
        for ref in refs:
            expected = state(replay.load(ROOT / ref).root().text(0))
            # A/B are randomized by the server; select two with exactly the loaded labels.
            if loaded['dragons'] != expected['dragons']:
                continue
            equal = {k: ('equal' if loaded[k] == expected[k] else 'differs')
                     for k in ('size', 'walls', 'portals', 'dragons', 'tiles', 'edges', 'metadata')}
            assert all(v == 'equal' for v in equal.values()), (key, ref, equal)
            checks.append(dict(replay=ref, result=equal))
            if len(checks) == 2:
                break
        assert len(checks) == 2, ('need two exact-team replays', key)
        result = dict(layout=key, file=target.name, source=str(source),
                      sha256=hashlib.sha256(data).hexdigest(), size=loaded['size'],
                      cells=loaded['size'][0]*loaded['size'][1],
                      dragons_per_side=dict(Counter('AB'[t] for t, b in loaded['dragons'])),
                      check=checks, engine=diagnostics)
        results.append(result)
        print(key, result['size'], 'equal x2', diagnostics, flush=True)
    (OUT / 'checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
    lines = ['# 래더 지도 6개', '',
             '정확히 일치하는 기존 .map을 우선 탐색했다. 없으면 기보의 전체 시작 지도 헤더를 그대로 추출했다. 셀 수는 전체 격자 기준이다.',
             '각 지도는 엔진 1.2.7 WASM 로더로 초기화하고 첫 행동 요청에서 중단했다(행동 0).',
             '검증은 서로 다른 두 래더 기보의 r0와 대조했다. 아래 S/W/P/D/T는 크기/벽/포털 쌍/양팀 전체 몸/진주 생성 타일이다.',
             '전체 변(켈프·랩 경계 포함), SYMMETRY도 모두 equal. A/B와 id 순서까지 같은 기보 두 개를 선택했다.',
             '상세 기보 경로·항목별 결과·해시는 `checks.json`, 재검증은 지정 venv로 `python3 -B verify_maps.py`.', '',
             '| 지도 파일 | 크기 | 셀 | A/B 마리 | 원본 | 두 기보 S/W/P/D/T |',
             '|---|---:|---:|---:|---|---|']
    for r in results:
        lines.append(f"| {r['file']} | {r['size'][0]}×{r['size'][1]} | {r['cells']} | {r['dragons_per_side']['A']}/{r['dragons_per_side']['B']} | {r['source']} | equal/equal/equal/equal/equal ×2 |")
    lines += ['', '형식과 재현 한계:',
              '- TILE의 두 값은 생성 간격 min/max다. 고정 주기·위상이나 기보의 RNG 상태/실제 첫 생성 카운트다운은 저장하지 않는다.',
              '- 켈프는 EDGE kind 1, 포털은 kind 2와 연결 id, 랩은 격자 경계 변으로 보존된다.',
              '- UNIT_LIMIT는 형식에서 지원한다. 원본과 기보에는 명시가 없으며 엔진 초기화에서 확인한 기본값은 '+str(results[0]['engine']['unit_limits'])+'이다.',
              '- 라운드 상한은 지도 항목이 아닌 엔진 상수 MAX_ROUNDS=500이다(문서 helper.hpp).',
              '- MAP_NAME과 SYMMETRY는 원본 그대로다. 서버 map_version, 팀 이름/봇, 시드는 지도 형식의 항목이 아니다.']
    assert len(lines) <= 30
    (OUT / 'README.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    main()
