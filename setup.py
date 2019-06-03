import re
from setuptools import find_packages
from setuptools import setup
import sys

for line in [ln for ln in open("mpienv/__init__.py").readlines() \
             if re.search(r'VERSION', ln)]:
    exec(line)

if sys.version_info[0] == 2:
    dep = ['pip', 'configparser']
else:
    dep = ['pip']

setup(
    name="mpienv",
    version=__version__,
    description="MPI environment switcher",
    author="Keisuke Fukuda",
    author_email="keisukefukuda@gmail.com",
    url="https://github.com/keisukefukuda/mpienv",
    packages=find_packages(),
    install_requires=dep,
    entry_points={
        'console_scripts': ['mpienv-init=mpienv.mpienv_init:main'],
    }
)
