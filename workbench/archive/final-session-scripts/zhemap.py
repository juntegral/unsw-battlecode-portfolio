"""Fetch the map file Zhe attached in #meow at 14:17 (portal_boomerang.map) into the community map folder."""
import re, os, urllib.request
md = open('~/01. Project/개인 프로젝트/unsw-swarm/data/discord/900000000000000004.md').read()
m = re.findall(r'\((https://cdn\.discordapp\.com/attachments/[^)\s]*portal_boomerang\.map[^)\s]*)\)', md)
print('links found', len(m))
if m:
    out = os.path.expanduser('~/meow-redteam/maps/community/portal_boomerang.map')
    req = urllib.request.Request(m[-1], headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=30).read()
    open(out, 'wb').write(data)
    print('saved', len(data), 'bytes')
    print(data[:400].decode('utf-8', 'replace'))
