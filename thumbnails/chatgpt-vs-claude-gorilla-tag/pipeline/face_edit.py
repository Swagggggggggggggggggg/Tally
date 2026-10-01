"""Make expression variants of the 64x65 Gorilla Tag face texture while keeping its pixel-art style."""
import os, random, sys, math
from PIL import Image

SRC = os.environ.get("GT_FACE", "gorillatexture.png")  # extracted from the NachoEngine rig
OUT = "tex/"

# eye boxes measured from the texture grid (inclusive pixel bounds)
EYES = {
    "L": dict(x0=14, x1=27, y0=23, y1=38, inner=+1),   # texture-left eye; inner corner toward +x
    "R": dict(x0=33, x1=46, y0=23, y1=38, inner=-1),   # texture-right eye; inner corner toward -x
}


def make(name, lid_outer_y=25.0, lid_inner_y=30.5, thick=1.6, shift=0, seed=4):
    rnd = random.Random(seed)
    im = Image.open(SRC).convert("RGB")
    px = im.load()
    src = im.copy().load()
    for key, e in EYES.items():
        xo = e["x0"] if e["inner"] > 0 else e["x1"]   # outer x
        xi = e["x1"] if e["inner"] > 0 else e["x0"]   # inner x
        # optional pupil shift (dx pixels) inside the eye: move dark pupil pixels
        if shift:
            cx0, cx1 = e["x0"] + 3, e["x1"] - 3
            for y in range(e["y0"] + 3, e["y1"] - 2):
                row = [src[x, y] for x in range(cx0, cx1 + 1)]
                for i, x in enumerate(range(cx0, cx1 + 1)):
                    j = i - shift
                    if 0 <= j < len(row):
                        px[x, y] = row[j]
                    else:
                        px[x, y] = (236, 236, 236)
        for x in range(e["x0"] - 1, e["x1"] + 2):
            t = (x - xo) / (xi - xo)
            ly = lid_outer_y + (lid_inner_y - lid_outer_y) * t
            for y in range(e["y0"] - 1, e["y1"] + 1):
                d = y - ly
                if d < -thick / 2:
                    # above the lid: face-plate grey with pixel noise (only where the eye was)
                    if e["x0"] <= x <= e["x1"]:
                        v = 128 + rnd.randint(-14, 14)
                        px[x, y] = (v, v, v)
                elif d <= thick / 2:
                    px[x, y] = (12, 12, 12)
    im.save(OUT + name + ".png")
    return OUT + name + ".png"


if __name__ == "__main__":
    make("face_angry", 24.5, 30.5, 1.8)
    make("face_angry_lookR", 24.5, 30.5, 1.8, shift=1)
    make("face_angry_lookL", 24.5, 30.5, 1.8, shift=-1)
    make("face_determined", 25.5, 29.0, 1.6)
    # preview sheet
    names = ["face_angry", "face_angry_lookR", "face_angry_lookL", "face_determined"]
    sheet = Image.new("RGB", (4 * 320, 325), (255, 0, 255))
    sheet.paste(Image.open(SRC).convert("RGB").resize((320, 325), Image.NEAREST), (0, 0))
    for i, n in enumerate(names[:3]):
        sheet.paste(Image.open(OUT + n + ".png").resize((320, 325), Image.NEAREST), ((i + 1) * 320, 0))
    sheet.save(OUT + "face_variants.png")
