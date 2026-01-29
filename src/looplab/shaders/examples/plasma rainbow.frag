
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float time = LOOP_TIME*1.0;
    vec2 uv = ((fragCoord.xy / iResolution.xy)-0.5)*8.0;     
    
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    vec2 uv0=uv;
    float i0=1.0;
    float i1=1.0;
    float i2=1.0;
    float i4=0.0;
    float power = pow(iForce/5.5, 2.);
    for(int s=0;s<iComplexity;s++)
    {
        vec2 r;
        // Use sin(time) for cyclic motion instead of accumulating time
        float timeOffset = sin(time + float(s) * 0.5) * 0.5;
        r=vec2(cos(uv.y*i0-i4+time/i1+sin(.728 + time)),sin(uv.x*i0-i4+time/i1-cos(.128 + time)))/i2;
        r+=vec2(-r.y,r.x)*0.3;
        uv.xy+=r;
        
        i0*=1.93*power;
        i1*=1.15;
        i2*=1.7;
        i4+=0.05 + timeOffset*i1;  // Cyclic instead of accumulating
    }
    float r=sin(uv.x-time+cos(.628 + 1.0*time)-sin(.1628 + 1.0*time))*0.5+0.5;
    float b=sin(uv.y+time+cos(.228 + 1.0*time)-sin(.0828 + 1.0*time))*0.5+0.5;
    float g=sin((uv.x+uv.y+sin(time*1.0+cos(.328 + 1.0*time)))*0.5)*0.5+0.5;
    
    fragColor = vec4(r,g,b,1.0);
    
    fragColor *= vec4(1, .7, .4, 1) 
        *  pow(max(normalize(vec3(length(dFdx(fragColor)), length(dFdy(fragColor)), .5/iResolution.y)).z, 0.), 2.)
        + .75; 
}