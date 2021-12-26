# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse
from image_scanner import ImageScanner
from curses_scanner import CursesScanner

def main():
    parser = argparse.ArgumentParser(description='Attempts to parse files')
    parser.add_argument('fileName', help='name of file to parse')
    parser.add_argument("--pixels", help="Runs in GUI mode to display bytes as pixel data", action="store_true")
    args = parser.parse_args()
    fileName = args.fileName
    print('Attempting to parse file at: ' + fileName)
    with open(fileName, mode='rb') as file:
        running = True
        if args.pixels:
            scanner = ImageScanner(file)
        else:
            scanner = CursesScanner(file)
        while running:
            event = scanner.wait_for_event()
            running = scanner.handle_event(event)
        del scanner


if __name__ == '__main__':
    main()
