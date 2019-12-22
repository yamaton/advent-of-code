import sys
import pathlib
import asyncio
import itertools as it
import collections
from typing import Tuple, List, DefaultDict

Intcode = DefaultDict[int, int]
Modes = Tuple[str, str, str]


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
        print(
            f"{name}: processing {intcode[loc]} at {loc} with relbase {relbase}",
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


def day09_read():
    file_ = get_path(9)
    assert file_.exists()
    return [int(w) for w in open(file_).read().split(",")]


async def day09(intcode, inputs=None):
    q_in = asyncio.Queue()
    if isinstance(inputs, List):
        for x in inputs:
            q_in.put_nowait(x)
    q_out = asyncio.Queue()
    await intcomputer(intcode, q_in, q_out)
    print(q_out)


async def day07_amp_feedback(intcode: str, phases: List[int], verbose=False):
    if isinstance(phases, int):
        phases = str(phases)
    if isinstance(phases, str):
        phases = list(map(int, phases))

    qs = [asyncio.Queue() for _ in range(5)]
    for phase, q in zip(phases, qs):
        q.put_nowait(phase)
    qs[0].put_nowait(0)

    tasks = []
    for i in range(5):
        i_next = (i + 1) % 5
        task = asyncio.create_task(
            intcomputer(intcode[:], qs[i], qs[i_next], name=f"comp-{i}")
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    try:
        res = qs[0].get_nowait()
    except asyncio.QueueEmpty:
        raise ValueError("Failed to get the remnant of queue")
    return res


if __name__ == "__main__":
    # intcode = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
    # intcode = [1102, 34915192, 34915192, 7, 4, 7, 99, 0]
    # intcode = [104, 1125899906842624, 99]
    intcode = day09_read()
    print(intcode)

    # asyncio.run(day09(intcode, [1]))
    asyncio.run(day09(intcode, [2]))
