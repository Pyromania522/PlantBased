"""Original MIT vector drawings; no downloaded art, fonts or raster images."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "frontend/public/illustrations"
STROKE = (
    'fill="none" stroke="#416b4c" stroke-width="3" '
    'stroke-linecap="round" stroke-linejoin="round"'
)


def path(d: str, color: str) -> str:
    return f'<path d="{d}" fill="{color}"/>'


def stem(d: str) -> str:
    return f'<path d="{d}" {STROKE}/>'


def leaf(
    x: int, y: int, angle: int = 0, scale: float = 1, color: str = "#52805b"
) -> str:
    return (
        f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})">'
        + path("M0 0C-20-7-26-27-15-44C3-45 13-17 0 0Z", color)
        + stem("M0-1-12-33")
        + "</g>"
    )


def fern() -> str:
    fronds = []
    for dx, color in [(-15, "#729559"), (15, "#8ba663"), (0, "#4e7c54")]:
        fronds.append(stem(f"M72 111Q{72 + dx} 69 {72 + dx * 2} {35 + abs(dx) // 2}"))
        side = -1 if dx <= 0 else 1
        for j in range(2, 7):
            fronds.append(
                path(
                    f"M{72 + dx * j / 7:.1f} {105 - j * 9}"
                    f"q{side * 18} -4 {side * 15} -17q{-side * 14} 0 {-side * 15} 17Z",
                    color,
                )
            )
    return "".join(fronds)


POT = (
    path("M42 111h60l-7 31H49Z", "#c58460")
    + path("M39 108h66v9H39Z", "#dcaa85")
    + '<path d="M50 119h8l4 23H55Z" fill="#f1c6a3" opacity=".45"/>'
)
DRAWINGS = {
    "generic": stem("M72 110V49")
    + leaf(71, 78, -40)
    + leaf(73, 96, 50, 0.9, "#75965e")
    + leaf(73, 54, 35, 0.8),
    "ficus": stem("M71 111 75 37")
    + "".join(
        leaf(x, y, angle, 0.8, color)
        for x, y, angle, color in [
            (73, 96, -50, "#3e6d51"),
            (74, 81, 48, "#8fa761"),
            (74, 65, -48, "#4d7953"),
            (75, 49, 35, "#668957"),
        ]
    ),
    "pothos": stem("M71 110C49 86 42 57 57 38M73 108c6-25 27-34 29-60")
    + "".join(
        path(f"M{x} {y}c-18-24-35 0-4 18c27-10 22-32 4-18Z", color)
        for x, y, color in [
            (54, 41, "#7f9a53"),
            (50, 66, "#527c53"),
            (64, 87, "#8fa761"),
            (96, 57, "#5b8258"),
        ]
    ),
    "snake_plant": path("M66 111C49 69 51 35 60 15c11 29 15 57 16 96Z", "#456d51")
    + path("M76 111C73 69 83 39 94 27c4 35-2 61-8 84Z", "#75945e")
    + path("M53 111C39 84 35 62 41 47c12 13 19 35 20 64Z", "#8ba467")
    + '<path d="m60 29 9 81M91 41l-9 69M42 59l12 51" '
    'stroke="#c1cc7e" stroke-width="3" fill="none"/>',
    "succulent": "".join(
        f'<ellipse cx="72" cy="83" rx="13" ry="36" '
        f'transform="rotate({angle} 72 96)" fill="{color}"/>'
        for angle, color in [
            (-68, "#8da58b"),
            (68, "#7d9b86"),
            (-38, "#a9ba93"),
            (38, "#94ad91"),
            (0, "#648c76"),
        ]
    )
    + '<ellipse cx="72" cy="95" rx="10" ry="21" fill="#b8c9a2"/>',
    "cactus": path("M58 111V47a14 14 0 0 1 28 0v64Z", "#618964")
    + path(
        "M58 84H47a9 9 0 0 1-9-9V60a6 6 0 0 1 12 0v12h8"
        "M86 72h8V54a6 6 0 0 1 12 0v23a9 9 0 0 1-9 9H86",
        "#7c9b6d",
    )
    + '<path d="M68 44v59M77 44v59" stroke="#b6c391" stroke-width="2"/>'
    '<path d="m63 56-4-2m24 7 4-2m-24 18-4-2m24 13 4-2" '
    'stroke="#e9dfbb" stroke-width="2"/>',
    "fern": fern(),
    "orchid": stem("M73 111C62 83 75 50 98 29")
    + leaf(70, 112, -72, 0.9, "#547b58")
    + leaf(72, 111, 75, 1, "#72936c")
    + "".join(
        f'<g transform="translate({x} {y})">'
        '<ellipse rx="8" ry="14" fill="#e1c2ce"/>'
        '<ellipse rx="15" ry="7" fill="#ecced8"/>'
        '<path d="M-6 2Q0-5 6 2L0 10Z" fill="#b47092"/>'
        '<circle r="2.5" fill="#ecd299"/></g>'
        for x, y in [(98, 31), (84, 50), (77, 72)]
    ),
    "herb": "".join(
        stem(f"M72 111Q{x} 80 {x} {y}")
        + leaf(x, y + 10, -30, 0.65, color)
        + leaf(x, y + 24, 55, 0.62, color)
        for x, y, color in [
            (48, 57, "#8eaa63"),
            (74, 39, "#5b8a56"),
            (96, 67, "#749b5d"),
        ]
    ),
    "palm": stem("M70 112q-4-38 3-65")
    + "".join(
        path(f"M73 48Q{x} {y} {tx} {ty}Q{x} {y + 17} 73 48Z", color)
        for x, y, tx, ty, color in [
            (43, 16, 20, 64, "#4e7d54"),
            (31, 39, 18, 93, "#79985a"),
            (58, 9, 67, 19, "#76985e"),
            (91, 14, 123, 51, "#537e52"),
            (112, 30, 133, 83, "#8ca766"),
            (103, 50, 111, 106, "#668d5a"),
        ]
    ),
    "hanging_plant": '<path d="M37 97 72 14l35 83" fill="none" '
    'stroke="#be9b7b" stroke-width="2"/>'
    '<path d="M48 103q-10 5-6 22t-2 24M91 103q17 8 13 25t4 23" '
    'fill="none" stroke="#668451" stroke-width="3"/>'
    + leaf(55, 103, -48, 0.8, "#7f9e5f")
    + leaf(75, 102, 20, 1, "#527c56")
    + leaf(92, 104, 60, 0.7, "#91a86a")
    + path("M40 130q-19-12-20 4q10 15 20-4M103 135q19-13 20 1q-9 14-20-1", "#6f9259"),
    "monstera": stem("M69 111Q65 78 51 52M72 110Q81 74 96 48")
    + path("M56 66C16 55 18 17 43 20c21-14 43 18 13 46Z", "#4d7959")
    + path("M91 77c-34-18-24-52-2-51 25-7 42 28 2 51Z", "#709262")
    + '<path d="m51 58-10-24m51 35 4-30" stroke="#a5ba81" stroke-width="2"/>'
    '<path d="m28 30 14 10m-17 4 16 7m27-20-9 10m58 1-12 5m10 7-14 4" '
    'stroke="#f4f2e5" stroke-width="5" stroke-linecap="round"/>',
}


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, drawing in DRAWINGS.items():
        # Fixed viewBox, no CSS/fonts/scripts/external references.
        shadow = (
            '<ellipse cx="72" cy="148" rx="39" ry="5" fill="#647b60" opacity=".09"/>'
        )
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="144" height="160" '
            f'viewBox="0 0 144 160"><title>{name.replace("_", " ").title()}</title>'
            f"{shadow}{drawing}{POT}</svg>\n"
        )
        (ROOT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote {len(DRAWINGS)} original SVG illustrations")


if __name__ == "__main__":
    main()
