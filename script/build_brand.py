"""Render the original SVG into the local HA brand directory."""

from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Build transparent, square light/dark assets at both official sizes."""
    source = (ROOT / "assets/brand/icon.svg").read_text()
    output = ROOT / "custom_components/plantbased/brand"
    output.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        svg = source
        if dark:
            for light, night in (
                ("#246844", "#9cdb94"),
                ("#38894d", "#60b569"),
                ("#5ba951", "#86cc70"),
                ("#b8603e", "#d58b68"),
                ("#cf7852", "#efaa81"),
            ):
                svg = svg.replace(light, night)
        for size, suffix in ((256, ""), (512, "@2x")):
            prefix = "dark_" if dark else ""
            cairosvg.svg2png(
                bytestring=svg.encode(),
                write_to=str(output / f"{prefix}icon{suffix}.png"),
                output_width=size,
                output_height=size,
            )


if __name__ == "__main__":
    main()
