"""
Usage: python day01.py < input.txt

"""

def day01a(word: str) -> int:
    """Get two-digit integer fro the first and the last digit"""
    first = int(next(s for s in word if s.isdigit()))
    last = int(next(s for s in reversed(word) if s.isdigit()))
    return first * 10 + last


def day01b(word: str) -> int:
    """Get two-digit integer from the first and the last digit"""
    digits = [
        "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine",
    ]
    s2int = {d: i for i, d in enumerate(digits, 1)}
    single_digits = {str(n): n for n in range(1, 10)}
    s2int.update(single_digits)

    indices_number_pairs_left = {ind: s2int[d] for d in s2int if (ind := word.find(d)) != -1}
    indices_number_pairs_right = {ind: s2int[d] for d in s2int if (ind := word.rfind(d)) != -1}
    _, first = min(indices_number_pairs_left.items(), key=lambda tup: tup[0])
    _, last = max(indices_number_pairs_right.items(), key=lambda tup: tup[0])
    return first * 10 + last


if __name__ == "__main__":
    acc_a = []
    acc_b = []
    while True:
        try:
            w = input().strip()
            if w:
                res_a = day01a(w)
                res_b = day01b(w)
                # print(f"{w}: {res_b}")
                acc_a.append(res_a)
                acc_b.append(res_b)
        except EOFError:
            break
    print(sum(acc_a))
    print(sum(acc_b))
