import ast
import itertools
from mna import MNASolver
from pprint import pprint

def exp_to_netlist(s, n1, n2, handler):
    node_idx = 0

    def get_nodes(n):
        nonlocal node_idx

        for _ in range(n):
            yield node_idx
            node_idx += 1

    def parse_child(a, n1, n2):
        if isinstance(a, ast.Call):
            assert len(a.args) > 0

        if isinstance(a, ast.Call) and a.func.id == 'S':
            nodes = [n1, *get_nodes(len(a.args) - 1), n2]

            for arg, nodes in zip(a.args, itertools.pairwise(nodes)):
                parse_child(arg, nodes[0], nodes[1])

        elif isinstance(a, ast.Call) and a.func.id == 'P':
            for idx, arg in enumerate(a.args):
                parse_child(arg, n1, n2)

        elif isinstance(a, ast.Constant):
            handler(n1, n2)

    # Parse AST tree breadth-first, assign node numbers and generate netlist entries
    expr = ast.parse(s).body[0].value
    parse_child(expr, n1, n2)


def calculate(r1, r2, values):
    c = MNASolver()
    c.V('vin', c.gnd, 1)

    def add_node(c, n1, n2):
        value = values.pop(0)
        c.R(n1, n2, value)

    exp_to_netlist('S(%s,%s)' % (r1, r2), 'vin', c.gnd, handler=lambda n1, n2: add_node(c, n1, n2))

    nodes = c.solve()
    nodes.pop('vin')

    return nodes


def num_resistors(*circuits):
    return sum(c.count('1') for c in circuits)


def netlist_to_str(s, out_node):
    strings = []

    def name(x):
        return 'out' if str(x) == str(out_node) else x

    exp_to_netlist(s, 'vin', 'gnd', handler=lambda n1, n2: strings.append('%s_%s' % (name(n1), name(n2))))

    return '(' + ','.join(strings) + ')'


def simulate(r1, r2):
    base_values = calculate(r1, r2, [1] * num_resistors(r1, r2))
    errors = {}

    for idx in range(num_resistors(r1, r2)):
        resistors = [1] * num_resistors(r1, r2)
        resistors[idx] = 1 + 100e-6

        offset_values = calculate(r1, r2, resistors)

        for n in base_values.keys():
            if n not in errors:
                errors[n] = []

            errors[n].append(abs(offset_values[n] - base_values[n]) / base_values[n] * 1e6)

    for k in base_values.keys():
        yield k, base_values[k], max(errors[k]), sum(errors[k]) / len(errors[k])

values = [s.strip() for s in open('circuits.txt').readlines()]
ratios = []

for r1, r2 in itertools.product(values, repeat=2):
    if not (4 <= num_resistors(r1, r2) <= 8):
        continue

    for node, ratio, emax, eavg in simulate(r1, r2):
        netlist = netlist_to_str('S(%s,%s)' % (r1, r2), node)
        ratios.append((1 / float(ratio), netlist, int(emax), int(eavg)))

ratios = [('{:6.3f}'.format(r[0]), r[1], r[2], r[3]) for r in ratios]
ratios = sorted(ratios, key=lambda x: (x[0], x[2], x[3]), reverse=False)

print('%-07s %-75s %8s %8s' % ('V1/V2', 'netlist', 'MAX err', 'AVG err'))

for r in ratios:
    print('%-07s %-75s %8.0f %8.0f' % r)
