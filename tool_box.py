#
# Tools for test scripts
#
import os, sys

def get_dev_id(path):
    st = os.lstat(path)
    return st.st_dev

def system(command):
    ret = os.system(command)
    if ret != 0:
        raise RuntimeError("Command failed: " + command)

def read_file(path):
    fd = open(path, "r")
    data = fd.read()
    del fd
    return data

#
# Check for taint (kernel warnings and oopses)
#
def check_not_tainted():
    taint = read_file("/proc/sys/kernel/tainted")
    if taint != current_taint:
        raise RuntimeError("TAINTED " + current_taint + " -> ", taint)