
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// by Nikos Papadopoulos, 4rknova / 2016
// WTFPL

// Specular highlights contributed by Shane
#define SPECULAR

void mainImage(out vec4 col, in vec2 fragCoord)
{
    float time = LOOP_TIME*1.0;

    vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*2.0;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    
    vec2 c =uv * 4. + time * .3;

    float k = .1 + cos(c.y + sin(.148 - time)) + 2.4 + time;
    float w = .9 + sin(c.x + cos(.628 + time)) - 0.7 + time;
    float d = length(c);
    float s = 7. * cos(d+w) * sin(k+w);
    
    col = vec4(.5 + .5 * cos(s + vec3(0.5)), 1);
    
    #ifdef SPECULAR
    col *= vec4(1, .7, .4, 1) 
        *  pow(max(normalize(vec3(length(dFdx(col)), length(dFdy(col)), .5/iResolution.y)).z, 0.), 2.)
        + .75; 
    #endif
}