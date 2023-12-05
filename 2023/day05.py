"""
Usage: python day05.py input.txt

"""

from typing import List, Tuple
from itertools import zip_longest

from pydantic import BaseModel


# https://docs.python.org/3.11/library/itertools.html
def grouper(iterable, n, *, incomplete="fill", fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == "strict":
        return zip(*args, strict=True)
    if incomplete == "ignore":
        return zip(*args)
    else:
        raise ValueError("Expected fill, strict, or ignore")


class Range(BaseModel):
    start: int
    length: int

    def __lt__(self, other: "Range"):
        return self.start < other.start


class RangeMap(BaseModel):
    dst: int
    src: int
    length: int


def _parse_section(section: str) -> List[RangeMap]:
    _, *rest = section.split("\n")
    return [
        RangeMap(dst=int(d), src=int(s), length=int(l))
        for d, s, l in [line.split() for line in rest]
    ]


def parse_input(input_str: str) -> Tuple[List[int], List[List[RangeMap]]]:
    """
    Parse the input string to extract the initial seed numbers
    and the conversion maps for each category.

    :param input_str: The input string containing seed numbers and conversion maps.
    :return: A tuple containing the list of initial seed numbers and the list of conversion maps.
    """
    seed_str, *rest = input_str.strip().split("\n\n")
    seeds = [int(s) for s in seed_str.split(": ")[1].split()]
    maps = [_parse_section(section) for section in rest]
    return seeds, maps


def convert(conversion_map: List[RangeMap], number: int) -> int:
    """
    Convert a source number to a destination number using the given conversion map.

    :param number: The source number to be converted.
    :param conversion_map: The conversion map to be used for the conversion.
    :return: The destination number after conversion.
    """
    for r in conversion_map:
        if r.src <= number < r.src + r.length:
            return r.dst + (number - r.src)
    return number


def apply(m: RangeMap, r: Range) -> Tuple[List[Range], List[Range]]:
    """
    Apply a range map to a range.
    Returns a tuple containing the list of unmapped and mapped ranges.

    >>> apply(RangeMap(dst=100, src=0, length=10), Range(start=15, length=10))
    ([Range(start=15, length=10)], [])

    >>> apply(RangeMap(dst=100, src=15, length=10), Range(start=5, length=10))
    ([Range(start=5, length=10)], [])

    >>> apply(RangeMap(dst=100, src=0, length=100), Range(start=15, length=10))
    ([], [Range(start=115, length=10)])

    >>> apply(RangeMap(dst=100, src=0, length=10), Range(start=6, length=10))
    ([Range(start=10, length=6)], [Range(start=106, length=4)])

    >>> apply(RangeMap(dst=100, src=6, length=10), Range(start=0, length=10))
    ([Range(start=0, length=6)], [Range(start=100, length=4)])

    >>> apply(RangeMap(dst=200, src=30, length=10), Range(start=0, length=100))
    ([Range(start=0, length=30), Range(start=40, length=60)], [Range(start=200, length=10)])
    """
    if r.start >= m.src + m.length:
        return [r], []

    if r.start + r.length <= m.src:
        return [r], []

    # if entire range is mapped
    if m.src <= r.start and r.start + r.length <= m.src + m.length:
        return [], [Range(start=m.dst + r.start - m.src, length=r.length)]

    # if lower part of range is mapped
    if m.src <= r.start and r.start + r.length > m.src + m.length:
        overlap_len = m.src + m.length - r.start
        return (
            [
                Range(
                    start=r.start + overlap_len,
                    length=r.length - overlap_len,
                )
            ],
            [Range(start=m.dst + r.start - m.src, length=overlap_len)],
        )

    # if upper part of range is mapped
    if r.start < m.src and r.start + r.length <= m.src + m.length:
        overlap_len = r.start + r.length - m.src
        return (
            [Range(start=r.start, length=r.length - overlap_len)],
            [Range(start=m.dst, length=overlap_len)],
        )

    # if middle part of range is mapped
    if r.start < m.src and m.src + m.length < r.start + r.length:
        return (
            [
                Range(start=r.start, length=m.src - r.start),
                Range(
                    start=m.src + m.length, length=r.start + r.length - m.src - m.length
                ),
            ],
            [Range(start=m.dst, length=m.length)],
        )

    print(m)
    print(r)
    raise ValueError("ERROR")


def apply_batch(maps: List[List[RangeMap]], ranges: List[Range]) -> List[Range]:
    """ """
    res = ranges[:]
    for ms in maps:
        res = apply_session(ms, res)
    return res


def apply_session(maps: List[RangeMap], ranges: List[Range]) -> List[Range]:
    """
    Apply a list of range maps to a list of ranges.

    :param maps: The list of range maps to be applied.
    :param ranges: The list of ranges to be mapped.
    :return: The list of ranges after the mapping.
    """
    mapped = []
    unmapped = ranges[:]
    for m in maps:
        acc = []
        for r in unmapped:
            tmp_unmapped, tmp_mapped = apply(m, r)
            mapped.extend(tmp_mapped)
            acc.extend(tmp_unmapped)
        unmapped = acc

    res = sorted(mapped + unmapped)
    return res


def day05a(input_str: str) -> int:
    """
    Find the lowest location number that corresponds to any of the initial seed numbers.

    :param input_str: The input string containing seed numbers and conversion maps.
    :return: The lowest location number.
    """
    seeds, maps = parse_input(input_str)
    res = 1000000000000

    for seed in seeds:
        n = seed
        for conversion_map in maps:
            n = convert(conversion_map, n)
        res = min(res, n)

    return res


def day05b(input_str: str) -> int:
    """
    Find the lowest location number that corresponds to any of the initial seed numbers.

    :param input_str: The input string containing seed numbers and conversion maps.
    :return: The lowest location number.
    """
    seeds, maps = parse_input(input_str)
    seed_ranges = sorted(
        [Range(start=int(s), length=int(l)) for s, l in grouper(seeds, 2)]
    )
    res = apply_batch(maps, seed_ranges)
    return min(res, key=lambda r: r.start).start


if __name__ == "__main__":
    import sys

    input_str = open(sys.argv[1]).read()
    print(day05a(input_str))
    print(day05b(input_str))
