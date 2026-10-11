#!/usr/bin/env python3
"""Draw docs/linkedin.png from the measured plate framework.

Does not render HTML. Geometry, type sizes, and colors come from plate.py,
which was measured off the HTML screenshot component by component.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "linkedin.png"
SVG = ROOT / "docs" / "linkedin.svg"

STORIES = (
    {
        "head": "Block n",
        "title": "The Last Lamp",
        "score": "4.4",
        "scores": (4.4, 4.6, 4.4, 4.3, 4.5),
        "parts": (
            ("Mara reached the ", False),
            ("harbor", True),
            (" after the last ferry had gone. She lit the ", False),
            ("lantern", True),
            (", set it on a crate of ", False),
            ("salt", True),
            (", and pinned the ", False),
            ("map", True),
            (" under a stone so the wind could not take Tomas’s mark. Out past the pier, the ", False),
            ("tide", True),
            (" was already turning. She would wait the night.", False),
        ),
    },
    {
        "head": "Block n+1",
        "title": "What the Tide Kept",
        "score": "4.6",
        "scores": (4.5, 4.7, 4.5, 4.5, 4.7),
        "parts": (
            ("At dawn the ", False),
            ("lantern", True),
            (" was cold. ", False),
            ("Salt", True),
            (" had crusted Tomas’s mark on the ", False),
            ("map", True),
            (", and the ink had run to a cove Mara had never drawn. She walked the empty ", False),
            ("harbor", True),
            (" until the ", False),
            ("tide", True),
            (" laid his skiff on the stones, oar still lashed, and a second lantern burning inside.", False),
        ),
    },
)


def rgb(color: tuple[int, int, int]) -> tuple[float, float, float]:
    return tuple(c / 255 for c in color)


def hex_of(color: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*color)


def set_font(cr, family: str, size: float, bold: bool = False, italic: bool = False) -> None:
    cr.select_font_face(
        family,
        cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL,
    )
    cr.set_font_size(size)


def center(cr, spec: plate.TextSpec) -> None:
    set_font(cr, spec.family, spec.size, bold=spec.bold, italic=spec.italic)
    cr.set_source_rgb(*rgb(spec.fill))
    ext = cr.text_extents(spec.text)
    cr.move_to(spec.cx - (ext.x_bearing + ext.width / 2), spec.cy - (ext.y_bearing + ext.height / 2))
    cr.show_text(spec.text)


def tracked(cr, spec: plate.TextSpec) -> None:
    set_font(cr, spec.family, spec.size, bold=spec.bold)
    cr.set_source_rgb(*rgb(spec.fill))
    widths = [cr.text_extents(ch).x_advance for ch in spec.text]
    total = sum(widths) + spec.tracking * (len(spec.text) - 1)
    x = spec.cx - total / 2
    for ch, advance in zip(spec.text, widths):
        ext = cr.text_extents(ch)
        cr.move_to(x - ext.x_bearing, spec.cy - (ext.y_bearing + ext.height / 2))
        cr.show_text(ch)
        x += advance + spec.tracking


def draw_measured_line(cr, x: float, pieces, baseline: float) -> None:
    size = plate.STORY_SIZE
    pen = x
    for text, mark in pieces:
        set_font(cr, plate.STORY_FACE, size, bold=mark)
        advance = cr.text_extents(text).x_advance
        if mark:
            cr.set_source_rgb(*rgb(plate.HL_BG))
            cr.rectangle(pen - 2, baseline - size * 0.95, advance + 4, size * 1.25)
            cr.fill()
            cr.set_source_rgb(*rgb(plate.HL))
            set_font(cr, plate.STORY_FACE, size, bold=True)
        else:
            cr.set_source_rgb(*rgb(plate.NAVY))
        cr.move_to(pen, baseline)
        cr.show_text(text)
        pen += advance


def draw_story(cr, lines) -> None:
    baseline = plate.STORY_BASELINE
    for x, pieces in lines:
        draw_measured_line(cr, x, pieces, baseline)
        baseline += plate.STORY_LINE_H


def radar_point(cx: float, cy: float, radius: float, index: int, score: float):
    angle = -math.pi / 2 + index * (2 * math.pi / 5)
    reach = radius * (score / 5)
    return cx + math.cos(angle) * reach, cy + math.sin(angle) * reach


def draw_radar(cr, cx: float, cy: float, scores) -> None:
    radius = plate.RADAR_RADIUS
    cr.set_line_width(1.1)
    cr.set_source_rgb(*rgb(plate.RING))
    for scale in (1, 0.75, 0.5, 0.25):
        pts = [radar_point(cx, cy, radius * scale, i, 5) for i in range(5)]
        cr.move_to(*pts[0])
        for pt in pts[1:]:
            cr.line_to(*pt)
        cr.close_path()
        cr.stroke()
    cr.set_source_rgba(*rgb(plate.NAVY), 0.28)
    cr.set_line_width(0.8)
    for i in range(5):
        cr.move_to(cx, cy)
        cr.line_to(*radar_point(cx, cy, radius, i, 5))
        cr.stroke()
    fill_pts = [radar_point(cx, cy, radius, i, scores[i]) for i in range(5)]
    cr.set_source_rgba(*rgb(plate.GREEN), 0.30)
    cr.move_to(*fill_pts[0])
    for pt in fill_pts[1:]:
        cr.line_to(*pt)
    cr.close_path()
    cr.fill_preserve()
    cr.set_source_rgb(*rgb(plate.GREEN))
    cr.set_line_width(2.2)
    cr.stroke()
    for pt in fill_pts:
        cr.arc(pt[0], pt[1], 3.4, 0, math.tau)
        cr.fill()
    set_font(cr, plate.SANS, 14, bold=True)
    cr.set_source_rgb(*rgb(plate.NAVY))
    for i, (dx, dy, anchor) in enumerate(plate.LABEL_OFFSETS):
        text = f"{plate.AXES[i]} {scores[i]:.1f}"
        ext = cr.text_extents(text)
        x = cx + dx
        if anchor == "middle":
            x -= ext.x_bearing + ext.width / 2
        elif anchor == "end":
            x -= ext.x_advance
        cr.move_to(x, cy + dy)
        cr.show_text(text)


def draw_block(cr, box: plate.Box, story: dict) -> None:
    cr.set_source_rgb(*rgb(plate.NAVY))
    cr.rectangle(box.x, box.y, box.w, plate.HEADER_H)
    cr.fill()
    cr.set_line_width(2)
    cr.rectangle(box.x + 1, box.y + 1, box.w - 2, box.h - 2)
    cr.stroke()
    head = plate.TextSpec(
        story["head"], plate.SANS, plate.HEADER_LABEL_SIZE, plate.CREAM,
        cx=box.cx, cy=plate.HEADER_LABEL_CY, bold=True,
    )
    center(cr, head)
    title = plate.TextSpec(
        story["title"], plate.STORY_TITLE_FACE, plate.STORY_TITLE_SIZE, plate.NAVY,
        cx=box.cx, cy=plate.STORY_TITLE_CY, italic=True,
    )
    center(cr, title)
    cr.set_source_rgb(*rgb(plate.NAVY))
    cr.set_line_width(1.5)
    cr.move_to(box.x + 16, plate.TITLE_RULE_Y)
    cr.line_to(box.right - 16, plate.TITLE_RULE_Y)
    cr.stroke()
    draw_story(cr, plate.LEFT_LINES if box is plate.LEFT else plate.RIGHT_LINES)
    draw_radar(cr, box.cx, plate.RADAR_CY, story["scores"])
    score = plate.TextSpec(story["score"], plate.SERIF, 18, plate.NAVY, cx=box.cx - 18, cy=plate.SCORE_CY, bold=True)
    center(cr, score)
    set_font(cr, plate.SERIF, 18, bold=True)
    half = cr.text_extents(story["score"]).width / 2
    set_font(cr, plate.SANS, 16)
    cr.set_source_rgb(*rgb(plate.TAUPE))
    cr.move_to(box.cx - 18 + half + 8, plate.SCORE_CY + 4)
    cr.show_text("of 5")


def render_png() -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, plate.W, plate.H)
    cr = cairo.Context(surf)
    cr.set_source_rgb(*rgb(plate.CREAM))
    cr.paint()
    tracked(cr, plate.KICKER)
    center(cr, plate.TITLE)
    center(cr, plate.TAGLINE)
    draw_block(cr, plate.LEFT, STORIES[0])
    draw_block(cr, plate.RIGHT, STORIES[1])
    arrow = plate.TextSpec("→", plate.SERIF, 36, plate.NAVY, cx=(plate.LEFT.right + plate.RIGHT.x) / 2, cy=557)
    center(cr, arrow)
    center(cr, plate.COPYRIGHT)
    surf.write_to_png(str(OUT))


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;")


def svg_text(spec: plate.TextSpec, extra: str = "") -> str:
    style = ""
    if spec.italic:
        style += ' font-style="italic"'
    if spec.bold:
        style += ' font-weight="700"'
    if spec.tracking:
        style += f' letter-spacing="{spec.tracking}"'
    return (
        f'<text x="{spec.cx}" y="{spec.cy}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="{spec.family}, serif" font-size="{spec.size}"{style} fill="{hex_of(spec.fill)}"{extra}>'
        f"{esc(spec.text)}</text>"
    )


def svg_font(family: str) -> str:
    if family == plate.SANS:
        return "Lato, sans-serif"
    if family == plate.SERIF_CJK:
        return "Noto Serif CJK KR, Liberation Serif, serif"
    return f"{family}, Liberation Serif, serif"


def svg_run(text: str, x: float, y: float, family: str, size: float, fill, *, bold=False, italic=False, anchor="start") -> str:
    style = ""
    if italic:
        style += ' font-style="italic"'
    if bold:
        style += ' font-weight="700"'
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{svg_font(family)}" font-size="{size}"{style} fill="{hex_of(fill)}">{esc(text)}</text>'
    )


def measure_lines() -> list[list[tuple[str, bool, float]]]:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
    cr = cairo.Context(surf)
    measured = []
    for lines in (plate.LEFT_LINES, plate.RIGHT_LINES):
        block = []
        for _x, pieces in lines:
            row = []
            for text, mark in pieces:
                set_font(cr, plate.STORY_FACE, plate.STORY_SIZE, bold=mark)
                row.append((text, mark, cr.text_extents(text).x_advance))
            block.append(row)
        measured.append(block)
    return measured


def svg_story(lines, measured) -> list[str]:
    out = []
    baseline = plate.STORY_BASELINE
    size = plate.STORY_SIZE
    for (x, _pieces), row in zip(lines, measured):
        pen = x
        for text, mark, advance in row:
            if mark:
                out.append(
                    f'  <rect x="{pen - 2:.1f}" y="{baseline - size * 0.95:.1f}" width="{advance + 4:.1f}" height="{size * 1.25:.1f}" fill="{hex_of(plate.HL_BG)}"/>'
                )
            out.append(
                "  " + svg_run(
                    text, pen, baseline, plate.STORY_FACE, size,
                    plate.HL if mark else plate.NAVY, bold=mark,
                )
            )
            pen += advance
        baseline += plate.STORY_LINE_H
    return out


def svg_radar(cx: float, cy: float, scores) -> list[str]:
    radius = plate.RADAR_RADIUS
    out = []
    ring = hex_of(plate.RING)
    for scale in (1, 0.75, 0.5, 0.25):
        pts = [radar_point(cx, cy, radius * scale, i, 5) for i in range(5)]
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        out.append(f'  <polygon points="{points}" fill="none" stroke="{ring}" stroke-width="1.1"/>')
    navy = hex_of(plate.NAVY)
    for i in range(5):
        x, y = radar_point(cx, cy, radius, i, 5)
        out.append(f'  <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{navy}" stroke-opacity="0.28" stroke-width="0.8"/>')
    fill_pts = [radar_point(cx, cy, radius, i, scores[i]) for i in range(5)]
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in fill_pts)
    green = hex_of(plate.GREEN)
    out.append(f'  <polygon points="{points}" fill="{green}" fill-opacity="0.30" stroke="{green}" stroke-width="2.2"/>')
    for x, y in fill_pts:
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{green}"/>')
    for i, (dx, dy, anchor) in enumerate(plate.LABEL_OFFSETS):
        text = f"{plate.AXES[i]} {scores[i]:.1f}"
        out.append("  " + svg_run(text, cx + dx, cy + dy, plate.SANS, 14, plate.NAVY, bold=True, anchor=anchor))
    return out


def render_svg() -> None:
    measured = measure_lines()
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{plate.W}" height="{plate.H}" viewBox="0 0 {plate.W} {plate.H}">',
        f'  <rect width="{plate.W}" height="{plate.H}" fill="{hex_of(plate.CREAM)}"/>',
        "  " + svg_text(plate.KICKER),
        "  " + svg_text(plate.TITLE),
        "  " + svg_text(plate.TAGLINE),
    ]
    blocks = (
        (plate.LEFT, STORIES[0], plate.LEFT_LINES, measured[0]),
        (plate.RIGHT, STORIES[1], plate.RIGHT_LINES, measured[1]),
    )
    for box, story, story_lines, widths in blocks:
        lines.append(
            f'  <rect x="{box.x}" y="{box.y}" width="{box.w}" height="{box.h}" fill="none" stroke="{hex_of(plate.NAVY)}" stroke-width="2"/>'
        )
        lines.append(
            f'  <rect x="{box.x}" y="{box.y}" width="{box.w}" height="{plate.HEADER_H}" fill="{hex_of(plate.NAVY)}"/>'
        )
        head = plate.TextSpec(
            story["head"], plate.SANS, plate.HEADER_LABEL_SIZE, plate.CREAM,
            cx=box.cx, cy=plate.HEADER_LABEL_CY, bold=True,
        )
        title = plate.TextSpec(
            story["title"], plate.STORY_TITLE_FACE, plate.STORY_TITLE_SIZE, plate.NAVY,
            cx=box.cx, cy=plate.STORY_TITLE_CY, italic=True,
        )
        lines.append("  " + svg_text(head))
        lines.append("  " + svg_text(title))
        lines.append(
            f'  <line x1="{box.x + 16}" y1="{plate.TITLE_RULE_Y}" x2="{box.right - 16}" y2="{plate.TITLE_RULE_Y}" stroke="{hex_of(plate.NAVY)}" stroke-width="1.5"/>'
        )
        lines.extend(svg_story(story_lines, widths))
        lines.extend(svg_radar(box.cx, plate.RADAR_CY, story["scores"]))
        lines.append(
            "  " + svg_run(story["score"], box.cx - 18, plate.SCORE_CY + 6, plate.SERIF, 18, plate.NAVY, bold=True, anchor="middle")
        )
        lines.append(
            "  " + svg_run("of 5", box.cx + 22, plate.SCORE_CY + 6, plate.SANS, 16, plate.TAUPE, anchor="start")
        )
    lines.append(
        "  " + svg_run("→", (plate.LEFT.right + plate.RIGHT.x) / 2, 568, plate.SERIF, 36, plate.NAVY, anchor="middle")
    )
    lines.append("  " + svg_text(plate.COPYRIGHT))
    lines.append("</svg>")
    lines.append("")
    SVG.write_text("\n".join(lines))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    render_png()
    render_svg()
    print(OUT)


if __name__ == "__main__":
    main()
