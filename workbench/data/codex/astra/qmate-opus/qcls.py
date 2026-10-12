"""qmate-opus: cls() from qexit-opus/classify.py without running its main."""
src = open('data/codex/astra/qexit-opus/classify.py').read().split('\ndef main')[0]
ns = {}
exec(src, ns)
cls = ns['cls']
