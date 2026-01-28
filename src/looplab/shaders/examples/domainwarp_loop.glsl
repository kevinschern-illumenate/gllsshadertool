// Domain Warp Loop - Warped noise patterns with perfect loop
// @param scale float 1.0 10.0 3.0
// @param warp_strength float 0.0 2.0 1.0
// @param speed float 0.5 3.0 1.0

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Normalized coordinates
    vec2 uv = fragCoord / u_resolution.xy;
    vec2 p = (uv - 0.5) * 2.0;
    p.x *= u_resolution.x / u_resolution.y;
    
    // Use phase for loop-safe animation
    float t = u_phase;
    
    // Looping offset using sin/cos
    vec2 loopOffset = u_loop * 0.5;
    
    // Scale the coordinates
    p *= 3.0;
    
    // Domain warping layers
    vec2 q = vec2(
        fbm(p + loopOffset, u_seed, 4),
        fbm(p + vec2(5.2, 1.3) + loopOffset, u_seed + 1.0, 4)
    );
    
    vec2 r = vec2(
        fbm(p + 4.0 * q + vec2(1.7, 9.2) + loopOffset * 0.5, u_seed + 2.0, 4),
        fbm(p + 4.0 * q + vec2(8.3, 2.8) + loopOffset * 0.5, u_seed + 3.0, 4)
    );
    
    float f = fbm(p + 4.0 * r, u_seed + 4.0, 4);
    
    // Color based on warped value
    vec3 col = vec3(0.0);
    col = mix(vec3(0.1, 0.2, 0.4), vec3(0.8, 0.5, 0.2), clamp(f * f * 4.0, 0.0, 1.0));
    col = mix(col, vec3(0.0, 0.0, 0.2), clamp(length(q), 0.0, 1.0));
    col = mix(col, vec3(0.9, 0.6, 0.3), clamp(length(r.x), 0.0, 1.0));
    
    // Add some glow
    col += 0.2 * vec3(f * f * f);
    
    fragColor = vec4(col, 1.0);
}
