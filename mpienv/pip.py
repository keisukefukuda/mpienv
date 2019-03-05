# coding: utf-8

import os
import re
from subprocess import check_call
from subprocess import check_output  # NOQA
from subprocess import PIPE
from subprocess import Popen
import sys

import mpienv.util as util

# We support pip 10.x.x, 9.x.x and 1.5
_pip_ver = None


def _get_pip_ver():
    global _pip_ver

    p = Popen(['pip', '--version'], stdout=PIPE)
    out, err = p.communicate()

    m = re.match(r'pip (\S+)', util.decode(out))
    ver = m.group(1)

    m = re.match(r'(\d+)[.](\S+)', ver)
    major_ver = int(m.group(1))

    if major_ver >= 9:
        _pip_ver = str(major_ver)
    elif ver.startswith("1.5"):
        _pip_ver = '1.5'
    else:
        raise RuntimeError("Error: Unsupported pip version")


def install(libname, target_dir, build_dir, env):
    if _pip_ver is None:
        _get_pip_ver()

    # if 'LD_LIBRARY_PATH' not in env:
    #    env['LD_LIBRARY_PATH'] = ""

    cmd = None

    if float(_pip_ver) > 8:  # >= 9
        # 9.x.x
        cmd = ['pip', 'install',
               # '-q',
               '--no-binary', ':all:',
               '-t', target_dir,
               '-b', build_dir,
               # '--no-cache-dir',
               libname]
    else:
        # 1.5.x
        cmd = ['pip', 'install',
               # '-q',
               '-t', target_dir,
               '-b', build_dir,
               libname]

    if os.environ.get("MPIENV_PIP_VERBOSE") is not None:
        cmd[2:3] = ['-v']

    # sys.stderr.write("{}\n".format(' '.join(cmd)))
    check_call(cmd,
               stdout=sys.stderr,
               env=env)
