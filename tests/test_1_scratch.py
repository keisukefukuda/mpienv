# coding:utf-8

import os.path
import unittest
from subprocess import Popen, PIPE
import sys


ProjDir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))


def bash_session(cmd):
    p = Popen(["/bin/bash"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    enc = sys.getdefaultencoding()
    cmd = ". {}/init; {};\n".format(ProjDir, cmd)

    out, err = p.communicate(cmd.encode(enc))
    return out.decode(enc), err.decode(enc), p.returncode


class TestList(unittest.TestCase):
    def test_list_empty(self):
        # It outputs nothing if no MPI is installed yet.
        o, e, r = bash_session("mpienv list")
        self.assertEqual(0, r)
        self.assertEqual("", o)
        self.assertEqual("", e)

