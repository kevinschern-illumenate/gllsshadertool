
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

vec2 position(float z) {
    return vec2(
        0.0 + sin(z * 0.1) * 1.0 + sin(cos(z * 0.031) * 4.0) * 1.0 + sin(sin(z * 0.0091) * 3.0) * 3.0,
        0.0 + cos(z * 0.1) * 1.0 + cos(cos(z * 0.031) * 4.0) * 1.0 + cos(sin(z * 0.0091) * 3.0) * 3.0
    ) * 1.0;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 p = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }
    p *= 2.8;
    float time = LOOP_TIME*1.0 + 20.;
    float camZ = 25.0*time;
    vec2 cam = position(camZ);

    float dt = 0.5;
    float camZ2 = 25.0 * (time + dt);
    vec2 cam2 = position(camZ2);
    vec2 dcamdt = (cam2 - cam) / dt;
    float power = pow(iForce/5.5, 1.8);
    float nbIters = pow(0.+iComplexity, 2.)+1.;
    vec3 f = vec3(0.0);
    for(int j = 1; j < nbIters; j++) {
        float i = float(j);
        float realZ = floor(camZ) + i;
        float screenZ = realZ - camZ;
        float r = 1.0 / screenZ;
        vec2 c = (position(realZ) - cam) * 10.0 / screenZ - dcamdt * 0.4;

        vec3 color = mColorMode == 1 ? vec3(1.0/max(1.,screenZ)) : (vec3(sin(realZ * 0.07), sin(realZ * 0.1), sin(realZ * 0.08)) + vec3(1.0)) / 2.0;

        f += color * 0.05 * power / screenZ / (abs(length(p - c) - r) + 0.01);
    }

    fragColor = vec4(f, 1.0);
}