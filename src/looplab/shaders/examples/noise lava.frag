
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

//Noise animation - Lava
//by nimitz (twitter: @stormoid)


//Somewhat inspired by the concepts behind "flow noise"
//every octave of noise is modulated separately
//with displacement using a rotated vector field

//This is a more standard use of the flow noise
//unlike my normalized vector field version (https://www.shadertoy.com/view/MdlXRS)
//the noise octaves are actually displaced to create a directional flow

//Sinus ridged fbm is used for better effect.

#define iBaseHueRad 0.2844

#define time (LOOP_TIME*1.0)

float hash21(in vec2 n){ return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453); }
mat2 makem2(in float theta){float c = cos(theta);float s = sin(theta);return mat2(c,-s,s,c);}
float noise( in vec2 x ){return texture(iChannel0, x*.01).x;}

vec2 gradn(vec2 p)
{
    float ep = .09;
    float gradx = noise(vec2(p.x+ep,p.y))-noise(vec2(p.x-ep,p.y));
    float grady = noise(vec2(p.x,p.y+ep))-noise(vec2(p.x,p.y-ep));
    return vec2(gradx,grady);
}

float flow(in vec2 p)
{
    float z=2.;
    float rz = 0.;
    vec2 bp = p;
    float count = 2.0 + iComplexity;
    float power = pow(iForce/5.5, 3.);
    for (float i= 1.;i < count;i++ )
    {
        //primary flow speed
        p += sin(time)*.6;
        
        //secondary flow speed (speed of the perceived flow)
        bp += sin(time)*2.0;
        
        //displacement field (try changing time multiplier)
        vec2 gr = gradn(i*p*.34+time*1.);
        
        //rotation of the displacement field
        gr*=makem2(time*6.-(0.05*p.x+0.03*p.y)*40.);
        
        //displace the system
        p += gr*.5;
        
        //add noise octave
        rz+= (sin(noise(p)*7.)*0.5+0.5)/z;
        
        //blend factor (blending displaced system with base system)
        //you could call this advection factor (.5 being low, .95 being high)
        p = mix(bp,p,.77);
        
        //intensity scaling
        z *= 1.4*power;
        //octave scaling
        p *= 2.;
        bp *= 1.9;
    }
    return rz;  
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
   vec2 p = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }
    p*= 3.;
    float rz = flow(p);
    
    vec3 col = vec3(.2,0.07,0.01)/rz;
    col=pow(col,vec3(1.4));
    fragColor = vec4(col,1.0);
}