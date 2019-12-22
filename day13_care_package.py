import sys
import collections
from typing import List, Tuple, Dict, DefaultDict
from utils import get_path

Intcode = DefaultDict[int, int]
Modes = Tuple[str, str, str]
Position = Tuple[int, int]
Facing = int


def day13_read():
    path = get_path(13)
    intcode = collections.defaultdict(int)
    xs = [int(x) for x in open(path).read().split(',')]
    for i, x in enumerate(xs):
        intcode[i] = x
    return intcode


def intcomputer(
    q_in: collections.deque, intcode: Intcode, loc=0, relbase=0, name="name", verbose=True
) -> (collections.deque, Intcode, int, int):
    q_out = collections.deque()

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

    def _in(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        target = _get_addr(xs, loc + 1, mode[0], relbase)
        xs[target] = q_in.popleft()
        return xs, loc + 2, relbase

    def _out(
        xs: Intcode, loc: int, mode: Modes, relbase: int
    ) -> Tuple[Intcode, int, int]:
        target = _get_addr(xs, loc + 1, mode[0], relbase)
        q_out.append(xs[target])
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

    while intcode[loc] != 99:
        if verbose:
            print(
                f"{name}: processing {intcode[loc]} at {loc} with relbase {relbase}",
                file=sys.stderr,
            )

        opcode = intcode[loc]
        op, mode = _decode_opcode(opcode)

        if op == 3 and not q_in:
            # if verbose:
            print(f"exhausted qin and freezing... at loc={loc} with intcode[loc]={intcode[loc]}", file=sys.stderr)
            break

        f = opfun[op]
        intcode, loc, relbase = f(intcode, loc, mode, relbase)

    return q_out, intcode, loc, relbase


def count_tiles(q: collections.deque):
    bag = collections.defaultdict()
    while q:
        x = q.popleft()
        y = q.popleft()
        code = q.popleft()
        bag[(x, y)] = code
    return sum(1 for x in bag.values() if x == 2)


def day13():
    inputs = day13_read()
    q = collections.deque([])
    q, _, _, _ = intcomputer(q, inputs, verbose=False)
    print(count_tiles(q))


def day13_draw_breakout(d: DefaultDict[Tuple[int, int], int]):
    xmin = 1000000000
    ymin = 1000000000
    xmax = -xmin
    ymax = -ymin
    for (x, y) in d:
        if (x, y) != (-1, 0):
            xmin = min(x, xmin)
            xmax = max(x, xmax)
            ymin = min(y, ymin)
            ymax = max(y, ymax)

    score = d[(-1, 0)]

    res = [[" "] * (xmax - xmin + 1) for _ in range(ymin, ymax + 1)]
    for i, y in enumerate(range(ymin, ymax + 1)):
        for j, x in enumerate(range(xmin, xmax +1)):
            if x == -1: continue
            if d[(x, y)] == 1:
                res[i][j] = '#'
            elif d[(x, y)] == 2:
                res[i][j] = 'X'
            elif d[(x, y)] == 3:
                res[i][j] = '-'
            elif d[(x, y)] == 4:
                res[i][j] = 'o'

    print(f"Score: {score}")
    # revert y-dir
    for xs in res:
        line = "".join(xs)
        print(line)


def day13_update_board(board: DefaultDict[Position, int], q: collections.deque):
    while q:
        x = q.popleft()
        y = q.popleft()
        code = q.popleft()
        board[(x, y)] = code
    return board


def day13_part2():
    intcode = day13_read()
    intcode[0] = 2
    q = collections.deque([])
    loc, relbase = 0, 0
    board = collections.defaultdict(int)

    while True:
        q, intcode, loc, relbase = intcomputer(q, intcode, loc, relbase, verbose=False)
        board = day13_update_board(board, q)
        day13_draw_breakout(board)
        c = input()
        if c.startswith("a"):
            q.append(-1)
        elif c.startswith("d"):
            q.append(1)
        else:
            q.append(0)

if __name__ == "__main__":
    day13_part2()
