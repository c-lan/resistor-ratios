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


def calculate_v(r1, r2, values):
    c = MNASolver()
    c.V('vin', c.gnd, 1)

    def add_node(c, n1, n2):
        value = values.pop(0)
        c.R(n1, n2, value)

    exp_to_netlist('S(%s,%s)' % (r1, r2), 'vin', c.gnd, handler=lambda n1, n2: add_node(c, n1, n2))

    return c.solve()


def calculate_rin(r1, r2):
    c = MNASolver()
    c.I('vin', c.gnd, 1)

    exp_to_netlist('S(%s,%s)' % (r1, r2), 'vin', c.gnd, handler=lambda n1, n2: c.R(n1, n2, 1))

    return c.solve()['vin']


def calculate_rout(r1, r2, node):
    c = MNASolver()
    c.I(node, c.gnd, 1)

    exp_to_netlist('S(%s,%s)' % (r1, r2), c.gnd, c.gnd, handler=lambda n1, n2: c.R(n1, n2, 1))

    return c.solve()[node]


def num_resistors(*circuits):
    return sum(c.count('1') for c in circuits)


def netlist_to_str(s, out_node):
    strings = []

    def name(x):
        return 'out' if str(x) == str(out_node) else x

    exp_to_netlist(s, 'vin', 'gnd', handler=lambda n1, n2: strings.append('%s_%s' % (name(n1), name(n2))))

    return '(' + ','.join(strings) + ')'


def simulate(r1, r2):
    base_values = calculate_v(r1, r2, [1] * num_resistors(r1, r2))
    rin = calculate_rin(r1, r2)
    errors = {}

    base_values.pop('vin')

    for idx in range(num_resistors(r1, r2)):
        resistors = [1] * num_resistors(r1, r2)
        resistors[idx] = 1 + 100e-6

        offset_values = calculate_v(r1, r2, resistors)

        for n in base_values.keys():
            if n not in errors:
                errors[n] = []

            errors[n].append((offset_values[n] - base_values[n]) / base_values[n] * 1e6)

    for k in base_values.keys():
        rout = calculate_rout(r1, r2, k)

        yield k, base_values[k], errors[k], rin, rout

circuits = [s.strip() for s in open('circuits.txt').readlines()]
ratios = []
max_resistors = max(num_resistors(c) for c in circuits) + 1

assert max_resistors >= 4

for r1, r2 in itertools.product(circuits, repeat=2):
    if not (4 <= num_resistors(r1, r2) <= max_resistors):
        continue

    for node, ratio, errors, rin, rout in simulate(r1, r2):
        netlist = netlist_to_str('S(%s,%s)' % (r1, r2), node)
        ratios.append((1 / float(ratio), netlist, errors, rin, rout))

def render_row(row):
    ratio, netlist, errors, rin, rout = row

    errors_abs = [abs(e) for e in errors]
    emax = round(max(errors_abs))
    eavg = round(sum(errors_abs) / len(errors))

    errors_s = ' '.join('{:<+3.0f}'.format(e) for e in errors)

    return (
        '{:7.3f}'.format(ratio),
        len(errors),
        netlist,
        errors_s,
        '{:8d}'.format(emax),
        '{:8d}'.format(eavg),
        '{:8.3f}'.format(rin),
        '{:8.3f}'.format(rout)
    )

ratios = [render_row(r) for r in ratios]
ratios = sorted(ratios, key=lambda x: (x[0], x[4], x[5]), reverse=False)

for r in [('V1/V2', 'N', 'netlist', 'errors', 'MAX err', 'AVG err', 'Rin', 'Rout')] + ratios:
    print('%07s %02s %-100s %-50s %8s %8s %8s %8s' % r)
