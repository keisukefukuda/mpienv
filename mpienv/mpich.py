# coding: utf-8
import re
from subprocess import check_output

from mpienv import mpibase
from mpienv import util


class Mpich(mpibase.MpiBase):
    def __init__(self, *args):
        super(Mpich, self).__init__(*args)

        out = util.decode(check_output([self.mpiexec, '--version']))

        self._type = "MPICH"

        # Parse 'Configure options' section
        # Config options are like this:
        # '--disable-option-checking' '--prefix=NONE' '--enable-cuda'
        m = re.search(r'Configure options:\s+(.*)$', out, re.MULTILINE)
        conf_str = m.group(1)
        self._conf_params = [s.replace("'", '') for s
                             in re.findall(r'\'[^\']+\'', conf_str)]

        m = re.search(r'Version:\s+(\S+)', out, re.MULTILINE)
        self._version = m.group(1)
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
        # TODO(keisukefukuda): if cmds include '-genvall',
        #                      no need to specify '-genvlist'
        cmds[:0] = ['-genvlist', 'PYTHONPATH,PATH,LD_LIBRARY_PATH']
        cmds[:0] = [self.mpiexec]
        self.run_cmd(cmds, {})
