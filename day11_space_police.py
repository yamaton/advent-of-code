import sys
import pathlib
import asyncio
import itertools as it
import collections
from typing import Tuple, List, DefaultDict

Intcode = DefaultDict[int, int]
Modes = Tuple[str, str, str]
Position = Tuple[int, int]
Facing = int

async def intcomputer(
    intcode: str, q_in: asyncio.Queue, q_out: asyncio.Queue, name="name", verbose=True
):
    def _decode_opcode(n: int) -> Tuple[int, Modes]:
        op = n % 100  # take two right-most digits as int
        s = str(n).zfill(5)
        # '0' position mode, '1' immediate mode, '2': relative mode
        modes = (s[2], s[1], s[0])
        return op, modes

    def _get_addr(xs: Intcode, loc: int, m: str, relbase: int) -> int:
        if m == "0":
            res = xs[loc]
        elif m == "1":
            res = loc
        else:
            assert m == "2"
            res = relbase + xs[loc]
        return res

    def _bin_op(
        f, xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        left = _get_addr(xs, loc + 1, mode[0], relbase)
        right = _get_addr(xs, loc + 2, mode[1], relbase)
        target = _get_addr(xs, loc + 3, mode[2], relbase)
        xs[target] = f(xs[left], xs[right])
        return xs, loc + 4, relbase

    def _add(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        return _bin_op(lambda a, b: a + b, xs, loc, mode, relbase)

    def _mul(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        return _bin_op(lambda a, b: a * b, xs, loc, mode, relbase)

    async def _in(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        target = _get_addr(xs, loc+1, mode[0], relbase)
        xs[target] = await q_in.get()
        return xs, loc + 2, relbase

    async def _out(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        target = _get_addr(xs, loc + 1, mode[0], relbase)
        await q_out.put(xs[target])
        return xs, loc + 2, relbase

    def _jmp_true(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int]:
        addr = _get_addr(xs, loc + 1, mode[0], relbase)
        if xs[addr] > 0:
            target = _get_addr(xs, loc + 2, mode[1], relbase)
            loc = xs[target]
        else:
            loc += 3
        return xs, loc, relbase

    def _jmp_false(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int]:
        addr = _get_addr(xs, loc + 1, mode[0], relbase)
        if xs[addr] == 0:
            target = _get_addr(xs, loc + 2, mode[1], relbase)
            loc = xs[target]
        else:
            loc += 3
        return xs, loc, relbase

    def _lt(xs: Intcode, loc: int, mode: Modes, relbase: int) -> Tuple[Intcode, int]:
        return _bin_op(lambda a, b: int(a < b), xs, loc, mode, relbase)

    def _eq(xs: Intcode, loc: int, mode: Modes, relbase: int) -> Tuple[Intcode, int]:
        return _bin_op(lambda a, b: int(a == b), xs, loc, mode, relbase)

    def _adj_relbase(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int]:
        addr = _get_addr(xs, loc + 1, mode[0], relbase)
        inc = xs[addr]
        return xs, loc + 2, relbase + inc

    opfun = {
        1: _add,
        2: _mul,
        3: _in,
        4: _out,
        5: _jmp_true,
        6: _jmp_false,
        7: _lt,
        8: _eq,
        9: _adj_relbase,
    }

    loc = 0
    relbase = 0
    d = collections.defaultdict(int)
    for i, x in enumerate(intcode):
        d[i] = x
    intcode = d
    while intcode[loc] != 99:
        if verbose:
            print(
                f"{name}: processing {intcode[loc]} at {loc} with relbase {relbase}, q_in={q_in}, q_out={q_out}",
                file=sys.stderr,
            )
        opcode = intcode[loc]
        op, mode = _decode_opcode(opcode)
        f = opfun[op]
        if asyncio.iscoroutinefunction(f):
            intcode, loc, relbase = await f(intcode, loc, mode, relbase)
        else:
            intcode, loc, relbase = f(intcode, loc, mode, relbase)


def get_path(day):
    return pathlib.Path(f"./2019/day{day:02}.txt")


def day11_read():
    file_ = get_path(11)
    assert file_.exists()
    return [int(w) for w in open(file_).read().split(",")]


class RobotAndFieldState(object):
    def __init__(self, loc: Position, facing: Facing):
        self.loc = loc
        self.facing = facing
        self.field = collections.defaultdict(int)
        self.painted_panel = set()

    def _update_field(self, color):
        if self.field[self.loc] != color:
            self.painted_panel.add(self.loc)
            self.field[self.loc] = color
            print(f"Painted {color} at {self.loc}")
        else:
            print(f"Did nothing at {self.loc}")

    def _update_facing(self, dir_move):
        shift = 1 if dir_move == 1 else -1
        self.facing = (self.facing + shift) % 4

    def _update_loc(self):
        dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        diff = dirs[self.facing]
        self.loc = (self.loc[0] + diff[0], self.loc[1] + diff[1])

    def update(self, commands: asyncio.Queue):
        color, dir_move = commands
        self._update_field(color)
        self._update_facing(dir_move)
        self._update_loc()

    def get_color(self):
        return self.field[self.loc]

    def get_paint_count(self):
        return len(self.painted_panel)

    async def run(self, queue_in: asyncio.Queue, queue_out: asyncio.Queue):
        while True:
            print(" ... runing env update")
            try:
                color = await asyncio.wait_for(queue_out.get(), timeout=1.0)
                dir_move = await asyncio.wait_for(queue_out.get(), timeout=1.0)
            except asyncio.TimeoutError:
                print("Timeout!")
                print(f"Painted {len(self.painted_panel)} panels!")
                break
            self.update([color, dir_move])
            next_input = self.get_color()
            await queue_in.put(next_input)


async def day11_robot(intcode) -> asyncio.Queue:
    """
    loc ... 2-d position (x, y)
    facing ... < ^ > v  as [0, 1, 2, 3]
    """
    env = RobotAndFieldState(loc=(0, 0), facing=1)
    q_in = asyncio.Queue()
    q_out = asyncio.Queue()
    q_in.put_nowait(env.get_color())

    tasks = []
    tasks.append(asyncio.create_task(intcomputer(intcode, q_in, q_out)))
    tasks.append(asyncio.create_task(env.run(q_in, q_out)))
    await asyncio.gather(*tasks)

    print(q_in)
    print(q_out)


def draw(d: DefaultDict):
    xmin = 1000000000
    ymin = 1000000000
    xmax = -xmin
    ymax = -ymin
    for (x, y) in d:
        xmin = min(x, xmin)
        xmax = max(x, xmax)
        ymin = min(y, ymin)
        ymax = max(y, ymax)

    res = [["."] * (xmax - xmin + 1) for _ in range(ymin, ymax + 1)]
    for i, y in enumerate(range(ymin, ymax + 1)):
        for j, x in enumerate(range(xmin, xmax +1)):
            if d[(x, y)] == 1:
                res[i][j] = '#'

    # revert y-dir
    grid = []
    for xs in res[::-1]:
        line = grid.append(("".join(xs)))
        print(line)


async def day11_robot_mod(intcode) -> asyncio.Queue:
    """
    loc ... 2-d position (x, y)
    facing ... < ^ > v  as [0, 1, 2, 3]
    """
    env = RobotAndFieldState(loc=(0, 0), facing=1)
    env.field[env.loc] = 1  # white at the starting point

    q_in = asyncio.Queue()
    q_out = asyncio.Queue()
    q_in.put_nowait(env.get_color())

    tasks = []
    tasks.append(asyncio.create_task(intcomputer(intcode, q_in, q_out, verbose=False)))
    tasks.append(asyncio.create_task(env.run(q_in, q_out)))
    await asyncio.gather(*tasks)
    print(env.field)
    draw(env.field)


if __name__ == "__main__":
    # intcode = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
    # intcode = [1102, 34915192, 34915192, 7, 4, 7, 99, 0]
    # intcode = [104, 1125899906842624, 99]
    intcode = day11_read()
    print(intcode)

    # asyncio.run(day09(intcode, [1]))
    asyncio.run(day11_robot_mod(intcode))
