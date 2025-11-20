#!/usr/bin/env python

import argparse
import logging
import sys

import omf80

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files_in", nargs="+", help="input omf files")
    parser.add_argument("-o", "--out", nargs="?", help="output file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                                                        action="store_true")
    args = parser.parse_args()

    files_in = args.files_in
    file_out = args.out
    verbose = args.verbose
    verbosity_level = logging.DEBUG if verbose else logging.ERROR
    logging.basicConfig(level=verbosity_level, stream=sys.stdout, format='%(levelname)s:\t%(message)s')

    logging.debug(f'files_in = {files_in}')
    logging.debug(f'file_out = {file_out}')

    # reading the files    
    lst = []
    for filename in files_in:
        f = open(filename, "rb")
        data = f.read()
        f.close()
        records = omf80.read_omf80(data)
        assert records[-1]['rec_typ'] == omf80.END_OF_FILE_RECORD
        lst.append(omf80.read_records(records[:-1]))

    # creating the output module
    module = omf80.link(lst)

    # writing the output to file
    r0 = omf80.module_to_records(module)
    r1 = omf80.add_eof(r0)
    bin_data = omf80.records_to_bin(r1)
    with open(file_out, 'wb') as file:
        file.write(bin_data)
        file.close()

if __name__ == "__main__":
    main()
