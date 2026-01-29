
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

//Ether by nimitz (twitter: @stormoid)
float power = pow(iForce/5.5, 1.7);
#define t LOOP_TIME
mat2 m(float a){float c=cos(a), s=sin(a);return mat2(c,-s,s,c);}
float map(vec3 p){
    p.xz*= m(t*0.4);p.xy*= m(t*0.3);
    vec3 q = p*2.+t;
    return length(p+vec3(sin(t*0.7)))*log(length(p)+1.) + sin(q.x+sin(q.z+sin(q.y)))*0.5*power - 1.;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord ){       

    vec2 p = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }

    vec3 cl = vec3(0.);
    float d = 2.5;
    for(int i=0; i<=iComplexity*2; i++) {
        vec3 p = vec3(0,0,5.) + normalize(vec3(p, -1.))*d;
        float rz = map(p);
        float f =  clamp((rz - map(p+.1))*0.5, -.1, 1. );
        vec3 l = vec3(0.3) + vec3(2.0)*f;
        cl = cl*l + (1.-smoothstep(0., 2.5, rz))*.7*l;
        d += min(rz, 1.);
    }
    fragColor = vec4(vec3(pow(cl.x*2.0, 0.35)), 1.);  
}