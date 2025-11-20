#!/usr/bin/env python

import argparse
import logging
import sys

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_in", help="path of the input omf file")
    parser.add_argument("-o", "--out", help="name of the binary output file")
    parser.add_argument("--code", help="start of the code segment")
    parser.add_argument("--stack", help="size of the stack segment")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                                                        action="store_true")
    args = parser.parse_args()

    file_in = args.file_in
    file_out = args.out
    code_start = read_int(args.code)
    stack_size = read_int(args.stack)
    verbose = args.verbose
    verbosity_level = logging.INFO if verbose else logging.ERROR
    logging.basicConfig(level=verbosity_level, stream=sys.stdout, format='%(levelname)s:\t%(message)s')

    logging.info(f'file_in = {file_in}')
    logging.info(f'file_out = {file_out}')
    logging.info(f'code_start = 0x{code_start:x} ({code_start})')
    logging.info(f'stack_size = 0x{stack_size:x} ({stack_size})')

    omf_file = open(file_in, "rb")
    omf_data = omf_file.read()
    omf_file.close()
    records = omf80.read_omf80(omf_data)

    mrecs = records[:-1]
    module = omf80.records_to_module(mrecs)

    code_length = module['segments'][omf80.CODE_SEGMENT]['seg_length']
    data_start = code_start + code_length + stack_size

    omf80.module_adjust(module, code_start=code_start, data_start=data_start)
    bin_data = omf80.module_to_bin(module)

    bin_file = open(file_out, "wb")
    bin_file.write(bin_data)
    bin_file.close()
    logging.info('DONE')

if __name__ == "__main__":
    main()
