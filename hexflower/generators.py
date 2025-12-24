from __future__ import annotations

import random
from typing import List, Optional, Tuple

from .grid import HexGrid
from .hex import Hex
from .tables import BiomeTables
from .traversal import HexTraversal

Biome = str


class SnowflakeHexflowerGenerator:
    """
    Generates a "snowflake" cluster ring-by-ring using an inward-neighbor
    as the "previous hex" to bias biome transitions.

    IMPORTANT: The center hex is always generated first and always included.
    """

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    @staticmethod
    def _choose_inward_neighbor(target: Hex, center: Hex, grid: HexGrid) -> Optional[Hex]:
        """
        Prefer an already-generated neighbor that is exactly one step closer to center.
        Fallback to any already-generated neighbor.
        """
        dist_target = target.distance(center)

        inward_candidates: List[Hex] = []
        for nb in target.neighbors():
            if nb in grid and nb.distance(center) == dist_target - 1:
                inward_candidates.append(nb)

        if inward_candidates:
            return inward_candidates[0]  # deterministic choice

        for nb in target.neighbors():
            if nb in grid:
                return nb

        return None

    def generate(self, center: Hex = Hex(0, 0), radius: int = 2) -> HexGrid:
        if radius < 0:
            raise ValueError("radius must be >= 0")

        grid = HexGrid()

        # Center ALWAYS included
        grid.set(center, BiomeTables.start_biome(self.rng))

        # Ring-by-ring fill
        for r in range(1, radius + 1):
            for h in HexTraversal.ring(center, r):
                prev_hex = self._choose_inward_neighbor(h, center, grid)
                if prev_hex is None:
                    # Defensive fallback; should not happen after center is set
                    grid.set(h, BiomeTables.start_biome(self.rng))
                else:
                    prev_biome = grid.get(prev_hex) or "grassland"
                    grid.set(h, BiomeTables.next_biome(prev_biome, self.rng))

        return grid


class ConnectedHexflowerBuilder:
    """
    Places multiple snowflakes so each new one touches the existing super-map
    (edge-adjacent) and does not overlap.

    The first component is always the center snowflake at (0,0).
    """

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def build_chain(self, count: int, radius: int, max_tries: int = 5000) -> HexGrid:
        if count < 1:
            raise ValueError("count must be >= 1")

        gen = SnowflakeHexflowerGenerator(self.rng)

        super_map = HexGrid()
        super_map.update(gen.generate(center=Hex(0, 0), radius=radius))

        for _ in range(count - 1):
            new = gen.generate(center=Hex(0, 0), radius=radius)

            super_keys = list(super_map.keys())
            new_keys = list(new.keys())

            # Precompute frontier targets: empty neighbors adjacent to super_map
            super_set = set(super_map.keys())
            frontier: list[Hex] = []
            for h in super_set:
                for nb in h.neighbors():
                    if nb not in super_set:
                        frontier.append(nb)

            if not frontier:
                raise RuntimeError("No frontier found; super_map unexpectedly has no empty adjacent hexes.")

            placed = False
            for _try in range(max_tries):
                target = self.rng.choice(frontier)  # empty hex adjacent to super_map
                anchor = self.rng.choice(new_keys)  # hex in the new snowflake we will align to target

                dq = target.q - anchor.q
                dr = target.r - anchor.r

                moved = new.translate(dq, dr)

                # overlap check
                if not super_map.is_disjoint(moved):
                    continue

                # touching check: guaranteed in most cases, but keep it strict
                if not super_map.touches(moved):
                    continue

                super_map.update(moved)
                placed = True
                break

            if not placed:
                raise RuntimeError(
                    f"Failed to place a connected snowflake without overlap after {max_tries} attempts. "
                    "Try increasing max_tries."
                )

        return super_map

class ConcentricHexflowerOfHexflowersBuilder:
    """
    Builds a symmetric 'hexflower of hexflowers' by placing snowflake-centers on a meta-hexflower.

    - meta_radius = number of concentric rings of snowflakes (1 -> 7, 2 -> 19, 3 -> 37 ...)
    - snowflake_radius = radius of each snowflake (2 -> 19 hexes)

    Spacing S = 2*snowflake_radius + 1 ensures:
      - no overlap between snowflake disks
      - edge-adjacent touching between neighboring snowflakes
    """

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def build(self, meta_radius: int, snowflake_radius: int) -> HexGrid:
        if meta_radius < 0:
            raise ValueError("meta_radius must be >= 0")
        if snowflake_radius < 0:
            raise ValueError("snowflake_radius must be >= 0")

        # Overlapping spacing to remove visible gaps and create stitched edges
        spacing = 2 * snowflake_radius  # for R=2 => 4

        gen = SnowflakeHexflowerGenerator(self.rng)
        out = HexGrid()

        meta_center = Hex(0, 0)
        meta_positions = HexTraversal.spiral(meta_center, meta_radius)

        for mh in meta_positions:
            center = Hex(mh.q * spacing, mh.r * spacing)
            snowflake = gen.generate(center=center, radius=snowflake_radius)

            # Merge policy: FIRST WINS (do not overwrite existing cells)
            for h, v in snowflake.items():
                if out.get(h) is None:
                    out.set(h, v)

        return out

