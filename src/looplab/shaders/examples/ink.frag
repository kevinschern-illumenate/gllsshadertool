
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// based on https://www.shadertoy.com/view/ltjXWW

float L =  (iComplexity-1.) * 3. + 5.;
#define R(a) mat2(C=cos(a),S=sin(a),-S,C)
float C,S,v, T;

float N(vec2 u) { // infinite perlin noise with constant image-space spectrum (like Shepard scale)
    mat2 M = R(1.7);
    float v = 0., t = 0.;
    for (float i=0.; i<L; i++)
    {   float k = i-T,
              a = 1.-cos(6.28*k/L),
              s = exp2(mod(k,L));
        v += a/s* ( 1. - abs( 2.* texture(iChannel0, M*u*s/1e3 ).r - 1.) ); 
        t += a/s;  M *= M;
    }
    return v/t;
}

void mainImage( out vec4 O, vec2 fragCoord ) {
   

    vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*2.0;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    
    T = 1.0*LOOP_TIME;
    float e = 0.;  
    
    O = vec4 ( sqrt(smoothstep(.7-e,.7+e, N(uv) )) );  // NB: sqrt approximates gamma 1./2.2
}