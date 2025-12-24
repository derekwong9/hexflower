from __future__ import annotations

import random

Biome = str


class BiomeTables:
    """
    Implements the Sandbox Generator tables:
    - Start hex biome (d10):
        1-4 Grassland
        5-6 Forest
        7-8 Hills
        9   Marsh
        10  Mountains
    - Next hex biome (d10):
        1-5 Same as previous hex
        6   Grassland
        7   Forest
        8   Hills
        9   Marsh
        10  Mountains
    """

    @staticmethod
    def start_biome(rng: random.Random) -> Biome:
        x = rng.randint(1, 10)
        if 1 <= x <= 4:
            return "grassland"
        if 5 <= x <= 6:
            return "forest"
        if 7 <= x <= 8:
            return "hills"
        if x == 9:
            return "marsh"
        return "mountains"

    @staticmethod
    def next_biome(prev: Biome, rng: random.Random) -> Biome:
        x = rng.randint(1, 10)
        if 1 <= x <= 5:
            return prev
        if x == 6:
            return "grassland"
        if x == 7:
            return "forest"
        if x == 8:
            return "hills"
        if x == 9:
            return "marsh"
        return "mountains"
