import heapq
from collections import defaultdict
import os

class Node:
    def __init__(self, symbol, freq):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def count_frequencies(file_path):
    frequencies = defaultdict(int)
    with open(file_path, 'r', encoding='latin-1') as file:
        for line in file:
            for char in line:
                frequencies[char] += 1
    return frequencies

def build_huffman_tree(frequencies):
    heap = [Node(symbol, freq) for symbol, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left_child = heapq.heappop(heap)
        right_child = heapq.heappop(heap)

        new_node = Node(None, left_child.freq + right_child.freq)
        new_node.left = left_child
        new_node.right = right_child

        heapq.heappush(heap, new_node)

    return heap[0]

def traverse_tree(root, current_code="", codes={}):
    if root is not None:
        if root.symbol is not None:
            codes[root.symbol] = current_code
        traverse_tree(root.left, current_code + "0", codes)
        traverse_tree(root.right, current_code + "1", codes)

def write_compacted_file(file_path, output_path, codes):
    compacted_data = ""
    with open(file_path, 'r', encoding='latin-1') as file:
        for line in file:
            for char in line:
                compacted_data += codes[char]

    # Pad the compacted data to fill complete bytes
    padding_length = (8 - len(compacted_data) % 8) % 8
    compacted_data += "0" * padding_length

    # Convert the data to bytes and write to the output file
    compacted_bytes = bytes(int(compacted_data[i:i+8], 2) for i in range(0, len(compacted_data), 8))
    with open(output_path, 'wb') as output_file:
        output_file.write(bytes([len(codes)]))
        for char, code in codes.items():
            ascii_code = ord(char)
            code_length = len(code)
            output_file.write(bytes([ascii_code, code_length]))
            output_file.write(int(code, 2).to_bytes((code_length + 7) // 8, byteorder='big'))
        output_file.write(compacted_bytes)

def huffman_compress(file_path, output_path):
    frequencies = count_frequencies(file_path)
    huffman_tree = build_huffman_tree(frequencies)
    codes = {}
    traverse_tree(huffman_tree, "", codes)
    write_compacted_file(file_path, output_path, codes)

if __name__ == "__main__":
    input_file_path = "C:/Users/Windows/Desktop/Codigos/Código gerenciador de arquivos/Código Huffman/curvas-e-retas.txt"

    output_file_path = "output.uzip"

    huffman_compress(input_file_path, output_file_path)

    original_size = os.path.getsize(input_file_path)
    compacted_size = os.path.getsize(output_file_path)
    compression_ratio = original_size / compacted_size

    print("Original file size:", original_size, "bytes")
    print("Compacted file size:", compacted_size, "bytes")
    print("Compression ratio:", compression_ratio)
