// Keep the unmodified validator CLI's report writes inside the requested scope.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../..'),target=path.join(root,'exp/mapgen');
const mkdir=fs.mkdirSync,write=fs.writeFileSync;
fs.mkdirSync=function(p,...rest){return mkdir.call(fs,path.resolve(String(p))===target?__dirname:p,...rest);};
fs.writeFileSync=function(p,...rest){const full=path.resolve(String(p));
  if(full===path.join(target,'validation-generated.json'))p=path.join(__dirname,'validator-strict.json');
  if(full===path.join(target,'validation-existing.json'))p=path.join(__dirname,'validator-format.json');
  return write.call(fs,p,...rest);
};
