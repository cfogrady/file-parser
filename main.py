# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse
from image_scanner import ImageScanner
import config

def main():
    parser = argparse.ArgumentParser(description='Attempts to parse files')
    parser.add_argument('fileName', help='name of file to parse')
    args = parser.parse_args()
    fileName = args.fileName
    print('Attempting to parse file at: ' + fileName)
    with open(fileName, mode='rb') as file:
        scanner = ImageScanner(file)
        scanner.run_with_file()

if __name__ == '__main__':
    main()
