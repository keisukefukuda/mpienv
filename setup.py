from setuptools import find_packages
from setuptools import setup

from mpienv import __version__


setup(
    name="mpienv",
    version=__version__,
    description="MPI environment switcher",
    author="Keisuke Fukuda",
    author_email="keisukefukuda@gmail.com",
    url="https://github.com/keisukefukuda/mpienv",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['mpienv-init=mpienv.mpienv_init:main'],
    }
)
