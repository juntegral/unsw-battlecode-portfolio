// Official 1.2.7 replay-viewer decoder, read out of the engine's own vsix (audit only, read-only).
const cp=require('child_process'),vm=require('vm');
const vsix='~/01. Project/개인 프로젝트/battlecode/work/bc127/lib/python3.13/site-packages/unswbc/replay-viewer.vsix';
let src=cp.execFileSync('unzip',['-p',vsix,'extension/dist/webview/webview.js'],{maxBuffer:16<<20}).toString();
const cut=src.indexOf('var Xf=V(');
if(cut<0||!src.includes('function Yf(e){let t=qf(e);')) throw new Error('viewer layout changed');
src=src.slice(0,cut)+'globalThis.parseReplay=Yf;})();';
const ctx={TextEncoder,TextDecoder,console};vm.runInNewContext(src,ctx,{timeout:5000});
module.exports={ctx};
