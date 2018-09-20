from setuptools import setup

setup(
    name="mpienv",
    version="0.1.0",
    description="MPI environment switcher",
    author="Keisuke Fukuda",
    author_email="keisukefukuda@gmail.com",
    url="https://github.com/keisukefukuda/mpienv",
    scripts=['bin/mpienv-init'],
    packages=['mpienv'],
)
