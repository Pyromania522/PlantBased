# Original plant illustrations

The twelve presets are original vector drawings authored for PlantBased under
this repository's MIT license. They use simple paths/ellipses and a common
terracotta pot. No downloaded artwork, photos, fonts or raster tracing is used.

The editable source is `script/build_illustrations.py`. Run it with Python 3.13+
to regenerate `frontend/public/illustrations/*.svg`, then run `npm run build` to
copy the drawings beside the integration's compiled module. CI checks both steps
against the committed files. Each SVG has a fixed 144 × 160 viewBox and contains
no script, external reference, embedded image or foreignObject.

Presets: generic, monstera, ficus, pothos, snake plant, succulent, cactus, fern,
orchid, herb, palm and hanging plant. The card treats images as decorative because
the plant's name is already a visible heading. A custom /local/ or HTTP(S) image
can replace its preset; a failed image falls back to the local drawing.
