import numpy as np
import numpy.linalg as linalg
import numpy.random

pointsDist = 0.2


class GraphAlignment:
    cRep = 200
    cAttr = 0.06
    delta = 0.85
    addOnEdges = 2
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
                #if u > v:
                #    u, v = v, u
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
                edges[(u, v)].append(v)
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
        dist2 = vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]
        #dist2 = vec.dot(vec)

        return dist2, vec

    def f_rep(self, u, v):
        dist2, vec = self.get_direction(v, u)
        return self.cRep * vec / dist2

    def f_attr(self, u, v):
        dist2, vec = self.get_direction(u, v)
        res = self.cAttr * vec
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

    pts = []
    for i in xrange(len(points)):
        pts.append(points[i])

    edges = interpolate(pts, edges)

    print "got points %s" % len(pts)
    return pts, edges


def interpolateBetweenPoints(bp, ep):
    dist = linalg.norm(ep - bp)
    pointsCnt = int(np.floor(dist / pointsDist))

    res = np.zeros((pointsCnt, 3))
    t = bp.copy()
    step = (ep-bp) / pointsCnt
    for i in range(pointsCnt):
        t += step
        res[i] = t

    return res


def interpolate(points, edges):
    newEdges = {}
    for (u, v), li in edges.iteritems():
        nli = []
        last = u
        for t in li:
            newPoints = interpolateBetweenPoints(points[last], points[t])
            n = len(points)
            points.extend(newPoints)
            nli.extend(range(n, n+len(newPoints)))
            nli.append(t)
            last = t
        newEdges[(u, v)] = nli

    return newEdges

def get_lines(points, edges):
    lines = []
    for (u, v), li in edges.iteritems():
        last = u
        for t in li:
            lines.append((points[last], points[t]))
            last = t
    return lines

if __name__ == '__main__':
    graph = [[1, 4], [2, 3], [0], [0], [5], []]
    points, edges = align_graph(graph)

    #from src.graph.graph import drawLines
    #drawLines(get_lines(points, edges))