# Astra analyst: avengewhy

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `avengewhy`. Builder notes: `data/codex/build/avenge/done.txt`.

Team kraken (id 989, about 1990) has beaten us 3 to 2 in three ranked battles in 35 minutes. In one8's 15-game set against it
(`data/online/smoke/one8-k1-old/`, bot `one8-bot/main.cpp`) we won 9 and the six losses were all decided on the queen while we
were far ahead on everything else: Australia 1485169 we end with 42 dragons / 481 length against 10 / 82, our queen dead, theirs
alive at length 3; Portals 1485181 we have 11 dragons / 59 length against ONE dragon, their queen, 8 long; Around UNSW 1485174
30 / 285 against 26 / 232 with their queen 19; Slithery Fight 1485182; Islands 1485170; Trauma 1485180 where both queens live,
ours 3 long, theirs 16. one8 has `QUEEN_AVENGE 8` on: once our queen is dead and theirs is alive, dragons of 4 or less should
hunt her. It did not win these games. Find out exactly why, game by game, so a builder can fix it within the hour.
1. For each of the five games where our queen died and theirs lived: the round ours died; from then on, every 25 rounds, where
   their queen was, how many of our dragons had her in view, the nearest of ours to her (steps) and its length, how many of ours
   were 4 or less; whether the armed state could have been set (reconstruct the signal the builder used: who saw our queen die,
   what the sonar carried, who could hear it); the turns on which one of ours had her head inside its reach (free, and with paid
   steps) and what it did instead. Classify each game: never armed / armed but she was never found / found but nobody of 4 or less
   near / in reach and not rammed / rammed a body, not the head / other.
2. What would have killed her: the earliest round at which a plain rule "every dragon of ours of 8 or less walks to her last
   known cell and rams her head when it can reach it, paying segments if needed" would have had a dragon in reach. Is her
   position known to the side at all after our queen dies (sightings per 25 rounds)?
3. Trauma 1485180 and every game in one8's three sets where both queens were alive at the end: lengths of both, and what our
   queen did in r300-499 (pearls eaten, splits, whether mates fed her: `queen_game`, feeding rules near lines 5592-5700 of
   one8-bot). Why does ours stay at 3 while theirs grows?
4. Two cards with lines: (a) the avenge rule that wins the five games; (b) the rule that makes our live queen the longer one.
Report under 500 words plus tables; first three lines = why avenge did not fire or did not kill, the two cards, how sure.
