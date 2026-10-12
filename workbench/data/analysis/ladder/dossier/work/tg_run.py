#!/usr/bin/env python3
"""One-command offline fingerprint rebuild. Writes done.txt only after verification."""
import sys
sys.dont_write_bytecode=True
from datetime import datetime
from pathlib import Path
import subprocess

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[4]


def main():
    done=WORK.parent/'target/done.txt'
    if done.exists(): done.unlink()
    for name in ('tg_count.py','tg_score.py','tg_verify.py'):
        subprocess.run([sys.executable,'-B',str(WORK/name)],cwd=ROOT,check=True)
    done.write_text('Complete and verified: '+datetime.now().astimezone().isoformat(timespec='seconds')+'\n')


if __name__=='__main__': main()
