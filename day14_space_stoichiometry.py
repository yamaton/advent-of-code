from utils import get_path
import collections


def day14_read():
    path = get_path(14)
    return [line.strip() for line in open(path).readlines()]


def day14_parse(lines):
    formuli = dict()
    for line in lines:
        before, after = line.split(" => ")
        sources = before.split(", ")
        bag = collections.Counter()
        for source in sources:
            count, name = source.strip().split()
            bag += {name: int(count)}

        targets = after.split(", ")
        assert len(targets) == 1

        count, name = after.strip().split()
        formuli[name] = (int(count), bag)
    return formuli


def toposort(adj, vertices=None):
    """
    Args:
        adj: (list of list) adjacency list
        vertices (iterable): graph vertices
    Returns:
        topo_order: list of vertices in topologically-sorted order
        parent: dict {vertex: vertex or None} indicating parent of each vertex
    """
    parent = dict()
    finish_time = dict()
    time = 0

    if vertices is None:
        vertices = set()
        for k in adj:
            vertices.add(k)
            for v in adj[k]:
                vertices.add(v)

    def dfs_visit(u):
        nonlocal time
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                dfs_visit(v)
        time += 1
        finish_time[u] = time

    for i in vertices:
        if i not in parent:
            parent[i] = None
            dfs_visit(i)

    topo_order = sorted(finish_time.keys(), key=lambda k: finish_time[k], reverse=True)
    return topo_order, parent


def _to_adj(formuli):
    adj = collections.defaultdict(list)
    for material in formuli:
        _, ingredients = formuli[material]
        adj[material] = list(ingredients.keys())
    return adj


def day14(formuli):
    def get_weight():
        adj = _to_adj(formuli)
        print(f"adj: {adj}")
        topo_order, _ = toposort(adj)
        topo_weight = dict()
        for i, item in enumerate(topo_order):
            topo_weight[item] = i
        return topo_weight

    def _add(name, cnt):
        assert name != "ORE"
        cnt_needed, ingredients = formuli[name]
        multiplier = (cnt + cnt_needed - 1) // cnt_needed
        ingredients = collections.Counter(
            {tag: cnt * multiplier for tag, cnt in ingredients.items()}
        )
        return ingredients

    weight = get_weight()
    print(weight)

    hand = collections.Counter({"FUEL": 1})
    while len(hand) > 1 or ("ORE" not in hand):
        name = min(hand.keys(), key=lambda k: weight[k])
        cnt = hand.pop(name)
        hand += _add(name, cnt)
        print(hand)

    return hand["ORE"]


if __name__ == "__main__":
    raw = """
    9 ORE => 2 A
    8 ORE => 3 B
    7 ORE => 5 C
    3 A, 4 B => 1 AB
    5 B, 7 C => 1 BC
    4 C, 1 A => 1 CA
    2 AB, 3 BC, 4 CA => 1 FUEL""".strip().split(
        "\n"
    )

    raw = """
    157 ORE => 5 NZVS
    165 ORE => 6 DCFZ
    44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
    12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
    179 ORE => 7 PSHF
    177 ORE => 5 HKGWZ
    7 DCFZ, 7 PSHF => 2 XJWVT
    165 ORE => 2 GPVTF
    3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""".strip().split(
        "\n"
    )

    raw = """
    2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
    17 NVRVD, 3 JNWZP => 8 VPVL
    53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
    22 VJHF, 37 MNCFX => 5 FWMGM
    139 ORE => 4 NVRVD
    144 ORE => 7 JNWZP
    5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
    5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
    145 ORE => 6 MNCFX
    1 NVRVD => 8 CXFTF
    1 VJHF, 6 MNCFX => 4 RFSQX
    176 ORE => 6 VJHF""".strip().split(
        "\n"
    )

    raw = """
    171 ORE => 8 CNZTR
    7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
    114 ORE => 4 BHXH
    14 VRPVC => 6 BMBT
    6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
    6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
    15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
    13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
    5 BMBT => 4 WPTQ
    189 ORE => 9 KTJDG
    1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
    12 VRPVC, 27 CNZTR => 2 XDBXC
    15 KTJDG, 12 BHXH => 5 XCVML
    3 BHXH, 2 VRPVC => 7 MZWV
    121 ORE => 7 VRPVC
    7 XCVML => 6 RJRHP
    5 BHXH, 4 VRPVC => 5 LTCX""".strip().split(
        "\n"
    )
    raw = day14_read()
    formuli = day14_parse(raw)
    print(formuli)
    res = day14(formuli)
    print(res)

