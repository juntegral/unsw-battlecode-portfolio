#!/usr/bin/env python3
"""Claude Code PreToolUse hook: local black-box restrictions from the setup brief."""
import json
import re
import sys

FORBIDDEN = ('battlecode', 'unsw-swarm', 'meow-cards', 'meow-release', 'meow-loop',
             'meow-dev', 'meow-queen', 'meow-bigmap', 'meow-deploy', 'meow-tx',
             'mybot', '.claude/projects', 'api.txt', 'discord')
INSPECT = re.compile(r'\b(?:strings|objdump|otool|nm|lldb|gdb|hexdump|xxd|dtruss|dtrace)\b', re.I)
NETWORK = re.compile(r'\b(?:curl|wget|ssh)\b|\b(?:gh|nc)\s|\bgit\s+push\b', re.I)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def check(event):
    values = list(strings(event.get('tool_input', {})))
    for value in values:
        lowered = value.lower()
        for term in FORBIDDEN:
            if term in lowered:
                return f'protected string: {term}'
    text = '\n'.join(values)
    if 'opponent' in text.lower() and INSPECT.search(text):
        return 'opponent binary inspection is blocked'
    if NETWORK.search(text):
        return 'network commands are blocked'
    return None


def main():
    try:
        event = json.load(sys.stdin)
        reason = check(event)
    except (ValueError, TypeError, AttributeError):
        reason = 'invalid hook input'
    if reason:
        print('Blocked: ' + reason, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
