# coding:utf-8

import os.path
import unittest
from subprocess import Popen, PIPE
import sys
import re
import tempfile
import shutil
import platform


ProjDir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))


if re.search(r'linux', platform.platform(), re.I):
    mpi_list = ['/mpi/mpich-3.2/bin/mpiexec',
                '/mpi/mvapich2-2.2/bin/mpiexec',
                '/mpi/openmpi-1.10.7/bin/mpiexec',
                '/mpi/openmpi-2.1.1/bin/mpiexec']
else:
    mpi_list = ['/mpi/mpich-3.2/bin/mpiexec',
                '/mpi/openmpi-1.10.7/bin/mpiexec',
                '/mpi/openmpi-2.1.1/bin/mpiexec']


def bash_session(cmd):
    ver_dir = tempfile.mkdtemp()

    if os.path.exists(ver_dir):
        os.rmdir
    if type(cmd) == list:
        cmd = ";".join(cmd)

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

    return out.decode(enc), err.decode(enc), p.returncode


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

        sys.stderr.write(err)
        
        lines = [re.search(r'(/mpi/.*)$', ln).group(1)
                 for ln in out.split("\n") if len(ln) > 0]

        self.assertEqual(mpi_list, lines)

    def test_autodiscover_add(self):
        out, err, ret = bash_session([
            "mpienv autodiscover -v --add ~/mpi",
            "mpienv list"
        ])

        sys.stderr.write(err)

        lines = sorted(ln for ln in out.split("\n") if re.search('^Found', ln))
        lines = [re.search(r'(/mpi/.*)$', ln).group(0) for ln in lines]
        self.assertEqual(mpi_list, lines)
