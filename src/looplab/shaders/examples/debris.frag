// https://www.shadertoy.com/view/7lyyzd

//<100 chars playlist: https://www.shadertoy.com/playlist/f3lGDN
/*
    "Debris" by @XorDev

    I just wanted another 3D shader in less than 100 characters.
*/


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

void mainImage(out vec4 O, vec2 I)
{
	

    I *= 0.5;
    //Clear the fragcolor, texture sample with parallax, iterate 
    for(O-=O; O.r<texture(iChannel0, I/3e3-1.0*LOOP_TIME/O.r/1e2).r; O+=.1);
	
	float force = pow(iForce/5.5, 3.0)+0.5;
	
	O = force*vec4(pow(O.x, 2.0));
}