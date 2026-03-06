## Ans of this script is not passing
from PIL import Image

img = Image.open("jigsaw.webp").convert("RGBA")

width, height = img.size
grid = 5

tile_w = width // grid
tile_h = height // grid

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

