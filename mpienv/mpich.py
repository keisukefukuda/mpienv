# coding: utf-8
import os
import re
from subprocess import check_output
from subprocess import PIPE
from subprocess import Popen
import sys  # NOQA

import mpienv.mpibase as mpibase
import mpienv.util as util

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def find_mpi_h(mpiexec, ver_str=None):
    """Find mpi.h file from MPICH mpiexec binary"""
    if ver_str is None:
        p = Popen([mpiexec, '--version'], stderr=PIPE, stdout=PIPE)
        out, err = p.communicate()
        ver_str = util.decode(out + err)

    # Search prefix from configure options
    line = next(ln for ln in ver_str.split("\n")
                if re.search(r'Configure options', ln))
    dir_cands = re.findall(r'--includedir=([^\' \n]+)', line)
    inc_paths = re.findall(r'--includedir=([^\' \n]+)', line)
    prefixes = [d for d in re.findall(r'--prefix=([^\' \n]+)', line)
                if os.path.isdir(d)]

    # Search prefix from the binary's path
    m = re.match(r'^(.*)/bin/[^/]+$', mpiexec)
    if m is not None:
        incdir = m.group(1)
        if os.path.isdir(incdir):
            prefixes += [incdir]

    dir_cands = set(inc_paths + [os.path.join(d, 'include') for d in prefixes])
    try:
        inc_dir = next(p for p in dir_cands
                       if os.path.exists(os.path.join(p, 'mpi.h')))
    except StopIteration:
        raise FileNotFoundError(
            "mpi.h not found in {}".format(",".join(dir_cands)))

    return os.path.join(inc_dir, 'mpi.h')


def find_prefix(mpiexec, info=None):
    if info is None:
        info = _parse_mpich_version(mpiexec)

    prefix = info['Configure options']['--prefix']
    if not os.path.isdir(prefix):
        m = re.match(r'^(.*)/bin/mpiexec.*$', mpiexec)
        assert m is not None
        prefix = m.group(1)
    return prefix


def _parse_mpich_version(mpiexec):
    out = util.decode(check_output([mpiexec, '--version']))

    # Split the --version output into lines.
    lines = out.split("\n")[1:]
    lines = [ln.strip() for ln in lines]
    d = {}
    for ln in lines:
        if len(ln.strip()) == 0:
            continue
        m = re.match(r'^([^:]*):\s*(\S.*)?$', ln)
        if m is None:
            print("Internal warning: m is None!!! ln='{}'".format(ln))
        else:
            d[m.group(1)] = m.group(2)

    conf = re.findall(r'\'[^\']+\'', d['Configure options'])
    conf = [re.sub(r'\'$', '', re.sub(r'^\'', '', c)) for c in conf]
    d['Configure options'] = {}
    for c in conf:
        m = c.split('=')
        if len(m) == 1:
            m[1:] = [True]
        d['Configure options'][m[0]] = m[1]
    return d


def _parse_mpich_mpicc_show(mpicc):
    """Obtain inc_dir and lib_dir by parsing `mpicc -show` of MPICH"""
    out = util.decode(check_output([mpicc, '-show']))
    # returns inc_dir, lib_dir
    m = re.search(r'-I(\S+)', out)
    inc_dir = m.group(1)

    m = re.search(r'-L(\S+)', out)
    lib_dir = m.group(1)

    return inc_dir, lib_dir


class Mpich(mpibase.MpiBase):
    def __init__(self, mpiexec, conf, name=None):
        # `mpiexec` might be 'mpiexec' or 'mpiexec.mpich' etc.
        mpiexec = mpiexec
        mpicc = re.sub('mpiexec', 'mpicc', mpiexec)

        if not os.path.exists(mpicc):
            sys.stderr.write("mpicc does not exist: {}".format(mpicc))

        info = _parse_mpich_version(mpiexec)
        self._mpich_ver_info = info
        inc_dir, lib_dir = _parse_mpich_mpicc_show(mpicc)

        prefix = find_prefix(mpiexec, info)
        inc_dir = inc_dir
        lib_dir = lib_dir
        super(Mpich, self).__init__(prefix, mpiexec, mpicc,
                                    inc_dir, lib_dir, conf, name)

        self._type = "MPICH"

        # Parse 'Configure options' section
        # Config options are like this:
        # '--disable-option-checking' '--prefix=NONE' '--enable-cuda'
        self._conf_params = info['Configure options']
        self._version = info['Version']
        self._default_name = "mpich-{}".format(self._version)

    def bin_files(self):
        # MPICH-specific files, which would not conflict with
        # other MPI implementations.
        mpich_files = util.glob_list([self.prefix, 'bin'],
                                     ['hydra_*',
                                      'parkill'])
        return mpich_files

    def lib_files(self):
        return util.glob_list([self.prefix, 'lib'],
                              ['lib*mpi*.*',
                               'lib*mpl*.*',
                               'libopa.*'])

    def inc_files(self):
        return util.glob_list([self.prefix, 'include'],
                              ['mpi*.h',
                               'mpi*.mod',
                               'opa*.h',
                               'primitives'])

    def libexec_files(self):
        return []
