#!/usr/bin/env python3
"""Hourly ladder runner. No background processes; --once is an immediate cycle."""
import argparse
from datetime import datetime, timedelta
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from ladder_collect import ROOT, OUT, KST, atomic

DEADLINE=datetime(2026,10,8,20,tzinfo=KST)
ANALYSIS_EVERY_HOURS=3

def effort(first=False):return 'high'

def log(step,status,detail=''):
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'runner.log').open('a') as f:f.write(f'{datetime.now(KST).isoformat()} {step} {status} {detail.replace(chr(10)," ")}\n')

RUN_DEADLINE=None

def run(argv,timeout=3600,stdin=None,output=None,env=None):
    if RUN_DEADLINE is not None:
        remaining=(RUN_DEADLINE-datetime.now(KST)).total_seconds()
        if remaining<=0:raise RuntimeError('Runner deadline reached')
        timeout=min(timeout,remaining)
    stream=output.open('a') if output else subprocess.PIPE
    try:
        p=subprocess.Popen(list(map(str,argv)),cwd=ROOT,env=env,stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                           stdout=stream,stderr=subprocess.STDOUT,text=True,start_new_session=True,pass_fds=tuple(LOCK_FDS))
        try:stdout,_=p.communicate(stdin,timeout=timeout)
        except BaseException:
            os.killpg(p.pid,signal.SIGKILL);p.wait();raise
        if p.returncode:raise RuntimeError(f'{argv[0]} exited {p.returncode}: {(stdout or "see stream log")[-1000:]}')
        return stdout or ''
    finally:
        if output:stream.close()

LOCK_FDS=[]

def ai(role,stamp,first=False):
    level=effort(first)
    timeout=3000 if role=='analyst' else 2400
    env=os.environ.copy();env['LADDER_ROLE']=role;env['PYTHONDONTWRITEBYTECODE']='1'
    prompt=(OUT/f'{role}-prompt.md').read_text()+f"\nThis run's hour file: data/analysis/ladder/hours/{stamp}.md\nCurrent time: {datetime.now(KST).isoformat()} KST\n"
    path=OUT/f'logs/{role}-{stamp}.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
    argv=['claude','-p','--model','claude-opus-5-5','--effort',level,'--permission-mode','bypassPermissions','--settings','tools/ladder_settings.json','--output-format','stream-json','--verbose']
    run(argv,timeout=timeout,stdin=prompt,output=path,env=env)
    results=[]
    for line in path.read_text().splitlines():
        try:r=json.loads(line)
        except ValueError:continue
        if r.get('type')=='result':results.append(r)
    if not results or results[-1].get('is_error'):raise RuntimeError(f'{role} has no successful stream result')

def verify(stamp,call=ai):
    queue=OUT/'verify-queue.json'
    if not queue.exists():return False
    items=json.loads(queue.read_text())
    if not isinstance(items,list):raise ValueError('verify queue must be a list')
    if not items:return False
    call('verifier',stamp)
    saved=OUT/f'verified/{stamp}-queue.json';saved.parent.mkdir(parents=True,exist_ok=True)
    queue.replace(saved);atomic(queue,[])
    return True

def step(name,fn):
    log(name,'start')
    try:result=fn();log(name,'ok',str(result or '').strip());return True
    except Exception as e:log(name,'failed',f'{type(e).__name__}: {e}');return False

def cycle(no_ai=False,first=False):
    now=datetime.now(KST);stamp=now.strftime('%Y%m%d-%H%M');(OUT/'hours').mkdir(parents=True,exist_ok=True)
    step('collect',lambda:run([sys.executable,'tools/ladder_collect.py']))
    step('rows',lambda:run([sys.executable,'tools/ladder_rows.py']))
    if no_ai:log('ai','skipped','--no-ai');return
    if now.hour%ANALYSIS_EVERY_HOURS:log('ai','skipped','analysis skipped this hour');return
    step('analyst',lambda:ai('analyst',stamp,first))
    step('verifier',lambda:verify(stamp))

def main():
    global RUN_DEADLINE
    ap=argparse.ArgumentParser();ap.add_argument('--once',action='store_true');ap.add_argument('--no-ai',action='store_true');ap.add_argument('--first',action='store_true');args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'.runner.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:print('runner: already running');return
        LOCK_FDS.append(lock.fileno())
        if args.once:cycle(args.no_ai,args.first);return
        RUN_DEADLINE=DEADLINE
        now=datetime.now(KST);next_hour=now.replace(minute=0,second=0,microsecond=0)+timedelta(hours=1)
        next_poll=now.replace(second=0,microsecond=0)+timedelta(minutes=10-now.minute%10);first=args.first
        while datetime.now(KST)<DEADLINE:
            now=datetime.now(KST)
            if now>=next_hour:
                cycle(args.no_ai,first);first=False
                now=datetime.now(KST);next_hour=now.replace(minute=0,second=0,microsecond=0)+timedelta(hours=1)
                next_poll=now.replace(second=0,microsecond=0)+timedelta(minutes=10-now.minute%10)
            elif now>=next_poll:
                step('poll',lambda:run([sys.executable,'tools/ladder_collect.py','--poll-only']))
                now=datetime.now(KST);next_poll=now.replace(second=0,microsecond=0)+timedelta(minutes=10-now.minute%10)
            time.sleep(max(0.01,min(30,(min(next_hour,next_poll,DEADLINE)-datetime.now(KST)).total_seconds())))
        log('runner','stopped','deadline reached')
if __name__=='__main__':main()
