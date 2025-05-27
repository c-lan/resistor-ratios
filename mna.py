import numpy

# https://cheever.domains.swarthmore.edu/Ref/mna/MNA3.html

class MNASolver(object):
    def __init__(self, dtype=None):
        self.node_names = []
        self.admittances = []
        self.sources_v = []
        self.sources_i = []
        self.gnd = object()
        self.dtype = dtype or numpy.double

    def _get_node_idx(self, name):
        if name is self.gnd:
            return self.gnd

        name = str(name)

        if name not in self.node_names:
            self.node_names.append(name)

        return self.node_names.index(name)

    def R(self, node1, node2, value):
        self.admittances.append((
            self._get_node_idx(node1),
            self._get_node_idx(node2),
            1 / self.dtype(value)
        ))

    def V(self, node1, node2, value):
        self.sources_v.append((
            self._get_node_idx(node1),
            self._get_node_idx(node2),
            self.dtype(value)
        ))

    def I(self, node1, node2, value):
        self.sources_i.append((
            self._get_node_idx(node1),
            self._get_node_idx(node2),
            self.dtype(value)
        ))

    def d(val):
        return val

    def solve(self):
        N = len(self.node_names)
        M = len(self.sources_v)

        G = numpy.zeros((N, N), dtype=self.dtype)
        B = numpy.zeros((N, M), dtype=self.dtype)

        i = numpy.zeros((N, 1), dtype=self.dtype)
        e = numpy.zeros((M, 1), dtype=self.dtype)

        for n1, n2, val in self.admittances:
            if n1 is not self.gnd:
                G[n1][n1] += val

            if n2 is not self.gnd:
                G[n2][n2] += val

            if n1 is not self.gnd and n2 is not self.gnd:
                G[n1][n2] -= val
                G[n2][n1] -= val

        for idx, data in enumerate(self.sources_v):
            n1, n2, val = data

            if n1 is not self.gnd:
                B[n1][idx] = 1

            if n2 is not self.gnd:
                B[n2][idx] = -1

            e[idx] = val

        for idx, data in enumerate(self.sources_i):
            n1, n2, val = data

            i[n1] = val

            if n2 is not self.gnd:
                i[n2] = -val

        C = numpy.transpose(B)
        D = numpy.zeros((M, M), dtype=self.dtype)

        A = numpy.concatenate((numpy.concatenate((G, B), axis=1), numpy.concatenate((C, D), axis=1)))
        z = numpy.concatenate((i, e))

        # print(self.node_names)
        # print(self.sources_v)
        # sympy.pprint(A)
        # print(numpy.linalg.inv(A))
        # print(z)

        x = numpy.matmul(numpy.linalg.inv(A), z)[0:N]
        # x = numpy.linalg.solve(A, z)[0:N]
        pairs = sorted(zip(self.node_names, x), key=lambda q: q[0])

        return {k: v[0] for k, v in pairs}
