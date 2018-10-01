#!/bin/bash

if [ ! -f $PWD/mpienv/__init__.py ]; then
    echo "Must be in mpienv/ root directory" >&2
    exit 1
fi

rm -rf build
rm -rf mpienv.egg-info

python setup.py bdist_wheel
twine upload dist/*


