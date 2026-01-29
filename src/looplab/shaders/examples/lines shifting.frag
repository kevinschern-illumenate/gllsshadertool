
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

float noiseish(vec2 coord, vec2 coordMultiplier1, vec2 coordMultiplier2, vec2 coordMultiplier3, vec3 timeMultipliers) {
    return 0.333 * (sin(dot(coordMultiplier1, coord) + timeMultipliers.x * LOOP_TIME) + sin(dot(coordMultiplier2, coord) + timeMultipliers.y * LOOP_TIME) + sin(dot(coordMultiplier3, coord) + timeMultipliers.z * LOOP_TIME));
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy / iResolution.y;
    vec2 uvOffset;
    uvOffset.x = 0.;//.2 * sin(LOOP_TIME*1.0 + 0.7) *pow(abs(uv.y - 0.5), 3.1) - sin(LOOP_TIME*1.0 + 0.1);
    uvOffset.y = 0.;//-LOOP_TIME*1.0 + .05 * sin(LOOP_TIME*1.0) * pow(abs(uv.x - 0.5), 1.8);
    uv += uvOffset;
    float cellResolution = iComplexity;
    const float lineSmoothingWidth = 0.05;
    vec2 localUV = fract(uv * cellResolution);
    vec2 cellCoord = floor(uv * cellResolution);
    
    float power = pow(iForce/5.5, 3.)+0.3;
    vec2 angle = 4.9 / power * normalize(vec2(noiseish(cellCoord, vec2(1.7, 0.9), vec2(2.6, 1.1), vec2(0.0), vec3(0.55, 0.93, 0.0)), noiseish(cellCoord, vec2(0.6, 1.9), vec2(1.3, 0.3), vec2(0.0), vec3(1.25, 0.83, 0.0))));
    
    float v = smoothstep(-lineSmoothingWidth, lineSmoothingWidth, abs(fract(dot(localUV, angle) + 1.0*LOOP_TIME)-0.5) - 0.25);
    
    const float borderSmoothingWidth = 0.02;
    // apply borders
    vec2 centeredLocalUV = localUV - vec2(0.5);
    const float borderDistance = 0.45; // 0.5 = all the way to the edge of the cell
    v = max(v, max(smoothstep(-borderSmoothingWidth, borderSmoothingWidth, abs(centeredLocalUV.x) - borderDistance), smoothstep(-borderSmoothingWidth, borderSmoothingWidth, abs(centeredLocalUV.y) - borderDistance)));
    v = 1.0 - v;
    fragColor = vec4(v, v, v, 1.0);
}