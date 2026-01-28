// LoopLab Loop Helpers
// Helper functions for creating loop-safe animations

// Get loop vector from phase (cos, sin pair)
vec2 loopVec(float phase) {
    return vec2(cos(phase), sin(phase));
}

// Loop-safe sine oscillation
float loopSin(float phase) {
    return sin(phase);
}

// Loop-safe cosine oscillation
float loopCos(float phase) {
    return cos(phase);
}

// Multi-frequency loop oscillation (all frequencies must be integers for perfect loop)
float loopSinMulti(float phase, float freq) {
    return sin(phase * freq);
}

float loopCosMulti(float phase, float freq) {
    return cos(phase * freq);
}

// Smooth triangle wave (loop-safe)
float loopTriangle(float phase) {
    float t = mod(phase / TAU, 1.0);
    return 1.0 - abs(t * 2.0 - 1.0);
}

// Smooth sawtooth wave (loop-safe)
float loopSawtooth(float phase) {
    return mod(phase / TAU, 1.0);
}

// Rotation matrix from phase (for rotating patterns)
mat2 loopRotation(float phase) {
    float c = cos(phase);
    float s = sin(phase);
    return mat2(c, -s, s, c);
}

// Multi-frequency rotation
mat2 loopRotationMulti(float phase, float freq) {
    float a = phase * freq;
    float c = cos(a);
    float s = sin(a);
    return mat2(c, -s, s, c);
}

// Pseudo-random function (deterministic based on seed)
float hash(vec2 p, float seed) {
    p = fract(p * vec2(123.34, 456.21) + seed);
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

// 2D noise (deterministic)
float noise(vec2 p, float seed) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = hash(i, seed);
    float b = hash(i + vec2(1.0, 0.0), seed);
    float c = hash(i + vec2(0.0, 1.0), seed);
    float d = hash(i + vec2(1.0, 1.0), seed);
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Fractal brownian motion (deterministic)
float fbm(vec2 p, float seed, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for (int i = 0; i < octaves; i++) {
        value += amplitude * noise(p * frequency, seed + float(i) * 10.0);
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    
    return value;
}
