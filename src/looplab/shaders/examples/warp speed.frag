
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================




#define iBaseHueRad 3.11

// 'Warp Speed' by David Hoskins 2013.
// I tried to find gaps and variation in the star cloud for a feeling of structure.
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float time = (LOOP_TIME+29.) * 15.0;

    float s = 0.0, v = 0.0;
    vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*2.0;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    float t = time*1.0;
    uv.x = (uv.x * iResolution.x / iResolution.y) + sin(t) * 0.5;
    float si = sin(t + 2.17); // ...Squiffy rotation matrix!
    float co = cos(t);
    uv *= mat2(co, si, -si, co);
    vec3 col = vec3(0.0);
    vec3 init = vec3(0.25, 0.25 + sin(time*1.0) * 0.4, time*1.0);
    int count = iComplexity * 10+10;
    float power = pow(iForce/5.5, 3.)+0.05;
    for (int r = 0; r < count; r++) 
    {
        vec3 p = init + s * vec3(uv, 0.143/power);
        p.z = mod(p.z, 2.0);
        for (int i=0; i < 10; i++)  p = abs(p * 2.04) / dot(p, p) - 0.75;
        v += length(p * p) * smoothstep(0.0, 0.5, 0.9 - s) * .009;
        // Get a purple and cyan effect by biasing the RGB in different ways...
        if(mColorMode == 1)
        {
            col +=  vec3(0.2+(1.1-s + v)*0.5) * v * 0.9/count;
        }
        else
        {
            col +=  vec3(v * 0.3, 1.1 - s * 0.5, .7 + v * 0.5) * v * 0.9/count;
        }
        
        s += .01;
    }
    fragColor = vec4(col, 1.0);
}