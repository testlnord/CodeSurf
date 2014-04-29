__author__ = 'arkady'


class Teleport:
    def __init__(self, f, t, p, n):
        self.from_fun = f
        self.to_fun = t
        self.pos = p
        self.orient = n


def get_teleports(steps, graphs):
    teleports = {}
    prev = None
    for step in steps:
        if prev is None:
            prev = step
            continue
        if prev.fun != step.fun:
            if prev.fun not in teleports.keys():
                teleports[prev.fun] = []
            teleports[prev.fun].append(Teleport(prev.fun,
                                                step.fun,
                                                graphs[prev.fun][0][prev.line],
                                                graphs[prev.fun][0][prev.line+1])
            )
        prev = step
    return teleports

class TrajStep:
    def __init__(self, coord, name,t=False, v=False, vrs=None):
        self.coord = coord
        self.t = t
        self.v = v
        self.vrs = vrs
        self.name = name


def make_trajectory(steps, graphs):
    real_steps = []
    prev = None
    for step in steps:
        if prev is None:
            prev = step
            continue
        points = graphs[step.fun][0]
        edges = graphs[step.fun][1]
        if prev.fun == step.fun:
            for p in edges[(prev.line, step.line)]:
                real_steps.append(TrajStep(points[p], step.fun))
            real_steps.append(TrajStep(points[step.line],step.fun, v=True, vrs=step.vars))
        else:
            real_steps.append(TrajStep(points[step.line], step.fun, t=True))

        prev = step

    return real_steps

def razdvigator(points, i):
    return [(x+i*1000, y, z+1)for (x,y,z) in points]