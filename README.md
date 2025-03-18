# file-parser

This is a simple app to help search through binary data. It can show text, hex, characters, shorts, ints, signed, unsigned, big-endian, small-endian, etc.

## Run
1) pip -r requirements.txt
2) if running on a system other than windows skip to step 4
3) pip install windows-curses
4) python main.py /path/to/file

### Keys
* Up Arrow, Down Arrow, Page Up, and Page Down for navigation.
* Ctrl Page Up and Ctrl Page Down to skip 5 pages at a time.
* `o` to display the initial offset.
* ```` to display show the bitwise NOT values.
* `b` to toggle big-endian vs little-endian.
* `z` to skip rows with no data (0 value bytes)
* `w` to toggle 8 vs 16 bytes per rows
* `h` to toggle hex
* `t` to toggle text
* `m` and `M` to go between column data sizes (UINT8, UINT16, UINT32)

