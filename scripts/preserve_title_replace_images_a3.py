from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

BOARD = Path(r"D:\Downloads\微信图片_20260613163642_67_352.png")
PHOTO = Path(r"D:\Downloads\微信图片_20260613212853_111_352.jpg")

SRC_SIZE = (1054, 1492)
A3_SIZE = (3508, 4961)

FONT_SERIF = Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf")
FONT_SANS = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
FONT_FALLBACK = Path(r"C:\Windows\Fonts\simhei.ttf")


def font(size: int, serif: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_SERIF if serif and FONT_SERIF.exists() else FONT_SANS
    if not path.exists():
        path = FONT_FALLBACK
    return ImageFont.truetype(str(path), size)


def scale_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    sx = A3_SIZE[0] / SRC_SIZE[0]
    sy = A3_SIZE[1] / SRC_SIZE[1]
    x1, y1, x2, y2 = box
    return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)


def fit_cover(img: Image.Image, size: tuple[int, int], anchor: tuple[float, float]) -> Image.Image:
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    ax, ay = anchor
    left = max(0, min(nw - tw, round((nw - tw) * ax)))
    top = max(0, min(nh - th, round((nh - th) * ay)))
    return resized.crop((left, top, left + tw, top + th))


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def add_paper_grain(img: Image.Image, amount: int = 24) -> Image.Image:
    rng = random.Random(img.width * 17 + img.height * 31 + amount)
    grain = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grain)
    count = max(600, img.width * img.height // 2300)
    for _ in range(count):
        x = rng.randrange(img.width)
        y = rng.randrange(img.height)
        color = rng.choice([
            (255, 240, 205, rng.randrange(5, amount)),
            (145, 86, 35, rng.randrange(4, amount // 2 + 4)),
            (210, 146, 62, rng.randrange(4, amount // 2 + 5)),
        ])
        gd.point((x, y), fill=color)
    return Image.alpha_composite(img.convert("RGBA"), grain.filter(ImageFilter.GaussianBlur(0.35)))


def warm_photo(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    img = ImageEnhance.Color(img).enhance(1.04)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = Image.alpha_composite(img, Image.new("RGBA", img.size, (239, 198, 126, 26)))
    return add_paper_grain(img, 20)


def watercolor(img: Image.Image) -> Image.Image:
    base = warm_photo(img).filter(ImageFilter.GaussianBlur(0.45))
    edge = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)
    edge = ImageOps.autocontrast(edge)
    edge = ImageOps.invert(edge).point(lambda p: 255 if p > 120 else 170)
    line = Image.new("RGBA", img.size, (92, 57, 32, 0))
    line.putalpha(ImageOps.invert(edge).point(lambda p: int(p * 0.42)))
    wash = Image.alpha_composite(base, Image.new("RGBA", img.size, (247, 224, 179, 48)))
    return Image.alpha_composite(wash, line)


def sketch(img: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(img)
    edge = gray.filter(ImageFilter.FIND_EDGES)
    edge = ImageOps.autocontrast(edge)
    paper = Image.new("RGBA", img.size, (246, 229, 190, 255))
    lines = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lines.putalpha(edge.point(lambda p: min(210, int(p * 1.2))))
    tint = Image.new("RGBA", img.size, (80, 54, 35, 255))
    lines = Image.composite(tint, Image.new("RGBA", img.size, (0, 0, 0, 0)), lines.split()[-1])
    return add_paper_grain(Image.alpha_composite(paper, lines), 18)


def plan_style(img: Image.Image) -> Image.Image:
    base = watercolor(img)
    overlay = Image.new("RGBA", img.size, (247, 229, 190, 120))
    result = Image.alpha_composite(base, overlay)
    d = ImageDraw.Draw(result)
    rng = random.Random(img.width + img.height)
    colors = [(196, 93, 28, 185), (223, 150, 45, 165), (111, 128, 83, 150)]
    for _ in range(10):
        x = rng.randrange(-30, img.width)
        y = rng.randrange(0, img.height)
        pts = []
        for i in range(5):
            pts.append((x + rng.randrange(40, img.width // 2 + 80), y + rng.randrange(-80, 120)))
        d.line(pts, fill=rng.choice(colors), width=max(3, img.width // 115), joint="curve")
    for _ in range(16):
        x = rng.randrange(20, img.width - 20)
        y = rng.randrange(18, img.height - 18)
        r = rng.randrange(10, 24)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(217, 141, 45, 110), outline=(130, 72, 31, 135), width=2)
    return result


def material_mosaic(img: Image.Image) -> Image.Image:
    base = warm_photo(img)
    w, h = base.size
    out = Image.new("RGBA", base.size, (246, 226, 187, 255))
    d = ImageDraw.Draw(out)
    crops = [
        ((0.10, 0.70), "红砖/门头"),
        ((0.34, 0.72), "外摆/橱窗"),
        ((0.52, 0.58), "钢构/玻璃"),
        ((0.74, 0.74), "秋色乔木"),
    ]
    pad = max(8, w // 35)
    sw = (w - pad * 3) // 2
    sh = (h - pad * 3) // 2
    for i, (anchor, label) in enumerate(crops):
        x = pad + (i % 2) * (sw + pad)
        y = pad + (i // 2) * (sh + pad)
        tile = fit_cover(img, (sw, sh), anchor)
        tile = watercolor(tile)
        out.paste(tile, (x, y), rounded_mask((sw, sh), max(6, pad // 2)))
        d.rectangle((x, y + sh - 24, x + sw, y + sh), fill=(66, 40, 24, 160))
        try:
            d.text((x + 8, y + sh - 22), label, font=font(max(13, w // 38)), fill=(255, 235, 202, 255))
        except Exception:
            pass
    return out


def stylize(img: Image.Image, mode: str) -> Image.Image:
    if mode == "watercolor":
        return watercolor(img)
    if mode == "sketch":
        return sketch(img)
    if mode == "plan":
        return plan_style(img)
    if mode == "mosaic":
        return material_mosaic(img)
    return warm_photo(img)


def paste_replacement(
    board: Image.Image,
    source: Image.Image,
    original_box: tuple[int, int, int, int],
    *,
    anchor: tuple[float, float] = (0.5, 0.58),
    mode: str = "photo",
    radius: int = 7,
    preserve_original_rects: list[tuple[int, int, int, int]] | None = None,
    opacity: int = 255,
) -> None:
    b = scale_box(original_box)
    x1, y1, x2, y2 = b
    w, h = x2 - x1, y2 - y1
    patch = fit_cover(source, (w, h), anchor)
    patch = stylize(patch, mode)
    mask = rounded_mask((w, h), radius)
    if opacity < 255:
        mask = mask.point(lambda p: int(p * opacity / 255))
    if preserve_original_rects:
        md = ImageDraw.Draw(mask)
        for rect in preserve_original_rects:
            rx1, ry1, rx2, ry2 = scale_box(rect)
            md.rectangle((rx1 - x1, ry1 - y1, rx2 - x1, ry2 - y1), fill=0)
    board.paste(patch, (x1, y1), mask)
    d = ImageDraw.Draw(board)
    d.rounded_rectangle((x1, y1, x2, y2), radius=radius, outline=(157, 91, 41, 120), width=max(1, round(1.5 * A3_SIZE[0] / SRC_SIZE[0])))


def small_caption(board: Image.Image, original_box: tuple[int, int, int, int], text: str) -> None:
    x1, y1, x2, y2 = scale_box(original_box)
    d = ImageDraw.Draw(board)
    h = max(32, (y2 - y1) // 7)
    d.rectangle((x1, y2 - h, x2, y2), fill=(65, 39, 23, 150))
    d.text((x1 + 16, y2 - h + 7), text, font=font(max(18, h - 13), serif=True), fill=(255, 235, 200, 245))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    base = Image.open(BOARD).convert("RGB").resize(A3_SIZE, Image.Resampling.LANCZOS).convert("RGBA")
    photo = Image.open(PHOTO).convert("RGB")

    # Large and medium image areas from the first board. Header/title/subtitle are never touched.
    replacements = [
        # Left analysis column.
        ((34, 126, 276, 430), (0.48, 0.56), "plan"),
        ((302, 139, 490, 252), (0.30, 0.28), "watercolor"),
        ((302, 288, 490, 426), (0.52, 0.68), "photo"),
        ((36, 482, 276, 620), (0.38, 0.68), "plan"),
        ((302, 485, 490, 620), (0.70, 0.68), "sketch"),
        ((34, 654, 490, 775), (0.50, 0.52), "sketch"),
        ((34, 816, 490, 962), (0.55, 0.64), "mosaic"),
        ((34, 992, 490, 1064), (0.34, 0.70), "watercolor"),
        # Right main visual stack.
        ((520, 92, 1034, 348), (0.50, 0.57), "photo"),
        ((520, 368, 766, 498), (0.31, 0.70), "photo"),
        ((776, 368, 1034, 498), (0.78, 0.70), "photo"),
        ((520, 528, 1034, 748), (0.50, 0.72), "plan"),
        ((520, 790, 1034, 1030), (0.55, 0.62), "sketch"),
        # Bottom information strip.
        ((34, 1097, 214, 1196), (0.36, 0.72), "watercolor"),
        ((230, 1097, 405, 1198), (0.72, 0.68), "plan"),
        ((420, 1097, 642, 1196), (0.50, 0.68), "photo"),
        ((656, 1097, 835, 1195), (0.18, 0.70), "watercolor"),
        ((848, 1097, 1024, 1196), (0.78, 0.55), "photo"),
        ((34, 1212, 218, 1330), (0.28, 0.68), "photo"),
        ((232, 1214, 420, 1330), (0.50, 0.62), "photo"),
        ((436, 1214, 622, 1330), (0.76, 0.68), "photo"),
        ((642, 1214, 1024, 1330), (0.54, 0.68), "mosaic"),
        ((34, 1342, 258, 1458), (0.52, 0.72), "plan"),
        ((270, 1342, 630, 1458), (0.44, 0.66), "photo"),
        ((642, 1342, 1024, 1458), (0.70, 0.58), "mosaic"),
    ]

    preserve_on_main = [(520, 90, 650, 128)]
    for original_box, anchor, mode in replacements:
        preserve = preserve_on_main if original_box == (520, 92, 1034, 348) else None
        paste_replacement(base, photo, original_box, anchor=anchor, mode=mode, preserve_original_rects=preserve)

    # Add a few small captions only on newly inserted rendering thumbnails; main board title/subtitle remain original.
    small_caption(base, (520, 368, 766, 498), "入口外摆局部")
    small_caption(base, (776, 368, 1034, 498), "街角停留局部")
    small_caption(base, (420, 1097, 642, 1196), "红光市场效果")
    small_caption(base, (270, 1342, 630, 1458), "建筑外观效果图")

    # Restore the exact original title and subtitle area by pasting it back over the result.
    # This guarantees the top title/subtitle text is unchanged.
    original_header = Image.open(BOARD).convert("RGBA").resize(A3_SIZE, Image.Resampling.LANCZOS)
    header_box = scale_box((0, 0, 690, 126))
    base.paste(original_header.crop(header_box), (header_box[0], header_box[1]))

    rgb = base.convert("RGB")
    png = OUT / "coal-town-a3-preserve-title-replace-images.png"
    jpg = OUT / "coal-town-a3-preserve-title-replace-images.jpg"
    pdf = OUT / "coal-town-a3-preserve-title-replace-images.pdf"
    rgb.save(png, dpi=(300, 300))
    rgb.save(jpg, quality=95, dpi=(300, 300), subsampling=0)
    rgb.save(pdf, "PDF", resolution=300.0)
    print(png.resolve())
    print(jpg.resolve())
    print(pdf.resolve())


if __name__ == "__main__":
    main()
