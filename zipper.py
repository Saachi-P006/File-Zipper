import heapq
import os

MAX_TREE_HT = 256

class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

codes = {}

def build_huffman_tree(data_list, freq_list):
    heap = [Node(data_list[i], freq_list[i]) for i in range(len(data_list))]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)
    return heap[0]

def generate_codes(node, current_code=""):
    if node is None:
        return
    if node.char is not None:
        codes[node.char] = current_code
    generate_codes(node.left, current_code + "0")
    generate_codes(node.right, current_code + "1")

def calc_freq(filename):
    freq = [0]*256
    with open(filename, "rb") as f:
        byte = f.read(1)
        while byte:
            freq[byte[0]] += 1
            byte = f.read(1)
    return freq

def compress_file(input_file, output_file):
    freq = calc_freq(input_file)
    data, f = [], []
    for i in range(256):
        if freq[i] > 0:
            data.append(i)
            f.append(freq[i])
    root = build_huffman_tree(data, f)
    global codes
    codes = {}
    generate_codes(root)

    with open(input_file, "rb") as fin, open(output_file, "wb") as fout:
        fout.write(len(data).to_bytes(2, 'big'))
        for i in range(len(data)):
            fout.write(bytes([data[i]]))
            fout.write(f[i].to_bytes(4, 'big'))
        buffer = 0
        bit_count = 0
        byte = fin.read(1)
        while byte:
            code = codes[byte[0]]
            for bit in code:
                buffer = (buffer << 1) | int(bit)
                bit_count += 1
                if bit_count == 8:
                    fout.write(bytes([buffer]))
                    buffer = 0
                    bit_count = 0
            byte = fin.read(1)
        if bit_count > 0:
            buffer <<= (8 - bit_count)
            fout.write(bytes([buffer]))

def decompress_file(input_file, output_file):
    with open(input_file, "rb") as fin, open(output_file, "wb") as fout:
        size = int.from_bytes(fin.read(2), 'big')
        data, f = [], []
        for _ in range(size):
            data.append(fin.read(1)[0])
            f.append(int.from_bytes(fin.read(4), 'big'))
        root = build_huffman_tree(data, f)
        current = root
        byte = fin.read(1)
        while byte:
            bits = f"{byte[0]:08b}"
            for bit in bits:
                current = current.right if bit == '1' else current.left
                if current.left is None and current.right is None:
                    fout.write(bytes([current.char]))
                    current = root
            byte = fin.read(1)
