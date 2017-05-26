# coding:utf-8

import os.path
import platform
import re
import shutil
from subprocess import PIPE
from subprocess import Popen
import sys
import tempfile
import unittest


ProjDir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))


print("Platform: {}".format(platform.platform()))
if re.search(r'linux', platform.platform(), re.I):
    mpi_list = ['mpich-3.2',
                'mvapich2-2.2',
                'openmpi-1.10.7',
                'openmpi-2.1.1']
else:
    mpi_list = ['mpich-3.2',
                'openmpi-1.10.7',
                'openmpi-2.1.1']


def bash_session(cmd):
    ver_dir = tempfile.mkdtemp()

    if os.path.exists(ver_dir):
        os.rmdir
    if type(cmd) == list:
        cmd = " && ".join(cmd)

    p = Popen(["/bin/bash"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    enc = sys.getdefaultencoding()
    cmd = (". {}/init;"
           "export MPIENV_VERSIONS_DIR={};"
           "set -eu; {}\n".format(ProjDir,
                                  ver_dir,
                                  cmd))

    out, err = p.communicate(cmd.encode(enc))
    ret = p.returncode

    shutil.rmtree(ver_dir)

    return out.decode(enc), err.decode(enc), ret


class TestList(unittest.TestCase):
    def test_list_empty(self):
        # It outputs nothing if no MPI is installed yet.
        o, e, r = bash_session("mpienv list")
        self.assertEqual(0, r)
        self.assertEqual("", o)
        self.assertEqual("", e)


class TestAutoDiscover(unittest.TestCase):
    def test_autodiscover(self):
        out, err, ret = bash_session([
            "mpienv autodiscover -v ~/mpi | grep Found | sort"
        ])

        lines = [re.search(r'/mpi/([^/]*)/bin/mpiexec', ln).group(1)
                 for ln in out.split("\n") if len(ln) > 0]

        self.assertEqual(mpi_list, lines)

    def test_autodiscover_add(self):
        out, err, ret = bash_session([
            "mpienv autodiscover -v --add ~/mpi",
            "mpienv list"
        ])
        lines = sorted(ln for ln in out.split("\n") if re.search('^Found', ln))
        lines = [re.search(r'/mpi/([^/]*)/bin/mpiexec', ln).group(1)
                 for ln in lines]
        self.assertEqual(mpi_list, lines)


class TestRename(unittest.TestCase):
    def test_rename(self):
        out, err, ret = bash_session([
            "ls ~/mpi",
            "mpienv autodiscover --add ~/mpi",
            "mpienv rename mpich-3.2 mpich-3.2x",
            "mpienv list"
        ])

        if ret != 0:
            print(err)
        self.assertEqual(0, ret)

        print(out)

        should = [re.sub(r'mpich-3.2', 'mpich-3.2x', m) for m in mpi_list]

        lines = [ln for ln in out.split("\n") if re.search('->', ln)]
        lines = sorted([re.search(r'([^/ ]*)\s+->', ln).group(1)
                        for ln in lines])
        self.assertEqual(should, lines)
