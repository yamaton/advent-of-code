import pathlib
import bs4
import urllib


def get_title(day):
    f = urllib.request.urlopen(f"https://adventofcode.com/2019/day/{day}")
    soup = bs4.BeautifulSoup(f.read())
    print(soup.h2.text.replace("-", "").strip())


def get_path(day):
    return pathlib.Path(f"./2019/day{day:02}.txt")


def read_intcode(path):
    return [int(x) for x in open(path).read().strip().split(",")]
