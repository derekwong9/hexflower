from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from .hex import Hex

Biome = str


class HexGrid:
    """Sparse hex grid mapping Hex -> Biome (or any payload)."""

    def __init__(self) -> None:
        self._cells: Dict[Hex, Biome] = {}

    def __len__(self) -> int:
        return len(self._cells)

    def __contains__(self, h: Hex) -> bool:
        return h in self._cells

    def items(self) -> Iterable[Tuple[Hex, Biome]]:
        return self._cells.items()

    def keys(self) -> Iterable[Hex]:
        return self._cells.keys()

    def get(self, h: Hex) -> Optional[Biome]:
        return self._cells.get(h)

    def set(self, h: Hex, value: Biome) -> None:
        self._cells[h] = value

    def update(self, other: "HexGrid") -> None:
        self._cells.update(other._cells)

    def is_disjoint(self, other: "HexGrid") -> bool:
        return set(self._cells.keys()).isdisjoint(other._cells.keys())

    def touches(self, other: "HexGrid") -> bool:
        """True if any hex in self is edge-adjacent to any hex in other."""
        other_keys = set(other._cells.keys())
        for h in self._cells.keys():
            for nb in h.neighbors():
                if nb in other_keys:
                    return True
        return False

    def translate(self, dq: int, dr: int) -> "HexGrid":
        out = HexGrid()
        for h, v in self._cells.items():
            out.set(h.add(dq, dr), v)
        return out

    def bbox_pixels(self, layout: "PointyTopLayout") -> Tuple[float, float, float, float]:
        """
        Returns (min_x, max_x, min_y, max_y) of hex centers in pixel space.
        Layout is duck-typed: needs layout.axial_to_pixel(Hex) -> (x, y).
        """
        if not self._cells:
            return (0.0, 0.0, 0.0, 0.0)

        xs: List[float] = []
        ys: List[float] = []
        for h in self._cells.keys():
            x, y = layout.axial_to_pixel(h)
            xs.append(x)
            ys.append(y)
        return (min(xs), max(xs), min(ys), max(ys))

    def to_jsonable_list(self) -> List[dict]:
        """Stable, human-readable JSON structure."""
        out: List[dict] = []
        for h, v in sorted(self._cells.items(), key=lambda kv: (kv[0].r, kv[0].q)):
            out.append({"q": h.q, "r": h.r, "value": v})
        return out