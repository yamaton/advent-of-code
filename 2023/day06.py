"""
Usage:
  python day06.py input.txt

  where `input.txt` is a file containing the input string of the form:

  ```
  Time:      7  15   30
  Distance:  9  40  200
  ```

"""
import functools
from typing import Iterable, List, Tuple


def parse_input(input_str: str) -> Tuple[List[int], List[int]]:
    ts_line, ds_line = [ss for s in input_str.split("\n") if (ss := s.strip())]
    times = [int(s) for s in ts_line.split(": ")[-1].split()]
    distances = [int(s) for s in ds_line.split(": ")[-1].split()]
    return times, distances


def solve(t: int, d: int) -> int:
    """
    Solve the equation  x * (t - x) > d and
    returns the number of integers x satisfying the inequality.
    """

    # x * x - t * x + d < 0
    # x = (t +- sqrt(t * t - 4 * d)) / 2
    def f(x):
        return x * x - t * x + d

    sqrt_discriminant = (t * t - 4 * d) ** 0.5
    xmin = int((t - sqrt_discriminant) / 2 + 1)  # +1 to round up
    xmax = int((t + sqrt_discriminant) / 2)

    # glitches may exist due to rounding errors
    if f(xmin) == 0:
        xmin += 1
    if f(xmax) == 0:
        xmax -= 1

    if xmax >= xmin:
        assert f(xmin) < 0
        assert f(xmax) < 0
    return max(0, xmax - xmin + 1)


def product(xs: Iterable[int]) -> int:
    """
    Return the product of the given numbers.
    """
    return functools.reduce(lambda x, y: x * y, xs, 1)


def day06a(input_file: str) -> int:
    times, distances = parse_input(input_file)
    return product(solve(t, d) for t, d in zip(times, distances))


def parse_input_mod(input_str: str) -> Tuple[int, int]:
    ts_line, ds_line = [ss for s in input_str.split("\n") if (ss := s.strip())]
    time = int("".join(s.strip() for s in ts_line.split(": ")[-1].split()))
    distance = int("".join(s.strip() for s in ds_line.split(": ")[-1].split()))
    return time, distance


def day06b(input_file: str) -> int:
    t, d = parse_input_mod(input_file)
    return solve(t, d)


if __name__ == "__main__":
    import sys

    input_str = open(sys.argv[1]).read()
    print(day06a(input_str))
    print(day06b(input_str))
