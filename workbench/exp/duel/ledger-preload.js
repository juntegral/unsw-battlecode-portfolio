// Keep eval/board.js unchanged; replace its ledger only for a verified quarter-policy replay.
'use strict';
const ledger=require('../../tools/mass_ledger'),local=require('./ledger');
ledger.perGame=(R,info,hooks)=>local.perGame(R,{...info,freePolicy:process.env.DUEL_LEDGER_POLICY||'one_fit'},hooks);
