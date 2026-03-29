
import json

with open('stego_image.json', 'r') as f:

    data = json.load(f)

bits = []
for row in data['pixels']:
    for pixel in row:
        for channel in pixel:  # R, G, B
            bits.append(channel & 1)  # Extract LSB (last bit)

message = ''
for i in range(0, 16 * 8, 8):   # 16 characters × 8 bits
    byte = bits[i:i+8]
    char = chr(int(''.join(map(str, byte)), 2))
    message += char

print(message)  # → 0d28049049e96974
# ```

# ### 🎯 Answer:
# ```
# 0d28049049e96974