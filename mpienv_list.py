# coding: utf-8

from common import manager

if __name__ == '__main__':
    if len(manager.keys()) == 0:
        exit(0)

    max_label_len = max(len(name) for name in manager.keys())

    print("\nInstalled MPIs:\n")
    lst = [info for name, info in manager.items()]
    lst.sort(key=lambda x: x['name'])
    for info in lst:
        print(" {} {:<{width}} -> {}".format(
            "*" if info['active'] else " ",
            info['name'],
            info['path'],
            width=max_label_len))

    print()
