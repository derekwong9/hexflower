from __future__ import annotations

from typing import List

from .hex import Hex


class HexTraversal:
    """Ring traversal in axial coords (pointy-top)."""

    @staticmethod
    def ring(center: Hex, radius: int) -> List[Hex]:
        if radius < 0:
            raise ValueError("radius must be >= 0")
        if radius == 0:
            return [center]

        # Start at SW * radius (DIR index 4)
        h = center.scale_dir(4, radius)
        out: List[Hex] = []
        for side in range(6):
            for _ in range(radius):
                out.append(h)
                h = h.neighbor(side)
        return out

    @staticmethod
    def spiral(center: Hex, radius: int) -> List[Hex]:
        """All hexes from ring 0..radius in order (center first)."""
        out: List[Hex] = []
        for r in range(0, radius + 1):
            out.extend(HexTraversal.ring(center, r))
        return out
