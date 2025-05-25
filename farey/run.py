import sys
import itertools
from pprint import pprint

def S(*args):
    return sum(x for  x in args)

def P(*args):
    return 1 / sum(1 / x for x in args)

class Circuit(object):
    def __init__(self, expression, expected):
        self.expression = expression
        self.compiled = self.compile(expression)
        self.length = expression.count('1')

        assert abs(self.eval([1] * self.length) - expected) < 1e-4

    @staticmethod
    def compile(expression):
        num = expression.count('1')
        parts = expression.split('1')
        subs = ['r[%d]' % i for i in range(num)] + ['']

        return ''.join(''.join(x) for x in zip(parts, subs))

    def eval(self, values):
        if len(values) < self.length:
            raise ValueError('Not enough resistor values provided')

        return eval(self.compiled, globals={}, locals={
            'S': S,
            'P': P,
            'r': values
        })

    def __repr__(self):
        return self.expression

    def __len__(self):
        return self.length

# from: "Farey sequences and resistor networks"
values = [
    [
        Circuit('S(1)', 1)
    ],
    [
        Circuit('P(1,1)', 1/2),
        Circuit('S(1,1)', 2)
    ],
    [
        Circuit('P(1,1,1)', 1/3),
        Circuit('P(S(1,1),1)', 2/3),
        Circuit('S(1,P(1,1))', 3/2),
        Circuit('S(1,1,1)', 3)
    ],
    [
        Circuit('P(1,1,1,1)', 1/4),
        Circuit('P(S(1,1),1,1)', 2/5),
        Circuit('P(S(P(1,1),1),1)', 3/5),
        Circuit('P(S(1,1,1),1)', 3/4),
        Circuit('P(S(1,1),S(1,1))', 1),
        Circuit('S(P(1,1,1),1)', 4/3),
        Circuit('S(P(S(1,1),1),1)', 5/3),
        Circuit('S(P(1,1),1,1)', 5/2),
        Circuit('S(1,1,1,1)', 4)
    ],
    [
        Circuit('P(1,1,1,1,1)', 1/5),
        Circuit('P(S(1,1),1,1,1)', 2/7),
        Circuit('P(S(P(1,1),1),1,1)', 3/8),
        Circuit('P(S(1,1,1),1,1)', 3/7),
        Circuit('P(S(1,1),S(1,1),1)', 1/2),
        Circuit('P(S(P(1,1,1),1),1)', 4/7),
        Circuit('P(S(P(S(1,1),1),1),1)', 5/8),
        Circuit('P(S(P(1,1),S(1,1)),1)', 5/7),
        Circuit('P(S(1,1,1,1),1)', 4/5),
        Circuit('S(P(1,1),P(1,1,1))', 5/6),
        Circuit('P(S(1,1),S(P(1,1),1))', 6/7),
        Circuit('S(P(1,1),P(S(1,1),1))', 7/6),
        Circuit('P(S(1,1),S(1,1,1))', 6/5),
        Circuit('S(P(1,1,1,1),1)', 5/4),
        Circuit('S(P(S(1,1),P(1,1)),1)', 7/5),
        Circuit('S(P(S(P(1,1),1),1),1)', 8/5),
        Circuit('S(P(S(1,1,1),1),1)', 7/4),
        Circuit('S(P(1,1),P(1,1),1)', 2),
        Circuit('S(P(1,1,1),1,1)', 7/3),
        Circuit('S(P(S(1,1),1),1,1)', 8/3),
        Circuit('S(P(1,1),1,1,1)', 7/2),
        Circuit('S(1,1,1,1,1)', 5)
    ]
]

values = sum(values, [])
ratios = []


def divider(r1, r2, values):
    r1e = r1.eval(values[:len(r1)])
    r2e = r2.eval(values[len(r1):])

    return r2e / (r1e + r2e)


def simulate(r1, r2, offset=100e-6):
    base_value = divider(r1, r2, [1] * (len(r1) + len(r2)))
    errors = []

    for idx in range(len(r1) + len(r2)):
        resistors = [1] * (len(r1) + len(r2))
        resistors[idx] = 1 + offset

        offset_value = divider(r1, r2, resistors)
        error = abs((offset_value - base_value) / base_value)

        if error > 1e-6:
            errors.append(error)

    return base_value, max(errors), sum(errors) / len(errors)


for r1, r2 in itertools.product(values, repeat=2):
    if not (4 <= len(r1) + len(r2) <= 8):
        continue

    ratio, dmax, davg = simulate(r1, r2)
    ratios.append((1 / ratio, r1, r2, dmax * 1e6, davg * 1e6))

ratios = sorted(ratios, key=lambda x: (x[0], x[3]), reverse=False)
ratios = [('%.2f' % (r[0]), r[1], r[2], r[3], r[4]) for r in ratios]

print('%-05s %-24s %-24s %10s %10s' % ('V1/V2', 'R1', 'R2', 'MAX error', 'AVG error'))

for r in ratios:
    print('%-05s %-24s %-24s %10.0f %10.0f' % r)
