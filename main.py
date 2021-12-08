# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pygame
import argparse

def main():
    parser = argparse.ArgumentParser(description='Attempts to parse files')
    parser.add_argument('fileName', help='name of file to parse')
    args = parser.parse_args()
    fileName = args.fileName
    print('Attempting to parse file at: ' + fileName)
    parse_file(fileName)

def scaleTo8BitColor(colorByte, bitsPerColor):
    fullColor = int((int(colorByte) * 255) / (2**bitsPerColor-1))
    # print('Converting byte ' + str(colorByte) + ' with int value of ' + str(int(colorByte)) + ' to fullColor int of ' + str(fullColor) + ' having byte ' + str(fullColor.to_bytes(1, 'big')))
    return fullColor.to_bytes(1, 'little')[0]

def getSectionOfFile(file, position, size, modeIdx):
    width = size[0]
    height = size[1]
    mode = Mode.modeTypes[modeIdx]
    imageSize = width * height * Mode.modeBitsPerPixel[mode]
    print("Reading next " + str(imageSize) + " bytes starting at location: " + hex(position))
    file.seek(position)
    imageBytes = file.read(imageSize)
    if mode == 'HC':
        newBytes = [0x00] * (width*height*3)
        for i in range(0, len(imageBytes), 2):
            # RRRRRGGG GGGBBBBB
            byte1 = imageBytes[i]
            byte2 = imageBytes[i+1]
            #print("Byte1: " + str(byte1) + " " + format(byte1, 'b'))
            #print("Byte2: " + str(byte2) + " " + format(byte2, 'b'))
            rBits = (byte1 & 0b11111000) >> 3
            gBits = ((byte1 & 0b00000111) << 3) | ((byte2 & 0b11100000) >> 5)
            bBits = byte2 & 0b00011111
            #print('Red bits ' + str(rBits))
            #print('Green bits ' + str(gBits))
            #print('Blue bits ' + str(bBits))
            newBytesIndex = int(3*i/2)
            newBytes[newBytesIndex] = 255 - scaleTo8BitColor(rBits, 5)
            newBytes[newBytesIndex+1] = 255 - scaleTo8BitColor(gBits, 6)
            newBytes[newBytesIndex+2] = 255 - scaleTo8BitColor(bBits, 5)
        imageBytes = bytearray(newBytes)
        mode = 'RGB'
    elif mode == 'HCR5G5B5':
        newBytes = [0x00] * (width * height * 3)
        for i in range(0, len(imageBytes), 2):
            # RRRRRGGG GGBBBBBX
            byte1 = imageBytes[i]
            byte2 = imageBytes[i + 1]
            #print("Byte1: " + str(byte1) + " " + format(byte1, 'b'))
            #print("Byte2: " + str(byte2) + " " + format(byte2, 'b'))
            rBits = (byte1 & 0b01111100) >> 3
            gBits = ((byte1 & 0b00000011) << 3) | ((byte2 & 0b11100000) >> 5)
            bBits = byte2 & 0b00011111
            #print('Red bits ' + str(rBits))
            #print('Green bits ' + str(gBits))
            #print('Blue bits ' + str(bBits))
            newBytesIndex = int(3 * i / 2)
            newBytes[newBytesIndex] = 255 - scaleTo8BitColor(rBits, 5)
            newBytes[newBytesIndex + 1] = 255 - scaleTo8BitColor(gBits, 5)
            newBytes[newBytesIndex + 2] = 255 - scaleTo8BitColor(bBits, 5)
        imageBytes = bytearray(newBytes)
        mode = 'RGB'
    elif mode == 'HCR4G4B4':
        newBytes = [0x00] * (width * height * 3)
        for i in range(0, len(imageBytes), 2):
            # RRRRGGGG BBBBXXXX
            byte1 = imageBytes[i]
            byte2 = imageBytes[i + 1]
            #print("Byte1: " + str(byte1) + " " + format(byte1, 'b'))
            #print("Byte2: " + str(byte2) + " " + format(byte2, 'b'))
            rBits = (byte1 & 0b11110000) >> 4
            gBits = (byte2 & 0b00001111)
            bBits = (byte2 & 0b11110000) >> 4
            #print('Red bits ' + str(rBits))
            #print('Green bits ' + str(gBits))
            #print('Blue bits ' + str(bBits))
            newBytesIndex = int(3 * i / 2)
            newBytes[newBytesIndex] = 255 - scaleTo8BitColor(rBits, 4)
            newBytes[newBytesIndex + 1] = 255 - scaleTo8BitColor(gBits, 4)
            newBytes[newBytesIndex + 2] = 255 - scaleTo8BitColor(bBits, 4)
        imageBytes = bytearray(newBytes)
        mode = 'RGB'
    if len(imageBytes) < imageSize:
        print("Could not read bytes for full image. Only " + str(len(imageBytes)) + " bytes remained.")
        return None
    print("Creating image from " + str(len(imageBytes)) + " byte array for " + mode + " " + str(width) + "x" + str(height))
    return pygame.image.frombuffer(imageBytes, (width, height), mode)

SCROLL_KEYS = [ pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_w, pygame.K_h, pygame.K_m, pygame.K_s ]

class Mode:
    modeTypes = ['P', 'RGB', 'BGR', 'RGBX', 'RGBA', 'ARGB', 'HC', 'HCR5G5B5', 'HCR4G4B4']
    modeBitsPerPixel = {'P': 1, 'RGB': 3, 'BGR': 3, 'RGBX': 4, 'RGBA': 4, 'ARGB': 4, 'HC': 2, 'HCR5G5B5': 2, 'HCR4G4B4': 2}

def parse_file(fileName):
    pygame.init()
    width, height = 80, 160
    scale = 1
    screen = pygame.display.set_mode((width * scale, height * scale))
    with open(fileName, mode='rb') as file:
        location = 0
        modeIdx = 4
        img = getSectionOfFile(file, location, (width, height), modeIdx)
        img = pygame.transform.scale(img, (width * scale, height * scale))
        parsing = True
        while parsing and file.readable():
            pygame.event.pump()
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN and event.key in SCROLL_KEYS:
                increment = 1
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_LCTRL or mods & pygame.KMOD_CTRL:
                    increment = 10
                    print("CRTL Down")
                if mods & pygame.KMOD_LSHIFT or mods & pygame.KMOD_SHIFT:
                    increment = increment * -1
                    print("SHIFT Down")
                if event.key == pygame.K_m:
                    modeIdx = (modeIdx + increment) % len(Mode.modeTypes)
                    print('Mode Index: ' + str(modeIdx))
                    print('Changed mode to ' + Mode.modeTypes[modeIdx] + ' with ' + str(Mode.modeBitsPerPixel[Mode.modeTypes[modeIdx]]) + 'bpp')
                if event.key == pygame.K_PAGEDOWN:
                    location = location + (Mode.modeBitsPerPixel[Mode.modeTypes[modeIdx]] * width * height)
                if event.key == pygame.K_RIGHT:
                    location = location + increment
                if event.key == pygame.K_DOWN:
                    location = location + (Mode.modeBitsPerPixel[Mode.modeTypes[modeIdx]] * width * increment)
                if event.key == pygame.K_PAGEUP:
                    location = location - (Mode.modeBitsPerPixel[Mode.modeTypes[modeIdx]] * width * height)
                if event.key == pygame.K_LEFT:
                    location = location - increment
                if event.key == pygame.K_UP:
                    location = location - (Mode.modeBitsPerPixel[Mode.modeTypes[modeIdx]] * width * increment)
                if event.key == pygame.K_w:
                    width = width + increment
                    screen = pygame.display.set_mode((width * scale, height * scale))
                    print("New Size: Width: " + str(width) + ", Height:" + str(height))
                if event.key == pygame.K_s:
                    scale = scale + increment
                    if scale < 1:
                        scale = 1
                    screen = pygame.display.set_mode((width * scale, height * scale))
                if event.key == pygame.K_h:
                    height = height + increment
                    screen = pygame.display.set_mode((width * scale, height * scale))
                    print("New Size: Width: " + str(width) + ", Height:" + str(height))
                if location < 0:
                    location = 0
                lastImg = img
                img = getSectionOfFile(file, location, (width, height), modeIdx)
                if img is not None:
                    img = pygame.transform.scale(img, (width*scale, height*scale))
                else:
                    img = lastImg
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                parsing = False
            screen.fill((0, 0, 0))
            screen.blit(img, img.get_rect())
            pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
