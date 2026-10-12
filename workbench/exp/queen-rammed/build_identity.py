from pathlib import Path
import hashlib,json,os,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
T=ROOT/'exp/queen-rammed'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT.parent/'UNSW/.unswbc-123'))
sys.path.insert(1,str(ROOT.parent/'UNSW/.venv-ppo/lib/python3.13/site-packages'))
os.environ['XDG_CACHE_HOME']=str(T/'build-cache')
os.environ['UNSWBC_NO_UPDATE']='1'
os.environ['UNSWBC_NO_VSCODE']='1'
from unswbc import clangtool,sandbox
sys.path.insert(0,str(ROOT/'tools'))
from importlib.machinery import SourceFileLoader
freeze=SourceFileLoader('clean_builder',str(ROOT/'tools/unswbc-clean.py')).load_module().freeze
cache=T/'build-cache/unswbc';cache.mkdir(parents=True,exist_ok=True)
home=clangtool.toolchain()
for p in [home/'clang.wasm',home/'root/bin/wasm-ld']:
 target=sandbox.compiled_path(p)
 for source in [ROOT/'.cache/unswbc'/target.name,ROOT/'exp/qsight/build-cache/unswbc'/target.name]:
  if not target.exists() and source.is_file():shutil.copy2(source,target)
source=freeze(ROOT/'versions/v1.8/bot',T/'source-cache')
blob=clangtool.build(source).read_bytes()
(T/'current-default.wasm').write_bytes(blob)
sha=lambda b:hashlib.sha256(b).hexdigest()
report={'current':{'bytes':len(blob),'sha256':sha(blob)},'sourceSnapshot':str(source.relative_to(ROOT)),'references':{}}
for task in ['q2box','freecost','q1c','qsight']:
 for p in sorted((ROOT/f'exp/{task}/compiled').glob('*.wasm')):
  b=p.read_bytes();report['references'][str(p.relative_to(ROOT))]={'bytes':len(b),'sha256':sha(b),'equalsCurrent':b==blob}
(T/'build-identity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
