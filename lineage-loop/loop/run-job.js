#!/usr/bin/env node
// Run diagnostic matches through the shared batch queue. The command must use <=2 games.
const rt = require('./runtime');
const [name, ...args] = process.argv.slice(2);
if (args[0] === '--') args.shift();
if (!args.length) { console.error('usage: node loop/run-job.js <lineage> -- <command> [args...]'); process.exit(2); }
rt.job(name, onSpawn => rt.command(args[0], args.slice(1), { cwd: process.cwd(), onSpawn }))
  .then(result => { process.exitCode = result.code; })
  .catch(e => { console.error(e.message); process.exitCode = 1; });
