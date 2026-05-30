#!/usr/bin/env python3
"""
Generates all brand raster assets for Exactly from a single drawn mark.
Run:  python assets/generate-icons.py
Outputs (repo root): favicon.ico, apple-touch-icon.png, icon-192.png,
icon-512.png, maskable-512.png, og-image.png
The vector favicon.svg is hand-authored and not produced here.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Brand palette
ACCENT_TOP = (193, 74, 35)   # #c14a23
ACCENT_BOT = (140, 48, 20)   # #8c3014
CREAM = (245, 241, 232)      # #f5f1e8
INK = (28, 26, 23)           # #1c1a17
INK_SOFT = (74, 70, 63)      # #4a463f
ACCENT = (181, 66, 31)       # #b5421f
SS = 4                       # supersampling factor for crisp edges


def _gradient_square(size):
    """Vertical accent gradient as an RGB image."""
    grad = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / (size - 1)
        col = tuple(int(ACCENT_TOP[i] + (ACCENT_BOT[i] - ACCENT_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (size, y)], fill=col)
    return grad


def make_mark(out_size, rounded=True, pad_ratio=0.0):
    """The 'precision target' mark: gradient tile + concentric ring + dot.
    pad_ratio insets the whole tile (used for maskable safe zone)."""
    s = out_size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    pad = int(s * pad_ratio)
    tile = s - 2 * pad
    grad = _gradient_square(tile)

    mask = Image.new("L", (tile, tile), 0)
    md = ImageDraw.Draw(mask)
    if rounded:
        md.rounded_rectangle([0, 0, tile - 1, tile - 1], radius=int(tile * 0.23), fill=255)
    else:
        md.rectangle([0, 0, tile - 1, tile - 1], fill=255)
    img.paste(grad, (pad, pad), mask)

    d = ImageDraw.Draw(img)
    cx = cy = s / 2
    R = tile * 0.27
    ring_w = max(1, int(tile * 0.075))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=CREAM + (255,), width=ring_w)
    r2 = tile * 0.105
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=CREAM + (255,))

    return img.resize((out_size, out_size), Image.LANCZOS)


def _font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_og():
    """1200x630 social share card."""
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # soft brand blobs
    for (cx, cy, rad, col) in [(120, -40, 360, (181, 66, 31)), (1120, 70, 300, (47, 111, 79))]:
        blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blob)
        bd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col + (16,))
        img.paste(Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB"), (0, 0))

    # logo mark
    mark = make_mark(150)
    img.paste(mark, (90, 96), mark)

    serif = _font(["georgiab.ttf", "Georgia Bold.ttf", "times.ttf", "DejaVuSerif-Bold.ttf"], 96)
    serif_i = _font(["georgiaz.ttf", "georgiai.ttf", "timesi.ttf", "DejaVuSerif-Italic.ttf"], 96)
    body = _font(["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"], 38)
    small = _font(["seguisb.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"], 30)

    # wordmark "Exactly" with accent italic "ly"
    tx, ty = 270, 110
    d.text((tx, ty), "Exact", font=serif, fill=INK)
    w_exact = d.textlength("Exact", font=serif)
    d.text((tx + w_exact, ty), "ly", font=serif_i, fill=ACCENT)

    # subtitle
    d.text((272, 250), "Compress images · Passport photos · Convert data",
           font=body, fill=INK_SOFT)

    # value line
    d.text((92, 430), "Get files to the exact size — free, no upload, no watermark.",
           font=body, fill=INK)

    # privacy pill
    pill = "100% in your browser — nothing is uploaded"
    pw = d.textlength(pill, font=small)
    px, py = 92, 520
    d.rounded_rectangle([px, py, px + pw + 56, py + 56], radius=28,
                        fill=(47, 111, 79, 255))
    d.text((px + 28, py + 12), pill, font=small, fill=CREAM)

    img.save(os.path.join(ROOT, "og-image.png"), "PNG")


def main():
    # favicon.ico (multi-size from one mark)
    make_mark(256).save(os.path.join(ROOT, "favicon.ico"),
                        sizes=[(16, 16), (32, 32), (48, 48)])
    # apple touch icon — opaque, full bleed (iOS rounds it)
    make_mark(180, rounded=False).save(os.path.join(ROOT, "apple-touch-icon.png"), "PNG")
    # PWA icons
    make_mark(192).save(os.path.join(ROOT, "icon-192.png"), "PNG")
    make_mark(512).save(os.path.join(ROOT, "icon-512.png"), "PNG")
    # maskable — full bleed with safe-zone padding
    make_mark(512, rounded=False, pad_ratio=0.0).save(os.path.join(ROOT, "maskable-512.png"), "PNG")
    make_og()
    print("Generated: favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png, maskable-512.png, og-image.png")


if __name__ == "__main__":
    main()
