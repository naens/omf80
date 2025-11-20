#!/usr/bin/env python

import sys

import argparse
import pprint

import omf80

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
    args = parser.parse_args()
    pprinter = HexIntPrettyPrinter()

    files = args.files

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

    code_start = 0x100
    code_length = module['segments'][omf80.CODE_SEGMENT]['seg_length']
    stack_size = 0x64
    data_start = code_start + code_length + stack_size
    omf80.module_adjust(module, code_start=code_start, data_start=data_start)
    
    bin_data = omf80.module_to_bin(module)

    name = module['name'].lower()
    filename = f'{name}.tmp.bin'
    with open(filename, 'wb') as file:
        file.write(bin_data)
        file.close()
    print(f'written into {filename}')
    

if __name__ == "__main__":
    main()
