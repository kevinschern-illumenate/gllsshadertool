
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define pi  3.14159
#define tau 6.28318
#define rot(a) mat2(cos(a), -sin(a), sin(a), cos(a)) // col1a col1b col2a col2b

vec2 random2( vec2 p ) {
    return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453);
}

const float timeDiv = 4.5;

float voronoi(vec2 uv) 
{
    vec2 cell = floor(uv);
    vec2 frac = fract(uv);
    float ret = 1.0;
    float change = LOOP_TIME / timeDiv;

    for (int i = -1; i <= 1; i++) {
        for (int j = -1; j <=1; j++) {
            vec2 neighbor = vec2(float(i), float(j));
            vec2 rand = random2(cell + neighbor);
            float t = LOOP_TIME *floor(sin(LOOP_TIME));
            rand = 0.5 + 0.5 * sin(change * 4. + 2. * pi * rand);
            vec2 toCenter = neighbor + rand - frac;
            ret = min(ret, max(abs(toCenter.x), abs(toCenter.y)));
        }
    }
    
    return ret;
}

vec2 gradient(in vec2 x, float thickness)
{
    vec2 h = vec2(thickness, 0.);
    return vec2(voronoi(x + h.xy) - voronoi(x - h.xy),
               voronoi(x + h.yx) - voronoi(x - h.yx)) / (.9 * h.x);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{    
    vec2 uv = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    uv *= 4.;

    float power = pow(iForce/5.5, 3.);

        
    float val = voronoi(uv) / length(gradient(uv, .0235));
    float colVal = pow(val, 3.) *123.5 * power;
    
    fragColor.rgb = mix( vec3(0.86+colVal, 0.86+colVal, 0.86+colVal), 
                        vec3(0., 0., 0.),
                        0.8);

}
