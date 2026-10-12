#!/usr/bin/env node
// One-turn smoke test of the actual sandboxed Claude client in a migrated worktree.
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const name = process.argv[2];
if (!['g3', 'g4'].includes(name)) throw Error('usage: verify-orca-client.js g3|g4');
const root = path.join('~/orca/workspaces/unsw-arena', name);
const config = path.join(root, '.isolation');
const args = ['-f', path.join(config,'profile.sb'), 'claude', '-p',
  'Reply with READY only. Do not inspect files or use tools.',
  '--safe-mode','--no-session-persistence','--strict-mcp-config','--mcp-config',path.join(config,'mcp.json'),
  '--no-chrome','--disable-slash-commands','--setting-sources','project','--settings',path.join(config,'settings.json'),
  '--tools','Bash,Read,Edit,Write,Glob,Grep,TaskOutput,TaskStop,TodoWrite',
  '--model','claude-opus-5-5','--dangerously-skip-permissions','--max-turns','1',
  '--output-format','stream-json','--verbose'];
const env={...process.env,UNSW_ARENA_DATA:path.join(root,'.arena-data'),
  UNSW_ARENA_CONTROL:path.join(path.dirname(path.dirname(__dirname)),'unsw-arena-clean-control'),
  XDG_CACHE_HOME:path.join(root,'.arena-data/cache'),CLAUDE_CODE_TMPDIR:path.join(root,'.arena-data/tmp'),
  CLAUDE_CODE_DISABLE_BACKGROUND_TASKS:'1'};
const result=cp.spawnSync('/usr/bin/sandbox-exec',args,{cwd:root,env,encoding:'utf8',timeout:90000,maxBuffer:8<<20});
const events=(result.stdout||'').split('\n').filter(Boolean).flatMap(line=>{try{return[JSON.parse(line)]}catch{return[]}});
const init=events.find(x=>x.type==='system'&&x.subtype==='init');
const final=events.findLast(x=>x.type==='result');
const unexpected=!!init&&(init.cwd!==root||init.skills?.length||init.mcp_servers?.length||
  init.plugins?.some(p=>p.path!=='builtin'||!['agents-md','telemetry'].includes(p.name)));
const summary={name,exit:result.status,signal:result.signal,init:!!init,isolated:!!init&&!unexpected,
  cwd:init?.cwd,skills:init?.skills,servers:init?.mcp_servers,plugins:init?.plugins,
  result:final?.result,error:result.error?.message,stderr:result.stderr?.slice(-1000)};
console.log(JSON.stringify(summary,null,2));
if(result.status!==0||!summary.isolated||final?.is_error)process.exitCode=1;
