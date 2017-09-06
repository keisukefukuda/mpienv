# coding: utf-8

import argparse
import glob
import os
import os.path
import pprint
import re
import sys

from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv autodiscover',
    description='Find MPI environments already installed in your host.')
parser.add_argument('-a', '--add', dest='add',
                    action="store_true", default=None)
parser.add_argument('-v', '--verbose', dest='verbose',
                    action="store_true", default=None)
parser.add_argument('-q', '--quiet', dest='quiet',
                    action="store_true", default=None)
parser.add_argument('paths', nargs='*')


default_search_paths = [
    "/usr",
    "/usr/local",
    "/opt/local",
    os.path.expanduser("~"),
    os.path.expanduser("~/local"),
]

_verbose = None
_quiet = None


def printv(s):
    if _verbose:
        sys.stderr.write(s + "\n")


def prints(s=""):
    if not _quiet:
        print(s)


def filter_valid_paths(paths, warn=True):
    ret = []
    for p in paths:
        if os.path.isdir(p):
            ret.append(p)
        else:
            if warn:
                sys.stderr.write("Error: '{}' is not a directory\n".format(p))

    return ret


def list_mpiexec(dirpath):
    """List all mpiexec command in `dirpath`

    Some binaries may be symlinks pointing the same binary.
    ex.) In /usr
      mpiexec -> orterun
      mpiexsec.openmpi -> orterun
      mpiexec.hydra
      mpiexec.mpich -> mpiexec.hydra

    The most appropriate one is selected and duplicates are eliminted.
    In the exmaple, 'mpiexec' is selected.
    The rule:
      * if the filename is 'mpiexec', then it's selected.
      * If a file "the_file.replace('mpiexec', 'mpicc')" exists,
        then the_file is selected.
      * If a filename matches r'mpiexec.*mpi*', it is chosen.
      * Otherwise, one is randomly chosen
    """

    lst = glob.glob(os.path.join(dirpath, 'bin', '*mpiexec*'))
    link_rel = {}

    # As an exception, we need to exclude binaries like
    # 'mpiexec.mpirun_rsh' in a rule-based filter. This is because
    # these command does not accept --version arguments.
    lst = [x for x in lst if re.search(r'mpiexec.mpirun_rsh', x) is None]

    # mx: mpiexec
    for mx in lst:
        link_dst = os.path.realpath(mx)
        if link_dst in link_rel:
            link_rel[link_dst].append(mx)
        else:
            link_rel[link_dst] = [mx]

    res = []  # Result
    for orig in link_rel.keys():
        # for each original mpiexec binary, select the most appropriate symlink
        # (include the file itself) by the selection rule described above
        cands = link_rel[orig]
        cand_1 = [x for x in cands
                  if os.path.basename(x) == "mpiexec"]
        cand_2 = [x for x in cands
                  if os.path.exists(x.replace('mpiexec', 'mpicc'))]
        cand_3 = [x for x in cands
                  if re.match(r'^mpiexec\.\S*mpi\S*$',
                              os.path.basename(x), re.I)]

        for cand in [cand_1, cand_2, cand_3]:
            if len(cand) > 0:
                res.append(cand[0])
                break
        else:
            res.append(cands[0])

    return res


def investigate_path(path, flg_to_add, done={}):
    for mpiexec in list_mpiexec(path):
        if mpiexec in done:
            continue
        else:
            done.add(mpiexec)

        if os.path.isfile(mpiexec):
            printv("checking {}".format(mpiexec))

            # Exclude mpienv's own directory
            name = mpienv.is_installed(path)
            if name:
                prints("{}\n\t Already known as "
                       "'{}'".format(path, name))
                prints()
            else:
                prints("--------------------------------------")
                prints("Found {}".format(mpiexec))
                prints(pprint.pformat(mpienv.get_mpi_from_mpiexec(mpiexec)))
                # Install the new MPI
                if flg_to_add:
                    try:
                        name = mpienv.add(mpiexec)
                        prints("Added {} as {}".format(path, name))
                    except RuntimeError as e:
                        prints("Error occured while "
                               "adding {}".format(path))
                        prints(e)
                        prints()
        else:
            printv("No such file '{}'".format(mpiexec))

    return done


def main():
    global _verbose
    global _quiet

    args = parser.parse_args()

    search_paths = args.paths
    to_add = args.add
    _verbose = args.verbose
    _quiet = args.quiet

    if _verbose and _quiet:
        sys.stderr.write("Error: -q and -v cannot "
                         "specified at the same time.\n")
        exit(-1)

    if len(search_paths) == 0:
        search_paths = default_search_paths
        using_default = True
    else:
        using_default = False

    search_paths = filter_valid_paths(search_paths,
                                      warn=(not using_default))

    done = set()

    for path in search_paths:
        for (dirpath, dirs, files) in os.walk(path):
            # print("done = {}".format(done))
            done = investigate_path(dirpath, to_add, done)


if __name__ == "__main__":
    main()
