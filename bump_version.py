#!/usr/bin/python3

"""
bump_version
"""


import argparse
import pathlib


parser = argparse.ArgumentParser()
parser.add_argument('package', help='Path of folder where __init__.py resides')
parser.add_argument('version', help='New version to use')
args = parser.parse_args()


package = pathlib.Path(args.package)
init_path = package / pathlib.Path('__init__.py')
version = args.version


file_lines = []


with open(str(init_path), 'r') as file:
    for line in file.readlines():
        if '__version__ = ' in line:
            line = "__version__ = '{}'\n".format(version)
        file_lines.append(line)

with open(str(init_path), 'w') as file:
    for line in file_lines:
        file.write(line)
