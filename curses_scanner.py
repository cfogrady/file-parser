import curses
import config
import os
from enum import Enum
import logging as log
log.basicConfig(filename='curses_scanner.log', encoding='utf-8', level=log.DEBUG)

# This method scales to 32-bit color (8-bit per R/G/B value)

KEY_ESCAPE = 27
KEY_CTRL_PAGE_DOWN = 551
KEY_CTRL_PAGE_UP = 556

class DisplayMode(Enum):
    UINT8 = 1, 1
    UINT16 = 2, 2
    UINT32 = 4, 4

DisplayModeOptions = [DisplayMode.UINT8, DisplayMode.UINT16, DisplayMode.UINT32]


class CursesScanner:
    def __init__(self, file):
        self.file = file
        self.escape_delay = os.environ.get('ESCDELAY')
        self.location = 0
        self.rows = []
        self.modeIdx = 0
        self.message = 'Initialized'
        self.width = 8
        self.height = 30
        self.skip_zeros = False
        self.show_hex = False
        self.offset = 0

    def __enter__(self):
        os.environ.setdefault('ESCDELAY', '0')
        self.window = curses.initscr()
        self.window.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        self.window.keypad(False)
        curses.endwin()
        os.environ.setdefault('ESCDELAY', self.escape_delay)
        print('Test exit')

    def __del__(self):
        print("test delete")

    def wait_for_event(self):
        return self.window.getch()

    def handle_event(self, event):
        self.message = 'Key: ' + str(event)
        if event == curses.KEY_DOWN:
            self.location = self.rows[1]
        elif event == curses.KEY_UP:
            self.location -= self.width
        elif event == curses.KEY_NPAGE:
            self.location = self.rows[self.height-1] + self.width
        elif event == KEY_CTRL_PAGE_DOWN:
            self.location += self.width*self.height * 5
        elif event == curses.KEY_PPAGE:
            self.location -= self.width*self.height
        elif event == KEY_CTRL_PAGE_UP:
            self.location -= self.width*self.height * 5
        elif event == ord('o'):
            self.offset = (self.offset + 1) % DisplayModeOptions[self.modeIdx].value[1]
            self.message = 'Offset set to ' + str(self.offset) + ' bytes'
        elif event == ord('`'):
            config.APPLY_BITWISE_NOT = not config.APPLY_BITWISE_NOT
        elif event == ord('b'):
            config.LITTLE_ENDIAN_BYTES = not config.LITTLE_ENDIAN_BYTES
            self.message = 'Little Byte Endianess: ' + str(config.LITTLE_ENDIAN_BYTES)
        elif event == ord('z'):
            self.skip_zeros = not self.skip_zeros
            self.message = 'Skip Zeros set to: ' + str(self.skip_zeros)
        elif event == ord('w'):
            if self.width == 16:
                self.width = 8
            else:
                self.width = 16
        elif event == ord('h'):
            self.show_hex = not self.show_hex
            self.message = 'Show hex set to: ' + str(self.show_hex)
        elif event == ord('m'):
            self.modeIdx = (self.modeIdx + 1) % len(DisplayModeOptions)
            self.message = 'Mode set to ' + DisplayModeOptions[self.modeIdx].name + ' with idx ' + str(self.modeIdx) + ' with ' + str(DisplayModeOptions[self.modeIdx].value[1]) + ' bytes.'
        elif event == ord('M') :
            self.modeIdx = (self.modeIdx - 1) % len(DisplayModeOptions)
            self.message = 'Mode set to ' + DisplayModeOptions[self.modeIdx].name + ' with idx ' + str(self.modeIdx) + ' with ' + str(DisplayModeOptions[self.modeIdx].value[1]) + ' bytes.'
        elif event == KEY_ESCAPE:
            return False
        if self.location < 0:
            self.location = 0
        self.get_section_of_file()
        return True

    def read_size_from_file(self, size):
        self.file.seek(self.location)
        self.rows = [None] * self.height
        byte_buffer = bytearray(size)
        skip = 0
        y = 0
        while y < self.height:
            file_bytes = self.file.read(self.width)
            all_zeros = True
            self.rows[y] = self.location + skip + self.width * y
            for x in range(0, self.width):
                byte = file_bytes[x]
                byte_buffer[y * self.width + x] = byte
                if config.APPLY_BITWISE_NOT:
                    byte = ~byte & 0xff
                if byte != 0:
                    all_zeros = False
            if all_zeros and self.skip_zeros:
                y -= 1
                skip = skip + self.width
            y += 1
        left_over_range = size - (self.width * self.height)
        for i in range(0, left_over_range):
            file_bytes = self.file.read(left_over_range)
            byte_buffer[self.width * self.height + i] = file_bytes[i]
        return byte_buffer

    def get_section_of_file(self):
        self.window.clear()
        # 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f
        word_size = DisplayModeOptions[self.modeIdx].value[1]
        size = self.width*self.height + (word_size-1)
        file_bytes = self.read_size_from_file(size)
        if len(file_bytes) < size:
            self.message = "Reached end of file at " + hex(self.location + len(file_bytes))

        file_bytes = config.reverse_bits_if_needed(file_bytes)
        file_bytes = config.not_bits_if_needed(file_bytes)
        byte_order = 'little' if config.LITTLE_ENDIAN_BYTES else 'big'

        byte_buffer = bytearray(word_size)

        self.window.addstr(0, 0, self.file.name)

        self.print_width_headers()
        self.print_height_left_side_headers()
        for i in range(0, word_size):
            byte_buffer[i] = file_bytes[i]
        for y in range(0, self.height):
            for x in range(0, int(self.width/word_size)):
                current_byte = y * self.width + x*word_size + self.offset
                for i in range(0, word_size):
                    if current_byte + i >= len(file_bytes):
                        byte_buffer[i] = 0
                    else:
                        byte_buffer[i] = file_bytes[current_byte + i]
                if current_byte + word_size - 1 < len(file_bytes):
                    if self.show_hex:
                        self.window.addstr(y + 4, x * 13 + 8,
                                           "| " + hex(int.from_bytes(byte_buffer, byteorder=byte_order, signed=False)))
                    else:
                        self.window.addstr(y+4, x*13+8, "| " + str(int.from_bytes(byte_buffer, byteorder=byte_order, signed=False)))
        self.window.addstr(1, 0, self.message)
        self.window.refresh()

    def print_height_left_side_headers(self):
        for i in range(0, len(self.rows)):
            self.window.addstr(i+4, 0, hex(self.rows[i]))

    def print_width_headers(self):
        dimensions = self.window.getmaxyx()
        word_size = DisplayModeOptions[self.modeIdx].value[1]
        for i in range(0, int(self.width / word_size)):
            header_str = "| " + hex(i * word_size + self.offset)
            if self.width == 8:
                header_str = header_str + "/" + hex(i*word_size+8 + self.offset)
            self.window.addstr(2, i * 13 + 8, header_str)
        for i in range(0, dimensions[1]):
            self.window.addch(3, i, '-')