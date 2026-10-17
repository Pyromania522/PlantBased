# PlantBased brand artwork

`icon.svg` is original vector artwork created for PlantBased and licensed under
the repository's MIT license. It contains no external assets or fonts.

The square sprout is both icon and logo. The current HA brands specification
explicitly supports using icon images as logo fallbacks, so no duplicate logo
files are needed. Normal PNGs are 256×256; hDPI PNGs are 512×512. Transparent
backgrounds and light/dark variants are supplied.

Reference: [Home Assistant brands image specification](https://github.com/home-assistant/brands#image-specification).
Local `brand/` directories work in HA ≥2026.3. On older supported HA versions,
the generic integration icon is acceptable.

To regenerate the committed PNG files, from the repository root:

```sh
.venv/bin/python script/build_brand.py
```

CairoSVG is a development-only tool from requirements-dev.txt. It is never
installed by the integration and does not alter its empty runtime requirements.
