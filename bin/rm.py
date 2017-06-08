# coding: utf-8

import argparse

from common import manager


def main():
    parser = argparse.ArgumentParser(description="mpienv-add")
    parser.add_argument('targets', type=str, nargs='+')
    parser.add_argument('-i', action="store_true", default=False)

    args = parser.parse_args()

    # Remove a link
    for trg in args.targets:
        manager.rm(trg, prompt=args.i)


if __name__ == "__main__":
    main()
