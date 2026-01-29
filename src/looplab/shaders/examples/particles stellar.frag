
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// Created by Stephane Cuillerdier - Aiekick/2015
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

#define iBaseHueRad 5.7636

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float t = LOOP_TIME+5.;
        
    // vars
    float z = 2.5;
    
    float n = pow(0.+iComplexity,2.)*3.; // particle count
    
    vec3 startColor = normalize(vec3(1.,0.,0.));
    vec3 endColor = normalize(vec3(0.2,0.2,.8));
    
    float startRadius = 0.3;
    float endRadius = 0.6 * pow(iForce/5.5, 5.);
    
    float power = 0.3;
    float duration = 8.;
    
  
    vec2 v = (fragCoord.xy / iResolution.xy-0.5)*z*3.;
    if(iResolution.x < iResolution.y)
    {
        v.x *= iResolution.x/iResolution.y;
    }
    else
    {
        v.y *= iResolution.y/iResolution.x;
    }
    
   
    
    vec3 col = vec3(0.);
    
    vec2 pm = v.yx*2.8;
    
    float dMax = duration;
    
    float mb = 0.;
    float mbRadius = 0.;
    float sum = 0.;
    for(int i=0;i<n;i++)
    {
        float d = fract(t*power+48934.4238*sin(float(i)*692.7398))*duration;
        float a = 6.28*float(i)/float(n);
         
        float x = d*cos(a);
        float y = d*sin(a);
        
        float distRatio = d/dMax;
        
        mbRadius = mix(startRadius, endRadius, distRatio); 
        
        v = mod(v,pm) - 0.5*pm;
        
        vec2 p = v - vec2(x,y);
        
        p = mod(p,pm) - 0.5*pm;
        
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
