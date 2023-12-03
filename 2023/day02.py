"""
Usage: python day02.py < input.txt

"""
from pydantic import BaseModel
from typing import Iterable

class Hand(BaseModel):
    red: int = 0
    green: int = 0
    blue: int = 0


def parse_event(s: str) -> Hand:
    count_color_pairs = [tup.split() for tup in s.split(", ")]
    hand_dict = {color: int(count) for count, color in count_color_pairs}
    hand = Hand(**hand_dict)
    return hand


def is_good(hand: Hand) -> bool:
    return hand.red <= 12 and hand.green <= 13 and hand.blue <= 14


def power(hand: Hand) -> int:
    return hand.red * hand.green * hand.blue


def reduce(hands: Iterable[Hand]) -> Hand:
    r, g, b = 0, 0, 0
    for h in hands:
        r = max(r, h.red)
        g = max(g, h.green)
        b = max(b, h.blue)
    return Hand(red=r, green=g, blue=b)


def day02a(s: str) -> int:
    game_id_str, content = s.split(": ")
    hands = [parse_event(s.strip()) for s in content.split("; ")]
    if all(is_good(hand) for hand in hands):
        game_id = game_id_str.split()[1]
        return int(game_id)
    return 0


def day02b(s: str) -> int:
    _, content = s.split(": ")
    hands = [parse_event(s.strip()) for s in content.split("; ")]
    hand = reduce(hands)
    return power(hand)


if __name__ == "__main__":
    acc = []
    acc2 = []
    while True:
        try:
            line = input().strip()
            if line:
                res = day02a(line)
                res2 = day02b(line)
                print(f"{line} --> {res2}")
                acc.append(res)
                acc2.append(res2)
        except EOFError:
            break
    print(sum(acc))
    print(sum(acc2))
