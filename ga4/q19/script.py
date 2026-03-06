from PIL import Image

img = Image.open("jigsaw.webp").convert("RGBA")

width, height = img.size
grid = 5

tile_w = width / grid
tile_h = height / grid

tiles = {}

# extract scrambled tiles
for r in range(grid):
    for c in range(grid):

        box = (
            c * tile_w,
            r * tile_h,
            (c + 1) * tile_w,
            (r + 1) * tile_h
        )

        tiles[(r, c)] = img.crop(box)


mapping = {
(0,0):(2,1),(0,1):(1,1),(0,2):(4,1),(0,3):(0,3),(0,4):(0,1),
(1,0):(1,4),(1,1):(2,0),(1,2):(2,4),(1,3):(4,2),(1,4):(2,2),
(2,0):(0,0),(2,1):(3,2),(2,2):(4,3),(2,3):(3,0),(2,4):(3,4),
(3,0):(1,0),(3,1):(2,3),(3,2):(3,3),(3,3):(4,4),(3,4):(0,2),
(4,0):(3,1),(4,1):(1,2),(4,2):(1,3),(4,3):(0,4),(4,4):(4,0)
}

reconstructed = Image.new("RGBA", (width, height))

# place tiles
for (sr, sc), (orow, ocol) in mapping.items():

    tile = tiles[(sr, sc)]

    x = ocol * tile_w
    y = orow * tile_h

    reconstructed.paste(tile, (x, y))


pixels = reconstructed.load()

# grayscale conversion
for y in range(height):
    for x in range(width):

        r, g, b, a = pixels[x, y]

        gray = round(
            0.2126 * r +
            0.7152 * g +
            0.0722 * b
        )

        pixels[x, y] = (gray, gray, gray, a)  # keep alpha


reconstructed.save("answer.png")

# from PIL import Image
# import numpy as np

# # ── 1. Load scrambled image as RGBA (preserve alpha like the browser canvas does)
# img = Image.open("jigsaw.webp").convert("RGBA")
# width, height = img.size
# print(f"Image size: {width} x {height}")

# GRID = 5
# tile_w = width  // GRID
# tile_h = height // GRID
# print(f"Tile size:  {tile_w} x {tile_h}")

# # ── 2. Mapping: "scrambled_row,scrambled_col" → "original_row,original_col"
# #    Taken directly from the validator's Kt object
# Kt = {
#     "0,0": "2,1",
#     "0,1": "1,1",
#     "0,2": "4,1",
#     "0,3": "0,3",
#     "0,4": "0,1",
#     "1,0": "1,4",
#     "1,1": "2,0",
#     "1,2": "2,4",
#     "1,3": "4,2",
#     "1,4": "2,2",
#     "2,0": "0,0",
#     "2,1": "3,2",
#     "2,2": "4,3",
#     "2,3": "3,0",
#     "2,4": "3,4",
#     "3,0": "1,0",
#     "3,1": "2,3",
#     "3,2": "3,3",
#     "3,3": "4,4",
#     "3,4": "0,2",
#     "4,0": "3,1",
#     "4,1": "1,2",
#     "4,2": "1,3",
#     "4,3": "0,4",
#     "4,4": "4,0"
# }

# # ── 3. Reassemble using RGBA canvas (matches browser canvas behaviour)
# reconstructed = Image.new("RGBA", (width, height))

# for src_key, dst_key in Kt.items():
#     src_r, src_c = map(int, src_key.split(","))
#     dst_r, dst_c = map(int, dst_key.split(","))

#     # Crop tile from scrambled image
#     left   = src_c * tile_w
#     top    = src_r * tile_h
#     right  = left + tile_w
#     bottom = top  + tile_h
#     tile   = img.crop((left, top, right, bottom))

#     # Paste into correct position
#     dest_x = dst_c * tile_w
#     dest_y = dst_r * tile_h
#     reconstructed.paste(tile, (dest_x, dest_y))

# # ── 4. Apply grayscale exactly as validator does:
# #    g = Math.round(0.2126*R + 0.7152*G + 0.0722*B)
# #    output[R] = output[G] = output[B] = g
# #    output[A] = original Alpha
# arr = np.array(reconstructed, dtype=np.float64)  # shape: (H, W, 4)

# R = arr[:, :, 0]
# G = arr[:, :, 1]
# B = arr[:, :, 2]
# A = arr[:, :, 3]  # preserve alpha exactly

# # Match JavaScript Math.round() behaviour
# luminance = np.round(0.2126 * R + 0.7152 * G + 0.0722 * B).astype(np.uint8)

# # Build output array: R=G=B=luminance, A=original alpha
# out_arr = np.zeros_like(np.array(reconstructed))
# out_arr[:, :, 0] = luminance   # R
# out_arr[:, :, 1] = luminance   # G
# out_arr[:, :, 2] = luminance   # B
# out_arr[:, :, 3] = np.array(reconstructed)[:, :, 3]  # A unchanged

# # ── 5. Save as lossless PNG (RGBA, no compression artefacts)
# output_img = Image.fromarray(out_arr.astype(np.uint8), mode="RGBA")
# output_img.save("output_grayscale.png")  # PNG = lossless, pixel-perfect
# print("✅ Saved: output_grayscale.png")
# print(f"Mode: {output_img.mode}, Size: {output_img.size}")