#!/usr/bin/env python3
"""Complete the staged renderer into another new file; never edits its sources."""
from pathlib import Path
p=Path(__file__).resolve().parent
src=(p/'render.py').read_text()
src=src[:src.index('signal=[]')]+src[src.index('signal=[]'):].replace("ci(__import__('analyse').wilson(c,nn),True)","ci(wilson(c,nn),True)")
src=src[:src.index('# Avoid importing analyse.py')]
helper='''\ndef wilson(k,n):
    if not n:return [None,None]
    z=1.959963984540054;p=k/n;d=1+z*z/n
    c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]
'''
src=src.replace('L=[]',helper+'\nL=[]',1)
with open(p/'render-v2.py','x') as f:f.write(src+(p/'render_tail.txt').read_text())
print('created render-v2.py')
