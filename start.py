__author__ = 'arkady'

import src.gdbrer
import src.log_parser
import config
from src.graph_alignment import align_graph, get_lines
from src.graph.graph import drawLines

def main():
    log = src.gdbrer.gdblog(config.def_bin, config.gdb_script, config.logs_path)
    (graphs, steps) = src.log_parser.parse(log)
    lines = []
    for name in graphs:
        points, edges = align_graph(graphs[name].graph)
        l = get_lines(points, edges)
        lines.extend(l)

    drawLines(lines)


if __name__ == '__main__':
    main()