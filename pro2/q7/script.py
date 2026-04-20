from scipy.io import wavfile
import numpy as np
import string

# Read the wav file
rate, data = wavfile.read('main.wav')
print(rate,data) #2736 [2002 2507 2001 ... 7502 1001 6009]
print(len(data)) # 2736

# Map each sample to a hex digit (0-15)
# Formula: strip noise (//100), subtract 10, divide by 5
hex_indices = [(v // 100 - 10) // 5 for v in data]
#print(hex_indices) # [0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7, 0, 8, 0, 9, 0, 10, ...]

# Convert to hex string using Python's hexdigits
hex_str = "".join(string.hexdigits[i] for i in hex_indices)

# Decode hex string back to text
decoded = bytearray.fromhex(hex_str).decode('utf-8')
print(decoded)