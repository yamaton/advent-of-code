"""
Usage: python day04.py < input.txt

"""

from typing import List


def win_count(line: str) -> int:
    """
    >>> win_count("Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53")
    4
    >>> win_count("Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19")
    2
    """
    _, content = line.strip().split(": ")
    pair = content.split(" | ")
    winning_numbers = {int(s) for s in pair[0].split()}
    hand_numbers = {int(s) for s in pair[1].split()}
    overlap = winning_numbers & hand_numbers
    return len(overlap)


def day04a(line: str) -> int:
    """
    >>> day04a("Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53")
    8
    >>> day04a("Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19")
    2
    """
    x = win_count(line)
    if x > 0:
        return 2 ** (x - 1)
    return 0


def day04b(acc: List[int]) -> int:
    """
    >>> day04b([4, 2, 2, 1, 0, 0])
    30
    """
    n = len(acc)
    state = [1] * n
    for i, win_num in enumerate(acc):
        for j in range(win_num):
            if i + j + 1 < n:
                state[i + j + 1] += state[i]
    return sum(state)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    acc = []
    wincount_list = []
    while True:
        try:
            line = input()
            if not line.strip():
                continue
        except EOFError:
            break
        c = win_count(line)
        wincount_list.append(c)
        res = day04a(line)
        acc.append(res)

    print(sum(acc))
    print(day04b(wincount_list))
