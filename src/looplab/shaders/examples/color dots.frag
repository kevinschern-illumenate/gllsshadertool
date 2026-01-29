
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// https://www.shadertoy.com/view/fl2fWm

float SMOOTH_BOORDER = iForce2 / 50.0;
#define PI   3.1415926
#define PId2 1.5707963
#define PI2  6.2831853
int NUMCIRCLES = iNbItems * 4;
float  TIME_SCALE = 1.0 ;
float RADIUS = iForce / 12.0 ;


vec2 random( float x, float y )
{
    vec2 K1 = vec2(
        23.14069263277926, // e^pi (Gelfond's constant)
         2.665144142690225 // 2^sqrt(2) (Gelfondâ€“Schneider constant)
    );
    return abs(fract( vec2(cos( x * K1.x), sin( y * K1.y + 166.6))));
}

vec2 generateRandomShift(float xSeed, float ySeed, float time, vec2 ratio)
{
    return (2.0 *random(ceil(time/PI2) + xSeed, ceil(time/PI2) + ySeed) - 1.0) * ratio;
}

float sinWave01(float time)
{
    return 0.5 + 0.5 * sin(time - PId2);
}

float calculateCircle(vec2 uv, float r, float blur)
{
    float dist = length(uv);
    return smoothstep(r + blur, r, dist); 
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = (fragCoord.xy / iResolution.xy-0.5);
	vec2 ratio = iResolution.xy/ iResolution.y;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
		ratio = iResolution.xy/ iResolution.x;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    
    uv *= 3.5;
        
    float col;
    for(int i = 0; i < NUMCIRCLES; ++i)
    {
        float timeShift = 2.0*float(i);
        float time = TIME_SCALE*(LOOP_TIME + timeShift);
        vec2 shift =  generateRandomShift(2.0*float(i), float(i + 56), time, ratio);
        col += calculateCircle(uv - shift, RADIUS * sinWave01(time), SMOOTH_BOORDER) * 
                              (1.0 - sinWave01(time)); 
    }
    
    vec3 sincol = mColorMode != 1 ? 0.5 + 0.5*cos(LOOP_TIME+uv.xyx+vec3(0,2,4)) : vec3(1.0);
    
    //fragColor = vec4(uv, 0.0, 1.0);
    fragColor = vec4(sincol * (clamp(col, 0.0, 1.0)), 1.0);
}