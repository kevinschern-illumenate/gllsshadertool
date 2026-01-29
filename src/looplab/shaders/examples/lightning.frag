
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// Lightning
// By: Brandon Fogerty
// bfogerty at gmail dot com 
// xdpixel.com


// By: Brandon Fogerty
// bfogerty at gmail dot com 
// xdpixel.com
 
 
// EVEN MORE MODS BY 27
 
 
#ifdef GL_ES
precision lowp float;
#endif
// EVEN MORE MODS BY 27


#ifdef GL_ES
precision lowp float;
#endif

 
#define iBaseHueRad 4.03

float count = 2.0 * iComplexity;

float Hash( vec2 p, in float s)
{
    vec3 p2 = vec3(p.xy,27.0 * abs(sin(s)));
    return fract(sin(dot(p2,vec3(27.1,61.7, 12.4)))*273758.5453123);
}

float noise(in vec2 p, in float s)
{
    vec2 i = floor(p);
    vec2 f = fract(p);
    f *= f * (3.0-2.0*f);

    return mix(mix(Hash(i + vec2(0.,0.), s), Hash(i + vec2(1.,0.), s),f.x),
               mix(Hash(i + vec2(0.,1.), s), Hash(i + vec2(1.,1.), s),f.x),
               f.y) * s;
}

float fbm(vec2 p)
{
     float v = 0.0;
     v += noise(p*1., 0.35);
     v += noise(p*2., 0.25);
     v += noise(p*4., 0.125);
     v += noise(p*8., 0.0625);
     return v;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{

    vec2 uv = (fragCoord.xy / iResolution.xy-0.9);
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }

    vec3 finalColor = vec3( 0.0 );
    float force = pow(iForce/5.5,2.);
    for( float i=1.; i < count; ++i )
    {
        float t = abs(force / ((uv.x + fbm( uv + LOOP_TIME*1.0/i)) * (i*50.0)));
        finalColor +=  t * vec3( i * 0.075 +0.1, 0.5, 2.0 );
    }
    
    fragColor = vec4( finalColor, 1.0 );

}