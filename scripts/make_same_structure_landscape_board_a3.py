from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
BASE_REF = Path(r"D:\Downloads\微信图片_20260613163642_67_352.png")
PHOTO = Path(r"D:\Downloads\微信图片_20260613212853_111_352.jpg")

A3 = (3508, 4961)
REF_SIZE = (1054, 1492)

FONT_SANS = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
FONT_SERIF = Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf")
FONT_HEI = Path(r"C:\Windows\Fonts\simhei.ttf")


def f(size: int, serif: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_SERIF if serif and FONT_SERIF.exists() else FONT_SANS
    if not path.exists():
        path = FONT_HEI
    return ImageFont.truetype(str(path), size)


def box(x1: int, y1: int, x2: int, y2: int) -> tuple[int, int, int, int]:
    sx = A3[0] / REF_SIZE[0]
    sy = A3[1] / REF_SIZE[1]
    return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)


def fit_cover(img: Image.Image, size: tuple[int, int], anchor: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    ax, ay = anchor
    left = round((nw - tw) * ax)
    top = round((nh - th) * ay)
    return resized.crop((left, top, left + tw, top + th))


def fit_contain(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = min(tw / img.width, th / img.height)
    return img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)


def text_wh(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def wrap_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.FreeTypeFont,
              fill: tuple[int, int, int, int], max_width: int, line_gap: int = 8) -> int:
    x, y = xy
    line = ""
    lines: list[str] = []
    for ch in text:
        candidate = line + ch
        if text_wh(draw, candidate, font)[0] <= max_width or not line:
            line = candidate
        else:
            lines.append(line)
            line = ch
    if line:
        lines.append(line)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += text_wh(draw, ln, font)[1] + line_gap
    return y


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def paste_round(canvas: Image.Image, img: Image.Image, b: tuple[int, int, int, int], radius: int = 14,
                shadow: bool = False, cover: bool = True, anchor: tuple[float, float] = (0.5, 0.5)) -> None:
    x1, y1, x2, y2 = b
    w, h = x2 - x1, y2 - y1
    content = fit_cover(img, (w, h), anchor) if cover else fit_contain(img, (w, h))
    content = content.convert("RGBA")
    if shadow:
        sh = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((34, 34, w + 34, h + 34), radius=radius, fill=(95, 50, 15, 80))
        sh = sh.filter(ImageFilter.GaussianBlur(20))
        canvas.alpha_composite(sh, (x1 - 34, y1 - 20))
    canvas.paste(content, (x1, y1), rounded_mask((w, h), radius))


def paper_background() -> Image.Image:
    rng = random.Random(20260614)
    base = Image.new("RGBA", A3, (239, 220, 182, 255))
    pix = base.load()
    for y in range(A3[1]):
        for x in range(A3[0]):
            n = rng.randint(-8, 9)
            r = 239 + n + int(8 * y / A3[1])
            g = 220 + n // 2
            b = 182 + n // 3
            pix[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255)
    return base.filter(ImageFilter.GaussianBlur(0.35))


def maple_leaf(size: int, color: tuple[int, int, int, int]) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, int(size * 0.54)
    pts = []
    for i in range(18):
        ang = -math.pi / 2 + i * math.tau / 18
        rad = size * (0.43 if i % 2 == 0 else 0.21)
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    d.polygon(pts, fill=color, outline=(121, 64, 25, 90))
    d.line((cx, cy, cx, size - 4), fill=(112, 63, 25, 160), width=max(2, size // 38))
    for p in pts[::2]:
        d.line((cx, cy, p[0], p[1]), fill=(126, 70, 28, 70), width=max(1, size // 60))
    return img


def decorate(canvas: Image.Image) -> None:
    rng = random.Random(61)
    d = ImageDraw.Draw(canvas)
    d.rectangle((60, 58, A3[0] - 60, A3[1] - 60), outline=(153, 85, 32, 220), width=5)
    d.rectangle((88, 88, A3[0] - 88, A3[1] - 88), outline=(225, 168, 83, 120), width=2)
    for _ in range(42):
        size = rng.randint(46, 130)
        leaf = maple_leaf(size, rng.choice([
            (178, 89, 26, 130),
            (218, 151, 56, 125),
            (126, 70, 31, 110),
            (236, 184, 84, 105),
        ]))
        leaf = leaf.rotate(rng.randint(-60, 60), expand=True, resample=Image.Resampling.BICUBIC)
        edge = rng.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x, y = rng.randint(-35, A3[0] - 120), rng.randint(-30, 210)
        elif edge == "bottom":
            x, y = rng.randint(-35, A3[0] - 120), rng.randint(A3[1] - 300, A3[1] - 35)
        elif edge == "left":
            x, y = rng.randint(-45, 120), rng.randint(120, A3[1] - 280)
        else:
            x, y = rng.randint(A3[0] - 180, A3[0] - 35), rng.randint(120, A3[1] - 280)
        canvas.alpha_composite(leaf, (x, y))


def title_bar(draw: ImageDraw.ImageDraw, b: tuple[int, int, int, int], title: str) -> None:
    x1, y1, x2, _ = b
    draw.rectangle((x1, y1, x2, y1 + 62), fill=(177, 88, 26, 238))
    draw.text((x1 + 18, y1 + 10), title, font=f(36, serif=True), fill=(255, 238, 205, 255))


def panel(draw: ImageDraw.ImageDraw, b: tuple[int, int, int, int], title: str, fill=(250, 235, 199, 164)) -> None:
    x1, y1, x2, y2 = b
    draw.rounded_rectangle((x1, y1, x2, y2), radius=10, fill=fill, outline=(181, 111, 49, 170), width=2)
    title_bar(draw, b, title)


def warm_photo(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    img = ImageEnhance.Color(img).enhance(1.03)
    img = ImageEnhance.Contrast(img).enhance(1.04)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = Image.alpha_composite(img, Image.new("RGBA", img.size, (238, 200, 132, 28)))
    return img


def draw_header(canvas: Image.Image) -> None:
    d = ImageDraw.Draw(canvas)
    d.text((box(40, 18, 0, 0)[0], box(0, 18, 0, 0)[1]), "炭光里", font=f(178, serif=True), fill=(92, 43, 13, 255))
    d.text((box(350, 50, 0, 0)[0], box(0, 48, 0, 0)[1]), "石炭井小镇景观方案意向图", font=f(67, serif=True), fill=(68, 44, 25, 255))
    d.text((box(360, 87, 0, 0)[0], box(0, 87, 0, 0)[1]), "景观小品 · 景观材料 · 互动策略 · 效果图最大", font=f(37), fill=(117, 73, 34, 255))
    d.line((box(28, 116, 0, 0)[0], box(0, 116, 0, 0)[1], box(1025, 116, 0, 0)[0], box(0, 116, 0, 0)[1]),
           fill=(163, 91, 34, 200), width=4)


def draw_objects_large(canvas: Image.Image, b: tuple[int, int, int, int]) -> None:
    d = ImageDraw.Draw(canvas)
    panel(d, b, "景观小品总览图")
    x1, y1, x2, y2 = b
    inner = (x1 + 32, y1 + 90, x2 - 32, y2 - 36)
    d.rounded_rectangle(inner, radius=16, fill=(242, 213, 166, 245), outline=(150, 86, 38, 120), width=2)
    ix1, iy1, ix2, iy2 = inner
    # A bold pergola / market-stall scene.
    floor_y = iy2 - 96
    d.polygon([(ix1 + 40, floor_y), (ix2 - 40, floor_y - 42), (ix2 - 8, iy2 - 16), (ix1 + 10, iy2 - 10)],
              fill=(184, 135, 74, 160))
    d.line((ix1 + 70, iy1 + 96, ix2 - 66, iy1 + 96), fill=(78, 55, 39, 255), width=16)
    d.line((ix1 + 105, iy1 + 58, ix2 - 110, iy1 + 58), fill=(165, 78, 28, 255), width=10)
    for sx in range(ix1 + 115, ix2 - 100, 105):
        d.line((sx, iy1 + 58, sx + 58, iy1 + 96), fill=(118, 70, 35, 220), width=5)
        d.rectangle((sx, iy1 + 96, sx + 18, floor_y), fill=(82, 62, 47, 245))
    d.rounded_rectangle((ix1 + 130, floor_y - 92, ix1 + 360, floor_y - 52), radius=17, fill=(179, 88, 27, 255))
    d.rounded_rectangle((ix1 + 410, floor_y - 105, ix1 + 665, floor_y - 62), radius=17, fill=(116, 78, 48, 255))
    d.rounded_rectangle((ix2 - 270, floor_y - 156, ix2 - 115, floor_y - 62), radius=8, fill=(205, 146, 58, 235), outline=(96, 60, 28, 210), width=4)
    d.ellipse((ix2 - 165, iy1 + 92, ix2 - 68, iy1 + 188), fill=(226, 155, 48, 235), outline=(112, 66, 28, 180), width=4)
    d.line((ix2 - 116, iy1 + 188, ix2 - 116, floor_y), fill=(85, 74, 62, 235), width=9)
    labels = [("矿轨座椅", ix1 + 134, floor_y - 150), ("井架导视", ix2 - 300, floor_y - 215), ("可移动摊架", ix1 + 420, floor_y - 160)]
    for text, lx, ly in labels:
        tw, th = text_wh(d, text, f(25, serif=True))
        d.rounded_rectangle((lx - 12, ly - 8, lx + tw + 12, ly + th + 12), radius=6, fill=(255, 238, 199, 220))
        d.text((lx, ly), text, font=f(25, serif=True), fill=(94, 45, 16, 255))


def draw_object_detail(canvas: Image.Image, b: tuple[int, int, int, int], title: str, kind: str) -> None:
    d = ImageDraw.Draw(canvas)
    panel(d, b, title)
    x1, y1, x2, y2 = b
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 + 34
    if kind == "node":
        d.rounded_rectangle((x1 + 50, cy - 80, x2 - 50, cy - 30), radius=20, fill=(177, 89, 28, 245))
        d.line((x1 + 75, cy - 30, x1 + 75, cy + 86), fill=(88, 62, 43, 230), width=11)
        d.line((x2 - 75, cy - 30, x2 - 75, cy + 86), fill=(88, 62, 43, 230), width=11)
        d.arc((x1 + 42, y1 + 104, x2 - 42, y2 - 38), 200, 340, fill=(89, 66, 49, 210), width=9)
    else:
        d.line((x1 + 50, y1 + 128, x2 - 50, y1 + 128), fill=(82, 59, 42, 250), width=12)
        for i in range(4):
            sx = x1 + 78 + i * 120
            d.line((sx, y1 + 128, sx + 55, y1 + 214), fill=(133, 78, 34, 210), width=5)
            d.rectangle((sx + 22, y1 + 214, sx + 42, y2 - 70), fill=(83, 62, 47, 230))
        d.ellipse((x2 - 112, y1 + 155, x2 - 45, y1 + 222), fill=(229, 158, 52, 220), outline=(117, 63, 26, 170), width=4)
    wrap_text(d, (x1 + 28, y2 - 83), "强调可坐、可拍、可运营的街角停留点。", f(22), (109, 77, 46, 255), x2 - x1 - 56, 4)


def draw_effect_area(canvas: Image.Image, photo: Image.Image) -> None:
    d = ImageDraw.Draw(canvas)
    hero = box(520, 98, 1034, 357)
    title_bar(d, (hero[0], hero[1] - 44, hero[2], hero[3]), "效果图最大｜红光市场入口场景")
    paste_round(canvas, warm_photo(photo), hero, radius=14, shadow=True, anchor=(0.5, 0.58))
    hx1, hy1, hx2, hy2 = hero
    # Gradient label layer inside the rendering.
    overlay = Image.new("RGBA", (hx2 - hx1, hy2 - hy1), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(overlay.height):
        a = max(0, 125 - int(y * 0.5))
        od.line((0, y, overlay.width, y), fill=(72, 34, 10, a))
    canvas.alpha_composite(overlay, (hx1, hy1))
    d.text((hx1 + 26, hy1 + 26), "秋色入口 · 开放市集 · 社交停留", font=f(38, serif=True), fill=(255, 240, 210, 250))
    d.rounded_rectangle((hx2 - 360, hy2 - 58, hx2 - 18, hy2 - 18), radius=7, fill=(64, 34, 18, 170))
    d.text((hx2 - 342, hy2 - 50), "第二张效果图已融入主视觉", font=f(22), fill=(255, 232, 196, 245))

    detail1 = box(520, 368, 766, 496)
    detail2 = box(774, 368, 1034, 496)
    for i, (bb, title, anchor) in enumerate([
        (detail1, "市集外摆局部", (0.38, 0.68)),
        (detail2, "街角停留局部", (0.76, 0.68)),
    ]):
        crop = warm_photo(photo)
        paste_round(canvas, crop, bb, radius=10, shadow=False, anchor=anchor)
        d.rectangle((bb[0], bb[3] - 34, bb[2], bb[3]), fill=(63, 39, 24, 175))
        d.text((bb[0] + 18, bb[3] - 30), title, font=f(24, serif=True), fill=(255, 235, 200, 255))


def material_texture(kind: str, size: tuple[int, int]) -> Image.Image:
    w, h = size
    rng = random.Random(abs(hash(kind)) & 0xFFFF)
    img = Image.new("RGBA", size, (230, 200, 155, 255))
    d = ImageDraw.Draw(img)
    if kind == "brick":
        img.paste((158, 68, 31, 255), (0, 0, w, h))
        for y in range(0, h, 32):
            d.line((0, y, w, y), fill=(239, 176, 102, 130), width=3)
            off = 54 if (y // 32) % 2 else 0
            for x in range(-off, w, 108):
                d.line((x, y, x, y + 32), fill=(239, 176, 102, 110), width=3)
    elif kind == "steel":
        for y in range(h):
            c = 75 + int(36 * y / h)
            d.line((0, y, w, y), fill=(c + 50, c, 58, 255))
        for _ in range(34):
            x = rng.randrange(w)
            d.line((x, 0, x + rng.randrange(-35, 40), h), fill=(196, 92, 30, rng.randrange(70, 145)), width=rng.randrange(2, 6))
    elif kind == "wood":
        img.paste((155, 100, 50, 255), (0, 0, w, h))
        for y in range(0, h, 22):
            d.line((0, y + rng.randrange(-4, 4), w, y + rng.randrange(-4, 4)), fill=(96, 57, 29, 110), width=3)
        for _ in range(20):
            cx, cy = rng.randrange(w), rng.randrange(h)
            d.arc((cx - 90, cy - 22, cx + 170, cy + 42), 0, 360, fill=(100, 58, 28, 85), width=2)
    elif kind == "stone":
        img.paste((187, 176, 149, 255), (0, 0, w, h))
        for _ in range(90):
            x, y = rng.randrange(w), rng.randrange(h)
            r = rng.randrange(10, 34)
            d.ellipse((x - r, y - r, x + r, y + r), fill=rng.choice([(126, 118, 101, 85), (224, 210, 178, 130), (105, 98, 86, 70)]))
    elif kind == "plant":
        img.paste((112, 124, 86, 255), (0, 0, w, h))
        for _ in range(120):
            x, y = rng.randrange(w), rng.randrange(h)
            d.ellipse((x - 14, y - 6, x + 22, y + 9), fill=rng.choice([(222, 155, 45, 170), (181, 100, 30, 150), (84, 112, 75, 170)]))
    else:
        img.paste((215, 170, 94, 255), (0, 0, w, h))
        for x in range(0, w, 62):
            d.line((x, 0, x, h), fill=(139, 86, 38, 95), width=2)
        for y in range(0, h, 62):
            d.line((0, y, w, y), fill=(139, 86, 38, 95), width=2)
    return img.filter(ImageFilter.GaussianBlur(0.18))


def draw_material_board(canvas: Image.Image, b: tuple[int, int, int, int]) -> None:
    d = ImageDraw.Draw(canvas)
    panel(d, b, "景观材料意向图")
    x1, y1, x2, y2 = b
    names = [("红砖肌理", "brick"), ("耐候钢", "steel"), ("防腐木", "wood"), ("洗米石", "stone"), ("秋色植物", "plant"), ("透水铺装", "paver")]
    sx, sy = x1 + 28, y1 + 88
    gap = 18
    cw = (x2 - x1 - 74) // 2
    ch = (y2 - y1 - 220) // 3
    for i, (name, kind) in enumerate(names):
        cx = sx + (i % 2) * (cw + gap)
        cy = sy + (i // 2) * (ch + 26)
        tex = material_texture(kind, (cw, ch))
        canvas.paste(tex, (cx, cy), rounded_mask((cw, ch), 10))
        d.rounded_rectangle((cx, cy, cx + cw, cy + ch), radius=10, outline=(118, 70, 34, 120), width=2)
        d.rectangle((cx, cy + ch - 34, cx + cw, cy + ch), fill=(64, 40, 25, 165))
        d.text((cx + 12, cy + ch - 30), name, font=f(22, serif=True), fill=(255, 233, 199, 255))
    wrap_text(d, (x1 + 34, y2 - 98), "材料从原有红砖、钢构与场地秋色中提取，形成耐看、耐用、易维护的室外街区语言。", f(24), (100, 68, 38, 255), x2 - x1 - 68, 5)


def draw_material_detail(canvas: Image.Image, b: tuple[int, int, int, int]) -> None:
    d = ImageDraw.Draw(canvas)
    panel(d, b, "材料节点大样图")
    x1, y1, x2, y2 = b
    ground = y2 - 150
    d.rectangle((x1 + 42, ground - 34, x2 - 42, ground), fill=(214, 158, 72, 255))
    d.rectangle((x1 + 42, ground, x2 - 42, ground + 35), fill=(180, 170, 145, 255))
    d.rectangle((x1 + 42, ground + 35, x2 - 42, ground + 82), fill=(128, 100, 72, 255))
    for x in range(x1 + 48, x2 - 42, 72):
        d.line((x, ground - 34, x, ground), fill=(139, 86, 38, 110), width=2)
    d.text((x1 + 50, y1 + 88), "铺装层", font=f(25, serif=True), fill=(104, 50, 18, 255))
    d.text((x1 + 50, y1 + 132), "透水找平层", font=f(25, serif=True), fill=(104, 50, 18, 255))
    d.text((x1 + 50, y1 + 176), "碎石垫层", font=f(25, serif=True), fill=(104, 50, 18, 255))
    for i, label in enumerate(["耐候钢收边", "木质坐面", "暖光灯带"]):
        yy = y1 + 92 + i * 68
        d.ellipse((x2 - 230, yy - 12, x2 - 200, yy + 18), fill=(177, 89, 26, 255))
        d.text((x2 - 190, yy - 18), label, font=f(24), fill=(95, 64, 36, 255))


def draw_interaction_strategy(canvas: Image.Image, b: tuple[int, int, int, int], photo: Image.Image) -> None:
    d = ImageDraw.Draw(canvas)
    panel(d, b, "互动策略总图")
    x1, y1, x2, y2 = b
    inner = (x1 + 30, y1 + 88, x2 - 30, y2 - 48)
    bg = fit_cover(warm_photo(photo).filter(ImageFilter.GaussianBlur(2.3)), (inner[2] - inner[0], inner[3] - inner[1]), (0.5, 0.62))
    wash = Image.alpha_composite(bg.convert("RGBA"), Image.new("RGBA", bg.size, (244, 218, 169, 118)))
    canvas.paste(wash, (inner[0], inner[1]), rounded_mask(wash.size, 12))
    d.rounded_rectangle(inner, radius=12, outline=(146, 82, 35, 150), width=2)
    ix1, iy1, ix2, iy2 = inner
    route = [
        (ix1 + 82, iy2 - 92),
        (ix1 + 240, iy1 + 220),
        (ix1 + 420, iy2 - 150),
        (ix1 + 650, iy1 + 166),
        (ix2 - 92, iy2 - 120),
    ]
    for a, c in zip(route, route[1:]):
        d.line((a, c), fill=(184, 83, 25, 255), width=10)
    for i, (px, py) in enumerate(route, start=1):
        d.ellipse((px - 35, py - 35, px + 35, py + 35), fill=(255, 225, 148, 245), outline=(130, 61, 22, 255), width=5)
        label = str(i)
        tw, th = text_wh(d, label, f(29, serif=True))
        d.text((px - tw / 2, py - th / 2 - 3), label, font=f(29, serif=True), fill=(107, 45, 16, 255))
    labels = [("入口打卡", "形象门头、导视拍照"), ("市集漫游", "摊架、展陈、快闪"), ("休憩停留", "座椅、树荫、外摆"), ("夜间点亮", "灯带、橱窗、活动")]
    lx, ly = ix1 + 28, iy2 - 270
    for i, (name, desc) in enumerate(labels):
        yy = ly + i * 58
        d.rounded_rectangle((lx, yy, lx + 305, yy + 42), radius=8, fill=(255, 241, 211, 205), outline=(177, 89, 26, 120), width=2)
        d.text((lx + 16, yy + 6), name, font=f(22, serif=True), fill=(93, 45, 17, 255))
        d.text((lx + 116, yy + 9), desc, font=f(18), fill=(110, 76, 44, 255))


def draw_wind_relation(canvas: Image.Image, b: tuple[int, int, int, int]) -> None:
    d = ImageDraw.Draw(canvas)
    panel(d, b, "互动动线与停留关系图")
    x1, y1, x2, y2 = b
    cx = (x1 + x2) // 2
    base_y = y2 - 82
    d.line((x1 + 64, base_y, x2 - 64, base_y), fill=(100, 70, 44, 210), width=6)
    for x in range(x1 + 96, x2 - 96, 120):
        d.line((x, base_y, x + 50, y1 + 122), fill=(96, 69, 50, 160), width=3)
    d.arc((cx - 250, y1 + 90, cx + 250, y2 - 80), 185, 355, fill=(77, 59, 45, 210), width=8)
    colors = [(179, 88, 26, 255), (213, 141, 46, 255), (104, 115, 80, 255)]
    names = ["通行流线", "停留节点", "活动外摆"]
    for i in range(5):
        x = x1 + 102 + i * 170
        y = y1 + 116 + (i % 2) * 70
        d.ellipse((x - 28, y - 28, x + 28, y + 28), fill=colors[i % 3])
        d.text((x + 40, y - 20), names[i % 3], font=f(22), fill=(102, 68, 38, 255))
    for i, c in enumerate(colors):
        yy = y2 - 54 + i * 0
        d.rectangle((x1 + 62 + i * 210, y2 - 50, x1 + 102 + i * 210, y2 - 28), fill=c)
        d.text((x1 + 116 + i * 210, y2 - 56), names[i], font=f(20), fill=(105, 72, 42, 255))


def draw_bottom_panels(canvas: Image.Image, photo: Image.Image) -> None:
    d = ImageDraw.Draw(canvas)
    panels = [
        (box(30, 1088, 216, 1208), "小品策略", "坐、看、逛、拍四类动作串联入口街角。"),
        (box(225, 1088, 405, 1208), "材料策略", "红砖、钢、木、石与秋色植物形成统一语言。"),
        (box(416, 1088, 638, 1208), "互动策略", "入口打卡、集市漫游、夜间运营分时组织。"),
        (box(650, 1088, 840, 1208), "运营场景", "早市、周末文创、夜间轻活动灵活切换。"),
        (box(850, 1088, 1024, 1208), "色彩关键词", "暖砖红、耐候橙、木色、植物灰绿。"),
    ]
    for b, title, desc in panels:
        panel(d, b, title)
        wrap_text(d, (b[0] + 22, b[1] + 84), desc, f(20), (103, 69, 39, 255), b[2] - b[0] - 44, 5)
    # Row with image-led cards.
    cards = [
        (box(30, 1220, 220, 1355), "入口效果局部", (0.46, 0.62)),
        (box(235, 1220, 420, 1355), "外摆活动", (0.34, 0.72)),
        (box(435, 1220, 620, 1355), "夜景点亮", (0.58, 0.48)),
    ]
    for b, title, anchor in cards:
        paste_round(canvas, warm_photo(photo), (b[0], b[1] + 42, b[2], b[3] - 10), radius=8, cover=True, anchor=anchor)
        d.rectangle((b[0], b[1], b[2], b[1] + 42), fill=(177, 88, 26, 238))
        d.text((b[0] + 14, b[1] + 8), title, font=f(22, serif=True), fill=(255, 238, 205, 255))
        d.rounded_rectangle(b, radius=8, outline=(181, 111, 49, 150), width=2)
    # Materials and icons in the lower right, matching the dense strip of the reference board.
    mat_box = box(640, 1220, 1024, 1464)
    panel(d, mat_box, "材料与互动图例")
    x1, y1, x2, y2 = mat_box
    mats = [("红砖", "brick"), ("耐候钢", "steel"), ("木", "wood"), ("石", "stone"), ("植物", "plant")]
    sw = (x2 - x1 - 80) // 5
    for i, (name, kind) in enumerate(mats):
        sx = x1 + 30 + i * (sw + 10)
        sy = y1 + 86
        tex = material_texture(kind, (sw, 72))
        canvas.paste(tex, (sx, sy), rounded_mask((sw, 72), 8))
        d.text((sx, sy + 82), name, font=f(18), fill=(99, 67, 39, 255))
    for i, name in enumerate(["拍照点", "停留点", "摊位点", "灯光点"]):
        xx = x1 + 36 + (i % 2) * 180
        yy = y1 + 194 + (i // 2) * 58
        d.ellipse((xx, yy, xx + 34, yy + 34), fill=(177, 88, 26, 245))
        d.text((xx + 48, yy + 2), name, font=f(22), fill=(103, 69, 39, 255))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    canvas = paper_background()
    decorate(canvas)
    draw_header(canvas)
    photo = Image.open(PHOTO).convert("RGB")

    # First-image structure, replaced content.
    draw_objects_large(canvas, box(30, 120, 278, 446))
    draw_object_detail(canvas, box(302, 120, 493, 252), "矿轨座椅节点", "node")
    draw_object_detail(canvas, box(302, 264, 493, 426), "导视灯架节点", "frame")
    draw_material_board(canvas, box(30, 458, 278, 618))
    draw_material_detail(canvas, box(302, 458, 493, 618))
    draw_effect_area(canvas, photo)
    draw_interaction_strategy(canvas, box(520, 523, 1035, 754), photo)
    draw_wind_relation(canvas, box(520, 783, 1035, 1012))
    draw_material_detail(canvas, box(30, 632, 500, 787))
    draw_material_board(canvas, box(30, 810, 500, 1050))
    draw_bottom_panels(canvas, photo)

    # Small footer slogan, preserving the long reference-board feel.
    d = ImageDraw.Draw(canvas)
    d.text((box(36, 1465, 0, 0)[0], box(0, 1465, 0, 0)[1]), "留住工业记忆，放大市井烟火，让街角成为可参与、可停留、可运营的开放场景。",
           font=f(30, serif=True), fill=(133, 75, 30, 235))

    rgb = canvas.convert("RGB")
    png = OUT / "coal-town-a3-same-structure-landscape-intent.png"
    jpg = OUT / "coal-town-a3-same-structure-landscape-intent.jpg"
    pdf = OUT / "coal-town-a3-same-structure-landscape-intent.pdf"
    rgb.save(png, dpi=(300, 300))
    rgb.save(jpg, quality=95, dpi=(300, 300), subsampling=0)
    rgb.save(pdf, "PDF", resolution=300.0)
    print(png.resolve())
    print(jpg.resolve())
    print(pdf.resolve())


if __name__ == "__main__":
    main()
