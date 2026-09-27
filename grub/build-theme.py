#!/usr/bin/env python3
"""Generate the i3green GRUB theme assets (background, selection bar, icons, fonts).

The background is procedural (dark shards + green glow, same style as the desktop
wallpaper) so the centred menu sits on empty space.

Run: python3 grub/build-theme.py   -> writes grub/themes/i3green/
"""
import math
import os
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "themes", "i3green")
ICONS = os.path.join(OUT, "icons")
W, H = 1920, 1080

# Same palette as .config/i3/config
GREEN = (0x12, 0x95, 0x4D)
DARK_GREEN = (0x0B, 0x59, 0x2E)
PANEL = (0x0E, 0x14, 0x11)

ICON = 24          # must equal icon_width/icon_height in theme.txt
SS = 4             # supersampling for smooth shapes

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def save(img, path):
    img.save(path, "PNG", optimize=True)  # PIL never writes interlaced PNGs


# Clear area in the middle kept free of shards (title + menu sit here).
# Nothing panel-like is baked into the background: it would stay on screen
# after the menu closes.
PX, PY, PW, PH = 620, 290, 680, 500

# --- background --------------------------------------------------------------
# Rendered at 2x as float RGB (0..1) so light can be added, then downsampled.
K = 2
BW, BH = W * K, H * K
CX, CY = BW / 2, BH / 2


def arr(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r * K)) if r else img


def over(canvas, layer):
    """Alpha-composite an RGBA PIL layer onto the float canvas."""
    a = arr(layer)
    alpha = a[..., 3:4]
    return canvas * (1 - alpha) + a[..., :3] * alpha


def add(canvas, layer, gain=1.0):
    """Additive light: RGBA layer, colour premultiplied by alpha."""
    a = arr(layer)
    return canvas + a[..., :3] * a[..., 3:4] * gain


def panel_keep():
    """1 outside the panel, 0 under it (soft), so nothing pokes out from beneath."""
    keep = Image.new("L", (BW, BH), 255)
    ImageDraw.Draw(keep).rounded_rectangle(
        [(PX - 60) * K, (PY - 60) * K, (PX + PW + 60) * K, (PY + PH + 100) * K],
        radius=70 * K, fill=0)
    return blur(keep, 30)


def masked(layer, keep):
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", layer.size, 0), keep))
    return layer


def fog(rng):
    """Low-frequency noise: gives the dark background some depth instead of a flat gradient."""
    small = Image.fromarray((np.random.default_rng(rng.randint(0, 1 << 30))
                             .random((27, 48)) * 255).astype(np.uint8), "L")
    return arr(blur(small.resize((BW, BH), Image.BICUBIC), 40))[..., None]


def place(rng, rmin, rmax):
    """Random point in an elliptical ring around the centre (radii in ellipse units)."""
    a = rng.uniform(0, 2 * math.pi)
    r = rng.uniform(rmin, rmax)
    return CX + math.cos(a) * r * BW * 0.5, CY + math.sin(a) * r * BH * 0.56


def crystal(d, glow_d, x, y, size, rng, green, alpha):
    """Two-facet shard flying away from the centre, lit from the centre."""
    out = math.atan2(y - CY, x - CX)
    ang = out + rng.gauss(0, 0.35)
    length = size * rng.uniform(0.45, 1.0)
    width = length * rng.uniform(0.08, 0.22)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    back = (x - dx * length * 0.25, y - dy * length * 0.25)
    tip = (x + dx * length, y + dy * length)
    k1, k2 = rng.uniform(0.15, 0.45), rng.uniform(0.15, 0.45)
    s1 = (x + dx * length * k1 + nx * width * rng.uniform(0.4, 0.6),
          y + dy * length * k1 + ny * width * rng.uniform(0.4, 0.6))
    s2 = (x + dx * length * k2 - nx * width * rng.uniform(0.4, 0.6),
          y + dy * length * k2 - ny * width * rng.uniform(0.4, 0.6))

    # facet facing the centre gets the light
    to_c = (CX - x, CY - y)
    lit_first = (nx * to_c[0] + ny * to_c[1]) > 0
    if green:
        base = np.array(rng.choice([(18, 149, 77), (46, 190, 90), (120, 220, 70), (11, 110, 50)]))
    else:
        v = rng.uniform(34, 78)
        base = np.array((v, v * 1.06, v * 1.03))
    light = tuple(int(c) for c in np.clip(base * 1.55 + 12, 0, 255))
    dark = tuple(int(c) for c in np.clip(base * 0.55, 0, 255))
    fa, fb = (light, dark) if lit_first else (dark, light)
    d.polygon([back, s1, tip], fill=fa + (alpha,))
    d.polygon([back, s2, tip], fill=fb + (alpha,))
    # crisp highlight along the ridge and the lit edge
    hi = tuple(int(c) for c in np.clip(base * 2.2 + 40, 0, 255)) + (int(alpha * 0.9),)
    d.line([back, tip], fill=hi, width=max(1, int(K * 0.8)))
    d.line([s1 if lit_first else s2, tip], fill=hi, width=max(1, int(K * 0.6)))
    if green and glow_d is not None:
        glow_d.polygon([back, s1, tip, s2], fill=tuple(int(c) for c in base) + (255,))
    return back


def shard_layers(rng, keep, count, size, rmin, rmax, green_ratio, alpha, depth_blur, trails):
    layer = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    emit = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    trail = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d, ed, td = ImageDraw.Draw(layer), ImageDraw.Draw(emit), ImageDraw.Draw(trail)
    for _ in range(count):
        x, y = place(rng, rmin, rmax)
        green = rng.random() < green_ratio
        back = crystal(d, ed, x, y, size * K, rng, green, int(alpha * rng.uniform(0.6, 1.0)))
        if trails and rng.random() < 0.5:
            # faint motion streak back towards the centre
            t = rng.uniform(0.12, 0.3)
            end = (back[0] + (CX - back[0]) * t, back[1] + (CY - back[1]) * t)
            col = (90, 200, 110) if green else (110, 120, 115)
            for i in range(6):
                f0, f1 = i / 6, (i + 1) / 6
                p0 = (back[0] + (end[0] - back[0]) * f0, back[1] + (end[1] - back[1]) * f0)
                p1 = (back[0] + (end[0] - back[0]) * f1, back[1] + (end[1] - back[1]) * f1)
                td.line([p0, p1], fill=col + (int(60 * (1 - f0)),), width=max(1, K))
    return (masked(blur(layer, depth_blur), keep), masked(blur(emit, depth_blur), keep),
            masked(blur(trail, 0.6), keep))


def background():
    rng = random.Random(15)
    keep = panel_keep()
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    rad = np.sqrt(((xx - CX) / (BW * 0.5)) ** 2 + ((yy - CY) / (BH * 0.5)) ** 2)[..., None]

    # base: deep green-black, brighter towards the centre, with foggy variation
    canvas = np.array([0.012, 0.018, 0.016]) + np.array([0.05, 0.085, 0.065]) * np.clip(1.25 - rad, 0, 1) ** 1.6
    canvas = canvas * (0.75 + 0.5 * fog(rng))

    # soft green light behind the panel and in two corners
    for gx, gy, gr, gs in [(CX, CY, 560, 0.10), (300 * K, 880 * K, 300, 0.30), (1650 * K, 180 * K, 260, 0.24)]:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([gx - gr * K, gy - gr * K, gx + gr * K, gy + gr * K],
                                  fill=(18, 149, 77, 255))
        canvas = add(canvas, blur(g, gr * 0.7), gs * 2.2)

    # light rays from the centre
    rays = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for _ in range(170):
        a = rng.uniform(0, 2 * math.pi)
        r0, r1 = rng.uniform(0.35, 0.6), rng.uniform(0.8, 1.6)
        p0 = (CX + math.cos(a) * r0 * BW * 0.5, CY + math.sin(a) * r0 * BH * 0.56)
        p1 = (CX + math.cos(a) * r1 * BW * 0.5, CY + math.sin(a) * r1 * BH * 0.56)
        rd.line([p0, p1], fill=(40, 190, 100, rng.randint(10, 45)), width=rng.choice([1, 1, 2, 3]) * K)
    canvas = add(canvas, masked(blur(rays, 1.2), keep), 0.9)

    # bokeh and dust
    bokeh = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bokeh)
    for _ in range(60):
        x, y = place(rng, 0.6, 1.3)
        r = rng.uniform(6, 30) * K
        bd.ellipse([x - r, y - r, x + r, y + r], fill=(60, 200, 110, rng.randint(12, 40)),
                   outline=(120, 230, 150, rng.randint(20, 60)), width=K)
    canvas = add(canvas, masked(blur(bokeh, 3), keep), 1.0)

    # three depth layers of crystals: far (soft, dim), mid, near (sharp, big)
    for count, size, rmin, rmax, gr, al, db, tr in [
        (260, 60, 0.62, 1.35, 0.22, 150, 3.0, False),
        (150, 120, 0.68, 1.3, 0.28, 215, 1.0, True),
        (38, 260, 0.78, 1.25, 0.32, 245, 0, True),
    ]:
        body, emit, trail = shard_layers(rng, keep, count, size, rmin, rmax, gr, al, db, tr)
        canvas = add(canvas, trail, 0.8)
        canvas = over(canvas, body)
        # bloom around the green crystals
        canvas = add(canvas, blur(emit, 6), 0.35)
        canvas = add(canvas, blur(emit, 22), 0.25)

    # glowing sparks
    dust = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(420):
        x, y = place(rng, 0.5, 1.4)
        r = rng.choice([0.6, 0.8, 1.0, 1.5, 2.2]) * K
        dd.ellipse([x - r, y - r, x + r, y + r], fill=(170, 255, 150, rng.randint(60, 220)))
    dust = masked(dust, keep)
    canvas = add(canvas, blur(dust, 0.4), 1.0)
    canvas = add(canvas, blur(dust, 4), 0.8)

    # vignette
    canvas *= np.clip(1.15 - 0.35 * rad ** 2, 0.35, 1.0)

    img = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    img = img.resize((W, H), Image.LANCZOS)

    # fine grain against banding in the dark gradients
    noise = Image.effect_noise((W, H), 12).convert("RGBA")
    noise.putalpha(9)
    img = Image.alpha_composite(img, noise)
    save(img.convert("RGB"), os.path.join(OUT, "background.png"))


def selection():
    """9-slice rounded highlight bar: select_{nw,n,ne,w,c,e,sw,s,se}.png"""
    r = 6          # slice size; theme.txt item_padding must be >= this
    size = r * 2 + 4
    big = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle(
        [0, 0, size * SS - 1, size * SS - 1], radius=r * SS,
        fill=DARK_GREEN + (200,), outline=GREEN + (255,), width=1 * SS)
    bar = big.resize((size, size), Image.LANCZOS)
    m = size - r
    boxes = {
        "nw": (0, 0, r, r), "n": (r, 0, m, r), "ne": (m, 0, size, r),
        "w": (0, r, r, m), "c": (r, r, m, m), "e": (m, r, size, m),
        "sw": (0, m, r, size), "s": (r, m, m, size), "se": (m, m, size, size),
    }
    for name, box in boxes.items():
        save(bar.crop(box), os.path.join(OUT, f"select_{name}.png"))


def accent():
    """Short green line under the title (an image component, gone with the menu)."""
    save(Image.new("RGBA", (60, 3), GREEN + (255,)), os.path.join(OUT, "accent.png"))


def terminal_box():
    """Flat near-black box behind the terminal (full screen): when the menu closes
    to boot, the screen goes plain dark instead of showing a framed square."""
    for name in ("nw", "n", "ne", "w", "c", "e", "sw", "s", "se"):
        save(Image.new("RGB", (4, 4), (0x05, 0x08, 0x07)), os.path.join(OUT, f"term_{name}.png"))


def icon_canvas():
    return Image.new("RGBA", (ICON * SS, ICON * SS), (0, 0, 0, 0))


def finish(img, *names):
    img = img.resize((ICON, ICON), Image.LANCZOS)
    for n in names:
        save(img, os.path.join(ICONS, f"{n}.png"))


def icons():
    # shapes are designed on a 40px grid; U scales them to ICON
    S = ICON * SS
    U = SS * ICON / 40
    white = (0xF3, 0xF4, 0xF5, 255)

    # Windows: four panes
    img = icon_canvas(); d = ImageDraw.Draw(img)
    g, pad = round(3 * U), round(3 * U)
    half = (S - 2 * pad - g) // 2
    for i in range(2):
        for j in range(2):
            x0, y0 = pad + i * (half + g), pad + j * (half + g)
            d.rectangle([x0, y0, x0 + half, y0 + half], fill=(0x3A, 0xA0, 0xE8, 255))
    finish(img, "windows")

    # Ubuntu / Linux: terminal prompt in a rounded square
    img = icon_canvas(); d = ImageDraw.Draw(img)
    d.rounded_rectangle([2 * U, 4 * U, S - 2 * U, S - 4 * U], radius=6 * U,
                        fill=(0x14, 0x1C, 0x18, 255), outline=GREEN + (255,), width=round(3 * U))
    lw = round(4 * U)
    d.line([(10 * U, 13 * U), (18 * U, 20 * U), (10 * U, 27 * U)], fill=GREEN + (255,),
           width=lw, joint="curve")
    d.line([(21 * U, 27 * U), (30 * U, 27 * U)], fill=white, width=lw)
    finish(img, "ubuntu", "gnu-linux", "linux")

    # Recovery / memtest / generic: circle with a wrench-ish mark -> keep it simple: gear
    img = icon_canvas(); d = ImageDraw.Draw(img)
    c = S // 2
    for k in range(8):
        a = k * math.pi / 4
        x, y = c + math.cos(a) * 14 * U, c + math.sin(a) * 14 * U
        d.ellipse([x - 4 * U, y - 4 * U, x + 4 * U, y + 4 * U], fill=(0x9A, 0xA3, 0x9F, 255))
    d.ellipse([c - 13 * U, c - 13 * U, c + 13 * U, c + 13 * U], fill=(0x9A, 0xA3, 0x9F, 255))
    d.ellipse([c - 6 * U, c - 6 * U, c + 6 * U, c + 6 * U], fill=(0, 0, 0, 0))
    finish(img, "os", "recovery", "memtest", "efi")


def fonts():
    """grub-mkfont -> .pf2 in the theme root (00_header loadfont's every *.pf2 there)."""
    specs = [
        (FONT_REG, 18, "dejavu_18"),
        (FONT_BOLD, 28, "dejavu_bold_28"),
        (FONT_REG, 16, "dejavu_16"),
        (FONT_REG, 14, "dejavu_14"),
        (FONT_MONO, 16, "dejavu_mono_16"),
    ]
    for ttf, size, name in specs:
        subprocess.run(["grub-mkfont", "-s", str(size), "-r", "0x20-0x24F,0x2000-0x206F,0x2190-0x21FF,0x25A0-0x25FF", "-o",
                        os.path.join(OUT, f"{name}.pf2"), ttf], check=True)


if __name__ == "__main__":
    os.makedirs(ICONS, exist_ok=True)
    background()
    selection()
    accent()
    terminal_box()
    icons()
    fonts()
    print("theme assets written to", OUT)
