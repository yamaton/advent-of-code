"""
Usage:
  python day03.py input.txt

Requirements:
  - pydantic

"""
from pydantic import BaseModel
from typing import Set, Tuple


class Coordinate(BaseModel):
    x: int
    y: int

    def __repr__(self):
        return f"C({self.x}, {self.y})"

    class Config:
        frozen = True


class Part(BaseModel):
    number: int
    coordinates: frozenset[Coordinate]

    def __repr__(self):
        return f"Part({self.number}, {self.coordinates})"

    class Config:
        frozen = True


class Symbol(BaseModel):
    symbol: str
    coord: Coordinate

    def __repr__(self):
        return f"Symbol({self.symbol}, {self.coord})"

    class Config:
        frozen = True


def neighbors(coord: Coordinate, grid_shape: Tuple[int, int]) -> frozenset[Coordinate]:
    xmax, ymax = grid_shape

    def _f():
        x = coord.x
        y = coord.y
        for _i in (x - 1, x, x + 1):
            if _i < 0 or _i >= xmax:
                continue
            for _j in (y - 1, y, y + 1):
                if _j < 0 or _j >= ymax:
                    continue
                yield Coordinate(x=_i, y=_j)

    return frozenset(_f())


def locate_symbols(grid: list[str]) -> frozenset[Symbol]:
    def _f():
        for i, row in enumerate(grid):
            for j, c in enumerate(row):
                if c != "." and not c.isdigit():
                    coord = Coordinate(x=i, y=j)
                    yield Symbol(symbol=c, coord=coord)

    return frozenset(_f())


def locate_parts(grid: list[str]) -> frozenset[Part]:
    def _f():
        for i, row in enumerate(grid):
            coords: Set[Coordinate] = set()
            str_list = []
            for j, c in enumerate(row):
                if c.isdigit():
                    coords.add(Coordinate(x=i, y=j))
                    str_list.append(c)
                else:
                    if coords:
                        yield Part(
                            number=int("".join(str_list)), coordinates=frozenset(coords)
                        )
                        coords = set()
                        str_list = []
            if coords:
                yield Part(number=int("".join(str_list)), coordinates=frozenset(coords))

    return frozenset(_f())


def day03a(grid: list[str]) -> int:
    symbols = locate_symbols(grid)
    parts = locate_parts(grid)
    shape = len(grid), len(grid[0])
    territory = {loc for sym in symbols for loc in neighbors(sym.coord, shape)}  # type: ignore
    selected_parts = {p for p in parts if any(p.coordinates & territory)}  # type: ignore
    return sum(p.number for p in selected_parts)


def day03b(grid: list[str]) -> int:
    symbols = locate_symbols(grid)
    parts = locate_parts(grid)
    shape = len(grid), len(grid[0])
    power = 0
    for sym in symbols:
        territory = {loc for loc in neighbors(sym.coord, shape)}  # type: ignore
        xs = [p for p in parts if any(p.coordinates & territory)]  # type: ignore
        if len(xs) == 2:
            power += xs[0].number * xs[1].number
    return power


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "r") as f:
        grid = [line.strip() for line in f.readlines()]
    print(day03a(grid))
    print(day03b(grid))
