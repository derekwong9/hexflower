from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .grid import HexGrid
from .hex import Hex

Biome = str


@dataclass(frozen=True, slots=True)
class PointyTopLayout:
    """Axial -> pixel conversion for pointy-top hexes."""
    size: float  # hex radius in px

    def axial_to_pixel(self, h: Hex) -> Tuple[float, float]:
        x = self.size * math.sqrt(3) * (h.q + h.r / 2)
        y = self.size * 1.5 * h.r
        return x, y

    def hex_corners(self, cx: float, cy: float) -> List[Tuple[float, float]]:
        pts: List[Tuple[float, float]] = []
        for i in range(6):
            angle = math.radians(60 * i - 30)  # pointy-top
            pts.append((cx + self.size * math.cos(angle), cy + self.size * math.sin(angle)))
        return pts


class SVGRenderer:
    """Render a HexGrid to SVG."""

    DEFAULT_PALETTE: Dict[Biome, str] = {
        "grassland": "#9ACD32",
        "forest": "#2E8B57",
        "hills": "#C2B280",
        "marsh": "#5F9EA0",
        "mountains": "#A9A9A9",
    }

    def __init__(
        self,
        layout: PointyTopLayout,
        palette: Optional[Dict[Biome, str]] = None,
        stroke: str = "#333333",
        stroke_width: float = 2.0,
        background: str = "white",
    ) -> None:
        self.layout = layout
        self.palette = palette or self.DEFAULT_PALETTE
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.background = background

    def render(
        self,
        grid: HexGrid,
        title: str,
        show_coords: bool = True,
        show_biome_label: bool = True,
        padding_factor: float = 2.2,
    ) -> str:
        if len(grid) == 0:
            raise ValueError("Cannot render an empty grid.")

        minx, maxx, miny, maxy = grid.bbox_pixels(self.layout)
        pad = self.layout.size * padding_factor

        view_minx = minx - pad
        view_miny = miny - pad
        width = (maxx - minx) + 2 * pad
        height = (maxy - miny) + 2 * pad

        def esc(s: str) -> str:
            return (
                s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("'", "&apos;")
            )

        parts: List[str] = []
        parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width:.0f}" height="{height:.0f}" '
            f'viewBox="{view_minx:.0f} {view_miny:.0f} {width:.0f} {height:.0f}">'
        )
        parts.append(
            f'<rect x="{view_minx:.0f}" y="{view_miny:.0f}" width="{width:.0f}" height="{height:.0f}" fill="{esc(self.background)}"/>'
        )

        parts.append(
            f'<text x="{view_minx + pad/2:.1f}" y="{view_miny + pad/2:.1f}" '
            f'font-family="Arial" font-size="18" fill="#111">{esc(title)}</text>'
        )

        for h, biome in sorted(grid.items(), key=lambda kv: (kv[0].r, kv[0].q)):
            cx, cy = self.layout.axial_to_pixel(h)
            corners = self.layout.hex_corners(cx, cy)
            pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in corners)
            fill = self.palette.get(biome, "#DDDDDD")

            parts.append(
                f'<polygon points="{pts_str}" fill="{esc(fill)}" '
                f'stroke="{esc(self.stroke)}" stroke-width="{self.stroke_width:.2f}"/>'
            )

            if show_coords:
                parts.append(
                    f'<text x="{cx:.1f}" y="{cy - 2:.1f}" '
                    f'font-family="Arial" font-size="12" text-anchor="middle" fill="#111">'
                    f'{esc(f"{h.q},{h.r}")}</text>'
                )
            if show_biome_label:
                parts.append(
                    f'<text x="{cx:.1f}" y="{cy + 16:.1f}" '
                    f'font-family="Arial" font-size="11" text-anchor="middle" fill="#111">'
                    f'{esc(biome)}</text>'
                )

        parts.append("</svg>")
        return "\n".join(parts)

    def write_svg(self, grid: HexGrid, path: Path, **kwargs) -> None:
        svg = self.render(grid, **kwargs)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8")
