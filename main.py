# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse
from curses_scanner import CursesScanner
import traceback


def get_scanner(file, use_image):
    if use_image:
        from image_scanner import ImageScanner
        return ImageScanner(file)
    else:
        return CursesScanner(file)


def main():
    parser = argparse.ArgumentParser(description='Attempts to parse files')
    parser.add_argument('fileName', help='name of file to parse')
    parser.add_argument("--pixels", help="Runs in GUI mode to display bytes as pixel data", action="store_true")
    args = parser.parse_args()
    fileName = args.fileName
    print('Attempting to parse file at: ' + fileName)
    with open(fileName, mode='rb') as file:
        running = True
        with get_scanner(file, args.pixels) as scanner:
            scanner.get_section_of_file()
            while running:
                event = scanner.wait_for_event()
                running = scanner.handle_event(event)


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()


