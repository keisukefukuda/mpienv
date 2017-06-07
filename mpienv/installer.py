# coding: utf-8

import os
import os.path
import re
import shutil
from subprocess import check_call
import sys

_list = {
    'openmpi-1.10.7': {
        'type': 'openmpi',
        'ver': '1.10.7',
        'url': ('https://www.open-mpi.org/software/ompi/'
                'v1.10/downloads/openmpi-1.10.7.tar.bz2'),
    },
    'openmpi-2.0.3': {
        'type': 'openmpi',
        'ver': '2.0.3',
        'url': ('https://www.open-mpi.org/software/ompi/'
                'v2.0/downloads/openmpi-2.0.3.tar.bz2'),
    },
    'openmpi-2.1.1': {
        'type': 'openmpi',
        'ver': '2.1.1',
        'url': ('https://www.open-mpi.org/software/ompi/'
                'v2.1/downloads/openmpi-2.1.1.tar.bz2'),
    },
}


class BaseInstaller(object):
    def __init__(self, manager, mpi, name, verbose=False):
        self.mpi = mpi
        self.manager = manager
        self.name = name

        self.url = _list[mpi]['url']

        # Downloaded file name
        self.local_file = os.path.join(self.manager.cache_dir(),
                                       os.path.basename(self.url))

        # build directory name
        dir_bname = re.sub(r'(\.tar\.(gz|bz2))|(\.tgz)$',
                           '',
                           os.path.basename(self.url))

        self.ext_path = os.path.join(self.manager.build_dir(),
                                     name)
        self.dir_path = os.path.join(self.ext_path,
                                     dir_bname)

        self.prefix = os.path.join(manager.mpi_dir(), name)

        if not os.path.exists(self.ext_path):
            os.makedirs(self.ext_path)

    def clean(self):
        if os.path.exists(self.dir_path):
            print("Deleting the build directory...")
            shutil.rmtree(self.dir_path)

    def download(self):
        if not os.path.exists(self.local_file):
            with open(self.local_file, 'w') as f:
                check_call(['curl', self.url], stdout=f)

    def configure(self, conf_args):
        self.download()

        # Extract the archive files
        if not os.path.exists(self.dir_path):
            check_call(['tar', '-xf', self.local_file],
                       cwd=self.ext_path)

        # fix the configure argument
        try:
            idx = conf_args.index('--prefix')
            if idx >= 0:
                sys.stderr.write("Warning: --prefix argument is "
                                 "replaced by mpienv\n")
                # remove --prefix xxxx
                try:
                    conf_args[idx:idx + 2] = []
                except IndexError:
                    pass
        except ValueError:
            # If --prefix is not found
            pass

        # Check args = --help, or insert our --prefix argument
        try:
            idx = conf_args.index('--help')
            if idx >= 0:
                conf_args = ['--help']
        except ValueError:
            # if --help is not found
            conf_args[:-1] = ['--prefix', self.prefix]

        print(' '.join(['./configure', *conf_args]))

        # run configure scripts
        assert(os.path.exists(self.dir_path))
        check_call(['./configure', *conf_args],
                   cwd=self.dir_path)

    def build(self, npar=1):
        config_log = os.path.join(self.dir_path, 'config.log')
        if not os.path.exists(config_log):
            self.configure([])

        # run configure scripts
        check_call(['make', '-j', str(npar)],
                   shell=True, cwd=self.dir_path)

    def install(self, npar=1):
        config_log = os.path.join(self.dir_path, 'config.log')
        if not os.path.exists(config_log):
            self.configure([])

        check_call(['make', 'install', '-j', str(npar)],
                   cwd=self.dir_path)


class OmpiInstaller(BaseInstaller):
    def __init__(self, *args, verbose=False):
        BaseInstaller.__init__(self, *args, verbose=verbose)


class MpichInstaller(BaseInstaller):
    def __init__(self, *args, verbose=False):
        BaseInstaller.__init__(self, *args, verbose=verbose)


class MvapichInstaller(BaseInstaller):
    def __init__(self, *args, verbose=False):
        BaseInstaller.__init__(self, *args, verbose=verbose)


def list_avail():
    for k in _list:
        print(k)


def create_installer(manager, mpi, name, verbose):

    if mpi not in _list.keys():
        sys.stderr.write("Error: Unknown MPI: '{}'\n".format(mpi))
        exit(-1)

    mpi_type = _list[mpi]['type']

    if mpi_type == 'openmpi':
        return OmpiInstaller(manager, mpi, name,
                             verbose=verbose)
    elif mpi_type == 'mvapich':
        return MvapichInstaller(manager, mpi, name,
                                verbose=verbose)
    elif mpi_type == 'mpich':
        return MpichInstaller(manager, mpi, name,
                              verbose=verbose)

    raise RuntimeError("")
