
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

//Noise animation - Watery by nimitz (twitter: @stormoid)

//The domain is rotated by the values of a preliminary fbm call
//then the fbm function is called again to color the screen.
//Turbulent fbm (aka ridged) is used for better effect.
//define centered to see the rotation better.

#define iBaseHueRad 4.44

#define CENTERED

#define time (LOOP_TIME*1.0)

mat2 makem2(in float theta){float c = cos(theta);float s = sin(theta);return mat2(c,-s,s,c);}
float noise( in vec2 x ){return texture(iChannel0, x*.01).x;}

mat2 m2 = mat2( 0.80,  0.60, -0.60,  0.80 );
float fbm( in vec2 p )
{   
    float z=2.;
    float rz = 0.;
    for (float i= 1.;i < 3.;i++ )
    {
        rz+= abs((noise(p)-0.5)*2.)/z;
        z = z*2.;
        p = p*2.;
        p*= m2;
    }
    return rz;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 p = (fragCoord.xy / iResolution.xy-0.5)*2.0;
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }
    vec2 bp = p;
    #ifndef CENTERED
    p += 5.;
    p *= 0.6;
    #endif
    float rb = fbm(p*.5+time*.17)*.1;
    rb = sqrt(rb);
    #ifndef CENTERED
    p *= makem2(rb*.2+atan(p.y,p.x)*1.);
    #else
    p *= makem2(rb*.2+atan(p.y,p.x)*(0.+iComplexity));
    #endif
    
  //coloring
    float rz = fbm(p*0.9-time*.7);
    rz *= dot(bp*10.5,bp)+10.5;
    rz *= sin(p.x*.5+time*4.)*1.9;
    float power = pow(iForce/5.5, 3.);
    vec3 col = vec3(.2,.2,1.5)/(2.1-rz)*power;
    fragColor = vec4(sqrt(abs(col)),1.0);
}