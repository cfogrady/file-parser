LITTLE_ENDIAN_BYTES = True
LITTLE_ENDIAN_BITS = True
APPLY_BITWISE_NOT = False

def reverse_bytes_if_needed(bytes, bytes_per_group):
    new_bytes = [0x00] * len(bytes)
    if not LITTLE_ENDIAN_BYTES and bytes_per_group > 1:
        for i in range(0, len(bytes), bytes_per_group):
            for k in range(0, bytes_per_group):
                new_bytes[i+k] = bytes[i+(bytes_per_group-1-k)]
        return bytearray(new_bytes)
    return bytes

def reverse_bits_if_needed(bytes):
    new_bytes = [0x00] * len(bytes)
    if not LITTLE_ENDIAN_BITS:
        for i in range(0, len(bytes)):
            new_bytes[i] = reverseBits(bytes[i])
        return bytearray(new_bytes)
    return bytes

def not_bits_if_needed(bytes):
    new_bytes = [0x00] * len(bytes)
    if APPLY_BITWISE_NOT:
        for i in range(0, len(bytes)):
            new_bytes[i] = ~bytes[i] & 0xff # Force 8-bit
        return bytearray(new_bytes)
    return bytes

def reverseBits(byte):
    bits = bin(byte)
    # print(bits)
    reverse = bits[-1: 1: -1]
    reverse = reverse + (8 - len(reverse)) * '0'
    # print(reverse)
    # print(int(reverse, 2))
    return int(reverse, 2)