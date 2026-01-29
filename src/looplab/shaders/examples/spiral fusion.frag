
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define PI 3.14159265359


vec2 rotate2D (vec2 _st, float _angle) {
    _st =  mat2(cos(_angle),-sin(_angle),
                sin(_angle),cos(_angle)) * _st;
    return _st;
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
    p *= 4.0;

    float power = pow(iForce/5.5, 3.);
    vec3 color = vec3(1.);
    float r = length(p)*1.;
    float w = 1.5;
    float time = LOOP_TIME*2.0;
    float t = sin(r*3.0+time*PI*.35)*2.5/power;
    p *= t;
    p = rotate2D(p,(r*PI*0.8*iComplexity-time*.6));
    color *= smoothstep(-w,.0,p.x)*smoothstep(w,.0,p.x);
    color *= distance(vec2(0.), vec2(cos(r*4.3+time*PI*0.25)));
    fragColor = vec4(color, 1.);
}