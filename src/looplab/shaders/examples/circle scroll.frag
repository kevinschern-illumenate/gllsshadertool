
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// https://www.shadertoy.com/view/ldycR3

float scale(float value, float min, float max, float toMin, float toMax)
{
    return (value - min) / (max - min) * (toMax - toMin) + toMin;
}


void mainImage( out vec4 fragColor, in vec2 fragCoord )
{   
    vec2 p = fragCoord.xy / iResolution.xy-0.5;
    p *= 6.0;
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }

    float r = length(p)*1.8;
    
    
    
    r = r*2.-.0;
    float color = 1.0;

    float ringTime = scale(iNbItems+0.0, 1., 64., 10., 0.4 );
    float s = mod(LOOP_TIME*2.0-r, ringTime)/(ringTime);
    
    float sizeHalf = scale(iForce, 1.0, 10.0, 0.05, 0.9) / 2.0;
    float fade = scale(iForce2, 1.0, 10.0, 1., .0);
    
    float start = 0.5 - sizeHalf;
    float end = 0.5 + sizeHalf;    
    
    s = s >= start && s <= end ? 1.-2.*abs(scale(s, start, end, 0., 1.)-0.5) : -1.;    
    s = s>0. && (s < fade) ? s / fade  : (s > 0. ? 1.0 : 0.);    

    fragColor = vec4(vec3(s), 1.);
}