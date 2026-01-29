
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

/* ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * Nimda@zl wrote this file.  As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return.
 * ----------------------------------------------------------------------------
 */

precision highp float;

uniform float time;
uniform vec2 touch;
uniform vec2 resolution;

float rand(vec2 co)
{
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float GetLocation(vec2 s, float d)
{
    vec2 f = s*d;

    //s = mix(vec2(0), floor(s*d),step(0.5, f));

    // tris
    f = mod(f, 8.); // because i failed somewhere
    
    f = f + vec2(0,0.5)*floor(f).x;
    s = fract(f);
    f = floor(f);

    d = s.y - 0.5;
    float l = abs(d) + 0.5 * s.x;
    float ff = f.x+f.y;
    f = mix(f, f+sign(d)*vec2(0,0.5), step(0.5, l));
    l = mix(ff, ff+sign(d)*0.5, step(0.5, l));

    return l * rand(vec2(f));
}

vec3 hsv2rgb(float h, float s, float v)
{    
    vec3 c = smoothstep(2./6., 1./6., abs(fract(h) -vec3(0.5,2./6.,4./6.)));
    c.r = 1.-c.r;
    return (s + (1.-s)*c) * v;
}

vec3 getRandomColor(float f, float t)
{
    return hsv2rgb(f+t, 0.2+cos(sin(f))*0.3, 0.9);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    
    float t = LOOP_TIME*1.0;
    vec2 s = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        s.x *= iResolution.x/iResolution.y;
    }
    else
    {
        s.y *= iResolution.y/iResolution.x;
    }


    float f[3];
    f[0] = GetLocation(s, 12.);
    f[1] = GetLocation(s, 6.);
    f[2] = GetLocation(s, 3.);

    vec3 color = getRandomColor(f[1] *0.05 + 0.01*f[0] + 0.9*f[2], t);

    fragColor = vec4(color, 1.);
}