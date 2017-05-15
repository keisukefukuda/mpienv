# coding: utf-8

import os
import os.path
import re
import sys

import common

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

def use(label):
    # Check label is a valid MPI installation
    if not os.path.exists(os.path.join(vers_dir, label)):
        sys.stderr.write("mpienv: Error: unknown MPI installation: '{}'\n".format(
            label))
        exit(-1)

    dst = os.path.join(root_dir, 'shims')

    # Check if the current `shims` is a symlink.
    # If not, something is broken
    if os.path.exists(dst) and not os.path.islink(dst):
        sys.stderr.write(("mpienv: Error: {} is not a sylink... " + 
                          "Something is broken\n").format(dst))
        exit(-1)

    # Check if `label` is the currently active one,
    # and do nothing if so
    cur_mpi = os.path.realpath(os.path.join(root_dir, 'shims'))
    trg_mpi = os.path.realpath(os.path.join(vers_dir, label))

    if cur_mpi == trg_mpi:
        print("You are already using {}".format(label))
        return True

    if os.path.exists(dst):
        os.remove(dst)

    src = os.path.realpath(os.path.join(vers_dir, label))

    os.symlink(src, dst)

    print("Using {} -> {}".format(label, src))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("mpienv: Error: mpienv use [mpi-name]\n")
        exit(-1)
    else:
        use(sys.argv[1])
