#!/bin/sh

set -eu

# Initial state: no MPI is managed.
. $(dirname $0)/../init

mpienv list
