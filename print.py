#!/usr/bin/env python

import argparse

import omf80


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path of the omf file")
    args = parser.parse_args()

    filename = args.filename

    file = open(filename, "rb")

    data = file.read()

    records = omf80.read_omf80(data)

    for record in records:
        print(omf80.record_to_string(record))

if __name__ == "__main__":
    main()
