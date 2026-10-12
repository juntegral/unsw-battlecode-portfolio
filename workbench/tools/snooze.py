"""Local decision-check snoozes shared by Discord and the hourly nudge."""
from contextlib import contextmanager
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import tempfile
import threading
from member_names import member_name, member_state

STORE = Path(__file__).resolve().parents[1] / 'data/meowbot/snooze.json'
KST = dt.timezone(dt.timedelta(hours=9))
_LOCK = threading.Lock()


def duration(text):
    if re.search(r'\b(?:until\s+)?tomorrow\b|내일|明天', text, re.I):
        return 24
    match = re.search(r'(?<![\w.-])(\d+(?:\.\d+)?)\s*(?:hours?\b|hrs?\b|h\b|시간|小[时時])', text, re.I)
    return min(24, float(match[1])) if match and float(match[1]) > 0 else 6


def parse_intent(text):
    match = re.fullmatch(r'\s*#?([1-9]\d*)\s+(.+?)\s*', text, re.S)
    if not match:
        return None
    number, note = int(match[1]), match[2]
    if re.fullmatch(r'(?:back|done|cancel|resume|끝|취소)[.!。！]*', note, re.I):
        return {'action': 'unsnooze', 'card': number}
    # Ambiguous questions and negated requests belong to the existing conversation.
    if re.search(r"\?|？|\b(?:don['’]?t|do not|not taking|not still|no longer)\b|하지\s*마|不要", note, re.I):
        return None
    if re.search(r'\btak(?:ing|e)\s+(?:(?:some|more|a little)\s+)?time\b|'
                 r'\bstill\s+(?:thinking|deciding)\b|\bneed\s+(?:some\s+)?more\s+time\b|'
                 r'\bnot\s+yet\b|\blater\b|\bsnooze\b|아직|(?:생각|고민)\s*중|나중에|좀\s*더|'
                 r'还在|還在|稍[后後]|再想想', note, re.I):
        return {'action': 'snooze', 'card': number, 'text': note}
    return None


def read_store(path=None):
    try:
        with open(path or STORE, encoding='utf-8') as stream:
            return member_state(json.load(stream))
    except FileNotFoundError:
        return {}


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK, open(str(path) + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def write_store(path, data):
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            name = stream.name
            json.dump(member_state(data), stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def set_snooze(number, by, note, now=None, path=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    path = Path(path or STORE)
    entry = {'until': (now + dt.timedelta(hours=duration(note))).isoformat(),
             'by': member_name(by), 'note': note, 'set': now.isoformat()}
    with locked(path):
        data = read_store(path)
        data[str(number)] = entry
        write_store(path, data)
    return entry


def clear_snooze(number, path=None):
    path = Path(path or STORE)
    with locked(path):
        data = read_store(path)
        if data.pop(str(number), None) is not None:
            write_store(path, data)


def active_snoozes(now, waiting_cards, path=None, persist=True):
    path = Path(path or STORE)
    waiting_cards = {str(n) for n in waiting_cards}

    def prune():
        data = read_store(path)
        active = {n: entry for n, entry in data.items()
                  if n in waiting_cards and dt.datetime.fromisoformat(entry['until']) > now}
        if persist and active != data:
            write_store(path, active)
        return active

    if not path.exists():
        return {}
    if not persist:
        return prune()
    with locked(path):
        return prune()


def quiet_until(entry):
    return dt.datetime.fromisoformat(entry['until']).astimezone(KST).strftime('%H:%M')
