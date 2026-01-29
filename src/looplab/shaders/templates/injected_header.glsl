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

// Shadertoy/Library compatibility uniforms
uniform vec3 iResolution;    // Viewport resolution (width, height, aspect)
uniform float iTime;         // Time in seconds
uniform float iTimeDelta;    // Time since last frame
uniform int iFrame;          // Current frame number
uniform vec4 iMouse;         // Mouse position (xy=current, zw=click)
uniform int iComplexity;     // Quality/detail level (1-10, default 5)
uniform float iForce;        // Primary intensity parameter (0-10, default 5)
uniform float iForce2;       // Secondary intensity parameter (0-10, default 5)
uniform float iBaseHueRad;   // Base hue in radians (0-6.28)
uniform int mColorMode;      // Color mode toggle (0 or 1)

// Output color
out vec4 fragColor;

// Constants
#define PI 3.14159265359
#define TAU 6.28318530718

