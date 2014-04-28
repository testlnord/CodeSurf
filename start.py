__author__ = 'arkady'

import src.gdbrer
import src.log_parser
import config


def main():
    log = src.gdbrer.gdblog(config.def_bin, config.gdb_script, config.logs_path)
    (graphs, steps) = src.log_parser.parse(log)
    print graphs



if __name__ == '__main__':
    main()