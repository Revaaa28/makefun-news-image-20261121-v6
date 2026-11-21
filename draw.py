#!/usr/bin/env python3
"""Render entry.png - the world news of Saturday 21 November 2026 as one
broadsheet newspaper front page. Deterministic: no randomness, no clocks."""
import math
from PIL import Image, ImageDraw, ImageFont

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SERIF = FD + "DejaVuSerif.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

W = H = 1024
MX = 22                 # side margin
CW = W - 2 * MX         # 980 content width
RX = MX + CW            # 1002 right edge

PAPER = (247, 241, 222)
INK = (26, 23, 18)
RED = (176, 32, 24)
DARKRED = (148, 26, 20)
GREY = (96, 90, 78)
RULE = (43, 38, 32)

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def tw(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, width):
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if tw(d, t, f) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_size(d, s, path, width, start, minimum=9):
    size = start
    while size > minimum and tw(d, s, F(path, size)) > width:
        size -= 1
    return size


def fit_lines(d, s, path, width, max_lines, start, minimum=9):
    size = start
    while size > minimum and len(wrap(d, s, F(path, size), width)) > max_lines:
        size -= 1
    return size


def center(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)


def banner(d, x, y, w, h, label, fsize=13):
    """Red banner strip with white bold label, text indented from left."""
    d.rectangle([x, y, x + w, y + h], fill=RED)
    f = F(SANS_B, fsize)
    ty = y + (h - fsize) / 2 - 2
    d.text((x + 8, ty), label, font=f, fill=(255, 255, 255))


def tagchip(d, x2, y2, s, fsize=10):
    """Small dark source tag, bottom-right corner anchored at (x2, y2)."""
    f = F(SANS_B, fsize)
    w = tw(d, s, f) + 10
    d.rectangle([x2 - w, y2 - fsize - 7, x2, y2], fill=(20, 18, 16))
    d.text((x2 - w + 5, y2 - fsize - 5), s, font=f, fill=(255, 246, 220))


def badge(d, cx, cy, r, num, fsize=13):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
              outline=(255, 255, 255), width=2)
    f = F(SANS_B, fsize)
    s = str(num)
    d.text((cx - tw(d, s, f) / 2, cy - fsize / 2 - 2), s, font=f,
           fill=(255, 255, 255))


def fake_italic(img, box, d_text, f, fill):
    """Draw text on a strip and shear it to fake an italic deck line."""
    x0, y0, x1, y1 = (int(v) for v in box)
    strip = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    sd.text((4, 2), d_text, font=f, fill=fill + (255,))
    h = y1 - y0
    out = Image.new("RGBA", strip.size, (0, 0, 0, 0))
    for yy in range(h):
        off = int(0.26 * (h - yy))
        row = strip.crop((0, yy, strip.width, yy + 1))
        out.paste(row, (off, yy))
    img.paste(out, (x0, y0), out)


# ---------------------------------------------------------------- scenes
def dashed_arc(d, p0, p1, p2, color, steps=44, dash=3, width=2):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    for i in range(steps):
        if (i // dash) % 2 == 0:
            d.line([pts[i], pts[i + 1]], fill=color, width=width)


def starburst(d, cx, cy, r, color=(255, 214, 90)):
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))],
               fill=color, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 242, 190))


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(219, 238, 224))
    # globe
    gx, gy, gr = x + 62, y + h // 2 + 8, 40
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 116, 178))
    for dx, dy, rw, rh in [(-22, -18, 26, 14), (-6, 2, 20, 16), (12, -24, 18, 12),
                          (16, 12, 14, 10), (-28, 14, 14, 9)]:
        d.ellipse([gx + dx, gy + dy, gx + dx + rw, gy + dy + rh],
                  fill=(74, 148, 84))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(38, 84, 132), width=2)
    # thermometer
    tx = x + 128
    d.rounded_rectangle([tx, y + 16, tx + 16, y + h - 26], 8,
                        fill=(245, 245, 240), outline=INK, width=2)
    d.rectangle([tx + 5, y + 34, tx + 11, y + h - 30], fill=RED)
    d.ellipse([tx - 5, y + h - 34, tx + 21, y + h - 8], fill=RED, outline=INK, width=2)
    for k in range(4):
        ly = y + 26 + k * 14
        d.line([(tx + 18, ly), (tx + 25, ly)], fill=INK, width=2)
    # clock
    kx, ky, kr = x + w - 52, y + h // 2 + 8, 34
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(252, 250, 240),
              outline=INK, width=3)
    for k in range(12):
        a = k * math.pi / 6
        r1 = kr - 7 if k % 3 == 0 else kr - 4
        d.line([(kx + r1 * math.cos(a), ky + r1 * math.sin(a)),
                (kx + (kr - 2) * math.cos(a), ky + (kr - 2) * math.sin(a))],
               fill=INK, width=2)
    d.line([(kx, ky), (kx + 4, ky - 20)], fill=INK, width=3)
    d.line([(kx, ky), (kx + 17, ky + 8)], fill=RED, width=3)
    d.ellipse([kx - 3, ky - 3, kx + 3, ky + 3], fill=INK)


def scene_saudi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 24, 46))
    # stars
    for i in range(26):
        sx = x + (i * 53) % w
        sy = y + (i * 29) % max(10, h - 52)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(210, 220, 240))
    ground = y + h - 26
    # skyline: dense buildings with lit windows
    bw = 26
    heights = [44, 62, 36, 70, 50, 78, 42, 58, 66, 48, 72, 40]
    for bi, bh in enumerate(heights):
        bx = x + 4 + bi * (bw + 2)
        if bx + bw > x + w - 2:
            break
        d.rectangle([bx, ground - bh, bx + bw, ground], fill=(24, 38, 66))
        for r in range(bh // 9):
            for c in range(3):
                if (r * 7 + c * 3 + bi) % 3 != 0:
                    wx = bx + 4 + c * 8
                    wy = ground - bh + 4 + r * 9
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 205, 84))
    d.rectangle([x, ground, x + w, y + h], fill=(8, 14, 28))
    # missile trails (dashed arcs) ending in starbursts
    arcs = [((x + 18, y + 16), (x + 90, y - 14), (x + 150, y + 40)),
            ((x + w - 30, y + 10), (x + w - 110, y - 16), (x + w - 168, y + 34)),
            ((x + 120, y + 8), (x + 170, y - 10), (x + 208, y + 30))]
    for p0, p1, p2 in arcs:
        dashed_arc(d, p0, p1, p2, (255, 120, 90))
        starburst(d, p2[0], p2[1], 11)


def scene_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 223, 186))
    # ridge
    ridge = [(x, y + h - 30), (x + 50, y + h - 62), (x + 110, y + h - 40),
             (x + 170, y + h - 70), (x + 235, y + h - 44), (x + w, y + h - 58),
             (x + w, y + h), (x, y + h)]
    d.polygon(ridge, fill=(168, 118, 74))
    ridge2 = [(x, y + h - 12), (x + 80, y + h - 34), (x + 160, y + h - 18),
              (x + 240, y + h - 36), (x + w, y + h - 24), (x + w, y + h),
              (x, y + h)]
    d.polygon(ridge2, fill=(138, 94, 56))
    # seismograph trace: bold red jagged line across the middle
    pts = []
    n = 46
    amp = [2, 3, 2, 4, 3, 2, 5, 3, 2, 4, 6, 14, 22, 9, 18, 26, 12, 20, 8, 15,
           5, 3, 6, 4, 2, 3, 5, 3, 2, 4, 3, 2, 3, 2, 4, 3, 2, 3, 2, 2, 3, 2,
           2, 3, 2, 2]
    midy = y + h // 2 - 6
    for i in range(n):
        px = x + 8 + i * (w - 16) / (n - 1)
        off = amp[i] if i % 2 == 0 else -amp[i]
        pts.append((px, midy + off))
    d.line(pts, fill=RED, width=3)
    # two houses
    for hx in (x + 34, x + w - 74):
        hy = y + h - 34
        d.rectangle([hx, hy, hx + 30, hy + 22], fill=(250, 246, 235),
                    outline=INK, width=2)
        d.polygon([(hx - 4, hy), (hx + 15, hy - 13), (hx + 34, hy)],
                  fill=DARKRED)
        d.rectangle([hx + 11, hy + 8, hx + 19, hy + 22], fill=(90, 60, 40))


# ------------------------------------------------------------- brief scenes
def sc_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(172, 205, 226))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(70, 120, 170))
    for i in range(4):
        wx = x + 8 + i * (w // 4)
        d.arc([wx, y + h - 14, wx + 22, y + h - 2], 0, 180, fill=(240, 250, 255), width=2)
    deck = y + h - 16
    t1, t2 = x + w * 0.32, x + w * 0.68
    top = y + 5
    # main cable: three spans through the tower tops, middle one sagging
    pts = []
    spans = [(x + 2, deck - 3, t1, top), (t1, top, t2, top), (t2, top, x + w - 2, deck - 3)]
    for x0, y0, x1, y1 in spans:
        sag = 7 if y0 == y1 else 2
        for i in range(13):
            t = i / 12
            px = x0 + (x1 - x0) * t
            py = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
            pts.append((px, py))
    d.line(pts, fill=(60, 60, 68), width=2)
    # suspenders
    for px, py in pts[::3]:
        d.line([(px, py), (px, deck)], fill=(60, 60, 68), width=1)
    for tx in (t1 - 3, t2 - 3):
        d.rectangle([tx, top, tx + 6, deck], fill=(80, 80, 88))
    d.rectangle([x, deck, x + w, deck + 4], fill=(52, 52, 58))


def sc_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 52, 92))
    for r in range(3):
        wy = y + h - 16 + r * 5
        for i in range(5):
            wx = x + 6 + i * (w // 5) + (r % 2) * 8
            d.arc([wx, wy, wx + 26, wy + 7], 0, 180, fill=(120, 190, 235), width=2)
    cx, cy = x + w // 2, y + 16
    d.ellipse([cx - 12, cy - 5, cx + 12, cy + 5], fill=(16, 18, 22))
    for dx, dy in [(-26, -9), (26, -9), (-26, 9), (26, 9)]:
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=(16, 18, 22), width=3)
        d.line([(cx + dx - 8, cy + dy), (cx + dx + 8, cy + dy)],
               fill=(200, 210, 220), width=2)
    d.line([(cx, cy + 4), (cx, y + h - 18)], fill=(255, 120, 90), width=1)


def sc_uranium(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 56, 48))
    for i, bx in enumerate((x + 22, x + w // 2 - 16, x + w - 54)):
        by = y + 10
        d.rectangle([bx, by, bx + 32, by + h - 16], fill=(238, 196, 32),
                    outline=(120, 96, 10), width=2)
        d.rectangle([bx, by + 5, bx + 32, by + 9], fill=(120, 96, 10))
        ccx, ccy = bx + 16, by + (h - 16) // 2 + 4
        d.ellipse([ccx - 3, ccy - 3, ccx + 3, ccy + 3], fill=(20, 20, 20))
        for k in range(3):
            a0 = 90 + k * 120 - 28
            d.pieslice([ccx - 9, ccy - 9, ccx + 9, ccy + 9], a0, a0 + 56,
                       fill=(20, 20, 20))


def sc_datacentre(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 208, 218))
    bw = (w - 24) // 4
    for i in range(4):
        bx = x + 8 + i * (bw + 3)
        bh = h - 16 - (i % 2) * 6
        d.rectangle([bx, y + h - 8 - bh, bx + bw, y + h - 8], fill=(96, 106, 118))
        for r in range(bh // 8):
            for c in range(3):
                if (r + c + i) % 2 == 0:
                    d.rectangle([bx + 3 + c * 7, y + h - 12 - bh + r * 8,
                                 bx + 7 + c * 7, y + h - 9 - bh + r * 8],
                                fill=(255, 214, 110))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(80, 88, 96))
    f = F(SANS_B, 15)
    d.text((x + w - 22, y + 4), "$", font=f, fill=DARKRED)


def sc_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 226, 240))
    for px, col, kind in ((x + 44, (206, 40, 32), "cn"), (x + w - 62, (240, 240, 240), "jp")):
        d.rectangle([px, y + 6, px + 3, y + h - 6], fill=(70, 60, 50))
        d.rectangle([px + 3, y + 7, px + 48, y + 25], fill=col,
                    outline=(120, 110, 100), width=1)
        if kind == "cn":
            d.ellipse([px + 8, y + 11, px + 14, y + 17], fill=(255, 214, 60))
        else:
            d.ellipse([px + 19, y + 11, px + 31, y + 23], fill=(188, 0, 45))


def sc_jet(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 196, 232))
    d.ellipse([x + 14, y + 8, x + 52, y + 15], fill=(250, 252, 255))
    d.ellipse([x + w - 62, y + 6, x + w - 16, y + 13], fill=(250, 252, 255))
    cy = y + h // 2 + 2
    d.ellipse([x + 26, cy - 7, x + w - 30, cy + 7], fill=(238, 242, 246),
              outline=(90, 100, 112), width=2)
    d.polygon([(x + 30, cy - 4), (x + 16, cy - 14), (x + 30, cy - 12)],
              fill=(176, 32, 24))
    d.polygon([(x + w // 2 - 6, cy + 2), (x + w // 2 + 18, cy + 16),
               (x + w // 2 + 30, cy + 16), (x + w // 2 + 8, cy)],
              fill=(120, 132, 146))
    for i in range(7):
        wx = x + 52 + i * 13
        d.ellipse([wx, cy - 3, wx + 5, cy + 1], fill=(70, 110, 150))


def sc_handshake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 188))
    cy = y + h // 2
    d.polygon([(x, cy - 12), (x + w // 2 - 8, cy + 2), (x + w // 2 - 20, cy + 14),
               (x, cy + 10)], fill=(52, 74, 110))
    d.polygon([(x + w, cy - 12), (x + w // 2 + 8, cy + 2),
               (x + w // 2 + 20, cy + 14), (x + w, cy + 10)], fill=(120, 44, 38))
    d.ellipse([x + w // 2 - 13, cy - 4, x + w // 2 + 13, cy + 14],
              fill=(232, 184, 138), outline=(160, 116, 74), width=2)
    for k in range(3):
        d.line([(x + w // 2 - 6 + k * 6, cy + 10), (x + w // 2 - 4 + k * 6, cy + 15)],
               fill=(160, 116, 74), width=2)


def sc_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 34))
    pts = [(x + 8, y + 12), (x + 40, y + 18), (x + 66, y + 14), (x + 96, y + 26),
           (x + 124, y + 24), (x + 152, y + 36), (x + w - 10, y + h - 12)]
    d.line(pts, fill=(240, 120, 90), width=2)
    cx, cy, r = x + w - 30, y + 17, 12
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26))
    f = F(SANS_B, 15)
    d.text((cx - 5, cy - 9), "B", font=f, fill=(255, 255, 255))


def sc_flag_cheq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(170, 200, 150))
    px = x + 40
    d.rectangle([px, y + 4, px + 3, y + h - 4], fill=(70, 60, 50))
    sq = 8
    for r in range(3):
        for c in range(6):
            col = (20, 20, 20) if (r + c) % 2 == 0 else (245, 245, 245)
            d.rectangle([px + 3 + c * sq, y + 6 + r * sq,
                         px + 3 + (c + 1) * sq, y + 6 + (r + 1) * sq], fill=col)
    d.rectangle([x + w - 58, y + h - 12, x + w - 12, y + h - 5], fill=(90, 130, 80))


def sc_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 158, 84))
    d.rectangle([x + 16, y + 8, x + w - 16, y + h - 8], fill=(216, 198, 150))
    # stumps
    sx = x + w - 44
    for k in range(3):
        d.rectangle([sx + k * 7, y + 12, sx + k * 7 + 3, y + h - 14],
                    fill=(240, 200, 80), outline=(150, 120, 40), width=1)
    d.rectangle([sx, y + 10, sx + 20, y + 13], fill=(240, 200, 80))
    # bat, angled
    bx, by = x + 34, y + h - 12
    d.polygon([(bx, by), (bx + 10, by - 26), (bx + 19, by - 23), (bx + 9, by + 3)],
              fill=(232, 208, 160), outline=(150, 120, 74), width=1)
    d.line([(bx + 13, by - 24), (bx + 19, by - 34)], fill=(90, 70, 50), width=3)
    d.ellipse([x + w // 2 + 8, y + 14, x + w // 2 + 19, y + 25], fill=(178, 30, 40))


BRIEF_SCENES = [sc_bridge, sc_drone, sc_uranium, sc_datacentre, sc_flags,
                sc_jet, sc_handshake, sc_bitcoin, sc_flag_cheq, sc_cricket]

# ------------------------------------------------------------------- map
# continent polygons in a 100 x 56 grid (rough equirectangular shapes)
CONTINENTS = [
    [(3, 11), (13, 6), (23, 6), (29, 11), (27, 17), (23, 21), (24, 26),
     (20, 29), (16, 26), (13, 30), (11, 33), (9, 27), (5, 21), (2, 15)],
    [(21, 33), (27, 32), (30, 36), (28, 43), (25, 51), (21, 52), (19, 44),
     (19, 37)],
    [(45, 13), (51, 9), (56, 11), (55, 16), (50, 18), (45, 16)],
    [(46, 20), (56, 19), (60, 24), (58, 34), (54, 43), (48, 44), (45, 34),
     (44, 26)],
    [(56, 11), (71, 6), (86, 9), (93, 15), (89, 21), (81, 20), (77, 25),
     (71, 23), (65, 19), (58, 16), (55, 12)],
    [(66, 23), (71, 23), (68, 31), (66, 27)],
    [(78, 25), (83, 25), (82, 32), (79, 30)],
    [(83, 37), (94, 36), (96, 42), (90, 47), (84, 44)],
]
ISLANDS = [(81, 35, 4, 2), (86, 36, 4, 2), (90, 35, 3, 2), (95, 44, 3, 4),
           (42, 15, 3, 2), (76, 33, 3, 2)]
# (story number, grid x, grid y)
PINS = [(1, 57, 19), (2, 60, 24), (3, 24, 39), (4, 53, 13), (5, 66, 23),
        (6, 64, 18), (7, 15, 17), (8, 88, 17), (9, 84, 28), (10, 91, 43),
        (12, 9, 18), (13, 96, 48)]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 38, 66))
    sx, sy = w / 100.0, h / 56.0
    for poly in CONTINENTS:
        pts = [(x + gx * sx, y + gy * sy) for gx, gy in poly]
        d.polygon(pts, fill=(216, 192, 148))
    for gx, gy, gw, gh in ISLANDS:
        d.ellipse([x + gx * sx, y + gy * sy, x + (gx + gw) * sx,
                   y + (gy + gh) * sy], fill=(216, 192, 148))
    for num, gx, gy in PINS:
        cx, cy = x + gx * sx, y + gy * sy
        r = 7
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = F(SANS_B, 8)
        s = str(num)
        d.text((cx - tw(d, s, f) / 2, cy - 5), s, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------- rich text
def wrap_rich(d, segments, width):
    """segments: list of (text, font, color). Returns lines of (word, font,
    color) tokens wrapped to width."""
    tokens = []
    for text, f, color in segments:
        for word in text.split():
            tokens.append((word, f, color))
    space_w = {}
    lines, cur, cur_w = [], [], 0.0
    for word, f, color in tokens:
        if f not in space_w:
            space_w[f] = tw(d, " ", f)
        ww = tw(d, word, f)
        add = ww if not cur else ww + space_w[cur[-1][1]]
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [(word, f, color)], ww
        else:
            cur.append((word, f, color))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_rich(d, lines, x, y, lh):
    for line in lines:
        cx = x
        prev_f = None
        for word, f, color in line:
            if prev_f is not None:
                cx += tw(d, " ", prev_f)
            d.text((cx, y), word, font=f, fill=color)
            cx += tw(d, word, f)
            prev_f = f
        y += lh
    return y


# ---------------------------------------------------------------- content
STATS = [
    ("Day 13", "of a COP31 summit planned to close on day 12"),
    ("5", "missiles shot down over Riyadh and Jizan"),
    ("6.7", "magnitude of the quake in Junín, Peru"),
    ("146", "people safe after a jet's emergency landing"),
    ("$58,983", "bitcoin early Saturday, down 3.9% in a day"),
    ("124*", "K L Rahul's score at tea in Wellington"),
]

REGIONS = [
    ("EUROPE 4", 112, (70, 100, 122), (255, 255, 255)),
    ("ASIA 10", 246, (176, 74, 50), (255, 255, 255)),
    ("MIDDLE EAST 5", 140, (207, 138, 46), (26, 23, 18)),
    ("AFRICA 1", 62, (109, 138, 68), (255, 255, 255)),
    ("AMERICAS 11", 274, (63, 109, 90), (255, 255, 255)),
    ("OCEANIA 3", 84, (122, 74, 110), (255, 255, 255)),
    ("GLOBAL 1", 62, (85, 80, 73), (255, 255, 255)),
]

HEROES = [
    dict(num=1, banner="COP31: OVERTIME", tag="No deal · day 13",
         chip="AFP · Al Jazeera", tagline="ANTALYA, TÜRKIYE · CLIMATE",
         headline="Climate summit runs into Saturday with no deal",
         body="COP31 missed its Friday close on day 13; a draft with no "
              "mention of fossil fuels split nearly 200 countries; a third "
              "text is promised (AFP, Al Jazeera).",
         scene=scene_cop31),
    dict(num=2, banner="SAUDI: MISSILES", tag="5 shot down",
         chip="AFP · Dawn", tagline="RIYADH · JIZAN · WAR",
         headline="Five Houthi missiles shot down over Saudi Arabia",
         body="Three ballistic missiles were destroyed over Riyadh before "
              "dawn and two over Jizan late on Friday, a day after it bombed "
              "Hodeidah port (AFP, Dawn).",
         scene=scene_saudi),
    dict(num=3, banner="PERU: QUAKE 6.7", tag="00:09 UTC · 108 km deep",
         chip="USGS · IGP", tagline="JUNÍN, PERU · EARTHQUAKE",
         headline="Magnitude 6.7 earthquake shakes central Peru",
         body="The deep quake near Carhuamayo was felt in Lima and along "
              "the coast; Peru's institute reported no deaths or tsunami "
              "risk (USGS, IGP, Gestión).",
         scene=scene_peru),
]

BRIEFS = [
    (4, "KYIV: WARNING", "NBC", 'Zelensky: Crimea bridge "will not stay"',
     "He warns of more double-tap strikes (NBC)."),
    (5, "HORMUZ: DRONE", "IRIB", "Iran says it shot down a US drone",
     "No confirmation from Washington (IRIB)."),
    (6, "IRAN: URANIUM", "Tol", "Iran: uranium stock stays in the country",
     'Minister still sees a "fair solution" (Tol).'),
    (7, "TRUMP: AI TAX", "ABC", "Trump vows tax on data centres abroad",
     '"Tremendous" penalty, no details yet (ABC).'),
    (8, "CHINA–JAPAN", "AFP", 'China tells Japan to "correct" Taiwan words',
     "Tokyo says its stance is unchanged (AFP)."),
    (9, "DAVAO: 146 SAFE", "AP", "Jet lands safely after engine fire alert",
     "Air Niugini diverts after midnight (AP)."),
    (10, "CANBERRA: AI", "ABC", "Australia and China agree to AI talks",
     "Albanese ends an 11-day trip (ABC)."),
    (11, "BITCOIN: $58,983", "CoinGecko", "Bitcoin trades below $59,000",
     "Down 3.9% in a day, ether $1,625 (CoinGecko)."),
    (12, "RUSSELL: P1", "Formula 1", "Russell fastest in final Vegas practice",
     "1:34.041 in a damp, messy session (Formula 1)."),
    (13, "RAHUL: 124*", "AFP", "Rahul hits a century against New Zealand",
     "India 344 for 2 at tea, replying to 368 (AFP)."),
]

INDEX = [
    (14, "Kryvyi Rih", "double strike kills 2, injures 42 (Kyiv Independent)"),
    (15, "Copenhagen", "Russian attaché expelled over a plot (Al Jazeera)"),
    (16, "Antalya", 'EU warns COP31 risks a no-"fossil summit" (AFP)'),
    (17, "Antalya", "Panama threatens to block the climate text (Al Jazeera)"),
    (18, "Antalya", "Indonesia's PLN signs six clean-power deals (Antara)"),
    (19, "Yemen", "Houthis threaten Jeddah and Red Sea ports (Al Jazeera)"),
    (20, "Washington", "Vance: Iran strikes were Trump's decision (Reuters)"),
    (21, "Washington", "lawmaker threatens SpaceX's funding (CNN)"),
    (22, "Texas", "execution of a man of 67 takes 63 minutes (ABC)"),
    (23, "Los Angeles", "jury convicts man who started the Palisades fire (ABC)"),
    (24, "Missouri", "judge approves $7.25bn Roundup settlement (AFP)"),
    (25, "Vancouver", "Canada rests defence in youth climate trial (AFP)"),
    (26, "Pyongyang", "Kim tours factories after no Trump meeting (AFP)"),
    (27, "Sejong", "freight train derails, no one hurt (Korea Herald)"),
    (28, "Taipei", "budget and cash payout passed (Taipei Times)"),
    (29, "Bangkok", "six-point plan on arsenic in two rivers (The Nation)"),
    (30, "New Delhi", "Pakistani minister joins SCO forum in India (Dawn)"),
    (31, "Eastern India", "rain alerts as Akvan's remnants move inland (ETV)"),
    (32, "Myanmar", "rights groups urge sanctions after court ruling (AP)"),
    (33, "Port Louis", "African rating agency talks to 15 states (UN)"),
    (34, "Melbourne", "Cummins keeps the Australian captaincy (ABC)"),
    (35, "Las Vegas", "Verstappen sent to stewards after contact (Autosport)"),
]


def date_check_segments(size):
    fb, fr = F(SANS_B, size), F(SANS, size)
    return [
        ("DATE CHECK — NOT SATURDAY NEWS.", fb, RED),
        ("Fri 20 Nov:", fb, INK),
        ("Wall Street's fall into a correction · the Russian barrage that "
         "hit Kyiv's bridges · the missile that landed in Poland · the "
         "UK–EU deal · Cyclone Akvan's landfall · Virginia measles death "
         "announced · the ICJ's Myanmar genocide ruling.", fr, INK),
        ("Thu 19 Nov:", fb, INK),
        ("the Shenzhen summit (Trump–Xi–Putin) · the GTA VI launch · "
         "Anthropic's market debut, shares up 17%.", fr, INK),
        ("Older:", fb, INK),
        ("Voyager 1's light-day (18 Nov) · Starc's 7/58 — that was the "
         "2025 Ashes, a year ago.", fr, INK),
        ("Not confirmed when drawn, so not shown:", fb, INK),
        ("BepiColombo's Mercury orbit entry · any final COP31 text.", fr, INK),
    ]


# ------------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 8

    # kicker
    fk = F(SANS_B, 15)
    d.text((MX, y), "THE WORLD IN ONE DAY", font=fk, fill=RED)
    right = "35 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((RX - tw(d, right, fk), y), right, font=fk, fill=RED)
    y += 24
    d.rectangle([MX, y, RX, y + 3], fill=RULE)
    d.rectangle([MX, y + 5, RX, y + 6], fill=RULE)
    y += 10

    # masthead
    title = "Saturday 21 November 2026"
    ms = fit_size(d, title, SERIF_B, CW, 62, 40)
    fm = F(SERIF_B, ms)
    center(d, W // 2, y, title, fm, INK)
    y += ms

    # deck (faked italic serif)
    deck = ("Climate summit runs past its deadline · Five missiles shot down "
            "over Saudi Arabia · Strong quake shakes Peru")
    ds = fit_size(d, deck, SERIF, CW - 30, 20, 14)
    fd = F(SERIF, ds)
    dx = (W - tw(d, deck, fd)) // 2
    fake_italic(img, (dx - 6, y, dx + int(tw(d, deck, fd)) + 16, y + ds + 8),
                deck, fd, INK)
    y += ds + 6
    d.rectangle([MX, y, RX, y + 1], fill=RULE)
    y += 5

    # stat strip
    cell = CW / 6.0
    fn = F(SERIF_B, 31)
    fc = F(SANS, 12)
    cap_lines = [wrap(d, cap, fc, cell - 8) for _, cap in STATS]
    stats_h = 37 + max(len(cl) for cl in cap_lines) * 15 + 2
    for i, (num, cap) in enumerate(STATS):
        cx = MX + i * cell
        center(d, cx + cell / 2, y, num, fn, DARKRED)
        for j, line in enumerate(cap_lines[i]):
            center(d, cx + cell / 2, y + 37 + j * 15, line, fc, INK)
        if i:
            d.line([(cx, y + 4), (cx, y + stats_h - 8)], fill=GREY, width=1)
    y += stats_h + 5

    # region bar
    bx = MX
    for label, wseg, bg, fg in REGIONS:
        d.rectangle([bx, y, bx + wseg, y + 28], fill=bg)
        fs = fit_size(d, label, SANS_B, wseg - 8, 13, 9)
        center(d, bx + wseg / 2, y + (28 - fs) / 2 - 2, label, F(SANS_B, fs), fg)
        bx += wseg
    y += 33

    # heroes
    hero_y = y
    ill_h = 84
    col_w = (CW - 28) // 3
    fb = F(SANS, 14)
    hero_bodies = [wrap(d, hz["body"], fb, col_w - 4) for hz in HEROES]
    max_body = max(len(b) for b in hero_bodies)
    for i, hz in enumerate(HEROES):
        x = MX + i * (col_w + 14)
        hz["scene"](d, x, hero_y, col_w, ill_h)
        banner(d, x, hero_y, col_w, 20, hz["banner"], 13)
        tagchip(d, x + col_w, hero_y + ill_h, hz["chip"], 9)
        # small tag bottom-left on illustration, clear of the badge
        ft = F(SANS_B, 9)
        tagw = tw(d, hz["tag"], ft) + 10
        d.rectangle([x + 33, hero_y + ill_h - 16, x + 33 + tagw,
                     hero_y + ill_h], fill=(20, 18, 16))
        d.text((x + 38, hero_y + ill_h - 14), hz["tag"], font=ft,
               fill=(255, 246, 220))
        badge(d, x + 15, hero_y + ill_h + 2, 14, hz["num"], 13)
        d.text((x + 36, hero_y + ill_h + 3), hz["tagline"],
               font=F(SANS_B, 13), fill=RED)
        hs = fit_lines(d, hz["headline"], SERIF_B, col_w - 4, 2, 25, 18)
        fh = F(SERIF_B, hs)
        ly = hero_y + ill_h + 22
        for line in wrap(d, hz["headline"], fh, col_w - 4):
            d.text((x, ly), line, font=fh, fill=INK)
            ly += hs + 3
        by = hero_y + ill_h + 78
        for line in hero_bodies[i]:
            d.text((x, by), line, font=fb, fill=INK)
            by += 16
    y = hero_y + ill_h + 78 + max_body * 16 + 6

    # briefs: two rows of five
    bw = (CW - 40) // 5
    for row in range(2):
        ry = y + row * 112
        for c in range(5):
            num, blabel, chip, head, text = BRIEFS[row * 5 + c]
            x = MX + c * (bw + 10)
            BRIEF_SCENES[row * 5 + c](d, x, ry, bw, 44)
            banner(d, x, ry, bw, 15, blabel, 9)
            tagchip(d, x + bw, ry + 44, chip, 8)
            badge(d, x + 10, ry + 45, 10, num, 10)
            hs = fit_lines(d, head, SANS_B, bw - 2, 2, 13, 10)
            fh = F(SANS_B, hs)
            ly = ry + 50
            for line in wrap(d, head, fh, bw - 2):
                d.text((x, ly), line, font=fh, fill=INK)
                ly += hs + 2
            ft = F(SANS, 12)
            ty = ry + 82
            for line in wrap(d, text, ft, bw - 2):
                d.text((x, ty), line, font=ft, fill=INK)
                ty += 14
    y += 2 * 112 + 2

    # bottom band: map + index (index height is independent of the map)
    band_y = y
    map_h = 144
    d.text((MX, band_y), "WHERE IT HAPPENED", font=F(SANS_B, 13), fill=RED)
    draw_map(d, MX, band_y + 17, 252, map_h)
    ix = MX + 252 + 14
    iw = RX - ix
    ititle = "ALSO ON SATURDAY 21 NOVEMBER 2026 — 22 MORE STORIES"
    fs = fit_size(d, ititle, SANS_B, iw, 14, 10)
    d.text((ix, band_y), ititle, font=F(SANS_B, fs), fill=INK)
    items_top = band_y + 19
    items_h = 206
    colw = (iw - 24) // 3
    placed = False
    used_h = 0
    for size in (11, 10, 9):
        fb_, fr_ = F(SANS_B, size), F(SANS, size)
        fnr = F(SANS_B, size)
        lh = size + 2
        cols, cur_col, cur_y = [], [], items_top
        ok = True
        for num, lead, rest in INDEX:
            segs = [(str(num) + " ", fnr, RED), (lead + " ", fb_, INK),
                    (rest, fr_, INK)]
            lines = wrap_rich(d, segs, colw)
            need = len(lines) * lh + 1
            if cur_y + need > items_top + items_h and cur_col:
                cols.append(cur_col)
                cur_col, cur_y = [], items_top
                if len(cols) > 2:
                    ok = False
                    break
            cur_col.append((lines, cur_y))
            cur_y += need
        if ok:
            cols.append(cur_col)
            used_h = max(ly + len(lines) * lh
                         for col in cols for lines, ly in col) - items_top
            for ci, col in enumerate(cols):
                for lines, ly in col:
                    draw_rich(d, lines, ix + ci * (colw + 12), ly, lh)
            placed = True
            break
    if not placed:
        raise SystemExit("index does not fit")
    y = band_y + 19 + max(map_h - 1, used_h) + 6

    # date check
    avail = 1004 - y
    for size, lh in ((12, 15), (11, 14), (10, 13)):
        lines = wrap_rich(d, date_check_segments(size), CW - 16)
        if len(lines) * lh + 12 <= avail:
            break
    d.rectangle([MX, y, RX, y + len(lines) * lh + 12], outline=RED, width=2)
    draw_rich(d, lines, MX + 8, y + 6, lh)
    y += len(lines) * lh + 18

    # footer
    foot = ("Every story happened, or was first reported, on Saturday 21 "
            "November 2026 · Officials' counts and claims are attributed · "
            "Sources named beside each story · Original drawings")
    fs = fit_size(d, foot, SANS, CW, 11, 8)
    center(d, W // 2, 1008, foot, F(SANS, fs), GREY)

    img.save("entry.png")
    print("final y:", y)


if __name__ == "__main__":
    main()
