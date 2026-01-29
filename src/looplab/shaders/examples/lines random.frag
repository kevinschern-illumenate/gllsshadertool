
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define TIMESCALE 0.025 
#define TILES iNbItems
#define COLOR 1.0,1.0,1.0


float snoise(vec3 uv, float res)
{
    const vec3 s = vec3(1e0, 1e2, 1e3);
    
    uv *= res;
    
    vec3 uv0 = floor(mod(uv, res))*s;
    vec3 uv1 = floor(mod(uv+vec3(1.), res))*s;
    
    vec3 f = fract(uv); f = f*f*(3.0-2.0*f);

    vec4 v = vec4(uv0.x+uv0.y+uv0.z, uv1.x+uv0.y+uv0.z,
                  uv0.x+uv1.y+uv0.z, uv1.x+uv1.y+uv0.z);

    vec4 r = fract(sin(v*1e-1)*1e3);
    float r0 = mix(mix(r.x, r.y, f.x), mix(r.z, r.w, f.x), f.y);
    
    r = fract(sin((v + uv1.z - uv0.z)*1e-1)*1e3);
    float r1 = mix(mix(r.x, r.y, f.x), mix(r.z, r.w, f.x), f.y);
    
    return mix(r0, r1, f.z)*2.-1.;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy / iResolution.xy;
    //uv.x *= iResolution.x / iResolution.y;
    uv.y = uv.x;
    float time = LOOP_TIME*1.0+9.;
    
    float noise = snoise(vec3(floor(uv * float(TILES)) / float(TILES), 0.5)+ vec3(0.,-time*.05, time*.01), 38.);

    float odds = iForce2 / 10. * 0.6 + 0.7;
    float p = odds - mod(noise + time * float(TIMESCALE), 1.0);
    p = min(max(p * 3.0 - 1.8, 0.), 2.0);
    
    float force = pow(iForce / 5.5, 3.0);
    fragColor = vec4(COLOR, 1.0) * p * force;
}