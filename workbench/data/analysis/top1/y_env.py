#!/usr/bin/env python3
"""Which Python and which numeric modules are here. Output: stdout."""
import sys

print(sys.version)
for m in ("numpy", "scipy", "statsmodels"):
    try:
        mod = __import__(m)
        print(m, getattr(mod, "__version__", "?"))
    except Exception as e:  # noqa: BLE001
        print(m, "missing:", e)
