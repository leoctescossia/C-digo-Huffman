from heapq import heappush, heappop, heapify
from collections import defaultdict
import struct
import os

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def count_characters(file_path):
    character_count = defaultdict(int)

    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            for char in line:
                character_count[char] += 1

    return character_count

def build_huffman_tree(character_count):
    priority_queue = [Node(char, freq) for char, freq in character_count.items()]
    heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heappop(priority_queue)
        right = heappop(priority_queue)

        merged = Node(None, left.freq + right.freq)
        merged.left, merged.right = left, right
        heappush(priority_queue, merged)

    return priority_queue[0]

def build_huffman_codes(root, current_code="", codes={}):
    if root is None:
        return

    if root.char is not None:
        codes[root.char] = current_code
        return

    build_huffman_codes(root.left, current_code + "0", codes)
    build_huffman_codes(root.right, current_code + "1", codes)

def write_uzip_file(original_text, codes, output_file):
    header_format = 'B'
    header_size = struct.calcsize(header_format)

    with open(output_file, 'wb') as f:
        char_count = len(codes)
        f.write(struct.pack(header_format, char_count))

        for char, code in codes.items():
            char_ascii = ord(char)
            code_size = len(code)
            header_data = struct.pack('BB', char_ascii, code_size)
            f.write(header_data)
            f.write(int(code, 2).to_bytes((code_size + 7) // 8, byteorder='big'))

        # Convert the encoded text to bytes
        encoded_text_bytes = int(original_text, 2).to_bytes((len(original_text) + 7) // 8, byteorder='big')
        f.write(encoded_text_bytes)

def read_uzip_file(file_path):
    header_format = 'B'
    header_size = struct.calcsize(header_format)

    with open(file_path, 'rb') as f:
        char_count_bytes = f.read(header_size)
        char_count = struct.unpack(header_format, char_count_bytes)[0]

        codes = {}
        for _ in range(char_count):
            char_ascii, code_size = struct.unpack('BB', f.read(2))
            code_bytes = f.read((code_size + 7) // 8)
            code = ''.join(bin(byte)[2:].zfill(8) for byte in code_bytes)[:code_size]
            codes[chr(char_ascii)] = code

        # Convert the remaining bits of the file to binary string
        remaining_bits = f.read()
        encoded_text = ''.join(bin(byte)[2:].zfill(8) for byte in remaining_bits)

    return codes, encoded_text

def huffman_decoding(encoded_text, root):
    if not encoded_text or not root:
        return ""

    decoded_text = ""
    current_node = root

    for bit in encoded_text:
        if bit == "0":
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node.char is not None:
            decoded_text += current_node.char
            current_node = root

    return decoded_text


def show_binary_representation(character_count):
    for char, count in character_count.items():
        char_ascii = ord(char)
        binary_representation = bin(char_ascii)[2:].zfill(8)
        print(f"'{char}': {count} ({binary_representation})")

def get_file_size_in_bytes(file_path):
    return os.path.getsize(file_path)


if __name__ == "__main__":
    file_path = "poesias-margareth.txt"  # Substitua pelo caminho do seu arquivo de entrada
    character_count = count_characters(file_path)

    # Construir a árvore de Huffman a partir da contagem dos caracteres
    root = build_huffman_tree(character_count)

    # Construir a tabela de códigos binários para cada caractere
    codes = {}
    build_huffman_codes(root, "", codes)

    #print("Contagem de caracteres:")
    #for char, count in character_count.items():
      #  print(f"'{char}': {count}")

    contagem = len(character_count)
    #print("Total de caracteres diferentes:", contagem)

    # Codificar o texto original usando a tabela de códigos
    encoded_text = "".join(codes[char] for char in open(file_path, 'r', encoding='ISO-8859-1').read())

    # Escrever o arquivo compactado .uzip
    compacted_file = "arquivo.uzip"  # Substitua pelo nome do arquivo compactado de saída
    write_uzip_file(encoded_text, codes, compacted_file)
    print("\nArquivo compactado com sucesso!\n")

    # Ler o arquivo compactado
    codes, encoded_text = read_uzip_file(compacted_file)

    # Decode the encoded text using the Huffman tree
    decoded_text = huffman_decoding(encoded_text, root)

    # Escreva o arquivo descompactado
    output_file = "arquivo_descompactado.txt"  # Substitua pelo nome do arquivo de saída
    with open(output_file, 'w', encoding='ISO-8859-1') as f:
        f.write(decoded_text)

    print("\nArquivo descompactado com sucesso!\n")

    # Mostrar tamanhos dos arquivos
    original_size = get_file_size_in_bytes(file_path)
    compacted_size = get_file_size_in_bytes(compacted_file)
    decompressed_size = get_file_size_in_bytes(output_file)

    print("\nTamanho do arquivo original:", original_size, "bytes")
    print("\nTamanho do arquivo compactado:", compacted_size, "bytes")
    print("\nTamanho do arquivo descompactado:", decompressed_size, "bytes")

# Mostrar representação binária dos caracteres ao lado da contagem
    print("\nRepresentação binária dos caracteres:")
    show_binary_representation(character_count)

