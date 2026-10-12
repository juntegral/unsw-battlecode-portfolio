import pathlib,subprocess,re,shutil,datetime
O=pathlib.Path(__file__).resolve().parent
def guard():
 p=subprocess.run(['memory_pressure','-Q'],capture_output=True,text=True,check=True);m=re.search(r'System-wide memory free percentage:\s*(\d+)%',p.stdout);f=shutil.disk_usage(O).free/(1024**3);r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memoryFreePercent':int(m[1]) if m else None,'diskFreeGiB':f}
 if r['memoryFreePercent'] is None or r['memoryFreePercent']<10 or f<21:raise RuntimeError('RESOURCE PAUSE '+str(r))
 return r
