#!/usr/bin/env python3
"""Generate the animated profile assets used by the GitHub README."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCALE = 2
FRAMES = 36
DURATION_MS = 85

MONO = "/System/Library/Fonts/Menlo.ttc"
MONO_BOLD = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO_BOLD if bold else MONO, size * SCALE)


def canvas(width: int, height: int) -> Image.Image:
    return Image.new("RGB", (width * SCALE, height * SCALE), "#f8f7f3")


def xy(values: tuple[float, ...]) -> tuple[int, ...]:
    return tuple(round(value * SCALE) for value in values)


def text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    value: str,
    size: int,
    color: str,
    *,
    bold: bool = False,
    anchor: str | None = None,
) -> None:
    draw.text(xy(position), value, font=font(size, bold=bold), fill=color, anchor=anchor)


def downsample(image: Image.Image, width: int, height: int) -> Image.Image:
    return image.resize((width, height), Image.Resampling.LANCZOS)


def glow_layer(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGBA", size, (0, 0, 0, 0))


def composite_glow(base: Image.Image, overlay: Image.Image, radius: int = 10) -> None:
    blurred = overlay.filter(ImageFilter.GaussianBlur(radius * SCALE))
    base.paste(blurred, (0, 0), blurred)
    base.paste(overlay, (0, 0), overlay)


def save_gif(frames: list[Image.Image], path: Path) -> None:
    palette = frames[0].quantize(colors=192, method=Image.Quantize.MEDIANCUT)
    indexed = [palette]
    indexed.extend(
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in frames[1:]
    )
    indexed[0].save(
        path,
        save_all=True,
        append_images=indexed[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )


def flame_points(cx: float, base_y: float, height: float, width: float, phase: float) -> list[tuple[int, int]]:
    lean = math.sin(phase * math.tau) * width * 0.22
    return [
        xy((cx - width / 2, base_y)),
        xy((cx - width * 0.34, base_y - height * 0.38)),
        xy((cx + lean, base_y - height)),
        xy((cx + width * 0.27, base_y - height * 0.43)),
        xy((cx + width / 2, base_y)),
    ]


def generate_terminal_embers() -> None:
    width, height = 1200, 360
    coal_groups = (
        ((82, 338, 13), (116, 333, 18), (158, 340, 15), (201, 332, 20), (247, 339, 16)),
        ((478, 337, 17), (522, 331, 21), (571, 338, 17), (616, 330, 22), (666, 339, 16)),
        ((904, 338, 15), (946, 331, 20), (994, 339, 17), (1040, 332, 19), (1083, 339, 14)),
    )
    sparks = (
        (193, 326, 0.00, -18),
        (216, 330, 0.34, 13),
        (586, 329, 0.14, -11),
        (607, 328, 0.48, 15),
        (636, 331, 0.78, -6),
        (994, 330, 0.22, 10),
        (1021, 329, 0.60, -12),
        (1050, 331, 0.86, 8),
    )
    frames: list[Image.Image] = []

    for frame_index in range(FRAMES):
        t = frame_index / FRAMES
        image = canvas(width, height)
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(xy((12, 12, 1188, 348)), radius=22 * SCALE, fill="#f8f7f3", outline="#d6d3d1", width=2 * SCALE)
        draw.line(xy((12, 62, 1188, 62)), fill="#dedbd4", width=SCALE)
        for cx, color in ((42, "#fb923c"), (64, "#facc15"), (86, "#60a5fa")):
            draw.ellipse(xy((cx - 6, 31, cx + 6, 43)), fill=color)
        text(draw, (1118, 42), "profile.sh", 14, "#78716c", anchor="ra")
        text(draw, (62, 105), "$ profile --show", 17, "#c2410c")
        text(draw, (62, 164), "NAZARII HAFYCH", 38, "#1c1917", bold=True, anchor="ls")
        if frame_index % 14 < 8:
            draw.rounded_rectangle(xy((423, 132, 440, 170)), radius=2 * SCALE, fill="#f97316")
        text(draw, (64, 203), "computational science / data / AI evaluation / product engineering", 17, "#57534e")
        text(draw, (64, 236), "Kraków · CET/CEST · inspectable systems · reproducible results", 15, "#78716c")

        for x in range(62, 1138):
            ratio = (x - 62) / 1076
            strength = math.sin(math.pi * ratio)
            red = round(249 + (37 - 249) * ratio)
            green = round(115 + (99 - 115) * ratio)
            blue = round(22 + (235 - 22) * ratio)
            color = (red, green, blue)
            draw.point((x * SCALE, 264 * SCALE), fill=color)
            if strength > 0.25:
                draw.point((x * SCALE, 265 * SCALE), fill=color)

        glow = glow_layer(image.size)
        gd = ImageDraw.Draw(glow)
        group_centers = (170, 575, 1008)
        for group_index, center in enumerate(group_centers):
            pulse = 0.55 + 0.35 * math.sin((t + group_index * 0.28) * math.tau)
            gd.ellipse(xy((center - 116, 323, center + 116, 357)), fill=(249, 115, 22, round(80 * pulse)))
        composite_glow(image, glow, radius=9)
        draw = ImageDraw.Draw(image)

        for group in coal_groups:
            for coal_index, (cx, cy, radius) in enumerate(group):
                pulse = 0.82 + 0.18 * math.sin((t * 1.4 + coal_index * 0.12) * math.tau)
                outer = "#7c2d12"
                inner = (round(234 + 21 * pulse), round(88 + 60 * pulse), round(12 + 18 * pulse))
                draw.ellipse(xy((cx - radius, cy - radius, cx + radius, cy + radius)), fill=outer)
                draw.ellipse(xy((cx - radius + 3, cy - radius + 3, cx + radius - 3, cy + radius - 3)), fill=inner)
                hot = radius * 0.34
                draw.ellipse(xy((cx - hot, cy - hot, cx + hot, cy + hot)), fill="#fdba74")

        flame_specs = ((195, 345, 61, 38, 0.00), (606, 345, 69, 42, 0.31), (1019, 345, 57, 36, 0.62))
        flames = glow_layer(image.size)
        fd = ImageDraw.Draw(flames)
        for cx, base_y, max_height, flame_width, offset in flame_specs:
            wave = (math.sin((t + offset) * math.tau) + 1) / 2
            intensity = 0.18 + wave**3 * 0.82
            height_now = max_height * (0.48 + 0.52 * intensity)
            fill = (249, 115, 22, round(60 + 130 * intensity))
            fd.polygon(flame_points(cx, base_y, height_now, flame_width, t + offset), fill=fill)
        composite_glow(image, flames, radius=5)

        spark_glow = glow_layer(image.size)
        sd = ImageDraw.Draw(spark_glow)
        for sx, sy, offset, drift in sparks:
            progress = (t + offset) % 1
            px = sx + drift * progress + math.sin((progress + offset) * math.tau) * 4
            py = sy - progress * 108
            opacity = round(math.sin(progress * math.pi) * 230)
            radius = 2.2 if progress < 0.65 else 1.4
            sd.ellipse(xy((px - radius, py - radius, px + radius, py + radius)), fill=(249, 115, 22, opacity))
        composite_glow(image, spark_glow, radius=3)

        frames.append(downsample(image, width, height))

    save_gif(frames, ASSETS / "terminal-embers.gif")


def bezier(points: tuple[tuple[float, float], ...], t: float) -> tuple[float, float]:
    p0, p1, p2, p3 = points
    u = 1 - t
    x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
    return x, y


def dashed_curve(draw: ImageDraw.ImageDraw, points: tuple[tuple[float, float], ...], offset: int) -> None:
    samples = [bezier(points, index / 80) for index in range(81)]
    for index, (start, end) in enumerate(zip(samples, samples[1:])):
        if ((index + offset) // 5) % 2 == 0:
            draw.line((*xy(start), *xy(end)), fill="#b8b4ad", width=2 * SCALE)


def node(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    color: str,
    outline: str,
) -> None:
    draw.rounded_rectangle(xy(box), radius=12 * SCALE, fill="#ffffff", outline=outline, width=SCALE)
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2 + 1
    text(draw, (cx, cy), label, 17, color, bold=True, anchor="mm")


def generate_system_map() -> None:
    width, height = 1200, 250
    paths = (
        ((465, 112), (405, 84), (350, 62), (292, 62)),
        ((465, 130), (400, 146), (350, 181), (302, 185)),
        ((735, 112), (795, 82), (850, 62), (908, 62)),
        ((735, 130), (800, 145), (850, 181), (898, 185)),
    )
    frames: list[Image.Image] = []

    for frame_index in range(FRAMES):
        t = frame_index / FRAMES
        image = canvas(width, height)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(xy((12, 12, 1188, 238)), radius=22 * SCALE, fill="#f8f7f3", outline="#d6d3d1", width=2 * SCALE)

        dash_offset = frame_index // 2
        for path in paths:
            dashed_curve(draw, path, dash_offset)
        for y in range(161, 210, 12):
            draw.line(xy((600, y, 600, min(y + 6, 210))), fill="#fb923c", width=2 * SCALE)

        node(draw, (92, 36, 292, 88), "SCIENCE", "#1d4ed8", "#bfdbfe")
        node(draw, (82, 159, 302, 211), "DATA / ANALYSIS", "#1d4ed8", "#bfdbfe")
        node(draw, (908, 36, 1108, 88), "AI EVALUATION", "#c2410c", "#fed7aa")
        node(draw, (898, 159, 1118, 211), "PRODUCT SYSTEMS", "#c2410c", "#fed7aa")

        pulse = (math.sin(t * math.tau) + 1) / 2
        border = (251, round(134 + 13 * pulse), round(49 + 22 * pulse))
        draw.rounded_rectangle(xy((465, 83, 735, 163)), radius=17 * SCALE, fill="#fff2df", outline=border, width=2 * SCALE)
        text(draw, (600, 111), "NAZARII / BUILDER", 14, "#9a3412", anchor="mm")
        text(draw, (600, 139), "INSPECTABLE SYSTEMS", 18, "#1c1917", bold=True, anchor="mm")
        draw.rounded_rectangle(xy((506, 204, 694, 233)), radius=9 * SCALE, fill="#292524")
        text(draw, (600, 219), "SECURITY + RELIABILITY", 13, "#fdba74", anchor="mm")

        dots = glow_layer(image.size)
        dd = ImageDraw.Draw(dots)
        for path_index, path in enumerate(paths):
            progress = (t + path_index * 0.19) % 1
            if path_index < 2:
                progress = 1 - progress
            px, py = bezier(path, progress)
            dd.ellipse(xy((px - 4, py - 4, px + 4, py + 4)), fill=(249, 115, 22, 245))
        composite_glow(image, dots, radius=4)

        frames.append(downsample(image, width, height))

    save_gif(frames, ASSETS / "system-map.gif")


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_terminal_embers()
    generate_system_map()
