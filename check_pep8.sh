#!/usr/bin/env bash

set -e
set -x

autopep8 --diff -r . --global-config .pep8

flake8 $(find . -name "*.py")
