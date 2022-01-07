# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse
import random

import config
from curses_scanner import CursesScanner
import traceback


def get_scanner(file, use_image, offset):
    offset = int(offset, 0) if offset.startswith('0x') else int(offset)
    if use_image:
        from image_scanner import ImageScanner
        return ImageScanner(file, offset)
    else:
        return CursesScanner(file, offset, calculate_checksum(file))


IGNORE = [0x10000, 0x10002, 0x10004, 0x10006, 0x3ffffe]


def calculate_checksum(file):
    bytes = file.read()
    config.APPLY_BITWISE_NOT = True
    bytes = config.not_bits_if_needed(bytes)
    config.APPLY_BITWISE_NOT = False
    file.seek(0)
    total = 0
    for i in range(0, len(bytes), 2):
        if i not in IGNORE:
            tmp_bytes = bytearray(2)
            tmp_bytes[0] = bytes[i]
            tmp_bytes[1] = bytes[i+1]
            total += int.from_bytes(tmp_bytes, byteorder='little', signed=False)
            total = total & 0xffff
    return int.from_bytes(total.to_bytes(2, 'big'), 'little')

def main():
    parser = argparse.ArgumentParser(description='Attempts to parse files')
    parser.add_argument('fileName', help='name of file to parse')
    parser.add_argument("--pixels", help="Runs in GUI mode to display bytes as pixel data", action="store_true")
    parser.add_argument("--table", help="Outputs a section of data in CSV format", action="store_true")
    parser.add_argument("--offset", type=str, default='0', help="Offset location to start reading from")
    args = parser.parse_args()
    fileName = args.fileName
    print('Attempting to parse file at: ' + fileName)
    with open(fileName, mode='rb') as file:
        if args.table:
            import table_scanner as TableScanner
            TableScanner.output_table(file)
        else:
            running = True
            with get_scanner(file, args.pixels, args.offset) as scanner:
                scanner.get_section_of_file()
                while running:
                    event = scanner.wait_for_event()
                    running = scanner.handle_event(event)


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()


