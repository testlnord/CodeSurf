__author__ = 'arkady'

from subprocess import call


def gdblog(bin_path, script_path):
    call(["gdb",bin_path, "-x", script_path])
    