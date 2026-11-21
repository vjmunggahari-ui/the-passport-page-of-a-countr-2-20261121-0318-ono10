#!/usr/bin/env python3
"""Generate entry.png — the passport spread of the Republic of Tavara,
an invented coral-atoll nation. Deterministic: fixed seed, no timestamps.
Authored fresh for the-passport-page-of-a-countr-2-20261121-0318."""
import math, random, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
random.seed(20261121)

SANS  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

# ---------- palette ----------
TEAL_DK   = (7, 36, 36)
TEAL_BG   = (11, 50, 50)
CREAM     = (246, 239, 219)
CREAM_DK  = (238, 228, 200)
NAVY      = (30, 58, 76)
NAVY_LT   = (58, 92, 110)
GOLD      = (176, 141, 58)
GOLD_LT   = (201, 170, 90)
GREY      = (110, 108, 96)
INK_BLUE  = (44, 95, 138)
INK_RED   = (166, 58, 46)
INK_PURP  = (107, 78, 142)
INK_GREEN = (62, 122, 78)
SKIN      = (201, 142, 107)
HAIR      = (42, 32, 24)

def tracked(draw, xy, text, fnt, fill, tracking=0):
    """Draw text with letter tracking; returns width used."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x

def text_w(draw, text, fnt, tracking=0):
    return sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking

def centered(draw, cx, y, text, fnt, fill, tracking=0):
    w = text_w(draw, text, fnt, tracking)
    tracked(draw, (cx - w / 2, y), text, fnt, fill, tracking)

def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)

# ---------- MRZ check digits ----------
def mrz_val(ch):
    if ch == '<':
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10

def mrz_check(s):
    w = [7, 3, 1]
    return str(sum(mrz_val(c) * w[i % 3] for i, c in enumerate(s)) % 10)

# ---------- background ----------
img = Image.new("RGB", (W, H), TEAL_DK)
bg = Image.new("RGB", (W, H))
bd = ImageDraw.Draw(bg)
for y in range(H):
    t = y / H
    c = tuple(int(TEAL_BG[i] + (TEAL_DK[i] - TEAL_BG[i]) * t) for i in range(3))
    bd.line([(0, y), (W, y)], fill=c)
img = bg
# faint map contour lines on the desk
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for k, (cx, cy, r0) in enumerate([(120, 900, 60), (950, 120, 80), (880, 940, 50), (60, 140, 40)]):
    for j in range(4):
        r = r0 + j * 26
        od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 180, 170, 26), width=2)
img = Image.alpha_composite(img.convert("RGBA"), ov)

# ---------- spread shadow + pages ----------
SHADOW = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(SHADOW)
sd.rounded_rectangle([86, 214, 966, 834], radius=10, fill=(0, 0, 0, 110))
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(14))
img = Image.alpha_composite(img, SHADOW)

PAGE_Y0, PAGE_Y1 = 200, 820
LX0, LX1 = 72, 502
RX0, RX1 = 522, 952
d = ImageDraw.Draw(img)
d.rounded_rectangle([LX0, PAGE_Y0, LX1, PAGE_Y1], radius=6, fill=CREAM)
d.rounded_rectangle([RX0, PAGE_Y0, RX1, PAGE_Y1], radius=6, fill=CREAM)
# spine shadow
sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
spd = ImageDraw.Draw(sp)
for i in range(20):
    a = 46 - abs(i - 10) * 4
    spd.line([(502 + i - 10, PAGE_Y0), (502 + i - 10, PAGE_Y1)], fill=(60, 40, 10, max(a, 0)))
img = Image.alpha_composite(img, sp)
d = ImageDraw.Draw(img)

# paper speckle (deterministic)
for _ in range(900):
    x = random.randint(72, 952); y = random.randint(200, 820)
    d.point((x, y), fill=(190, 175, 140))

def page_frame(x0, x1):
    d.rectangle([x0 + 13, PAGE_Y0 + 13, x1 - 13, PAGE_Y1 - 13],
                outline=GOLD, width=2)
    d.rectangle([x0 + 18, PAGE_Y0 + 18, x1 - 18, PAGE_Y1 - 18],
                outline=(GOLD_LT + (255,)) if False else GOLD_LT, width=1)

def guilloche(x0, x1, cx, cy, rmax):
    """Fine concentric arcs, very light gold, clipped to page area."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for r in range(24, rmax, 9):
        ld.ellipse([cx - r, cy - r, cx + r, cy + r],
                   outline=(176, 141, 58, 20), width=1)
    img.paste(Image.alpha_composite(img, lay), (0, 0))

# ---------- emblem: compass rose + frigate bird ----------
def emblem(cx, cy, s):
    """s = overall radius."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.ellipse([cx - s, cy - s, cx + s, cy + s], outline=GOLD, width=3)
    ld.ellipse([cx - s * 0.82, cy - s * 0.82, cx + s * 0.82, cy + s * 0.82],
               outline=GOLD, width=1)
    # 8-point star
    for k in range(8):
        ang = math.radians(k * 45 - 90)
        long = s * 0.78 if k % 2 == 0 else s * 0.55
        wdt = math.radians(7)
        tip = (cx + long * math.cos(ang), cy + long * math.sin(ang))
        b1 = (cx + s * 0.14 * math.cos(ang - wdt), cy + s * 0.14 * math.sin(ang - wdt))
        b2 = (cx + s * 0.14 * math.cos(ang + wdt), cy + s * 0.14 * math.sin(ang + wdt))
        col = GOLD if k % 2 == 0 else NAVY
        ld.polygon([tip, b1, b2], fill=col)
    ld.ellipse([cx - s * 0.16, cy - s * 0.16, cx + s * 0.16, cy + s * 0.16],
               fill=NAVY)
    ld.ellipse([cx - s * 0.07, cy - s * 0.07, cx + s * 0.07, cy + s * 0.07],
               fill=GOLD)
    # frigate bird above the rose
    bx, by, bs = cx, cy - s * 1.55, s * 0.42
    ld.polygon([(bx - bs, by), (bx - bs * 0.45, by - bs * 0.42),
                (bx, by - bs * 0.08), (bx + bs * 0.45, by - bs * 0.42),
                (bx + bs, by), (bx + bs * 0.4, by + bs * 0.16),
                (bx, by + bs * 0.05), (bx - bs * 0.4, by + bs * 0.16)],
               fill=NAVY)
    return lay

# ---------- portrait: flat-vector photo ----------
def portrait(w, h):
    p = Image.new("RGB", (w, h), (127, 181, 168))
    pd = ImageDraw.Draw(p)
    # sky -> horizon -> sea
    for y in range(h):
        if y < h * 0.52:
            t = y / (h * 0.52)
            c = tuple(int(a + (b - a) * t) for a, b in zip((143, 196, 178), (232, 217, 160)))
        else:
            t = (y - h * 0.52) / (h * 0.48)
            c = tuple(int(a + (b - a) * t) for a, b in zip((232, 217, 160), (23, 96, 96)))
        pd.line([(0, y), (w, y)], fill=c)
    # sun
    pd.ellipse([w - 52, 14, w - 14, 52], fill=(240, 205, 110))
    # sea lines: short horizontal strokes
    for yy in range(int(h * 0.62), h - 6, 12):
        for x0 in range(10, w - 30, 34):
            pd.line([(x0, yy), (x0 + 20, yy)], fill=(255, 255, 255), width=2)
    cx = w // 2
    # shoulders / dress
    pd.polygon([(cx - 62, h), (cx - 46, h - 52), (cx - 18, h - 62),
                (cx + 18, h - 62), (cx + 46, h - 52), (cx + 62, h)],
               fill=(30, 58, 76))
    pd.polygon([(cx - 18, h - 62), (cx, h - 40), (cx + 18, h - 62)],
               fill=(176, 141, 58))  # gold collar
    # neck + face
    pd.rectangle([cx - 9, h - 78, cx + 9, h - 58], fill=(188, 128, 94))
    pd.ellipse([cx - 27, h - 128, cx + 27, h - 66], fill=SKIN)
    # hair: bob framing the face
    pd.pieslice([cx - 32, h - 134, cx + 32, h - 60], start=180, end=360, fill=HAIR)
    pd.polygon([(cx - 32, h - 100), (cx - 27, h - 128), (cx - 20, h - 118),
                (cx - 24, h - 92)], fill=HAIR)
    pd.polygon([(cx + 32, h - 100), (cx + 27, h - 128), (cx + 20, h - 118),
                (cx + 24, h - 92)], fill=HAIR)
    pd.ellipse([cx - 30, h - 132, cx + 30, h - 96], fill=HAIR)
    pd.ellipse([cx - 24, h - 126, cx + 24, h - 92], fill=SKIN)  # face opening
    # gold headband
    pd.arc([cx - 27, h - 128, cx + 27, h - 76], start=200, end=340, fill=GOLD, width=3)
    # features: brows, closed eyes, nose, lips
    pd.arc([cx - 19, h - 106, cx - 5, h - 96], start=200, end=340, fill=HAIR, width=2)
    pd.arc([cx + 5, h - 106, cx + 19, h - 96], start=200, end=340, fill=HAIR, width=2)
    pd.arc([cx - 18, h - 98, cx - 6, h - 88], start=20, end=160, fill=(90, 60, 40), width=2)
    pd.arc([cx + 6, h - 98, cx + 18, h - 88], start=20, end=160, fill=(90, 60, 40), width=2)
    pd.line([(cx, h - 96), (cx - 2, h - 84)], fill=(150, 100, 70), width=2)
    pd.arc([cx - 8, h - 82, cx + 8, h - 72], start=10, end=170, fill=(163, 74, 58), width=2)
    # earring
    pd.ellipse([cx - 30, h - 88, cx - 26, h - 84], fill=GOLD)
    pd.ellipse([cx + 26, h - 88, cx + 30, h - 84], fill=GOLD)
    return p

# ---------- caption above the spread ----------
d = ImageDraw.Draw(img)
centered(d, 512, 108, "R E P U B L I C   O F   T A V A R A", font(SANSB, 26), (232, 217, 160), tracking=2)
centered(d, 512, 148, "A  C O U N T R Y  T H A T  I S N ' T  T H E R E", font(SANS, 15), (150, 190, 180), tracking=3)
centered(d, 512, 852, "Specimen passport spread  ·  Port Luan, Tavara  ·  The tide returns",
         font(SERIFI, 15), (140, 175, 165))

# ---------- LEFT PAGE: data page ----------
page_frame(LX0, LX1)
guilloche(LX0, LX1, 287, 510, 300)
d = ImageDraw.Draw(img)

# emblem + titles
img = Image.alpha_composite(img, emblem(287, 268, 34))
d = ImageDraw.Draw(img)
centered(d, 287, 318, "REPUBLIC OF TAVARA", font(SANSB, 20), NAVY, tracking=2)
centered(d, 287, 344, "PASSPORT", font(SANSB, 27), NAVY, tracking=6)
centered(d, 287, 376, "PASPOR  ·  TRAVEL DOCUMENT", font(SANS, 10), GREY, tracking=2)
d.line([(110, 396), (464, 396)], fill=GOLD, width=2)

# photo
photo = portrait(150, 185)
img.paste(photo, (100, 410))
d = ImageDraw.Draw(img)
d.rectangle([100, 410, 250, 595], outline=GOLD, width=3)
d.rectangle([104, 414, 246, 591], outline=(255, 255, 255), width=1)
# photo caption + signature
centered(d, 175, 600, "PHOTO  ·  FOTO", font(SANS, 9), GREY, tracking=1)
d.text((100, 622), "Seline Mara", font=font(SERIFI, 19), fill=NAVY)
d.line([(100, 646), (250, 646)], fill=NAVY, width=1)
d.text((100, 650), "HOLDER'S SIGNATURE", font=font(SANS, 8), fill=GREY)

# data fields, right of photo
FX, FW = 266, 222
fields = [
    ("TYPE", "P"), ("CODE", "TVA"), ("PASSPORT NO.", "TV8841207"),
    ("SURNAME", "MARA"),
    ("GIVEN NAMES", "SELINE AURELIA"),
    ("NATIONALITY", "TAVARAN"),
    ("DATE OF BIRTH", "14 MAR 1998"),
    ("PLACE OF BIRTH", "PORT LUAN"),
    ("SEX", "F"),
    ("DATE OF ISSUE", "02 JAN 2026"),
    ("DATE OF EXPIRY", "01 JAN 2036"),
    ("AUTHORITY", "MINISTRY OF TIDES"),
]
y = 410
for i, (lab, val) in enumerate(fields):
    if i in (0, 3, 6, 9):
        pass
    d.text((FX, y), lab, font=font(SANS, 9), fill=GREY)
    # value on same line for short rows, next line for long ones
    if i < 3:
        d.text((FX + 118, y - 2), val, font=font(SANSB, 13), fill=NAVY)
        if i < 2:
            y += 22
        else:
            y += 30
    else:
        d.text((FX, y + 11), val, font=font(SANSB, 14), fill=NAVY)
        y += 30 if i not in (4,) else 34

# MRZ
doc = "TV8841207"
l1 = "P<TVA" + "MARA<<SELINE<AURELIA" + "<" * 19
assert len(l1) == 44
dob, dob_c = "980314", mrz_check("980314")
exp, exp_c = "360101", mrz_check("360101")
opt = "<" * 14
body2 = doc + mrz_check(doc) + "<TVA" + dob + dob_c + "F" + exp + exp_c + opt
l2 = body2 + mrz_check(body2)
assert len(l2) == 44, len(l2)
d.rectangle([92, 700, 482, 756], fill=(232, 226, 198))
d.text((100, 708), l1, font=font(MONO, 13), fill=(20, 30, 40))
d.text((100, 729), l2, font=font(MONO, 13), fill=(20, 30, 40))
d.text((92, 762), "MACHINE READABLE ZONE — DO NOT FOLD", font=font(SANS, 8), fill=GREY)

# ---------- RIGHT PAGE: visa page ----------
page_frame(RX0, RX1)
d = ImageDraw.Draw(img)
d.text((542, 222), "VISAS", font=font(SANSB, 18), fill=NAVY)
d.text((880, 226), "PAGE 12", font=font(SANSB, 12), fill=GREY)
d.line([(542, 248), (932, 248)], fill=GOLD, width=2)
# perforated number along top edge
for i, ch in enumerate("TV8841207"):
    d.text((560 + i * 13, 200 + 0), "", font=font(SANS, 1), fill=NAVY)

# compass watermark (star only, no bird) for the visa page
def watermark_compass(cx, cy, s, alpha=52):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.ellipse([cx - s, cy - s, cx + s, cy + s],
               outline=(176, 141, 58, alpha), width=3)
    for k in range(8):
        ang = math.radians(k * 45 - 90)
        long = s * 0.78 if k % 2 == 0 else s * 0.55
        wdt = math.radians(7)
        tip = (cx + long * math.cos(ang), cy + long * math.sin(ang))
        b1 = (cx + s * 0.14 * math.cos(ang - wdt), cy + s * 0.14 * math.sin(ang - wdt))
        b2 = (cx + s * 0.14 * math.cos(ang + wdt), cy + s * 0.14 * math.sin(ang + wdt))
        col = (176, 141, 58, alpha) if k % 2 == 0 else (30, 58, 76, alpha)
        ld.polygon([tip, b1, b2], fill=col)
    ld.ellipse([cx - s * 0.10, cy - s * 0.10, cx + s * 0.10, cy + s * 0.10],
               outline=(176, 141, 58, alpha), width=2)
    return lay

img = Image.alpha_composite(img, watermark_compass(737, 500, 150))
d = ImageDraw.Draw(img)

# visa vignette sticker: mini atoll scene
st = Image.new("RGB", (170, 128), (255, 252, 240))
sd2 = ImageDraw.Draw(st)
for yy in range(96):
    t = yy / 96
    c = tuple(int(a + (b - a) * t) for a, b in zip((250, 214, 140), (120, 190, 200)))
    sd2.line([(0, yy), (170, yy)], fill=c)
sd2.ellipse([128, 10, 156, 38], fill=(240, 190, 90))
# sea band
sd2.rectangle([0, 62, 170, 96], fill=(46, 130, 130))
for yy in (70, 80, 90):
    for x0 in range(6, 160, 30):
        sd2.line([(x0, yy), (x0 + 18, yy)], fill=(220, 240, 235), width=2)
# sandbar
sd2.ellipse([-20, 84, 190, 112], fill=(238, 220, 170))
def blade(p0, p1, p2, w0=3.5):
    """Filled tapered quadratic-bezier blade (a palm frond)."""
    pts_l, pts_r = [], []
    for i in range(13):
        t = i / 12
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        n = math.hypot(dx, dy) or 1
        w = w0 * (1 - t) + 0.4
        pts_l.append((x - dy / n * w, y + dx / n * w))
        pts_r.append((x + dy / n * w, y - dx / n * w))
    sd2.polygon(pts_l + pts_r[::-1], fill=(34, 110, 66))

def palm(px, py, s, lean):
    # curved trunk
    sd2.line([(px, py), (px + lean, py - 26 * s), (px + lean * 2, py - 40 * s)],
             fill=(96, 66, 36), width=4)
    tx, ty = px + lean * 2, py - 40 * s
    L = 20 * s
    for ang in (-160, -120, -80, -40, -5):
        a = math.radians(ang)
        tip = (tx + L * math.cos(a), ty + L * math.sin(a) * 0.9 + 6 * s)
        mid = (tx + L * 0.55 * math.cos(a), ty + L * 0.55 * math.sin(a) * 0.9 - 4 * s)
        blade((tx, ty), mid, tip)
palm(52, 96, 1.0, 6)
palm(118, 96, 0.8, -5)
# canoe on the sea
sd2.polygon([(28, 76), (62, 76), (54, 82), (36, 82)], fill=(120, 60, 40))
sd2.line([(45, 76), (45, 62)], fill=(90, 60, 30), width=2)
sd2.polygon([(45, 62), (45, 74), (58, 74)], fill=(240, 235, 210))
st = st.filter(ImageFilter.GaussianBlur(0.4))
img.paste(st, (556, 268))
d = ImageDraw.Draw(img)
d.rectangle([556, 268, 726, 396], outline=(255, 255, 255), width=5)
d.rectangle([551, 263, 731, 401], outline=GOLD, width=2)
d.text((560, 404), "VISIT VISA — KINGDOM OF ALDOR", font=font(SANSB, 10), fill=NAVY)
d.text((560, 420), "SINGLE ENTRY · 90 DAYS · ISSUED 03 MAR 2026", font=font(SANS, 9), fill=GREY)

def stamp(cx, cy, lines, color, angle, w=210, h=86, fsize=13):
    lay = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=10,
                         outline=color + (235,), width=3)
    ld.rounded_rectangle([24, 24, 16 + w, 16 + h], radius=8,
                         outline=color + (235,), width=1)
    yy = 20 + (h - len(lines) * (fsize + 5)) // 2 + 2
    for ln in lines:
        fnt = font(SANSB, fsize)
        tw = ld.textlength(ln, font=fnt)
        ld.text(((w + 40 - tw) / 2, yy), ln, font=fnt, fill=color + (235,))
        yy += fsize + 5
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)

stamp(838, 330, ["ARRIVED", "PORT LUAN · 12 FEB 2026", "TAVARA"], INK_BLUE, -8, w=196, h=80)
stamp(650, 520, ["DEPARTED", "NORDHAVN · 28 FEB 2026"], INK_PURP, 6, w=190, h=72)
stamp(830, 600, ["ENTRY · KINGDOM OF ALDOR", "03 MAR 2026 · ADMITTED", "90 DAYS"], INK_RED, -4, w=216, h=84)
stamp(640, 672, ["CUSTOMS — CLEARED", "PORT LUAN"], INK_GREEN, 9, w=170, h=64, fsize=12)

# bottom note
d.text((542, 742), "This document is the property of the Republic of Tavara.",
       font=font(SANS, 10), fill=GREY)
d.text((542, 758), "If found, return to any Tavaran mission or to the Ministry",
       font=font(SANS, 10), fill=GREY)
d.text((542, 774), "of Tides, Port Luan. The tide returns.",
       font=font(SANS, 10), fill=GREY)
d.text((880, 790), "12", font=font(SANSB, 12), fill=GREY)

# subtle SPECIMEN diagonal across the spread
sp2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
s2d = ImageDraw.Draw(sp2)
fnt = font(SANSB, 46)
s2d.text((512, 470), "SPECIMEN", font=fnt, fill=(166, 58, 46, 26),
         anchor="mm")
sp2 = sp2.rotate(-24, center=(512, 512), resample=Image.BICUBIC)
img = Image.alpha_composite(img.convert("RGBA"), sp2).convert("RGB")

img.save("entry.png", optimize=True)
data = open("entry.png", "rb").read()
print("bytes:", len(data), "sha256:", hashlib.sha256(data).hexdigest())
print("size:", Image.open("entry.png").size)
