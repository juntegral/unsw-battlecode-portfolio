#!/usr/bin/env python3
"""Fail-closed PreToolUse policy for read-only /meow sessions."""
import json
import os
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[1]
TEAM = ROOT.parent / 'battlecode'
MEMORY = Path('~/.claude/projects/-Users-jun-01--Project---------battlecode/memory')
REPO = 'forrest-gan2005/battlecode'


def roots():
    return [ROOT, TEAM, Path.home() / 'meow-release', Path.home() / 'meow-loop',
            Path.home() / 'meow-loop-out', MEMORY]


def safe_path(name, cwd=None):
    if not isinstance(name, str) or not name or '\x00' in name:
        return False
    path = Path(cwd or TEAM) / os.path.expanduser(name)
    path = path.resolve()
    parts = {p.lower() for p in path.parts}
    if parts & {'.git', '.ssh', '.aws', '.env', '.credentials', 'node_modules'}:
        return False
    if re.search(r'(?:api|discord|token|secret|credential|password|private[_-]?key)', path.name, re.I):
        return False
    if path.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'} or path.name.startswith('.env'):
        return False
    return any(path.is_relative_to(p.resolve()) for p in roots())


def check(event):
    tool, data = event.get('tool_name'), event.get('tool_input') or {}
    cwd = event.get('cwd') or str(TEAM)
    if tool in {'Read', 'Grep', 'Glob', 'LS'}:
        name = data.get('file_path') or data.get('path') or cwd
        if not safe_path(name, cwd):
            return 'This path is outside the team brain or may contain credentials.'
        if tool == 'Grep' and not (Path(cwd) / os.path.expanduser(name)).is_file():
            return 'Grep one approved file at a time; recursive content search can expose keys.'
        if tool == 'Glob':
            pattern = data.get('pattern', '')
            if Path(pattern).is_absolute() or '..' in Path(pattern).parts:
                return 'Glob patterns must remain beneath the approved path.'
        return None
    if tool != 'Bash':
        return 'Only approved read tools are available. Return an ACTION PLAN for changes.'
    command = data.get('command', '')
    if any(c in command for c in ('\n', '\r', '$', '`', ';', '|', '&', '<', '>', '\\')):
        return 'Shell evaluation, pipelines and redirection are unavailable.'
    try:
        args = shlex.split(command)
    except ValueError:
        return 'Invalid command.'
    if not args:
        return 'Empty command.'
    if args[0] == 'gh' and len(args) >= 3 and (args[1], args[2]) in {
            ('issue', 'list'), ('issue', 'view'), ('pr', 'list'), ('pr', 'view')}:
        allowed = {'--repo', '--state', '--limit', '--json', '--search', '--label', '--author', '--head', '--base'}
        flags = {'--comments'}
        i = 3
        while i < len(args):
            a = args[i]
            if a in allowed and i + 1 < len(args):
                if a == '--repo' and args[i + 1] != REPO:
                    return 'Only the team repository is readable.'
                i += 2
            elif a in flags or a.isdecimal():
                i += 1
            else:
                return 'Unsupported gh read argument.'
        if '--repo' not in args:
            return 'Specify the team --repo explicitly.'
        return None
    if args[0] == 'git':
        if len(args) < 4 or args[1] != '-C' or not safe_path(args[2], cwd):
            return 'Use git -C with an approved checkout.'
        sub, tail = args[3], args[4:]
        if sub == 'log' and all(re.fullmatch(r'--(?:oneline|no-decorate|max-count=\d+)|[0-9a-f]{7,40}', x) for x in tail):
            return None
        if sub == 'show' and len(tail) == 1:
            match = re.fullmatch(r'([0-9a-f]{7,40}|HEAD|main):(.+)', tail[0])
            if match and safe_path(match[2], args[2]) and not match[2].startswith(('/', ':')):
                return None
        return 'Only bounded git log or git show COMMIT:approved-file is available.'
    if args[0] == 'node' and len(args) >= 3:
        if (Path(cwd) / args[1]).resolve() != (ROOT / 'tools/online.js').resolve():
            return 'Only the reviewed online read tool is available.'
        if args[2] not in {'leaderboard', 'team', 'battles', 'battle', 'submissions', 'download'}:
            return 'Online mutations and ranked requests are blocked.'
        i = 3
        while i < len(args):
            a = args[i]
            if a in {'--json', '--all', '--eligible', '--only', '--no-events'} or re.fullmatch(r'\d+(?:,\d+)*', a):
                i += 1
            elif a in {'--top', '--limit'} and i + 1 < len(args) and args[i + 1].isdigit():
                i += 2
            elif a == '--out' and i + 1 < len(args) and re.fullmatch(r'meow/[a-zA-Z0-9_-]+', args[i + 1]):
                destination = ROOT / 'data/online' / args[i + 1]
                if destination.is_symlink() or not destination.resolve().is_relative_to((ROOT / 'data/online/meow').resolve()):
                    return 'Unsafe download path.'
                i += 2
            else:
                return 'Unsupported online read argument.'
        if args[2] == 'download' and '--out' not in args:
            return 'Replay downloads need --out meow/NAME.'
        return None
    return 'Command is not in the read-only allowlist.'


def main():
    try:
        reason = check(json.load(sys.stdin))
    except Exception:
        reason = 'Invalid hook input.'
    if reason:
        print('Blocked by /meow guard: ' + reason, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
