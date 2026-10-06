"""Render the real text in many candidate fonts on one sheet, next to the reference.

    python font_sheet.py --text "your text" --out sheet.png [--ref photo.jpg --crop x0 y0 x1 y1] FONT.ttf ...

Fonts come from Google Fonts' repo (all open licences, fine to sell prints with):
    curl -sfLO https://github.com/google/fonts/raw/main/ofl/<family>/<File>-Regular.ttf
(some families live under apache/ instead of ofl/, e.g. comingsoon, schoolbell).
A starting set for hand-stamped or casual lettering: GochiHand, Schoolbell, Mansalva,
Kalam, PatrickHand, Handlee, Itim, ShortStack, Sniglet, BalsamiqSans, ComicNeue-Bold,
Delius, Mali-Medium, VarelaRound, IndieFlower, CaveatBrush.
"""

import argparse
import os

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--text", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ref", help="the customer's reference photo")
ap.add_argument("--crop", nargs=4, type=int, help="x0 y0 x1 y1 of the lettering in --ref")
ap.add_argument("--size", type=int, default=64)
ap.add_argument("fonts", nargs="+")
a = ap.parse_args()

row = int(a.size * 1.6)
top = 0
ref = None
if a.ref:
    ref = Image.open(a.ref)
    if a.crop: ref = ref.crop(tuple(a.crop))
    ref.thumbnail((560, 240))
    top = ref.height + 10
W = max(1000, 300 + int(a.size * 0.6 * len(a.text)))
im = Image.new("RGB", (W, top + row * len(a.fonts)), "#c9cacc")
d = ImageDraw.Draw(im)
if ref: im.paste(ref, (300, 0))
try:
    lab = ImageFont.truetype("arial.ttf", 18)
except OSError:
    lab = ImageFont.load_default()
for i, f in enumerate(a.fonts):
    y = top + i * row
    d.text((10, y + 8), f"{i + 1}. " + os.path.basename(f).rsplit(".", 1)[0], fill="#444", font=lab)
    d.text((300, y + 6), a.text, fill="#222", font=ImageFont.truetype(f, a.size))
im.save(a.out)
print(a.out, im.size)
