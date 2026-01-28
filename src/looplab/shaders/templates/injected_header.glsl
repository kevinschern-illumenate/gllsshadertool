// LoopLab Injected Header
// This header is automatically prepended to all shaders

#version 330 core

// Standard uniforms provided by LoopLab
uniform vec2 u_resolution;   // Viewport resolution in pixels
uniform float u_time;        // Time in seconds (for debugging, not loop-safe)
uniform float u_phase;       // Loop phase: 0.0 to 2*PI (use this for loops!)
uniform int u_frame;         // Current frame index
uniform float u_duration;    // Loop duration in seconds (default: 30.0)
uniform float u_seed;        // Random seed for reproducibility
uniform vec2 u_loop;         // vec2(cos(u_phase), sin(u_phase))
uniform vec2 u_jitter;       // Subpixel jitter for accumulation AA (in pixels)

// Output color
out vec4 fragColor;

// Constants
#define PI 3.14159265359
#define TAU 6.28318530718
