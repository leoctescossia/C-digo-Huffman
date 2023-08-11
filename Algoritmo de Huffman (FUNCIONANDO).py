import os
from collections import defaultdict

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

class HuffmanTree:
    def __init__(self, char_freq_map):
        self.char_freq_map = char_freq_map
        self.root = self.build_tree()

    def build_tree(self):
        nodes = [HuffmanNode(char, freq) for char, freq in self.char_freq_map.items()]

        while len(nodes) > 1:
            nodes.sort(key=lambda node: node.freq)

            left = nodes.pop(0)
            right = nodes.pop(0)

            merged_node = HuffmanNode(None, left.freq + right.freq)
            merged_node.left = left
            merged_node.right = right

            nodes.append(merged_node)

        return nodes[0]

    def build_codes(self, node=None, code="", codes=None):
        if codes is None:
            codes = {}

        if node is None:
            node = self.root

        if node.char:
            codes[node.char] = code
        else:
            self.build_codes(node.left, code + "0", codes)
            self.build_codes(node.right, code + "1", codes)

        return codes


class UernZip:
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.char_freq_map = self.count_characters()
        self.huffman_tree = HuffmanTree(self.char_freq_map)
        self.codes = self.huffman_tree.build_codes()

   
    def count_characters(self):
        char_freq_map = {}

        with open(self.input_file_path, "r", encoding="ISO-8859-1") as file:
            content = file.read()
            for char in content:
                char_freq_map[char] = char_freq_map.get(char, 0) + 1

        return char_freq_map

    def compress(self, output_file_path):
        with open(output_file_path, "wb") as output_file:
            # Calculate number of different characters
            num_characters = len(self.codes)

            # Write number of different characters (8 bits)
            output_file.write(num_characters.to_bytes(1, byteorder="big"))

            # Write character codes and their sizes
            for char, code in self.codes.items():
                ascii_char = ord(char)
                code_size = len(code)

                # Write ASCII code of character (8 bits)
                output_file.write(ascii_char.to_bytes(1, byteorder="big"))

                # Write code size (4 bits)
                output_file.write(code_size.to_bytes(1, byteorder="big"))

                # Write code
                code_byte = int(code, 2)
                code_bytes_length = (code_size + 7) // 8
                output_file.write(code_byte.to_bytes(code_bytes_length, byteorder="big"))

            # Encode and write the content using the codes
            encoded_content = self.encode_content()
            bits_padding = 8 - len(encoded_content) % 8
            encoded_content += "0" * bits_padding
            encoded_content_bytes = bytes([int(encoded_content[i:i + 8], 2) for i in range(0, len(encoded_content), 8)])
            output_file.write(encoded_content_bytes)

    def encode_content(self):
        content = open(self.input_file_path, "r", encoding="ISO-8859-1").read()
        encoded_content = "".join(self.codes[char] for char in content)
        return encoded_content


class UernUnzip:
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.codes = {}
        self.encoded_content = b""
        self.num_characters = 0

    def read_codes(self):
        with open(self.input_file_path, "rb") as input_file:
            # Read number of different characters (8 bits)
            num_characters = int.from_bytes(input_file.read(1), byteorder="big")

            for _ in range(num_characters):
                # Read ASCII code of character (8 bits)
                ascii_char = int.from_bytes(input_file.read(1), byteorder="big")

                # Read code size (4 bits)
                code_size = int.from_bytes(input_file.read(1), byteorder="big")

                # Read code
                code_bytes_length = (code_size + 7) // 8
                code_byte = int.from_bytes(input_file.read(code_bytes_length), byteorder="big")
                binary_code = bin(code_byte)[2:].rjust(code_size, "0")

                char = chr(ascii_char)
                self.codes[binary_code] = char

            # Read the encoded content
            self.encoded_content = input_file.read()

    def decompress(self, output_file_path):
        self.read_codes()

        current_code = ""
        decoded_content = []

        for byte in self.encoded_content:
            current_byte = format(byte, '08b')

            for bit in current_byte:
                current_code += bit

                if current_code in self.codes:
                    decoded_content.append(self.codes[current_code])
                    current_code = ""

        # Convert the decoded characters to a string before writing to the file
        decoded_content_str = "".join(decoded_content)

        # Remove the last 2 characters
        decoded_content_str = decoded_content_str[:-2]

        with open(output_file_path, "wb") as output_file:
            output_file.write(decoded_content_str.encode("ISO-8859-1"))


def count_characters(file_path):
    character_count = defaultdict(int)

    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            for char in line:
                character_count[char] += 1

    return character_count

def show_binary_representation(character_count):
    for char, count in character_count.items():
        char_ascii = ord(char)
        binary_representation = bin(char_ascii)[2:].zfill(8)
        print(f"'{char}': {count} ({binary_representation})")



# Example usage:

# Compactação:
input_file_path = "poesias-margareth.txt"
output_file_path = "poesias-margareth.uzip"

character_count = count_characters(input_file_path)

uern_zip = UernZip(input_file_path)
uern_zip.compress(output_file_path)

# Mostrar tamanhos dos arquivos
original_size = os.path.getsize(input_file_path)
compacted_size = os.path.getsize(output_file_path)
print("\nTamanho do arquivo original:", original_size, "bytes")
print("Tamanho do arquivo compactado:", compacted_size, "bytes")

# Descompactação:
input_file_path = "poesias-margareth.uzip"
output_file_path_decompressed = "poesias-margareth-decompressed.txt"

uern_unzip = UernUnzip(input_file_path)
uern_unzip.decompress(output_file_path_decompressed)

# Mostrar tamanho do arquivo descompactado
decompressed_size = os.path.getsize(output_file_path_decompressed)
print("Tamanho do arquivo descompactado:", decompressed_size, "bytes")

# Mostrar representação binária dos caracteres ao lado da contagem
print("\nRepresentação binária dos caracteres:")
show_binary_representation(character_count)