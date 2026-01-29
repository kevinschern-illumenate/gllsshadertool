
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// https://www.shadertoy.com/view/XXyGzh
#define iBaseHueRad 0.

void mainImage( out vec4 o, vec2 u )
{
    vec2 v = iResolution.xy;
         u = .2*(u+u-v)/v.y;    
         
    vec4 z = o = -vec4(0.,1.,1.,1.);
    float force1 = pow(iForce / 5., 2.);
	float force2 = 10. - iForce2 - 2.0;
    for (float a = .5, t = LOOP_TIME*1.0, i; 
         ++i < 2.2*iComplexity; 
         o += (force1 + cos(z+t)) 
            / length((force2+i*dot(v,v)) 
                   * sin(1.5*u/(.5-dot(u,u)) - 9.*u.yx + t))
         )  
        v = cos(++t - 7.*u*pow(a += .03, i)) - 5.*u,                 
        u += tanh(40. * dot(u *= mat2(cos(i + .02*t - vec4(0,11,33,0)))
                           ,u)
                      * cos(1e2*u.yx + t)) / 2e2
           + .2 * a * u
           + cos(4./exp(dot(o,o)/1e2) + t) / 3e2;
              
     o = 25.6 / (min(o, 13.) + 464. / o);
       
     
}