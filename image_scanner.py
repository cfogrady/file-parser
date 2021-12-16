import pygame
import config

# This method scales to 32-bit color (8-bit per R/G/B value)
def scale_to_8_bit_color_value(colorByte, bitsPerColor, colorValue='Unknown'):
    fullColor = int((int(colorByte) * 255) / (2 ** bitsPerColor - 1))
    #print('Converting ' + colorValue + ' byte ' + str(colorByte) + ' with int value of ' + str(
    #    int(colorByte)) + ' to fullColor int of ' + str(fullColor) + ' having byte ' + str(
    #    fullColor.to_bytes(1, 'big')))
    return fullColor.to_bytes(1, 'little')[0]

def formatHCPixels(bytes, pixel_count):
    # RRRRRGGG GGGBBBBB
    newBytes = [0x00] * (pixel_count * 3)
    for i in range(0, len(bytes), 2):
        byte1 = bytes[i]
        byte2 = bytes[i+1]
        rBits = (byte1 & 0b11111000) >> 3
        gBits = ((byte1 & 0b00000111) << 3) | ((byte2 & 0b11100000) >> 5)
        bBits = byte2 & 0b00011111
        newBytesIndex = int(3 * i / 2)
        newBytes[newBytesIndex] = scale_to_8_bit_color_value(rBits, 5)
        newBytes[newBytesIndex + 1] = scale_to_8_bit_color_value(gBits, 6)
        newBytes[newBytesIndex + 2] = scale_to_8_bit_color_value(bBits, 5)
    return bytearray(newBytes)

def formatHCR5G5B5Pixels(bytes, pixel_count):
    # RRRRRGGG GGBBBBBX
    newBytes = [0x00] * (pixel_count * 3)
    for i in range(0, len(bytes), 2):
        byte1 = bytes[i]
        byte2 = bytes[i + 1]
        rBits = (byte1 & 0b01111100) >> 3
        gBits = ((byte1 & 0b00000011) << 3) | ((byte2 & 0b11100000) >> 5)
        bBits = byte2 & 0b00011111
        newBytesIndex = int(3 * i / 2)
        newBytes[newBytesIndex] = scale_to_8_bit_color_value(rBits, 5)
        newBytes[newBytesIndex + 1] = scale_to_8_bit_color_value(gBits, 5)
        newBytes[newBytesIndex + 2] = scale_to_8_bit_color_value(bBits, 5)
    return bytearray(newBytes)

def formatHCR4G4B4Pixels(bytes, pixel_count):
    # RRRRGGGG BBBBXXXX
    newBytes = [0x00] * (pixel_count * 3)
    for i in range(0, len(bytes), 2):
        byte1 = bytes[i]
        byte2 = bytes[i + 1]
        rBits = (byte1 & 0b11110000) >> 4
        gBits = (byte2 & 0b00001111)
        bBits = (byte2 & 0b11110000) >> 4
        newBytesIndex = int(3 * i / 2)
        newBytes[newBytesIndex] = scale_to_8_bit_color_value(rBits, 4)
        newBytes[newBytesIndex + 1] = scale_to_8_bit_color_value(gBits, 4)
        newBytes[newBytesIndex + 2] = scale_to_8_bit_color_value(bBits, 4)
    return bytearray(newBytes)

class PixelFormat:
    formatTypes = ['P', 'RGB', 'BGR', 'RGBX', 'RGBA', 'ARGB', 'HC', 'HCR5G5B5', 'HCR4G4B4']
    modeBitsPerPixel = {'P': 1, 'RGB': 3, 'BGR': 3, 'RGBX': 4, 'RGBA': 4, 'ARGB': 4, 'HC': 2, 'HCR5G5B5': 2, 'HCR4G4B4': 2}
    nativeFormat = {'P': True, 'RGB': True, 'BGR': True, 'RGBX': True, 'RGBA': True, 'ARGB': True, 'HC': False, 'HCR5G5B5': False, 'HCR4G4B4': False}
    reformatRGBMethod = {'HC': formatHCPixels, 'HCR5G5B5': formatHCR5G5B5Pixels, 'HCR4G4B4': formatHCR4G4B4Pixels}


class ImageScanner:
    def __init__(self, file):
        self.file = file

    SCROLL_KEYS = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                       pygame.K_w, pygame.K_h, pygame.K_m, pygame.K_s, pygame.K_b, pygame.K_BACKQUOTE]

    def run_with_file(self):
        pygame.init()
        width, height = 80, 160
        scale = 1
        screen = pygame.display.set_mode((width * scale, height * scale))
        location = 0
        modeIdx = 4
        img = self.getSectionOfFile(location, (width, height), modeIdx)
        img = pygame.transform.scale(img, (width * scale, height * scale))
        parsing = True
        while parsing and self.file.readable():
            pygame.event.pump()
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN and event.key in ImageScanner.SCROLL_KEYS:
                increment = 1
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_LCTRL or mods & pygame.KMOD_CTRL:
                    increment = 10
                    print("CRTL Down")
                if mods & pygame.KMOD_LSHIFT or mods & pygame.KMOD_SHIFT:
                    increment = increment * -1
                    print("SHIFT Down")
                if event.key == pygame.K_m:
                    modeIdx = (modeIdx + increment) % len(PixelFormat.formatTypes)
                    print('Mode Index: ' + str(modeIdx))
                    print('Changed mode to ' + PixelFormat.formatTypes[modeIdx] + ' with ' + str(
                        PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[modeIdx]]) + 'bpp')
                if event.key == pygame.K_b:
                    if mods & pygame.KMOD_SHIFT or mods & pygame.KMOD_LSHIFT:
                        config.LITTLE_ENDIAN_BITS = not config.LITTLE_ENDIAN_BITS
                        print('Little Endian on bits: ' + str(config.LITTLE_ENDIAN_BITS))
                    else:
                        config.LITTLE_ENDIAN_BYTES = not config.LITTLE_ENDIAN_BYTES
                        print('Little Endian on bytes: ' + str(config.LITTLE_ENDIAN_BYTES))
                if event.key == pygame.K_BACKQUOTE:
                    config.APPLY_BITWISE_NOT = not config.APPLY_BITWISE_NOT
                    print('Bitwise Not Applied: ' + str(config.APPLY_BITWISE_NOT))
                if event.key == pygame.K_PAGEDOWN:
                    location = location + (PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[modeIdx]] * width * height * increment)
                if event.key == pygame.K_RIGHT:
                    location = location + increment
                if event.key == pygame.K_DOWN:
                    location = location + (PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[modeIdx]] * width * increment)
                if event.key == pygame.K_PAGEUP:
                    location = location - (PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[modeIdx]] * width * height * increment)
                if event.key == pygame.K_LEFT:
                    location = location - increment
                if event.key == pygame.K_UP:
                    location = location - (PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[modeIdx]] * width * increment)
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
                img = self.getSectionOfFile(location, (width, height), modeIdx)
                if img is not None:
                    img = pygame.transform.scale(img, (width * scale, height * scale))
                else:
                    img = lastImg
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                parsing = False
            screen.fill((0, 0, 0))
            screen.blit(img, img.get_rect())
            pygame.display.flip()
        pygame.quit()

    def getSectionOfFile(self, position, size, modeIdx):
        width = size[0]
        height = size[1]
        mode = PixelFormat.formatTypes[modeIdx]
        imageSize = width * height * PixelFormat.modeBitsPerPixel[mode]
        print("Reading next " + str(imageSize) + " bytes starting at location: " + hex(position))
        self.file.seek(position)
        imageBytes = self.file.read(imageSize)
        if len(imageBytes) < imageSize:
            print("Could not read bytes for full image. Only " + str(len(imageBytes)) + " bytes remained.")
            return None
        imageBytes = config.reverse_bytes_if_needed(imageBytes, PixelFormat.modeBitsPerPixel[mode])
        imageBytes = config.reverse_bits_if_needed(imageBytes)
        imageBytes = config.not_bits_if_needed(imageBytes)
        if not PixelFormat.nativeFormat[mode]:
            imageBytes = PixelFormat.reformatRGBMethod[mode](imageBytes, width*height)
            mode = 'RGB'
        print("Creating image from " + str(len(imageBytes)) + " byte array for " + mode + " " + str(width) + "x" + str(
            height))
        return pygame.image.frombuffer(imageBytes, (width, height), mode)