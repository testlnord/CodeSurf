__author__ = 'arkady'
# coding : utf-8
import re

function = re.compile(r'^#\d*\s*(\w*)\s*\(([\w=,\s]*)\)\s*at\s*[\w\.]*:(\d*)$')
var = re.compile(r'^(\w*)\s*=\s*(\w*)$')


class Step:
    def __init__(self, f, l):
        self.fun = f
        self.line = l
        self.vars = {}


class func_graph:
    def __init__(self):
        self.prev = -1
        self.graph = {}
        self.lines = []

    def num(self, line):
        if not line in self.lines:
            self.lines.append(line)
            self.graph[len(self.lines)-1] = []

        return self.lines.index(line)

    def add(self, line):
        line = self.num(line)
        if not self.prev < 0:
            if not line in self.graph[self.prev]:
                self.graph[self.prev].append(line)
        self.prev = line


def parse(log_path):
    log_file = open(log_path)

    func_graphs = {}
    steps = []
    for line in log_file.readlines():
        if not line:
            continue
        func_match = function.match(line)
        if func_match:
            name = func_match.group(1)+func_match.group(2)
            if not name in func_graphs.keys():
                func_graphs[name] = func_graph()

            line_num = int(func_match.group(3))
            func_graphs[name].add(line_num)
            steps.append(Step(name, func_graphs[name].num(line_num)))

        else:
            var_match = var.match(line)
            if var_match:
                steps[-1].vars[var_match.group(1)] = var_match.group(2)

    func_graphs = {name: func_graphs[name] for name in func_graphs if name[0] != '_'}

    #for name in func_graphs:
    #    print name +": " + str( func_graphs[name].graph)

    return func_graphs, steps