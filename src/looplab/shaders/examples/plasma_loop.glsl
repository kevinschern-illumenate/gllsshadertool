// Plasma Loop - Classic plasma effect with perfect loop
// @param speed float 0.1 5.0 1.0
// @param complexity float 1.0 10.0 4.0
// @param color_shift float 0.0 1.0 0.0

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Normalized coordinates
    vec2 uv = fragCoord / u_resolution.xy;
    vec2 p = (uv - 0.5) * 2.0;
    p.x *= u_resolution.x / u_resolution.y;
    
    // Use phase for loop-safe animation
    float t = u_phase;
    
    // Plasma formula using loop-safe functions
    float v = 0.0;
    
    // Layer 1: Horizontal waves
    v += loopSin(p.x * 5.0 + t);
    
    // Layer 2: Vertical waves  
    v += loopSin((p.y * 5.0 + t) * 0.5);
    
    // Layer 3: Diagonal waves
    v += loopSin((p.x + p.y) * 5.0 + t * 0.7);
    
    // Layer 4: Radial waves
    float cx = p.x + loopSin(t * 0.3);
    float cy = p.y + loopCos(t * 0.4);
    v += loopSin(sqrt(cx * cx + cy * cy) * 5.0);
    
    // Normalize
    v = v * 0.25 + 0.5;
    
    // Color palette (loop-safe)
    vec3 col;
    col.r = sin(v * PI + t) * 0.5 + 0.5;
    col.g = sin(v * PI + t + 2.094) * 0.5 + 0.5; // +2π/3
    col.b = sin(v * PI + t + 4.188) * 0.5 + 0.5; // +4π/3
    
    fragColor = vec4(col, 1.0);
}
