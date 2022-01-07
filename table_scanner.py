import config

def bytes_have_data(bytes):
    has_data = False
    for byte_idx in range(0, len(bytes)):
        if bytes[byte_idx] != 0:
            has_data = True
    return has_data

def output_table(file):
    bitewise_input = input("Apply Bitwise NOT? Y/N: ")
    config.APPLY_BITWISE_NOT = True if bitewise_input == 'Y' else False
    endianess_input = input("Little Endian? Y/N: ")
    endianess_type = 'big' if endianess_input == 'N' else 'little'
    columns_str = input("Number of expected columns? ")
    columns = int(columns_str)
    column_definitions = [None]*columns
    offset_str = input("Offset from start of file? ")
    file_offset = int(offset_str, 0) if offset_str.startswith('0x') else int(offset_str)
    row_size = 0
    for column_idx in range(0, columns):
        size = int(input("Number of bytes for column " + str(column_idx+1) + "? "))
        row_size += size
        as_hex = True if input("Output as hex? Y/N: ") == 'Y' else False
        column_definitions[column_idx] = (size, as_hex)
    rows_to_read = int(input("How many rows should be read? "))
    rows_idx = 0
    data_remaining = True
    file.seek(file_offset)
    while rows_idx < rows_to_read or (rows_to_read == 0 and data_remaining):
        file_bytes = file.read(row_size)
        file_bytes = config.not_bits_if_needed(file_bytes)
        if rows_to_read == 0 and not bytes_have_data(file_bytes):
            data_remaining = False
        if data_remaining:
            line = ''
            offset = 0
            for column_idx in range(0, columns):
                as_hex = column_definitions[column_idx][1]
                size = column_definitions[column_idx][0]
                col_bytes = bytearray(size)
                for i in range(0, size):
                    col_bytes[i] = file_bytes[offset + i]
                value = int.from_bytes(col_bytes, byteorder=endianess_type, signed=False)
                if as_hex:
                    line = line + hex(value)
                else:
                    line = line + str(value)
                line = line + ','
                offset += size
            print(line)
            rows_idx += 1


