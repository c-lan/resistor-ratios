import itertools
from PySpice.Spice.Netlist import Circuit


def to_str(u):
    return u if isinstance(u, str) else ''.join(u)


def resistor_count(comb):
    return sum([2 if r == 'P' else 1 for r in comb])


def count_useless(comb):
    idx_trailing =  to_str(comb).rfind('G')
    trailing_part = comb[idx_trailing + 1:]

    trailing_count = resistor_count(trailing_part)
    leading_count = 0

    for r in comb:
        if r == 'G':
            leading_count += 1
        else:
            break

    return trailing_count + leading_count


def cleanup_useless(comb):
    return to_str(comb).lstrip('G').rstrip('SP')


def count_nodes(comb):
    comb = to_str(comb).replace('G', '')
    inner_count = len(comb) - 1

    # Inner connections, input and output, ground is available by default
    return inner_count + 2


def assemble(comb, offset_idx=None, offset=0):
    circuit = Circuit('divider')

    circuit.V('input', 1, circuit.gnd, 1)

    node_idx = 1
    r_idx = 1

    if offset_idx is None:
        offset_idx = -1

    for r in comb:

        def get_value():
            return 1 + offset if r_idx == offset_idx else 1

        if r == 'S':
            circuit.R(r_idx, node_idx, node_idx + 1, get_value())
            r_idx += 1
            node_idx += 1

        elif r == 'P':
            circuit.R(r_idx, node_idx, node_idx + 1, get_value())
            r_idx += 1
            circuit.R(r_idx, node_idx, node_idx + 1, get_value())
            r_idx += 1
            node_idx += 1

        else:
            circuit.R(r_idx, node_idx, circuit.gnd, get_value())
            r_idx += 1


    return circuit


def calculate(circuit):
    simulator = circuit.simulator()
    analysis = simulator.operating_point()

    last_node = max(analysis.nodes.keys())

    return 1 / float(analysis.nodes[last_node])


def simulate(comb, offset=100e-6):
    base_value = calculate(assemble(comb))
    errors = []

    for idx in range(8):
        offset_value = calculate(assemble(comb, idx + 1, offset))
        error = abs((offset_value - base_value) / base_value)

        if error > 1e-6:
            errors.append(error)

    return base_value, max(errors), sum(errors) / len(errors)


sets = {}

for comb in itertools.product(['S', 'G', 'P'], repeat=8):
    # Reject 1:1 ratios
    if 'G' not in comb:
        continue

    # Reject excessive leading grounds or trailing series
    # if count_useless(comb) > 3:
        # continue

    comb = cleanup_useless(comb)

    # Reject > 8
    if resistor_count(comb) > 8:
        continue

    if comb in sets or len(comb) == 0:
        continue

    sets[comb] = simulate(comb)

data = []

for k, v in sets.items():
    value, max_error, avg_error = v
    data.append((k, round(value, 2), round(max_error * 1e6), round(avg_error * 1e6)))

data.sort(key=lambda x: (x[1], x[2]))

print('%-12s %8s %10s %10s' % ('combination', 'V ratio', 'MAX error', 'AVG error'))

for key, value, max_error, avg_error in data:
    print('%-012s %8.2f %10.0f %10.0f' % (key, round(value, 2), max_error, avg_error))

