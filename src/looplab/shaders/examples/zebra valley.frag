// https://www.shadertoy.com/view/sdlfRj



// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

void mainImage( out vec4 O, vec2 U )
{
    vec2 R = iResolution.xy;
    U *= 7./R;
    O-=O;
    for(float i=0.,v; i++ < 70.; )
        v = 9.-i/6.+2.*cos(U.x + sin(i/6. + LOOP_TIME ) ) - U.y,
        O = mix(O, vec4(int(i)%2), smoothstep(0.,15./R.y, v) );
}


