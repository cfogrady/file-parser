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
        self.location = 0
        self.mode_idx = 4
        self.width, self.height = 80, 160
        self.scale = 1
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
        self.img = self.getSectionOfFile(self.location, (self.width, self.height))
        self.img = pygame.transform.scale(self.img, (self.width * self.scale, self.height * self.scale))
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.img, self.img.get_rect())
        pygame.display.flip()

    def __del__(self):
        pygame.quit()

    SCROLL_KEYS = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                       pygame.K_w, pygame.K_h, pygame.K_m, pygame.K_s, pygame.K_b, pygame.K_BACKQUOTE]

    def wait_for_event(self):
        return pygame.event.wait()

    def handle_event(self, event):
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
                self.mode_idx = (self.mode_idx + increment) % len(PixelFormat.formatTypes)
                print('Mode Index: ' + str(self.mode_idx))
                print('Changed mode to ' + PixelFormat.formatTypes[self.mode_idx] + ' with ' + str(
                    PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[self.mode_idx]]) + 'bpp')
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
                self.location = self.location + (
                            PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[self.mode_idx]] * self.width * self.height * increment)
            if event.key == pygame.K_RIGHT:
                self.location = self.location + increment
            if event.key == pygame.K_DOWN:
                self.location = self.location + (
                            PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[self.mode_idx]] * self.width * increment)
            if event.key == pygame.K_PAGEUP:
                self.location = self.location - (
                            PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[self.mode_idx]] * self.width * self.height * increment)
            if event.key == pygame.K_LEFT:
                self.location = self.location - increment
            if event.key == pygame.K_UP:
                self.location = self.location - (
                            PixelFormat.modeBitsPerPixel[PixelFormat.formatTypes[self.mode_idx]] * self.width * increment)
            if event.key == pygame.K_w:
                self.width = self.width + increment
                self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
                print("New Size: Width: " + str(self.width) + ", Height:" + str(self.height))
            if event.key == pygame.K_s:
                self.scale = self.scale + increment
                if self.scale < 1:
                    self.scale = 1
                self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
            if event.key == pygame.K_h:
                self.height = self.height + increment
                self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
                print("New Size: Width: " + str(self.width) + ", Height:" + str(self.height))
            if self.location < 0:
                self.location = 0
            lastImg = self.img
            self.img = self.getSectionOfFile(self.location, (self.width, self.height))
            if self.img is not None:
                self.img = pygame.transform.scale(self.img, (self.width * self.scale, self.height * self.scale))
            else:
                self.img = lastImg
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return False
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.img, self.img.get_rect())
        pygame.display.flip()
        return True

    def getSectionOfFile(self, position, size):
        width = size[0]
        height = size[1]
        mode = PixelFormat.formatTypes[self.mode_idx]
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