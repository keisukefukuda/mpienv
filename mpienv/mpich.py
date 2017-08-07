# coding: utf-8
import re
from subprocess import check_output
import sys  # NOQA

from mpienv import mpibase
from mpienv import util


def _parse_mpich_version(mpiexec):
    out = util.decode(check_output([mpiexec, '--version']))

    # Split the --version output into lines.
    lines = out.split("\n")[1:]
    lines = [ln.strip() for ln in lines]
    d = {}
    for ln in lines:
        if len(ln.strip()) == 0:
            continue
        m = re.match(r'^([^:]*):\s*(\S.*)$', ln)
        if m is None:
            print(ln)
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

        info = _parse_mpich_version(mpiexec)
        self._mpich_ver_info = info
        inc_dir, lib_dir = _parse_mpich_mpicc_show(mpicc)

        prefix = info['Configure options']['--prefix']
        inc_dir = inc_dir
        lib_dir = lib_dir
        super(Mpich, self).__init__(prefix, mpiexec, mpicc,
                                    inc_dir, lib_dir, conf, name)

        self._type = "MPICH"

        # TODO(keisukefukuda) find prefix
        # TODO(keisukefukuda) find includedir
        # TODO(keisukefukuda) find libexec_dir
        # TODO(keisukefukuda) find lib_dir

        # Parse 'Configure options' section
        # Config options are like this:
        # '--disable-option-checking' '--prefix=NONE' '--enable-cuda'
        self._conf_params = info['Configure options']
        self._version = info['Version']
        self._default_name = "mpich-{}".format(self._version)

    def bin_files(self):
        return util.glob_list([self.prefix, 'bin'],
                              ['hydra_*',
                               'mpi*',
                               'parkill'])

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

    def exec_(self, cmds):
        if '-genvall' not in cmds:
            cmds[:0] = ['-genvlist', 'PYTHONPATH,PATH,LD_LIBRARY_PATH']
        cmds[:0] = [self.mpiexec]
        self.run_cmd(cmds, {})
