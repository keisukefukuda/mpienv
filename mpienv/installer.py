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
        'url': 'https://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.7.tar.bz2',
    },
    'openmpi-2.0.3': {
        'type': 'openmpi',
        'ver': '2.0.3',
        'url': 'https://www.open-mpi.org/software/ompi/v2.0/downloads/openmpi-2.0.3.tar.bz2',
    },
    'openmpi-2.1.1': {
        'type': 'openmpi',
        'ver': '2.1.1',
        'url': 'https://www.open-mpi.org/software/ompi/v2.1/downloads/openmpi-2.1.1.tar.bz2',
    },
}


class BaseInstaller(object):
    def __init__(self, manager, mpi, name, config_args):
        self.mpi = mpi
        self.manager = manager
        self.name = name
        self.config_args = config_args

        self.url = _list[mpi]['url']

        # Downloaded file name
        self.local_file = os.path.join(self.manager.cache_dir(),
                                       os.path.basename(self.url))

        # build directory name
        dir_bname = re.sub(r'(\.tar\.(gz|bz2))|(\.tgz)$',
                           '',
                           os.path.basename(self.url))

        self.dir_path = os.path.join(self.manager.build_dir(),
                                     dir_bname)

    def clean(self):
        if os.path.exists(self.dir_path):
            print("Deleting the build directory...")
            shutil.rmtree(self.dir_path)

    def download(self):
        if not os.path.exists(self.local_file):
            with open(self.local_file, 'w') as f:
                check_call(['curl', self.url], stdout=f)

    def configure(self):
        self.download()

        try:
            idx = self.config_args.index('--prefix')
            if idx >= 0:
                sys.stderr.write("Warning: --prefix argument is "
                                 "replaced by mpienv\n")
                # remove --prefix xxxx
                try:
                    del(self.config_args[idx + 1])
                except IndexError:
                    pass
                del(self.config_args[idx])
        except ValueError:
            pass

        self.config_args[:-1] = ['--prefix',
                                 os.path.join(self.manager.mpi_dir(), self.name)]

        if not os.path.exists(self.dir_path):
            check_call(['tar', '-xf', self.local_file],
                        cwd=self.manager.build_dir())

        # run configure scripts
        print("./configure " + str(self.config_args))
        return
        check_call(['./configure', *self.config_args],
                   shell=True, cwd=self.dir_path)

    def build(self):
        # run configure scripts
        check_call(['make'],
                   shell=True, cwd=self.dir_path)

    def install(self):
        check_call(['make', 'install'],
                   shell=True, cwd=self.dir_path)


class OmpiInstaller(BaseInstaller):
    def __init__(self, *args):
        BaseInstaller.__init__(self, *args)


class MpichInstaller(BaseInstaller):
    def __init__(self, *args):
        BaseInstaller.__init__(self, *args)


class MvapichInstaller(BaseInstaller):
    def __init__(self, *args):
        BaseInstaller.__init__(self, *args)


def list_avail():
    for k in _list:
        print(k)


def create_installer(manager, mpi, name, conf_args=[]):

    if mpi not in _list.keys():
        sys.stderr.write("Error: Unknown MPI: '{}'\n".format(mpi))
        exit(-1)

    mpi_type = _list[mpi]['type']
    mpi_ver = _list[mpi]['ver']

    if mpi_type == 'openmpi':
        return OmpiInstaller(manager, mpi, name, conf_args)
    elif mpi_type == 'mvapich':
        return MvapichInstaller(manager, mpi, name, conf_args)
    elif mpi_type == 'mpich':
        return MpichInstaller(manager, mpi, name, conf_args)

    raise RuntimeError("")
