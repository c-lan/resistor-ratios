import sys
import argparse
from collections import namedtuple

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num-resistors', type=int, nargs='*')
parser.add_argument('-c', '--count', type=int, help='How many combinations for a given ratio to display')
parser.add_argument('-i', '--min-rin', type=float)
parser.add_argument('-o', '--max-rout', type=float)
parser.add_argument('-e', '--max-err', type=int)
parser.add_argument('min', type=float)
parser.add_argument('max', type=float)

args = parser.parse_args()

ParsedLine = namedtuple('ParsedLine', ('text', 'ratio', 'num_resistors', 'rin', 'rout', 'max_err'))

def parse_line(s):
    items = s.split()

    return ParsedLine(
        text=s,
        ratio=float(items[0]),
        num_resistors=items[2].count('_'),
        rin=float(items[-2]),
        rout=float(items[-1]),
        max_err=int(items[-4])
    )

last_ratio = 0
last_ratio_count = 0

f = open('ratios.txt', 'rt')
print(next(f), end='')

for s in f:
    line = parse_line(s)

    if line.ratio > args.max:
        continue

    if line.ratio < args.min:
        continue

    if args.num_resistors and line.num_resistors not in args.num_resistors:
        continue

    if args.min_rin and line.rin < args.min_rin:
        continue

    if args.max_rout and line.rout > args.max_rout:
        continue

    if args.max_err and line.max_err > args.max_err:
        continue

    if args.count:
        if last_ratio != line.ratio:
            last_ratio = line.ratio
            last_ratio_count = 1
        else:
            last_ratio_count += 1

        if last_ratio_count > args.count:
            continue

    print(line.text, end='')
