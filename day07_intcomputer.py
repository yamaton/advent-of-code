import sys
import pathlib
import asyncio
import itertools as it
from typing import Tuple, List


async def intcomputer(
    intcode: str, q_in: asyncio.Queue, q_out: asyncio.Queue, name="name", verbose=True
):
    def _decode_opcode(n: int) -> Tuple[int, bool, bool, bool]:
        op = n % 100  # take two right-most digits as int
        s = str(n).zfill(5)
        mode3 = (
            s[0] == "0"
        )  # '0' position mode, '1' immediate mode ('2': relative mode in day 9)
        mode2 = s[1] == "0"  # True === position mode (pointer)
        mode1 = s[2] == "0"  # False === immediate mode (value)
        return op, mode1, mode2, mode3

    def _bin_op(f, xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        left = xs[xs[loc + 1]] if mode[0] else xs[loc + 1]
        right = xs[xs[loc + 2]] if mode[1] else xs[loc + 2]
        if mode[2]:
            xs[xs[loc + 3]] = f(left, right)
        else:
            raise ValueError("Something is wrong")
        return xs, loc + 4

    def _add(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        return _bin_op(lambda a, b: a + b, xs, loc, *mode)

    def _mul(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        return _bin_op(lambda a, b: a * b, xs, loc, *mode)

    async def _in(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        xs[xs[loc + 1]] = await q_in.get()
        return xs, loc + 2

    async def _out(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        out = xs[xs[loc + 1]] if mode[0] else xs[loc + 1]
        await q_out.put(out)
        return xs, loc + 2

    def _jmp_true(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        x = xs[xs[loc + 1]] if mode[0] else xs[loc + 1]
        if x > 0:
            loc = xs[xs[loc + 2]] if mode[1] else xs[loc + 2]
        else:
            loc += 3
        return xs, loc

    def _jmp_false(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        x = xs[xs[loc + 1]] if mode[0] else xs[loc + 1]
        if x == 0:
            loc = xs[xs[loc + 2]] if mode[1] else xs[loc + 2]
        else:
            loc += 3
        return xs, loc

    def _lt(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        return _bin_op(lambda a, b: int(a < b), xs, loc, *mode)

    def _eq(xs: List[int], loc: int, *mode) -> Tuple[List[int], int]:
        return _bin_op(lambda a, b: int(a == b), xs, loc, *mode)

    opfun = {
        1: _add,
        2: _mul,
        3: _in,
        4: _out,
        5: _jmp_true,
        6: _jmp_false,
        7: _lt,
        8: _eq,
    }

    loc = 0
    while intcode[loc] != 99:
        print(f"{name}: processing {intcode[loc]} at {loc}", file=sys.stderr)
        opcode = intcode[loc]
        op, mode1, mode2, mode3 = _decode_opcode(opcode)
        f = opfun[op]
        if asyncio.iscoroutinefunction(f):
            intcode, loc = await f(intcode, loc, mode1, mode2, mode3)
        else:
            intcode, loc = f(intcode, loc, mode1, mode2, mode3)


async def day07_amp(intcode: str, phases: List[int], verbose=False):
    """
    >>> day07_amp([3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0], [4,3,2,1,0])
    43210
    >>> day07_amp([3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0], [0,1,2,3,4])
    54321
    >>> day07_amp([3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0], [1,0,4,3,2])
    65210
    """
    if isinstance(phases, int):
        phases = str(phases)
    if isinstance(phases, str):
        phases = list(map(int, phases))

    qs = [asyncio.Queue() for _ in range(5 + 1)]  # the last one for recording
    for phase, q in zip(phases, qs):
        q.put_nowait(phase)
    qs[0].put_nowait(0)

    tasks = [
        asyncio.create_task(intcomputer(intcode[:], qs[i], qs[i + 1], name=f"comp-{i}"))
        for i in range(5)
    ]
    await asyncio.gather(*tasks)

    try:
        res = qs[-1].get_nowait()
    except asyncio.QueueEmpty:
        raise ValueError("queue is empty!")
    return res


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


async def day07(verbose=True):
    intcode = day07_read()
    choices = range(5)

    res = 0
    for phases in it.permutations(choices):
        tmp = await day07_amp(intcode, phases, verbose=verbose)
        if tmp > res:
            res = tmp
    print(res)


async def day07_mod():
    intcode = day07_read()
    choices = range(5, 10)

    res = 0
    for phases in it.permutations(choices):
        tmp = await day07_amp_feedback(intcode, phases)
        if tmp > res:
            res = tmp
    print(res)


def get_path(day):
    return pathlib.Path(f"./2019/day{day:02}.txt")


def day07_read():
    file_ = get_path(7)
    assert file_.exists()
    return [int(w) for w in open(file_).read().split(",")]


if __name__ == "__main__":
    asyncio.run(day07())
    # asyncio.run(day07_mod())
