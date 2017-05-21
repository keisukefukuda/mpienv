#!/bin/bash

set -eu

# Initial state: no MPI is managed.
. $(dirname $0)/../init

mpienv list # Check it finishes normally

test -z "$(mpienv list)"

