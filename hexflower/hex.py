from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True, slots=True, order=True)
class Hex:
    """Axial hex coordinate (q, r), pointy-top orientation."""
    q: int
    r: int

    # Axial direction vectors (pointy-top)
    DIRS: Tuple[Tuple[int, int], ...] = (
        (1, 0),    # E
        (1, -1),   # NE
        (0, -1),   # NW
        (-1, 0),   # W
        (-1, 1),   # SW
        (0, 1),    # SE
    )

    def neighbor(self, direction_index: int) -> "Hex":
        dq, dr = self.DIRS[direction_index]
        return Hex(self.q + dq, self.r + dr)

    def neighbors(self) -> List["Hex"]:
        return [self.neighbor(i) for i in range(6)]

    def add(self, dq: int, dr: int) -> "Hex":
        return Hex(self.q + dq, self.r + dr)

    def scale_dir(self, direction_index: int, k: int) -> "Hex":
        dq, dr = self.DIRS[direction_index]
        return Hex(self.q + dq * k, self.r + dr * k)

    def distance(self, other: "Hex") -> int:
        """
        Axial distance:
        max(|dq|, |dr|, |d(q+r)|)
        """
        dq = self.q - other.q
        dr = self.r - other.r
        return max(abs(dq), abs(dr), abs((self.q + self.r) - (other.q + other.r)))

    def __str__(self) -> str:
        return f"({self.q},{self.r})"
