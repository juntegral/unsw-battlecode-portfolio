"""unA-opus: variants of the start-box map (importing gen_ua rewrites the first nine maps unchanged)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_ua import Map, scatter, chain_map


def chain1_map(name, w, h, rs, pearl_in_box=False, to_field=False):
    """Start box -> one closed rs x rs pearl room -> field (or straight to the field when to_field)."""
    m = Map(name, w, h)
    hh = h // 2
    scatter(m, 4, 3, 40)
    m.room(1, 1, 5, 3, beds=False)
    if pearl_in_box: m.bed(5, 1, 400, 500)
    m.starter([(4 - i, 2) for i in range(3)])
    m.starter([(2 + i, 3) for i in range(2)])
    if to_field:
        m.portal(m.edge(6, 2, True), m.edge(w - 6, hh - 2, True))
    else:
        m.room(8, 1, rs, rs, 2, 20)
        m.portal(m.edge(6, 2, True), m.edge(8, 2, True))
        m.portal(m.edge(8 + rs, 2, True), m.edge(w - 6, hh - 2, True))
    m.save()


chain_map('ua_chain_720', 36, 20)
chain1_map('ua_chain1_320', 20, 16, 2)
chain1_map('ua_chain1p_320', 20, 16, 2, pearl_in_box=True)
chain1_map('ua_boxnp_320', 20, 16, 2, to_field=True)
chain1_map('ua_chain1_660', 30, 22, 3)
