# coding: utf-8

import argparse

from common import manager


def main():
    parser = argparse.ArgumentParser(description="mpienv-add")
    parser.add_argument('name_from', type=str)
    parser.add_argument('name_to', type=str)

    args = parser.parse_args()

    manager.rename(args.name_from, args.name_to)


if __name__ == "__main__":
    main()
