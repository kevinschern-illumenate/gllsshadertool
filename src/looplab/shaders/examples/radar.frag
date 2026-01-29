
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// Author: asmith13
// mainly from https://www.shadertoy.com/view/MsG3WW - mlkn
// Free to use

// i finally understood polar coordinates..
// http://mathworld.wolfram.com/PolarCoordinates.html

const float PI = 3.1415926535897932384626433832795;
const float TWOPI = 6.283185307179586476925286766559;

float scale(float value, float min, float max, float toMin, float toMax)
{
    return (value - min) / (max - min) * (toMax - toMin) + toMin;
}

float nbSweeps = (iNbItems + 0.0);

float RadarSweep(in float time, in vec2 c, in float speed, in bool dir_cw){
    
    time *= speed; // adjust speed by multiplying the time
    
    
    if(!dir_cw) c.xy = c.yx; 
    
    // x,y - polar coords see header
    float x = length(c); // x = length of 0,0 to current pixel
    // y is the angle of our coord system. i mod it to TWO PI to reduce doubler effects
    float s = mod(atan(c.y, c.x) + time, TWOPI/nbSweeps);// see header or build in function

    s /= TWOPI/nbSweeps;
   

    float sizeHalf = scale(iForce, 1.0, 10.0, 0.02, 0.98) / 2.0;
    float fade = scale(iForce2, 1.0, 10.0, 1., .0);
    
    float start = 0.5 - sizeHalf;
    float end = 0.5 + sizeHalf;    
    
    s = s >= start && s <= end ? 1.-2.*abs(scale(s, start, end, 0., 1.)-0.5) : -1.;    
    s = s>0. && (s < fade) ? s / fade  : (s > 0. ? 1.0 : 0.);

    return s;
    
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 p = fragCoord.xy / iResolution.xy-0.5;
    p *= 2.0;
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }
        
    //settings
    vec2 left = vec2(-0.0, 0.0);
    
    float speed = 1.5/2.0;
    
    bool dir_cw = true;
    float time = LOOP_TIME*1.0;
       
    fragColor = vec4(vec3(RadarSweep(time, p, speed,  dir_cw)), 1.0);    
}