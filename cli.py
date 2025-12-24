from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from hexflower.generators import (
    ConnectedHexflowerBuilder,
    SnowflakeHexflowerGenerator,
    ConcentricHexflowerOfHexflowersBuilder,
)

from hexflower.render_svg import PointyTopLayout, SVGRenderer
from hexflower.hex import Hex


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate hexflower snowflakes and export to SVG/JSON.")
    ap.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility.")
    ap.add_argument("--radius", type=int, default=2, help="Snowflake radius (2 => 19 hexes).")
    ap.add_argument("--count", type=int, default=1, help="Number of snowflakes to connect in a chain.")
    ap.add_argument("--json", type=str, default="", help="Write JSON output to this path (optional).")
    ap.add_argument("--svg", type=str, default="", help="Write SVG output to this path (optional).")
    ap.add_argument("--hex-size", type=float, default=38.0, help="Hex radius in pixels for SVG.")
    ap.add_argument("--no-coords", action="store_true", help="Do not render coordinate labels in SVG.")
    ap.add_argument("--no-labels", action="store_true", help="Do not render biome labels in SVG.")
    ap.add_argument("--title", type=str, default="", help="SVG title (optional).")
    ap.add_argument(
        "--meta-radius",
        type=int,
        default=None,
        help="Number of concentric rings of snowflakes (1->7, 2->19, 3->37 ...). If set, overrides --count.",
    )

    return ap.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    # Generation
    if getattr(args, "meta_radius", None) is not None:
        # Symmetric concentric "hexflower of hexflowers"
        builder = ConcentricHexflowerOfHexflowersBuilder(rng)
        grid = builder.build(meta_radius=args.meta_radius, snowflake_radius=args.radius)
    elif args.count == 1:
        # Single snowflake
        gen = SnowflakeHexflowerGenerator(rng)
        grid = gen.generate(center=Hex(0, 0), radius=args.radius)
    else:
        # Organic connected placement (fallback)
        builder = ConnectedHexflowerBuilder(rng)
        grid = builder.build_chain(count=args.count, radius=args.radius)

    # JSON output
    if args.json:
        payload = grid.to_jsonable_list()
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # SVG output
    if args.svg:
        layout = PointyTopLayout(size=args.hex_size)
        renderer = SVGRenderer(layout=layout)

        if getattr(args, "meta_radius", None) is not None:
            title = args.title or (
                f"Hexflower-of-Hexflowers (snowflake_radius={args.radius}, "
                f"meta_radius={args.meta_radius}, seed={args.seed})"
            )
        else:
            title = args.title or f"Hexflower (radius={args.radius}, seed={args.seed}, count={args.count})"

        renderer.write_svg(
            grid=grid,
            path=Path(args.svg),
            title=title,
            show_coords=not args.no_coords,
            show_biome_label=not args.no_labels,
        )

    # Default: print JSON to stdout
    if not args.json and not args.svg:
        print(json.dumps(grid.to_jsonable_list(), indent=2))


if __name__ == "__main__":
    main()
