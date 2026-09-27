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
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "themes", "i3green")
ICONS = os.path.join(OUT, "icons")
W, H = 1920, 1080

# Same palette as .config/i3/config
GREEN = (0x12, 0x95, 0x4D)
DARK_GREEN = (0x0B, 0x59, 0x2E)
PANEL = (0x0E, 0x14, 0x11)

ICON = 40          # must equal icon_width/icon_height in theme.txt
SS = 4             # supersampling for smooth shapes

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def save(img, path):
    img.save(path, "PNG", optimize=True)  # PIL never writes interlaced PNGs


# Centered menu panel (theme.txt positions are derived from these)
PX, PY, PW, PH = 570, 220, 780, 600


def shard(d, cx, cy, ang, length, width, color):
    """Thin triangle pointing along ang, base at (cx, cy)."""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    tip = (cx + dx * length, cy + dy * length)
    b1 = (cx + nx * width / 2, cy + ny * width / 2)
    b2 = (cx - nx * width / 2, cy - ny * width / 2)
    back = (cx - dx * length * 0.15, cy - dy * length * 0.15)
    d.polygon([b1, tip, b2, back], fill=color)


def shard_layer(rng, count, size, blur, alpha, green_ratio):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W / 2, H / 2
    for _ in range(count):
        a = rng.uniform(0, 2 * math.pi)
        # keep the middle empty: radius in ellipse units, 0.7 .. 1.2
        r = rng.uniform(0.7, 1.2)
        x, y = cx + math.cos(a) * r * W * 0.55, cy + math.sin(a) * r * H * 0.62
        ang = math.atan2(y - cy, x - cx) + rng.uniform(-0.5, 0.5)
        if rng.random() < 0.5:
            ang += math.pi                     # some point inwards
        length = rng.uniform(0.3, 1.0) * size
        width = rng.uniform(0.04, 0.16) * size
        if rng.random() < green_ratio:
            g = rng.choice([GREEN, (0x3C, 0xC8, 0x5A), (0x7E, 0xE0, 0x4A), DARK_GREEN])
        else:
            v = rng.randint(28, 70)
            g = (v, v + 4, v + 2)
        shard(d, x, y, ang, length, width, g + (int(alpha * rng.uniform(0.5, 1.0)),))
    layer = layer.filter(ImageFilter.GaussianBlur(blur)) if blur else layer
    # clear a soft margin around the panel so nothing pokes out from under it
    keep = Image.new("L", (W, H), 255)
    ImageDraw.Draw(keep).rounded_rectangle([PX - 50, PY - 50, PX + PW + 50, PY + PH + 90],
                                           radius=60, fill=0)
    keep = keep.filter(ImageFilter.GaussianBlur(25))
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (W, H), 0), keep))
    return layer


def glow(img, x, y, radius, color, strength):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([x - radius, y - radius, x + radius, y + radius],
                                  fill=color + (strength,))
    return Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(radius * 0.6)))


def background():
    rng = random.Random(15)

    # radial base: dark green-black centre -> black edges
    base = Image.new("L", (W, H))
    bd = ImageDraw.Draw(base)
    for i in range(60, 0, -1):
        t = i / 60
        bd.ellipse([W / 2 - t * W * 0.8, H / 2 - t * H * 0.8,
                    W / 2 + t * W * 0.8, H / 2 + t * H * 0.8], fill=int(255 * (1 - t)))
    base = base.filter(ImageFilter.GaussianBlur(40))
    img = Image.composite(Image.new("RGBA", (W, H), (0x10, 0x1C, 0x16, 255)),
                          Image.new("RGBA", (W, H), (0x02, 0x03, 0x03, 255)), base)

    img = glow(img, W / 2, H / 2, 520, DARK_GREEN, 70)
    img = glow(img, 260, 880, 220, GREEN, 60)
    img = glow(img, 1680, 170, 180, GREEN, 50)

    img = Image.alpha_composite(img, shard_layer(rng, 240, 90, 6, 120, 0.25))   # far
    img = Image.alpha_composite(img, shard_layer(rng, 140, 150, 2.5, 180, 0.3))  # mid
    img = Image.alpha_composite(img, shard_layer(rng, 40, 260, 0.7, 225, 0.35))    # near

    # a few bright sparks near the glows
    for gx, gy in [(260, 880), (1680, 170)]:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for _ in range(12):
            x, y = gx + rng.gauss(0, 120), gy + rng.gauss(0, 90)
            shard(d, x, y, rng.uniform(0, 2 * math.pi), rng.uniform(15, 50), rng.uniform(3, 7),
                  (0xA8, 0xF0, 0x6A, 230))
        img = Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(0.8)))

    # frosted centred panel
    blurred = img.crop((PX, PY, PX + PW, PY + PH)).filter(ImageFilter.GaussianBlur(22))
    img.paste(blurred, (PX, PY))
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    od.rounded_rectangle([PX, PY, PX + PW, PY + PH], radius=24, fill=PANEL + (200,),
                         outline=GREEN + (130,), width=2)
    od.rectangle([W // 2 - 45, PY + 105, W // 2 + 45, PY + 109], fill=GREEN + (255,))
    img = Image.alpha_composite(img, over)

    # fine grain against banding in the dark gradients
    noise = Image.effect_noise((W, H), 12).convert("RGBA")
    noise.putalpha(10)
    img = Image.alpha_composite(img, noise)
    save(img.convert("RGB"), os.path.join(OUT, "background.png"))


def selection():
    """9-slice rounded highlight bar: select_{nw,n,ne,w,c,e,sw,s,se}.png"""
    r = 12
    size = r * 2 + 4
    big = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle(
        [0, 0, size * SS - 1, size * SS - 1], radius=r * SS,
        fill=DARK_GREEN + (230,), outline=GREEN + (255,), width=2 * SS)
    bar = big.resize((size, size), Image.LANCZOS)
    m = size - r
    boxes = {
        "nw": (0, 0, r, r), "n": (r, 0, m, r), "ne": (m, 0, size, r),
        "w": (0, r, r, m), "c": (r, r, m, m), "e": (m, r, size, m),
        "sw": (0, m, r, size), "s": (r, m, m, size), "se": (m, m, size, size),
    }
    for name, box in boxes.items():
        save(bar.crop(box), os.path.join(OUT, f"select_{name}.png"))


def icon_canvas():
    return Image.new("RGBA", (ICON * SS, ICON * SS), (0, 0, 0, 0))


def finish(img, *names):
    img = img.resize((ICON, ICON), Image.LANCZOS)
    for n in names:
        save(img, os.path.join(ICONS, f"{n}.png"))


def icons():
    S = ICON * SS
    white = (0xF3, 0xF4, 0xF5, 255)

    # Windows: four panes
    img = icon_canvas(); d = ImageDraw.Draw(img)
    g, pad = 3 * SS, 4 * SS
    half = (S - 2 * pad - g) // 2
    for i in range(2):
        for j in range(2):
            x0, y0 = pad + i * (half + g), pad + j * (half + g)
            d.rectangle([x0, y0, x0 + half, y0 + half], fill=(0x3A, 0xA0, 0xE8, 255))
    finish(img, "windows")

    # Ubuntu / Linux: terminal prompt in a rounded square
    img = icon_canvas(); d = ImageDraw.Draw(img)
    d.rounded_rectangle([2 * SS, 4 * SS, S - 2 * SS, S - 4 * SS], radius=6 * SS,
                        fill=(0x14, 0x1C, 0x18, 255), outline=GREEN + (255,), width=3 * SS)
    lw = 4 * SS
    d.line([(10 * SS, 13 * SS), (18 * SS, 20 * SS), (10 * SS, 27 * SS)], fill=GREEN + (255,),
           width=lw, joint="curve")
    d.line([(21 * SS, 27 * SS), (30 * SS, 27 * SS)], fill=white, width=lw)
    finish(img, "ubuntu", "gnu-linux", "linux")

    # Recovery / memtest / generic: circle with a wrench-ish mark -> keep it simple: gear
    img = icon_canvas(); d = ImageDraw.Draw(img)
    c = S // 2
    for k in range(8):
        a = k * math.pi / 4
        x, y = c + math.cos(a) * 14 * SS, c + math.sin(a) * 14 * SS
        d.ellipse([x - 4 * SS, y - 4 * SS, x + 4 * SS, y + 4 * SS], fill=(0x9A, 0xA3, 0x9F, 255))
    d.ellipse([c - 13 * SS, c - 13 * SS, c + 13 * SS, c + 13 * SS], fill=(0x9A, 0xA3, 0x9F, 255))
    d.ellipse([c - 6 * SS, c - 6 * SS, c + 6 * SS, c + 6 * SS], fill=(0, 0, 0, 0))
    finish(img, "os", "recovery", "memtest", "efi")


def fonts():
    """grub-mkfont -> .pf2 in the theme root (00_header loadfont's every *.pf2 there)."""
    specs = [
        (FONT_REG, 24, "dejavu_24"),
        (FONT_BOLD, 24, "dejavu_bold_24"),
        (FONT_BOLD, 40, "dejavu_bold_40"),
        (FONT_REG, 18, "dejavu_18"),
        (FONT_MONO, 18, "dejavu_mono_18"),
    ]
    for ttf, size, name in specs:
        subprocess.run(["grub-mkfont", "-s", str(size), "-r", "0x20-0x24F,0x2000-0x206F,0x2190-0x21FF,0x25A0-0x25FF", "-o",
                        os.path.join(OUT, f"{name}.pf2"), ttf], check=True)


if __name__ == "__main__":
    os.makedirs(ICONS, exist_ok=True)
    background()
    selection()
    icons()
    fonts()
    print("theme assets written to", OUT)
