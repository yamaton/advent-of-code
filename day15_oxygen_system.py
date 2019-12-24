import collections
from utils import get_path
from day13_care_package import intcomputer

"""
Robot Exploration

Command to the robot:
1 ... One step to the north
2 ... One step to the south
3 ... One step to the west
4 ... One step to the east

Response from the robot
0 ... Hit a wall. Not moving.
1 ... Moved one step to the requested direction
2 ... Moved one step to the requested direction AND found the oxigen

Breadth-first search

"""


class Brain(object):
    def __init__(self):
        self.current = (0, 0)
        self.next_pos = None
        self.fieldmap = {(0, 0): "+"}
        self.stack = self.next_steps()
        self.parent = {(0, 0): None}

        for pos in self.next_steps():
            self.parent[pos] = self.current

    def _prev(self, pos):
        return self.parent.get(pos)

    def _translate_to_command(self, pos, next_p):
        trans = {(0, 1): 1, (0, -1): 2, (-1, 0): 3, (1, 0): 4}
        x0, y0 = pos
        x, y = next_p
        diff = (x - x0, y - y0)
        return trans[diff]

    def backup_to(self, basecamp):
        res = collections.deque()
        while self.current != basecamp:
            assert self.current in self.fieldmap
            next_ = self._prev(self.current)
            assert next_ in self.fieldmap
            cmd = self._translate_to_command(self.current, next_)
            res.append(cmd)
            self.current = next_
        return res

    def next_steps(self):
        x, y = self.current
        return [(x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)][::-1]

    def command(self):
        if not self.stack:
            print("Cannot move any more!")
            print(self.fieldmap)
            return None, None

        commands = collections.deque()

        self.next_pos = self.stack.pop()
        print(f"self.next_pos = {self.next_pos}")
        basecamp = self._prev(self.next_pos)
        if basecamp is None:
            print("done???")
            return None, None
        if basecamp != self.current:
            self.stack.append(basecamp)  # start from basecamp in the next run
            commands = self.backup_to(basecamp)

        cmd = self._translate_to_command(self.current, self.next_pos)
        commands.append(cmd)
        return commands, self.next_pos

    def report(self, response):
        if response in [1, 2]:
            self.fieldmap[self.next_pos] = "*" if response == 2 else "."
            self.current = self.next_pos
            for nxt in self.next_steps():
                if nxt not in self.fieldmap:
                    self.stack.append(nxt)
                    self.parent[nxt] = self.current
        else:
            self.fieldmap[self.next_pos] = "#"


def day15_read():
    path = get_path(15)
    return [int(x) for x in open(path).read().split(",")]


def update_pos(position, direction):
    if direction == 1:
        dx = (0, 1)
    elif direction == 2:
        dx = (0, -1)
    elif direction == 3:
        dx = (-1, 0)
    else:
        assert direction == 4
        dx = (1, 0)

    position = (position[0] + dx[0], position[1] + dx[1])

    return position


def show(fieldmap, pos=None):
    x_min = 100000000
    y_min = 100000000
    x_max = -100000000
    y_max = -100000000

    for (x, y) in fieldmap:
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x)
        y_max = max(y_max, y)

    res = [[" "] * (x_max - x_min + 1) for _ in range(y_max - y_min + 1)]
    for j in range(y_max - y_min + 1):
        for i in range(x_max - x_min + 1):
            x, y = i + x_min, j + y_min
            if (x, y) in fieldmap:
                res[j][i] = fieldmap[(x, y)]

    if pos:
        res[pos[1] - y_min][pos[0] - x_min] = "D"

    for xs in res[::-1]:
        print("".join(xs))


def bfs(fieldmap):
    def _next(pos):
        x, y = pos
        yield from [(x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)]

    assert fieldmap[(0, 0)] == "+"
    parent = dict()
    q = collections.deque([(0, 0)])

    while q:
        pos = q.popleft()
        if pos not in fieldmap:
            print(f"something wrong!: pos={pos}")
        if fieldmap[pos] == "*":
            break

        for next_pos in _next(pos):
            criteria = (
                next_pos not in parent
                and next_pos in fieldmap
                and fieldmap.get(next_pos) in ".*"
            )
            if criteria:
                q.append(next_pos)
                parent[next_pos] = pos

    print(f"parent: {parent}")
    cnt = 0
    while fieldmap[pos] != "+":
        pos = parent[pos]
        cnt += 1

    return cnt


def bfs(fieldmap):
    def _next(pos):
        x, y = pos
        yield from [(x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)]

    assert fieldmap[(0, 0)] == "+"
    # start from the oxigen
    pos = next(k for k, v in fieldmap.items() if v == '*')
    time = {pos: 0}

    q = collections.deque([pos])
    while q:
        pos = q.popleft()
        if pos not in fieldmap:
            print(f"something wrong!: pos={pos}")

        for next_pos in _next(pos):
            criteria = (
                next_pos not in time
                and fieldmap.get(next_pos) in ".*+"
            )
            if criteria:
                q.append(next_pos)
                time[next_pos] = time[pos] + 1

    print(f"time: {time}")
    return max(time.values())



def day15_manual():
    intcode = day15_read()
    loc, relbase = 0, 0
    q_in = collections.deque([])

    position = (0, 0)
    fieldmap = {position: "+"}
    while True:
        show(fieldmap, position)
        x = input()
        if x.startswith("a"):
            dir_ = 3
        elif x.startswith("d"):
            dir_ = 4
        elif x.startswith("s"):
            dir_ = 2
        else:
            dir_ = 1
        q_in.append(dir_)
        next_position = update_pos(position, dir_)

        q_out, intcode, loc, relbase = intcomputer(
            q_in, intcode, loc, relbase, verbose=False
        )
        response = q_out.pop()
        if response == 2:
            position = next_position
            fieldmap[position] = "*"
            print(f"Found the oxigen at {position}")
            show(fieldmap)
            print(fieldmap)
            break
        elif response == 1:
            position = next_position
            fieldmap[position] = "."
        else:
            assert response == 0
            fieldmap[next_position] = "#"

    cnt = bfs(fieldmap)
    print(f"Steps to the oxigen: {cnt}")
    return cnt


def day15_auto():
    intcode = day15_read()
    loc, relbase = 0, 0

    position = (0, 0)
    fieldmap = {position: "+"}

    brain = Brain()

    while True:
        show(fieldmap, position)
        q_in, next_position = brain.command()
        if q_in is None:
            break
        print(f"q_in = {q_in}, next_position = {next_position}")
        q_out, intcode, loc, relbase = intcomputer(
            q_in, intcode, loc, relbase, verbose=False
        )
        response = q_out.pop()
        brain.report(response)
        if response == 2:
            position = next_position
            fieldmap[position] = "*"
            print(f"Found the oxigen at {position}")
        elif response == 1:
            position = next_position
            fieldmap[position] = "."
        else:
            assert response == 0
            fieldmap[next_position] = "#"

    show(fieldmap)
    print(fieldmap)
    assert brain.fieldmap == fieldmap

    cnt = bfs(fieldmap)
    print(f"Steps to fill with the oxigen: {cnt}")
    return cnt


if __name__ == "__main__":
    print(day15_auto())
    # print(day15_manual())
    # d = {(0, 0): '+', (0, -1): '.', (0, -2): '.', (0, -3): '#', (-1, -2): '.', (-2, -2): '.', (-3, -2): '#', (-2, -1): '.', (-2, 0): '.', (-2, 1): '#', (-3, 0): '.', (-4, 0): '.', (-5, 0): '#', (-4, -1): '.', (-4, -2): '.', (-4, -3): '#', (-5, -2): '.', (-6, -2): '.', (-7, -2): '#', (-6, -1): '.', (-6, 0): '.', (-6, 1): '.', (-6, 2): '.', (-6, 3): '.', (-6, 4): '.', (-6, 5): '#', (-7, 4): '.', (-7, 5): '#', (-8, 4): '.', (-9, 4): '#', (-8, 5): '.', (-8, 6): '.', (-8, 7): '#', (-7, 6): '#', (-9, 6): '.', (-10, 6): '.', (-11, 6): '#', (-10, 7): '.', (-10, 8): '.', (-10, 9): '#', (-9, 8): '.', (-8, 8): '.', (-7, 8): '.', (-6, 8): '.', (-5, 8): '#', (-6, 7): '.', (-6, 6): '.', (-5, 6): '.', (-4, 6): '.', (-3, 6): '#', (-4, 7): '#', (-4, 5): '.', (-4, 4): '.', (-4, 3): '#', (-3, 4): '.', (-3, 5): '#', (-2, 4): '.', (-1, 4): '#', (-2, 5): '#', (-2, 3): '.', (-2, 2): '.', (-1, 2): '.', (0, 2): '.', (1, 2): '#', (0, 3): '.', (0, 4): '.', (0, 5): '#', (1, 4): '.', (2, 4): '.', (3, 4): '#', (2, 5): '#', (2, 3): '.', (3, 3): '#', (2, 2): '.', (2, 1): '#', (3, 2): '.', (4, 2): '.', (4, 3): '#', (5, 2): '#', (4, 1): '.', (5, 1): '#', (3, 1): '#', (4, 0): '.', (3, 0): '.', (2, 0): '.', (1, 0): '#', (2, -1): '.', (2, -2): '.', (2, -3): '.', (2, -4): '.', (1, -4): '.', (0, -4): '.', (-1, -4): '.', (-1, -3): '#', (-2, -4): '.', (-2, -3): '#', (-3, -4): '.', (-4, -4): '.', (-3, -3): '#', (-5, -4): '#', (-3, -5): '#', (-4, -5): '.', (-5, -5): '#', (-4, -6): '.', (-4, -7): '#', (-5, -6): '#', (-3, -6): '.', (-2, -6): '.', (-2, -7): '.', (-3, -7): '#', (-2, -8): '.', (-2, -9): '#', (-1, -8): '#', (-3, -8): '.', (-3, -9): '#', (-4, -8): '.', (-4, -9): '.', (-5, -9): '#', (-5, -8): '#', (-4, -10): '.', (-3, -10): '#', (-5, -10): '#', (-4, -11): '.', (-3, -11): '#', (-5, -11): '#', (-4, -12): '.', (-3, -12): '.', (-5, -12): '#', (-4, -13): '#', (-3, -13): '#', (-2, -12): '.', (-2, -11): '#', (-2, -13): '#', (-1, -12): '.', (-1, -11): '#', (-1, -13): '#', (0, -12): '.', (0, -11): '#', (0, -13): '#', (1, -12): '.', (1, -11): '#', (1, -13): '#', (2, -12): '.', (2, -11): '.', (2, -13): '#', (3, -12): '#', (3, -11): '#', (2, -10): '.', (1, -10): '#', (3, -10): '#', (2, -9): '.', (1, -9): '#', (3, -9): '#', (2, -8): '.', (1, -8): '#', (3, -8): '.', (3, -7): '#', (2, -7): '#', (4, -8): '.', (4, -7): '#', (4, -9): '#', (5, -8): '.', (6, -8): '.', (5, -7): '#', (5, -9): '#', (6, -7): '.', (6, -9): '#', (7, -8): '#', (6, -6): '.', (5, -6): '#', (7, -6): '#', (6, -5): '.', (5, -5): '#', (7, -5): '#', (6, -4): '.', (5, -4): '#', (7, -4): '#', (6, -3): '.', (5, -3): '#', (7, -3): '#', (6, -2): '.', (5, -2): '.', (4, -2): '.', (3, -2): '#', (5, -1): '#', (7, -2): '#', (6, -1): '.', (6, 0): '.', (7, 0): '.', (7, 1): '#', (8, 0): '.', (9, 0): '#', (8, 1): '.', (8, 2): '.', (8, 3): '#', (9, 2): '.', (9, 3): '#', (10, 2): '.', (11, 2): '#', (10, 3): '.', (10, 4): '.', (10, 5): '#', (11, 4): '.', (11, 5): '#', (9, 4): '#', (12, 4): '.', (13, 4): '#', (12, 5): '#', (12, 3): '.', (12, 2): '.', (11, 3): '#', (13, 3): '#', (13, 2): '#', (12, 1): '.', (11, 1): '#', (13, 1): '#', (12, 0): '.', (11, 0): '#', (13, 0): '#', (12, -1): '.', (11, -1): '#', (13, -1): '#', (12, -2): '.', (11, -2): '#', (13, -2): '.', (12, -3): '#', (13, -3): '#', (14, -2): '.', (14, -3): '#', (14, -1): '.', (14, 0): '.', (14, 1): '#', (15, 0): '.', (16, 0): '.', (16, 1): '#', (15, 1): '#', (17, 0): '.', (17, 1): '#', (18, 0): '.', (18, 1): '#', (19, 0): '#', (18, -1): '.', (18, -2): '.', (19, -2): '#', (18, -3): '.', (19, -3): '#', (17, -3): '#', (17, -2): '#', (17, -1): '#', (19, -1): '#', (18, -4): '.', (17, -4): '.', (19, -4): '#', (18, -5): '#', (17, -5): '#', (16, -4): '.', (15, -4): '#', (16, -3): '.', (16, -2): '.', (16, -1): '#', (15, -2): '#', (15, -3): '#', (16, -5): '.', (16, -6): '.', (16, -7): '#', (15, -6): '#', (17, -6): '.', (18, -6): '.', (19, -6): '#', (18, -7): '.', (18, -8): '.', (18, -9): '.', (18, -10): '.', (18, -11): '#', (17, -10): '.', (16, -10): '.', (15, -10): '#', (16, -9): '.', (16, -8): '.', (15, -8): '.', (17, -8): '#', (17, -9): '#', (16, -11): '#', (19, -10): '#', (15, -9): '#', (15, -7): '#', (14, -8): '.', (14, -7): '#', (14, -9): '#', (13, -8): '.', (13, -7): '#', (13, -9): '#', (12, -8): '.', (12, -7): '#', (12, -9): '#', (11, -8): '.', (11, -7): '#', (11, -9): '#', (10, -8): '.', (10, -7): '#', (9, -8): '.', (9, -7): '#', (8, -8): '.', (8, -7): '.', (8, -6): '.', (8, -5): '.', (8, -4): '.', (8, -3): '.', (8, -2): '.', (8, -1): '#', (9, -4): '#', (9, -2): '.', (9, -1): '#', (10, -2): '.', (10, -1): '.', (10, 0): '.', (10, 1): '#', (10, -3): '.', (10, -4): '.', (11, -4): '.', (11, -5): '#', (11, -3): '#', (12, -4): '.', (13, -4): '#', (10, -5): '#', (12, -5): '.', (13, -5): '#', (12, -6): '.', (13, -6): '.', (14, -6): '.', (14, -5): '.', (14, -4): '.', (15, -5): '#', (11, -6): '.', (10, -6): '.', (9, -6): '#', (9, -3): '#', (9, -5): '#', (7, -7): '#', (8, -9): '.', (8, -10): '.', (8, -11): '#', (9, -10): '#', (7, -10): '.', (6, -10): '.', (5, -10): '.', (4, -10): '.', (4, -11): '.', (4, -12): '.', (4, -13): '.', (4, -14): '.', (4, -15): '.', (4, -16): '.', (4, -17): '#', (3, -16): '#', (5, -16): '.', (5, -15): '#', (6, -16): '.', (7, -16): '#', (6, -17): '.', (5, -17): '#', (7, -17): '#', (6, -18): '.', (5, -18): '.', (7, -18): '.', (5, -19): '#', (4, -18): '.', (3, -18): '.', (6, -19): '#', (8, -18): '.', (7, -19): '#', (8, -17): '#', (8, -19): '#', (9, -18): '.', (9, -19): '#', (9, -17): '#', (10, -18): '.', (10, -19): '#', (10, -17): '.', (10, -16): '.', (10, -15): '#', (11, -16): '.', (12, -16): '.', (12, -15): '#', (11, -15): '#', (13, -16): '#', (12, -17): '.', (13, -17): '#', (12, -18): '.', (13, -18): '.', (14, -18): '.', (15, -18): '#', (14, -17): '.', (14, -16): '.', (14, -15): '#', (15, -16): '.', (15, -15): '#', (16, -16): '.', (17, -16): '#', (16, -15): '#', (16, -17): '.', (16, -18): '.', (16, -19): '#', (17, -18): '.', (17, -19): '#', (17, -17): '#', (18, -18): '.', (18, -19): '#', (18, -17): '.', (18, -16): '.', (18, -15): '.', (18, -14): '.', (18, -13): '.', (18, -12): '.', (17, -12): '.', (16, -12): '.', (15, -12): '.', (15, -11): '#', (17, -11): '#', (19, -12): '#', (19, -13): '#', (19, -14): '#', (19, -15): '#', (19, -16): '#', (19, -17): '#', (19, -18): '#', (17, -14): '#', (17, -15): '#', (17, -13): '#', (16, -13): '#', (15, -13): '#', (14, -12): '.', (14, -11): '#', (13, -12): '#', (14, -13): '.', (14, -14): '.', (13, -14): '.', (12, -14): '.', (11, -14): '.', (10, -14): '.', (9, -14): '#', (10, -13): '.', (10, -12): '.', (10, -11): '.', (10, -10): '.', (11, -10): '.', (12, -10): '.', (13, -10): '.', (13, -11): '#', (12, -11): '.', (12, -12): '*'}
    # print(bfs(d))
