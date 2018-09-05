from setuptools import setup

setup(
    name="mpienv",
    version="0.1",
    scripts=['bin/mpienv-init',
             'bin/mpienv-add.py',
             'bin/mpienv-autodiscover.py',
             'bin/mpienv-build.py',
             'bin/mpienv-configure.py',
             'bin/mpienv-exec.py',
             'bin/mpienv-help.py',
             'bin/mpienv-info.py',
             'bin/mpienv-install.py',
             'bin/mpienv-list.py',
             'bin/mpienv-prefix.py',
             'bin/mpienv-rename.py',
             'bin/mpienv-rm.py',
             'bin/mpienv-use.py'],
    packages=['mpienv'],
)
