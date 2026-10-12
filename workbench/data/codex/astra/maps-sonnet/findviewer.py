import zipfile, glob, os
cands = glob.glob('~/01. Project/개인 프로젝트/*/work/*/lib/python3.13/site-packages/unswbc/replay-viewer.vsix')
cands += glob.glob('~/.claude/jobs/*/tmp/*/new/unswbc/replay-viewer.vsix')
cands += glob.glob('~/.claude/jobs/*/tmp/*/new/unswbc/*.vsix')
for c in sorted(set(cands)):
    try:
        s = zipfile.ZipFile(c).read('extension/dist/webview/webview.js').decode()
        print(c, 'Af=B(' in s, 'formatVersion>1' in s, 'formatVersion>2' in s, len(s))
    except Exception as e:
        print(c, 'ERR', e)
for d in glob.glob('~/.vscode/extensions/unswbc*/dist/webview/webview.js'):
    s = open(d).read()
    print(d, 'Af=B(' in s, 'formatVersion>1' in s, 'formatVersion>2' in s, len(s))
