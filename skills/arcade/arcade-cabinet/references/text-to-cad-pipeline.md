# Text-to-CAD Pipeline for Arcade Lobby Assets

## Overview

Generate 3D models (GLB format) for the arcade lobby from plain-language descriptions, using `earthtojake/text-to-cad` (10.6k ⭐, MIT).

**Pipeline:** Write build123d Python → `scripts/step source.py --glb output.glb` → load into Three.js arcade scene

## Setup

```bash
# Clone
git clone https://github.com/earthtojake/text-to-cad.git /root/text-to-cad

# Python 3.12+ required
python3.12 -m venv /root/text-to-cad/.venv
source /root/text-to-cad/.venv/bin/activate
pip install -e /root/text-to-cad/skills/cad/scripts/packages/cadpy
```

## Writing a Generator Script

Create a Python file with a `gen_step()` function returning a `build123d.Shape`:

```python
"""Description of the model."""
from build123d import *

def gen_step():
    body = Box(width, depth, height)
    # Add/subtract features
    cutout = Box(w, d, h)
    cutout = Pos(x, y, z) * cutout
    body -= cutout
    # Add details
    detail = Box(w, d, h)
    detail = Pos(x, y, z) * detail
    result = body + detail
    return result
```

## Generating GLB

```bash
source /root/text-to-cad/.venv/bin/activate
cd /tmp  # or any writable directory
python3 /root/text-to-cad/skills/cad/scripts/step \
  /path/to/source.py \
  --glb output-file.glb \
  --verbose
```

The `--glb` path must be relative (not absolute). Output files use the source filename as basename.

## Generated Models (this session)

| Model | GLB Size | Description |
|-------|----------|-------------|
| Arcade cabinet | 4.2 KB | Body, monitor bezel, control panel, coin door, marquee |
| Arcade stairs | 17 KB | 5 steps, glass railings, neon top rail |

## Best Practices

- Use millimeters as units
- Base plane: XY, up axis: +Z
- Keep models simple — complex geometry = slow rendering in browser
- Export as GLB (native Y-up, direct import into Three.js)
- Reuse STEP as the canonical source; GLB is the browser format

## Limitations

- Python 3.12+ required
- Geometry is parametric/CSG (boxes, cylinders, extrusions) — not organic shapes
- Build time: ~2s per model for simple geometry
- No texturing in the pipeline (models are untextured meshes)
