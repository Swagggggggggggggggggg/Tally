"""Happy (closed smile) variant of the 64x65 Gorilla Tag face texture, pixel-art style."""
import random
from PIL import Image
SRC = "/tmp/claude-0/-home-user-Tally/702e814a-b90a-5d68-bc9a-bc92c217492c/scratchpad/nacho/extracted/gorillatexture.png"
OUT = "/tmp/claude-0/-home-user-Tally/702e814a-b90a-5d68-bc9a-bc92c217492c/scratchpad/blender/tex/"
rnd = random.Random(7)
im = Image.open(SRC).convert("RGB")
px = im.load()
# erase the original mouth line with muzzle grey
for y in range(54, 60):
    for x in range(22, 39):
        r, g, b = px[x, y]
        if r < 120:
            v = 150 + rnd.randint(-12, 12)
            px[x, y] = (v, v, v)
# smile arc: corners high, centre low; 2px thick in the middle, 1px at the tips
for x in range(23, 38):
    t = (x - 30) / 7.0
    yc = 54.2 + 3.6 * (1 - t * t)
    for y in range(52, 61):
        d = abs(y - yc)
        thick = 1.1 if abs(t) < 0.75 else 0.7
        if d <= thick:
            px[x, y] = (14, 14, 14)
# small cheek dimples at the corners
px[22, 53] = (40, 40, 40)
px[38, 53] = (40, 40, 40)
im.save(OUT + "face_happy.png")
big = im.resize((64 * 8, 65 * 8), Image.NEAREST)
big.save(OUT + "face_happy_preview.png")
print("ok")
