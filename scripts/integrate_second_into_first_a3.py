from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

BASE_PATH = Path(r"D:\Downloads\微信图片_20260613163642_67_352.png")
INSERT_PATH = Path(r"D:\Downloads\微信图片_20260613212853_111_352.jpg")

# A3 portrait at 300 dpi.
A3_SIZE = (3508, 4961)

# Placement measured on the original first image.
# This is the largest rendering area in the upper-right quadrant.
INSERT_BOX_ORIGINAL = (520, 98, 1034, 357)


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / img.width, target_h / img.height)
    new_size = (round(img.width * scale), round(img.height * scale))
    resized = img.resize(new_size, Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def scaled_box(
    box: tuple[int, int, int, int],
    base_size: tuple[int, int],
    target_size: tuple[int, int],
) -> tuple[int, int, int, int]:
    sx = target_size[0] / base_size[0]
    sy = target_size[1] / base_size[1]
    x1, y1, x2, y2 = box
    return (round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy))


def soft_irregular_mask(size: tuple[int, int]) -> Image.Image:
    w, h = size
    mask = Image.new("L", size, 255)
    edge = max(34, min(w, h) // 15)
    px = mask.load()
    rng = random.Random(20260613)

    for y in range(h):
        for x in range(w):
            dist = min(x, y, w - 1 - x, h - 1 - y)
            if dist < edge:
                base_alpha = int(255 * (dist / edge) ** 0.55)
                jitter = rng.randint(-18, 18)
                px[x, y] = max(0, min(255, base_alpha + jitter))

    mask = mask.filter(ImageFilter.GaussianBlur(edge * 0.28))
    center = Image.new("L", size, 0)
    d = ImageDraw.Draw(center)
    d.rounded_rectangle(
        (edge // 2, edge // 2, w - edge // 2, h - edge // 2),
        radius=edge // 3,
        fill=255,
    )
    return Image.composite(Image.new("L", size, 255), mask, center)


def warm_match(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    img = ImageEnhance.Color(img).enhance(0.92)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    img = ImageEnhance.Brightness(img).enhance(1.02)

    warm = Image.new("RGBA", img.size, (239, 202, 138, 34))
    img = Image.alpha_composite(img, warm)

    paper = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(paper)
    rng = random.Random(7)
    for _ in range(max(1600, img.width * img.height // 3200)):
        x = rng.randrange(img.width)
        y = rng.randrange(img.height)
        a = rng.randrange(10, 28)
        color = rng.choice([(255, 239, 198, a), (129, 78, 33, a), (205, 144, 68, a)])
        d.point((x, y), fill=color)
    paper = paper.filter(ImageFilter.GaussianBlur(0.35))
    img = Image.alpha_composite(img, paper)
    return img


def add_label(base: Image.Image, box: tuple[int, int, int, int]) -> None:
    x1, y1, _, _ = box
    d = ImageDraw.Draw(base)
    # Recreate the original warm label style so the new rendering belongs to the board.
    label = "红光市场"
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf", 42)
    except Exception:
        from PIL import ImageFont

        font = ImageFont.load_default()
    pad_x, pad_y = 22, 10
    bbox = d.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.rounded_rectangle(
        (x1 + 18, y1 + 20, x1 + 18 + tw + pad_x * 2, y1 + 20 + th + pad_y * 2),
        radius=5,
        fill=(171, 83, 25, 235),
    )
    d.text((x1 + 18 + pad_x, y1 + 20 + pad_y - 4), label, font=font, fill=(255, 238, 204, 255))


def main() -> None:
    OUT.mkdir(exist_ok=True)

    original = Image.open(BASE_PATH).convert("RGB")
    insert = Image.open(INSERT_PATH).convert("RGB")

    base = original.resize(A3_SIZE, Image.Resampling.LANCZOS).convert("RGBA")
    box = scaled_box(INSERT_BOX_ORIGINAL, original.size, A3_SIZE)
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1

    patch = fit_cover(insert, (w, h))
    patch = warm_match(patch)
    mask = soft_irregular_mask((w, h))

    # Leave a trace of the original watercolor rendering at the edges.
    base.paste(patch, (x1, y1), mask)

    d = ImageDraw.Draw(base)
    d.rounded_rectangle((x1, y1, x2, y2), radius=8, outline=(144, 83, 39, 155), width=4)

    rgb = base.convert("RGB")
    png = OUT / "coal-town-a3-integrated-second-into-first.png"
    jpg = OUT / "coal-town-a3-integrated-second-into-first.jpg"
    pdf = OUT / "coal-town-a3-integrated-second-into-first.pdf"
    rgb.save(png, dpi=(300, 300))
    rgb.save(jpg, quality=95, dpi=(300, 300), subsampling=0)
    rgb.save(pdf, "PDF", resolution=300.0)

    print(png.resolve())
    print(jpg.resolve())
    print(pdf.resolve())


if __name__ == "__main__":
    main()
