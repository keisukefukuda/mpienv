# coding: utf-8

from __future__ import print_function
import os
import platform
from subprocess import check_output
import sys

try:
    from mpi4py import MPI
    _mpi4py_available = True
except ImportError:
    _mpi4py_available = False
    

from common import manager


def _find_mpi4py_lib(path):
    lines = []
    if os.path.isdir(path):
        out = check_output(['find', path,
                            '-type', 'f',
                            '-name', '*MPI*.so'])
        lines = [ln.strip() for ln in out.split("\n")
                 if len(ln.strip()) > 0]

    return lines


def _call_otool(lib):
    out = check_output(['otool', '-L', lib])
    sys.stderr.write(out)


def _find_linked_mpi_lib(lib):
    plt = platform.platform()
    if plt.find('Darwin') >= 0:
        # Mac OS. We use 'otool -L' to find linked libraries
        _call_otool(lib)
    elif plt.find('Linux') >= 0:
        # Linux
        pass
    else:
        sys.stderr.write("The platform is not Linux nor MacOS. Unsupported.\n")
        exit(-1)
            

def main():
    if not _mpi4py_available:
        sys.stderr.write("Error: mpi4py is not installed.\n")
        exit(-1)

    libs = set()

    for p in sys.path:
        for lib in _find_mpi4py_lib(p):
            libs.add(lib)

    if len(libs) == 0:
        sys.stderr.write("Erorr: MPI.so is not "
                         "found in your Python path.")
        exit(-1)

    if len(libs) > 1:
        sys.stderr.write("Erorr: multiple MPI.so are "
                         "found in your Python path.")
        exit(-1)

    lib = libs.pop()
    sys.stderr.write("{}\n".format(lib))
    _find_linked_mpi_lib(lib)
        

if __name__ == "__main__":
    main()
