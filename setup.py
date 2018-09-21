from setuptools import find_packages
from setuptools import setup

setup(
    name="mpienv",
    version="0.1.1",
    description="MPI environment switcher",
    author="Keisuke Fukuda",
    author_email="keisukefukuda@gmail.com",
    url="https://github.com/keisukefukuda/mpienv",
    scripts=['bin/mpienv-init'],
    packages=find_packages(),
)
