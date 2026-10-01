"""QA sheet for the final thumbnail: feed sizes, grayscale, safe zones, specs."""
import sys, os, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
im = Image.open(src).convert("RGB")
assert im.size == (1280, 720), im.size
F = ImageFont.truetype("fonts/Inter.ttf", 22)
# 1) feed sizes + grayscale
t160 = im.resize((160, 90), Image.LANCZOS)
t240 = im.resize((240, 135), Image.LANCZOS)
t360 = im.resize((360, 203), Image.LANCZOS)
g = im.convert("L").convert("RGB").resize((640, 360), Image.LANCZOS)
sheet = Image.new("RGB", (1300, 520), (15, 15, 15))
d = ImageDraw.Draw(sheet)
x = 10
for lab, t in (("160x90 (sidebar)", t160), ("240x135", t240), ("360x203 (phone feed)", t360)):
    sheet.paste(t, (x, 40)); d.text((x, 10), lab, font=F, fill=(220, 220, 220)); x += t.width + 20
sheet.paste(t160.resize((480, 270), Image.NEAREST), (10, 240)); d.text((10, 212), "160x90 zoomed", font=F, fill=(220, 220, 220))
sheet.paste(g.resize((480, 270)), (520, 240)); d.text((520, 212), "grayscale", font=F, fill=(220, 220, 220))
sheet.save(os.path.join(outdir, "qa_sizes_grayscale.png"))
# 2) safe zones: duration badge (bottom-right), progress bar, 5% overscan
z = im.copy().convert("RGBA")
ov = Image.new("RGBA", z.size, (0, 0, 0, 0))
o = ImageDraw.Draw(ov)
o.rounded_rectangle([1280 - 8 - 100, 720 - 8 - 38, 1280 - 8, 720 - 8], 8, fill=(0, 0, 0, 200))
o.text((1280 - 96, 720 - 42), "12:04", font=ImageFont.truetype("fonts/Inter.ttf", 26), fill=(255, 255, 255))
o.rectangle([0, 720 - 8, 1280, 720], fill=(255, 0, 0, 230))
o.rectangle([64, 36, 1280 - 64, 720 - 36], outline=(255, 255, 0, 200), width=2)
z.alpha_composite(ov)
z.convert("RGB").save(os.path.join(outdir, "qa_safezones.png"))
# 3) stats
a = np.asarray(im).astype(float)
hsv = np.array([colorsys.rgb_to_hsv(*(p / 255)) for p in a.reshape(-1, 3)[::11]])
luma = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])
jpg = os.path.splitext(src)[0] + ".jpg"
print("size", im.size, "| jpg KB", os.path.getsize(jpg) // 1024 if os.path.exists(jpg) else "n/a")
print("mean HSV V %.1f/255 | mean S %.3f | luma mean %.1f" % (hsv[:, 2].mean() * 255, hsv[:, 1].mean(), luma.mean()))
print("clipped highlights %.3f%% | crushed blacks %.3f%%" % ((a.max(axis=2) >= 254).mean() * 100, (a.max(axis=2) <= 2).mean() * 100))
