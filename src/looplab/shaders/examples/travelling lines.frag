
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

float hash(in vec2 st) {
    return fract(sin(dot(st, vec2(12.9898, 4.1414))) * 43758.5453);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    

    vec2 uv = fragCoord.xy / iResolution.xy;    

    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }

    vec2 p = uv * 10.0;

    float count1 = (iNbItems + 0.0) / 10.0;
    float count2 = (iNbItems2 + 0.0) / 10.0;
    p.x *= count1;
    p.y *= count2;

    vec2 fp = floor(p);

    // random line direction
    float dir = -1.0 + hash(fp) + 0.5;
    float t = LOOP_TIME * hash(fp) * 5.0;
     
    vec2 m = vec2(
        t + hash(fp),
        0
    );
    vec2 ip = floor(p + m * dir);
    
    float c = hash(ip);
    float force = (1.0-pow(iForce / 10.0, 2.0)) / 1.3 + 0.2;
    c = step(force, c);
    vec3 col =  vec3(c);
    
    float a = 1.0;
    
    a = 0.000;

    // Output to screen
    fragColor = vec4(col + a, 1.0);
}
