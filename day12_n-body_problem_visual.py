"""
Day 12: N-body problem

Part 1
Implement simulation of particles based given the map

v_k^(n+1) = \sum_i \sign (x_i^(n) - x_k^(n))
x_k^(n+1) = x_k^(n) + v_k^(n+1)

where x_k^(n) and v_k^(n) is 3-d position and velocity of k-th particle at step n.
Ininital condition is given as

x_k^(0) = (from input values)
v_k^(0) = 0


Part 2 is to find preiod of periodic orbit.
The dynamical system has a conserved quantity over time such that

\sum_k x_k^(n) = \sum_k x_k^(0)
\sum_k v_k^(n) = 0

Note that x, y and z components are independent; i.e. we can treat them separately.



"""
import copy
import functools
import math
import pathlib
import numpy as np

# import plotly
import matplotlib.pyplot as plt


def _lcm(a: int, b: int) -> int:
    return a // math.gcd(a, b) * b


def lcm(xs):
    return functools.reduce(_lcm, xs)


def _get_path(day):
    return pathlib.Path(f"./2019/day{day:02}.txt")


def day12_read():
    path = _get_path(12)
    return open(path).readlines()


def day12_parse(inputs):
    res = []
    for line in inputs:
        items = line.strip()[1:-1].split(", ")
        pos = [int(x[2:]) for x in items]
        res.append(pos)
    return res


def _day12_update(xs: np.array, vs: np.array):
    for i, _ in enumerate(xs):
        v_diffs = np.sign(xs - xs[i])
        vs[i] += v_diffs.sum(axis=0)
    xs += vs

    return xs, vs


def day12_energy(xs: np.array, vs: np.array):
    return np.sum(np.abs(xs).sum(axis=1) * np.abs(vs).sum(axis=1))


def xs_vs_sum(xs, vs):
    return (xs.sum(axis=0), vs.sum(axis=0))


def day12(inputs, steps=1000):
    n = len(inputs)
    print(f"n = {n}")
    xs = np.array(inputs)
    vs = np.zeros(shape=(n, 3), dtype=np.int64)
    for _ in range(steps):
        xs, vs = _day12_update(xs, vs)
        # if xs[0, 1] == xs_y0:
        #     print(f"y-comp returned at {i}")

    return day12_energy(xs, vs)


def day12_mod(inputs):
    n = len(inputs)
    print(f"n = {n}")
    xs = np.array(inputs)
    vs = np.zeros(shape=(n, 3), dtype=np.int64)

    xs_ini = copy.deepcopy(xs)
    vs_ini = copy.deepcopy(vs)
    periods = [0, 0, 0]
    steps = 0

    while not all(p > 0 for p in periods):
        xs, vs = _day12_update(xs, vs)
        steps += 1
        for component in range(3):
            if (
                periods[component] == 0
                and (xs_ini[:, component] == xs[:, component]).all()
                and (vs_ini[:, component] == vs[:, component]).all()
            ):
                periods[component] = steps
                print(f"component-{component} step={steps}")

    return lcm(periods)


if __name__ == "__main__":
    # raw = """<x= -1, y=  0, z=  2>
    #     <x=  2, y=-10, z= -7>
    #     <x=  4, y= -8, z=  8>
    #     <x=  3, y=  5, z= -1>""".strip().split(
    #     "\n"
    # )

    # raw = """
    # <x=-8, y=-10, z=0>
    # <x=5, y=5, z=10>
    # <x=2, y=-7, z=3>
    # <x=9, y=-8, z=-3>""".strip().split(
    #     "\n"
    # )

    raw = day12_read()
    inputs = day12_parse(raw)
    out = day12_mod(inputs)
    print(f"Period = {out}")
    # plt.plot(range(len(x_traj)), x_traj)
    # plt.show()
