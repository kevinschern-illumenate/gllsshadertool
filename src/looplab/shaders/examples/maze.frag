
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

const float PI = 3.14159265359;
mat2 z=mat2(1,1,1,-1);
float m(vec2 p)
{    
    return step(cos(PI/2.5*(texture(iChannel0, floor(z*p*.1)/64.,-32.).r>.5?p.y:p.x)),.17);
}
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
      vec2 p = (fragCoord.xy / iResolution.xy-0.5)*35.0;
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }
    p += 2.0*sin(LOOP_TIME)*vec2(1.8,1.08);
    p *= z;
    vec2 c = floor(p);

    float s = step(1. - p.x + c.x, p.y - c.y), f = m(c), g = m(c + vec2(-1, 0) + s);s/=4.;
    fragColor.rgb = mix(vec3(0.),vec3(1),m(c-z[1])+(g < f ? f*(.75-s) : g*(.5+s)));
}