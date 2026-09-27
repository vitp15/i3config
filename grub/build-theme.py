#!/usr/bin/env python3
"""Generate the i3green GRUB theme assets (background, selection bar, icons, fonts).

Run: python3 grub/build-theme.py   -> writes grub/themes/i3green/
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
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


def background():
    src = Image.open(os.path.join(REPO, "wallpapers", "background.jpg")).convert("RGB")
    # cover-crop 16:10 -> 16:9
    scale = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    left, top = (src.width - W) // 2, (src.height - H) // 2
    img = src.crop((left, top, left + W, top + H)).convert("RGBA")

    # darken towards the right where the menu lives
    shade = Image.new("L", (W, H))
    d = ImageDraw.Draw(shade)
    for x in range(W):
        t = max(0.0, min(1.0, (x - W * 0.35) / (W * 0.25)))
        d.line([(x, 0), (x, H)], fill=int(90 + 110 * t))
    img = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), img, shade)

    # frosted panel behind the menu
    px, py, pw, ph = int(W * 0.52), int(H * 0.16), int(W * 0.40), int(H * 0.70)
    blurred = img.crop((px, py, px + pw, py + ph)).filter(ImageFilter.GaussianBlur(18))
    img.paste(blurred, (px, py))
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    od.rounded_rectangle([px, py, px + pw, py + ph], radius=22, fill=PANEL + (190,),
                         outline=GREEN + (120,), width=2)
    # accent line under the header
    od.rectangle([px + 48, py + 118, px + 48 + 90, py + 122], fill=GREEN + (255,))
    img = Image.alpha_composite(img, over)
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
    import math
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
