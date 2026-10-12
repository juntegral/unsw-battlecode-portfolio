// Official replay-viewer parser (same loader as L-G1 scripts/events.js and tools/scenario_inputs.js; vsix read-only).
const fs=require('fs'),path=require('path'),cp=require('child_process'),vm=require('vm');
const root='~/01. Project/개인 프로젝트/UNSW';const viewer=path.join(root,'.venv-ppo/lib/python3.13/site-packages/unswbc/replay-viewer.vsix');
let src=cp.execFileSync('unzip',['-p',viewer,'extension/dist/webview/webview.js'],{maxBuffer:8<<20}).toString();
src=src.slice(0,src.indexOf('var Af=B(')).replace('if(n.formatVersion>1)','if(n.formatVersion>2)')+'globalThis.parseReplay=kf;})();';
const ctx={TextEncoder,TextDecoder};vm.runInNewContext(src,ctx,{timeout:5000});
const load=d=>{const f=fs.readdirSync(d).find(x=>x.endsWith('.replay'));return ctx.parseReplay(fs.readFileSync(path.join(d,f)));};
module.exports={ctx,load,root};
