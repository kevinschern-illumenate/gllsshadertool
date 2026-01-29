// Geometric Loop - Rotating geometric patterns with perfect loop

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Normalized coordinates centered at origin
    vec2 uv = fragCoord / u_resolution.xy;
    vec2 p = (uv - 0.5) * 2.0;
    p.x *= u_resolution.x / u_resolution.y;
    
    // Use phase for loop-safe animation
    float t = u_phase;
    
    // Accumulate color from multiple layers
    vec3 col = vec3(0.0);
    float intensity = 0.0;
    
    int numLayers = 5;
    for (int i = 0; i < numLayers; i++) {
        float fi = float(i);
        
        // Rotate each layer differently (integer frequencies for perfect loop)
        float angle = t * (fi + 1.0);
        mat2 rot = loopRotation(angle);
        vec2 q = rot * p;
        
        // Scale each layer
        q *= 1.0 + fi * 0.3;
        
        // Create geometric pattern (octagon approximation)
        float d = max(abs(q.x), abs(q.y));
        d = max(d, (abs(q.x) + abs(q.y)) * 0.707);
        
        // Ring pattern
        float ring = abs(d - 0.5 - fi * 0.15);
        ring = smoothstep(0.05, 0.0, ring);
        
        // Color per layer - use TAU/3 for 120 degree hue shifts
        vec3 layerCol = vec3(
            0.5 + 0.5 * loopSin(t + fi),
            0.5 + 0.5 * loopSin(t + fi + TAU / 3.0),
            0.5 + 0.5 * loopSin(t + fi + 2.0 * TAU / 3.0)
        );
        
        col += ring * layerCol / float(numLayers);
        intensity += ring;
    }
    
    // Add glow
    col += intensity * 0.1;
    
    // Background gradient
    vec3 bg = vec3(0.02, 0.03, 0.08);
    col = max(col, bg);
    
    fragColor = vec4(col, 1.0);
}
