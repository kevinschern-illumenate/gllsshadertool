
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// Created by Stephane Cuillerdier - Aiekick/2015
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
// Tuned via XShade (http://www.funparadigm.com/xshade/)

 
 

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float t = LOOP_TIME*1.0;
    float z = 2.;

    int n = iComplexity * 33; // particle count
    
    vec3 startColor = vec3(0.1);
    vec3 endColor = vec3(1);
    
    float startRadius = 0.24;
    float endRadius = 3.0;
    
    float power = 0.51;
    float duration = 4.;

    vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*6.0;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
  
    
    vec3 col = vec3(0.);
    
    vec2 pm = uv.yx*2.8;
    
    float dMax = duration;
    

    float evo = 1.;
    
    float mb = 0.;
    float mbRadius = 0.;
    float sum = 0.;
    for(int i=0;i<n;i++)
    {
        float d = fract(t*power+489.4238*sin(float(i/int(evo))*692.7398));
                
        float tt = 0.;
            
        float a = 6.28*float(i)/float(n);

        float x = d*cos(a)*duration;

        float y = d*sin(a)*duration;
        
        float distRatio = d/dMax;
        
        mbRadius = mix(startRadius, endRadius, distRatio)*pow(7.,iForce/5.5)/7.; 
        
        vec2 p = uv - vec2(x,y);//*vec2(1,sin(a+3.14159/2.));
        
        mb = mbRadius/dot(p,p);
        
        sum += mb;
        
        col = mix(col, mix(startColor, endColor, distRatio), mb/sum);
    }
    
    sum /= float(n);
    
    col = normalize(col) * sum;
    
    sum = clamp(sum, 0., .4);
    
    vec3 tex = vec3(1.);
     
    col *= smoothstep(tex, vec3(0.), vec3(sum));
        
    fragColor.rgb = col;
}