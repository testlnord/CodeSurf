__author__ = 'arkady'

from subprocess import call
import os.path
import time


def makeLogPath(out_dir):
    return os.path.join(out_dir, str(time.time()))

def gdblog(bin_path, script_path, out_dir):
    log_path = makeLogPath(out_dir)
    out_log = open(log_path, 'w')
    call(["gdb",bin_path, "-q", "-x", script_path], stdout=out_log)
    out_log.close()
    return log_path

