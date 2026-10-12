#!/usr/bin/env python3
"""PreToolUse defence in depth; conservative shell and Python write-target checks."""
import ast
import json
import os
from pathlib import Path
import re
import shlex
import sys

ROOT=Path(__file__).resolve().parents[1]
READ={'Read','Glob','Grep','LS'}
WRITE={'Write','Edit','MultiEdit','NotebookEdit','apply_patch'}

def allowed_write(name,cwd,role):
    p=(Path(cwd)/name).resolve();out=ROOT/'data/analysis/ladder'
    if role=='verifier':return p.is_relative_to(out/'verify') or p==out/'verify-results.json'
    return p.is_relative_to(out)

def protected(text):
    return re.search(r'(?:api|discord)\.txt|--confirm|submit\.js|meowbot|meow_|discord|board\.py|bc_[A-Za-z0-9_-]+',text,re.I)

def python_check(source,cwd,role):
    try:tree=ast.parse(source)
    except SyntaxError:return 'Unparseable Python.'
    values={}
    def value(n):
        if isinstance(n,ast.Constant):return n.value if isinstance(n.value,str) else None
        if isinstance(n,ast.Name):return values.get(n.id)
        if isinstance(n,ast.JoinedStr):
            parts=[]
            for v in n.values:
                s=value(v) if isinstance(v,ast.Constant) else '*'
                if s is None:return None
                parts.append(s)
            return ''.join(parts)
        if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Div,ast.Add)):
            a,b=value(n.left),value(n.right)
            if a is not None and b is not None:return str(Path(a)/b) if isinstance(n.op,ast.Div) else a+b
        if isinstance(n,ast.Call):
            if isinstance(n.func,ast.Name) and n.func.id=='Path' and n.args:return value(n.args[0])
            if isinstance(n.func,ast.Attribute) and n.func.attr in ('resolve','absolute'):return value(n.func.value)
        return None
    nodes=list(ast.walk(tree))
    for _ in range(4):
        for n in nodes:
            if isinstance(n,ast.Assign):
                v=value(n.value)
                for target in n.targets:
                    if isinstance(target,ast.Name) and v is not None:values[target.id]=v
    for n in nodes:
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            mods=[a.name.split('.')[0] for a in n.names] if isinstance(n,ast.Import) else [(n.module or '').split('.')[0]]
            permitted={'sys','json','math','statistics','collections','pathlib','datetime','zoneinfo','re','csv','hashlib','gzip','struct','itertools','functools','random','typing','replay','ladder_replay','ladder_rows'}
            if any(m not in permitted for m in mods):return 'Python import is not on the read-only analysis allowlist.'
        if not isinstance(n,ast.Call):continue
        fn=n.func;name=fn.id if isinstance(fn,ast.Name) else fn.attr if isinstance(fn,ast.Attribute) else ''
        if name in ('eval','exec','compile','__import__','getattr','setattr','delattr','globals','locals','system','popen','run','Popen','unlink','rmdir','rename','replace','chmod','symlink_to','hardlink_to','touch'):
            return 'Opaque Python execution or filesystem mutation is blocked.'
        target=None
        if name in ('write_text','write_bytes','mkdir') and isinstance(fn,ast.Attribute):target=value(fn.value)
        if name=='open':
            mode=next((value(k.value) for k in n.keywords if k.arg=='mode'),None)
            if isinstance(fn,ast.Name):
                mode=mode or (value(n.args[1]) if len(n.args)>1 else 'r')
                if mode is None:return 'Unknown Python open mode.'
                if any(c in mode for c in 'wax+'):target=value(n.args[0]) if n.args else None
                else:continue
            else:
                mode=mode or (value(n.args[0]) if n.args else 'r')
                if mode is None:return 'Unknown Python open mode.'
                if any(c in mode for c in 'wax+'):target=value(fn.value)
                else:continue
        elif name not in ('write_text','write_bytes','mkdir'):continue
        if target is None or '*' in target or not allowed_write(target,cwd,role):
            return 'Python writes must resolve inside the role output directory.'
    return None

def check(event):
    tool=event.get('tool_name','');data=event.get('tool_input') or {};cwd=event.get('cwd') or str(ROOT);role=os.environ.get('LADDER_ROLE','analyst')
    if role not in ('analyst','verifier'):return 'Unknown ladder role.'
    text=json.dumps(data,ensure_ascii=False).replace('\\/','/')
    if protected(text):return 'Credentials, confirmation, submission and posting tools are blocked.'
    if tool in WRITE or tool.endswith('__apply_patch'):
        paths=[data[k] for k in ('file_path','path','notebook_path') if data.get(k)]
        paths+=re.findall(r'\*\*\* (?:Add|Update|Delete) File: (.+)',str(data.get('patch',data.get('input',''))))
        if not paths or any(not allowed_write(p,cwd,role) for p in paths):return 'Write target is outside the role output directory.'
        return None
    if tool in READ:
        for k in ('file_path','path'):
            if data.get(k) and protected(str((Path(cwd)/data[k]).resolve())):return 'Credential reads are blocked.'
        return None
    if tool!='Bash':return 'Only local read, write and reviewed Bash tools are allowed.'
    command=data.get('command','')
    if protected(command):return 'Protected command.'
    if re.search(r'\b(?:nohup|disown|curl|wget)\b|(?<!&)&(?!&)|\$\(|`|\b(?:eval|exec)\s|\b(?:bash|zsh|sh)\s+-c\b',command):return 'Network, detaching and opaque shell evaluation are blocked.'
    if re.search(r'\b(?:python\S*|node|ruby|perl)\s+(?:-c|-e)\b',command):return 'Inline interpreter flags are blocked.'
    heredoc=re.search(r"(?:python3)\s+-\s*<<\s*(['\"]?)(\w+)\1\s*\n(.*?)\n\2\s*$",command,re.S)
    if heredoc:
        if command[:heredoc.start()].strip():return 'Heredoc must be a single Python command.'
        if not heredoc.group(1):return 'Quote the heredoc delimiter to prevent shell expansion.'
        return python_check(heredoc.group(3),cwd,role)
    if '$' in command or '{' in command or '}' in command:return 'Shell variable and brace expansion are blocked; use explicit paths.'
    try:
        lex=shlex.shlex(command,posix=True,punctuation_chars=';&|()<>');lex.whitespace_split=True;tokens=list(lex)
    except ValueError:return 'Unparseable shell.'
    segments=[];part=[]
    for t in tokens:
        if t in (';','&&','||','|'):
            if part:segments.append(part);part=[]
        else:part.append(t)
    if part:segments.append(part)
    for words in segments:
        if not words:continue
        args=[];i=0
        while i<len(words):
            t=words[i]
            if t in ('>','>>','2>','2>>','&>') or t in ('<','<<'):
                if i+1>=len(words):return 'Missing redirect target.'
                if t!='<' and not allowed_write(words[i+1],cwd,role):return 'Redirect outside role output directory.'
                if t=='<<':return 'Only quoted Python heredocs are allowed.'
                i+=2;continue
            if any(c in t for c in '<>()'):return 'Unsupported shell syntax.'
            args.append(t);i+=1
        if not args:continue
        import glob
        for token in args:
            for resolved in glob.glob(str(Path(cwd)/token)):
                if protected(str(Path(resolved).resolve())):return 'Credential or protected path is blocked.'
        cmd=Path(args[0]).name;tail=args[1:]
        if cmd=='git':
            if not tail or tail[0] not in ('status','diff','log','show','rev-parse','ls-files'):return 'Git mutations are blocked.'
            if any(t in ('--output','--ext-diff','--textconv') or t.startswith('--output=') for t in tail):return 'Git output/execution option blocked.'
        elif cmd=='gh':
            if len(tail)<2 or tuple(tail[:2]) not in {('issue','list'),('issue','view'),('pr','list'),('pr','view'),('pr','diff'),('repo','view')} or any(t in tail for t in ('--method','-X','-f','-F','--field','--raw-field','--input','--web')):return 'GitHub writes are blocked.'
        elif cmd=='node':
            if len(tail)<2 or Path(tail[0]).resolve()!= (ROOT/'tools/online.js').resolve() and (Path(cwd)/tail[0]).resolve()!=(ROOT/'tools/online.js').resolve() or tail[1] not in ('battles','battle','download','submissions','maps'):return 'Only approved online reads are allowed.'
            if tail[1]=='download':return 'Replay downloads write outside the AI output directory; runner owns collection.'
        elif cmd=='python3':
            if not tail or tail[0].startswith('-'):return 'Use a script file or a quoted stdin heredoc.'
            p=(Path(cwd)/tail[0]).resolve()
            if protected(str(p)):return 'Protected Python script.'
            if not p.is_file():return 'Python script is missing; write it first.'
            reason=python_check(p.read_text(),cwd,role)
            if reason:return reason
        elif cmd in ('mkdir','rm'):
            names=[t for t in tail if not t.startswith('-')]
            if not names or any(not allowed_write(t,cwd,role) for t in names):return 'Filesystem mutation outside role output directory.'
        elif cmd in ('cp','mv','tee','install','touch','ln','chmod','truncate','dd','sed','find'):
            return 'Use Write/Edit or reviewed Python for filesystem operations.'
        elif cmd not in ('cat','head','tail','ls','rg','grep','wc','du','pwd','date','echo','printf','sort','uniq','cut'):
            return 'Shell command is not on the read-only allowlist.'
        if cmd=='rg' and any(t=='--pre' or t.startswith('--pre=') for t in tail):return 'rg external preprocessor blocked.'
    return None

def main():
    try:reason=check(json.load(sys.stdin))
    except Exception as e:reason=f'Invalid hook input: {type(e).__name__}'
    if reason:print('Blocked by ladder guard: '+reason,file=sys.stderr);return 2
    return 0
if __name__=='__main__':sys.exit(main())
