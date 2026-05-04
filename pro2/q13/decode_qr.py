import re
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode

# SVG path data - copy this from your assignment portal page source
# Right click on QR code → Inspect Element → find the <path d="..."> tag
# Copy everything inside d="..."
svg_path = """M56,56h14v14h-14z M70,56h14v14h-14z M84,56h14v14h-14z M98,56h14v14h-14z M112,56h14v14h-14z M126,56h14v14h-14z M140,56h14v14h-14z M168,56h14v14h-14z M182,56h14v14h-14z M252,56h14v14h-14z M266,56h14v14h-14z M280,56h14v14h-14z M294,56h14v14h-14z M308,56h14v14h-14z M322,56h14v14h-14z M336,56h14v14h-14z M56,70h14v14h-14z M140,70h14v14h-14z M210,70h14v14h-14z M252,70h14v14h-14z M336,70h14v14h-14z M56,84h14v14h-14z M84,84h14v14h-14z M98,84h14v14h-14z M112,84h14v14h-14z M140,84h14v14h-14z M224,84h14v14h-14z M252,84h14v14h-14z M280,84h14v14h-14z M294,84h14v14h-14z M308,84h14v14h-14z M336,84h14v14h-14z M56,98h14v14h-14z M84,98h14v14h-14z M98,98h14v14h-14z M112,98h14v14h-14z M140,98h14v14h-14z M168,98h14v14h-14z M196,98h14v14h-14z M210,98h14v14h-14z M224,98h14v14h-14z M252,98h14v14h-14z M280,98h14v14h-14z M294,98h14v14h-14z M308,98h14v14h-14z M336,98h14v14h-14z M56,112h14v14h-14z M84,112h14v14h-14z M98,112h14v14h-14z M112,112h14v14h-14z M140,112h14v14h-14z M182,112h14v14h-14z M196,112h14v14h-14z M210,112h14v14h-14z M224,112h14v14h-14z M252,112h14v14h-14z M280,112h14v14h-14z M294,112h14v14h-14z M308,112h14v14h-14z M336,112h14v14h-14z M56,126h14v14h-14z M140,126h14v14h-14z M210,126h14v14h-14z M224,126h14v14h-14z M252,126h14v14h-14z M336,126h14v14h-14z M56,140h14v14h-14z M70,140h14v14h-14z M84,140h14v14h-14z M98,140h14v14h-14z M112,140h14v14h-14z M126,140h14v14h-14z M140,140h14v14h-14z M168,140h14v14h-14z M196,140h14v14h-14z M224,140h14v14h-14z M252,140h14v14h-14z M266,140h14v14h-14z M280,140h14v14h-14z M294,140h14v14h-14z M308,140h14v14h-14z M322,140h14v14h-14z M336,140h14v14h-14z M182,154h14v14h-14z M196,154h14v14h-14z M224,154h14v14h-14z M84,168h14v14h-14z M112,168h14v14h-14z M126,168h14v14h-14z M140,168h14v14h-14z M168,168h14v14h-14z M182,168h14v14h-14z M196,168h14v14h-14z M210,168h14v14h-14z M224,168h14v14h-14z M238,168h14v14h-14z M294,168h14v14h-14z M336,168h14v14h-14z M70,182h14v14h-14z M84,182h14v14h-14z M112,182h14v14h-14z M168,182h14v14h-14z M224,182h14v14h-14z M266,182h14v14h-14z M308,182h14v14h-14z M322,182h14v14h-14z M336,182h14v14h-14z M56,196h14v14h-14z M84,196h14v14h-14z M112,196h14v14h-14z M126,196h14v14h-14z M140,196h14v14h-14z M168,196h14v14h-14z M182,196h14v14h-14z M196,196h14v14h-14z M210,196h14v14h-14z M224,196h14v14h-14z M238,196h14v14h-14z M252,196h14v14h-14z M280,196h14v14h-14z M294,196h14v14h-14z M308,196h14v14h-14z M322,196h14v14h-14z M336,196h14v14h-14z M56,210h14v14h-14z M154,210h14v14h-14z M168,210h14v14h-14z M182,210h14v14h-14z M210,210h14v14h-14z M252,210h14v14h-14z M280,210h14v14h-14z M322,210h14v14h-14z M336,210h14v14h-14z M56,224h14v14h-14z M70,224h14v14h-14z M112,224h14v14h-14z M126,224h14v14h-14z M140,224h14v14h-14z M210,224h14v14h-14z M224,224h14v14h-14z M238,224h14v14h-14z M252,224h14v14h-14z M266,224h14v14h-14z M280,224h14v14h-14z M322,224h14v14h-14z M336,224h14v14h-14z M168,238h14v14h-14z M182,238h14v14h-14z M266,238h14v14h-14z M280,238h14v14h-14z M294,238h14v14h-14z M308,238h14v14h-14z M336,238h14v14h-14z M56,252h14v14h-14z M70,252h14v14h-14z M84,252h14v14h-14z M98,252h14v14h-14z M112,252h14v14h-14z M126,252h14v14h-14z M140,252h14v14h-14z M182,252h14v14h-14z M210,252h14v14h-14z M224,252h14v14h-14z M238,252h14v14h-14z M252,252h14v14h-14z M266,252h14v14h-14z M280,252h14v14h-14z M308,252h14v14h-14z M336,252h14v14h-14z M56,266h14v14h-14z M140,266h14v14h-14z M168,266h14v14h-14z M182,266h14v14h-14z M196,266h14v14h-14z M210,266h14v14h-14z M238,266h14v14h-14z M336,266h14v14h-14z M56,280h14v14h-14z M84,280h14v14h-14z M98,280h14v14h-14z M112,280h14v14h-14z M140,280h14v14h-14z M168,280h14v14h-14z M210,280h14v14h-14z M224,280h14v14h-14z M252,280h14v14h-14z M308,280h14v14h-14z M322,280h14v14h-14z M336,280h14v14h-14z M56,294h14v14h-14z M84,294h14v14h-14z M98,294h14v14h-14z M112,294h14v14h-14z M140,294h14v14h-14z M182,294h14v14h-14z M210,294h14v14h-14z M224,294h14v14h-14z M252,294h14v14h-14z M294,294h14v14h-14z M322,294h14v14h-14z M56,308h14v14h-14z M84,308h14v14h-14z M98,308h14v14h-14z M112,308h14v14h-14z M140,308h14v14h-14z M168,308h14v14h-14z M182,308h14v14h-14z M210,308h14v14h-14z M238,308h14v14h-14z M252,308h14v14h-14z M266,308h14v14h-14z M280,308h14v14h-14z M294,308h14v14h-14z M308,308h14v14h-14z M336,308h14v14h-14z M56,322h14v14h-14z M140,322h14v14h-14z M182,322h14v14h-14z M196,322h14v14h-14z M252,322h14v14h-14z M280,322h14v14h-14z M322,322h14v14h-14z M56,336h14v14h-14z M70,336h14v14h-14z M84,336h14v14h-14z M98,336h14v14h-14z M112,336h14v14h-14z M126,336h14v14h-14z M140,336h14v14h-14z M182,336h14v14h-14z M196,336h14v14h-14z M210,336h14v14h-14z M238,336h14v14h-14z M266,336h14v14h-14z M322,336h14v14h-14z M336,336h14v14h-14z"""

# Step 1: Parse all (x,y) coordinates from SVG path
coords = re.findall(r'M(\d+),(\d+)h14v14h-14z', svg_path)
print(f"Found {len(coords)} black modules in SVG")

# Step 2: Build 21x21 grid
# SVG starts at pixel 56, each module is 14 pixels wide
g = np.zeros((21, 21), dtype=int)
for x_str, y_str in coords:
    x, y = int(x_str), int(y_str)
    col = (x - 56) // 14
    row = (y - 56) // 14
    if 0 <= row < 21 and 0 <= col < 21:
        g[row][col] = 1

# Print the grid visually
print("\n21x21 QR Grid (█=black, .=white):")
for i, row in enumerate(g):
    #print(i,row) #0 [1 1 1 1 1 1 1 0 1 1 0 0 0 0 1 1 1 1 1 1 1]

    print(f"{i:2d}: " + ''.join('█' if x==1 else '.' for x in row))

# Step 3: Build a clean scannable image from the grid
scale = 20        # each module = 20x20 pixels in output image
qz = 4 * scale    # quiet zone = 4 modules of white border around QR
size = 21 * scale + 2 * qz

img_out = Image.new('RGB', (size, size), (255, 255, 255))
pixels = img_out.load()

for r in range(21):
    for c in range(21):
        color = (0, 0, 0) if g[r][c] == 1 else (255, 255, 255)
        for dr in range(scale):
            for dc in range(scale):
                pixels[qz + c*scale + dc, qz + r*scale + dr] = color

img_out.save('qr_reconstructed.png')
print("\nSaved clean QR image as qr_reconstructed.png")

# Step 4: Decode the QR code
result = decode(img_out)
if result:
    decoded_text = result[0].data.decode('utf-8')
    print(f"\n✅ DECODED 7 CHARACTERS: '{decoded_text}'")
    print(f"\nNow insert these into the masked signature:")
    masked = "aKKvsqLrrwj6pEjmhp9EHGkQ36Q-------Q7SFVv1BD8JfVjSDncdWNTWtqxkQrfT7GhHiSZ7CN6do8LQy2CACx"
    complete = masked.replace("-------", decoded_text)
    print(f"Complete signature: {complete}")
else:
    print("❌ Could not decode QR code")