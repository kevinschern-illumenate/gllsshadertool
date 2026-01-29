
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

float SmoothCurve(float t){
 return smoothstep(0.0,1.0,t);   
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
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
    
    float vel = 0.2;
    vec2 uvrot = uv;
    uvrot.x = cos(vel*time)*uv.x + sin(vel*time)*uv.y;
    uvrot.y = -sin(vel*time)*uv.x + cos(vel*time)*uv.y;
    uv = uvrot;
    
    float radius = 1.0-iForce*0.08272;
    float offset = 0.01;
    float freq = 2.0;    
    
    float maskx = 2.0*smoothstep(0.0,0.0,sin(freq*2.0*3.1419*uv.y))-1.0; 
    float masky = 2.0*smoothstep(0.0,0.0,sin(freq*2.0*3.1419*uv.x))-1.0; 

    float t = mod(time,4.0);
    
    if(t<1.0){
          uv.x += SmoothCurve(t)*maskx;  
    }else if(t<2.0){
          uv.y += SmoothCurve(t-1.0)*masky;  
    }else if(t<3.0){
          uv.x -= SmoothCurve(t-2.0)*maskx;          
    }else if(t<4.0){
          uv.y -= SmoothCurve(t-3.0)*masky;             
    }
    
    
    float f = sin(freq*2.0*3.14159*uv.x)*sin(freq*2.0*3.1419*uv.y);
    f = smoothstep(radius-offset,radius+offset,abs(f));
    
    fragColor = vec4(f,f,f,1.0);
    
}