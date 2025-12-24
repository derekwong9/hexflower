# Hexflower Snowflake Generator

A procedural map generator written in Python that implements the **hexflower snowflake method**.  
It generates symmetric, concentric **hexflowers-of-hexflowers** with deterministic seeding, biome transition tables, and SVG/JSON export, designed for tabletop RPGs and worldbuilding.

---

## What this project does

This tool generates hex maps using a two-level approach:

### 1. Snowflake hexflowers
A single hexflower is generated ring-by-ring from a center hex using biome transition tables.  
For example, a radius of `2` produces a 19-hex snowflake.

### 2. Concentric hexflowers-of-hexflowers
Multiple snowflakes are placed on a higher-level hex grid, forming symmetric concentric rings  
(center + 6, then + 12, + 18, etc.). Snowflakes are intentionally overlapped and merged so that
they **share edges visually**, eliminating gaps.

The result is a clean, scalable, second-order hexflower structure suitable for:
- TTRPG regional maps
- Procedural worldbuilding
- Terrain prototyping
- Visual experimentation

---

## Key features

- Deterministic generation via RNG seeds
- Snowflake hexflower algorithm (ring-based growth)
- Concentric, symmetric meta-layouts
- Biome transition tables
- SVG export for visualization
- JSON export for further processing
- Modular, object-oriented design

---

## Requirements

- Python **3.10+**
- Standard library only (no external dependencies)

### Optional: Conda environment
```bash
conda create -n hexflower python=3.10
conda activate hexflower
````

---

## Project structure

```
.
├── cli.py
├── hexflower/
│   ├── __init__.py
│   ├── hex.py              # Axial hex coordinates and math
│   ├── grid.py             # Sparse hex grid container
│   ├── traversal.py        # Ring / spiral traversal
│   ├── tables.py           # Biome transition tables
│   ├── generators.py       # Snowflake + meta builders
│   └── render_svg.py       # SVG rendering
```

---

## How the algorithm works (high level)

### Snowflake generation

* Always starts from a center hex
* Expands outward ring by ring
* Each new hex selects an inward neighbor as its biome reference
* Biomes evolve using table-driven rules

### Meta generation (hexflower-of-hexflowers)

* Snowflake centers are placed on a larger hex spiral
* Spacing causes intentional overlap between neighboring snowflakes
* Overlapping hexes are merged using a first-write-wins policy
* This produces stitched edges and no visible gaps

---

## CLI usage

All interaction is done via `cli.py`.

### Generate a single snowflake (19 hexes)

```bash
python cli.py --seed 7 --radius 2 --svg snowflake.svg --json snowflake.json
```

---

### Generate a symmetric 7-flower ring (center + 6)

```bash
python cli.py --seed 123 --radius 2 --meta-radius 1 --svg ring7.svg --json ring7.json
```

This generates one full concentric meta ring.

---

### Generate larger concentric maps

**19 snowflakes (two meta rings):**

```bash
python cli.py --seed 123 --radius 2 --meta-radius 2 --svg ring19.svg
```

**37 snowflakes:**

```bash
python cli.py --seed 123 --radius 2 --meta-radius 3 --svg ring37.svg
```

---

## Optional CLI flags

* `--hex-size <float>`
  Control hex size in SVG output (default: 38)

* `--no-coords`
  Hide axial coordinates in SVG

* `--no-labels`
  Hide biome labels in SVG

* `--title "Custom Title"`
  Override SVG title text

Example:

```bash
python cli.py --seed 42 --radius 2 --meta-radius 1 --svg clean.svg --no-coords
```

---

## Output formats

### SVG

* Pointy-top axial hex layout
* Full biome names rendered in each hex
* Suitable for printing or digital maps

### JSON

Each hex is exported as:

```json
{
  "q": 0,
  "r": -1,
  "value": "forest"
}
```

Useful for:

* Importing into other tools
* Game logic
* Additional procedural passes

---

## Design philosophy

* Geometry first, aesthetics second
* Deterministic and reproducible
* Clear separation between generation, layout, and rendering
* Easy to extend with additional layers (roads, rivers, settlements)

---