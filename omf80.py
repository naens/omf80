#!/usr/bin/env python3

ABSOLUTE_SEGMENT = 0
CODE_SEGMENT = 1
DATA_SEGMENT = 2
STACK_SEGMENT = 3
MEMORY_SEGMENT = 4
RESERVED_SEGMENT = 5
UNNAMED_COMMON_SEGMENT = 255

MODULE_HEADER_RECORD = 0x02
LOCAL_SYMBOLS_RECORD = 0x12
EXTERNAL_NAMES_RECORD = 0x18
PUBLIC_DECLARATION_RECORD = 0x16
LINE_NUMBERS_RECORD = 0x08
CONTENT_RECORD = 0x06
INTERSEGMENT_REFERENCES_RECORD = 0x24
RELOCATION_RECORD = 0x22
EXTERNAL_REFERENCES_RECORD = 0x20
NAMED_COMMON_DEFINITIONS_RECORD = 0x2e
MODULE_ANCESTOR_RECORD = 0x10
MODULE_END_RECORD = 0x04
END_OF_FILE_RECORD = 0x0e
LIBRARY_HEADER_RECORD = 0x2c
LIBRARY_MODULE_NAMES_RECORD = 0x28
LIBRARY_MODULE_LOCATIONS_RECORD = 0x26
LIBRARY_DICTIONARY_RECORD = 0x2a

def get_str8(data):
    length = data[0]
    result = []
    for i in range(1, length+1):
        result.append(data[i])
    return bytearray(result).decode("ascii")

def write_str8(data):
    result = bytearray(len(data)+1)
    result[0] = len(data)
    result[1:] = data.encode('ascii')
    return result

def read16(data):
    return int.from_bytes(data[0:2], 'little', signed=False)

def check_ok(data):
    s = sum(data)
    r = s % 0x100
    return r == 0

def error(msg):
    print(f'error: {msg}')
    exit(1)


# PARSE BINARY RECORD DATA
def read_module_header_record(data):
    rec_typ = MODULE_HEADER_RECORD
    name = get_str8(data[0:])
    i = 1 + len(name) + 2
    segments = {}
    while i < len(data):
        seg_id = int(data[i])
        segment = {}
        segment["seg_length"] = read16(data[i+1:])
        segment["aln_typ"] = data[i+3]
        segments[seg_id] = segment
        i += 4
    record = {"rec_typ": rec_typ, "name": name, "segments": segments}
    return record

def read_local_symbols_record(data):
    rec_typ = LOCAL_SYMBOLS_RECORD
    seg_id = data[0]
    i = 1
    symbols = []
    while i < len(data):
        symbol = {}
        symbol["offset"] = read16(data[i+0:])
        name = get_str8(data[i+2:])
        symbol["name"] = name
        symbols.append(symbol)
        i += 2 + 1 + len(name) + 1
    record = {"rec_typ": rec_typ, "seg_id": seg_id, "symbols": symbols}
    return record

def read_external_names_record(data):
    rec_typ = EXTERNAL_NAMES_RECORD
    i = 0
    names = []
    while i < len(data):
        name = get_str8(data[i:])
        names.append(name)
        i += (1 + len(name)) + 1
    record = {"rec_typ": rec_typ, "names": names}
    return record

def read_public_declaration_record(data):
    rec_typ = PUBLIC_DECLARATION_RECORD
    seg_id = data[0]
    i = 1
    public_names = []
    while i < len(data):
        public_name = {}
        public_name["offset"] = read16(data[i+0:])
        name = get_str8(data[i+2:])
        public_name["name"] = name
        public_names.append(public_name)
        i = i + 2 + 1 + len(name) + 1
    record = {"rec_typ": rec_typ, "seg_id": seg_id, "public_names": public_names}
    return record

def read_line_numbers_record(data):
    rec_typ = LINE_NUMBERS_RECORD
    seg_id = data[0]
    i = 1
    line_numbers = []
    while i < len(data):
        lnum = {}
        lnum["offset"] = read16(data[i+0:])
        lnum["line_number"] = read16(data[i+2:])
        line_numbers.append(lnum)
        i = i + 4
    record = {"rec_typ": rec_typ, "seg_id": seg_id, "line_numbers": line_numbers}
    return record

def read_content_record(data):
    rec_typ = CONTENT_RECORD
    seg_id = data[0]
    offset = read16(data[1:])
    i = 3
    dat = bytearray()
    while i < len(data):
        dat.append(data[i])
        i += 1
    record = {"rec_typ": rec_typ, "seg_id": seg_id, "offset": offset, "dat": dat}
    return record

def read_intersegment_references_record(data):
    rec_typ = INTERSEGMENT_REFERENCES_RECORD
    seg_id = data[0]
    lo_hi_both = data[1]
    i = 2
    offsets = []
    while i < len(data):
        offset = read16(data[i:])
        offsets.append(offset)
        i += 2
    record = {"rec_typ": rec_typ, "seg_id": seg_id, "lo_hi_both": lo_hi_both, "offsets": offsets}
    return record

def read_relocation_record(data):
    rec_typ = RELOCATION_RECORD
    lo_hi_both = data[0]
    i = 1
    offsets = []
    while i < len(data):
        offsets.append(read16(data[i:]))
        i += 2
    record = {"rec_typ": rec_typ, "lo_hi_both": lo_hi_both, "offsets": offsets}
    return record

def read_external_references_record(data):
    rec_typ = EXTERNAL_REFERENCES_RECORD
    lo_hi_both = data[0]
    i = 1
    references = []
    while i < len(data):
        reference = {}
        reference["name_index"] = read16(data[i:])
        reference["offset"] = read16(data[i+2:])
        references.append(reference)
        i += 4
    record = {"rec_typ": rec_typ, "lo_hi_both": lo_hi_both, "references": references}
    return record
    
def read_named_common_definitions_record(data):
    rec_typ = NAMED_COMMON_DEFINITIONS_RECORD
    seg_id = data[0]
    i = 1
    cns = []
    while i < len(data):
        cn = {}
        cn["seg_id"] = data[i]
        name = get_str8(data[i+1:])
        cn["common_name"] = name
        cns.append(cn)
        i += 1 + (1 + len(name))
    record = {"rec_typ": rec_typ, "common_names": cns}
    return record

def read_module_ancestor_record(data):
    rec_typ = MODULE_ANCESTOR_RECORD
    module_name = get_str8(data)
    record = {"rec_typ": rec_typ, "module_name": module_name}
    return record

def read_module_end_record(data):
    rec_typ = MODULE_END_RECORD
    mod_typ = data[0]
    seg_id = data[1]
    offset = read16(data[2:])
    optional_info = []
    i = 4
    if i < len(data):
        while i < length + 3:
            optional_info.append(data[i])
            i += 1
    record = {"rec_typ": rec_typ, "mod_typ": mod_typ, "seg_id": seg_id,
                "offset": offset, "optional_info": optional_info}
    return record

def read_end_of_file_record(data):
    rec_typ = END_OF_FILE_RECORD
    record = {"rec_typ": rec_typ}
    return record

def read_library_header_record(data):
    rec_typ = LIBRARY_HEADER_RECORD
    module_count = read16(data[0:])
    block_number = read16(data[2:])
    byte_number = read16(data[4:])
    record = {"rec_typ": rec_typ, "module_count": module_count,
        "block_number": block_number, "byte_number": byte_number}
    return record

def read_library_module_names_record(data):
    rec_typ = LIBRARY_MODULE_NAMES_RECORD
    module_names = []
    i = 0
    while i < len(data):
        name = get_str8(data[i:])
        i += len(name) + 1
        module_names.append(name)
    record = {"rec_typ": rec_typ, "module_names": module_names}
    return record

def read_library_module_locations_record(data):
    rec_typ = LIBRARY_MODULE_LOCATIONS_RECORD
    i = 0
    pairs = []
    while i < len(data):
        block_number = read16(data[i:])
        byte_number = read16(data[i+2:])
        i += 4
        pairs.append({"block_number": block_number, "byte_number": byte_number})
    record = {"rec_typ": rec_typ, "pairs": pairs}
    return record

def read_library_dictionary_record(data):
    rec_typ = LIBRARY_DICTIONARY_RECORD
    i = 0
    module_groups = []
    while i < len(data):
        module_group = []
        while data[i] != 0:
            public_name = get_str8(data[i:])
            i += len(public_name) + 1
            module_group.append(public_name)
        i += 1
        module_groups.append(module_group)
    record = {"rec_typ": rec_typ, "module_groups": module_groups}
    return record

def bin_to_record(data):
    type = data[0]
    if not check_ok(data):
        print("check not OK")
        exit(0)
    if type == MODULE_HEADER_RECORD:
        return read_module_header_record(data[3:-1])
    elif type == LOCAL_SYMBOLS_RECORD:
        return read_local_symbols_record(data[3:-1])
    elif type == EXTERNAL_NAMES_RECORD:
        return read_external_names_record(data[3:-1])
    elif type == PUBLIC_DECLARATION_RECORD:
        return read_public_declaration_record(data[3:-1])
    elif type == LINE_NUMBERS_RECORD:
        return read_line_numbers_record(data[3:-1])
    elif type == CONTENT_RECORD:
        return read_content_record(data[3:-1])
    elif type == INTERSEGMENT_REFERENCES_RECORD:
        return read_intersegment_references_record(data[3:-1])
    elif type == RELOCATION_RECORD:
        return read_relocation_record(data[3:-1])
    elif type == EXTERNAL_REFERENCES_RECORD:
        return read_external_references_record(data[3:-1])
    elif type == MODULE_END_RECORD:
        return read_module_end_record(data[3:-1])
    elif type == NAMED_COMMON_DEFINITIONS_RECORD:
        return read_named_common_definitions_record(data[3:-1])
    elif type == MODULE_ANCESTOR_RECORD:
        return read_module_ancestor_record(data[3:-1])
    elif type == END_OF_FILE_RECORD:
        return read_end_of_file_record(data[3:-1])
    elif type == LIBRARY_HEADER_RECORD:
        return read_library_header_record(data[3:-1])
    elif type == LIBRARY_MODULE_NAMES_RECORD:
        return read_library_module_names_record(data[3:-1])
    elif type == LIBRARY_MODULE_LOCATIONS_RECORD:
        return read_library_module_locations_record(data[3:-1])
    elif type == LIBRARY_DICTIONARY_RECORD:
        return read_library_dictionary_record(data[3:-1])
    else:
        print(f"omf80: record type not supported 0x{type:02x}")
        exit(0)


# CONVERT RECORDS TO STRING
def module_header_record_to_string(record):
    result = ["MODULE HEADER RECORD"]
    result.append(f'\tMODULE NAME =\"{record["name"]}\"')
    segments = record["segments"]
    for seg_id,segment in segments.items():
        seg_length = segment["seg_length"]
        aln_typ = segment["aln_typ"]
        result.append(f"\tSEG ID = {seg_id:02x}, LENGTH = {seg_length}, ALN = {aln_typ}")
    return "\n".join(result)

def local_symbols_record_to_string(record):
    result = ["LOCAL SYMBOLS RECORD"]
    seg_id = record["seg_id"]
    result.append(f"\tSEG ID = {seg_id}")
    symbols = record["symbols"]
    for symbol in symbols:
        offset = symbol["offset"]
        name = symbol["name"]
        result.append(f"\tOFFSET = 0x{offset:04x}, SYMBOL NAME = {name}")
    return "\n".join(result)

def external_names_record_to_string(record):
    result = ["EXTERNAL NAMES RECORD"]
    names = record["names"]
    for name in names:
        result.append(f"\tEXTERNAL NAME = {name}")
    return "\n".join(result)

def public_declaration_record_to_string(record):
    result = ["PUBLIC DECLARATION RECORD"]
    seg_id = record["seg_id"]
    result.append(f"\tSEG ID = {seg_id}")
    public_names = record["public_names"]
    for public_name in public_names:
        offset = public_name["offset"]
        name = public_name["name"]
        result.append(f"\tOFFSET = 0x{offset:04x}, PUBLIC NAME = {name}")
    return "\n".join(result)

def line_numbers_record_to_string(record):
    result = ['LINE NUMBERS RECORD']
    seg_id = record["seg_id"]
    result.append(f"\tSEG ID = {seg_id}")
    line_numbers = record["line_numbers"]
    for lnum in line_numbers:
        offset = lnum["offset"]
        line_number = lnum["line_number"]
        result.append(f"\tOFFSET = 0x{offset:04x}, LINE NUMBER = {line_number}")
    return "\n".join(result)

def content_record_to_string(record):
    result = ['CONTENT RECORD']
    seg_id = record["seg_id"]
    result.append(f"\tSEG ID = {seg_id}")
    offset = record["offset"]
    result.append(f"\tOFFSET = 0x{offset:04x}")
    dat = record["dat"]
    str = "\tDAT = "
    i = 0
    for d in dat:
        str += f"{d:02x} "
        i += 1
        if i % 16 == 0 and i != len(dat) :
            result.append(str)
            str = "\t      "
    result.append(str)
    return "\n".join(result)

def intersegment_references_record_to_string(record):
    result = ["INTER-SEGMENT REFERENCES RECORD"]
    seg_id = record["seg_id"]
    result.append(f"\tSEG ID = {seg_id}")
    lo_hi_both = record["lo_hi_both"]
    result.append(f"\tLO HI BOTH = {lo_hi_both}")
    offsets = record["offsets"]
    for offset in offsets:
        result.append(f"\tOFFSET = 0x{offset:04x}")
    return "\n".join(result)

def relocation_record_to_string(record):
    result = ["RELOCATION RECORD"]
    lo_hi_both = record["lo_hi_both"]
    result.append(f"\tLO HI BOTH = {lo_hi_both}")
    offsets = record["offsets"]
    for offset in offsets:
        result.append(f"\tOFFSET = 0x{offset:04x}")
    return "\n".join(result)

def external_references_record_to_string(record):
    result = ["EXTERNAL REFERENCES RECORD"]
    lo_hi_both = record["lo_hi_both"]
    result.append(f"\tLO HI BOTH = {lo_hi_both}")
    references = record["references"]
    for reference in references:
        name_index = reference["name_index"]
        offset = reference["offset"]
        result.append(f"\tEXTERNAL_NAME_INDEX = 0x{name_index:04x},"
            f" OFFSET = 0x{offset:04x}")
    return "\n".join(result)
    
def named_common_definitions_record_to_string(record):
    result = ["NAMED_COMMON_DEFINITIONS_RECORD"]
    cns = record["common_names"]
    for cn in cns:
        seg_id = record["seg_id"]
        name = cn["common_name"]
        result.append(f"\tSEG ID = {seg_id}, SYMBOL NAME = {name}")
    return "\n".join(result)

def module_ancestor_record_to_string(record):
    result = ["MODULE_ANCESTOR_RECORD"]
    result.append(f'\tMODULE NAME = \"{record["module_name"]}\"')
    return "\n".join(result)

def module_end_record_to_string(record):
    result = ["MODULE END RECORD"]
    mod_typ = record["mod_typ"]
    result.append(f"\tMOD TYP = {mod_typ}")
    seg_id = record["seg_id"]
    result.append(f"\tSEG ID = {seg_id}")
    offset = record["offset"]
    result.append(f"\tOFFSET = 0x{offset:04x}")
    optional_info = record["optional_info"]
    if len(optional_info) > 0:
        str = f"\tOPTIONAL INFO = "
        i = 0
        while i < length:
            str += f"{optional_info[i]:02x} "
            i += 1
            if i % 16 == 0 and i != len(optional_info):
                result.append(str)
                str = "\t      "
        result.append(str)
    return "\n".join(result)

def library_header_record_to_string(record):
    result = ["LIBRARY_HEADER_RECORD"]
    module_count = record["module_count"]
    block_number = record["block_number"]
    byte_number = record["byte_number"]
    result.append(f'\tMODULE COUNT = {module_count}')
    result.append(f'\tBLOCK NUMBER = {block_number}')
    result.append(f'\tBYTE NUMBER = {byte_number}')
    return "\n".join(result)

def library_module_names_record_to_string(record):
    result = ["LIBRARY_MODULE_NAMES_RECORD"]
    for module_name in record["module_names"]:
        result.append(f'\t{module_name}')
    return "\n".join(result)

def library_module_locations_record_to_string(record):
    result = ["LIBRARY_MODULE_LOCATIONS_RECORD"]
    for pair in record["pairs"]:
        result.append(f'\tBLOCK NUMBER = {pair["block_number"]}, ' +
                        f'BYTE NUMBER = {pair["byte_number"]}')
    return "\n".join(result)

def library_dictionary_record_to_string(record):
    result = ["LIBRARY_DICTIONARY_RECORD"]
    for module_group in record["module_groups"]:
        result.append(f'\t{module_group}')
    return "\n".join(result)
    
def end_of_file_record_to_string(record):
    return "END OF FILE RECORD"

def record_to_string(record):
    type = record["rec_typ"]
    if type == MODULE_HEADER_RECORD:
        return module_header_record_to_string(record)
    elif type == LOCAL_SYMBOLS_RECORD:
        return local_symbols_record_to_string(record)
    elif type == EXTERNAL_NAMES_RECORD:
        return external_names_record_to_string(record)
    elif type == PUBLIC_DECLARATION_RECORD:
        return public_declaration_record_to_string(record)
    elif type == LINE_NUMBERS_RECORD:
        return line_numbers_record_to_string(record)
    elif type == CONTENT_RECORD:
        return content_record_to_string(record)
    elif type == INTERSEGMENT_REFERENCES_RECORD:
        return intersegment_references_record_to_string(record)
    elif type == RELOCATION_RECORD:
        return relocation_record_to_string(record)
    elif type == EXTERNAL_REFERENCES_RECORD:
        return external_references_record_to_string(record)
    elif type == NAMED_COMMON_DEFINITIONS_RECORD:
        return named_common_definitions_record_to_string(record)
    elif type == MODULE_ANCESTOR_RECORD:
        return module_ancestor_record_to_string(record)
    elif type == MODULE_END_RECORD:
        return module_end_record_to_string(record)
    elif type == LIBRARY_HEADER_RECORD:
        return library_header_record_to_string(record)
    elif type == LIBRARY_MODULE_NAMES_RECORD:
        return library_module_names_record_to_string(record)
    elif type == LIBRARY_MODULE_LOCATIONS_RECORD:
        return library_module_locations_record_to_string(record)
    elif type == LIBRARY_DICTIONARY_RECORD:
        return library_dictionary_record_to_string(record)
    elif type == END_OF_FILE_RECORD:
        return end_of_file_record_to_string(record)
    else:
        print(f"record_to_string: record type not supported 0x{type:02x}")
        print(record)
        exit(-1)


# CONVERT RECORDS TO BINARY DATA
def mkrec(data, type):
    rec = bytearray(3 + len(data) + 1)
    rec[0] = type
    rec[1:3] = (len(data)+1).to_bytes(length=2, byteorder='little')
    rec[3:-1] = data
    rec[-1] = (-sum(rec))  & 0xff
    return rec

def write_module_header_record(record):
    rec_data = bytearray()
    rec_data += write_str8(record["name"])
    rec_data.append(0)
    rec_data.append(0)
    segments = record["segments"]
    for seg_id, segment in segments.items():
        rec_data.append(seg_id)
        rec_data += segment["seg_length"].to_bytes(length=2, byteorder='little')
        rec_data.append(segment["aln_typ"])
    return mkrec(rec_data, record["rec_typ"])

def write_local_symbols_record(record):
    rec_data = bytearray()
    rec_data.append(record["seg_id"])
    symbols = record["symbols"]
    for symbol in symbols:
        rec_data += symbol["offset"].to_bytes(length=2, byteorder='little')
        rec_data += write_str8(symbol["name"])
        rec_data.append(0)
    return mkrec(rec_data, record["rec_typ"])

def write_external_names_record(record):
    rec_data = bytearray()
    names = record["names"]    
    for name in names:
        rec_data += write_str8(name)
        rec_data.append(0)
    return mkrec(rec_data, record["rec_typ"])

def write_public_declaration_record(record):
    rec_data = bytearray()
    seg_id = record["seg_id"]
    rec_data.append(seg_id)
    for pn in record["public_names"]:
        rec_data += pn["offset"].to_bytes(length=2, byteorder='little')
        rec_data += write_str8(pn["name"])
        rec_data.append(0)
    return mkrec(rec_data, record["rec_typ"])

def write_line_numbers_record(record):
    rec_data = bytearray()
    seg_id = record["seg_id"]
    rec_data.append(seg_id)
    for lnum in record["line_numbers"]:
        rec_data += lnum["offset"].to_bytes(length=2, byteorder='little')
        rec_data += lnum["line_number"].to_bytes(length=2, byteorder='little')
    return mkrec(rec_data, record["rec_typ"])

def write_content_record(record):
    rec_data = bytearray()
    rec_data.append(record["seg_id"])
    rec_data += record["offset"].to_bytes(length=2, byteorder='little')
    rec_data += record["dat"]
    return mkrec(rec_data, record["rec_typ"])

def write_intersegment_references_record(record):
    rec_data = bytearray()
    rec_data.append(record["seg_id"])
    rec_data.append(record["lo_hi_both"])
    for offset in record["offsets"]:
        rec_data += offset.to_bytes(length=2, byteorder='little')
    return mkrec(rec_data, record["rec_typ"])

def write_relocation_record(record):
    rec_data = bytearray()
    rec_data.append(record["lo_hi_both"])
    for offset in record["offsets"]:
        rec_data += offset.to_bytes(length=2, byteorder='little')
    return mkrec(rec_data, record["rec_typ"])

def write_external_references_record(record):
    rec_data = bytearray()
    rec_data.append(record["lo_hi_both"])
    for ref in record["references"]:
        rec_data += ref["name_index"].to_bytes(length=2, byteorder='little')
        rec_data += ref["offset"].to_bytes(length=2, byteorder='little')
    return mkrec(rec_data, record["rec_typ"])

def write_module_end_record(record):
    rec_data = bytearray()
    rec_data.append(record["mod_typ"])
    rec_data.append(record["seg_id"])
    rec_data += record["offset"].to_bytes(length=2, byteorder='little')
    for b in record["optional_info"]:
        rec_data.append(b)
    return mkrec(rec_data, record["rec_typ"])

def write_named_common_definitions_record(record):
    rec_data = bytearray()
    for cn in record["common_names"]:
        rec_data.append(cn["seg_id"])
        rec_data += write_str8(cn["common_name"])
    return mkrec(rec_data, record["rec_typ"])

def write_module_ancestor_record(record):
    return mkrec(write_str8(record["module_name"]), record["rec_typ"])

def write_end_of_file_record(record):
    return mkrec(b'', record["rec_typ"])

def write_library_header_record(record):
    rec_data = bytearray()
    rec_data += record["module_count"].to_bytes(length=2, byteorder='little')
    rec_data += record["block_number"].to_bytes(length=2, byteorder='little')
    rec_data += record["byte_number"].to_bytes(length=2, byteorder='little')
    return mkrec(rec_data, record["rec_typ"])

def write_library_module_names_record(record):
    rec_data = bytearray()
    for name in record["module_names"]:
        rec_data += write_str8(name)
    return mkrec(rec_data, record["rec_typ"])

def write_library_module_locations_record(record):
    rec_data = bytearray()
    for pair in record["pairs"]:
        rec_data += pair["block_number"].to_bytes(length=2, byteorder='little')
        rec_data += pair["byte_number"].to_bytes(length=2, byteorder='little')
    return mkrec(rec_data, record["rec_typ"])

def write_library_dictionary_record(record):
    rec_data = bytearray()
    for mgrp in record["module_groups"]:
        for name in mgrp:
            rec_data += write_str8(name)
        rec_data.append(0)
    return mkrec(rec_data, record["rec_typ"])

def record_to_bin(record):
    type = record["rec_typ"]
    if type == MODULE_HEADER_RECORD:
        return write_module_header_record(record)
    elif type == LOCAL_SYMBOLS_RECORD:
        return write_local_symbols_record(record)
    elif type == EXTERNAL_NAMES_RECORD:
        return write_external_names_record(record)
    elif type == PUBLIC_DECLARATION_RECORD:
        return write_public_declaration_record(record)
    elif type == LINE_NUMBERS_RECORD:
        return write_line_numbers_record(record)
    elif type == CONTENT_RECORD:
        return write_content_record(record)
    elif type == INTERSEGMENT_REFERENCES_RECORD:
        return write_intersegment_references_record(record)
    elif type == RELOCATION_RECORD:
        return write_relocation_record(record)
    elif type == EXTERNAL_REFERENCES_RECORD:
        return write_external_references_record(record)
    elif type == MODULE_END_RECORD:
        return write_module_end_record(record)
    elif type == NAMED_COMMON_DEFINITIONS_RECORD:
        return write_named_common_definitions_record(record)
    elif type == MODULE_ANCESTOR_RECORD:
        return write_module_ancestor_record(record)
    elif type == END_OF_FILE_RECORD:
        return write_end_of_file_record(record)
    elif type == LIBRARY_HEADER_RECORD:
        return write_library_header_record(record)
    elif type == LIBRARY_MODULE_NAMES_RECORD:
        return write_library_module_names_record(record)
    elif type == LIBRARY_MODULE_LOCATIONS_RECORD:
        return write_library_module_locations_record(record)
    elif type == LIBRARY_DICTIONARY_RECORD:
        return write_library_dictionary_record(record)
    else:
        print(f"omf80: record type not supported 0x{type:02x}")
        exit(0)


# bin_to_records
def read_omf80(data):
    records = []
    i = 0
    while i < len(data):
        type = data[i]
        length = read16(data[i+1:])
        records.append(bin_to_record(data[i:i+length+3]))
        i = i + length + 3
    return records
bin_to_records = read_omf80

def records_to_bin(records):
    bin_data = bytearray()
    for record in records:
        rec_bin = record_to_bin(record)
        bin_data += rec_bin
    return bin_data

def is_module(records):
    record = records[0]
    type = record["rec_typ"]
    return type == MODULE_HEADER_RECORD

def is_library(records):
    record = records[0]
    type = record["rec_typ"]
    return type == LIBRARY_HEADER_RECORD

def records_to_library(records):
    library = {'type': 'LIBRARY'}
    modules = []
    module_records = None
    dictionary = {}
    for record in records:
        type = record["rec_typ"]
        if type == LIBRARY_HEADER_RECORD:
            pass
        elif type == LIBRARY_MODULE_NAMES_RECORD:
            pass
        elif type == LIBRARY_MODULE_LOCATIONS_RECORD:
            pass
        elif type == LIBRARY_DICTIONARY_RECORD:
            module_groups = record["module_groups"]
            for i in range(len(module_groups)):
                for name in module_groups[i]:
                    dictionary[name] = i
        else:
            if type == MODULE_HEADER_RECORD:
                module_records = []
            module_records.append(record)
            if type == MODULE_END_RECORD:
                modules.append(records_to_module(module_records))
    library["modules"] = modules
    library["dictionary"] = dictionary
    return library

def make_module_header_record(module):
    record = {}
    record["rec_typ"] = MODULE_HEADER_RECORD
    record["name"] = module["name"]
    record["segments"] = module["segments"].copy()
    return record

def make_module_named_common_definitions_record(module):
    record = {}
    record["rec_typ"] = NAMED_COMMON_DEFINITIONS_RECORD
    record["comon_names"] = module["common_names"].copy()
    return record

def make_external_names_record(module):
    record = {}
    record["rec_typ"] = EXTERNAL_NAMES_RECORD
    record["names"] = module["external_names"].copy()
    return record

def make_public_declarations_records(module):
    records = []
    for seg_id, pub_decl in module["public_declarations"].items():
        record = {}
        record["rec_typ"] = PUBLIC_DECLARATION_RECORD
        record["seg_id"] = seg_id
        record["public_names"] = pub_decl.copy()
        records.append(record)
    return records

def make_module_ancestor_record(debug_info):
    record = {}
    record["rec_typ"] = MODULE_ANCESTOR_RECORD
    record["module_name"] = debug_info["ancestor_name"]
    return record

def make_module_local_symbols_records(debug_info):
    records = []
    for seg_id, loc_syms in debug_info.get("local_symbols", {}).items():
        record = {}
        record["rec_typ"] = LOCAL_SYMBOLS_RECORD
        record["seg_id"] = seg_id
        record["symbols"] = loc_syms
        records.append(record)
    return records

def make_module_line_numbers_records(debug_info):
    records = []
    for seg_id, lnums in debug_info.get("line_numbers", {}).items():
        record = {}
        record["rec_typ"] = LINE_NUMBERS_RECORD
        record["seg_id"] = seg_id
        record["line_numbers"] = lnums
        records.append(record)
    return records

def make_content_record(cdef):
    record = {}
    record["rec_typ"] = CONTENT_RECORD
    record["seg_id"] = cdef["seg_id"]
    record["offset"] = cdef["offset"]
    record["dat"] = cdef["data"]
    return record

def make_intersegment_refernces_records(cdef):
    records = []
    for (seg_id,lo_hi_both), offsets in cdef["internal"].items():
        record = {}
        record["rec_typ"] = INTERSEGMENT_REFERENCES_RECORD
        record["seg_id"] = seg_id
        record["lo_hi_both"] = lo_hi_both
        record["offsets"] = offsets
        records.append(record)
    return records

def make_external_references_record(cdef, exdict):
    records = []
    for lhb, exts in cdef["external"].items():
        record = {}
        record["rec_typ"] = EXTERNAL_REFERENCES_RECORD
        record["lo_hi_both"] = lhb
        f = lambda x : {"name_index" : exdict[x["name"]], "offset" : x["offset"]}
        record["references"] = list(map(f, exts))
        records.append(record)
    return records

def make_module_end_record(module):
    record = {}
    record["rec_typ"] = MODULE_END_RECORD
    record["mod_typ"] = 1 if module["is_main"] else 0
    record["seg_id"] = 1
    record["offset"] = 0
    record["optional_info"] = []
    return record

def module_to_records(module):
    records = []

    records.append(make_module_header_record(module))
    if "common_names" in module:
        records.append(make_module_named_common_definitions_record(module))

    if "external_names" in module:
        records.append(make_external_names_record(module))
    records += make_public_declarations_records(module)

    if "debug_info" in module:
        for debug_info in module["debug_info"]:
            if "ancestor_name" in debug_info:
                records.append(make_module_ancestor_record(debug_info))
            records += make_module_local_symbols_records(debug_info)
            records += make_module_line_numbers_records(debug_info)

    for cdef in module["content_definitions"]:
        records.append(make_content_record(cdef))
        if "internal" in cdef:
            records += make_intersegment_refernces_records(cdef)
        if "external_names" in module and "external" in cdef :
            exdict = dict((n,i) for i,n in enumerate(module["external_names"]))
            records += make_external_references_records(cdef, exdict)

    records.append(make_module_end_record(module))
    return records

def library_to_records(library):
    records = []
    for module in library["modules"]:
        records += module_to_records(module)
    return records

def records_to_module(records):
    module = {'type': 'MODULE'}
    assert len(records) > 0
    assert records[0]["rec_typ"] == MODULE_HEADER_RECORD
    assert records[-1]["rec_typ"] == MODULE_END_RECORD
    cdef = None
    for record in records:
        type = record["rec_typ"]
        if type == MODULE_HEADER_RECORD:
            module["name"] = record["name"]
            module["segments"] = record["segments"].copy()
        elif type == MODULE_END_RECORD:
            module["is_main"] = record["mod_typ"] == 1
        elif type == NAMED_COMMON_DEFINITIONS_RECORD:
            module["common_names"] = record["common_names"].copy()
        elif type == EXTERNAL_NAMES_RECORD:
            module["external_names"] = record["names"].copy()
        elif type == PUBLIC_DECLARATION_RECORD:
            seg_id = record["seg_id"]
            pub_decls = module.setdefault("public_declarations", {})
            pub_decl_seg = pub_decls.setdefault(seg_id, [])
            for pn in record["public_names"]:
                pub_decl_seg.append({"name": pn["name"], "offset" : pn["offset"]})
            pub_decl_seg.sort(key = lambda x : x["offset"])
        elif type == MODULE_ANCESTOR_RECORD:
            debug_info = {}
            module.setdefault("debug_info", []).append(debug_info)
            debug_info["ancestor_name"] = record["module_name"]
        elif type == LOCAL_SYMBOLS_RECORD:
            debug_info = module.setdefault("debug_info", [{}])[-1]
            seg_id = record["seg_id"]
            loc_syms = debug_info.setdefault("local_symbols", {})
            loc_sym_seg = loc_syms.setdefault(seg_id, [])
            for sym in record["symbols"]:
                loc_sym_seg.append({"name": sym["name"], "offset": sym["offset"]})
            loc_sym_seg.sort(key = lambda x : x["offset"])
        elif type == LINE_NUMBERS_RECORD:
            debug_info = module.setdefault("debug_info", [{}])[-1]
            seg_id = record["seg_id"]
            lns = debug_info.setdefault("line_numbers", {})
            ln_seg = lns.setdefault(seg_id, [])
            for ln in record["line_numbers"]:
                ln_seg.append({"line_number": ln["line_number"], "offset": ln["offset"]})
            ln_seg.sort(key = lambda x : x["offset"])
        elif type == CONTENT_RECORD:
            cdef = {}
            cdef["seg_id"] = record["seg_id"]
            cdef["offset"] = record["offset"]
            cdef["data"] = record["dat"]
            cdefs = module.setdefault("content_definitions", [])
            cdefs.append(cdef)
        elif type == RELOCATION_RECORD:
            lhb = record["lo_hi_both"]
            internal = cdef.setdefault("internal", {})
            for offs in record["offsets"]:
                seg = cdef["seg_id"]
                offlst = internal.setdefault((seg,lhb), [])
                offlst.append(offs)
        elif type == INTERSEGMENT_REFERENCES_RECORD:
            seg = record["seg_id"]
            lhb = record["lo_hi_both"]
            internal = cdef.setdefault("internal", {})
            intseg = internal.setdefault((seg, lhb), [])
            for offs in record["offsets"]:
                intseg.append(offs)
        elif type == EXTERNAL_REFERENCES_RECORD:
            lhb = record["lo_hi_both"]
            external = cdef.setdefault("external", {})
            exts = external.setdefault(lhb, [])
            for ext in record["references"]:
                name_index = ext["name_index"]
                name = module["external_names"][name_index]
                offs = ext["offset"]
                exts.append({"name": name, "offset": offs})
            exts.sort(key = lambda x : x["offset"])
        else:
            error(f"unknown type: 0x{type:02x}")
    return module

def add16(data, offset, num):
    old = int.from_bytes(data[offset:offset+2], byteorder='little')
    new = old + num
    data[offset:offset+2] = new.to_bytes(length=2, byteorder='little')

# link modules only one module
def link_modules(modules):

    def get_offset(seg_id, code_offset, data_offset):
        if seg_id == ABSOLUTE_SEGMENT:
            return 0
        if seg_id == CODE_SEGMENT:
            return code_offset
        if seg_id == DATA_SEGMENT:
            return data_offset
        if seg_id == STACK_SEGMENT:
            return data_offset
        if seg_id == MEMORY_SEGMENT:
            return 0
        error(f'link: unknown segment: {seg_id}')

    module = {'type': 'MODULE'}

    code_offset = 0
    data_offset = 0
    module['name'] = None
    module['is_main'] = False
    msegs = module.setdefault("segments", {})
    cdefs = module.setdefault("content_definitions", [])
    pub = {}
    for mod in modules:

        # segments
        for seg_id, seg in mod["segments"].items():
            mseg = msegs.setdefault(seg_id, {})
            mseg['aln_typ'] = mseg.get('aln_typ', seg['aln_typ'])
            mseg['seg_length'] = seg['seg_length'] + mseg.get('seg_length', 0)
        module["segments"] = {id: seg for id, seg in msegs.items() if seg['seg_length'] > 0}

        # is_main
        module['is_main'] = module['is_main'] or mod['is_main']

        # name
        if mod['is_main']:
            module['name'] = mod['name']

        # public declarations
        pub_decls = module.setdefault('public_declarations', {})
        for seg_id, pub_decl in mod["public_declarations"].items():
            pdlist = pub_decls.setdefault(seg_id, [])
            for pd in pub_decl:
                offset = pd['offset'] + get_offset(seg_id, code_offset, data_offset)
                name = pd['name']
                pdlist.append({'name': name, 'offset': offset})
                pub[name] = {'seg_id': seg_id, 'value': offset}
    
        # content definitions
        for cdef0 in mod["content_definitions"]:
            cdef1 = {}
            seg_id0 = cdef0['seg_id']
            cdef1['seg_id'] = seg_id0
            cdef_offset0 = cdef0['offset']
            cdef1['offset'] = cdef_offset0 + get_offset(seg_id0, code_offset, data_offset)
            data1 = cdef0['data'].copy()
            cdef1['data'] = data1
            if 'internal' in cdef0:
                internal0 = cdef0['internal']
                internal1 = {}
                for (seg_id, lhb), offsets0 in internal0.items():
                    offsets1 = []
                    for offset0 in offsets0:
                        offsets1.append(offset0 + get_offset(seg_id0, code_offset, data_offset))
                        i = offset0 - cdef_offset0
                        add16(data1, i, get_offset(seg_id, code_offset, data_offset))
                    internal1[(seg_id, lhb)] = offsets1
                cdef1['internal'] = internal1
            if 'external' in cdef0:
                external0 = cdef0['external']
                external1 = cdef1.setdefault('external', {})
                for lhb, exts0 in external0.items():
                    exts1 = external1.setdefault(lhb, [])
                    for ext in exts0:
                        name = ext["name"]
                        offset = ext["offset"] + get_offset(seg_id0, code_offset, data_offset)
                        exts1.append({'name': name, 'offset': offset})
            module["content_definitions"].append(cdef1)
                
        # debug info
        if 'debug_info' in mod:
            for debug_info0 in mod['debug_info']:
                debug_info1 = {}
                debug_info1['ancestor_name'] = mod['name']
                if 'line_numbers' in debug_info0:
                    line_numbers0 = debug_info0['line_numbers']
                    line_numbers1 = debug_info1.setdefault('line_numbers', {})
                    for seg_id, lnums0 in line_numbers0.items():
                        lnums1 = line_numbers1.setdefault(seg_id, [])
                        for lnum0 in lnums0:
                            offset1 = lnum0['offset'] + get_offset(seg_id, code_offset, data_offset)
                            lnums1.append({'line_number': lnum0['line_number'], 'offset': offset1})
                if 'local_symbols' in debug_info0:
                    local_symbols0 = debug_info0['local_symbols']
                    local_symbols1 = debug_info1.setdefault('local_symbols', {})
                    for seg_id, lsyms0 in local_symbols0.items():
                        lsyms1 = local_symbols1.setdefault(seg_id, [])
                        for lsym0 in lsyms0:
                            offset1 = lsym0['offset'] + get_offset(seg_id, code_offset, data_offset)
                            lsyms1.append({'name': lsym0['name'], 'offset': offset1})
                module['debug_info'] = module.get('debug_info', []) + [debug_info1]

        code_offset += mod["segments"][CODE_SEGMENT]["seg_length"]
        data_offset += mod["segments"][DATA_SEGMENT]["seg_length"]

    # resolve external
    for cdef in module["content_definitions"]:
        data = cdef['data']
        cdef_offset = cdef['offset']
        if 'external' in cdef:
            for lhb, exts in cdef['external'].items():
                for ext in exts:
                    name = ext['name']
                    offset = ext['offset']
                    if name in pub:
                        pu = pub[name]
                        seg_id = pu['seg_id']
                        add16(data, offset - cdef_offset, pu['value'])
                        k = (seg_id, lhb)
                        if seg_id != ABSOLUTE_SEGMENT:
                            internal = cdef.setdefault('internal', {})
                            if k in internal:
                                internal[k].append(ext['offset'])
                            else:
                                internal[k] = [ext['offset']]
                    else:
                        error(f'unresolved external {name}')
            del cdef['external']
    return module

# convert a list of records to a module or library
def read_records(records):
    if is_module(records):
        module = records_to_module(records)
        return module
    elif is_library(records):
        library = records_to_library(records)
        return library
    error("unknown records")
    

# link modules and libraries
def link(lst):
    modules = []
    public_names = set()
    extern_names = set()
    for item in lst:
        if item['type'] == 'MODULE':
            module = item
            ext = set(module['external_names'])
            extern_names |= ext
            pub = set(map(lambda x : x['name'], sum(module['public_declarations'].values(), [])))
            public_names |= pub
            extern_names -= public_names
            modules.append(module)
        if item['type'] == 'LIBRARY':
            library = item
            dictionary = library['dictionary']
            lib_names = set(dictionary.keys())
            common_names = lib_names & extern_names
            indices = set()
            for name in common_names:
                index = dictionary[name]
                indices.add(index)
            library_modules = library['modules']
            for index in indices:
                module = library_modules[index]
                ext = set(module.get('external_names', []))
                extern_names |= ext
                pub = set(map(lambda x : x['name'], sum(module['public_declarations'].values(), [])))
                public_names |= pub
                extern_names -= public_names
                modules.append(module)
    return link_modules(modules)

def add_eof(records):
    rec_typ = END_OF_FILE_RECORD
    eof_rec = {"rec_typ": rec_typ}
    return records + [eof_rec]

# EXAMPLE:
#    code_start = 0x100
#    code_length = module['segments'][omf80.CODE_SEGMENT]['seg_length']
#    stack_size = 0x64
#    data_start = code_start + code_length + stack_size
def module_adjust(module, code_start=0, stack_size=2):
    code_length = module['segments'][CODE_SEGMENT]['seg_length']
    data_start = code_start + code_length + stack_size
    module['segments'][STACK_SEGMENT]['seg_length'] = stack_size
    print(stack_size)
    for cdef in module["content_definitions"]:
        data = cdef['data']
        cdef_offset = cdef['offset']
        if cdef["seg_id"] == CODE_SEGMENT:
            for (seg_id, lhb), offsets in cdef.get('internal', {}).items():
                for offset in offsets:
                    if seg_id == CODE_SEGMENT:
                        add16(data, offset-cdef_offset, code_start)
                    elif seg_id == DATA_SEGMENT or seg_id == STACK_SEGMENT:
                        add16(data, offset-cdef_offset, data_start)
                    else:
                        error("module adjust: unknown segment")
    # do not adjust cdef['offset']: it represents the offset
    # from the beginning of the segment

# insert arr2 into arr1 at offset
# if needed, insert zeros
# if needed, extend arr1
def add_at(arr1, offset, arr2):
    offs_end = offset + len(arr2)
    if len(arr1) < offs_end:
        arr1 += bytearray([0] * (offs_end - len(arr1)))
    arr1[offset:offs_end] = arr2

def module_to_bin(module):
    code = bytearray()
    stack = bytearray(module["segments"][STACK_SEGMENT]["seg_length"])
    print(len(stack))
    data = bytearray()
    for cdef in module["content_definitions"]:
        if cdef["seg_id"] == CODE_SEGMENT:
            add_at(code, cdef["offset"], cdef["data"])
        elif cdef["seg_id"] == DATA_SEGMENT:
            add_at(data, cdef["offset"], cdef["data"])
    if len(data) == 0:
        return code
    else:
        return code + stack + data
