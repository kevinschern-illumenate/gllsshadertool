
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// https://www.shadertoy.com/view/XsBfRW

void mainImage( out vec4 O, vec2 u )
{

	vec2 uv = (u.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
	
	vec2  U = 10.0 * uv * mat2(1,1,-1,1)*.7 +5.,
          F = fract(U);
          F = min(F,1.-F);
    float s = length( ceil(U) -5.5 ),
          e = 2.* fract( ( LOOP_TIME - s* iForce2/2.0 ) / 4.) - 1.,
          v = fract ( iForce / 5.0 * min(F.x,F.y) );

    O = mix( vec4(2.0),
             vec4(0.0), 
             smoothstep( -.05, 0., .95*(e < 0. ? v : 1.-v) - e*e)
            + s*.1 );
}