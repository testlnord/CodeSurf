__author__ = 'arkady'


class TrajStep:
    def __init__(self, coord, t=False, v=False, vrs=None, name=None):
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
                real_steps.append(TrajStep(points[p]))
            real_steps.append(TrajStep(points[step.line], v=True, vrs=step.vars, name=step.fun))
        else:
            real_steps.append(TrajStep(points[step.line], t=True, name=step.fun))
        prev = step

    return real_steps

def razdvigator(points, i):
    return [(x+i*1000, y, z+1)for (x,y,z) in points]