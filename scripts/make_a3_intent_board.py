from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
IMG_1 = Path(r"D:\Downloads\微信图片_20260613163642_67_352.png")
IMG_2 = Path(r"D:\Downloads\微信图片_20260613212853_111_352.jpg")

W, H = 3508, 4961  # A3 portrait at 300 dpi
MARGIN = 150

FONT_SANS = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
FONT_SERIF = Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf")
FONT_HEI = Path(r"C:\Windows\Fonts\simhei.ttf")


def font(size: int, serif: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_SERIF if serif and FONT_SERIF.exists() else FONT_SANS
    if not path.exists():
        path = FONT_HEI
    return ImageFont.truetype(str(path), size)


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def fit_contain(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = min(tw / img.width, th / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    return img.resize((nw, nh), Image.Resampling.LANCZOS)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def paste_round(
    base: Image.Image,
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 28,
    shadow: bool = True,
) -> None:
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    content = fit_cover(img, (w, h)).convert("RGBA")
    mask = rounded_mask((w, h), radius)
    if shadow:
        shadow_img = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow_img)
        sd.rounded_rectangle((40, 40, w + 40, h + 40), radius=radius, fill=(80, 45, 15, 65))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(24))
        base.alpha_composite(shadow_img, (x1 - 40, y1 - 20))
    base.paste(content, (x1, y1), mask)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: tuple[int, int, int, int] = (98, 48, 16, 255),
    size: int = 48,
    accent: bool = True,
) -> None:
    x, y = xy
    f = font(size, serif=True)
    if accent:
        tw, th = text_size(draw, text, f)
        draw.rounded_rectangle(
            (x, y - 18, x + tw + 44, y + th + 26),
            radius=8,
            fill=(177, 91, 27, 235),
        )
        draw.text((x + 22, y - 8), text, font=f, fill=(255, 240, 210, 255))
    else:
        draw.text((x, y), text, font=f, fill=fill)


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    max_width: int,
    line_gap: int = 8,
) -> int:
    x, y = xy
    line = ""
    lines: list[str] = []
    for ch in text:
        trial = line + ch
        if text_size(draw, trial, fnt)[0] <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = ch
    if line:
        lines.append(line)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += text_size(draw, ln, fnt)[1] + line_gap
    return y


def make_texture() -> Image.Image:
    random.seed(13)
    bg = Image.new("RGBA", (W, H), (238, 218, 179, 255))
    pix = bg.load()
    for y in range(H):
        for x in range(W):
            n = random.randint(-9, 10)
            warm = int(10 * (y / H))
            r = max(0, min(255, 238 + n + warm))
            g = max(0, min(255, 218 + n // 2 + warm // 3))
            b = max(0, min(255, 179 + n // 3))
            pix[x, y] = (r, g, b, 255)
    bg = bg.filter(ImageFilter.GaussianBlur(0.45))
    return bg


def add_reference_wash(base: Image.Image, ref: Image.Image) -> None:
    wash = fit_cover(ref.convert("RGBA"), (W, H))
    wash = wash.filter(ImageFilter.GaussianBlur(34))
    wash = ImageEnhance.Color(wash).enhance(0.14)
    wash = ImageEnhance.Contrast(wash).enhance(0.22)
    overlay = Image.new("RGBA", (W, H), (236, 213, 170, 255))
    wash = Image.blend(overlay, wash, 0.1)
    wash.putalpha(36)
    base.alpha_composite(wash, (0, 0))


def maple_leaf(size: int, color: tuple[int, int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, int(size * 0.56)
    pts = []
    for i in range(18):
        angle = -math.pi / 2 + i * math.pi * 2 / 18
        radius = size * (0.44 if i % 2 == 0 else 0.21)
        if i in (2, 16):
            radius *= 0.82
        if i in (6, 12):
            radius *= 0.9
        pts.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    d.polygon(pts, fill=color, outline=(118, 66, 24, 120))
    d.line((cx, cy, cx, size - 5), fill=(120, 70, 28, 180), width=max(2, size // 35))
    for px, py in pts[::2]:
        d.line((cx, cy, px, py), fill=(120, 70, 28, 95), width=max(1, size // 55))
    return img


def decorate(base: Image.Image) -> None:
    rng = random.Random(42)
    for _ in range(34):
        size = rng.randint(52, 132)
        leaf = maple_leaf(size, rng.choice([
            (179, 91, 27, 142),
            (210, 144, 52, 132),
            (126, 67, 29, 118),
            (232, 179, 81, 115),
        ]))
        leaf = leaf.rotate(rng.randint(-55, 55), expand=True, resample=Image.Resampling.BICUBIC)
        edge = rng.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x, y = rng.randint(-40, W - 40), rng.randint(-30, 230)
        elif edge == "bottom":
            x, y = rng.randint(-40, W - 40), rng.randint(H - 320, H - 40)
        elif edge == "left":
            x, y = rng.randint(-50, 120), rng.randint(120, H - 250)
        else:
            x, y = rng.randint(W - 180, W - 40), rng.randint(120, H - 250)
        base.alpha_composite(leaf, (x, y))


def hero_treatment(img: Image.Image) -> Image.Image:
    hero = img.convert("RGBA")
    hero = ImageEnhance.Color(hero).enhance(1.13)
    hero = ImageEnhance.Contrast(hero).enhance(1.08)
    hero = ImageEnhance.Brightness(hero).enhance(1.03)
    return hero


def draw_hero(base: Image.Image, hero_src: Image.Image) -> tuple[int, int, int, int]:
    d = ImageDraw.Draw(base)
    hero_box = (MARGIN, 545, W - MARGIN, 2588)
    paste_round(base, hero_treatment(hero_src), hero_box, radius=36, shadow=True)
    x1, y1, x2, y2 = hero_box

    shade = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(shade.height):
        a = int(max(0, 142 - i * 0.18))
        sd.line((0, i, shade.width, i), fill=(70, 34, 10, a))
    base.alpha_composite(shade, (x1, y1))

    d.rounded_rectangle((x1 + 54, y1 + 52, x1 + 590, y1 + 150), radius=10, fill=(165, 79, 24, 238))
    d.text((x1 + 86, y1 + 70), "效果图最大", font=font(58, serif=True), fill=(255, 238, 203, 255))
    d.text((x1 + 62, y1 + 185), "红光市场 · 工业记忆更新场景", font=font(86, serif=True), fill=(255, 245, 220, 255))
    d.text((x1 + 66, y1 + 306), "以第二张效果图为核心，强化入口广场、秋色街景与开放市集氛围。", font=font(38), fill=(255, 238, 205, 240))

    d.rounded_rectangle((x2 - 820, y2 - 186, x2 - 52, y2 - 54), radius=18, fill=(54, 30, 19, 178), outline=(242, 189, 105, 150), width=2)
    d.text((x2 - 782, y2 - 154), "主视觉占据版面核心，先抓视线，再进入策略说明", font=font(35), fill=(255, 230, 190, 250))
    return hero_box


def draw_header(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    d.text((MARGIN, 94), "炭光里", font=font(176, serif=True), fill=(96, 45, 15, 255))
    d.text((MARGIN + 710, 137), "第五张｜方案意向图", font=font(70, serif=True), fill=(132, 66, 23, 255))
    d.text((MARGIN + 712, 228), "景观小品 · 景观材料 · 互动策略 · 核心效果图", font=font(38), fill=(133, 92, 48, 255))
    d.line((MARGIN, 357, W - MARGIN, 357), fill=(164, 94, 37, 190), width=5)
    d.line((MARGIN, 377, W - MARGIN, 377), fill=(204, 143, 59, 145), width=2)
    tag = "石炭井小镇建筑外观设计 / 工业记忆 · 市井烟火 · 交流新生"
    tw, _ = text_size(d, tag, font(35))
    d.rounded_rectangle((W - MARGIN - tw - 68, 104, W - MARGIN, 170), radius=8, fill=(178, 91, 28, 225))
    d.text((W - MARGIN - tw - 34, 116), tag, font=font(35), fill=(255, 238, 205, 255))


def panel(base: Image.Image, box: tuple[int, int, int, int], title: str) -> ImageDraw.ImageDraw:
    d = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    d.rounded_rectangle((x1, y1, x2, y2), radius=24, fill=(249, 234, 199, 214), outline=(182, 113, 49, 180), width=3)
    d.rectangle((x1, y1, x2, y1 + 86), fill=(178, 91, 28, 235))
    d.text((x1 + 34, y1 + 18), title, font=font(47, serif=True), fill=(255, 240, 211, 255))
    return d


def draw_landscape_objects(base: Image.Image, box: tuple[int, int, int, int]) -> None:
    d = panel(base, box, "景观小品")
    x1, y1, x2, y2 = box
    img_area = (x1 + 34, y1 + 118, x2 - 34, y1 + 560)
    d.rounded_rectangle(img_area, radius=16, fill=(242, 215, 170, 255), outline=(175, 103, 45, 120), width=2)

    ix1, iy1, ix2, iy2 = img_area
    # Industrial pergola and seating sketch.
    d.rectangle((ix1 + 75, iy2 - 136, ix2 - 78, iy2 - 92), fill=(96, 64, 39, 235))
    for sx in range(ix1 + 120, ix2 - 80, 210):
        d.rectangle((sx, iy1 + 105, sx + 24, iy2 - 92), fill=(92, 68, 54, 230))
    d.line((ix1 + 70, iy1 + 108, ix2 - 75, iy1 + 108), fill=(94, 61, 36, 255), width=18)
    d.line((ix1 + 110, iy1 + 66, ix2 - 135, iy1 + 66), fill=(135, 72, 28, 255), width=10)
    for sx in range(ix1 + 130, ix2 - 160, 126):
        d.line((sx, iy1 + 66, sx + 70, iy1 + 108), fill=(130, 78, 38, 210), width=5)
    d.rounded_rectangle((ix1 + 174, iy2 - 207, ix1 + 525, iy2 - 150), radius=18, fill=(179, 91, 27, 235))
    d.rounded_rectangle((ix1 + 602, iy2 - 218, ix1 + 948, iy2 - 158), radius=18, fill=(120, 81, 48, 245))
    d.ellipse((ix2 - 238, iy1 + 78, ix2 - 142, iy1 + 174), fill=(225, 155, 55, 220), outline=(112, 65, 28, 180), width=4)
    d.line((ix2 - 190, iy1 + 174, ix2 - 190, iy2 - 96), fill=(83, 72, 62, 235), width=10)
    d.rectangle((ix2 - 224, iy2 - 110, ix2 - 156, iy2 - 88), fill=(83, 72, 62, 235))

    items = [
        ("矿轨座椅", "以旧轨道、耐候钢与木面组合，形成可停留的街角节点。"),
        ("灯塔导视", "借煤矿井架形态转译，承担导览、夜景照明与打卡功能。"),
        ("市集摊架", "可移动摊架适配周末集市、文创展示与社区活动。"),
    ]
    tx = x1 + 46
    ty = y1 + 600
    for i, (name, desc) in enumerate(items):
        bx = tx + i * ((x2 - x1 - 92) // 3)
        d.ellipse((bx, ty + 10, bx + 38, ty + 48), fill=(176, 91, 29, 255))
        d.text((bx + 54, ty), name, font=font(33, serif=True), fill=(98, 47, 16, 255))
        draw_wrapped(d, (bx + 54, ty + 48), desc, font(24), (105, 76, 45, 255), 338, 6)

    concept = (x1 + 36, y1 + 890, x2 - 36, y2 - 36)
    d.rounded_rectangle(concept, radius=16, fill=(255, 243, 216, 176), outline=(176, 102, 40, 110), width=2)
    cx1, cy1, cx2, cy2 = concept
    d.text((cx1 + 28, cy1 + 26), "小品组合意向", font=font(35, serif=True), fill=(103, 50, 17, 255))
    path = [
        (cx1 + 150, cy2 - 150),
        (cx1 + 430, cy1 + 210),
        (cx1 + 705, cy2 - 210),
        (cx2 - 170, cy1 + 245),
    ]
    for a, b in zip(path, path[1:]):
        d.line((a, b), fill=(178, 91, 27, 210), width=9)
    node_titles = ["入口导视", "休憩树阵", "快闪摊架", "夜景灯带"]
    for i, ((nx, ny), label) in enumerate(zip(path, node_titles), start=1):
        d.ellipse((nx - 56, ny - 56, nx + 56, ny + 56), fill=(239, 178, 74, 245), outline=(116, 59, 22, 230), width=5)
        tw, th = text_size(d, str(i), font(38, serif=True))
        d.text((nx - tw / 2, ny - th / 2 - 4), str(i), font=font(38, serif=True), fill=(105, 45, 17, 255))
        d.text((nx - 80, ny + 74), label, font=font(26, serif=True), fill=(99, 66, 37, 255))
    for px in range(cx1 + 100, cx2 - 80, 92):
        d.rectangle((px, cy2 - 88, px + 48, cy2 - 64), fill=(110, 75, 45, 190))
        d.line((px + 10, cy2 - 88, px + 10, cy2 - 126), fill=(88, 63, 43, 185), width=4)
        d.line((px + 38, cy2 - 88, px + 38, cy2 - 126), fill=(88, 63, 43, 185), width=4)


def material_texture(kind: str, size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (230, 200, 155, 255))
    d = ImageDraw.Draw(img)
    rng = random.Random(hash(kind) & 0xFFFF)
    if kind == "brick":
        img.paste((158, 69, 32, 255), (0, 0, w, h))
        brick_h = 34
        for y in range(0, h + brick_h, brick_h):
            offset = 54 if (y // brick_h) % 2 else 0
            d.line((0, y, w, y), fill=(235, 175, 105, 155), width=3)
            for x in range(-offset, w, 108):
                d.line((x, y, x, y + brick_h), fill=(235, 175, 105, 120), width=3)
        for _ in range(350):
            x, y = rng.randrange(w), rng.randrange(h)
            d.point((x, y), fill=(100 + rng.randrange(60), 40 + rng.randrange(30), 23, 150))
    elif kind == "steel":
        for y in range(h):
            c = 86 + int(42 * y / h)
            d.line((0, y, w, y), fill=(c + 35, c, 63, 255))
        for _ in range(32):
            x = rng.randrange(w)
            d.line((x, 0, x + rng.randrange(-40, 40), h), fill=(189, 92, 34, rng.randrange(70, 145)), width=rng.randrange(3, 8))
    elif kind == "wood":
        img.paste((155, 99, 47, 255), (0, 0, w, h))
        for y in range(0, h, 24):
            d.line((0, y + rng.randrange(-4, 5), w, y + rng.randrange(-4, 5)), fill=(105, 62, 30, 120), width=3)
        for _ in range(24):
            cy = rng.randrange(h)
            cx = rng.randrange(w)
            d.arc((cx - 90, cy - 20, cx + 170, cy + 42), 0, 360, fill=(98, 58, 28, 85), width=2)
    elif kind == "stone":
        img.paste((185, 174, 148, 255), (0, 0, w, h))
        for _ in range(80):
            x, y = rng.randrange(w), rng.randrange(h)
            r = rng.randrange(10, 34)
            col = rng.choice([(145, 136, 119, 120), (217, 205, 177, 130), (120, 111, 100, 80)])
            d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    elif kind == "plant":
        img.paste((117, 127, 88, 255), (0, 0, w, h))
        for _ in range(95):
            x, y = rng.randrange(w), rng.randrange(h)
            col = rng.choice([(218, 155, 48, 185), (190, 112, 36, 160), (90, 112, 73, 165)])
            d.ellipse((x - 12, y - 5, x + 20, y + 9), fill=col)
    else:
        img.paste((215, 170, 95, 255), (0, 0, w, h))
        for x in range(0, w, 70):
            d.line((x, 0, x, h), fill=(150, 93, 39, 100), width=2)
        for y in range(0, h, 70):
            d.line((0, y, w, y), fill=(150, 93, 39, 100), width=2)
    return img.filter(ImageFilter.GaussianBlur(0.25))


def draw_materials(base: Image.Image, box: tuple[int, int, int, int]) -> None:
    d = panel(base, box, "景观材料")
    x1, y1, x2, y2 = box
    materials = [
        ("红砖肌理", "brick"),
        ("耐候钢板", "steel"),
        ("防腐木面", "wood"),
        ("洗米石铺装", "stone"),
        ("秋色植物", "plant"),
        ("暖色透水砖", "paver"),
    ]
    gap = 24
    cell_w = (x2 - x1 - 68 - gap) // 2
    cell_h = 208
    sx = x1 + 34
    sy = y1 + 122
    for i, (name, kind) in enumerate(materials):
        cx = sx + (i % 2) * (cell_w + gap)
        cy = sy + (i // 2) * (cell_h + 64)
        tex = material_texture(kind, (cell_w, cell_h))
        base.paste(tex, (cx, cy), rounded_mask((cell_w, cell_h), 14))
        d.rounded_rectangle((cx, cy, cx + cell_w, cy + cell_h), radius=14, outline=(117, 73, 38, 135), width=2)
        d.rectangle((cx, cy + cell_h - 52, cx + cell_w, cy + cell_h), fill=(65, 42, 28, 165))
        d.text((cx + 22, cy + cell_h - 45), name, font=font(29, serif=True), fill=(255, 235, 202, 255))
    note_y = y2 - 150
    d.rounded_rectangle((x1 + 36, note_y, x2 - 36, y2 - 34), radius=16, fill=(255, 245, 218, 175), outline=(176, 102, 40, 110), width=2)
    draw_wrapped(
        d,
        (x1 + 66, note_y + 22),
        "材料策略：保留红砖与钢构的工业底色，用木、石、植物降低硬度，形成可逛、可坐、可拍的市集街景。",
        font(28),
        (101, 67, 35, 255),
        x2 - x1 - 132,
        7,
    )


def draw_interaction(base: Image.Image, box: tuple[int, int, int, int], hero_src: Image.Image) -> None:
    d = panel(base, box, "互动策略")
    x1, y1, x2, y2 = box
    map_box = (x1 + 34, y1 + 120, x2 - 34, y1 + 570)
    mini = fit_cover(hero_treatment(hero_src).filter(ImageFilter.GaussianBlur(2)), (map_box[2] - map_box[0], map_box[3] - map_box[1]))
    mini = ImageEnhance.Brightness(mini).enhance(1.2)
    mini = ImageEnhance.Contrast(mini).enhance(0.82)
    overlay = Image.new("RGBA", mini.size, (238, 213, 168, 118))
    mini = Image.alpha_composite(mini.convert("RGBA"), overlay)
    base.paste(mini, (map_box[0], map_box[1]), rounded_mask(mini.size, 16))
    d.rounded_rectangle(map_box, radius=16, outline=(150, 84, 34, 150), width=2)

    mx1, my1, mx2, my2 = map_box
    route = [
        (mx1 + 160, my2 - 110),
        (mx1 + 420, my2 - 255),
        (mx1 + 735, my2 - 196),
        (mx1 + 1040, my2 - 325),
        (mx2 - 170, my2 - 214),
    ]
    for a, b in zip(route, route[1:]):
        d.line((a, b), fill=(185, 83, 25, 255), width=12)
    for idx, (x, y) in enumerate(route, start=1):
        d.ellipse((x - 42, y - 42, x + 42, y + 42), fill=(255, 225, 153, 245), outline=(157, 73, 24, 255), width=6)
        tw, th = text_size(d, str(idx), font(36, serif=True))
        d.text((x - tw / 2, y - th / 2 - 4), str(idx), font=font(36, serif=True), fill=(117, 48, 17, 255))

    labels = [
        ("入口打卡", "红光市场立面、矿灯导视"),
        ("市集漫游", "摊架、展陈、临时活动"),
        ("休憩停留", "轨道座椅、树阵遮荫"),
        ("夜间点亮", "暖光灯带、橱窗外摆"),
    ]
    lx = x1 + 48
    ly = y1 + 610
    card_w = (x2 - x1 - 120) // 2
    for i, (name, desc) in enumerate(labels):
        col = i % 2
        row = i // 2
        row_x = lx + col * (card_w + 24)
        row_y = ly + row * 104
        d.rounded_rectangle((row_x, row_y, row_x + card_w, row_y + 86), radius=14, fill=(255, 242, 211, 198), outline=(178, 91, 27, 115), width=2)
        d.rounded_rectangle((row_x + 18, row_y + 17, row_x + 68, row_y + 67), radius=25, fill=(179, 91, 27, 255))
        d.text((row_x + 34, row_y + 22), str(i + 1), font=font(27, serif=True), fill=(255, 239, 209, 255))
        d.text((row_x + 86, row_y + 9), name, font=font(27, serif=True), fill=(98, 47, 16, 255))
        d.text((row_x + 86, row_y + 46), desc, font=font(20), fill=(110, 78, 45, 255))


def draw_bottom_band(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    y = H - 360
    d.rounded_rectangle((MARGIN, y, W - MARGIN, H - 152), radius=22, fill=(117, 67, 35, 208), outline=(202, 139, 63, 170), width=3)
    d.text((MARGIN + 42, y + 42), "设计关键词", font=font(46, serif=True), fill=(255, 234, 196, 255))
    words = ["工业记忆", "市井烟火", "秋色入口", "可停留街角", "夜间运营", "社区共创"]
    x = MARGIN + 340
    for w in words:
        tw, th = text_size(d, w, font(34, serif=True))
        d.rounded_rectangle((x, y + 45, x + tw + 54, y + 104), radius=30, fill=(247, 222, 176, 235))
        d.text((x + 27, y + 54), w, font=font(34, serif=True), fill=(117, 57, 21, 255))
        x += tw + 82
    d.text(
        (MARGIN + 42, y + 145),
        "以大图建立第一视觉，以小品、材料、互动三组信息支撑落地表达；整体色调承接炭光里暖砖、耐候钢与秋叶记忆。",
        font=font(31),
        fill=(255, 236, 204, 242),
    )


def main() -> None:
    OUT.mkdir(exist_ok=True)
    ref = Image.open(IMG_1)
    hero = Image.open(IMG_2)
    base = make_texture()
    add_reference_wash(base, ref)
    decorate(base)

    d = ImageDraw.Draw(base)
    d.rectangle((58, 58, W - 58, H - 58), outline=(157, 86, 33, 210), width=5)
    d.rectangle((86, 86, W - 86, H - 86), outline=(225, 169, 86, 120), width=2)

    draw_header(base)
    draw_hero(base, hero)

    left_box = (MARGIN, 2710, 1790, 4550)
    right_top = (1848, 2710, W - MARGIN, 3615)
    right_bottom = (1848, 3672, W - MARGIN, 4550)
    draw_landscape_objects(base, left_box)
    draw_materials(base, right_top)
    draw_interaction(base, right_bottom, hero)
    draw_bottom_band(base)

    # Light vignette to keep attention toward the main rendering.
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(34):
        alpha = int(i * 2.7)
        vd.rectangle((i * 18, i * 25, W - i * 18, H - i * 25), outline=(86, 44, 18, alpha), width=18)
    base = Image.alpha_composite(base, vignette)

    png = OUT / "coal-town-a3-intent-board-05.png"
    jpg = OUT / "coal-town-a3-intent-board-05.jpg"
    pdf = OUT / "coal-town-a3-intent-board-05.pdf"
    rgb = base.convert("RGB")
    rgb.save(png, dpi=(300, 300))
    rgb.save(jpg, quality=95, dpi=(300, 300), subsampling=0)
    rgb.save(pdf, "PDF", resolution=300.0)
    print(png)
    print(jpg)
    print(pdf)


if __name__ == "__main__":
    main()
