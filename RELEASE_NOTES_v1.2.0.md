# v1.2.0 - Interactive WebGL preview and CLI customisation

## Added

- **Interactive browser preview** (`docs/interactive.html`)
  - Real-time Three.js point cloud rendered with custom GLSL shaders
  - Procedural FBM noise displacement matches the Blender Geometry Nodes setup
  - Blue-to-magenta gradient matches the Blender emission material
  - UnrealBloom post-processing for the characteristic glow
  - Orbit controls: drag to rotate, scroll to zoom
  - Linked from the main `docs/index.html` animation preview

- **CLI colour and noise customisation** (`make_point_cloud_blob.py`)
  - `--color1 <hex>` — gradient start colour (default `#e666ff`)
  - `--color2 <hex>` — gradient end colour (default `#38bdff`)
  - `--noise-scale <float>` — displacement noise scale multiplier (default `1.0`)
  - Argument parsing migrated to Python `argparse` for robustness

## Example

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" `
  -b --python ".\make_point_cloud_blob.py" `
  -- --color1 "#ff4400" --color2 "#ffee00" --noise-scale 2.0 `
  --render ".\render\custom.png"
```
