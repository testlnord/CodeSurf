import numpy as np
import numpy.linalg as linalg
import numpy.random

class GraphAlignment:
    cRep = 200
    cAttr = 0.06
    delta = 0.85
    addOnEdges = 0
    threshold = 0.05
    maxIterations = 1000

    def build_graph(self, graph):
        n = len(graph)
        edges = {}
        adj = []
        for i in range(n):
            adj.append(set())

        for tu in range(len(graph)):
            for tv in graph[tu]:
                u, v = tu, tv
                if u > v:
                    u, v = v, u
                if (u, v) in edges:
                    continue

                edges[(u, v)] = []
                last = u
                for t in range(self.addOnEdges):
                    cur = n
                    n += 1
                    edges[(u, v)].append(cur)
                    adj[last].add(cur)
                    adj.append({last})
                    last = cur
                adj[last].add(v)
                adj[v].add(last)
        return adj, edges

    def __init__(self, graph):
        self.adj, self.edges = self.build_graph(graph)

        self.n = len(self.adj)
        self.points = np.zeros((self.n, 3))

        for i in range(self.n):
            self.points[i] = numpy.random.random(3)  # vector of 3 random values

    def get_direction(self, u, v):
        vec = self.points[v] - self.points[u]
        dist = linalg.norm(vec)
        unit = vec / dist

        return dist, unit

    def f_rep(self, u, v):
        dist, unit = self.get_direction(v, u)
        return self.cRep * unit / dist

    def f_attr(self, u, v):
        dist, unit = self.get_direction(u, v)
        res = self.cAttr * dist * unit
        return res

    def align(self):
        f = np.zeros((self.n, 3))
        old = self.points.copy()

        for i in range(self.maxIterations):
            for u in range(self.n):
                #f[u] = np.zeros(3) #seems to be faster without this

                for v in range(self.n):
                    if u != v:
                        f[u] += self.f_rep(u, v)
                        if v in self.adj[u]:
                            f[u] += self.f_attr(u, v)

            for u in range(self.n):
                f[u] *= self.delta
                self.points[u] += f[u]

            if abs(old - self.points).max() < self.threshold:
                print "stop at: %d (%s)" % (i, abs(old - self.points).max())
                break

            old = self.points.copy()

        return self.points, self.edges

    @staticmethod
    def normalize_points(points):
        q = max(abs(points.max()), abs(points.min()))
        points /= 0.1*q
        return points


def align_graph(graph):
    al = GraphAlignment(graph)
    points, edges = al.align()
    points = GraphAlignment.normalize_points(points)
    return points, edges


def get_lines(points, edges):
    lines = []
    for v, u in edges:
        lines.append((points[v], points[u]))
    return lines

if __name__ == '__main__':
    graph = [[1, 4], [2, 3], [0], [0], [5], []]
    points, edges = align_graph(graph)

    #from src.graph.graph import drawLines
    #drawLines(get_lines(points, edges))