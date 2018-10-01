#!/bin/bash

if [ ! -f $PWD/mpienv/__init__.py ]; then
    echo "Must be in mpienv/ root directory" >&2
    exit 1
fi

rm -rf build
rm -rf mpienv.egg-info
rm -rf dist

python setup.py sdist
twine upload dist/*


