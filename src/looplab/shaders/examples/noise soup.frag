
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// GLSL textureless classic 3D noise "cnoise",
// with an RSL-style periodic variant "pnoise".
// Author:  Stefan Gustavson (stefan.gustavson@liu.se)
// Version: 2011-10-11
//
// Many thanks to Ian McEwan of Ashima Arts for the
// ideas for permutation and gradient selection.
//
// Copyright (c) 2011 Stefan Gustavson. All rights reserved.
// Distributed under the MIT license. See LICENSE file.
// https://github.com/ashima/webgl-noise
//


/* discontinuous pseudorandom uniformly distributed in [-0.5, +0.5]^3 */
vec3 random3(vec3 c) {
    float j = 4096.0*sin(dot(c,vec3(17.0, 59.4, 15.0)));
    vec3 r;
    r.z = fract(512.0*j);
    j *= .125;
    r.x = fract(512.0*j);
    j *= .125;
    r.y = fract(512.0*j);
    return r-0.5;
}

/* skew constants for 3d simplex functions */
const float F3 =  0.3333333;
const float G3 =  0.1666667;

/* 3d simplex noise */
float simplex3d(vec3 p) {
     /* 1. find current tetrahedron T and it's four vertices */
     /* s, s+i1, s+i2, s+1.0 - absolute skewed (integer) coordinates of T vertices */
     /* x, x1, x2, x3 - unskewed coordinates of p relative to each of T vertices*/
     
     /* calculate s and x */
     vec3 s = floor(p + dot(p, vec3(F3)));
     vec3 x = p - s + dot(s, vec3(G3));
     
     /* calculate i1 and i2 */
     vec3 e = step(vec3(0.0), x - x.yzx);
     vec3 i1 = e*(1.0 - e.zxy);
     vec3 i2 = 1.0 - e.zxy*(1.0 - e);
        
     /* x1, x2, x3 */
     vec3 x1 = x - i1 + G3;
     vec3 x2 = x - i2 + 2.0*G3;
     vec3 x3 = x - 1.0 + 3.0*G3;
     
     /* 2. find four surflets and store them in d */
     vec4 w, d;
     
     /* calculate surflet weights */
     w.x = dot(x, x);
     w.y = dot(x1, x1);
     w.z = dot(x2, x2);
     w.w = dot(x3, x3);
     
     /* w fades from 0.6 at the center of the surflet to 0.0 at the margin */
     w = max(0.6 - w, 0.0);
     
     /* calculate surflet components */
     d.x = dot(random3(s), x);
     d.y = dot(random3(s + i1), x1);
     d.z = dot(random3(s + i2), x2);
     d.w = dot(random3(s + 1.0), x3);
     
     /* multiply d by w^4 */
     w *= w;
     w *= w;
     d *= w;
     
     /* 3. return the sum of the four surflets */
     return dot(d, vec4(52.0));
}



// FBM
float fbm (in vec3 p) {
    float ret = -1.;
    float freq = 1.;
    float amp = 1.;
    for(int i=0; i<7; i++) {
        float n = simplex3d(p*freq+vec3(0,(LOOP_TIME*1.0),0)*2.);
        ret = ret + n * amp;
        amp *= .5;
        freq *= 1.5 + n * .1;
    }
    return ret;
}

float f(vec3 p) {
    float n = fbm(p);
    return p.y - 1. - exp(n) * .5;
}



vec3 calcNormal(vec3 p, float h) // for function f(p)
{
    const vec2 k = vec2(1,-1);
    return normalize( k.xyy*f( p + k.xyy*h ) + 
                      k.yyx*f( p + k.yyx*h ) + 
                      k.yxy*f( p + k.yxy*h ) + 
                      k.xxx*f( p + k.xxx*h ) );
}



void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord.xy / iResolution.xy;
    uv = (uv-0.5) * 2.0;

    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }


    vec3 ro = vec3(0, 2, -4);
    vec3 rd = normalize(vec3(uv, 1.77) + vec3(0,-1.5,0));
    float t = 0., d;

    
    for(int i=0; i<iComplexity; i++) {
        d = f(ro+rd*t);        
        t+=d;
    }
    
    vec3 n = calcNormal(ro+rd*t, t*t*.0004);
    // Time varying pixel color
    vec3 col = -n.yyy *n.y * .5 + .5;
    col /= t;

    float force2 = pow(iForce+0.0,1.8)+1.0;
    float force = ((iForce2-6.0) / 5.0);

    col *= force2;
    col += force;

    // Output to screen
    fragColor = vec4(col,1.0);
}
