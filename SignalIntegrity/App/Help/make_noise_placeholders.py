"""Generate placeholder PNG images for the Statistical Noise help documentation.

Each placeholder is a light-gray box with a centered caption naming the image,
sized to match the sibling images already used in the help pages. These are
intended to be replaced later with real screen captures / symbol renderings.
"""
import os
from PIL import Image, ImageDraw, ImageFont

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "docs", "media")

# (filename, width, height)
# The statistical noise source device symbols are now rendered from the actual
# part pictures, so only the dialog screenshots remain as placeholders here.
IMAGES = [
    ("StatisticalNoiseDialog.png", 604, 483),
    ("StatisticalNoiseMeasurements.png", 604, 483),
]

BG = (245, 245, 245)
BORDER = (150, 150, 150)
TEXT = (90, 90, 90)


def _font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(label):
    # split CamelCase-ish name into words for readable wrapping
    out, word = [], ""
    for ch in label:
        if ch.isupper() and word and not word[-1].isupper():
            out.append(word)
            word = ch
        else:
            word += ch
    if word:
        out.append(word)
    return out


def make(path, w, h):
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER, width=2)
    label = os.path.splitext(os.path.basename(path))[0]
    font = _font(16 if w < 300 else 22)
    lines = ["(placeholder)"] + _wrap(label)
    heights = []
    widths = []
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + (len(lines) - 1) * 6
    y = (h - total_h) / 2
    for ln, lw, lh in zip(lines, widths, heights):
        d.text(((w - lw) / 2, y), ln, fill=TEXT, font=font)
        y += lh + 6
    img.save(path)
    print("wrote", path)


def main():
    os.makedirs(MEDIA_DIR, exist_ok=True)
    for name, w, h in IMAGES:
        make(os.path.join(MEDIA_DIR, name), w, h)


if __name__ == "__main__":
    main()
