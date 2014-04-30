__author__ = 'arkady'

import src.gdbrer
import src.log_parser
import config
from src.graph_alignment import align_graph, get_lines
from src.trajectory import make_trajectory, razdvigator, get_teleports, get_instructions
from src.graph.app import App


def main():
    log = src.gdbrer.gdblog(config.def_bin, config.gdb_script, config.logs_path)
    (graphs, steps) = src.log_parser.parse(log)

    graphs = {name: (align_graph(graphs[name].graph)) for name in graphs}
    for i, name in enumerate(graphs):
        graphs[name] = razdvigator(graphs[name][0], i), graphs[name][1]

    trajectory = make_trajectory(steps, graphs)
    teleports = get_teleports(steps, graphs)
    instructions = get_instructions(steps, graphs)
    #lines = []
    app = App()
    for name in graphs:
        l = get_lines(graphs[name][0], graphs[name][1])
        app.addLines(l, teleports[name], instructions[name])
        #lines.extend(l)

    #drawLines(lines)


    app.setTrajectory(trajectory)
    app.run()


if __name__ == '__main__':
    main()