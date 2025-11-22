#!/usr/bin/env python

import sys

import argparse
import pprint

import omf80

def read_int(str):
    if str is None:
        return 0
    if str[-1].lower() == 'h':
        return int(str[0:-1], 16)
    elif len(str) > 1 and str[0:2] == '0x':
        return int(str[2:], 16)
    else:
        return int(str, 10)

class HexIntPrettyPrinter(pprint.PrettyPrinter):
    """A PrettyPrinter that formats integers as hex values."""
    def format(self, obj, ctx, maxlvl, level):
        if isinstance(obj, int):
            # Format integer as hex string with '0x' prefix
            return hex(obj), True, False
        # For all other types, use the default formatting
        return pprint.PrettyPrinter.format(self, obj, ctx, maxlvl, level)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='*')
    parser.add_argument("-o", "--out", help="name of the binary output file")
    parser.add_argument("--code", help="start of the code segment")
    parser.add_argument("--stack", help="size of the stack segment")

    args = parser.parse_args()

    files = args.files
    file_out = args.out
    code_start = read_int(args.code)
    stack_size = read_int(args.stack)

    pprinter = HexIntPrettyPrinter()

    lst = []
    for file in files:
        f = open(file, "rb")
        data = f.read()
        f.close()
        records = omf80.read_omf80(data)
        assert records[-1]['rec_typ'] == omf80.END_OF_FILE_RECORD
        lst.append(omf80.read_records(records[:-1]))
    module = omf80.link(lst)
#    pprinter.pprint(module)

    omf80.module_adjust(module, code_start=code_start, stack_size=stack_size)
    bin_data = omf80.module_to_bin(module)

    with open(file_out, 'wb') as file:
        file.write(bin_data)
        file.close()
    

if __name__ == "__main__":
    main()
