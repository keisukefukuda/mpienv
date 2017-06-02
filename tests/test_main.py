# -*- coding:utf-8 -*-

import json
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
                'openmpi-2.1.1']
else:
    mpi_list = ['mpich-3.2',
                'openmpi-2.1.1']

mpi_vers = {
    'mpich-3.2': '3.2',
    'mvapich2-2.2': '2.2',
    'openmpi-2.1.1': '2.1.1',
}


def sh_session(cmd):
    shell_cmd = os.environ.get('TEST_SHELL_CMD', None) or "bash"
    ver_dir = tempfile.mkdtemp()

    try:
        if os.path.exists(ver_dir):
            os.rmdir
        if type(cmd) == list:
            cmd = " && ".join(cmd)

        p = Popen([shell_cmd], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        enc = sys.getdefaultencoding()
        cmd = (". {}/init;"
               "export MPIENV_VERSIONS_DIR={};"
               "set -eu; {}\n".format(ProjDir,
                                      ver_dir,
                                      cmd))

        out, err = p.communicate(cmd.encode(enc))
        ret = p.returncode

        if ret != 0:
            print("sh_session(): return code != 0")
            print("----------------------------------")
            print("sh_session(): out=")
            print(out.decode(sys.getdefaultencoding()))
            print("----------------------------------")
            print("sh_session(): err=")
            print(err.decode(sys.getdefaultencoding()))
            print("----------------------------------")
    finally:
        shutil.rmtree(ver_dir)

    return out.decode(enc), err.decode(enc), ret


class TestList(unittest.TestCase):
    def test_list_empty(self):
        # It outputs nothing if no MPI is installed yet.
        o, e, r = sh_session("mpienv list")
        self.assertEqual(0, r)
        self.assertEqual("", o)
        self.assertEqual("", e)


class TestAutoDiscover(unittest.TestCase):
    def setUp(self):
        if os.environ.get("TRAVIS", None):
            self.tmpdir = tempfile.mkdtemp(dir=os.path.expanduser("~"))
        else:
            self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_autodiscover(self):
        out, err, ret = sh_session([
            "mpienv autodiscover -v ~/mpi | grep Found | sort"
        ])

        lines = [re.search(r'/mpi/([^/]*)/bin/mpiexec', ln).group(1)
                 for ln in out.split("\n") if len(ln) > 0]

        self.assertEqual(mpi_list, lines)

    def test_autodiscover_add(self):
        out, err, ret = sh_session([
            "mpienv autodiscover -v --add ~/mpi",
            "mpienv list"
        ])
        lines = sorted(ln for ln in out.split("\n") if re.search('^Found', ln))
        lines = [re.search(r'/mpi/([^/]*)/bin/mpiexec', ln).group(1)
                 for ln in lines]
        self.assertEqual(mpi_list, lines)

    def test_list(self):
        out, err, ret = sh_session([
            "mpienv autodiscover -q --add ~/mpi",
            "mpienv list --json"
        ])
        self.assertEqual(0, ret)

        data = json.loads(out)
        self.assertEqual(mpi_list, sorted(data.keys()))

    def test_info(self):
        for mpi in mpi_list:
            out, err, ret = sh_session([
                "mpienv autodiscover -q --add ~/mpi",
                "mpienv info {} --json".format(mpi)
            ])
            self.assertEqual(0, ret)

            data = json.loads(out)
            self.assertEqual(mpi, data['name'])
            self.assertEqual(mpi_vers[mpi], data['version'])

    def test_list_broken(self):
        out, err, ret = sh_session([
            "mpienv autodiscover -q --add ~/mpi",
            "mv ~/mpi/mpich-3.2 {}/".format(self.tmpdir),
            "mpienv list --json"
        ])

        try:
            self.assertEqual(0, ret)
            data = json.loads(out)
            self.assertTrue(data['mpich-3.2']['broken'])
        finally:
            out, err, ret = sh_session([
                "mv {}/mpich-3.2 ~/mpi/".format(self.tmpdir),
            ])


class TestRename(unittest.TestCase):
    def test_rename(self):
        out, err, ret = sh_session([
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


class TestUseMPI4Py(unittest.TestCase):
    def test_mpi4py(self):
        prog = ("from mpi4py import MPI;"
                "import sys;"
                "sys.stdout.write(str(MPI.COMM_WORLD.Get_rank()));")

        # Eliminate mvapich test
        # Because the sample mvapich is not configured '--with-cuda'
        # and causes error on CUDA-equpped environment.
        mpis = ['mpich-3.2']
        # mpis = ['mpich-3.2', 'openmpi-2.1.1']
        # mpis = [mpi for mpi in mpi_list if mpi.find("mvapich") == -1]

        cmds = ["mpienv use --python {}; "
                "mpiexec -n 2 python -c '{}'".format(mpi, prog)
                for mpi in mpis]

        out, err, ret = sh_session([
            "export TMPDIR=/tmp",  # Avoid Open MPI error
            "mpienv autodiscover --add ~/mpi >/dev/null"
        ] + cmds)

        self.assertEqual(0, ret)
        self.assertIsNotNone(re.match(r'^(01|10){1}$', out.strip()))
