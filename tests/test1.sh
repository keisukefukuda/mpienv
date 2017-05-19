#!/bin/sh

set -eu

# Initial state: no MPI is managed.
source $(dirname $0)/../init

mpienv list
