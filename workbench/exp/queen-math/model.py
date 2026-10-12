"""Small rule-text model. No engine, bots, games, network or subprocesses.

Body tuples are head first. Geometry is a graph of tiles (kelp = absent edge).
All free budgets are fixed at MOVE start. Death is before destination movement.
Sources: rules/execution-order.md:46-76; splitting.md:9-21.
"""
from dataclasses import dataclass

DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))
LETTERS = "NESW"

def add(p, d):
    return p[0] + d[0], p[1] + d[1]

def free(length):
    return (length + 3) // 4

def maximum(length):
    return free(length) + length - 2

def diamond(radius):
    return {(x, y) for x in range(-radius, radius + 1)
            for y in range(-radius + abs(x), radius - abs(x) + 1)}

@dataclass
class Dragon:
    ident: int
    team: int
    body: tuple
    alive: bool = True

class World:
    def __init__(self, dragons, cells=None, pearls=(), portals=None, blocked=()):
        self.dragons = {d.ident: Dragon(d.ident, d.team, tuple(d.body), d.alive)
                        for d in dragons}
        self.cells = None if cells is None else set(cells)
        self.pearls = set(pearls)
        self.portals = dict(portals or {})  # directed edge -> destination tile
        self.blocked = set(blocked)         # directed kelp edges
        self.events = []

    def clone(self):
        return World(self.dragons.values(), self.cells, self.pearls,
                     self.portals, self.blocked)

    def die(self, ident, reason):
        d = self.dragons[ident]
        drops = d.body[::2]
        self.pearls.update(drops)
        d.alive = False
        self.events.append({"event": "death", "id": ident, "reason": reason,
                            "body": d.body, "drops": drops})

    def step(self, ident, direction, paid=False):
        d = self.dragons[ident]
        if not d.alive:
            return False
        if paid and len(d.body) <= 2:
            self.die(ident, "No Valid Action")
            return False
        edge = d.body[0], direction
        dest = self.portals.get(edge, add(d.body[0], direction))
        if edge in self.blocked or (self.cells is not None and dest not in self.cells):
            self.die(ident, "Hit Wall")
            return False
        if dest in d.body:
            self.die(ident, "Hit Self")
            return False
        for other in self.dragons.values():
            if other.ident == ident or not other.alive or dest not in other.body:
                continue
            if dest == other.body[0]:
                self.die(other.ident, "Head to Head")
                self.die(ident, "Head to Head")
            else:
                self.die(ident, "Hit Other Body")
            return False
        eat = dest in self.pearls
        if eat:
            self.pearls.remove(dest)
        d.body = (dest,) + (d.body if eat else d.body[:-1])
        if paid:
            d.body = d.body[:-1]
        self.events.append({"event": "step", "id": ident, "dest": dest,
                            "paid": paid, "ate": eat, "length": len(d.body)})
        return True

    def move(self, ident, directions):
        budget = free(len(self.dragons[ident].body))
        if not directions:
            self.die(ident, "No Valid Action")
        for i, direction in enumerate(directions):
            if not self.step(ident, direction, i >= budget):
                break
        return self.dragons[ident].alive

    def split(self, ident, size):
        d = self.dragons[ident]
        count = sum(x.alive and x.team == d.team for x in self.dragons.values())
        if size < 2 or len(d.body) - size < 2 or count >= 64:
            self.die(ident, "No Valid Action")
            return None
        child_id = max(self.dragons) + 1
        self.dragons[child_id] = Dragon(child_id, d.team, d.body[-size:][::-1])
        d.body = d.body[:-size]
        self.events.append({"event": "split", "parent": ident, "child": child_id,
                            "parent_body": d.body,
                            "child_body": self.dragons[child_id].body})
        return child_id

    def round(self, actions):
        # No pearl countdowns in these fixtures; spawned pearls supplied explicitly.
        ids = sorted(i for i, d in self.dragons.items() if d.alive)
        i = 0
        while i < len(ids):
            ident = ids[i]
            i += 1
            if not self.dragons[ident].alive:
                continue
            action = actions.get(ident)
            if action is None:
                self.die(ident, "No Valid Action")
            elif action[0] == "split":
                child = self.split(ident, action[1])
                if child is not None:
                    ids.append(child)
            else:
                self.move(ident, action[1])

def move_states(world, ident, max_steps=None, include_kills=False):
    """Exhaust all nonempty MOVE prefixes, merging equivalent body/pearl states.

    Default bound includes every currently available pearl, a conservative
    complete bound for a turn with no new drops/spawns during that MOVE.
    include_kills retains death worlds as results.
    """
    length = len(world.dragons[ident].body)
    bound = maximum(length) + len(world.pearls) if max_steps is None else max_steps
    frontier = [(world, "")]
    results = []
    for n in range(bound):
        nxt = {}
        for state, path in frontier:
            for letter, direction in zip(LETTERS, DIRS):
                w = state.clone()
                alive = w.step(ident, direction, n >= free(length))
                if alive:
                    key = w.dragons[ident].body, tuple(sorted(w.pearls))
                    nxt.setdefault(key, (w, path + letter))
                elif include_kills:
                    results.append((w, path + letter))
        frontier = list(nxt.values())
        results.extend(frontier)
    return results

def attack_path(world, hunter, queen):
    for w, path in move_states(world, hunter, include_kills=True):
        if not w.dragons[queen].alive:
            return path
    return None

def family_attack_actions(world, hunter, queen):
    """One hunter's full same-round MOVE-or-recursive-SPLIT family.

    A split parent has finished its turn; only its new child can act again.
    Caller handles any other hunters interleaved before newborn ids.
    """
    path=attack_path(world,hunter,queen)
    if path is not None:
        return [(hunter,'move',path)]
    length=len(world.dragons[hunter].body)
    for size in range(2,length-1):
        w=world.clone(); child=w.split(hunter,size)
        if child is None:continue
        suffix=family_attack_actions(w,child,queen)
        if suffix is not None:return [(hunter,'split',size)]+suffix
    return None

def score(queens, living):
    """r500 only. Early elimination must be handled separately."""
    return tuple((queens[t], max(living[t], default=0), sum(living[t]))
                 for t in (0, 1))
