#!/usr/bin/env python3
"""Draw a travel poster for VELMARA, a place that does not exist.

A dusk seascape: a glass-calm sea under a low golden sun, one lighthouse
on a basalt headland, and the place's name set large at the top. No other
copy: no quotes, no star ratings, no taglines. Drawn with PIL only.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
HORIZON = 640
random.seed(20261121)

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"

IVORY = (247, 239, 221)
GOLD = (242, 166, 90)
GOLD_DEEP = (224, 138, 66)
ROSE = (198, 91, 107)
INDIGO = (22, 34, 74)
VIOLET = (74, 58, 110)
TEAL_DEEP = (39, 75, 94)
TEAL_DARK = (18, 40, 58)
CLIFF = (24, 30, 48)
WHITE = (245, 234, 214)
CORAL = (217, 106, 78)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, stops):
    """Vertical gradient over [y0, y1] through (pos, color) stops."""
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = lerp(c0, c1, f)
                break
        else:
            col = stops[-1][1]
        draw.line([(x0, y), (x1, y)], fill=col)


img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# ---- sky: indigo -> violet -> rose -> gold at the horizon ----
vgrad(d, 0, 0, W, HORIZON, [
    (0.00, INDIGO), (0.45, VIOLET), (0.78, ROSE), (1.00, GOLD),
])

# ---- stars in the upper sky ----
for _ in range(110):
    x = random.randint(20, W - 20)
    y = random.randint(24, 400)
    r = random.choice([1, 1, 1, 2])
    a = random.randint(120, 235)
    fade = max(0, 1 - y / 460)
    d.ellipse([x - r, y - r, x + r, y + r],
              fill=(int(255 * fade) if False else (255, 250, 235)))

# ---- low sun with glow ----
SUN = (330, 598)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, a in ((150, 26), (110, 45), (80, 80)):
    gd.ellipse([SUN[0] - r, SUN[1] - r, SUN[0] + r, SUN[1] + r],
               fill=(242, 166, 90, a))
glow = glow.filter(ImageFilter.GaussianBlur(18))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img)
d.ellipse([SUN[0] - 54, SUN[1] - 54, SUN[0] + 54, SUN[1] + 54],
          fill=(255, 217, 138))
d.ellipse([SUN[0] - 54, SUN[1] - 54, SUN[0] + 54, SUN[1] + 54],
          outline=(255, 236, 180), width=2)

# ---- sea: teal darkening downward, with a golden sun-path ----
vgrad(d, 0, HORIZON, W, H, [(0.0, TEAL_DEEP), (1.0, TEAL_DARK)])
# sun-path shimmer: short gold strokes, denser near the horizon
for _ in range(260):
    t = random.random()
    y = HORIZON + 6 + int((H - HORIZON - 20) * t * t)
    wdt = random.randint(14, 70) * (1 - t * 0.55)
    cx = SUN[0] + random.gauss(0, 26 + t * 55)
    a = int(150 * (1 - t) + 30)
    d.line([(cx - wdt / 2, y), (cx + wdt / 2, y)],
           fill=(242, 178, 96), width=2)
# long gentle wave lines
for yy in range(HORIZON + 34, H - 10, 46):
    d.arc([40, yy - 14, W - 40, yy + 26], start=200, end=340,
          fill=(120, 165, 175), width=2)

# ---- distant headland silhouette on the left horizon ----
d.polygon([(0, HORIZON), (60, HORIZON - 26), (150, HORIZON - 34),
           (230, HORIZON - 12), (300, HORIZON), (0, HORIZON)],
          fill=(52, 58, 96))

# ---- basalt headland, bottom right, carrying the lighthouse ----
d.polygon([(640, H), (668, 800), (700, 736), (742, 706), (800, 688),
           (872, 676), (940, 690), (1024, 716), (1024, H)],
          fill=CLIFF)
# rock facets: a few darker seams
d.line([(700, 736), (760, 830), (820, 900)], fill=(14, 18, 32), width=4)
d.line([(872, 676), (900, 780), (940, 860)], fill=(14, 18, 32), width=4)
d.line([(742, 706), (700, 800)], fill=(38, 46, 70), width=3)

# ---- lighthouse: white tower, coral band, glass dome, gold lamp ----
LX = 806  # tower centre x
BASE_Y, TOP_Y = 692, 470
d.polygon([(LX - 26, BASE_Y), (LX - 15, TOP_Y), (LX + 15, TOP_Y),
           (LX + 26, BASE_Y)], fill=WHITE)
d.polygon([(LX - 21, 606), (LX - 18, 566), (LX + 18, 566),
           (LX + 21, 606)], fill=CORAL)
# gallery + lamp room
d.rectangle([LX - 20, TOP_Y - 16, LX + 20, TOP_Y], fill=(30, 34, 52))
d.rectangle([LX - 13, TOP_Y - 44, LX + 13, TOP_Y - 16], fill=(255, 214, 120))
d.line([(LX - 13, TOP_Y - 30), (LX + 13, TOP_Y - 30)], fill=(30, 34, 52), width=2)
d.line([(LX, TOP_Y - 44), (LX, TOP_Y - 16)], fill=(30, 34, 52), width=2)
d.polygon([(LX - 16, TOP_Y - 44), (LX + 16, TOP_Y - 44), (LX, TOP_Y - 62)],
          fill=(30, 34, 52))
# tower shading on the side away from the sun
d.polygon([(LX + 8, TOP_Y), (LX + 15, TOP_Y), (LX + 26, BASE_Y),
           (LX + 14, BASE_Y)], fill=(214, 198, 170))

# ---- keeper's cottage on the headland, two lit windows ----
d.polygon([(700, 700), (700, 668), (736, 648), (772, 668), (772, 700)],
          fill=(18, 22, 38))
d.rectangle([714, 676, 726, 690], fill=(255, 214, 120))
d.rectangle([744, 676, 756, 690], fill=(255, 214, 120))

# ---- light beam sweeping left across the dusk sky ----
beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(beam)
bd.polygon([(LX, TOP_Y - 30), (120, 452), (120, 512)], fill=(255, 214, 120, 52))
bd.polygon([(LX, TOP_Y - 30), (1024, 500), (1024, 540)], fill=(255, 214, 120, 22))
beam = beam.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(img.convert("RGBA"), beam).convert("RGB")
d = ImageDraw.Draw(img)

# ---- sailboats on the glass sea ----
def sailboat(x, y, s, sail_fill):
    d.polygon([(x, y - 46 * s), (x, y), (x + 26 * s, y)], fill=sail_fill)
    d.polygon([(x - 3, y - 46 * s), (x - 3, y), (x - 20 * s, y)],
              fill=(232, 222, 200))
    d.line([(x, y - 48 * s), (x, y + 2)], fill=(30, 34, 52), width=2)
    d.polygon([(x - 26 * s, y), (x + 30 * s, y), (x + 22 * s, y + 10 * s),
               (x - 18 * s, y + 10 * s)], fill=(24, 30, 48))

sailboat(330, 812, 1.0, (255, 226, 160))   # on the sun-path
sailboat(176, 892, 0.62, (240, 232, 214))
sailboat(560, 940, 0.5, (235, 226, 208))

# ---- birds ----
for bx, by, bs in ((180, 300, 9), (230, 268, 7), (268, 312, 6),
                   (620, 250, 8), (668, 282, 6)):
    d.arc([bx - bs, by - bs // 2, bx, by + bs // 2], start=200, end=340,
          fill=(20, 24, 44), width=2)
    d.arc([bx, by - bs // 2, bx + bs, by + bs // 2], start=200, end=340,
          fill=(20, 24, 44), width=2)

# ---- the place's name, large, at the top; nothing else ----
font = ImageFont.truetype(SERIF_BLACK, 132)
word = "VELMARA"
widths = [d.textlength(ch, font=font) for ch in word]
tracking = 18
total = sum(widths) + tracking * (len(word) - 1)
x = (W - total) / 2
y = 64
# soft shadow, then ivory face
for ox, oy, col in ((0, 5, (16, 22, 46)), (0, 0, IVORY)):
    cx = x
    for ch, wch in zip(word, widths):
        d.text((cx + ox, y + oy), ch, font=font, fill=col)
        cx += wch + tracking
# thin gold rule under the name
d.line([(W / 2 - 150, 236), (W / 2 + 150, 236)], fill=GOLD, width=3)
d.line([(W / 2 - 150, 242), (W / 2 + 150, 242)], fill=(GOLD[0], GOLD[1], GOLD[2]),
       width=1)

# ---- thin inner frame ----
d.rectangle([26, 26, W - 27, H - 27], outline=(242, 166, 90), width=2)

img.save("entry.png", optimize=True)
print(f"entry.png: {img.size[0]}x{img.size[1]}")
import os
print(f"bytes: {os.path.getsize('entry.png')}")
