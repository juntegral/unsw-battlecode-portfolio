"""Canonical display names, with compatibility for older member input and state."""
JUN_ALIASES = ('jun', 'junsing', 'juntegral', '준싱')


def member_name(value):
    if isinstance(value, str) and value.strip().casefold() in JUN_ALIASES:
        return 'jun'
    return value


def member_state(value):
    if isinstance(value, dict):
        return {key: member_name(item) if key in {'by', 'idea_by', 'author', 'proposer'}
                else member_state(item) for key, item in value.items()}
    if isinstance(value, list):
        return [member_state(item) for item in value]
    return value


def display_text(value):
    return value.replace(JUN_ALIASES[-1], 'jun')
