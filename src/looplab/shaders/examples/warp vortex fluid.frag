
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

 
 

#define M_PI 3.141592

// tweaked version of this by 'bmodone' - https://www.shadertoy.com/view/4llcDH
// updated a bit since fabrice kindly commented :)

float radial(vec2 uv, float offset, float repeat)
{
    float a = mod((atan(uv.y, uv.x) + M_PI + (offset * 2.0 * M_PI)) * repeat / M_PI, 2.0);
    return min(a, 2.0 - a);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    
    vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*1.5;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
       
    float _d = length(uv); 
    float d = _d - 0.75;
    float off = _d;
    float a = radial(uv, sin(off*2.*iForce-LOOP_TIME)*0.161, (2.*(iComplexity-1.))+1.) - 0.2;

    d = off - d*d+d+a*a+d;
    float m = _d+d+off;
    
    vec3 col = mix(vec3(0.1, 0.1, 0.1), vec3(0.18, 0.18, 0.18), m);
    col = (col-off*off)+d+a;
    
    vec3 backg = vec3(0.);
    
    float m2 = col.r+col.g+col.b;
    col = mix(backg,col,m2);
    col *= _d-0.01;
    
    fragColor = vec4(1.-col,1.0);
}
