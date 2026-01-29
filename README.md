# LoopLab

**AI-assisted GLSL loop shader → preview → offline render → FFmpeg encode.**

## Core Features

- Generate/run **GLSL fragment shaders** that are **mathematically guaranteed** to loop perfectly over **30.0 seconds**
- **Real-time preview** in-app (lower quality/res)
- **Offline deterministic renderer** (highest quality) exporting image sequence + encoded video

## Loop Guarantee

All motion in shaders is based on `u_phase` (0 to 2π), ensuring perfect loops:

- Duration: D = 30.0 seconds (default)
- For frame index `f`: `t = f / fps`, `phase = 2π * (t / D)`
- Uniforms provided: `u_time`, `u_phase`, `u_loop` (cos/sin pair)

## Installation

```bash
# Install with pip
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Requirements

- Python 3.10+
- PySide6
- PyOpenGL
- NumPy
- Pillow
- FFmpeg (for video encoding, user must install separately)

## Usage

```bash
# Run the application
looplab

# Or run directly
python -m looplab.main
```

## Shader Interface

### Required Uniforms

```glsl
uniform vec2 u_resolution;   // Viewport resolution
uniform float u_time;        // Seconds (non-looped, for debugging)
uniform float u_phase;       // 0..2π (loop-safe)
uniform int u_frame;         // Current frame index
uniform float u_duration;    // 30.0 seconds
uniform float u_seed;        // Stable randomness seed
uniform vec2 u_loop;         // vec2(cos(u_phase), sin(u_phase))
uniform vec2 u_jitter;       // Subpixel jitter for accumulation AA
```

### Standard Entry Point (Shadertoy-style)

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Your shader code here
}
```

### Loop Helpers

```glsl
vec2 loopVec(float phase);  // Returns vec2(cos(phase), sin(phase))
```

## Project Structure

```
src/looplab/
  main.py               # Application entry point
  app/
    main_window.py      # Main window with dockable panels
    docks.py            # UI dock panels
    models.py           # Project data model
  gl/
    preview_widget.py   # QOpenGLWidget for preview
    gl_resources.py     # VAO/VBO/FBO management
    shader_manager.py   # Shader loading and compilation
    uniforms.py         # Uniform handling
  render/
    offline_worker.py   # Offline rendering in QThread
    timeline.py         # Timeline and frame calculations
    image_writer.py     # PNG output
  encode/
    ffmpeg.py           # FFmpeg integration
  project/
    project_io.py       # Project save/load
    schema.py           # Project schema
  shaders/
    templates/
      injected_header.glsl
      loop_helpers.glsl
    examples/
      plasma_loop.glsl
      domainwarp_loop.glsl
      geometric_loop.glsl
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=looplab
```

## License

MIT License
