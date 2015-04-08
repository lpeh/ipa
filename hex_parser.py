#! /usr/bin/env python3.3
# -*- coding: utf-8 -*-
"""
hex_parser - (will be) a simple tool to parse hex files
"""

import sys
import os

HEX_DATA = 0
HEX_EOF = 1
HEX_EXTENDED_SEGMENT_ADDRESS = 2
HEX_EXTENDED_LINEAR_ADDRESS = 4

hex_record_types = {
    HEX_DATA: 'data record',
    HEX_EOF: 'end of file record',
    HEX_EXTENDED_SEGMENT_ADDRESS: 'extended segment address',
    HEX_EXTENDED_LINEAR_ADDRESS: 'extended linear address'
}


class HexRecordError(Exception):
    """
    HexRecordError is raised if hex file cannot be parsed
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class HexRecord:
    def __init__(self):
        self.data_count = 0
        self.address = 0
        self.absolute_address = 0
        self.type = HEX_DATA
        self.data = []
        self.checksum = 0
        self.valid = False

    def print_type(self):
        if self.type in hex_record_types:
            print(hex_record_types[self.type])
        else:
            print("Unknown type {0}".format(self.type))


def get_hex_record_byte(record, n):
    """
    :param record: a single hex record, e.g. :00000001FF
    :param n: index
    :return: value
    """
    index = 1 + (n * 2)
    return int(record[index:index + 2], 16)


def get_hex_record_byte_count(record):
    return (len(record) - 1) // 2


def get_hex_record_data_count(record):
    return get_hex_record_byte(record, 0)


def get_hex_record_address(record):
    hi_byte = get_hex_record_byte(record, 1)
    lo_byte = get_hex_record_byte(record, 2)
    return (hi_byte << 8) + lo_byte


def get_hex_record_type(record):
    return get_hex_record_byte(record, 3)


def get_hex_record_data_byte(record, n):
    return get_hex_record_byte(record, 4 + n)


def get_hex_record_checksum(record):
    return int(record[-2:], 16)
    pass


def get_hex_record_data_content(record):
    byte_count = get_hex_record_byte_count(record) - 1

    data_content = []

    for n in range(0, byte_count):
        data_content.append(get_hex_record_byte(record, n))

    return bytearray(data_content)


def calculate_hex_record_checksum(record):
    byte_count = get_hex_record_byte_count(record) - 1

    checksum = 0

    for n in range(0, byte_count):
        checksum += get_hex_record_byte(record, n)
        checksum &= 0xff

    return (1 + (~checksum & 0xff)) & 0xff


def parse_hex_record(line):
    hex_record = HexRecord()

    line = line.strip()

    length = len(line)

    # minimum record length
    if length < 11:
        raise HexRecordError("Hex record too short (minimum length 11 bytes)")

    # length must be odd number
    if not length % 2 == 1:
        raise HexRecordError("Hex record length must be an odd number")

    # hex line begins with colon
    if line[0] != ':':
        raise HexRecordError("Hex record must begin with a colon")

    # parse data count
    data_count = get_hex_record_data_count(line)

    # data count must mach
    if length != (11 + data_count * 2):
        raise HexRecordError("Hex record data count does not mach actual content")

    # address
    address = get_hex_record_address(line)

    # type
    type = get_hex_record_type(line)

    # data
    data = get_hex_record_data_content(line)

    # checksum
    checksum = get_hex_record_checksum(line)
    calculated_checksum = calculate_hex_record_checksum(line)

    # checksum must match
    if checksum != calculated_checksum:
        raise HexRecordError(
            "Checksum does not mach: record={a}, calculated={b}".format(a=checksum, b=calculated_checksum))

    hex_record.data_count = data_count
    hex_record.address = address
    hex_record.type = type
    hex_record.data = data
    hex_record.checksum = checksum
    hex_record.valid = True

    return hex_record


def is_valid_hex_record(line):
    valid = False

    try:
        hex_record = parse_hex_record(line)
        valid = hex_record.valid
        hex_record.print_type()
    except HexRecordError as e:
        print(e)

    return valid


def read_hex_file(filename):
    try:
        with open(filename) as f:
            for line in f:
                if not is_valid_hex_record(line):
                    print(line.strip())
    except FileNotFoundError:
        print("File not found {0}".format(filename))
    except IsADirectoryError:
        print("{0} is a directory".format(filename))
    except:
        print("Error while reading file {0}".format(filename))


def main():
    if len(sys.argv) > 1:
        read_hex_file(sys.argv[1])
    else:
        print("{0} <filename>".format(os.path.basename(sys.argv[0])))


if __name__ == "__main__":
    main()