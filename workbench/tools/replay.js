// Load a replay file (.replay or .replay.gz) with the official viewer's parser.
// usage: const { load } = require('./tools/replay.js'); const R = load('data/top/<battle>/<game>.replay.gz');
// Server replays are format 2, and the viewer's format-1 schema reads every sonar `value` as 0. This uses the loader
// from tools/top_features.js, which adds the real message and landing to each sonarPing:
//   e.value64 (BigInt, the sent 64-bit value), e.hitKind ('kelp' | 'ally' | 'allyHead' | 'enemy' | 'enemyHead' | 'empty').
// value64 is a BigInt, so JSON.stringify of raw events needs a replacer. Details: docs/top_features.md.
let loader = null;
function load(file) {
  if (!loader) { const tf = require('./top_features.js'); loader = tf.makeLoader(tf.viewerSource()); }
  return loader(file);
}
module.exports = { load };
